Advanced Data Management (Future Notes)
======================================

Context
- Current outputs are PNG and CSV tables for portability and ease of diffing.
- For larger sweeps and long runs, a columnar format may be beneficial.

Proposal (future, optional)
- Parquet for tabular outputs (time series, parameter sweeps) to reduce size and speed IO.
- HDF5 for structured arrays (e.g., 2D fields at selected timesteps) with metadata.

Guidelines
- Keep current outputs unchanged by default; add optional flags to enable Parquet/HDF5 alongside CSV.
- Document schema versioning in provenance, and embed field units within dataset metadata.

Interoperability
- Ensure pandas-friendly layouts, and provide simple reader utilities under src/io/ if added later.

Future directions
- Add optional writers (default-off) for Parquet/HDF5 alongside existing CSV/PNG, with a small manifest linking formats. This will remain opt-in and will not change current outputs.
