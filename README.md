# EUV Tin Droplet — Laser Pre-Pulse Simulation (MPh + COMSOL)

This project models the interaction of a high-energy laser pulse with a **2D planar** liquid tin droplet (sphere → pancake transition) for EUV lithography sources.
It is implemented in **Python** using the [MPh](https://github.com/MPh-py/MPh) wrapper over the COMSOL Java API to automate geometry creation, physics/BC assignment, solving, and post-processing.

> **🚀 MPh Implementation Status (August 2025)**  
> MPh-based architecture **in development** with significant progress. Core modules (geometry, selections, materials) **completed**. Physics and studies modules next. See [MPh Setup Guide](docs/mph/comsol_setup.md) and [Next Steps](docs/mph/NEXT_STEPS.md) for current status.

---

## ✨ Key Features

- **Modern MPh Architecture** with modular design and comprehensive error handling
- **Two Validated Variants**: Fresnel (evaporation-focused) and Kumar (fluid dynamics-focused) models
- **Advanced CLI Interface** with parameter overrides, dry-run mode, and validation
- **All-Python pipeline** via MPh (no manual GUI steps required)
- **Externalized parameters** with automatic configuration detection
- **Advanced Physics:** Heat Transfer (HT), Transport of Diluted Species (TDS), Laminar Flow (SPF), **ALE** moving mesh, **surface tension**, **Marangoni effect**, **recoil pressure**, and **Hertz-Knudsen evaporation** with a latent-heat sink
- **Robust Laser Modeling:** Fresnel absorption at the droplet boundary with a Gaussian spatial profile and user-defined `P(t)`
- **Comprehensive Testing** with both unit and integration test suites
- **Reproducible outputs** (PNG + CSV) and saved `.mph` models with custom views

---

## 🎯 Quick Start

### Prerequisites
- COMSOL Multiphysics 6.2+ with valid license
- Python 3.9+ with MPh library

### Installation & Setup
```bash
# Clone repository
git clone <repository-url>
cd EUV_WORK

# Create and activate virtual environment
source .venv/bin/activate  # Or activate existing venv

# Install dependencies
pip install -r requirements.txt
```

### Run Simulations

#### Modern MPh Interface (Recommended)
We provide a minimal MPh runner that builds (and optionally solves) the model faithfully to `mph_example.py` API patterns.

```bash
# 0) Prepare COMSOL env (local install)
source scripts/setup_comsol_env.sh

# 1) Build-only (no solve); saves results/fresnel_model.mph
# After installing the package (make install), you can use the script:
euv-mph --check-only --variant fresnel --log-level INFO
# Or without installation:
python -m src.cli.mph_runner --check-only --variant fresnel --log-level INFO

# 2) Build + solve; saves results/fresnel_model_solved.mph
#    For remote servers set COMSOL_HOST/COMSOL_PORT via flags or env
euv-mph --solve --variant fresnel --host 127.0.0.1 --port 2036
# Or: python -m src.cli.mph_runner --solve --variant fresnel --host 127.0.0.1 --port 2036

# 3) Custom output and config
euv-mph --check-only --variant kumar --output results/kumar_run.mph --config data/config.yaml
# Or: python -m src.cli.mph_runner --check-only --variant kumar --output results/kumar_run.mph --config data/config.yaml
```

Environment variables (optional):
- `COMSOL_HOST`, `COMSOL_PORT`: point to a remote COMSOL server (overrides local).
- `COMSOL_CORES`: number of server cores to request if supported by `mph.start()`.
You can also pass `--host/--port` flags which are mapped to these envs.

### Environment Variables (Details)

- `COMSOL_HOST` and `COMSOL_PORT`: When set, the runner attempts to connect to a remote COMSOL server using `mph.start(host=..., port=...)`.
- `COMSOL_CORES`: Requests a specific number of cores if your `mph` version supports `mph.start(cores=N)`.
- `JAVA_HOME`, `COMSOL_HOME`, `LMCOMSOL_LICENSE_FILE` (or `LM_LICENSE_FILE`): Must be configured according to your local COMSOL installation. See `scripts/setup_comsol_env.sh` for an example.

Example:
```bash
export COMSOL_HOST=127.0.0.1
export COMSOL_PORT=2036
export COMSOL_CORES=4
python -m src.cli.mph_runner --check-only --variant fresnel
```

#### Legacy Interface
The legacy pp_model CLI has been removed in mph_dev. Use the modern `euv-mph` runner.

---

## 🔧 MPh Implementation Status

### ✅ **Completed Modules:**
- **License Configuration** - COMSOL license setup documented and working
- **MPh API Patterns** - Comprehensive understanding of correct API usage
- **Geometry Builder** (`src/mph_core/geometry.py`) - 2D droplet geometry creation
- **Selection Manager** (`src/mph_core/selections.py`) - Domain and boundary selections  
- **Materials Handler** (`src/mph_core/materials.py`) - Temperature-dependent materials with property assignment

### 🔄 **In Progress:**
- **Physics Manager** (`src/mph_core/physics.py`) - Heat transfer physics setup (base complete)
- **Study Manager** (`src/mph_core/studies.py`) - Transient studies and solving (activation fixed)

### 📚 **Key Resources:**
- **[COMSOL Setup Guide](docs/mph/comsol_setup.md)** - Complete license configuration and troubleshooting
- **[Next Steps Guide](docs/mph/NEXT_STEPS.md)** - Detailed roadmap for completing implementation
- **`mph_example.py`** - Reference implementation showing correct MPh API patterns

### 🚨 **Current Status:**
- Materials, geometry, selections, physics(HT) modules aligned to MPh patterns
- Study activation updated to mirror mph_example (frames + node refs; robust fallback)
- New CLI `euv-mph` for build-only and build+solve flows
- Pytests guarded from accidental COMSOL invocation (enable with `RUN_COMSOL=1`)

---

## 📦 Repository Structure
```
.
├─ src/
│ ├─ mph_core/                # Modern MPh architecture
│ │ ├─ model_builder.py      # Main orchestrator with context management
│ │ ├─ geometry.py           # Geometry creation and management
│ │ ├─ selections.py         # Domain and boundary selections
│ │ ├─ physics.py            # Physics interface configuration
│ │ ├─ materials.py          # Material property management
│ │ ├─ studies.py            # Study and solver configuration
│ │ └─ postprocess.py        # Results extraction and visualization
│ ├─ models/                 # Model variants
│ │ ├─ mph_fresnel.py        # Fresnel evaporation model
│ │ └─ mph_kumar.py          # Kumar fluid dynamics model
│ ├─ cli/
│ │  └─ mph_runner.py       # MPh CLI runner (script: euv-mph)
├─ tests/
│ ├─ mph_integration/        # MPh integration tests
│ ├─ unit/                   # Unit tests
│ └─ conftest.py             # Test configuration
├─ docs/
│ ├─ mph/                    # MPh implementation documentation
│ │ ├─ architecture.md       # Architecture overview
│ │ ├─ user_guide.md         # User guide and examples
│ │ └─ testing.md            # Testing guide
│ └─ mph_*.md                # Implementation notes and migration plan
├─ data/                     # Configuration files
│ ├─ global_parameters_pp_v2.txt
│ ├─ laser_parameters_pp_v2.txt
│ └─ Ppp_analytic_expression.txt
├─ results/                  # Outputs (PNG, CSV, MPH)
└─ pyproject.toml            # Project metadata and dependencies
```
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

## Testing

- Default test run does not invoke COMSOL. COMSOL-only tests are gated by `RUN_COMSOL=1` or explicit `-m comsol` markers.
- Legacy tests (pp_model/low-level Java paths) are skipped under the mph-only focus.
- Quick mph-only sanity:
  - `pytest -q tests/test_cli_help.py` – validates CLI help.
  - `pytest -q tests/test_mph_geometry.py tests/test_mph_selections.py tests/test_mph_materials.py tests/test_mph_physics.py tests/test_mph_study_activation.py tests/test_mph_modelbuilder.py` – core mph tests.
  - `make mph-check` – build-only via MPh saves `.mph` (requires COMSOL env configured but does not solve).
  - `RUN_COMSOL=1 make test-comsol` – enable COMSOL tests if your server is available.

### Troubleshooting Activation

- Set `--log-level DEBUG` (or `LOG_LEVEL=DEBUG`) to print activation payloads and types.
- Ensure a component exists before geometry; the runner creates `component` so frames (`spatial1`, `material1`) are present.
- Activation uses alternating keys/values, e.g., `[physics/'heat_transfer', 'on', 'frame:spatial1', 'on', 'frame:material1', 'on']`.
- If activation fails with “Invalid property value”, the code falls back to stringified node paths; check tags/paths in logs.
- Confirm that the expected physics interface exists (e.g., heat_transfer) and that frame tags match your COMSOL version.


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

# Adapter smoke (opens MPh session via adapter and exits)
uv run python src/pp_model.py --use-adapter
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

Milestones: build_start/build_done, pre_solve, post_solve, mph_saved (future) are logged where applicable. Perf summary writes to `results/perf_summary.json` when using the runner scaffold, including durations in seconds and human-readable format (e.g., `build_dt_s`, `build_dt_str`, `solve_dt_s`, `solve_dt_str`). After runs with `--emit-milestones`, a one-line timing summary is printed (e.g., `Build: 00:00:01.234; Solve: 00:00:05.678`).


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
