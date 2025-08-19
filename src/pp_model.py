"""
pp_model.py — CLI entrypoint for the 2D tin-droplet pre-pulse model.
Dispatches to variant builders in src/core/build.py via src/models/*.
"""

from pathlib import Path
from typing import Optional
import argparse
import sys
import os

# Additive imports (non-breaking)
try:
    from src.core.logging_utils import init_logger, write_provenance
    from src.core.config.loader import load_config
    from src.core.errors import ConfigError
except Exception:
    # Allow running as module or script without package context
    from core.logging_utils import init_logger, write_provenance
    from core.config.loader import load_config
    from core.errors import ConfigError


def main():
    """CLI: build (and optionally solve) the model via MPh."""
    ap = argparse.ArgumentParser(
        description="Build (and optionally solve) the pre-pulse tin droplet model via MPh."
    )
    ap.add_argument("--no-solve", action="store_true",
                    help="Build only; do not run the transient solver.")
    ap.add_argument("--params-dir", type=Path, default=None,
                    help="Directory containing global_parameters_pp_v2.txt, laser_parameters_pp_v2.txt, Ppp_analytic_expression.txt, or data/config.yaml.")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="Directory to write PNG/CSV/MPH (default: alongside this script).")
    ap.add_argument("--check-only", action="store_true", help="Validate config and exit without building the model.")
    ap.add_argument("--absorption-model", choices=["fresnel", "kumar"], default="fresnel",
                    help="Absorption/BC variant to use (default: fresnel).")
    ap.add_argument("--log-level", default=None, help="Optional log level: DEBUG|INFO|WARN|ERROR")
    args = ap.parse_args()

    try:
        # Lightweight structured logger
        level_env = args.log_level or os.environ.get("LOG_LEVEL", "INFO")
        log = init_logger(level=level_env)
        repo_root = Path(__file__).resolve().parents[1]

        # Optional: validate structured config if present (non-breaking)
        cfg_paths = [repo_root / "data" / "config.yaml", repo_root / "data" / "config.local.yaml"]
        if any(p.exists() for p in cfg_paths):
            try:
                cfg = load_config([p for p in cfg_paths if p.exists()])
                log("INFO", msg="Loaded structured config", paths=[str(p) for p in cfg_paths if p.exists()])
            except Exception as e:
                # Non-breaking: fall back to legacy path and warn
                log("WARN", msg="Structured config invalid; falling back to legacy params", error=str(e))

        # Validation-only path
        if args.check_only:
            try:
                from .core.build import build_model as core_build
            except Exception:
                from core.build import build_model as core_build
            core_build(
                no_solve=True,
                params_dir=args.params_dir,
                out_dir=args.out_dir,
                absorption_model=args.absorption_model,
                check_only=True,
            )
            # Write provenance for check-only as well
            out_dir = (args.out_dir or (repo_root / "results")).resolve()
            write_provenance(Path(out_dir) / "meta", config_dict={}, variant=args.absorption_model)
            return

        # Variant dispatch
        if args.absorption_model == "kumar":
            try:
                from .models.kumar_model import build as build_variant
            except Exception:
                from models.kumar_model import build as build_variant
        else:
            try:
                from .models.fresnel_model import build as build_variant
            except Exception:
                from models.fresnel_model import build as build_variant
        # Build variant
        build_variant(no_solve=args.no_solve, params_dir=args.params_dir, out_dir=args.out_dir)

        # Provenance for full runs
        out_dir = (args.out_dir or (repo_root / "results")).resolve()
        write_provenance(Path(out_dir) / "meta", config_dict={}, variant=args.absorption_model)
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
def load_fresnel_tables(repo_root: Path) -> dict:
    """Load precomputed Sizyuk tables (CSV) from data/derived/sizyuk.

    Returns a dict with pandas DataFrames for 'absorptivity', 'reflectivity' when present.
    Does not import COMSOL/mph; safe for tests.
    """
    import pandas as pd
    base = repo_root / "data" / "derived" / "sizyuk"
    out = {}
    fA = base / "absorptivity_vs_lambda.csv"
    fR = base / "reflectivity_vs_lambda.csv"
    if fA.is_file():
        out["absorptivity"] = pd.read_csv(fA)
    if fR.is_file():
        out["reflectivity"] = pd.read_csv(fR)
    return out
