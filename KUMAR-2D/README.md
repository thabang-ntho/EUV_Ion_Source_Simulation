# Kumar 2D — MPh Translation and Runner

This folder contains a self‑contained, MPh (Python) translation of the COMSOL Java model `Kumar_2D_demo_v5.java`. It mirrors the architecture used in `src/mph_core` and follows `mph_example.py` patterns.

Contents
- `parameters.txt`: model parameters (with units) consumed by the runners.
- `kumar_2d_mph.py`: direct MPh (container API) translation that builds and (optionally) solves, saving `.mph` and a temperature plot.
- `run_kumar_mph.py`: architecture‑aligned runner using `src/mph_core.model_builder.ModelBuilder` with `variant='kumar'`.
- `data/`, `results/`: local inputs/outputs (kept self‑contained here).

Prerequisites
- COMSOL Multiphysics 6.2+ reachable locally or via server.
- Python 3.10+ with `mph` installed (installed via project `pyproject.toml`).

Environment setup (local COMSOL)
```bash
source scripts/setup_comsol_env.sh
```

Run (no COMSOL)
```bash
python KUMAR-2D/kumar_2d_mph.py --dry-run
python KUMAR-2D/run_kumar_mph.py --dry-run
```

Build and save `.mph`
```bash
# Direct translation
python KUMAR-2D/kumar_2d_mph.py --check-only

# Architecture‑aligned
python KUMAR-2D/run_kumar_mph.py --check-only
```

Solve and export results (requires COMSOL server)
```bash
# Replace host/port as needed (or configure COMSOL_HOST/COMSOL_PORT in env)
python KUMAR-2D/kumar_2d_mph.py --solve --host 127.0.0.1 --port 2036
# or
python KUMAR-2D/run_kumar_mph.py --solve --host 127.0.0.1 --port 2036
```

Outputs
- `results/kumar2d_model.mph` (build‑only)
- `results/kumar2d_model_solved.mph` (after solve)
- `results/temperature_field.png` (simple temperature plot)

Notes
- The MPh translation follows the COMSOL Java model’s structure: parameters → geometry → functions → variables → physics → mesh → study.
- Physics currently sets up Heat Transfer (HT) and Single Phase Flow (SPF) and a volumetric laser heat source. Further BCs (e.g., explicit Marangoni surface stress, recoil pressure, multi‑physics couplings) can be added as needed using MPh node features, using `mph_example.py` as a pattern reference.

Tips
- If activation errors appear, run with `--log-level DEBUG` and verify frames exist and physics interfaces are referenced as nodes.
- You can open the generated `.mph` files in the COMSOL GUI to inspect/extend features.

