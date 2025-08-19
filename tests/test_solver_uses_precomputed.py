from pathlib import Path
import pandas as pd

from src.pp_model import load_fresnel_tables


def test_load_precomputed(tmp_path: Path):
    base = tmp_path / "data" / "derived" / "sizyuk"
    base.mkdir(parents=True, exist_ok=True)
    # Create a tiny absorptivity table
    dfA = pd.DataFrame({"lambda_um": [0.8, 1.0, 1.2], "A": [0.4, 0.44, 0.46]})
    dfA.to_csv(base / "absorptivity_vs_lambda.csv", index=False)
    # Create reflectivity as well
    dfR = pd.DataFrame({"lambda_um": [0.8, 1.0, 1.2], "R": [0.6, 0.56, 0.54]})
    dfR.to_csv(base / "reflectivity_vs_lambda.csv", index=False)

    data = load_fresnel_tables(tmp_path)
    assert "absorptivity" in data and not data["absorptivity"].empty
    assert "reflectivity" in data and not data["reflectivity"].empty

