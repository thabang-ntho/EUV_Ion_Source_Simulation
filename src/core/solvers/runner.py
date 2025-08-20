from __future__ import annotations

from pathlib import Path
from typing import Literal, Any, Dict
import time
import json

from ..logging_utils import init_logger, milestone, phase_timer


def _fmt_dt(seconds: float) -> str:
    msec = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    minutes = int(seconds) // 60
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}:{s:02d}.{msec:03d}"


def run(mode: Literal["check", "build", "solve"], build_fn, solve_fn=None, out_dir: Path | None = None, meta: Dict[str, Any] | None = None):
    """Lightweight runner that emits milestones and writes perf_summary.json.

    - mode=check: calls build_fn with no solve and returns.
    - mode=build: calls build_fn and saves perf.
    - mode=solve: calls build_fn then solve_fn if provided.
    """
    log = init_logger()
    out = Path(out_dir or ".").resolve()
    out.mkdir(parents=True, exist_ok=True)

    perf = {"mode": mode, "t0": time.time()}
    milestone(log, "build_start", **(meta or {}))
    with phase_timer(log, "build"):
        model = build_fn()
    milestone(log, "build_done")
    perf["build_done"] = time.time()
    perf["build_dt_s"] = perf["build_done"] - perf["t0"]
    perf["build_dt_str"] = _fmt_dt(perf["build_dt_s"])  # HH:MM:SS.mmm

    if mode == "check":
        _write_perf(out / "perf_summary.json", perf)
        return model

    if mode == "solve" and solve_fn is not None:
        milestone(log, "pre_solve")
        with phase_timer(log, "solve"):
            solve_fn(model)
        milestone(log, "post_solve")
        perf["solve_done"] = time.time()
        perf["solve_dt_s"] = perf["solve_done"] - perf["build_done"]
        perf["solve_dt_str"] = _fmt_dt(perf.get("solve_dt_s", 0.0))

    _write_perf(out / "perf_summary.json", perf)
    return model


def _write_perf(path: Path, data: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
