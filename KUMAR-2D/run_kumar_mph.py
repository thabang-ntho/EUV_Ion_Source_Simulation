"""
Kumar 2D Demo — MPh Python Runner (architecture-aligned)

Builds (and optionally solves) the Kumar 2D model using the same
src/mph_core architecture. Reads parameters from KUMAR-2D/parameters.txt
and saves the .mph file under KUMAR-2D/results/.

Usage examples:
  python KUMAR-2D/run_kumar_mph.py --dry-run
  python KUMAR-2D/run_kumar_mph.py --check-only
  python KUMAR-2D/run_kumar_mph.py --solve --host 127.0.0.1 --port 2036
"""

from __future__ import annotations

import argparse
from pathlib import Path
import os
import sys
import logging

# Add the project root to Python path
THIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from src.mph_core.model_builder import ModelBuilder


def parse_param_file(p: Path) -> dict[str, str]:
    params: dict[str, str] = {}
    for line in p.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith('%') or s.startswith('#'):
            continue
        parts = s.split()
        if len(parts) < 2:
            continue
        key = parts[0]
        val = ' '.join(parts[1:])
        # Stop at trailing inline comment tokens
        if '"""' in val:
            val = val.split('"""', 1)[0].strip()
        if '#' in val:
            val = val.split('#', 1)[0].strip()
        params[key] = val
    return params


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kumar 2D — MPh runner (aligned with mph_core architecture)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="No COMSOL; print plan and exit")
    g.add_argument("--check-only", action="store_true", help="Build only, no solve")
    g.add_argument("--solve", action="store_true", help="Build and solve")
    ap.add_argument("--host", type=str, default=None, help="COMSOL host")
    ap.add_argument("--port", type=int, default=None, help="COMSOL port")
    ap.add_argument("--cores", type=int, default=None, help="Server cores (optional)")
    ap.add_argument("--out", type=str, default=str(THIS_DIR / "results" / "kumar2d_model.mph"), help="Output mph path")
    ap.add_argument("--log-level", type=str, default="INFO")
    args = ap.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    params_file = THIS_DIR / "parameters.txt"
    if not params_file.exists():
        logging.error(f"Parameters file not found: {params_file}")
        return 2
    raw_params = parse_param_file(params_file)

    # Flatten into mph_core expected keys (we retain strings with units)
    flat_params = dict(raw_params)
    flat_params.setdefault('Output_Directory', str(THIS_DIR / 'results'))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        logging.info("Dry-run: no COMSOL. Summary:")
        logging.info(f"Params from: {params_file}")
        logging.info(f"Variant=kumar Output={out_path}")
        logging.info(f"Host={args.host or os.environ.get('COMSOL_HOST')} Port={args.port or os.environ.get('COMSOL_PORT')} Cores={args.cores or os.environ.get('COMSOL_CORES')}")
        logging.info("Planned steps: connect→create model→geometry→selections→materials→physics(Kumar)→studies→save .mph")
        return 0

    # Set environment variables for COMSOL connection if provided
    if args.host:
        os.environ['COMSOL_HOST'] = args.host
    if args.port:
        os.environ['COMSOL_PORT'] = str(args.port)
    if args.cores:
        os.environ['COMSOL_CORES'] = str(args.cores)

    # Build via mph_core ModelBuilder
    builder = ModelBuilder(flat_params, 'kumar')

    # Execute staged build to allow for Kumar-specific hooks later if desired
    builder._connect_to_comsol()
    builder._create_model()
    builder._set_parameters()
    builder._build_geometry()
    builder._create_selections()
    builder._setup_materials()
    builder._setup_physics()
    builder._create_studies()
    saved = builder._save_model(out_path)
    logging.info(f"Saved model: {saved}")

    if args.solve and not args.check_only:
        ok = builder.study_manager.run_study('transient')
        if not ok:
            logging.error("Solve failed")
            return 3
        # Save solved snapshot
        solved = out_path.with_name(out_path.stem + "_solved.mph")
        try:
            builder.model.save(str(solved))
            logging.info(f"Solved model saved: {solved}")
        except Exception as e:
            logging.warning(f"Failed to save solved model: {e}")

    builder.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

