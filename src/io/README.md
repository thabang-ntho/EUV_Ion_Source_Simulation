# IO Helpers (Scaffold)

Place optional CSV/JSON/Parquet readers/writers and manifest utilities here.
Current IO remains in existing modules (e.g., Sizyuk precompute in
`src/pp_sizyuk.py`). Any new utilities should be additive and optional.

Quick environment one-liner (KUMAR-2D)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```
