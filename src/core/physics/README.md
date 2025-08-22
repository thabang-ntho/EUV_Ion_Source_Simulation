# Physics Modules (Scaffold)

This package will host physics builders for COMSOL/MPh, e.g.,
- Heat transfer
- Species transport
- Laminar flow, surface tension, Marangoni

Current implementation remains in `src/core/build.py`. Additions here must be
opt-in and preserve existing behavior.

Quick environment one-liner (KUMAR-2D)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```
