from pathlib import Path
from scripts.sweep_demo import run_demo


def test_sweep_demo_writes_csv(tmp_path: Path):
    out = tmp_path / "demo.csv"
    p = run_demo(out)
    assert p.is_file()
    head = p.read_text(encoding="utf-8").splitlines()[0]
    assert "a" in head and "b" in head and "value" in head

