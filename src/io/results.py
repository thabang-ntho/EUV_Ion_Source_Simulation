from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Iterable, Tuple
import json
import csv
import hashlib
import pandas as pd
import numpy as np


def write_manifest(path: Path, inputs: Dict[str, str] | Iterable[str], outputs: Dict[str, str] | Iterable[str], meta: Dict[str, Any] | None = None):
    def _norm(obj):
        if isinstance(obj, dict):
            return {k: str(Path(v)) for k, v in obj.items()}
        return [str(Path(p)) for p in obj]

    data = {
        "inputs": _norm(inputs),
        "outputs": _norm(outputs),
    }
    if meta:
        data.update(meta)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def compare_results(baseline_dir: Path, candidate_dir: Path, rtol: float = 1e-5, atol: float = 1e-8) -> Tuple[bool, Dict[str, Any]]:
    """Compare common CSV files in two directories within tolerances.

    Returns (ok, report). Report contains per-file status and max errors.
    Only compares columns that exist in both files and are numeric.
    """
    baseline_dir = Path(baseline_dir)
    candidate_dir = Path(candidate_dir)
    report: Dict[str, Any] = {"files": {}}
    ok_all = True

    def _numeric_cols(df: pd.DataFrame):
        return [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]

    for b in sorted(baseline_dir.glob("*.csv")):
        c = candidate_dir / b.name
        if not c.is_file():
            continue
        dfb = pd.read_csv(b)
        dfc = pd.read_csv(c)
        cols = [c for c in _numeric_cols(dfb) if c in dfc.columns and np.issubdtype(dfc[c].dtype, np.number)]
        if not cols:
            continue
        errors = {}
        file_ok = True
        for col in cols:
            a = dfb[col].to_numpy()
            d = dfc[col].to_numpy()
            n = min(len(a), len(d))
            if n == 0:
                continue
            a = a[:n]; d = d[:n]
            diff = np.abs(a - d)
            max_abs = float(np.max(diff))
            # Handle zeros for relative error
            denom = np.maximum(np.abs(a), np.abs(d))
            with np.errstate(divide='ignore', invalid='ignore'):
                rel = np.where(denom > 0, diff / denom, 0.0)
            max_rel = float(np.max(rel))
            this_ok = np.allclose(a, d, rtol=rtol, atol=atol, equal_nan=True)
            if not this_ok:
                file_ok = False
            errors[col] = {"max_abs": max_abs, "max_rel": max_rel, "ok": bool(this_ok)}
        report["files"][b.name] = {"ok": file_ok, "columns": errors}
        ok_all = ok_all and file_ok
    report["ok"] = ok_all
    report["rtol"] = rtol; report["atol"] = atol
    return ok_all, report


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_inputs_manifest_csv(out_dir: Path, inputs: Iterable[str | Path]) -> Path:
    out = Path(out_dir) / "inputs_manifest.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "exists", "sha256"]) 
        for p in inputs:
            pth = Path(p)
            w.writerow([str(pth), pth.exists(), _sha256(pth) or ""])
    return out


def write_outputs_manifest_csv(out_dir: Path, outputs: Iterable[str | Path]) -> Path:
    out = Path(out_dir) / "outputs_manifest.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "exists", "sha256"]) 
        for p in outputs:
            pth = Path(p)
            w.writerow([str(pth), pth.exists(), _sha256(pth) or ""])
    return out
