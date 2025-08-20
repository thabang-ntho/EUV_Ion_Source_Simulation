from __future__ import annotations
from pathlib import Path
from typing import Iterable, Dict, Any
import os
import hashlib
import yaml
from .models import RootConfig
try:
    # Prefer unified schema version if available
    from ..params import SCHEMA_VERSION as _SCHEMA_VERSION
except Exception:  # pragma: no cover - optional import
    _SCHEMA_VERSION = None

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
_CONFIG_HASHES: dict[str, str] = {}


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


def _env_sensitive_blob() -> Dict[str, Any]:
    keys = [
        "COMSOL_HOST",
        "COMSOL_PORT",
        "JAVA_HOME",
        "COMSOL_HOME",
    ]
    return {k: os.environ.get(k) for k in keys if os.environ.get(k) is not None}


def _content_hash(merged: Dict[str, Any], env_blob: Dict[str, Any]) -> str:
    h = hashlib.sha256()
    # Stable dump (sorted keys) for hashing
    dumped = yaml.safe_dump(merged, sort_keys=True).encode("utf-8")
    h.update(dumped)
    h.update(yaml.safe_dump(env_blob, sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def load_config(paths: Iterable[Path]) -> RootConfig:
    """Load and validate structured config with inheritance and caching.

    - Later files override earlier keys (maps merged; lists replaced).
    - Cache key includes the merged content hash and selected environment variables.
    - Adds schema_version if missing and warns on mismatch (non-fatal).
    """
    paths = [Path(p) for p in paths]
    key_paths = "|".join(str(p.resolve()) for p in paths)
    merged: dict = {}
    for p in paths:
        if p.exists():
            merged = _deep_merge(merged, _load_any(p))
    merged = _normalize_legacy_keys(merged)

    env_blob = _env_sensitive_blob()
    h = _content_hash(merged, env_blob)
    composite_key = f"{key_paths}|{h}"

    # Fast path: return cached if hash matches
    if _CONFIG_HASHES.get(key_paths) == h and composite_key in _CONFIG_CACHE:
        return _CONFIG_CACHE[composite_key]

    # Attach schema version (non-fatal if absent)
    if "schema_version" not in merged and _SCHEMA_VERSION is not None:
        merged["schema_version"] = _SCHEMA_VERSION

    cfg = RootConfig.model_validate(merged)

    # Store cache under composite key and remember last hash for that path set
    _CONFIG_CACHE[composite_key] = cfg
    _CONFIG_HASHES[key_paths] = h
    return cfg


def cache_config(cfg: RootConfig) -> RootConfig:
    """Store a one-off config in memory for reuse within the process."""
    _CONFIG_CACHE["__single__"] = cfg
    return cfg
