import json, time, uuid, os, subprocess, sys, platform
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List


def _git_commit_or_none() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _git_dirty() -> bool:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return any(line.strip() for line in out.splitlines())
    except Exception:
        return False


def _comsol_version() -> str | None:
    try:
        out = subprocess.check_output(["comsol", "--version"], text=True, stderr=subprocess.STDOUT)
        line = out.splitlines()[0].strip()
        return line or None
    except Exception:
        return None


def init_logger(level: str = "INFO"):
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
    lvl = levels.get(level.upper(), 20)

    def log(level_name, **kv):
        # level_name is the level string (DEBUG/INFO/WARN/ERROR)
        cur = levels.get(str(level_name).upper(), 20)
        if cur < lvl:
            return
        print(json.dumps({"ts": time.time(), "level": str(level_name).upper(), **kv}))

    return log


def write_provenance(out_dir: Path, config_dict: dict, variant: str, extras: dict | None = None):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Best-effort software versions
    pyver = sys.version.split()[0]
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
    }
    mph_ver = None
    np_ver = None
    comsol_ver = None
    try:  # optional
        import mph  # type: ignore

        mph_ver = getattr(mph, "__version__", None)
    except Exception:
        mph_ver = None
    try:
        import numpy as _np  # type: ignore
        np_ver = getattr(_np, "__version__", None)
    except Exception:
        np_ver = None
    # Try CLI for COMSOL version (no session required)
    comsol_ver = _comsol_version()

    # Optional schema version (if unified params present)
    schema_version = None
    try:
        from .params import SCHEMA_VERSION as _SCHEMA_VERSION  # type: ignore

        schema_version = _SCHEMA_VERSION
    except Exception:
        schema_version = None

    meta: Dict[str, Any] = {
        "run_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "variant": variant,
        "config": config_dict,
        "software": {
            "python": pyver,
            "os": os_info,
            "mph": mph_ver,
            "numpy": np_ver,
            "comsol": comsol_ver,
        },
        "git": {"commit": _git_commit_or_none(), "dirty": _git_dirty()},
        "schema_version": schema_version,
    }
    if extras:
        meta.update(extras)

    # Optional input manifest (list of file paths or mapping name->path)
    inputs: List[str] | Dict[str, str] | None = None
    if extras and "inputs" in extras:
        inp = extras.get("inputs")
        if isinstance(inp, dict):
            inputs = {k: str(Path(v)) for k, v in inp.items()}
        elif isinstance(inp, list):
            inputs = [str(Path(p)) for p in inp]
    if inputs is not None:
        meta["inputs"] = _manifest(inputs)
    # Optional seeds
    seeds = {}
    for k in ("PYTHONHASHSEED", "SEED", "RANDOM_SEED"):
        if os.environ.get(k) is not None:
            seeds[k] = os.environ.get(k)
    if seeds:
        meta["seeds"] = seeds
    (out_dir / "provenance.json").write_text(json.dumps(meta, indent=2))
    return meta


def log_step(log, name: str, pct: float | None = None, **meta):
    rec = {"event": "step", "name": name}
    if pct is not None:
        rec["pct"] = float(pct)
    rec.update(meta)
    log("INFO", **rec)


def milestone(log, name: str, **meta):
    log("INFO", event="milestone", name=name, **meta)


@contextmanager
def phase_timer(log, phase: str, **meta):
    t0 = time.time()
    log("INFO", event="phase_start", phase=phase, **meta)
    try:
        yield
    finally:
        dt = time.time() - t0
        rss = _rss_mb()
        log("INFO", event="phase_done", phase=phase, dt_s=dt, rss_mb=rss, **meta)


def _rss_mb() -> float | None:
    # Best-effort RSS in MB without extra deps
    try:
        import resource  # Unix only

        usage = resource.getrusage(resource.RUSAGE_SELF)
        rss_kb = getattr(usage, "ru_maxrss", 0)
        # ru_maxrss is kilobytes on Linux, bytes on macOS; assume KB if large
        if rss_kb > 0:
            return float(rss_kb) / 1024.0
    except Exception:
        return None
    return None


def _sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest(inputs: List[str] | Dict[str, str]):
    def _pair(name: str, p: Path):
        return {"name": name, "path": str(p), "sha256": _sha256_file(p) if p.is_file() else None}

    if isinstance(inputs, dict):
        return [_pair(k, Path(v)) for k, v in inputs.items()]
    return [_pair(Path(p).name, Path(p)) for p in inputs]
