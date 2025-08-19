# Fresnel Precompute (Sizyuk) Workflow

- Input: `data/nk_optics.(xlsx|csv)` with columns `[lambda_um, n, k]`.
- Tool: `src/pp_sizyuk.py` (dual-use script + module).
- Outputs:
  - Tables (versionable): `data/derived/sizyuk/`
    - `absorptivity_vs_lambda.csv` (lambda_um, A)
    - `reflectivity_vs_lambda.csv` (lambda_um, R)
    - `sizyuk_manifest.json` (metadata/summary)
  - Plots (inspection): `results/sizyuk/plots/`
    - `absorptivity_vs_lambda.png`

Run (from repo root):

```bash
# Generate tables + plots
python src/pp_sizyuk.py --nk-file data/nk_optics.xlsx --out-root .
```

Consume in solver:
- Preferred: main simulation reads `data/derived/sizyuk/*.csv` (no Excel import).
- Optional: autogenerate if missing (set in `data/config.yaml`):
  - `absorption.use_precomputed: true`
  - `absorption.autogenerate_if_missing: true`
  - `absorption.nk_file: data/nk_optics.xlsx`
  - `absorption.lambda_um: 1.064`

Troubleshooting:
- Missing Excel engine: install `openpyxl` and ensure file extension is `.xlsx`.
- Bad wavelengths: verify units are micrometers (µm).
- Non-monotone n,k: CSV/XLSX loader filters non-finite values; ensure columns are numeric.

