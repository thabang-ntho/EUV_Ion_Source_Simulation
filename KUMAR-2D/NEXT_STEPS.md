# Next Steps — Kumar 2D (MPh)

This folder is a self‑contained acid test for translating a COMSOL Java model to the MPh (Python) API and running it headlessly. Two runners are provided:

- `kumar_2d_mph.py`: direct container‑API translation (mph_example style)
- `run_kumar_mph.py`: architecture‑aligned runner leveraging `src/mph_core` (ModelBuilder)

## Current Status

- Parameters parsed from `parameters.txt` (units preserved as strings)
- Geometry: vacuum box (rectangle) + droplet (circle)
- Functions: `pulse(t)`, `gaussXY(x,y)`, `sigma(T)`
- Variables: includes `q_laser` volumetric heat source expression
- Physics: Heat Transfer (HT) + Single Phase Flow (SPF) baseline
- Mesh: simple size control
- Study: transient, with activation and frames per `mph_example.py`
- Outputs: `.mph` saved to `results/`; on `--solve`, exports `temperature_field.png`

## Environment

- Local COMSOL:
  - `source scripts/setup_comsol_env.sh`
- Remote COMSOL:
  - `export COMSOL_HOST=... COMSOL_PORT=...` (or pass `--host/--port`)

## How to Run

- Dry run (no COMSOL):
  - `python KUMAR-2D/kumar_2d_mph.py --dry-run`
  - `python KUMAR-2D/run_kumar_mph.py --dry-run`
- Build & save `.mph` (no solve):
  - `python KUMAR-2D/kumar_2d_mph.py --check-only`
  - `python KUMAR-2D/run_kumar_mph.py --check-only`
- Solve & export plot:
  - `python KUMAR-2D/kumar_2d_mph.py --solve --host 127.0.0.1 --port 2036`
  - `python KUMAR-2D/run_kumar_mph.py --solve --host 127.0.0.1 --port 2036`

## To‑Do (Parity with Java Model)

1) Boundary Conditions & Couplings
- Add surface tension and Marangoni stress on droplet surface (temperature‑dependent `sigma(T)` and `d_sigma_dT`):
  - MPh nodes under `spf` boundary features (container API) to set surface stress conditions.
- Add recoil pressure and evaporation flux BCs on the interface:
  - Use `Psat(T)` relation; couple with HT boundary heat sink/source as needed.
- If the Java model uses a second HT or specific subfeatures (e.g., different domains), mirror them in MPh.

2) Studies & Solvers
- Confirm time stepping to match `t_step` and pulse duration in `parameters.txt`.
- If the Java report includes param sweeps, add a parametric study step.

3) Results & Report
- Export additional plots: velocity magnitude, pressure, and temperature evolution.
- Create a minimal Markdown/HTML report in `results/` with links to plots and key parameters.

4) Validation
- Open `results/kumar2d_model.mph` in COMSOL GUI; confirm nodes exist:
  - Geometry, functions, variables, HT + SPF, mesh, study/solution.
- Compare field snapshots to those from the Java model.

5) Architecture Alignment
- Keep `run_kumar_mph.py` in sync with `src/mph_core` improvements (selections, physics, studies).
- If adding Kumar‑specific physics, consider a dedicated module (e.g., `physics_kumar`) and call it from the runner.

## Tips

- If activation errors appear, run with `--log-level DEBUG` and confirm frames (`spatial1/material1`) exist.
- When adding boundary features, use the MPh container access pattern (`physics/'spf'` and `.create()` for features).
- Keep unit strings (e.g., `15[um]`) in parameters so COMSOL handles them correctly.

