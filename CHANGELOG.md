# Changelog

All notable changes to this project will be documented here.

The project adheres to non-breaking, additive changes by default. Existing CLI
behavior and physics are preserved unless explicitly marked as opt-in.

## Unreleased (0.13-dev)

Additive scaffolds and developer conveniences:
- CLI: `--use-adapter` flag to run a minimal MPh adapter smoke and exit (non-breaking).
- Plugins: explicit registry scaffold with a small example and tests.
- Config: friendlier schema_version handling with a warning on mismatch.
- Solvers: added sequential sweep stub (`core/solvers/sweep.py`) for future process-based runs.
- Manifests: inputs/outputs CSV now include `size_bytes` and `mtime_iso` columns.
- Runner: prints a one-line timing summary after runs with `--emit-milestones`.
- CLI UX: `--summary-only` suppresses JSON logs and relies on the printed timing summary.

## Phase 1 — Architecture & Observability (2025-08-19)

High-impact, low-risk improvements implemented without breaking existing flows.

- Configuration (additive):
  - Added Pydantic v2 models and a loader with inheritance and in-process cache under `src/core/config/`.
  - `pp_model.py` validates structured YAML when present; otherwise falls back to legacy TXT files with a warning.
- Logging & provenance:
  - Structured JSON logging with optional `LOG_LEVEL` env var and `--log-level` CLI flag.
  - `write_provenance` writes run metadata to `results/meta/provenance.json`.
  - Progress helpers (`log_step`, `phase_timer`) added and integrated into build pipeline (additive).
- Error handling & resilience:
  - Small, bounded retry for `mph.start()`; `--check-only` path avoids COMSOL entirely.
  - Custom exception types available under `src/core/errors.py` for future use.
- Developer experience:
  - Makefile targets: `lint`, `test-cov`, and `provenance` (additive).
  - Tests cover config parsing, provenance write, and error messages (all pass locally).
- Scaffolding (future work):
  - `src/models/base.py` introduces ABCs for AbsorptionModel and PhysicsVariant.
  - Docs: `docs/sweeps/README.md` (sweep API draft) and `docs/data_formats.md` (Parquet/HDF5 notes).

Notes
- No files were moved or renamed in `src/`; Fresnel vs. Kumar split and Sizyuk precompute remain intact.
- All enhancements are opt-in and default-off; legacy behavior remains the default path.

## 0.1.1 — CI, branching workflow, and docs (2025-08-20)

- Continuous Integration:
  - Added GitHub Actions workflow `CI` with `tests` and `smoke` jobs (no COMSOL in CI).
  - Uses `uv` to install and run tests for speed and reproducibility.
- Branch protections & workflow:
  - Protected `main` with PR-only merges; `dev` for iterative work.
  - Enabled auto-delete of merged branches; added CODEOWNERS and PR template.
- Developer UX:
  - Introduced `bootstrap.sh` for first-time setup; expanded Makefile (smoke, test-comsol, lint, coverage).
  - Optional `.githooks/pre-push` to run fast checks locally.
- Documentation:
  - README updated with local-vs-CI strategy, COMSOL test marker, and usage notes.

This release is prepared in PR #1 (dev → main) and is non-breaking.

## Phase 1.1 — Config caching, milestones, compare CLI (2025-08-20)

Additive enhancements building on Phase 1, keeping defaults unchanged.

- Configuration:
  - Content-hash caching (merged YAML + env-sensitive keys: COMSOL_HOST/PORT, JAVA_HOME, COMSOL_HOME) in `src/core/config/loader.py`.
  - Frozen Pydantic models provide an immutable view; `schema_version` attached if missing.
- Logging & provenance:
  - Milestones (`build_start`, `build_done`, pre/post_solve reserved) and phase timers emit JSON events; RSS memory reported where available.
  - Provenance enriched with Python/OS/MPh/NumPy versions, git commit + dirty flag, schema_version, optional seeds (`PYTHONHASHSEED`, `SEED`, `RANDOM_SEED`), and inputs manifest (paths + SHA-256).
  - Fresnel runs automatically include Sizyuk tables (if present) in provenance inputs.
- Errors:
  - `SimError` now carries an optional `suggested_fix`; standardized exit code constants added.
- Session (scaffold):
  - `src/core/session.py` context manager for MPh/COMSOL with bounded retries and targeted diagnostics; not used by default.
- Runner (scaffold):
  - `src/core/solvers/runner.py` exposes a lightweight wrapper to emit milestones and write `results/perf_summary.json`. Enable via `--emit-milestones` (default off).
  - Perf summary now includes timing in seconds and human-readable strings: `build_dt_s`, `build_dt_str`, and when solving, `solve_dt_s`, `solve_dt_str`.
- Results & CLI:
  - `src/io/results.py` adds `compare_results(baseline, candidate, rtol, atol)`.
  - New CLI `euv-compare` and Make target `make compare` for CSV-based regression checks.
  - `src/pp_model.py` supports `--compare-*` flags to run comparisons without building.
- Docs & tests:
  - README updated with milestones, provenance fields, compare CLI, and inputs manifest behavior.
  - ADRs: `docs/adr/ADR-0001-session-and-config.md`, `docs/adr/ADR-0002-adapters-and-results.md`.
  - Tests: config cache invalidation, provenance enrichment, session context (mocked), and result comparison.

All changes are non-breaking; existing CLI usage and physics remain intact by default.

## 0.1.2 — Phase 1.1 rollout (2025-08-20)

This tag captures the Phase 1.1 additive improvements:

- Config: content-hash caching; frozen Pydantic models; schema_version attachment.
- Observability: structured logs; milestone + phase timers; RSS; enriched provenance (Python/OS/MPh/NumPy, COMSOL CLI version, git commit+dirty, seeds, inputs manifest); auto-include Sizyuk tables for Fresnel.
- Runner: `--emit-milestones` optional timing with `results/perf_summary.json` including `build_dt_s/str` and, when solving, `solve_dt_s/str`.
- CLI & tooling: `euv-compare` script and `--compare-*` flags; Make `compare` target; CSV inputs/outputs manifests in `results/` (additive).
- Errors: standardized exit codes (0/2/3/4); suggested_fix surfaced when available.
- COMSOL local-only smokes: session start and CLI build-only; gated by `RUN_COMSOL=1`.

No breaking changes; defaults unchanged.
