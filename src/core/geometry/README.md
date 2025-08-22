# Geometry Builders (Scaffold)

Future geometry creation utilities live here. The current geometry is defined
programmatically in `src/core/build.py` to match the COMSOL Java demo.

Guidelines:
- Keep defaults unchanged.
- Export small, composable helpers that can be adopted by the existing build
  flow without breaking changes.

Quick environment one-liner (KUMAR-2D)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```
