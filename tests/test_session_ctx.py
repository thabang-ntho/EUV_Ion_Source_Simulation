import types
import sys

from src.core.session import Session


def test_session_retries_and_yields_client(monkeypatch):
    calls = {"n": 0}

    class DummyClient:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    def start():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("transient failure")
        return DummyClient()

    # Create a dummy mph module
    dummy_mph = types.SimpleNamespace(start=start)
    monkeypatch.setitem(sys.modules, "mph", dummy_mph)

    with Session(retries=3, delay=0.0) as client:
        assert isinstance(client, DummyClient)
    assert calls["n"] == 2

