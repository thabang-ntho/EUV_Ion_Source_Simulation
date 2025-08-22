# Troubleshooting (Adapters & COMSOL)

This page collects common setup issues for local runs that touch COMSOL or the MPh adapter.

Adapter session fails immediately
- Ensure COMSOL is installed and the `comsol` CLI is on PATH.
- If licensing is remote, verify `COMSOL_HOST` and `COMSOL_PORT` are set appropriately.
- When using Java bindings, ensure `JAVA_HOME` points to a compatible JDK.

`mph.start()` hangs or errors
- Try a minimal session smoke:
  ```bash
  uv run python - <<'PY'
  import mph; c = mph.start(); m = c.create('pp_smoke'); print('mph OK')
  PY
  ```
- If this fails, inspect local firewall and license server connectivity.

`pp_model.py` adapter smokes
- Use `--use-adapter` to only open a session (no build).
- Use `--adapter-build-fresnel` or `--adapter-build-kumar` to create and save a trivial MPH model.
- These are developer-oriented and default-off.

COMSOL in CI
- CI does not run COMSOL; tests that require it are under `@pytest.mark.comsol` and are skipped unless `RUN_COMSOL=1`.

Quick environment one-liner (KUMAR-2D check-only)
```bash
.venv/bin/activate && export \
COMSOL_HOME=/home/xdadmin/comsol62/multiphysics && export \
JAVA_HOME=/home/xdadmin/comsol62/multiphysics/java/glnxa64/jre && \
RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out \
KUMAR-2D/results/kumar2d_model.mph
```

Logs and provenance
- Set `LOG_LEVEL=DEBUG` to print more details.
- Provenance writes to `results/meta/provenance.json`; inspect `software.comsol` and `git` fields for context.
