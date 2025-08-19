from __future__ import annotations
from pathlib import Path
from typing import Iterable
import yaml
from .models import RootConfig

def _normalize_legacy_keys(d: dict) -> dict:
    """Best-effort mapping of a few legacy names to structured keys.

    Non-destructive: only adds missing structured keys if legacy ones exist.
    """
    out = dict(d)
    sim = out.get("simulation") or {}
    # Already handled via validation_alias in models, but keep here if nested merges change precedence
    if "t_end" not in sim and "time_end" in sim:
        sim["t_end"] = sim.get("time_end")
    out["simulation"] = sim
    return out

_CONFIG_CACHE: dict[str, RootConfig] = {}


def _load_any(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data or {}


def _deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(paths: Iterable[Path]) -> RootConfig:
    paths = [Path(p) for p in paths]
    key = "|".join(str(p.resolve()) for p in paths)
    if key in _CONFIG_CACHE:
        return _CONFIG_CACHE[key]
    merged: dict = {}
    for p in paths:
        if p.exists():
            merged = _deep_merge(merged, _load_any(p))
    # Apply a small normalization pass for legacy-friendly keys
    merged = _normalize_legacy_keys(merged)
    cfg = RootConfig.model_validate(merged)
    _CONFIG_CACHE[key] = cfg
    return cfg


def cache_config(cfg: RootConfig) -> RootConfig:
    _CONFIG_CACHE["__single__"] = cfg
    return cfg
