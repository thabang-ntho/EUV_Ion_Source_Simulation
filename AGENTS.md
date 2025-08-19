ROLE & NON-BREAKING SCOPE

You are a University Professor, who specialises in computational physics + software engineering. Your job now is to take the repository one professional-grade step forward with non-breaking, additive improvements to architecture, configuration, logging/observability, error handling, and developer experience—without moving or renaming existing files. Keep physics and current CLI behavior intact by default.Start by reading README.md before executing the commands below. Think deeply for this task.

Hard constraints

Do not relocate or rename existing files in src/ (keep src/pp_model.py and src/pp_sizyuk.py where they are).

Keep the existing Fresnel vs Kumar split and the pp_sizyuk.py integration you already implemented.

All improvements must be additive (opt-in flags, new modules, stubs, or wrappers). No breaking changes.

STARTUP CHECKLIST (MANDATORY)

Re-read README.md and confirm current commands still work after your changes.

Re-verify src/pp_sizyuk.py produces to data/derived/sizyuk/ (tables/JSON) and results/sizyuk/plots/ (figures).

Confirm pp_model.py consumes precomputed tables (or autogenerates via run_sizyuk) and does not read Excel itself.

OBJECTIVE

Implement Phase 1 (High impact, low risk) enhancements now; scaffold Phase 2/3 interfaces (no behavior change) for future work.

PHASE 1 (DO NOW): Non-breaking architecture upgrades
A) Configuration management (validation, inheritance, caching)

Additive packages: use Pydantic (v2) for config models.

Create src/core/config/ (additive) with:

models.py — Pydantic models mirroring our YAML/TOML schema:

Top-level sections: simulation, geometry, materials, environment, laser, absorption, evaporation, radiation, mesh, outputs.

loader.py — functions:

load_config(paths: list[Path]) -> Config: supports inheritance (base → overrides). Merge strategy: later files override earlier keys; lists replace by default.

cache_config(config: Config) -> Config: in-memory caching to avoid re-parsing within a process.

factory.py — optional helpers:

make_sim_config(kind: Literal["fresnel","kumar"]) -> Config for variant-specific defaults (non-breaking; only used if called).

Wire-up (additive, no break): in pp_model.py, if a structured config is detected, validate with Pydantic and keep legacy path as fallback. Emit deprecation warnings only, not errors.

B) Logging & observability (structured, provenance, progress)

Add src/core/logging_utils.py:

Initialize structured logging (JSON lines by default) with component and run IDs.

Logging levels: DEBUG/INFO/WARN/ERROR; CLI flag --log-level (default INFO).

Provenance helper: write_provenance(out_dir, config, extras) writes a metadata JSON including:

timestamp, user/env (if available), git commit (if repo), variant, CLI args, schema version.

Progress: simple step logger (e.g., log_step("mesh_refine", pct=0.3)), and wall-clock timers per major phase.

Update README.md with --log-level and link to provenance artifact.

C) Error handling & resilience

Add src/core/errors.py with a custom exception hierarchy:

SimError (base), ConfigError, PhysicsError, LicenseError, ComsolConnectError, DataError.

Wrap COMSOL connect/build with:

Clear messages + suggested fixes.

Graceful degradation: if COMSOL license/session unavailable, --check-only still works and prints actionable next steps.

Add a retry wrapper (small, bounded) for transient mph session opens; log attempts.

D) Code organization (additive skeleton only)

Create the following additive folders (keep all existing code untouched; place new utilities here and call them from existing entry points):

src/
  core/
    config/         # Pydantic models, loader, factory (new)
    logging_utils.py# structured logging & provenance (new)
    errors.py       # custom exceptions (new)
  io/               # (optional) small helpers for reading derived CSV/JSON
  validation/       # (optional) extra parameter validators beyond Pydantic
  visualization/    # (optional) shared plotting utils (Sizyuk plots can import)


Do not move existing modules; only import these helpers where beneficial.

E) Developer experience & requirements (uv-first kept)

Ensure pyproject.toml (existing) includes pydantic>=2, structlog or standard logging JSON formatter (your call; prefer stdlib + json for zero deps), and keep openpyxl, pandas, matplotlib for pp_sizyuk.py.

Add Make targets (additive; don’t remove existing):

make lint (ruff/flake8 if present; otherwise skip with note).

make provenance (runs a no-solve command that writes provenance).

Update README.md:

Configuration: explain base+override loading order and validation.

Logging: --log-level, provenance JSON location and fields.

F) Tests (light but useful)

tests/test_config_models.py: valid config passes; invalid types/units raise ConfigError with clear path (dot-notation key).

tests/test_logging_provenance.py: calling write_provenance writes file with required keys.

tests/test_errors.py: ensure LicenseError and ComsolConnectError messages include suggested fixes.

PHASE 2 (SCaffold only, NO behavior change)
Interfaces & plugins

Add src/models/base.py with minimal Abstract Base Classes:

class AbsorptionModel(ABC): build(self, params) -> Any

class PhysicsVariant(ABC): configure(self, model, params) -> None

Implement thin adapters for the existing Fresnel/Kumar paths that simply subclass (no logic changes). This is purely for future consistency.

Testing & quality hooks

Add pyproject.toml opt-in config for pytest-cov (if present) and a basic coverage.xml generation target in make test-cov (documented, optional).

PHASE 3 (Leave as TODOs only, with stubs)

Plugin discovery hooks (entry points): add commented stubs in src/models/base.py.

Async/parallel sweep support: add TODOs and a small sweeps/README.md noting intended API (no code path changes).

Advanced data management (parquet/HDF5): add a note in docs/ proposing a format; do not change current outputs.

REQUIRED CODE BLOCKS (RETURN IN YOUR RESPONSE)

Provide concise, ready-to-paste snippets (no placeholders) for:

Pydantic config models (src/core/config/models.py)

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Literal, Optional

class Simulation(BaseModel):
    t_end: float = Field(..., gt=0, description="End time [s]")
    dt_init: Optional[float] = Field(None, gt=0, description="Initial step [s]")
    solver: Literal["direct","iterative"] = "direct"

class Laser(BaseModel):
    wavelength_um: float = Field(..., gt=0)
    theta_deg: float = Field(0, ge=0, lt=360)

class Absorption(BaseModel):
    model: Literal["fresnel","kumar"] = "fresnel"
    use_precomputed: bool = True
    autogenerate_if_missing: bool = True
    nk_file: Optional[str] = None

class Environment(BaseModel):
    gas: Literal["none","H2"] = "none"
    pressure_torr: float = Field(1.33, gt=0)

class RootConfig(BaseModel):
    simulation: Simulation
    laser: Laser
    absorption: Absorption
    environment: Environment
    # add sections as needed: geometry, materials, evaporation, radiation, mesh, outputs


Config loader with inheritance & caching (src/core/config/loader.py)

from __future__ import annotations
from pathlib import Path
from typing import Iterable
import yaml
from .models import RootConfig

_CONFIG_CACHE: dict[str, RootConfig] = {}

def _load_any(path: Path) -> dict:
    with path.open("r") as f:
        return yaml.safe_load(f) or {}

def _deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_config(paths: Iterable[Path]) -> RootConfig:
    key = "|".join(str(p.resolve()) for p in paths)
    if key in _CONFIG_CACHE:
        return _CONFIG_CACHE[key]
    merged: dict = {}
    for p in paths:
        merged = _deep_merge(merged, _load_any(Path(p)))
    cfg = RootConfig.model_validate(merged)
    _CONFIG_CACHE[key] = cfg
    return cfg

def cache_config(cfg: RootConfig) -> RootConfig:
    _CONFIG_CACHE["__single__"] = cfg
    return cfg


Structured logging & provenance (src/core/logging_utils.py)

import json, time, uuid, os, subprocess
from pathlib import Path

def _git_commit_or_none() -> str | None:
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    except Exception:
        return None

def init_logger(level: str = "INFO"):
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    levels = {"DEBUG":10,"INFO":20,"WARN":30,"ERROR":40}
    lvl = levels.get(level.upper(), 20)
    def log(event, **kv):
        if levels["DEBUG"] < lvl and event == "DEBUG":
            return
        print(json.dumps({"ts": time.time(), "level": event, **kv}))
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


Error hierarchy (src/core/errors.py)

class SimError(Exception): ...
class ConfigError(SimError): ...
class PhysicsError(SimError): ...
class LicenseError(SimError): ...
class ComsolConnectError(SimError): ...
class DataError(SimError): ...


Minimal wiring in pp_model.py (additive; keep existing code)

# near top of pp_model.py
from pathlib import Path
from src.core.logging_utils import init_logger, write_provenance
from src.core.config.loader import load_config
from src.core.errors import ConfigError, LicenseError, ComsolConnectError

# inside main():
log = init_logger(level=os.environ.get("LOG_LEVEL","INFO"))
repo_root = Path(".").resolve()

# load (base, overrides) if available; fallback to legacy path if not
cfg_paths = [repo_root/"data"/"config.yaml"]
if any(p.exists() for p in cfg_paths):
    try:
        cfg = load_config([p for p in cfg_paths if p.exists()])
        # use cfg to populate existing params dict (non-breaking)
    except Exception as e:
        raise ConfigError(f"Configuration invalid: {e}") from e

# write provenance (non-breaking)
prov_dir = repo_root / "results" / "meta"
write_provenance(prov_dir, config_dict={}, variant="fresnel_or_kumar")  # fill with real dict


Tests (names & asserts only; you can fill fixtures)

# tests/test_config_models.py
from pathlib import Path
from src.core.config.loader import load_config
def test_valid_config(tmp_path: Path):
    p = tmp_path/"cfg.yaml"; p.write_text("simulation: {t_end: 1.0}\nlaser: {wavelength_um: 1.06}\nabsorption: {model: fresnel}\nenvironment: {gas: none, pressure_torr: 1.33}\n")
    cfg = load_config([p])
    assert cfg.simulation.t_end == 1.0

# tests/test_logging_provenance.py
from src.core.logging_utils import write_provenance
def test_provenance(tmp_path):
    meta = write_provenance(tmp_path, {"k":"v"}, "fresnel")
    assert (tmp_path/"provenance.json").exists()
    assert meta["variant"] == "fresnel"

README / DOC UPDATES (RETURN TEXT OR DIFF)

New section: “Configuration & Validation”

Explain base+override loading with Pydantic validation.

Example:

# base
data/config.yaml
# override (optional)
data/config.local.yaml


Failure messages will show the offending key path; legacy configs still work (with warnings).

Logging & Provenance

LOG_LEVEL=DEBUG python src/pp_model.py --check-only

Provenance written to results/meta/provenance.json.

ACCEPTANCE CRITERIA

Existing commands continue to work unchanged (Fresnel/Kumar, --check-only, Sizyuk precompute).

Config layer: Pydantic models accept current schema (or a minimal subset) and reject invalid types with clear messages. Inheritance works (base → override).

Structured logging prints JSON lines; provenance JSON created for runs.

Custom exceptions raised with actionable messages; COMSOL connection failures do not crash --check-only.

No file moves/renames; all changes are additive under src/core/ (+ optional small helpers in src/io, src/validation, src/visualization).

Tests added and passing (at least the two above).

PHASED PLAN (FOR TRACKING)

Phase 1 (now): config validation + inheritance + caching; structured logging + provenance; error hierarchy + graceful COMSOL handling; docs; tests.

Phase 2 (scaffold): base ABCs for models; optional coverage target; no behavior change.

Phase 3 (TODOs only): plugin hooks, async sweeps, data formats.

CHANGE CONTROL

Any behavior that might affect physics or outputs must be flag-guarded and default-off. Do not alter existing default physics or CLI semantics. Document every new flag in README.md.

Deliver your response with: code blocks above (filled), README/doc text additions, and a brief note confirming existing runs still pass locally (Fresnel & Kumar).

You said:
Give me the whole prompt (including code snippets—leave nothing out)—as one copiable text/file.
ChatGPT said:
Thought for 33s

Here’s the single, consolidated prompt (with all code snippets included). You can copy–paste this as one file/text for Codex to execute.

ROLE & NON-BREAKING SCOPE

You are Codex, a senior computational physicist + software engineer. Your job now is to take the repository one professional-grade step forward with non-breaking, additive improvements to architecture, configuration, logging/observability, error handling, and developer experience—without moving or renaming existing files. Keep physics and current CLI behavior intact by default.

Hard constraints

Do not relocate or rename existing files in src/ (keep src/pp_model.py and src/pp_sizyuk.py where they are).

Keep the existing Fresnel vs Kumar split and the pp_sizyuk.py integration you already implemented.

All improvements must be additive (opt-in flags, new modules, stubs, or wrappers). No breaking changes.

STARTUP CHECKLIST (MANDATORY)

Re-read README.md and confirm current commands still work after your changes.

Re-verify src/pp_sizyuk.py produces to data/derived/sizyuk/ (tables/JSON) and results/sizyuk/plots/ (figures).

Confirm pp_model.py consumes precomputed tables (or autogenerates via run_sizyuk) and does not read Excel itself.

OBJECTIVE

Implement Phase 1 (High impact, low risk) enhancements now; scaffold Phase 2/3 interfaces (no behavior change) for future work.

PHASE 1 (DO NOW): Non-breaking architecture upgrades
A) Configuration management (validation, inheritance, caching)

Use Pydantic v2 for config models.

Create src/core/config/ (additive) with:

models.py — Pydantic models mirroring our YAML/TOML schema:

Top-level sections: simulation, geometry, materials, environment, laser, absorption, evaporation, radiation, mesh, outputs.

loader.py — functions:

load_config(paths: list[Path]) -> Config: supports inheritance (base → overrides). Merge strategy: later files override earlier keys; lists replace by default.

cache_config(config: Config) -> Config: in-memory caching to avoid re-parsing within a process.

factory.py — optional helpers:

make_sim_config(kind: Literal["fresnel","kumar"]) -> Config for variant-specific defaults (non-breaking; only used if called).

Wire-up (additive, no break): in pp_model.py, if a structured config is detected, validate with Pydantic and keep legacy path as fallback. Emit deprecation warnings only, not errors.

B) Logging & observability (structured, provenance, progress)

Add src/core/logging_utils.py:

Initialize structured logging (JSON lines by default) with component and run IDs.

Logging levels: DEBUG/INFO/WARN/ERROR; CLI flag --log-level (default INFO).

Provenance helper: write_provenance(out_dir, config, extras) writes a metadata JSON including:

timestamp, user/env (if available), git commit (if repo), variant, CLI args, schema version.

Progress: simple step logger (e.g., log("INFO", event="mesh_refine", pct=0.3)), and wall-clock timers per major phase.

Update README.md with --log-level and link to provenance artifact.

C) Error handling & resilience

Add src/core/errors.py with a custom exception hierarchy:

SimError (base), ConfigError, PhysicsError, LicenseError, ComsolConnectError, DataError.

Wrap COMSOL connect/build with:

Clear messages + suggested fixes.

Graceful degradation: if COMSOL license/session unavailable, --check-only still works and prints actionable next steps.

Add a retry wrapper (small, bounded) for transient mph session opens; log attempts.

D) Code organization (additive skeleton only)

Create the following additive folders (keep all existing code untouched; place new utilities here and call them from existing entry points):

src/
  core/
    config/           # Pydantic models, loader, factory (new)
    logging_utils.py  # structured logging & provenance (new)
    errors.py         # custom exceptions (new)
  io/                 # (optional) small helpers for reading derived CSV/JSON
  validation/         # (optional) extra parameter validators beyond Pydantic
  visualization/      # (optional) shared plotting utils (Sizyuk plots can import)


Do not move existing modules; only import these helpers where beneficial.

E) Developer experience & requirements (uv-first kept)

Ensure pyproject.toml includes pydantic>=2, and either stdlib logging JSON output or a tiny helper (we’ll use stdlib + json for zero extra deps). Keep openpyxl, pandas, matplotlib for pp_sizyuk.py.

Add Make targets (additive; don’t remove existing):

make lint (ruff/flake8 if present; otherwise skip with note).

make provenance (runs a no-solve command that writes provenance).

Update README.md:

Configuration: explain base+override loading order and validation.

Logging: --log-level, provenance JSON location and fields.

F) Tests (light but useful)

tests/test_config_models.py: valid config passes; invalid types/units raise ConfigError with clear path (dot-notation key).

tests/test_logging_provenance.py: calling write_provenance writes file with required keys.

tests/test_errors.py: ensure LicenseError and ComsolConnectError messages include suggested fixes.

PHASE 2 (SCAFFOLD ONLY, NO behavior change)
Interfaces & plugins

Add src/models/base.py with minimal Abstract Base Classes:

class AbsorptionModel(ABC): build(self, params) -> Any

class PhysicsVariant(ABC): configure(self, model, params) -> None

Implement thin adapters for the existing Fresnel/Kumar paths that simply subclass (no logic changes). This is purely for future consistency.

Testing & quality hooks

Add pyproject.toml opt-in config for pytest-cov (if present) and a basic coverage.xml generation target in make test-cov (documented, optional).

PHASE 3 (LEAVE AS TODOs ONLY, with stubs)

Plugin discovery hooks (entry points): add commented stubs in src/models/base.py.

Async/parallel sweep support: add TODOs and a small sweeps/README.md noting intended API (no code path changes).

Advanced data management (parquet/HDF5): add a note in docs/ proposing a format; do not change current outputs.

REQUIRED CODE BLOCKS (PASTE EXACTLY)
1) src/core/config/models.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

class Simulation(BaseModel):
    t_end: float = Field(..., gt=0, description="End time [s]")
    dt_init: Optional[float] = Field(None, gt=0, description="Initial time step [s]")
    solver: Literal["direct","iterative"] = "direct"

class Laser(BaseModel):
    wavelength_um: float = Field(..., gt=0)
    theta_deg: float = Field(0, ge=0, lt=360, description="Incidence angle [deg]")

class Absorption(BaseModel):
    model: Literal["fresnel","kumar"] = "fresnel"
    use_precomputed: bool = True
    autogenerate_if_missing: bool = True
    nk_file: Optional[str] = None
    lambda_um: Optional[float] = Field(None, gt=0, description="Sampling wavelength for A")

class Environment(BaseModel):
    gas: Literal["none","H2"] = "none"
    pressure_torr: float = Field(1.33, gt=0)

# Extend as needed for geometry/materials/evaporation/radiation/mesh/outputs
class RootConfig(BaseModel):
    simulation: Simulation
    laser: Laser
    absorption: Absorption
    environment: Environment

2) src/core/config/loader.py
from __future__ import annotations
from pathlib import Path
from typing import Iterable
import yaml
from .models import RootConfig

_CONFIG_CACHE: dict[str, RootConfig] = {}

def _load_any(path: Path) -> dict:
    with path.open("r") as f:
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
    cfg = RootConfig.model_validate(merged)
    _CONFIG_CACHE[key] = cfg
    return cfg

def cache_config(cfg: RootConfig) -> RootConfig:
    _CONFIG_CACHE["__single__"] = cfg
    return cfg

3) src/core/logging_utils.py
import json, time, uuid, os, subprocess
from pathlib import Path

def _git_commit_or_none() -> str | None:
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    except Exception:
        return None

def init_logger(level: str = "INFO"):
    levels = {"DEBUG":10,"INFO":20,"WARN":30,"ERROR":40}
    lvl = levels.get(level.upper(), 20)
    def log(lvl_name: str, **kv):
        if levels.get(lvl_name.upper(), 20) < lvl:
            return
        record = {"ts": time.time(), "level": lvl_name.upper()}
        record.update(kv)
        print(json.dumps(record))
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

4) src/core/errors.py
class SimError(Exception): ...
class ConfigError(SimError): ...
class PhysicsError(SimError): ...
class LicenseError(SimError): ...
class ComsolConnectError(SimError): ...
class DataError(SimError): ...

5) Minimal additive wiring in src/pp_model.py
# --- Add these near the top of src/pp_model.py (keep all existing imports/logic) ---
import os
from pathlib import Path
from src.core.logging_utils import init_logger, write_provenance
from src.core.config.loader import load_config
from src.core.errors import ConfigError, LicenseError, ComsolConnectError

# --- Inside your existing main() entrypoint, add the following (non-breaking) ---
def _add_professional_scaffolding(params_or_cfg_dict: dict, variant_name: str = "fresnel_or_kumar"):
    """
    Non-breaking scaffolding: structured logging, config validation (if present),
    and provenance output. Safe to call early in main().
    """
    log = init_logger(level=os.environ.get("LOG_LEVEL","INFO"))
    repo_root = Path(".").resolve()

    # Attempt structured config load (base + local override); fallback to legacy params
    cfg_paths = [repo_root/"data"/"config.yaml", repo_root/"data"/"config.local.yaml"]
    try:
        if any(p.exists() for p in cfg_paths):
            cfg = load_config([p for p in cfg_paths if p.exists()])
            log("INFO", event="config_loaded", paths=[str(p) for p in cfg_paths if p.exists()])
        else:
            log("WARN", event="structured_config_missing", note="continuing with legacy params dict")
    except Exception as e:
        raise ConfigError(f"Configuration invalid: {e}") from e

    # Write provenance (non-breaking)
    prov_dir = repo_root / "results" / "meta"
    try:
        write_provenance(prov_dir, config_dict=params_or_cfg_dict or {}, variant=variant_name, extras={"cwd": str(repo_root)})
        log("INFO", event="provenance_written", path=str(prov_dir/"provenance.json"))
    except Exception as e:
        log("WARN", event="provenance_failed", error=str(e))

6) Tests
tests/test_config_models.py
from pathlib import Path
from src.core.config.loader import load_config

def test_valid_config(tmp_path: Path):
    p = tmp_path / "cfg.yaml"
    p.write_text(
        "simulation: {t_end: 1.0}\n"
        "laser: {wavelength_um: 1.06}\n"
        "absorption: {model: fresnel}\n"
        "environment: {gas: none, pressure_torr: 1.33}\n"
    )
    cfg = load_config([p])
    assert cfg.simulation.t_end == 1.0
    assert cfg.laser.wavelength_um == 1.06
    assert cfg.absorption.model == "fresnel"
    assert cfg.environment.gas == "none"

tests/test_logging_provenance.py
from pathlib import Path
from src.core.logging_utils import write_provenance

def test_provenance(tmp_path: Path):
    meta = write_provenance(tmp_path, {"k":"v"}, "fresnel")
    f = tmp_path / "provenance.json"
    assert f.exists()
    assert meta["variant"] == "fresnel"

tests/test_errors.py
import pytest
from src.core.errors import LicenseError, ComsolConnectError

def test_error_messages():
    with pytest.raises(LicenseError):
        raise LicenseError("COMSOL license not found. Tip: check LM_LICENSE_FILE.")
    with pytest.raises(ComsolConnectError):
        raise ComsolConnectError("COMSOL session connect failed. Tip: verify mph server is running.")

README / DOC UPDATES (PASTE TEXT)
Configuration & Validation

This repo now supports structured configuration with validation and inheritance.

Files (in order):

Base: data/config.yaml

Optional override: data/config.local.yaml (values here override base keys)

Validation is performed with Pydantic models. Invalid values raise clear errors identifying the offending key path. Legacy configuration paths remain supported; if data/config*.yaml is absent, the code will warn and proceed with legacy parameters.

Example minimal config

simulation:
  t_end: 1.0
laser:
  wavelength_um: 1.06
absorption:
  model: fresnel
environment:
  gas: none
  pressure_torr: 1.33

Logging & Provenance

Structured logging prints JSON lines to stdout. Set verbosity via:

LOG_LEVEL=DEBUG python src/pp_model.py --check-only


Each run writes a provenance file:

results/meta/provenance.json


It includes run ID, timestamp, git commit hash (if available), variant, and the config snapshot.

COMMANDS (FOR USERS)

Precompute (recommended):

python src/pp_sizyuk.py --nk-file data/nk_optics.xlsx --out-root .


Run solver (Fresnel path, consuming precomputed data):

python src/pp_model.py --absorption-model fresnel


Validate config only (no COMSOL):

python src/pp_model.py --check-only --absorption-model fresnel
python src/pp_model.py --check-only --absorption-model kumar


Logging:

LOG_LEVEL=DEBUG python src/pp_model.py --check-only

ACCEPTANCE CRITERIA

Existing commands continue to work unchanged (Fresnel/Kumar, --check-only, Sizyuk precompute).

Config layer: Pydantic models accept current schema (or a minimal subset) and reject invalid types with clear messages. Inheritance works (base → override).

Structured logging prints JSON lines; provenance JSON created for runs.

Custom exceptions raised with actionable messages; COMSOL connection failures do not crash --check-only.

No file moves/renames; all changes are additive under src/core/ (+ optional small helpers in src/io, src/validation, src/visualization).

Tests added and passing (at least the three above).

PHASED PLAN (FOR TRACKING)

Phase 1 (now): config validation + inheritance + caching; structured logging + provenance; error hierarchy + graceful COMSOL handling; docs; tests.

Phase 2 (scaffold): base ABCs for models; optional coverage target; no behavior change.

Phase 3 (TODOs only): plugin hooks, async sweeps, data formats.

CHANGE CONTROL

Any behavior that might affect physics or outputs must be flag-guarded and default-off. Do not alter existing default physics or CLI semantics. Document every new flag in README.md.