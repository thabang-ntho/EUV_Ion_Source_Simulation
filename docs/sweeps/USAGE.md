# Sweep Runner (Phase 3 stub)

This is a placeholder for future process-based parameter sweeps. For now, a
sequential stub is provided in `src/core/solvers/sweep.py`:

```python
from src.core.solvers.sweep import sweep

grid = {"a": [1, 2], "b": ["x"]}

def worker(cfg):
    # For COMSOL-heavy workloads, plan to use check-only builds here
    return f"{cfg['a']}{cfg['b']}"

results = sweep(grid, worker)
print(results)  # [("a":1,"b":"x"), "1x"), (…)]
```

Notes
- Default-off; no changes to existing CLI.
- COMSOL is not invoked here; plan is to orchestrate check-only tasks first.
- A future process-based runner can wrap this stub with concurrency guards.
- See `src/core/solvers/sweep_parallel.py` for the stub and planned API.

Manifest and schema (optional)

- A helper `src/io/sweep_manifest.py` can write an index JSON for sweep runs.
- A draft JSON Schema is provided in `docs/sweeps/manifest.schema.json`.
- Both are default-off and not used by the CLI yet.
