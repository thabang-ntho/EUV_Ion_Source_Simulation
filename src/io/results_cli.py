from __future__ import annotations

import argparse
import json
from pathlib import Path
from .results import compare_results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compare two result directories containing CSV files.")
    ap.add_argument("--baseline", type=Path, required=True, help="Baseline results directory")
    ap.add_argument("--candidate", type=Path, required=True, help="Candidate results directory")
    ap.add_argument("--rtol", type=float, default=1e-5, help="Relative tolerance (default: 1e-5)")
    ap.add_argument("--atol", type=float, default=1e-8, help="Absolute tolerance (default: 1e-8)")
    ap.add_argument("--json", type=Path, default=None, help="Optional path to write JSON report")
    args = ap.parse_args(argv)

    ok, report = compare_results(args.baseline, args.candidate, rtol=args.rtol, atol=args.atol)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"ok": ok, "summary": report.get("files", {})}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

