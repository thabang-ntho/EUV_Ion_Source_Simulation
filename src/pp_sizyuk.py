"""
Sizyuk Fresnel Precompute and Utilities
--------------------------------------

Purpose
- Provide Fresnel/absorption precompute utilities based on Sizyuk-style optics.
- Produce small, versionable tables (CSV/JSON) for use by the main solver.
- Generate quick inspection plots to aid calibration and regression checks.

Inputs
- n,k optical data vs wavelength λ (xlsx or csv). Columns order: [λ(µm), n, k].

Outputs (canonical paths relative to repo root)
- Tables (for solver): `data/derived/sizyuk/`
  - `absorptivity_vs_lambda.csv` with columns: `lambda_um`, `A` (unitless)
  - `reflectivity_vs_lambda.csv` with columns: `lambda_um`, `R` (unitless)
  - `sizyuk_manifest.json` with summary metadata
- Plots (inspection): `results/sizyuk/plots/`
  - `absorptivity_vs_lambda.png`

Module API
- `run_sizyuk(nk_path, out_tables_dir, out_plots_dir, config)` to compute and save artifacts.

Assumptions & Units
- Power P(t): W, intensity I: W/m^2, flux q_abs: W/m^2, energy: J.
- Normal incidence absorptivity: A = 1 − R, with metal reflectance at normal incidence:
  R = ((n − n_m)^2 + k^2)/((n + n_m)^2 + k^2), default medium index n_m = 1.
- This module currently computes normal-incidence properties only; oblique incidence
  requires polarization-aware Fresnel equations and is left for a future extension within Sizyuk.
"""

from dataclasses import dataclass
import numpy as np
import math
from pathlib import Path
from typing import Optional, Dict

import json
import pandas as pd
import matplotlib.pyplot as plt
try:
    import yaml  # optional for CLI config parsing
except Exception:
    yaml = None

@dataclass
class Scenario:
    R: float                # droplet radius (m)
    w0: float               # 1/e^2 radius (m)
    x0: float = 0.0         # droplet center x (m)
    y0: float = 0.0         # droplet center y (m)
    x_beam: float = 0.0     # beam center x (m)
    y_beam: float = 0.0     # beam center y (m)
    use_area_average: bool = False  # if True, treat all power as on πR^2; else use Gaussian footprint

def load_nk_excel(path:str):
    df = None
    try:
        df = __import__('pandas').read_excel(path)
    except Exception:
        return None
    lam = __import__('pandas').to_numeric(df.iloc[:,0], errors='coerce').values
    n = __import__('pandas').to_numeric(df.iloc[:,1], errors='coerce').values
    k = __import__('pandas').to_numeric(df.iloc[:,2], errors='coerce').values
    mask = np.isfinite(lam) & np.isfinite(n) & np.isfinite(k)
    return lam[mask], n[mask], k[mask]

def absorptivity_from_nk(lam_um:float, lam_um_array, n_array, k_array, n_medium:float=1.0) -> float:
    n = float(np.interp(lam_um, lam_um_array, n_array))
    k = float(np.interp(lam_um, lam_um_array, k_array))
    R = ((n - n_medium)**2 + k**2) / ((n + n_medium)**2 + k**2)
    return 1.0 - R

def skin_depth_m(lam_um:float, lam_um_array, k_array) -> float:
    k = float(np.interp(lam_um, lam_um_array, k_array))
    lam_m = lam_um * 1e-6
    return lam_m/(4.0*math.pi*k)

def pulse_profile(E_total:float, tau_square:float, E_ramp:float=0.0, tau_ramp:float=0.0, dt:float=None):
    if dt is None:
        total_T = tau_square + max(tau_ramp, 0.0)
        dt = total_T/2000.0
    # Ramp
    if E_ramp > 0 and tau_ramp > 0:
        t_r = np.arange(-tau_ramp, 0.0, dt)
        a = 2*E_ramp/(tau_ramp**2)   # P = a*(t+tau_ramp)
        P_r = a*(t_r + tau_ramp)
    else:
        t_r = np.array([]); P_r = np.array([])
        E_ramp = 0.0; tau_ramp = 0.0
    # Square
    t_s = np.arange(0.0, tau_square+1e-30, dt)
    E_sq = E_total - E_ramp
    P_sq = E_sq/tau_square * np.ones_like(t_s)
    t = np.concatenate([t_r, t_s])
    P = np.concatenate([P_r, P_sq])
    return t, P

def gaussian_intensity(x, y, P_t, x0, y0, w0):
    """
    I(x,y,t) = (2/πw0^2) P(t) * exp(-2*r^2/w0^2), r^2=(x-x0)^2+(y-y0)^2
    Returns a 3D array with shape (len(t), len(y), len(x)) if x,y are arrays.
    """
    tlen = P_t.shape[0]
    X, Y = np.meshgrid(x, y, indexing='xy')
    r2 = (X - x0)**2 + (Y - y0)**2
    pre = 2.0/(math.pi*w0*w0)
    I_spatial = np.exp(-2.0*r2/(w0*w0))
    # time broadcast
    I = (pre * I_spatial[None, :, :] ) * P_t[:, None, None]
    return I  # W/m^2

def intercepted_fraction_gaussian(R:float, w0:float) -> float:
    return 1.0 - math.exp(-2.0*R*R/(w0*w0))


def q_abs_hemisphere(scn:Scenario, t:np.ndarray, P_t:np.ndarray, A:float):
    """
    Returns θ array (radians), time array t (passed in), and q_abs(θ,t) [W/m^2].
    θ measured from +x axis; hemisphere is |θ| <= π/2.
    q_abs(θ,t) = A * I_surf(θ,t) * max(0, cosθ).
    """
    th = np.linspace(-math.pi/2, math.pi/2, 361)
    x_s = scn.x0 + scn.R*np.cos(th)
    y_s = scn.y0 + scn.R*np.sin(th)
    r2 = (y_s - scn.y_beam)**2
    I_spatial = np.exp(-2.0*r2/(scn.w0*scn.w0))
    pre = 2.0/(math.pi*scn.w0*scn.w0)
    cos_inc = np.cos(th)
    q = A * pre * (P_t[:, None]) * (I_spatial[None, :]) * np.maximum(0.0, cos_inc[None, :])
    return th, t, q


def integrate_q_abs_sphere(R:float, th:np.ndarray, t:np.ndarray, q:np.ndarray) -> float:
    """
    Absorbed energy via surface integral (hemisphere once).
    Integrate over θ ∈ [0, π/2] with band area dA = 2π R^2 sinθ dθ.
    q already includes the cosθ incidence factor.
    """
    dθ = th[1] - th[0]
    dt = (t[1] - t[0]) if t.size > 1 else 1.0
    mask = th >= 0.0
    thp = th[mask]
    band = 2.0 * math.pi * R * R * np.sin(thp) * dθ
    E = np.sum(q[:, mask] * band[None, :]) * dt
    return float(E)


def _load_cfg(path: Optional[Path]) -> Optional[Dict]:
    """Load a small JSON or YAML config into a dict (or return None)."""
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    try:
        if p.suffix.lower() in (".yaml", ".yml") and yaml is not None:
            return yaml.safe_load(p.read_text(encoding="utf-8"))
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_nk_any(path: Path):
    """Load n,k data from xlsx or csv; returns (lambda_um, n, k) as 1D numpy arrays."""
    if path.suffix.lower() in (".xlsx", ".xls"):
        lam, n, k = load_nk_excel(str(path))
        return np.asarray(lam), np.asarray(n), np.asarray(k)
    # CSV: expect 3 columns (lambda_um, n, k) with or without headers
    df = pd.read_csv(path)
    if df.shape[1] < 3:
        raise ValueError("CSV must have at least 3 columns: lambda_um, n, k")
    lam = pd.to_numeric(df.iloc[:, 0], errors='coerce').values
    n = pd.to_numeric(df.iloc[:, 1], errors='coerce').values
    k = pd.to_numeric(df.iloc[:, 2], errors='coerce').values
    mask = np.isfinite(lam) & np.isfinite(n) & np.isfinite(k)
    return lam[mask], n[mask], k[mask]


def _plot_absorptivity(lambda_um: np.ndarray, A: np.ndarray, out_png: Path):
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(lambda_um, A, lw=2)
    ax.set_xlabel("Wavelength λ (µm)")
    ax.set_ylabel("Absorptivity A (normal incidence)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def run_sizyuk(nk_path: Path,
               out_tables_dir: Path,
               out_plots_dir: Path,
               config: Optional[Dict] = None) -> Dict:
    """Compute Fresnel/absorption-related parameters based on Sizyuk.

    Inputs
    - nk_path: path to n,k data file (xlsx/csv)
    - out_tables_dir: destination for CSV/JSON tables (created if missing)
    - out_plots_dir: destination for figures/plots (created if missing)
    - config: optional dict (e.g., {"n_medium": 1.0})

    Returns
    - dict manifest with file paths to generated tables/plots and summary stats

    Notes
    - Computes normal-incidence absorptivity only (consistent with utilities here).
    - All paths are written as provided (no repo-root inference).
    """
    out_tables_dir.mkdir(parents=True, exist_ok=True)
    out_plots_dir.mkdir(parents=True, exist_ok=True)
    lam_um, n_arr, k_arr = _load_nk_any(nk_path)
    n_medium = 1.0
    if config and isinstance(config, dict):
        n_medium = float(config.get("n_medium", 1.0))

    # Compute A and R at normal incidence across λ
    A = []
    for lam in lam_um:
        # reuse scalar function with array context
        A.append(absorptivity_from_nk(float(lam), lam_um, n_arr, k_arr, n_medium=n_medium))
    A = np.asarray(A)
    R = 1.0 - A

    # Save tables
    dfA = pd.DataFrame({"lambda_um": lam_um, "A": A})
    dfR = pd.DataFrame({"lambda_um": lam_um, "R": R})
    fA = out_tables_dir / "absorptivity_vs_lambda.csv"
    fR = out_tables_dir / "reflectivity_vs_lambda.csv"
    dfA.to_csv(fA, index=False)
    dfR.to_csv(fR, index=False)

    # Plot
    fA_png = out_plots_dir / "absorptivity_vs_lambda.png"
    _plot_absorptivity(lam_um, A, fA_png)

    # Manifest
    manifest = {
        "nk_file": str(nk_path),
        "tables": {
            "absorptivity_vs_lambda": str(fA),
            "reflectivity_vs_lambda": str(fR),
        },
        "plots": {
            "absorptivity_vs_lambda": str(fA_png)
        },
        "summary": {
            "n_medium": n_medium,
            "lambda_min_um": float(np.min(lam_um)) if lam_um.size else None,
            "lambda_max_um": float(np.max(lam_um)) if lam_um.size else None,
        }
    }
    # Write manifest JSON alongside tables
    (out_tables_dir / "sizyuk_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Sizyuk precompute (n,k → Fresnel params, plots)")
    ap.add_argument("--nk-file", required=True, help="Path to n,k xlsx/csv")
    ap.add_argument("--out-root", default="./", help="Repo-root-relative output base")
    ap.add_argument("--config", help="Optional JSON/YAML config file")
    args = ap.parse_args()

    root = Path(args.out_root).resolve()
    out_tables = root / "data" / "derived" / "sizyuk"
    out_plots = root / "results" / "sizyuk" / "plots"
    cfg = _load_cfg(Path(args.config)) if args.config else None
    manifest = run_sizyuk(Path(args.nk_file), out_tables, out_plots, cfg)
    print(json.dumps({"status": "ok", "outputs": manifest}, indent=2))
