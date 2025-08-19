import json, time, uuid, os, subprocess
from contextlib import contextmanager
from pathlib import Path


def _git_commit_or_none() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def init_logger(level: str = "INFO"):
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
    lvl = levels.get(level.upper(), 20)

    def log(event, **kv):
        # event is the level string (DEBUG/INFO/WARN/ERROR)
        cur = levels.get(str(event).upper(), 20)
        if cur < lvl:
            return
        print(json.dumps({"ts": time.time(), "level": str(event).upper(), **kv}))

    return log


def write_provenance(out_dir: Path, config_dict: dict, variant: str, extras: dict | None = None):
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "run_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": _git_commit_or_none(),
        "variant": variant,
        "config": config_dict,
    }
    if extras:
        meta.update(extras)
    (out_dir / "provenance.json").write_text(json.dumps(meta, indent=2))
    return meta


def log_step(log, name: str, pct: float | None = None, **meta):
    rec = {"event": "step", "name": name}
    if pct is not None:
        rec["pct"] = float(pct)
    rec.update(meta)
    log("INFO", **rec)


@contextmanager
def phase_timer(log, phase: str, **meta):
    t0 = time.time()
    log("INFO", event="phase_start", phase=phase, **meta)
    try:
        yield
    finally:
        dt = time.time() - t0
        log("INFO", event="phase_done", phase=phase, dt_s=dt, **meta)
