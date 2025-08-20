from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict
import sys
import os

try:
    from .params import load_config, SCHEMA_VERSION
except Exception:
    load_config = None
    SCHEMA_VERSION = "unknown"

# Optional logging helpers (no-ops if unavailable)
try:
    from .logging_utils import init_logger, log_step, phase_timer  # type: ignore
except Exception:  # pragma: no cover
    def init_logger(level: str = "INFO"):
        def _log(*_a, **_k):
            return None
        return _log

    def log_step(*_a, **_k):  # noqa: D401
        return None

    from contextlib import contextmanager

    @contextmanager
    def phase_timer(*_a, **_k):
        yield

# Optional Fresnel helpers (Sizyuk); will be monkeypatched in tests
try:
    from ..pp_sizyuk import load_nk_excel as _load_nk_excel, absorptivity_from_nk as _absorptivity_from_nk
except Exception:
    _load_nk_excel = None
    _absorptivity_from_nk = None


def find_first(paths):
    for p in paths:
        if p.is_file():
            return p
    return None


def resolve_inputs(params_dir: Optional[Path]):
    here = Path(__file__).resolve().parent.parent
    cwd = Path.cwd().resolve()
    search_dirs = [params_dir.resolve()] if params_dir else [here, cwd]

    def candidates(fname: str):
        return [d / fname for d in search_dirs]

    gp = find_first(candidates("global_parameters_pp_v2.txt"))
    lp = find_first(candidates("laser_parameters_pp_v2.txt"))
    px = find_first(candidates("Ppp_analytic_expression.txt"))
    if not (gp and lp and px):
        raise FileNotFoundError("Missing legacy parameter files. Provide data/config.yaml or legacy TXT files.")
    return gp, lp, px


def _strip_inline_comment(s: str) -> str:
    cut = len(s)
    h = s.find('#')
    if h != -1:
        cut = min(cut, h)
    sl = s.find('//')
    if sl != -1:
        cut = min(cut, sl)
    return s[:cut].rstrip()


def read_kv_file(path: Path):
    kv = {}
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
        k = k.strip(); v = _strip_inline_comment(v.strip())
        if v:
            kv[k] = v
    return kv


def read_pulse_expression(path: Path) -> str:
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


def inject_parameters(model, params):
    parameters = model / "parameters"
    (parameters / "Parameters 1").rename("parameters")
    for k, v in params.items():
        model.parameter(k, v)
    params = dict(params)
    if "D_drop" not in params:
        if "R_drop" in params:
            model.parameter("D_drop", "2*R_drop"); params["D_drop"] = "2*R_drop"
        elif "R" in params:
            model.parameter("D_drop", "2*R"); params["D_drop"] = "2*R"
    return params


def build_model(no_solve: bool, params_dir: Optional[Path], out_dir: Optional[Path],
                absorption_model: str = "fresnel", check_only: bool = False):
    log = init_logger(level=os.environ.get("LOG_LEVEL", "INFO"))
    # If check-only: perform schema validation/migration dry-run and exit early
    if check_only and load_config is not None:
        try:
            ucfg, raw = load_config(params_dir)
            print("[CHECK] Schema version:", ucfg.schema_version)
            print("[CHECK] Absorption model:", absorption_model)
            print("[CHECK] Geometry (R,Lx,Ly):", ucfg.geometry.R, ucfg.geometry.Lx, ucfg.geometry.Ly)
            print("[CHECK] Laser (A_PP,w0,theta,mode):", ucfg.laser.A_PP, ucfg.laser.w0, ucfg.laser.laser_theta_deg, ucfg.laser.illum_mode)
            return None
        except Exception as e:
            print("[CHECK] Validation failed:", e, file=sys.stderr)
            sys.exit(2)

    gp_path, lp_path, pulse_path = resolve_inputs(params_dir)
    out_dir = (out_dir or Path(__file__).resolve().parent.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    OUT_MPH = out_dir / "pp_model_created.mph"
    PNG     = out_dir / "pp_temperature.png"
    CSV_T   = out_dir / "pp_T_vs_time.csv"
    CSV_M   = out_dir / "pp_massloss_vs_time.csv"
    CSV_R   = out_dir / "pp_radius_vs_time.csv"

    # (check-only handled above)

    # Import mph lazily to avoid hard dependency during tests
    import mph
    from .utils import retry
    # Small, bounded retry for transient session start failures
    with phase_timer(log, "mph_session"):
        client = retry(lambda: mph.start(), attempts=3, delay=1.0)
        model = client.create("pp_model")
    log_step(log, "mph_ready", pct=0.1)

    params = {}
    params.update(read_kv_file(gp_path))
    params.update(read_kv_file(lp_path))
    params = inject_parameters(model, params)
    log_step(log, "params_injected", pct=0.2)

    # Derive geometry aliases
    if "R" not in params:
        if "D_drop" in params:
            model.parameter("R", "D_drop/2"); params["R"] = "D_drop/2"
        elif "R_drop" in params:
            model.parameter("R", "R_drop"); params["R"] = "R_drop"
    if "Lx" not in params and "X_max" in params:
        model.parameter("Lx", "2*X_max"); params["Lx"] = "2*X_max"
    if "Ly" not in params and "Y_max" in params:
        model.parameter("Ly", "2*Y_max"); params["Ly"] = "2*Y_max"
    if "yCtr" not in params and "Ly" in params:
        model.parameter("yCtr", "Ly/2"); params["yCtr"] = "Ly/2"
    if params.get("y_beam") is None:
        model.parameter("y_beam", "yCtr"); params["y_beam"] = "yCtr"
    if params.get("x_beam") is None:
        model.parameter("x_beam", "Lx/2"); params["x_beam"] = "Lx/2"
    if "laser_theta_deg" not in params:
        model.parameter("laser_theta_deg", "0[deg]"); params["laser_theta_deg"] = "0[deg]"

    illum_mode = str(params.get("illum_mode", "cos_inc")).strip().lower()
    if illum_mode not in ("cos_inc", "nx_shadow"):
        illum_mode = "cos_inc"
    model.parameter("illum_cos", "1" if illum_mode == "cos_inc" else "0")
    params["illum_mode"] = illum_mode

    missing = []
    if not ("R" in params or "D_drop" in params or "R_drop" in params):
        missing.append("R or D_drop or R_drop")
    if not ("Lx" in params or "X_max" in params):
        missing.append("Lx or X_max")
    if not ("Ly" in params or "Y_max" in params):
        missing.append("Ly or Y_max")
    if missing:
        raise RuntimeError(f"Missing required parameters: {missing}\nIn: {gp_path}\nAnd: {lp_path}")

    # Optional YAML config
    cfg = None
    if load_config is not None:
        try:
            cfg, _ = load_config(params_dir)
        except Exception:
            cfg = None

    functions = model / "functions"
    Ppp = functions.create("Analytic", name="Ppp")
    Ppp.property("funcname", "Ppp")
    Ppp.property("args", ["t"])
    P_expr = read_pulse_expression(pulse_path)
    if cfg is not None and getattr(cfg, "laser", None) is not None and cfg.laser.temporal_profile:
        eps = "1e-12[s]"; t0 = "0[s]"
        if cfg.laser.temporal_profile == "square" and cfg.laser.tau_square:
            P_expr = f"(E_PP_total/{cfg.laser.tau_square})*(flc2hs(t-{t0},{eps})-flc2hs(t-({t0}+{cfg.laser.tau_square}),{eps}))"
        elif cfg.laser.temporal_profile in ("ramp_square", "ramp+square") and cfg.laser.tau_square:
            tau_r = cfg.laser.tau_ramp or 0.0; tau_s = cfg.laser.tau_square
            P_expr = (
                f"(E_PP_total/{tau_s})*min( (t-{t0})/({tau_r}+{eps}), 1)"
                f"*(flc2hs(t-{t0},{eps})-flc2hs(t-({t0}+{tau_r}+{tau_s}),{eps}))"
            )
    Ppp.property("expr", P_expr)

    psat = functions.create("Analytic", name="psat")
    psat.property("funcname", "p_sat")
    psat.property("args", ["T"])
    psat_expr = params.get("p_sat_expr")
    if absorption_model == "kumar" and not psat_expr:
        if "Lv_mol" not in params:
            model.parameter("Lv_mol", "L_v*M_Sn")
        if "T_boil" not in params:
            model.parameter("T_boil", "2875[K]")
        if "P_ref" not in params:
            model.parameter("P_ref", "101325[Pa]")
        psat_expr = "P_ref*exp( (Lv_mol/R_gas)*(1/T_boil - 1/T) )"
    psat.property("expr", psat_expr or "p_amb")

    # Optionally pick A_PP from precomputed tables (Sizyuk) or compute from n,k
    if absorption_model == "fresnel":
        Acalc = None
        if cfg is not None and getattr(cfg, "absorption", None) is not None and cfg.absorption.use_precomputed:
            Acalc = _pick_A_from_precomputed(cfg, repo_root=Path.cwd())
            # If missing and allowed to autogenerate, run pp_sizyuk to create tables
            if Acalc is None and cfg.absorption.autogenerate_if_missing and cfg.absorption.nk_file:
                try:
                    from ..pp_sizyuk import run_sizyuk
                except Exception:
                    from src.pp_sizyuk import run_sizyuk
                nkp = Path(cfg.absorption.nk_file)
                out_tables = Path.cwd() / "data" / "derived" / "sizyuk"
                out_plots = Path.cwd() / "results" / "sizyuk" / "plots"
                run_sizyuk(nkp, out_tables, out_plots, config=None)
                Acalc = _pick_A_from_precomputed(cfg, repo_root=Path.cwd())
        if Acalc is None:
            Acalc = compute_A_PP_from_nk(cfg)
        if Acalc is not None:
            model.parameter("A_PP", f"{Acalc:.6g}")

    components = model / "components"
    components.create(True, name="component"); comp = components / "component"
    geometries = model / "geometries"; geom = geometries.create(2, name="geometry")

    java_model = model.java; geom_tag = geom.tag()
    java_model.geom(geom_tag).feature().create("gas", "Rectangle")
    java_model.geom(geom_tag).feature("gas").set("pos",  ["0", "0"])
    java_model.geom(geom_tag).feature("gas").set("size", ["Lx", "Ly"]) 
    java_model.geom(geom_tag).feature().create("drop", "Circle")
    java_model.geom(geom_tag).feature("drop").set("r", "R")
    java_model.geom(geom_tag).feature("drop").set("pos", ["Lx/2", "Ly/2"]) 
    java_model.geom(geom_tag).feature().create("union", "Union")
    java_model.geom(geom_tag).feature("union").set("intbnd", "on")
    java_model.geom(geom_tag).feature("union").selection("input").set(["drop", "gas"]) 
    model.build(geom)
    log_step(log, "geometry_built", pct=0.35)

    selections_java = model.java.selection()
    selections_java.create("s_drop", "Disk"); sd = model.java.selection("s_drop")
    sd.set("type", "solid"); sd.set("r", "0.95*R"); sd.set("pos", ["Lx/2", "Ly/2"])
    selections_java.create("s_surf", "Adjacent"); ss = model.java.selection("s_surf")
    ss.set("input", ["s_drop"]); ss.set("type", "curve")
    selections_java.create("s_gas", "Complement"); sg = model.java.selection("s_gas")
    sg.set("input", ["s_drop"]); sg.set("type", "solid")

    cdefs = comp / "definitions"
    variables = cdefs.create("Variables", name="variables")
    variables.property("expr", [
        "I_xy = (2/(pi*w0^2))*Ppp(t)*exp(-2*((x-x_beam)^2+(y-y_beam)^2)/w0^2)",
        "theta_l = laser_theta_deg*pi/180",
        "kx = cos(theta_l)",
        "ky = sin(theta_l)",
        "cos_inc = max(0, -(nx*kx+ny*ky))",
        "inc_shadow = max(0, nx)",
        "inc_factor = illum_cos*cos_inc + (1-illum_cos)*inc_shadow",
        "q_abs_2D = A_PP*I_xy*inc_factor",
        "J_evap = HK_gamma*(p_sat(T)-p_amb)/sqrt(2*pi*R_gas*T/M_Sn)",
        "sigmaT = sigma0 + dSigma_dT*(T-T_ref)",
        "p_recoil = recoil_coeff*p_sat(T)",
        "Qb_eff = q_abs_2D - L_v*J_evap",
        "q_rad_if = epsilon_rad*sigma_SB*(T^4 - T_amb^4)",
        "rad = sqrt((x-Lx/2)^2+(y-Ly/2)^2)"
    ])
    variables.property("unit", ['W/m^2','W/m^2','kg/(m^2*s)','N/m','Pa','W/m^2','W/m^2','m'])
    variables.property("descr", [
        'Incident intensity (2D)',
        'Absorbed surface heat flux',
        'Evaporation mass flux',
        'Surface tension vs T',
        'Laser/plasma recoil pressure',
        'Net boundary heat flux on droplet',
        'Radius helper'
    ])

    int_surf = cdefs.create("Integration", name="intop_surf"); int_surf.property("entitydim", 1); int_surf.property("probetag", "none"); int_surf.select("s_surf")
    max_surf = cdefs.create("Maximum", name="maxop_surf"); max_surf.property("entitydim", 1); max_surf.property("probetag", "none"); max_surf.select("s_surf")
    int_drop = cdefs.create("Integration", name="intop_drop"); int_drop.property("entitydim", 2); int_drop.property("probetag", "none"); int_drop.select("s_drop")

    materials = model / "materials"
    tin = materials.create("Common", name="tin"); tin.select("s_drop")
    (tin / "Basic").property("density", ["rho_Sn"])
    (tin / "Basic").property("heatcapacity", ["cp_Sn"])
    (tin / "Basic").property("thermalconductivity", ["k_Sn"])
    (tin / "Basic").property("dynamicviscosity", ["mu_Sn"])
    gasm = materials.create("Common", name="gas"); gasm.select("s_gas")
    (gasm / "Basic").property("density", ["rho_gas"])
    (gasm / "Basic").property("heatcapacity", ["cp_gas"])
    (gasm / "Basic").property("thermalconductivity", ["k_gas"])
    (gasm / "Basic").property("dynamicviscosity", ["mu_gas"])

    physics = model / "physics"
    ht = physics.create("HeatTransferInFluids", geom, name="ht")
    bhf = ht.create("BoundaryHeatSource", 1, name="laser+latent"); bhf.select("s_surf")
    bhf.property("Qb", "q_abs_2D - L_v*J_evap")
    # Optional radiation
    if cfg is not None and getattr(cfg, "radiation", None) is not None and cfg.radiation.emissivity:
        radb = ht.create("SurfaceToAmbientRadiation", 1, name="radiation"); radb.select("s_surf")
        radb.property("epsilon_rad", str(cfg.radiation.emissivity)); radb.property("Tamb", "T_amb")

    tds = physics.create("TransportOfDilutedSpecies", geom, name="tds")
    evap = tds.create("Flux", 1, name="evaporation flux"); evap.select("s_surf"); evap.property("N0", "-J_evap")
    # Optional gas diffusion law
    if cfg is not None and getattr(cfg, "environment", None) is not None and cfg.environment.diffusivity_law:
        cdm_g = tds.create("ConvectionDiffusion", 2, name="gas transport"); cdm_g.select("s_gas")
        if cfg.environment.diffusivity_law == "t175_over_p":
            Dm0 = cfg.environment.Dm0 or 1.0e-3
            cdm_g.property("Dc", [[f"{Dm0}*(T/300[K])^1.75/max(p_amb,1[Pa])", "0", "0", "0",
                                     f"{Dm0}*(T/300[K])^1.75/max(p_amb,1[Pa])", "0", "0", "0",
                                     f"{Dm0}*(T/300[K])^1.75/max(p_amb,1[Pa])"]])

    spf = physics.create("LaminarFlow", geom, name="spf"); spf.select("s_drop")
    st = spf.create("SurfaceTension", 1, name="surface tension"); st.select("s_surf"); st.property("gamma", "sigmaT")
    mg = spf.create("Marangoni", 1, name="Marangoni"); mg.select("s_surf"); mg.property("dGammadT", "dSigma_dT")
    pr = spf.create("Pressure", 1, name="recoil pressure"); pr.select("s_surf"); pr.property("p0", "p_recoil")

    ale = physics.create("DeformingDomain", geom, name="ale")
    ale.create("FreeDeformation", 2, name="free deformation")
    vmesh = ale.create("PrescribedNormalMeshVelocity", 1, name="mesh follows fluid"); vmesh.select("s_surf"); vmesh.property("v", "u*nx+v*ny")
    if absorption_model == "kumar" and cfg is not None and getattr(cfg, "mesh", None) is not None and cfg.mesh.evaporation_mesh:
        vmesh2 = ale.create("PrescribedNormalMeshVelocity", 1, name="mesh evap drive"); vmesh2.select("s_surf"); vmesh2.property("v", "-J_evap/rho_Sn")

    # Kumar variant overrides
    if absorption_model == "kumar":
        # Heat source without incidence factor
        bhf.property("Qb", "A_PP*I_xy - L_v*J_evap")
        var_k = cdefs.create("Variables", name="variables_kumar")
        var_k.property("expr", [
            "inc_factor = 1",
            "J_evap = (1-beta_r)*p_sat(T)*sqrt(M_Sn/(2*pi*R_gas*T))",
            "J_evap = if(evap_clamp \\= 1, max(0,J_evap), J_evap)",
            "p_recoil = 0",
            "Qb_eff = A_PP*I_xy - L_v*J_evap",
        ])
        var_k.property("unit", ['1','kg/(m^2*s)','kg/(m^2*s)','Pa','W/m^2'])
        model.parameter("evap_clamp", "1" if (cfg and cfg.evaporation.clamp_nonneg) else "0")

        ht_gas = physics.create("HeatTransferInFluids", geom, name="ht_gas")
        bhs_g = ht_gas.create("BoundaryHeatSource", 1, name="latent_gas"); bhs_g.select("s_surf"); bhs_g.property("Qb", "L_v*J_evap")

        evap.property("N0", "-J_evap/M_Sn")

        pr.property("p0", "0")
        spf_g = physics.create("LaminarFlow", geom, name="spf_gas"); spf_g.select("s_gas")
        bs = spf_g.create("BoundaryStress", 1, name="gas_normal_stress"); bs.select("s_surf")
        bs.property("BoundaryCondition", "NormalStress"); bs.property("f0", "-(1+beta_r/2)*p_sat(T)")

    else:
        if cfg is not None and getattr(cfg, "evaporation", None) is not None and cfg.evaporation.clamp_nonneg:
            var_f = cdefs.create("Variables", name="variables_fresnel_clamp")
            var_f.property("expr", [
                "J_evap = max(0, HK_gamma*(p_sat(T)-p_amb)/sqrt(2*pi*R_gas*T/M_Sn))",
                "Qb_eff = q_abs_2D - L_v*J_evap",
            ])
            var_f.property("unit", ['kg/(m^2*s)','W/m^2'])
    log_step(log, "physics_setup", pct=0.6)

    meshes = model / "meshes"; mesh = meshes.create(geom, name="mesh")
    bl = mesh.create("BoundaryLayer", name="bl"); bl.select("s_surf")
    bl.property("n", params.get("n_bl", "5")); bl.property("thickness", params.get("bl_thick", "0.02*D_drop"))
    mesh.create("FreeTri", name="ftri")
    log_step(log, "mesh_ready", pct=0.75)

    studies = model / "studies"; solutions = model / "solutions"; study = studies.create(name="transient")
    study.java.setGenPlots(False); study.java.setGenConv(False)
    step = study.create("Transient", name="time-dependent"); tlist = params.get("tlist", "range(0, 1e-8, 200)"); step.property("tlist", tlist)
    sol = solutions.create(name="solution"); sol.java.study(study.tag()); sol.java.attach(study.tag())
    sol.create("StudyStep", name="equations"); sol.create("Variables", name="variables"); solver = sol.create("Time", name="time solver"); solver.property("tlist", tlist)
    if no_solve:
        log_step(log, "solve_skipped", pct=0.8)
    else:
        log_step(log, "solve_ready", pct=0.85)

    datasets = model / "datasets"; tables = model / "tables"
    tables.create("Table", name="T_vs_time"); tables.create("Table", name="mass_vs_time"); tables.create("Table", name="radius_vs_time"); tables.create("Table", name="energy_vs_time")
    evals = model / "evaluations"
    eT = evals.create("EvalGlobal", name="T_avg_drop"); eT.property("table", tables / "T_vs_time"); eT.property("expr", ["intop_drop(T)/intop_drop(1)"]); eT.property("unit", ["K"]); eT.java.setResult()
    eM = evals.create("EvalGlobal", name="mass loss rate"); eM.property("table", tables / "mass_vs_time"); eM.property("expr", ["intop_surf(J_evap)"]); eM.property("unit", ["kg/s"]); eM.java.setResult()
    eR = evals.create("EvalGlobal", name="apparent radius"); eR.property("table", tables / "radius_vs_time"); eR.property("expr", ["maxop_surf(rad)"]); eR.property("unit", ["m"]); eR.java.setResult()
    eP = evals.create("EvalGlobal", name="energy terms"); eP.property("table", tables / "energy_vs_time")
    if cfg is not None and getattr(cfg, "radiation", None) is not None and cfg.radiation.emissivity:
        eP.property("expr", ["intop_surf(q_abs_2D)", "intop_surf(L_v*J_evap)", "intop_surf(Qb_eff)", "intop_surf(q_rad_if)"])
        eP.property("unit", ["W", "W", "W", "W"]) 
        eP.property("descr", ["P_abs", "P_lat", "P_Qb_droplet", "P_rad"]) 
    else:
        eP.property("expr", ["intop_surf(q_abs_2D)", "intop_surf(L_v*J_evap)", "intop_surf(Qb_eff)"])
        eP.property("unit", ["W", "W", "W"]) 
        eP.property("descr", ["P_abs", "P_lat", "P_Qb_droplet"]) 
    eP.java.setResult()
    log_step(log, "postprocess_done", pct=1.0)

    plots = model / "plots"; plots.java.setOnlyPlotWhenRequested(True)
    pg = plots.create("PlotGroup2D", name="temperature field"); pg.property("titletype", "manual"); pg.property("title", "Temperature (K)")
    srf = pg.create("Surface", name="T"); srf.property("expr", "T"); srf.property("resolution", "normal")

    exports = model / "exports"
    img = exports.create("Image", name="image"); img.property("sourceobject", plots / "temperature field"); img.property("filename", str(PNG)); img.property("imagetype", "png"); img.property("size", "manualweb"); img.property("width", "1600"); img.property("height", "1200"); img.property("antialias", "on")
    dataT = exports.create("Table", name="T csv"); dataT.property("sourceobject", tables / "T_vs_time"); dataT.property("filename", str(CSV_T))
    dataM = exports.create("Table", name="M csv"); dataM.property("sourceobject", tables / "mass_vs_time"); dataM.property("filename", str(CSV_M))
    dataR = exports.create("Table", name="R csv"); dataR.property("sourceobject", tables / "radius_vs_time"); dataR.property("filename", str(CSV_R))
    dataE = exports.create("Table", name="E csv"); dataE.property("sourceobject", tables / "energy_vs_time"); dataE.property("filename", str(out_dir / "pp_energy_vs_time.csv"))

    model.save(str(OUT_MPH))
    try:
        milestone(log, "mph_saved", path=str(OUT_MPH))
    except Exception:
        pass
    if not no_solve:
        sol.java.run(); img.java.run(); dataT.java.run(); dataM.java.run(); dataR.java.run(); dataE.java.run(); model.save(str(OUT_MPH))

    try:
        from .provenance import write_metadata, git_commit_hash
        write_metadata(out_dir / "pp_metadata.json", {"schema_version": SCHEMA_VERSION, "absorption_model": absorption_model, "git_commit": git_commit_hash()})
    except Exception:
        pass

    print(f"[OK] saved MPH → {OUT_MPH}")
    if not no_solve:
        print(f"[OK] PNG      → {PNG}")
        print(f"[OK] CSVs     → {CSV_T} | {CSV_M} | {CSV_R} | {out_dir/'pp_energy_vs_time.csv'}")
    return model


def solve_and_export(model, out_dir: Path, no_solve: bool) -> None:
    """Run solve and export tables/plots assuming standard names from build_model.

    This is a thin adapter to support timing the solve phase via the runner
    without changing default behavior. It relies on object names created by
    build_model and filenames already set on exporters.
    """
    solutions = model / "solutions"; sol = solutions / "solution"
    exports = model / "exports"
    img = exports / "image"
    dataT = exports / "T csv"
    dataM = exports / "M csv"
    dataR = exports / "R csv"
    dataE = exports / "E csv"
    if not no_solve:
        sol.java.run(); img.java.run(); dataT.java.run(); dataM.java.run(); dataR.java.run(); dataE.java.run()
    # Save MPH again to ensure consistency
    model.save(str(Path(out_dir) / "pp_model_created.mph"))


def compute_A_PP_from_nk(cfg) -> Optional[float]:
    """Compute Fresnel absorptivity A from n,k at lambda_um if configured.

    Returns A in [0,1] or None if unavailable/misconfigured.
    """
    try:
        if cfg is None or getattr(cfg, "absorption", None) is None:
            return None
        ab = cfg.absorption
        if not getattr(ab, "use_nk", False):
            return None
        if not (ab.nk_file and ab.lambda_um):
            return None
        if _load_nk_excel is None or _absorptivity_from_nk is None:
            return None
        nk_path = Path(ab.nk_file)
        lam, n_arr, k_arr = _load_nk_excel(str(nk_path))
        if lam is None:
            return None
        return float(_absorptivity_from_nk(ab.lambda_um, lam, n_arr, k_arr))
    except Exception:
        return None


def _pick_A_from_precomputed(cfg, repo_root: Path) -> Optional[float]:
    """Load A(λ) from data/derived/sizyuk/ CSVs and return A at cfg.absorption.lambda_um (nearest)."""
    try:
        import pandas as pd
        if cfg is None or getattr(cfg, "absorption", None) is None:
            return None
        lam_sel = float(cfg.absorption.lambda_um or 0.0)
        if lam_sel <= 0:
            return None
        base = repo_root / "data" / "derived" / "sizyuk"
        fA = base / "absorptivity_vs_lambda.csv"
        if not fA.is_file():
            return None
        df = pd.read_csv(fA)
        if df.empty:
            return None
        # find nearest wavelength
        idx = (df["lambda_um"] - lam_sel).abs().idxmin()
        return float(df.loc[idx, "A"]) if "A" in df.columns else None
    except Exception:
        return None
