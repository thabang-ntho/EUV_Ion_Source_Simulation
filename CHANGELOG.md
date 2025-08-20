# Changelog

All notable changes to this project will be documented here.

The project adheres to non-breaking, additive changes by default. Existing CLI
behavior and physics are preserved unless explicitly marked as opt-in.

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

