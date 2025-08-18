"""
pp_model.py — MPh (Python) end-to-end build of a 2D planar tin-droplet pre-pulse model.

Inputs (never hardcoded):
  - data/global_parameters_pp_v2.txt      # materials, geometry, numerics
  - data/laser_parameters_pp_v2.txt       # beam geometry & constants (A_PP, w0, etc.)
  - data/Ppp_analytic_expression.txt      # analytic P(t) (Sizyuk-style)

What it builds:
  - 2D circle (droplet) + surrounding gas rectangle
  - Fresnel surface absorption heat source q_abs_2D on whole droplet surface (masked by max(0,nx))
  - Evaporation mass flux J_evap and latent-heat sink (-L_v*J_evap) on the same boundary
  - Surface tension sigma(T), Marangoni (dSigma/dT), and recoil pressure p_recoil on the free surface
  - HT in liquid & gas; TDS in gas; Laminar Flow in droplet; ALE on both domains
  - Transient study; exports PNG + CSVs; saves GUI-openable .mph

Quick usage (from repo root):
  python src/pp_model.py               # build → solve → export
  python src/pp_model.py --check-params-only   # parse and print parameters only (no COMSOL needed)
  python src/pp_model.py --no-solve            # build model but skip solve/exports, just save .mph
"""

from pathlib import Path
from typing import Dict, Iterable, List
import argparse

# ------------------------------- config -------------------------------

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

# Defaults (can be overridden by CLI)
PARAM_FILES_DEFAULT = [
    ROOT / "data" / "global_parameters_pp_v2.txt",
    ROOT / "data" / "laser_parameters_pp_v2.txt",
]
PULSE_EXPR_FILE_DEFAULT = ROOT / "data" / "Ppp_analytic_expression.txt"

RESULTS_DIR_DEFAULT = ROOT / "results"
OUT_MPH_DEFAULT = RESULTS_DIR_DEFAULT / "pp_model_created.mph"
PNG_DEFAULT = RESULTS_DIR_DEFAULT / "pp_temperature.png"
CSV_T_DEFAULT = RESULTS_DIR_DEFAULT / "pp_T_vs_time.csv"
CSV_M_DEFAULT = RESULTS_DIR_DEFAULT / "pp_massloss_vs_time.csv"
CSV_R_DEFAULT = RESULTS_DIR_DEFAULT / "pp_radius_vs_time.csv"


# --------------------------- helpers ---------------------------

def _strip_inline_comments(s: str) -> str:
    """Remove inline comments starting with # or //.
    Does not attempt to handle quoted strings.
    """
    for token in ("//", "#"):
        if token in s:
            s = s.split(token, 1)[0]
    return s.strip()


def read_kv(paths: Iterable[Path], *, allow_override: bool = True) -> Dict[str, str]:
    """Parse simple param files: 'name value' or 'name = value'. Keeps units.

    - Ignores blank lines and lines starting with '#' or '//'.
    - Strips inline comments after values.
    - For 'name value comment...' forms, only the second token is taken as value.
    - If the same key appears multiple times:
        - allow_override=True: last one wins
        - allow_override=False: first one wins
    """
    kv: Dict[str, str] = {}
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith(("#", "//")):
                continue
            line_nc = _strip_inline_comments(line)
            if not line_nc:
                continue
            if "=" in line_nc:
                k, v = [seg.strip() for seg in line_nc.split("=", 1)]
            else:
                parts: List[str] = line_nc.split()
                if len(parts) < 2:
                    continue
                k, v = parts[0], parts[1]
            if not allow_override and k in kv:
                continue
            kv[k] = v
    return kv


def inject_parameters(model, params: Dict[str, str]):
    """Create 'parameters' container and push all pairs."""
    parameters = model / "parameters"
    try:
        (parameters / "Parameters 1").rename("parameters")
    except Exception:
        pass
    for k, v in params.items():
        model.parameter(k, v)


# --------------------------- pipeline ---------------------------

def main():
    parser = argparse.ArgumentParser(description="Build/solve COMSOL model via MPh")
    parser.add_argument("--params", nargs="*", type=str, default=[str(p) for p in PARAM_FILES_DEFAULT], help="Parameter files (order matters; later values override earlier)")
    parser.add_argument("--pulse", type=str, default=str(PULSE_EXPR_FILE_DEFAULT), help="File containing analytic Ppp(t) expression")
    parser.add_argument("--outdir", type=str, default=str(RESULTS_DIR_DEFAULT), help="Output directory for PNG/CSV/MPH")
    parser.add_argument("--tlist", type=str, default=None, help="Override time list (COMSOL range() string)")
    parser.add_argument("--no-solve", action="store_true", help="Build model but skip solve and exports; still saves MPH")
    parser.add_argument("--check-params-only", action="store_true", help="Parse parameter files and print the resolved dict; no COMSOL required")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    OUT_MPH = outdir / OUT_MPH_DEFAULT.name
    PNG = outdir / PNG_DEFAULT.name
    CSV_T = outdir / CSV_T_DEFAULT.name
    CSV_M = outdir / CSV_M_DEFAULT.name
    CSV_R = outdir / CSV_R_DEFAULT.name

    # 1) parameters (NEVER hardcoded)
    param_paths = [Path(p) for p in args.params]
    params = read_kv(param_paths)

    if args.tlist:
        params["tlist"] = args.tlist

    if args.check_params_only:
        for k in sorted(params):
            print(f"{k} = {params[k]}")
        return

    # Import mph lazily so parser-only runs don't require it
    import mph  # type: ignore

    # 0) start COMSOL and create model (MPh pattern)
    client = mph.start()
    model = client.create("pp_model")

    inject_parameters(model, params)

    # 2) functions: analytic Ppp(t) from file, psat(T) if expression provided
    functions = model / "functions"

    # P(t) analytic (from file). If file missing, fall back to a short square.
    pulse_file = Path(args.pulse)
    p_expr = "1[W]*(flc2hs(t,1e-12)-flc2hs(t-1e-9,1e-12))"
    if pulse_file.is_file():
        p_expr = pulse_file.read_text(encoding="utf-8").strip()

    Ppp = functions.create("Analytic", name="Ppp")
    Ppp.property("funcname", "Ppp")
    Ppp.property("args", ["t"])
    Ppp.property("expr", p_expr)

    # Optional: user-provided vapor pressure expression
    if "p_sat_expr" in params:
        psat = functions.create("Analytic", name="psat")
        psat.property("funcname", "p_sat")
        psat.property("args", ["T"])
        psat.property("expr", params["p_sat_expr"])

    # 3) variables (laser, evaporation, capillarity, recoil)
    definitions = model / "definitions"
    variables = definitions.create("Variables", name="variables")
    variables.property("expr", [
        # Gaussian beam (2D planar) around (x_beam,y_beam)
        "I_xy = (2/(pi*w0^2))*Ppp(t)*exp(-2*((x-x_beam)^2+(y-y_beam)^2)/w0^2)",
        # Fresnel absorption (mask by nx so only illuminated half contributes)
        "q_abs_2D = A_PP*I_xy*max(0,nx)",
        # Hertz–Knudsen mass flux (or provide diffusion-based form via params)
        "J_evap = HK_gamma*(p_sat(T)-p_amb)/sqrt(2*pi*R_gas*T/M_Sn)",
        # Temperature-dependent surface tension
        "sigmaT = sigma0 + dSigma_dT*(T-T_ref)",
        # Recoil pressure model (simple scaling)
        "p_recoil = recoil_coeff*p_sat(T)",
        # Apparent radius for postprocessing (Euclidean distance)
        "rad = sqrt(x^2+y^2)"
    ])
    variables.property("unit", ['W/m^2', 'W/m^2', 'kg/(m^2*s)', 'N/m', 'Pa', 'm'])
    variables.property("descr", [
        'Incident intensity (2D)',
        'Absorbed surface heat flux',
        'Evaporation mass flux',
        'Surface tension vs T',
        'Laser/plasma recoil pressure',
        'Radius helper'
    ])

    # 4) component + geometry (2D planar)
    components = model / "components"
    components.create(True, name="component")
    geometries = model / "geometries"
    geom = geometries.create(2, name="geometry")

    # Droplet: circle of radius R_drop at origin
    drop = geom.create("Circle", name="droplet")
    drop.property("r", ["R_drop"])
    drop.property("pos", ["0", "0"])

    # Gas: big rectangle around droplet
    gas = geom.create("Rectangle", name="gas")
    gas.property("pos",  ["-X_max", "-Y_max"])
    gas.property("size", ["2*X_max", "2*Y_max"])

    # Keep interior boundary to separate droplet/gas domains
    union = geom.create("Union", name="union")
    union.property("intbnd", True)
    union.java.selection("input").set([drop.tag(), gas.tag()])

    model.build(geom)

    # 5) selections (robust targeting)
    selections = model / "selections"
    s_drop = selections.create("Disk", name="droplet domain")
    s_drop.property("entitydim", 2)
    s_drop.property("r", "0.95*R_drop")

    s_surf = selections.create("Adjacent", name="droplet surface")
    s_surf.property("input", [s_drop])   # boundary adjacent to droplet domain

    # 6) materials (properties come from params; no hardcoding here)
    materials = model / "materials"

    tin = materials.create("Common", name="tin")
    tin.select(s_drop)
    (tin / "Basic").property("density", ["rho_Sn"])
    (tin / "Basic").property("heatcapacity", ["cp_Sn"])
    (tin / "Basic").property("thermalconductivity", ["k_Sn"])
    (tin / "Basic").property("dynamicviscosity", ["mu_Sn"])

    gasm = materials.create("Common", name="gas")
    gasm.select("all")
    (gasm / "Basic").property("density", ["rho_gas"])
    (gasm / "Basic").property("heatcapacity", ["cp_gas"])
    (gasm / "Basic").property("thermalconductivity", ["k_gas"])
    (gasm / "Basic").property("dynamicviscosity", ["mu_gas"])

    # 7) physics
    physics = model / "physics"

    # Heat Transfer in Fluids (both domains)
    ht = physics.create("HeatTransferInFluids", geom, name="ht")

    # Boundary heat source: laser absorption minus latent heat on droplet surface
    bhf = ht.create("BoundaryHeatSource", 1, name="laser+latent")
    bhf.select(s_surf)
    bhf.property("Qb", "q_abs_2D - L_v*J_evap")

    # Transport of Diluted Species in gas (vapor diffusion)
    tds = physics.create("TransportOfDilutedSpecies", geom, name="tds")
    evap = tds.create("Flux", 1, name="evaporation flux")
    evap.select(s_surf)
    evap.property("N0", "-J_evap")  # outward positive into gas

    # Laminar Flow in droplet (free surface)
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

    # ALE on both domains; prescribe normal mesh velocity from fluid velocity
    ale = physics.create("DeformingDomain", geom, name="ale")
    free = ale.create("FreeDeformation", 2, name="free deformation")  # smoothing
    vmesh = ale.create("PrescribedNormalMeshVelocity", 1, name="mesh follows fluid")
    vmesh.select(s_surf)
    vmesh.property("v", "u*nx+v*ny")  # 2D normal projection

    # 8) mesh (boundary layer on droplet surface + free triangles)
    meshes = model / "meshes"
    mesh = meshes.create(geom, name="mesh")
    bl = mesh.create("BoundaryLayer", name="bl")
    bl.select(s_surf)
    bl.property("n", params.get("n_bl", "5"))
    bl.property("thickness", params.get("bl_thick", "0.01*R_drop"))
    ftri = mesh.create("FreeTri", name="ftri")

    # 9) operators & post objects
    defs = model / "definitions"
    int_surf = defs.create("Integration", name="intop_surf")
    int_surf.property("probetag", "none")
    int_surf.property("entitydim", 1)
    int_surf.select(s_surf)

    max_surf = defs.create("Maximum", name="maxop_surf")
    max_surf.property("probetag", "none")
    max_surf.property("entitydim", 1)
    max_surf.select(s_surf)

    # Average over droplet domain for temperature
    avg_drop = defs.create("Average", name="avgop_drop")
    avg_drop.property("probetag", "none")
    avg_drop.property("entitydim", 2)
    avg_drop.select(s_drop)

    datasets = model / "datasets"
    tables = model / "tables"
    tables.create("Table", name="T_vs_time")
    tables.create("Table", name="mass_vs_time")
    tables.create("Table", name="radius_vs_time")

    evals = model / "evaluations"
    eT = evals.create("EvalGlobal", name="T mean")
    eT.property("table", tables / "T_vs_time")
    eT.property("expr", ["avgop_drop(T)"])  # domain-averaged droplet temperature
    eT.property("unit", ["K"])
    eT.java.setResult()

    eM = evals.create("EvalGlobal", name="mass loss rate")
    eM.property("table", tables / "mass_vs_time")
    eM.property("expr", ["intop_surf(J_evap)"])  # kg/s
    eM.property("unit", ["kg/s"])
    eM.java.setResult()

    eR = evals.create("EvalGlobal", name="apparent radius")
    eR.property("table", tables / "radius_vs_time")
    eR.property("expr", ["maxop_surf(rad)"])  # m
    eR.property("unit", ["m"])
    eR.java.setResult()

    plots = model / "plots"
    plots.java.setOnlyPlotWhenRequested(True)
    pg = plots.create("PlotGroup2D", name="temperature field")
    pg.property("titletype", "manual")
    pg.property("title", "Temperature (K)")
    surf = pg.create("Surface", name="T")
    surf.property("expr", "T")
    surf.property("resolution", "normal")

    exports = model / "exports"
    img = exports.create("Image", name="image")
    img.property("sourceobject", plots / "temperature field")
    img.property("filename", str(PNG))
    img.property("imagetype", "png")
    img.property("size", "manualweb")
    img.property("width", "1600"); img.property("height", "1200")
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

    # 10) transient study & solution
    studies = model / "studies"
    solutions = model / "solutions"
    study = studies.create(name="transient")
    study.java.setGenPlots(False); study.java.setGenConv(False)
    step = study.create("Transient", name="time-dependent")
    step.property("activate", [
        physics / "ht",  'on',
        physics / "tds", 'on',
        physics / "spf", 'on',
        'frame:spatial1', 'on',
        'frame:material1','on',
    ])
    tlist = params.get("tlist", "range(0, 1e-8, 200)")  # override via file
    step.property("tlist", tlist)

    sol = solutions.create(name="solution")
    sol.java.study(study.tag()); sol.java.attach(study.tag())
    sol.create("StudyStep", name="equations")
    sol.create("Variables", name="variables")
    solver = sol.create("Time", name="time solver")
    solver.property("tlist", tlist)

    # solve -> export -> save
    if not args.no_solve:
        sol.java.run()
        img.java.run(); dataT.java.run(); dataM.java.run(); dataR.java.run()
    model.save(str(OUT_MPH))

    print(f"[OK] saved MPH → {OUT_MPH}")
    if not args.no_solve:
        print(f"[OK] PNG      → {PNG}")
        print(f"[OK] CSVs     → {CSV_T} | {CSV_M} | {CSV_R}")


if __name__ == "__main__":
    main()
