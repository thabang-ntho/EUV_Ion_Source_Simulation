from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Any

from src.core.solvers.sweep import sweep


def run_demo(out_csv: Path) -> Path:
    grid: Dict[str, Any] = {"a": [1, 2, 3], "b": ["x", "y"]}

    def worker(cfg: Dict[str, Any]) -> str:
        return f"{cfg['a']}{cfg['b']}"

    results = sweep(grid, worker)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["a", "b", "value"])
        for cfg, res in results:
            w.writerow([cfg["a"], cfg["b"], res])
    return out_csv


if __name__ == "__main__":
    path = Path("results/sweep_demo.csv")
    p = run_demo(path)
    print(f"Wrote {p}")

