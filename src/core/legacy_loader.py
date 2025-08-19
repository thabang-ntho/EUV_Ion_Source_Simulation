from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple


def _read_txt(path: Path) -> Dict[str, str]:
    kv: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith(("#", "//")):
            continue
        if "=" in s:
            k, v = s.split("=", 1)
        else:
            parts = s.split(None, 1)
            if len(parts) != 2:
                continue
            k, v = parts
        kv[k.strip()] = v.strip()
    return kv


def load_legacy_params(params_dir: Path) -> Dict[str, object]:
    gp = params_dir / "global_parameters_pp_v2.txt"
    lp = params_dir / "laser_parameters_pp_v2.txt"
    pulse = params_dir / "Ppp_analytic_expression.txt"
    if not (gp.is_file() and lp.is_file() and pulse.is_file()):
        raise FileNotFoundError(
            f"Legacy files not found in {params_dir}: {gp.name}, {lp.name}, {pulse.name}"
        )
    g = _read_txt(gp)
    l = _read_txt(lp)

    # Map legacy keys to unified schema skeleton
    # Best-effort: require R/Lx/Ly derivable; fall back to X_max/Y_max
    geom: Dict[str, float] = {}
    if "R" in g:
        geom["R"] = float(g["R"].split("[")[0])
    elif "R_drop" in g:
        geom["R"] = float(g["R_drop"].split("[")[0])
    elif "D_drop" in g:
        geom["R"] = float(g["D_drop"].split("[")[0]) / 2.0
    if "Lx" in g:
        geom["Lx"] = float(g["Lx"].split("[")[0])
    elif "X_max" in g:
        geom["Lx"] = 2.0 * float(g["X_max"].split("[")[0])
    if "Ly" in g:
        geom["Ly"] = float(g["Ly"].split("[")[0])
    elif "Y_max" in g:
        geom["Ly"] = 2.0 * float(g["Y_max"].split("[")[0])

    raw = {
        "schema_version": "0.1.0",
        "simulation": {
            "time_end": 1e-7,
        },
        "geometry": geom,
        "materials": {
            "rho_Sn": float(g.get("rho_Sn", "6970").split("[")[0]),
            "cp_Sn": float(g.get("cp_Sn", "255").split("[")[0]),
            "k_Sn": float(g.get("k_Sn", "33").split("[")[0]),
            "mu_Sn": float(g.get("mu_Sn", "0.002").split("[")[0]),
            "M_Sn": float(g.get("M_Sn", "118.71e-3").split("[")[0]),
            "L_v": float(g.get("L_v", "2.96e6").split("[")[0]),
            "sigma0": float(g.get("sigma0", "0.55").split("[")[0]),
            "dSigma_dT": float(g.get("dSigma_dT", "-3e-4").split("[")[0]),
            "T_ref": float(g.get("T_ref", "505").split("[")[0]),
        },
        "environment": {
            "gas": "none",
            "pressure_torr": None,
            "p_amb": float(g.get("p_amb", "0").split("[")[0]) if "p_amb" in g else None,
            "T_amb": float(g.get("T_amb", "300").split("[")[0]) if "T_amb" in g else 300.0,
        },
        "laser": {
            "A_PP": float(l.get("A_PP", "0.3")),
            "w0": float(l.get("w0", l.get("d_beam", "20e-6")).split("[")[0]) / (1.0 if "w0" in l else (2.0**0.5)),
            "E_PP_total": float(l.get("E_PP_total", l.get("E_PP", "8e-4")).split("[")[0]),
            "temporal_profile": None,
            "tau_ramp": float(l.get("tau_ramp", "0").split("[")[0]) if "tau_ramp" in l else None,
            "tau_square": float(l.get("tau_square", "0").split("[")[0]) if "tau_square" in l else None,
            "laser_theta_deg": float(l.get("laser_theta_deg", "0").split("[")[0]),
            "illum_mode": l.get("illum_mode", "cos_inc"),
        },
        "absorption": {
            "model": "fresnel",
        },
        "evaporation": {
            "HK_gamma": float(l.get("HK_gamma", "1.0")) if "HK_gamma" in l else None,
            "p_sat_option": None,
            "p_sat_expr": g.get("p_sat_expr") or l.get("p_sat_expr"),
            "beta_r": float(l.get("beta_r", "0.0")) if "beta_r" in l else None,
        },
        "radiation": {
            "emissivity": float(g.get("emissivity", "0.0")) if "emissivity" in g else None,
        },
        "mesh": {
            "n_bl": int(g.get("n_bl", "5")) if "n_bl" in g else None,
            "bl_thick": float(g.get("bl_thick", "0").split("[")[0]) if "bl_thick" in g else None,
        },
        "outputs": {
            "out_dir": None,
        },
    }
    return raw

