from __future__ import annotations

from itertools import product
from typing import Dict, Iterable, List, Tuple, Callable, Any


def sweep(grid: Dict[str, Iterable[Any]], worker: Callable[[Dict[str, Any]], Any]) -> List[Tuple[Dict[str, Any], Any]]:
    """Sequential sweep over a small parameter grid (Phase 3 stub).

    - No multiprocessing by default (keeps CI simple, COMSOL-free).
    - Designed to be called with check-only workers or light functions.
    """
    keys = list(grid.keys())
    combos = []
    for values in product(*[list(grid[k]) for k in keys]):
        cfg = {k: v for k, v in zip(keys, values)}
        combos.append((cfg, worker(cfg)))
    return combos

