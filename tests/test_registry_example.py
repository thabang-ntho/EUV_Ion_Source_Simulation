from src.models import registry


def test_registry_register_and_get():
    obj = {"hello": "world"}
    registry.register("dummy_plugin", obj)
    assert registry.get("dummy_plugin") is obj
    allp = registry.list_plugins()
    assert "dummy_plugin" in allp and allp["dummy_plugin"] is obj

