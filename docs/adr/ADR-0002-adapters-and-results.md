# ADR-0002: Adapters Layer and Result Manifest

Decision: Scaffold a solver runner (`src/core/solvers/runner.py`) and a results manifest helper (`src/io/results.py`) to standardize milestone logging, perf summaries, and result recording. Keep adapters thin and mockable.

Status: Proposed (scaffold only; non-breaking).

## Rationale

- Future integration tests benefit from a stable runner contract and result schema without binding to COMSOL internals.
- A JSON manifest simplifies regression comparison and provenance.

## Notes

- No default behavior changes. Existing entry points do not call the runner automatically.

