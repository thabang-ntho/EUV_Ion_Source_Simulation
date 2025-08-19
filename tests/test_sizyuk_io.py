from pathlib import Path
import json

from src.pp_sizyuk import run_sizyuk


def test_sizyuk_outputs(tmp_path: Path):
    # Prepare a minimal nk CSV (lambda_um, n, k)
    nk_csv = tmp_path / "nk.csv"
    nk_csv.write_text("lambda_um,n,k\n0.8,2.0,3.0\n1.0,2.0,3.0\n1.2,2.0,3.0\n", encoding="utf-8")

    out_tables = tmp_path / "tables"
    out_plots = tmp_path / "plots"
    manifest = run_sizyuk(nk_csv, out_tables, out_plots, config=None)

    assert out_tables.exists() and any(out_tables.iterdir())
    assert out_plots.exists() and any(out_plots.iterdir())
    # basic manifest shape
    assert "tables" in manifest and "plots" in manifest
    # manifest file exists
    mf = out_tables / "sizyuk_manifest.json"
    assert mf.is_file()
    js = json.loads(mf.read_text(encoding="utf-8"))
    assert js.get("tables") and js.get("plots")

