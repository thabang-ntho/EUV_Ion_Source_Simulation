"""
pp_model.py — MPh (Python) 2D planar tin-droplet pre-pulse model
Builds → (optionally solves) → postprocesses → saves .mph

Highlights
- Mirrors MPh demo style (create_capacitor.py).
- Geometry: Circle by DIAMETER (D_drop), big gas rectangle; interior boundary kept.
- Variables/operators live under component/definitions (required).
- Laser P(t) read verbatim from file (with inline comments stripped).
- Param files may use inline comments (# or //) — loader strips them safely.
- Robust file discovery & CLI flags: --no-solve, --params-dir, --out-dir.
"""

from pathlib import Path
from typing import Dict, Iterable, Optional
import argparse
import sys
import mph


# ------------------------------- file discovery -------------------------------

def find_first(paths: Iterable[Path]) -> Optional[Path]:
    for p in paths:
        if p.is_file():
            return p
    return None

def resolve_inputs(params_dir: Optional[Path]):
    here = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    search_dirs = [params_dir.resolve()] if params_dir else [here, cwd]

    def candidates(fname: str):
        return [d / fname for d in search_dirs]

    gp = find_first(candidates("global_parameters_pp_v2.txt"))
    lp = find_first(candidates("laser_parameters_pp_v2.txt"))
    px = find_first(candidates("Ppp_analytic_expression.txt"))

    missing = [name for name, p in [
        ("global_parameters_pp_v2.txt", gp),
        ("laser_parameters_pp_v2.txt", lp),
        ("Ppp_analytic_expression.txt",  px),
    ] if p is None]
    if missing:
        raise FileNotFoundError(
            "Missing required input file(s): "
            + ", ".join(missing)
            + "\nChecked:\n  " + "\n  ".join(str(d) for d in search_dirs)
        )
    return gp, lp, px


# ------------------------------- parsing helpers ------------------------------

def _strip_inline_comment(s: str) -> str:
    """
    Remove trailing inline comments beginning with '#' or '//'.
    Keeps everything before the first unquoted # or //.
    """
    # Simple, robust approach: cut at the earliest of '#' or '//' if present.
    cut = len(s)
    h = s.find('#')
    if h != -1:
        cut = min(cut, h)
    sl = s.find('//')
    if sl != -1:
        cut = min(cut, sl)
    return s[:cut].rstrip()

def read_kv_file(path: Path) -> Dict[str, str]:
    """
    Parse a single param file:
      - supports 'name value' or 'name = value'
      - ignores full-line comments (# or //)
      - strips inline comments after the value
      - preserves units (e.g., 25[um])
    """
    kv: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "//")):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
        else:
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            k, v = parts
        k = k.strip()
        v = _strip_inline_comment(v.strip())
        if not v:
            # entire value was a comment → skip
            continue
        kv[k] = v
    return kv

def read_pulse_expression(path: Path) -> str:
    """
    Load analytic P(t) and strip inline comments line-by-line.
    Joins lines with spaces so multi-line expressions are valid.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        cleaned = []
        for raw in lines:
            s = raw.strip()
            if not s or s.startswith(("#", "//")):
                continue
            cleaned.append(_strip_inline_comment(s))
        expr = " ".join([c for c in cleaned if c])
        return expr or "1[W]*(flc2hs(t,1e-12)-flc2hs(t-1e-9,1e-12))"
    except Exception:
        return "1[W]*(flc2hs(t,1e-12)-flc2hs(t-1e-9,1e-12))"

def inject_parameters(model, params: Dict[str, str]) -> Dict[str, str]:
    """Create 'parameters' container and push all pairs; ensure D_drop is defined."""
    parameters = model / "parameters"
    (parameters / "Parameters 1").rename("parameters")
    # Push existing
    for k, v in params.items():
        model.parameter(k, v)
    # Define D_drop if only R_drop supplied
    if "D_drop" not in params and "R_drop" in params:
        model.parameter("D_drop", "2*R_drop")
        params = dict(params)  # shallow copy
        params["D_drop"] = "2*R_drop"
    return params


# -------------------------------- pipeline ------------------------------------

def build_model(no_solve: bool, params_dir: Optional[Path], out_dir: Optional[Path]):
    # Resolve inputs/outputs
    gp_path, lp_path, pulse_path = resolve_inputs(params_dir)
    out_dir = (out_dir or Path(__file__).resolve().parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    OUT_MPH = out_dir / "pp_model_created.mph"
    PNG     = out_dir / "pp_temperature.png"
    CSV_T   = out_dir / "pp_T_vs_time.csv"
    CSV_M   = out_dir / "pp_massloss_vs_time.csv"
    CSV_R   = out_dir / "pp_radius_vs_time.csv"

    # Start COMSOL and create model
    client = mph.start()
    model = client.create("pp_model")

    # Parameters (from both files, inline comments allowed)
    params: Dict[str, str] = {}
    params.update(read_kv_file(gp_path))
    params.update(read_kv_file(lp_path))
    params = inject_parameters(model, params)

    # Guard: must have D_drop (or synthesized), X_max, Y_max
    required = ["D_drop", "X_max", "Y_max"]
    missing = [k for k in required if k not in params]
    if missing:
        raise RuntimeError(f"Missing required parameters: {missing}\nIn: {gp_path}\nAnd: {lp_path}")

    # Functions
    functions = model / "functions"

    Ppp = functions.create("Analytic", name="Ppp")
    Ppp.property("funcname", "Ppp")
    Ppp.property("args", ["t"])
    Ppp.property("expr", read_pulse_expression(pulse_path))

    if "p_sat_expr" in params:
        psat = functions.create("Analytic", name="psat")
        psat.property("funcname", "p_sat")
        psat.property("args", ["T"])
        # inline comments already stripped by read_kv_file
        psat.property("expr", params["p_sat_expr"])

    # Component + geometry (2D planar)
    components = model / "components"
    components.create(True, name="component")
    comp = components / "component"

    geometries = model / "geometries"
    geom = geometries.create(2, name="geometry")

    # Droplet: Circle by DIAMETER, uses D_drop
    drop = geom.create("Circle", name="droplet")
    drop.property("type", "d")
    drop.property("d", "D_drop")
    drop.property("pos", ["0", "0"])

    # Gas: big rectangle
    gas = geom.create("Rectangle", name="gas")
    gas.property("pos",  ["-X_max", "-Y_max"])
    gas.property("size", ["2*X_max", "2*Y_max"])

    union = geom.create("Union", name="union")
    union.property("intbnd", True)
    union.java.selection("input").set([drop.tag(), gas.tag()])

    model.build(geom)

    # Add a custom view for the droplet
    view = model.java.view().create("view2", 2)
    view.label("Droplet View")
    axis = view.axis()
    axis.set("xmin", "-D_drop*1.5")
    axis.set("xmax", "D_drop*1.5")
    axis.set("ymin", "-D_drop*1.5")
    axis.set("ymax", "D_drop*1.5")

    # Views for GUI
    views = model.java.view()
    views.create("view2", 2)
    view2 = model.view("view2")
    view2.label("Droplet View")
    view2.axis().set("xmin", "-D_drop*1.5")
    view2.axis().set("xmax", "D_drop*1.5")
    view2.axis().set("ymin", "-D_drop*1.5")
    view2.axis().set("ymax", "D_drop*1.5")

    # Selections
    selections = model / "selections"

    s_drop = selections.create("Disk", name="droplet domain")
    s_drop.property("entitydim", 2)
    s_drop.property("r", "0.49*D_drop")
    s_drop.property("pos", ["0", "0"])

    s_surf = selections.create("Adjacent", name="droplet surface")
    s_surf.property("input", [s_drop])

    s_gas = selections.create("Complement", name="gas domain")
    s_gas.property("input", [s_drop])

    # Component definitions: variables/operators
    cdefs = comp / "definitions"

    variables = cdefs.create("Variables", name="variables")
    variables.property("expr", [
        "I_xy = (2/(pi*w0^2))*Ppp(t)*exp(-2*((x-x_beam)^2+(y-y_beam)^2)/w0^2)",
        "q_abs_2D = A_PP*I_xy*max(0,nx)",
        "J_evap = HK_gamma*(p_sat(T)-p_amb)/sqrt(2*pi*R_gas*T/M_Sn)",
        "sigmaT = sigma0 + dSigma_dT*(T-T_ref)",
        "p_recoil = recoil_coeff*p_sat(T)",
        "rad = sqrt(x^2+y^2)"
    ])
    variables.property("unit", ['W/m^2','W/m^2','kg/(m^2*s)','N/m','Pa','m'])
    variables.property("descr", [
        'Incident intensity (2D)',
        'Absorbed surface heat flux',
        'Evaporation mass flux',
        'Surface tension vs T',
        'Laser/plasma recoil pressure',
        'Radius helper'
    ])

    int_surf = cdefs.create("Integration", name="intop_surf")
    int_surf.property("entitydim", 1)
    int_surf.property("probetag", "none")
    int_surf.select(s_surf)

    max_surf = cdefs.create("Maximum", name="maxop_surf")
    max_surf.property("entitydim", 1)
    max_surf.property("probetag", "none")
    max_surf.select(s_surf)

    int_drop = cdefs.create("Integration", name="intop_drop")
    int_drop.property("entitydim", 2)
    int_drop.property("probetag", "none")
    int_drop.select(s_drop)

    # Materials
    materials = model / "materials"

    tin = materials.create("Common", name="tin")
    tin.select(s_drop)
    (tin / "Basic").property("density", ["rho_Sn"])
    (tin / "Basic").property("heatcapacity", ["cp_Sn"])
    (tin / "Basic").property("thermalconductivity", ["k_Sn"])
    (tin / "Basic").property("dynamicviscosity", ["mu_Sn"])

    gasm = materials.create("Common", name="gas")
    gasm.select(s_gas)
    (gasm / "Basic").property("density", ["rho_gas"])
    (gasm / "Basic").property("heatcapacity", ["cp_gas"])
    (gasm / "Basic").property("thermalconductivity", ["k_gas"])
    (gasm / "Basic").property("dynamicviscosity", ["mu_gas"])

    # Physics
    physics = model / "physics"

    ht = physics.create("HeatTransferInFluids", geom, name="ht")
    bhf = ht.create("BoundaryHeatSource", 1, name="laser+latent")
    bhf.select(s_surf)
    bhf.property("Qb", "q_abs_2D - L_v*J_evap")

    tds = physics.create("TransportOfDilutedSpecies", geom, name="tds")
    evap = tds.create("Flux", 1, name="evaporation flux")
    evap.select(s_surf)
    evap.property("N0", "-J_evap")

    spf = physics.create("LaminarFlow", geom, name="spf")
    spf.select(s_drop)
    st = spf.create("SurfaceTension", 1, name="surface tension")
    st.select(s_surf)
    st.property("gamma", "sigmaT")
    mg = spf.create("Marangoni", 1, name="Marangoni")
    mg.select(s_surf)
    mg.property("dGammadT", "dSigma_dT")
    pr = spf.create("Pressure", 1, name="recoil pressure")
    pr.select(s_surf)
    pr.property("p0", "p_recoil")

    ale = physics.create("DeformingDomain", geom, name="ale")
    free = ale.create("FreeDeformation", 2, name="free deformation")
    vmesh = ale.create("PrescribedNormalMeshVelocity", 1, name="mesh follows fluid")
    vmesh.select(s_surf)
    vmesh.property("v", "u*nx+v*ny")

    # Mesh
    meshes = model / "meshes"
    mesh = meshes.create(geom, name="mesh")
    bl = mesh.create("BoundaryLayer", name="bl")
    bl.select(s_surf)
    bl.property("n", params.get("n_bl", "5"))
    bl.property("thickness", params.get("bl_thick", "0.02*D_drop"))
    ftri = mesh.create("FreeTri", name="ftri")

    # Studies/solutions
    studies = model / "studies"
    solutions = model / "solutions"
    study = studies.create(name="transient")
    study.java.setGenPlots(False)
    study.java.setGenConv(False)

    step = study.create("Transient", name="time-dependent")
    tlist = params.get("tlist", "range(0, 1e-8, 200)")
    step.property("tlist", tlist)

    sol = solutions.create(name="solution")
    sol.java.study(study.tag())
    sol.java.attach(study.tag())
    sol.create("StudyStep", name="equations")
    sol.create("Variables", name="variables")
    solver = sol.create("Time", name="time solver")
    solver.property("tlist", tlist)

    # Plots/exports
    datasets = model / "datasets"
    tables = model / "tables"
    tables.create("Table", name="T_vs_time")
    tables.create("Table", name="mass_vs_time")
    tables.create("Table", name="radius_vs_time")

    evals = model / "evaluations"
    eT = evals.create("EvalGlobal", name="T_avg_drop")
    eT.property("table", tables / "T_vs_time")
    eT.property("expr", ["intop_drop(T)/intop_drop(1)"])
    eT.property("unit", ["K"])
    eT.java.setResult()

    eM = evals.create("EvalGlobal", name="mass loss rate")
    eM.property("table", tables / "mass_vs_time")
    eM.property("expr", ["intop_surf(J_evap)"])
    eM.property("unit", ["kg/s"])
    eM.java.setResult()

    eR = evals.create("EvalGlobal", name="apparent radius")
    eR.property("table", tables / "radius_vs_time")
    eR.property("expr", ["maxop_surf(rad)"])
    eR.property("unit", ["m"])
    eR.java.setResult()

    plots = model / "plots"
    plots.java.setOnlyPlotWhenRequested(True)
    pg = plots.create("PlotGroup2D", name="temperature field")
    pg.property("titletype", "manual")
    pg.property("title", "Temperature (K)")
    srf = pg.create("Surface", name="T")
    srf.property("expr", "T")
    srf.property("resolution", "normal")

    exports = model / "exports"
    img = exports.create("Image", name="image")
    img.property("sourceobject", plots / "temperature field")
    img.property("filename", str(PNG))
    img.property("imagetype", "png")
    img.property("size", "manualweb")
    img.property("width", "1600")
    img.property("height", "1200")
    img.property("antialias", "on")

    dataT = exports.create("Table", name="T csv")
    dataT.property("sourceobject", tables / "T_vs_time")
    dataT.property("filename", str(CSV_T))

    dataM = exports.create("Table", name="M csv")
    dataM.property("sourceobject", tables / "mass_vs_time")
    dataM.property("filename", str(CSV_M))

    dataR = exports.create("Table", name="R csv")
    dataR.property("sourceobject", tables / "radius_vs_time")
    dataR.property("filename", str(CSV_R))

    # Save inspectable model before solving (so --no-solve yields a GUI-openable file)
    model.save(str(OUT_MPH))

    if not no_solve:
        sol.java.run()
        img.java.run(); dataT.java.run(); dataM.java.run(); dataR.java.run()
        model.save(str(OUT_MPH))

    print(f"[OK] saved MPH → {OUT_MPH}")
    if not no_solve:
        print(f"[OK] PNG      → {PNG}")
        print(f"[OK] CSVs     → {CSV_T} | {CSV_M} | {CSV_R}")

    return model


# ---------------------------------- CLI ---------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Build (and optionally solve) the pre-pulse tin droplet model via MPh."
    )
    ap.add_argument("--no-solve", action="store_true",
                    help="Build only; do not run the transient solver.")
    ap.add_argument("--params-dir", type=Path, default=None,
                    help="Directory containing global_parameters_pp_v2.txt, laser_parameters_pp_v2.txt, Ppp_analytic_expression.txt.")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="Directory to write PNG/CSV/MPH (default: alongside this script).")
    args = ap.parse_args()

    try:
        build_model(no_solve=args.no_solve, params_dir=args.params_dir, out_dir=args.out_dir)
    except Exception as e:
        print("\n[ERROR] Build failed:")
        print(f"  {e}\n", file=sys.stderr)
        print("Hints:")
        print("  • Ensure MPh can find COMSOL (set COMSOL_HOME if needed).")
        print("  • Verify parameter files contain D_drop (or R_drop), X_max, Y_max, etc.")
        print("  • Inline comments with # or // are OK now; the loader strips them.")
        print("  • Run with --params-dir if your files are not next to this script.")
        sys.exit(1)


if __name__ == "__main__":
    main()
