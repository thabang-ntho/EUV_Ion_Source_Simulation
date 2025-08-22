# Solver Wrappers (Scaffold)

This package will provide thin wrappers for study/solution setup and advanced
solver orchestration. The current implementation remains embedded in
`src/core/build.py`.

Planned (optional):
- Time-stepping presets.
- Convergence/reporting hooks.
- Batch/sweep coordination.

Quick environment one-liner (KUMAR-2D)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```
