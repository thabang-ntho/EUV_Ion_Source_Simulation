"""Parallel sweep stub (Phase 3).

This is a placeholder for a future process-based sweep runner. The default
sequential stub in `sweep.py` remains the preferred CI-safe path. When we add
parallelism, it will be guarded behind an explicit flag and configuration.
"""

from __future__ import annotations

from typing import Dict, Iterable, Any, Callable


def sweep_parallel(grid: Dict[str, Iterable[Any]], worker: Callable[[Dict[str, Any]], Any]):  # pragma: no cover
    raise NotImplementedError("Parallel sweeps are planned for Phase 3 and will remain opt-in.")

