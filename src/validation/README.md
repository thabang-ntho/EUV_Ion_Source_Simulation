# Validation (Scaffold)

Use this package for cross-field or domain-specific validators beyond the
Pydantic models in `src/core/config/models.py`.

Examples (future):
- Geometry consistency checks.
- Physics parameter coupling constraints.
Quick environment one-liner (KUMAR-2D)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```
