"""
CLI for building and optionally solving the COMSOL model via MPh.

Usage examples:
  - Build only (no solve), save mph:
      python -m src.cli.mph_runner --check-only --variant fresnel
  - Build and solve, with custom output:
      python -m src.cli.mph_runner --solve --variant kumar --output results/kumar_run.mph
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import yaml
import logging

from src.mph_core.model_builder import ModelBuilder


def _load_params(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r") as f:
        return yaml.safe_load(f) or {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build and optionally solve the EUV droplet model via MPh/COMSOL.",
        epilog=(
            "Examples:\n"
            "  euv-mph --check-only --variant fresnel\n"
            "  euv-mph --solve --variant fresnel --host 127.0.0.1 --port 2036\n"
            "  euv-mph --check-only --variant kumar --output results/kumar_run.mph\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--variant", choices=["fresnel", "kumar"], default="fresnel", help="Physics variant")
    parser.add_argument("--config", type=str, default="data/config.yaml", help="YAML config path")
    parser.add_argument("--output", type=str, default=None, help="Output .mph file path")
    mx = parser.add_mutually_exclusive_group()
    mx.add_argument("--check-only", action="store_true", help="Build only, no solve")
    mx.add_argument("--solve", action="store_true", help="Build and solve")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--host", type=str, default=None, help="COMSOL host (optional)")
    parser.add_argument("--port", type=int, default=None, help="COMSOL port (optional)")
    parser.add_argument("--cores", type=int, default=None, help="Cores for COMSOL server (optional)")
    parser.add_argument("--version", action="version", version="euv-mph runner 0.1")

    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    # Honor host/port via environment for compatibility with mph.start
    if args.host:
        os.environ["COMSOL_HOST"] = args.host
    if args.port:
        os.environ["COMSOL_PORT"] = str(args.port)

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        logging.warning(f"Config not found at {cfg_path}; continuing with empty params.")
        params = {}
    else:
        params = _load_params(cfg_path)

    # Flatten top-level section keys into a single dict for builders expecting simple params
    flat_params = {}
    for k, v in params.items():
        if isinstance(v, dict):
            flat_params.update(v)
        else:
            flat_params[k] = v
    # Preserve variant for provenance in results
    flat_params["Variant"] = args.variant

    # Build
    builder = ModelBuilder(flat_params, args.variant)
    out_path = builder.build_complete_model(Path(args.output) if args.output else None)
    logging.info(f"Model saved to: {out_path}")

    # Solve if requested
    if args.solve and not args.check_only:
        ok = builder.study_manager.run_study("transient")
        if not ok:
            logging.error("Study solve failed")
            return 2
        # Save post-solve snapshot
        solved_path = Path(out_path).with_name(Path(out_path).stem + "_solved.mph")
        try:
            builder.model.save(str(solved_path))
            logging.info(f"Solved model saved to: {solved_path}")
        except Exception as e:
            logging.warning(f"Failed saving solved model: {e}")

    # Cleanup connection
    builder.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
