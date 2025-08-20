import sys
from pathlib import Path

from src.pp_model import main as pp_main


def test_inputs_manifest_has_size_mtime(tmp_path, monkeypatch):
    out_dir = tmp_path / "out"; out_dir.mkdir(parents=True, exist_ok=True)
    argv = ["prog", "--check-only", "--absorption-model", "fresnel", "--out-dir", str(out_dir)]
    monkeypatch.setattr(sys, "argv", argv)
    pp_main()
    f = out_dir / "inputs_manifest.csv"
    assert f.is_file()
    head = f.read_text(encoding="utf-8").splitlines()[0]
    assert "size_bytes" in head and "mtime_iso" in head

