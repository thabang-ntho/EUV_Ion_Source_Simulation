# Developer Cheat Sheet (Local Workflows)

This cheat sheet lists common local commands for quick iteration. All are
additive and default-off. COMSOL commands require a local license.

## Build-only (no solve)

```bash
# Fresnel (writes results/fresnel/pp_model_created.mph)
uv run python src/pp_model.py --no-solve --absorption-model fresnel --out-dir results/fresnel --emit-milestones --summary-only

# Kumar (writes results/kumar/pp_model_created.mph)
uv run python src/pp_model.py --no-solve --absorption-model kumar --out-dir results/kumar --emit-milestones --summary-only
```

## Adapter smokes (developer-oriented)

```bash
# Minimal session + create() smoke
uv run python src/pp_model.py --use-adapter

# Trivial adapter builds
uv run python src/pp_model.py --adapter-build-fresnel --out-dir results/adapter
uv run python src/pp_model.py --adapter-build-kumar   --out-dir results/adapter
```

## Compare results

```bash
# Dedicated CLI (recommended)
uv run euv-compare --baseline results/baseline --candidate results/candidate --rtol 1e-5 --atol 1e-8 --json results/compare_report.json

# Make wrapper
make compare BASE=results/baseline CAND=results/candidate RTOL=1e-5 ATOL=1e-8
```

## Sweeps (stub)

```bash
# Demo sweep (writes results/sweep_demo.csv)
uv run python scripts/sweep_demo.py

# Lower-level stub (sequential)
python - <<'PY'
from src.core.solvers.sweep import sweep
print(sweep({"a":[1,2],"b":["x"]}, lambda c: f"{c['a']}{c['b']}"))
PY
```

## COMSOL tests (local-only)

```bash
# MPh session + minimal model
uv run python - <<'PY'
import mph; c = mph.start(); m = c.create('pp_smoke'); print('mph OK')
PY

# Run local COMSOL smokes
RUN_COMSOL=1 make test-comsol
```
