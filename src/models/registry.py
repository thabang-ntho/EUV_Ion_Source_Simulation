from __future__ import annotations

from typing import Dict, Any

_REGISTRY: Dict[str, Any] = {}


def register(name: str, obj: Any) -> None:
    if not name or not isinstance(name, str):
        raise ValueError("Plugin name must be a non-empty string")
    _REGISTRY[name] = obj


def get(name: str) -> Any:
    return _REGISTRY.get(name)


def list_plugins() -> Dict[str, Any]:
    return dict(_REGISTRY)

