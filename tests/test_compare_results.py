from pathlib import Path
from src.io.results import compare_results
import pandas as pd


def test_compare_results_pass(tmp_path: Path):
    base = tmp_path / "base"; cand = tmp_path / "cand"
    base.mkdir(); cand.mkdir()
    df1 = pd.DataFrame({"t": [0,1,2], "v": [0.0, 1.0, 2.0]})
    df2 = pd.DataFrame({"t": [0,1,2], "v": [0.0, 1.0+1e-7, 2.0]})
    df1.to_csv(base / "a.csv", index=False)
    df2.to_csv(cand / "a.csv", index=False)
    ok, rep = compare_results(base, cand, rtol=1e-6, atol=1e-6)
    assert ok
    assert rep["files"]["a.csv"]["ok"] is True


def test_compare_results_fail(tmp_path: Path):
    base = tmp_path / "base"; cand = tmp_path / "cand"
    base.mkdir(); cand.mkdir()
    df1 = pd.DataFrame({"t": [0,1,2], "v": [0.0, 1.0, 2.0]})
    df2 = pd.DataFrame({"t": [0,1,2], "v": [0.0, 1.1, 2.0]})
    df1.to_csv(base / "a.csv", index=False)
    df2.to_csv(cand / "a.csv", index=False)
    ok, rep = compare_results(base, cand, rtol=1e-6, atol=1e-6)
    assert not ok
    assert rep["files"]["a.csv"]["ok"] is False

