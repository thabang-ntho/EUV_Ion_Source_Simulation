import sys
import types
from pathlib import Path

from src.pp_model import main as pp_main


class DummyModel:
    def __init__(self):
        self.saved = None

    def save(self, path: str):
        p = Path(path)
        p.write_text("dummy mph", encoding="utf-8")


class DummyClient:
    def create(self, name):
        return DummyModel()

    def close(self):
        pass


def install_dummy_mph(monkeypatch):
    def start():
        return DummyClient()
    dummy_mph = types.SimpleNamespace(start=start)
    monkeypatch.setitem(sys.modules, "mph", dummy_mph)


def test_adapter_build_fresnel(tmp_path: Path, monkeypatch):
    install_dummy_mph(monkeypatch)
    out_dir = tmp_path / "out"
    argv = ["prog", "--adapter-build-fresnel", "--out-dir", str(out_dir)]
    monkeypatch.setattr(sys, "argv", argv)
    pp_main()
    assert (out_dir / "pp_adapter_build_fresnel.mph").is_file()


def test_adapter_build_kumar(tmp_path: Path, monkeypatch):
    install_dummy_mph(monkeypatch)
    out_dir = tmp_path / "out"
    argv = ["prog", "--adapter-build-kumar", "--out-dir", str(out_dir)]
    monkeypatch.setattr(sys, "argv", argv)
    pp_main()
    assert (out_dir / "pp_adapter_build_kumar.mph").is_file()

