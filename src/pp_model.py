"""
pp_model.py — CLI entrypoint for the 2D tin-droplet pre-pulse model.
Dispatches to variant builders in src/core/build.py via src/models/*.
"""

from pathlib import Path
from typing import Optional
import argparse
import sys
import os
import json

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
    ap.add_argument("--emit-milestones", action="store_true",
                    help="Optional: emit build milestones and write perf_summary.json (additive, default off).")
    ap.add_argument("--use-adapter", action="store_true",
                    help="Optional: run a minimal adapter smoke (MPh session adapter) and exit. Default off.")
    ap.add_argument("--adapter-build", action="store_true",
                    help="Optional: build a trivial MPH model via adapter and save to out-dir; exits. Default off.")
    # Optional results comparison (additive)
    ap.add_argument("--compare-baseline", type=Path, default=None, help="Optional: baseline results directory (CSV)")
    ap.add_argument("--compare-candidate", type=Path, default=None, help="Optional: candidate results directory (CSV)")
    ap.add_argument("--compare-rtol", type=float, default=1e-5, help="Relative tolerance for comparison")
    ap.add_argument("--compare-atol", type=float, default=1e-8, help="Absolute tolerance for comparison")
    ap.add_argument("--compare-json", type=Path, default=None, help="Optional path to write full JSON comparison report")
    args = ap.parse_args()

    try:
        # Lightweight structured logger
        level_env = args.log_level or os.environ.get("LOG_LEVEL", "INFO")
        log = init_logger(level=level_env)
        repo_root = Path(__file__).resolve().parents[1]

        # Optional: adapter smoke (non-breaking, exits early on success)
        if args.use_adapter:
            try:
                from .core.adapters.mph_adapter import MphSessionAdapter, ModelAdapter
            except Exception:
                from core.adapters.mph_adapter import MphSessionAdapter, ModelAdapter
            try:
                from .core.logging_utils import milestone
            except Exception:
                from core.logging_utils import milestone
            adapter = MphSessionAdapter(retries=1, delay=0.0)
            with adapter.open() as client:
                model = ModelAdapter(client).create_model("adapter_smoke")
                _ = model  # no-op
            milestone(log, "adapter_smoke_ok")
            return

        # Optional: adapter-build smoke — create a trivial model and save it
        if args.adapter_build:
            try:
                from .core.adapters.mph_adapter import MphSessionAdapter, ModelAdapter
            except Exception:
                from core.adapters.mph_adapter import MphSessionAdapter, ModelAdapter
            out_dir = (args.out_dir or (repo_root / "results")).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            mph_path = out_dir / "pp_adapter_build.mph"
            adapter = MphSessionAdapter(retries=1, delay=0.0)
            with adapter.open() as client:
                model = ModelAdapter(client).create_model("pp_adapter_build")
                # Best-effort save
                try:
                    model.save(str(mph_path))  # type: ignore[attr-defined]
                except Exception:
                    # Some mocked models may have a different save API; create a placeholder
                    mph_path.write_text("adapter-build placeholder", encoding="utf-8")
            log("INFO", event="adapter_build_saved", path=str(mph_path))
            # Write a tiny outputs manifest
            import csv
            from hashlib import sha256
            man = out_dir / "outputs_manifest.csv"
            with man.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["path", "exists", "sha256"])
                h = ""
                if mph_path.is_file():
                    hobj = sha256()
                    with mph_path.open("rb") as rf:
                        for ch in iter(lambda: rf.read(65536), b""):
                            hobj.update(ch)
                    h = hobj.hexdigest()
                w.writerow([str(mph_path), mph_path.exists(), h])
            return

        # Optional: results comparison mode (no build)
        if args.compare_baseline and args.compare_candidate:
            try:
                from .io.results import compare_results as _compare
            except Exception:
                from src.io.results import compare_results as _compare
            ok, report = _compare(args.compare_baseline, args.compare_candidate, rtol=args.compare_rtol, atol=args.compare_atol)
            if args.compare_json:
                args.compare_json.parent.mkdir(parents=True, exist_ok=True)
                args.compare_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(json.dumps({"ok": ok, "summary": report.get("files", {})}, indent=2))
            # One-line summary for humans
            files = report.get("files", {})
            n_total = len(files)
            n_bad = sum(1 for v in files.values() if not v.get("ok", False))
            status = "OK" if ok else f"FAILED ({n_bad}/{n_total} files over tolerance)"
            print(f"Comparison: {status}")
            sys.exit(0 if ok else 1)

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
            # If requested, wrap with runner to emit explicit milestones and perf
            if args.emit_milestones:
                try:
                    from .core.solvers.runner import run as runner_run
                except Exception:
                    from core.solvers.runner import run as runner_run
                out_dir = (args.out_dir or (repo_root / "results")).resolve()
                runner_run(
                    mode="check",
                    build_fn=lambda: core_build(
                        no_solve=True,
                        params_dir=args.params_dir,
                        out_dir=args.out_dir,
                        absorption_model=args.absorption_model,
                        check_only=True,
                    ),
                    out_dir=out_dir,
                    meta={"variant": args.absorption_model},
                )
            else:
                core_build(
                    no_solve=True,
                    params_dir=args.params_dir,
                    out_dir=args.out_dir,
                    absorption_model=args.absorption_model,
                    check_only=True,
                )
            # Write provenance for check-only as well (include inputs manifest when possible)
            out_dir = (args.out_dir or (repo_root / "results")).resolve()
            inputs = []
            # Prefer structured config
            present_cfgs = [p for p in cfg_paths if p.exists()]
            if present_cfgs:
                inputs.extend([str(p) for p in present_cfgs])
            else:
                # Fallback to legacy param files
                try:
                    from .core.build import resolve_inputs as _resolve_inputs
                except Exception:
                    from core.build import resolve_inputs as _resolve_inputs
                try:
                    gp, lp, px = _resolve_inputs(args.params_dir)
                    inputs.extend([str(gp), str(lp), str(px)])
                except Exception:
                    pass
            # Include Sizyuk tables if Fresnel and present
            if args.absorption_model == "fresnel":
                sizyuk_dir = repo_root / "data" / "derived" / "sizyuk"
                for fn in ("absorptivity_vs_lambda.csv", "reflectivity_vs_lambda.csv", "sizyuk_manifest.json"):
                    p = sizyuk_dir / fn
                    if p.is_file():
                        inputs.append(str(p))
            meta = write_provenance(Path(out_dir) / "meta", config_dict={}, variant=args.absorption_model, extras={"inputs": inputs} if inputs else None)
            # Write inputs manifest CSV for check-only (portable)
            if inputs:
                import csv
                from hashlib import sha256
                man = Path(out_dir) / "inputs_manifest.csv"
                with man.open("w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f); w.writerow(["path", "exists", "sha256"])
                    for p in inputs:
                        pth = Path(p); h = ""
                        if pth.is_file():
                            hobj = sha256()
                            with pth.open("rb") as rf:
                                for ch in iter(lambda: rf.read(65536), b""):
                                    hobj.update(ch)
                            h = hobj.hexdigest()
                        w.writerow([str(pth), pth.exists(), h])
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
        # Build (and possibly solve) with optional milestone runner
        if args.emit_milestones:
            try:
                from .core.solvers.runner import run as runner_run
            except Exception:
                from core.solvers.runner import run as runner_run
            out_dir_resolved = (args.out_dir or (repo_root / "results")).resolve()
            mode = "build" if args.no_solve else "solve"
            if mode == "solve":
                # Provide a solve_fn to time the solve/export phase separately
                try:
                    from .core.build import solve_and_export as core_solve
                except Exception:
                    from core.build import solve_and_export as core_solve
                runner_run(
                    mode=mode,
                    build_fn=lambda: build_variant(no_solve=True, params_dir=args.params_dir, out_dir=args.out_dir),
                    solve_fn=lambda model: core_solve(model, out_dir_resolved, no_solve=False),
                    out_dir=out_dir_resolved,
                    meta={"variant": args.absorption_model},
                )
            else:
                runner_run(
                    mode=mode,
                    build_fn=lambda: build_variant(no_solve=True, params_dir=args.params_dir, out_dir=args.out_dir),
                    solve_fn=None,
                    out_dir=out_dir_resolved,
                    meta={"variant": args.absorption_model},
                )
        else:
            build_variant(no_solve=args.no_solve, params_dir=args.params_dir, out_dir=args.out_dir)

        # Provenance for full runs (include inputs manifest when possible)
        out_dir = (args.out_dir or (repo_root / "results")).resolve()
        inputs = []
        present_cfgs = [p for p in cfg_paths if p.exists()]
        if present_cfgs:
            inputs.extend([str(p) for p in present_cfgs])
        else:
            try:
                from .core.build import resolve_inputs as _resolve_inputs
            except Exception:
                from core.build import resolve_inputs as _resolve_inputs
            try:
                gp, lp, px = _resolve_inputs(args.params_dir)
                inputs.extend([str(gp), str(lp), str(px)])
            except Exception:
                pass
        if args.absorption_model == "fresnel":
            sizyuk_dir = repo_root / "data" / "derived" / "sizyuk"
            for fn in ("absorptivity_vs_lambda.csv", "reflectivity_vs_lambda.csv", "sizyuk_manifest.json"):
                p = sizyuk_dir / fn
                if p.is_file():
                    inputs.append(str(p))
        meta = write_provenance(Path(out_dir) / "meta", config_dict={}, variant=args.absorption_model, extras={"inputs": inputs} if inputs else None)
        # Write CSV manifests for quick browsing (additive; portable)
        import csv
        from hashlib import sha256
        if inputs:
            man = Path(out_dir) / "inputs_manifest.csv"
            with man.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["path", "exists", "sha256"])
                for p in inputs:
                    pth = Path(p); h = ""
                    if pth.is_file():
                        hobj = sha256()
                        with pth.open("rb") as rf:
                            for ch in iter(lambda: rf.read(65536), b""):
                                hobj.update(ch)
                        h = hobj.hexdigest()
                    w.writerow([str(pth), pth.exists(), h])
        outs = [
            out_dir / "pp_model_created.mph",
            out_dir / "pp_temperature.png",
            out_dir / "pp_T_vs_time.csv",
            out_dir / "pp_massloss_vs_time.csv",
            out_dir / "pp_radius_vs_time.csv",
            out_dir / "pp_energy_vs_time.csv",
        ]
        man_o = Path(out_dir) / "outputs_manifest.csv"
        with man_o.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["path", "exists", "sha256"])
            for p in outs:
                pth = Path(p); h = ""
                if pth.is_file():
                    hobj = sha256()
                    with pth.open("rb") as rf:
                        for ch in iter(lambda: rf.read(65536), b""):
                            hobj.update(ch)
                    h = hobj.hexdigest()
                w.writerow([str(pth), pth.exists(), h])
    except Exception as e:
        # Map to standardized exit codes when possible
        try:
            from src.core.errors import ConfigError, LicenseError, ComsolConnectError, EXIT_CONFIG, EXIT_LICENSE, EXIT_RUNTIME
        except Exception:
            from core.errors import ConfigError, LicenseError, ComsolConnectError, EXIT_CONFIG, EXIT_LICENSE, EXIT_RUNTIME
        code = EXIT_RUNTIME
        if isinstance(e, (LicenseError, ComsolConnectError)):
            code = EXIT_LICENSE
        elif isinstance(e, ConfigError):
            code = EXIT_CONFIG
        print("\n[ERROR] Build failed:")
        print(f"  {e}\n", file=sys.stderr)
        # If enhanced errors include a suggested fix, show it
        fix = getattr(e, "suggested_fix", None)
        print("Hints:")
        if fix:
            print(f"  • {fix}")
        print("  • Ensure MPh can find COMSOL (set COMSOL_HOME if needed).")
        print("  • Verify parameter files contain D_drop (or R_drop), X_max, Y_max, etc.")
        print("  • Inline comments with # or // are OK now; the loader strips them.")
        print("  • Run with --params-dir if your files are not next to this script.")
        sys.exit(code)


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
