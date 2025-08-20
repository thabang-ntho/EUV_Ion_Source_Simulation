# Advanced CLI Flags (Developer Oriented)

These flags are available but hidden from the main `--help` to keep the user
surface focused on Fresnel/Kumar physics. They remain functional for developer
and power-user workflows. All are additive and default-off.

Core usage (visible)
- `--absorption-model {fresnel,kumar}`: Selects physics variant.
- `--check-only`: Validate config and environment without COMSOL.
- `--no-solve`: Build-only MPH model for GUI inspection.
- `--params-dir`, `--out-dir`: Control input/output directories.
- `--log-level`: Logging level.
- `--emit-milestones`: Emit milestone events + perf_summary.json and one-line timing summary.

Hidden advanced flags (still functional)
- `--summary-only`: Suppress JSON logs (use with `--emit-milestones`) and rely on the one-line timing summary.
  - Use-case: human-friendly local runs where you only want timing.
- `--use-adapter`: Open an MPh session via the adapter, create a dummy model, and exit.
  - Use-case: verify session acquisition without invoking the full build.
- `--adapter-build`: Create a trivial model via adapter and save `pp_adapter_build.mph` to `--out-dir`.
- `--adapter-build-fresnel`, `--adapter-build-kumar`: Same as above but variant-named MPH outputs.
  - Use-case: quick sanity checks for adapters and I/O plumbing.
- Deprecated in favor of `euv-compare` (still functional; prints a notice):
  - `--compare-baseline`, `--compare-candidate`, `--compare-rtol`, `--compare-atol`, `--compare-json`
  - Prefer: `uv run euv-compare --baseline ... --candidate ... --rtol ... --atol ... --json ...`

Make targets
- `make compare BASE=... CAND=... [RTOL=1e-5 ATOL=1e-8]`
  - Convenience wrapper around `euv-compare`.

Notes
- None of these change physics defaults or outputs unless explicitly invoked.
- Keep using the main flags for Fresnel/Kumar workflows; advanced flags are for
  session checks, adapter smokes, and timing/provenance enhancements.
