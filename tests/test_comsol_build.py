import os
import pytest


pytestmark = [
    pytest.mark.comsol,
    pytest.mark.skipif(os.environ.get("RUN_COMSOL") != "1", reason="COMSOL local-only; set RUN_COMSOL=1 to enable"),
]
def test_mph_session_and_model_creation():
    """Local-only smoke: ensure mph can start and create a model.

    This test requires a working COMSOL installation and license. It is marked
    as `comsol` and should not be run in CI. Run locally with:
      make test-comsol
    """
    import mph  # type: ignore

    client = mph.start()
    model = client.create("pp_smoke")
    assert model is not None
    try:
        if hasattr(client, "close"):
            client.close()
    except Exception:
        pass
