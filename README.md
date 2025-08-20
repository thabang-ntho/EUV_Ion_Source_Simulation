# EUV Tin Droplet — Laser Pre-Pulse Simulation (MPh + COMSOL)

This project models the interaction of a high-energy laser pulse with a **2D planar** liquid tin droplet (sphere → pancake transition) for EUV lithography sources.
It is implemented in **Python** using the [MPh](https://github.com/MPh-py/MPh) wrapper over the COMSOL Java API to automate geometry creation, physics/BC assignment, solving, and post-processing.

---

## ✨ Key Features

- **All-Python pipeline** via MPh (no manual GUI steps required).
- **Externalized parameters** (no hardcoding): global material/geometry/solver values in `global_parameters_pp_v2.txt`, laser/beam in `laser_parameters_pp_v2.txt`, and an analytic laser pulse `P(t)` in `Ppp_analytic_expression.txt`.
- **Advanced Physics:** Heat Transfer (HT), Transport of Diluted Species (TDS), Laminar Flow (SPF), **ALE** moving mesh, **surface tension**, **Marangoni effect**, **recoil pressure**, and **Hertz-Knudsen evaporation** with a latent-heat sink.
- **Robust Laser Modeling:** Fresnel absorption at the droplet boundary with a Gaussian spatial profile and user-defined `P(t)`. Includes an automatic "shadowing" effect.
- **Reproducible outputs** (PNG + CSV) and a saved `.mph` model with custom views for easy GUI inspection.

---

## 📦 Repository Structure
```
.
├─ src/
│ └─ pp_model.py              # Main MPh script (build → solve → post → save)
├─ data/
│ ├─ global_parameters_pp_v2.txt
│ ├─ laser_parameters_pp_v2.txt
│ └─ Ppp_analytic_expression.txt
├─ results/                   # Outputs written here (PNG, CSV, MPH)
├─ EVAPORATION_PHYSICS_REFERENCE/ # Reference COMSOL models and notes (evaporation & laser HT)
├─ pyproject.toml             # Project metadata and dependencies for uv
├─ requirements.txt           # Dependencies for pip
└─ README.md
```

> Notes:
> - The script reads parameters from `data/` and writes outputs to `results/` by default.
> - Geometry matches the COMSOL Java demo: a rectangle from `(0,0)` with size `(Lx,Ly)` and a circular droplet of radius `R` centered at `(Lx/2, Ly/2)`.
> - Laser incidence is direction-aware: default `laser_theta_deg = 0°` means light travels along +x (west → east), heating the west-facing droplet boundary and shadowing the east side.
> - Beam center defaults: `x_beam = Lx/2`, `y_beam = Ly/2` when not set (or set to zero-like values).

---

## Additive Module Layout (Scaffolded)

The following packages are added for future organization (non-breaking, opt-in). See their READMEs for intent and guidelines:

- `src/core/config/` — Configuration management (Pydantic models, loader, factory)
- `src/core/physics/` — Physics modules scaffolding (HT, TDS, SPF, ALE)
- `src/core/geometry/` — Geometry builder scaffolding
- `src/core/solvers/` — Solver/study orchestration scaffolding (runner)
- `src/core/adapters/` — Adapters layer isolating MPh/COMSOL (scaffold)
- `src/models/` — Existing Fresnel/Kumar variants; ABCs in `base.py`; simple plugin `registry.py`
- `src/io/` — IO helpers (CSV/JSON/Parquet) and compare CLI [scaffold]
- `src/validation/` — Additional validators beyond Pydantic [scaffold]
- `src/visualization/` — Shared plotting utilities [scaffold]

These are additive only; current entry points and physics remain unchanged by default.

Interfaces (Phase 2 scaffolds)
- ABCs: AbsorptionModel, PhysicsVariant, Solver, SessionIface (future adapters)
- Adapters: `core/adapters/mph_adapter.py` with MphSessionAdapter + ModelAdapter (mockable)
- Plugins: explicit registry in `models/registry.py` (opt-in; not used by defaults)
- Async/parallel: deferred; consider process-based sweep runner in Phase 3

---

## Maintenance

Use `make clean` to remove Python caches and test artifacts without touching `data/` or `results/`.

```
make clean
```


## 🔧 Requirements

- **COMSOL Multiphysics 6.2** (with Java API available) and a valid license.
- **Python 3.10+**.
- **MPh** library (installs automatically with the steps below).

---

## 🛠️ Setup

You can use the project bootstrap script, **uv** (recommended), or plain **pip**.

### Option A — uv (Recommended)

```bash
# Create a virtual environment
uv venv

# Activate the environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Bash (Linux/macOS):
source .venv/bin/activate

# Install runtime dependencies (pyproject)
uv pip install -e .

# For development (tests, etc.)
uv pip install -e .[dev]
```

### Option B — pip

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
pip install -e .
pip install -r requirements.txt  # only if you cannot use pyproject
```

---

## 🚀 Running the Simulation

```bash
# Run with uv (Fresnel, default)
uv run python src/pp_model.py --absorption-model fresnel

# Kumar variant (paper-faithful BCs/sources)
uv run python src/pp_model.py --absorption-model kumar

# Validate only (schema + geometry sanity) without COMSOL
uv run python src/pp_model.py --check-only

# Use custom dirs
uv run python src/pp_model.py --params-dir ./data --out-dir ./results

# Build-only (no solve): generate the .mph model
uv run python src/pp_model.py --no-solve

# Build-only COMSOL smoke (writes .mph; requires local COMSOL)
uv run python src/pp_model.py --no-solve --emit-milestones --absorption-model fresnel
uv run python src/pp_model.py --no-solve --emit-milestones --absorption-model kumar
```

### Fresnel Precompute (Sizyuk)

Generate small, versionable tables from n,k optics for the Fresnel path. Run once per n,k dataset.

```bash
# Precompute Sizyuk tables & plots (from repo root)
python src/pp_sizyuk.py --nk-file data/nk_optics.xlsx --out-root .
```

Artifacts:
- Tables: `data/derived/sizyuk/absorptivity_vs_lambda.csv`, `reflectivity_vs_lambda.csv`, `sizyuk_manifest.json`
- Plots:  `results/sizyuk/plots/absorptivity_vs_lambda.png`

See `docs/workflow_fresnel.md` for full details.

Or use the installed console script after `make install`:

```bash
# Fresnel (default)
uv run euv-sim --absorption-model fresnel

# Kumar
uv run euv-sim --absorption-model kumar

# Validate only
uv run euv-sim --check-only
```

On a successful run, you will find the following in your output directory:
- `pp_temperature.png`: Snapshot of the temperature field.
- `pp_T_vs_time.csv`: Time history of the average temperature.
- `pp_massloss_vs_time.csv`: Time history of the total mass loss rate.
- `pp_radius_vs_time.csv`: Time history of the droplet radius.
- `pp_energy_vs_time.csv`: Time history of absorbed/latent/net boundary powers.
  - Includes `P_abs`, `P_lat`, `P_Qb_droplet`, and `P_rad` when radiation is enabled.
- `pp_model_created.mph`: The COMSOL model file, which you can open in the GUI. It includes a custom "Droplet View" for easier inspection.

---

## Configuration & Validation (Additive)

In addition to the legacy TXT parameter files, this repo supports a structured YAML configuration with validation and inheritance.

- Base config: `data/config.yaml`
- Optional local override: `data/config.local.yaml` (values override base keys)

Validation is handled by Pydantic models in `src/core/config/models.py`. Invalid values raise clear errors. If the YAML files are not present, the code falls back to legacy files without changing behavior (a warning may be logged).

Quick check-only run with structured logging:

```bash
LOG_LEVEL=DEBUG python src/pp_model.py --check-only

Optional milestone logging and perf summary (additive):

uv run python src/pp_model.py --check-only --emit-milestones

This wraps the check path with a lightweight runner that emits explicit milestones
(build_start/build_done) and writes a `perf_summary.json` into `results/`.
You can also use it on full runs to time the build phase:

uv run python src/pp_model.py --absorption-model fresnel --emit-milestones --no-solve

When not using `--no-solve` and with `--emit-milestones`, the build and solve phases are timed separately.
```

Provenance is written to `results/meta/provenance.json` for both `--check-only` and full runs.

---

## Logging & Provenance

Structured logging prints JSON lines to stdout. You can set verbosity via an environment variable or CLI flag.

- Environment: `LOG_LEVEL=DEBUG`
- CLI flag: `--log-level DEBUG`

Provenance metadata (run ID, timestamp, git, variant, and config snapshot) is written to `results/meta/provenance.json`.

Additional fields captured (best-effort):
- software: Python, OS, MPh (if importable), COMSOL (n/a without a session)
  and NumPy (if importable)
- git: commit and dirty flag
- schema_version: unified schema version when available
- inputs: optional input file manifest with SHA-256 if you pass `extras={"inputs": [...]}` to `write_provenance`
  - seeds: environment-provided seeds like `PYTHONHASHSEED`, `SEED`, `RANDOM_SEED` when present
  - Fresnel runs: when Sizyuk tables exist under `data/derived/sizyuk/`, they are automatically included in the provenance inputs (CSV + manifest paths with SHA-256).

CSV manifests (additive):
- `results/inputs_manifest.csv` lists input files (path, exists, sha256).
- `results/outputs_manifest.csv` lists expected outputs for full runs (MPH, PNG, CSVs) with existence and hashes.

---

## CLI Exit Codes (additive)

The main CLI maps common error classes to exit codes (default behavior unchanged):

- 0: success
- 2: config error (e.g., invalid YAML)
- 3: COMSOL license/connect error
- 4: runtime error (other)

These codes are used only on failures; successful runs remain 0.

---

## Compare Results (Optional CLI)

You can compare two result directories (CSV files) using the additive CLI `euv-compare`.

Examples:

```bash
# After installing the project (`uv pip install -e .`)
uv run euv-compare --baseline results/baseline --candidate results/candidate --rtol 1e-5 --atol 1e-8 --json results/compare_report.json

# Or via Make (set BASE and CAND)
make compare BASE=results/baseline CAND=results/candidate RTOL=1e-5 ATOL=1e-8
```

The tool compares numeric columns in common CSV files across both directories, prints a JSON summary to stdout, and writes a full report if `--json` is provided. Exit code is `0` when comparisons are within tolerance, `1` otherwise.

You can also invoke comparison via the main CLI (additive; no build):

```bash
uv run python src/pp_model.py \
  --compare-baseline results/baseline \
  --compare-candidate results/candidate \
  --compare-rtol 1e-5 --compare-atol 1e-8 \
  --compare-json results/compare_report.json
```

---

## Progress Logging

When `LOG_LEVEL` is `INFO` or lower, the solver build pipeline emits JSON step events to stdout to help track progress (non-blocking, additive).

- mph_session: phase_start/phase_done with wall-clock time
- mph_ready: pct=0.10
- params_injected: pct=0.20
- geometry_built: pct=0.35
- physics_setup: pct=0.60
- mesh_ready: pct=0.75
- solve_ready or solve_skipped: pct=0.85 or 0.80
- postprocess_done: pct=1.00

Example (pretty-printed for readability):
{"ts": 1690000000.0, "level": "INFO", "event": "phase_start", "phase": "mph_session"}
{"ts": 1690000001.1, "level": "INFO", "event": "phase_done", "phase": "mph_session", "dt_s": 1.1}
{"ts": 1690000001.2, "level": "INFO", "event": "step", "name": "params_injected", "pct": 0.2}

Milestones: build_start/build_done, pre_solve, post_solve, mph_saved (future) are logged where applicable. Perf summary writes to `results/perf_summary.json` when using the runner scaffold, including durations in seconds and human-readable format (e.g., `build_dt_s`, `build_dt_str`, `solve_dt_s`, `solve_dt_str`).


## ⚙️ Parameters

Preferred: `data/config.yaml` (unified schema)

- Sections: `simulation, geometry, materials, environment, laser, absorption, evaporation, radiation, mesh, outputs`.
- Key knobs:
  - `absorption.model: fresnel|kumar` (default fresnel)
  - `absorption.use_nk: true|false` to compute `A_PP` from `absorption.nk_file` at `absorption.lambda_um` (Sizyuk)
  - `absorption.nk_file: path to n,k Excel` and `absorption.lambda_um: e.g., 1.064`
  - `laser.temporal_profile: gaussian|square|ramp_square` (optional override of `P(t)`)
  - `evaporation.p_sat_option: kumar_sn`, or `evaporation.p_sat_expr` string to override
  - `environment.gas: none|H2`, `environment.pressure_torr` (Kumar uses low-pressure H2)
  - `environment.diffusivity_law: t175_over_p` to set gas-side species diffusivity as `D ~ T^1.75/p` (Kumar-inspired)
  - `evaporation.clamp_nonneg: true|false` to clamp negative evaporative flux (condensation) to zero
  - `mesh.evaporation_mesh: true|false` to enable evaporation-driven mesh motion (Kumar)

Legacy still supported: `global_parameters_pp_v2.txt`, `laser_parameters_pp_v2.txt`, `Ppp_analytic_expression.txt` (auto-migrated with deprecation warnings)

### Expected Differences (Fresnel vs. Kumar)
- Heating pattern: Fresnel shows front-side heating with shadowing; Kumar is isotropic Gaussian on the surface.
- Evaporation coupling: Kumar adds gas-side latent heat source and gas-side recoil normal stress; typically stronger evaporation cooling.
- Environment: Fresnel assumes vacuum by default; Kumar supports low-pressure H2 and molar species flux at the interface.
- Psat(T): Kumar uses Clausius–Clapeyron anchored at Sn boiling; Fresnel can use user-specified `p_sat_expr`.
- Optional extras (Kumar flags): radiative losses via `radiation.emissivity`, evaporation-driven mesh motion via `mesh.evaporation_mesh`.

Tips
- Keep only one definition of `A_PP` and `w0` (or define `d_beam` and let `w0 = d_beam/sqrt(2*log(2))`).
- If you omit `y_beam`, it defaults to `Ly/2` to center the beam vertically on the droplet.
- Provide a calibrated `p_sat_expr` (e.g., Clausius–Clapeyron) for evaporation studies; otherwise the model runs with zero net evaporation.

---

## 📐 Geometry Details

- Domain: Rectangle with `pos = [0,0]` and `size = [Lx, Ly]`.
- Droplet: Circle with `pos = [Lx/2, Ly/2]` and `r = R`.
- Selections: Automatic selections for droplet solid, its boundary, and the gas domain.
- Laser: Direction-aware incidence. With `laser_theta_deg = 0°`, west-facing surface receives heat; east side is shadowed.

The above matches `EVAPORATION_PHYSICS_REFERENCE/demo_laser_ht.java` for easier cross-checking.

---

## 🧪 Physics Modules

## 🧠 Physics & Couplings

### Laser Heating (Boundary)
Fresnel: `q_abs_2D = A_PP * I_xy * inc_factor` with `inc_factor ∈ {cos_inc, nx_shadow}`.
Kumar: isotropic Gaussian surface flux with absorptivity (no incidence factor).

### Evaporation Physics
Fresnel: HK-like `J_evap = HK_gamma*(p_sat(T)-p_amb)/sqrt(2*pi*R_gas*T/M_Sn)`; latent heat sink on droplet.
Kumar: `J_evap = (1 - beta_r) * p_sat(T) * sqrt(M_Sn/(2*pi*R_gas*T))`; latent heat sink/source split across interface; gas-side normal stress `-(1+beta_r/2)*p_sat(T)`; optional H2 gas and species molar flux.

### Advanced Fluid Dynamics
The `Laminar Flow` interface includes several important effects for modeling laser-droplet interaction:
- **Surface Tension:** Standard surface tension forces.
- **Marangoni Effect:** Surface tension gradients caused by temperature differences on the droplet surface.
- **Recoil Pressure:** Pressure exerted on the surface by the evaporating material.
---

## 🧪 Tests and Checks

```bash
# Run tests (uv)
PYTHONPATH=$PWD uv run pytest -q

# Quick config validation (no COMSOL required)
uv run python src/pp_model.py --check-only --absorption-model fresnel
uv run python src/pp_model.py --check-only --absorption-model kumar

# Or via Makefile (uses uv under the hood)
make test
make check-fresnel
make check-kumar
```

### Optional: Local pre-push test gate

Enable a fast pre-push gate to catch issues before pushing:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

Bypass in emergencies:

```bash
SKIP_PREPUSH=1 git push
```

### Local vs CI (COMSOL-aware)

Some integration tests require a COMSOL license. These are marked with `@pytest.mark.comsol` and are skipped in CI by default.

Local developer workflow (use the repo virtual env):

```bash
# Activate project venv (recommended)
source .venv/bin/activate

# Fast unit tests (uses PYTHONPATH=$PWD in Makefile)
make test

# COMSOL integration tests (requires license)
make test-comsol

# Quick build/CLI sanity without COMSOL
make check-fresnel
make check-kumar
```

Notes:
- If uv warns about hardlinking, set `UV_LINK_MODE=copy` or pass `--link-mode=copy`.
- If you prefer editable installs: `uv pip install -e .[dev]` inside `.venv`.
- CI runs in fresh environments and doesn’t require your local COMSOL license.

---

## 🔀 Branching Strategy & CI

Branches:
- `main` — protected, always green. Merges happen via PR with tests passing and at least one review.
- `dev` — active development. Feature branches open PRs into `dev`. Small PRs may merge to `dev` directly after tests pass.

CI:
- GitHub Actions runs tests on pushes and PRs to `main` and `dev` (`.github/workflows/ci.yml`).
- Use `uv` for fast, reproducible installs.

Contribution flow:
1. Branch from `dev`: `git checkout -b feature/<short-name>`
2. Commit changes and push.
3. Open a PR into `dev`; ensure tests pass.
4. Periodically open a release PR from `dev` to `main` with version bump and changelog.

Protections:
- `main`: requires PR review, conversation resolution, no force-push, no deletion.
- `dev`: requires CI checks (tests, smoke) but no reviews by default. You may push directly or use PRs for visibility.

## 🧩 Configuration & Validation (new)

You can provide a structured YAML config at `data/config.yaml` (optionally overridden by `data/config.local.yaml`). The loader merges base → override and validates with Pydantic. Existing legacy text parameter files remain supported.

Example override:

```
# data/config.local.yaml
simulation:
  t_end: 2.0e-7
laser:
  wavelength_um: 1.06
absorption:
  model: fresnel
environment:
  gas: none
```

## 📜 Logging & Provenance (new)

Structured JSON logs are emitted to stdout. Control verbosity via `LOG_LEVEL` (DEBUG/INFO/WARN/ERROR).

Provenance metadata is written to `results/meta/provenance.json` for both `--check-only` and full runs.

Example:

```bash
LOG_LEVEL=DEBUG uv run python src/pp_model.py --check-only
```
