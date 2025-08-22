from pathlib import Path
import types
import sys

from src.core.adapters.mph_adapter import MphSessionAdapter, ModelAdapter


def test_mph_session_adapter_uses_session(monkeypatch):
    calls = {"start": 0}

    class DummyClient:
        def create(self, name):
            return {"name": name}

        def close(self):
            pass

    def start():
        calls["start"] += 1
        return DummyClient()

    dummy_mph = types.SimpleNamespace(start=start)
    monkeypatch.setitem(sys.modules, "mph", dummy_mph)

    adapter = MphSessionAdapter(retries=1, delay=0.0)
    with adapter.open() as client:
        model = ModelAdapter(client).create_model("foo")
        assert model["name"] == "foo"
    assert calls["start"] == 1

