import sys
import types

from src.pp_model import main as pp_main


def test_use_adapter_flag_smoke(monkeypatch):
    # Provide a dummy mph module for session start
    class DummyClient:
        def create(self, name):
            return {"name": name}

        def close(self):
            pass

    def start():
        return DummyClient()

    dummy_mph = types.SimpleNamespace(start=start)
    monkeypatch.setitem(sys.modules, "mph", dummy_mph)

    argv = ["prog", "--use-adapter"]
    monkeypatch.setattr(sys, "argv", argv)

    # Should complete without raising
    pp_main()

