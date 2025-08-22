Async/Parallel Parameter Sweeps (Phase 3 — Draft)
=================================================

Goal
- Allow running many short simulations across a small parameter grid (e.g., A_PP, w0, beta_r).
- Provide a consistent API that can later reuse the same config and provenance machinery.

Intended API (future)
- Python:
  from src.sweeps import run_sweep
  results = run_sweep(param_grid={"laser.A_PP": [0.3, 0.4, 0.5], "mesh.n_bl": [3, 5]},
                      variant="fresnel", check_only=True, max_parallel=4)

- CLI:
  python -m src.sweeps --grid laser.A_PP=0.3,0.4,0.5 --grid mesh.n_bl=3,5 --check-only --variant fresnel --parallel 4

Execution Model (future)
- Start with synchronous execution; add optional parallelism via multiprocessing.
- Optional async execution (e.g., with an external job queue) for HPC clusters.

Artifacts (future)
- Each run writes to results/sweep/<run_id>/ with its own provenance.json and compact CSV outputs.
- A sweep index (JSON) aggregates parameters and key metrics for quick analysis.

Manifest pattern (planned)
- Each sweep run writes a small manifest (JSON/CSV) enumerating the parameter grid and output paths.
- Manifests include the schema_version, tool version, and a pointer to per-run provenance.
- Default outputs (CSV/PNG) are retained; Parquet/HDF5 remain opt-in per data formats guidance.

Notes
- Implementation will be strictly additive and opt-in; no changes to default CLI behavior.
