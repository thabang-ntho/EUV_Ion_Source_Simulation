Ongoing Work: MPh Integration and Test Migration

Status (mph_dev)
- Activation parity: study activation matches `mph_example.py` (Node refs + frames; safe fallback to strings).
- Frames present: model creation ensures a default `component` so `spatial1/material1` exist.
- Session: `mph.start` honors `COMSOL_HOST`/`COMSOL_PORT`/`COMSOL_CORES` env.
- CLI: `euv-mph` (or `python -m src.cli.mph_runner`) with `--check-only` and `--solve`.
- Make targets: `make mph-check` and `make mph-solve`.
- PR: https://github.com/thabang-ntho/EUV_Ion_Source_Simulation/pull/3

Testing (mph-only focus)
- COMSOL-off by default; COMSOL-only tests gated by `RUN_COMSOL=1`.
- Legacy (pp_model/low-level java) tests skipped via `tests/conftest.py`.
- Added mph-only tests:
  - `tests/test_cli_help.py` — CLI help OK
  - `tests/test_mph_geometry.py` — geometry builder builds
  - `tests/test_mph_study_activation.py` — activation payload constructed

Next Steps
1. Add SelectionManager + MaterialsHandler mph-only tests [in progress]
2. Add PhysicsManager + ModelBuilder orchestration tests
3. Run full pytest (no COMSOL) with legacy skipped; ensure green
4. Remove legacy code/tests; scrub docs/Makefile
5. Optional: COMSOL smoke (`make mph-check`/`mph-solve`) on local server

Useful Commands
- Build-only (no solve): `make mph-check`
- Solve (requires server): `make mph-solve`
- CLI help: `python -m src.cli.mph_runner --help`
- Single test: `pytest -q tests/test_mph_geometry.py`

