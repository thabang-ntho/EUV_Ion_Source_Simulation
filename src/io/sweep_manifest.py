from __future__ import annotations

"""Sweep manifest writer (default-off utility).

This helper writes a small JSON index for sweep runs so results can be browsed
and compared easily. It is additive and not used by default.
"""

from pathlib import Path
from typing import Iterable, Mapping, Any
import json, time


def write_sweep_manifest(path: Path, runs: Iterable[Mapping[str, Any]], schema_version: str | None = None) -> Path:
    """Write a sweep manifest JSON file.

    Inputs
    - path: output JSON path
    - runs: iterable of per-run dict entries, suggested keys:
        {"run_id": str, "params": dict, "out_dir": str, "metrics": dict}
    - schema_version: optional string describing the sweep manifest schema

    Returns the written path.
    """
    # Best-effort tool version (optional)
    try:
        import importlib.metadata as _im
        tool_version = _im.version("euv_simulation")
    except Exception:
        tool_version = None
    data = {
        "schema": schema_version or "sweep-manifest/0",
        "tool_version": tool_version,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runs": list(runs),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path
