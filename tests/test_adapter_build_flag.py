import sys
import types
from pathlib import Path

from src.pp_model import main as pp_main


def test_adapter_build_flag_creates_mph(tmp_path, monkeypatch):
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

    def start():
        return DummyClient()

    dummy_mph = types.SimpleNamespace(start=start)
    monkeypatch.setitem(sys.modules, "mph", dummy_mph)

    out_dir = tmp_path / "out"
    argv = ["prog", "--adapter-build", "--out-dir", str(out_dir)]
    monkeypatch.setattr(sys, "argv", argv)

    pp_main()

    mph_path = out_dir / "pp_adapter_build.mph"
    assert mph_path.is_file()
