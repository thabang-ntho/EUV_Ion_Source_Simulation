# Models, Adapters, and Plugins (Phase 2 scaffolds)

This document outlines the additive scaffolds introduced to standardize how
variants, adapters, and plugins will integrate — without changing any default
behavior. Everything here is opt-in and safe to ignore for current workflows.

## ABCs (interfaces)

Defined in `src/models/base.py`:
- `AbsorptionModel.build(params) -> Any`
- `PhysicsVariant.configure(model, params) -> None`
- `Solver.build(cfg) -> Any` and `Solver.run(model, mode)`
- `SessionIface`: context manager for session handling (adapters can implement)

These provide a consistent surface for future extensions and testing.

## Adapters layer (mockable)

`src/core/adapters/mph_adapter.py` provides a thin wrapper around the MPh/COMSOL
client:
- `MphSessionAdapter.open()` yields an MPh client using the existing `Session`
  context manager with retries/diagnostics.
- `ModelAdapter.create_model(name)` calls the client’s `create` method.

Use the CLI smoke to exercise it without changing defaults:

```bash
uv run python src/pp_model.py --use-adapter
uv run python src/pp_model.py --adapter-build --out-dir ./results
```

## Plugin registry (explicit, opt-in)

`src/models/registry.py` exposes simple functions:
- `register(name, obj)`
- `get(name) -> obj | None`
- `list_plugins() -> dict`

Example:

```python
from src.models import registry

class MyAbsorber:
    def build(self, params):
        return None

registry.register("my_absorber", MyAbsorber())
assert registry.get("my_absorber") is not None
```

## Mocking adapters in tests

You can mock the `mph` module to test adapter code without COMSOL:

```python
import sys, types
from src.core.adapters.mph_adapter import MphSessionAdapter, ModelAdapter

class DummyClient:
    def create(self, name):
        return {"name": name}
    def close(self):
        pass

def start():
    return DummyClient()

sys.modules["mph"] = types.SimpleNamespace(start=start)

adapter = MphSessionAdapter(retries=1, delay=0.0)
with adapter.open() as client:
    model = ModelAdapter(client).create_model("adapter_smoke")
    assert model["name"] == "adapter_smoke"
```

## Notes

- No default code paths use adapters or the plugin registry yet.
- The goal is to make future integration tests cleaner, enable optional

Quick environment one-liner (KUMAR-2D)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```
  extension points, and keep vendor specifics isolated.
- Async/parallel sweeps are deferred to Phase 3 and will remain opt-in.
