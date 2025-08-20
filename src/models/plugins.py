from __future__ import annotations

"""Plugin discovery stubs (Phase 3; no behavior change).

This module centralizes optional plugin registration and (future) discovery.
By default, discovery is disabled; use explicit registration via
`src/models/registry.py`.
"""

from typing import Dict, Any
from . import registry


def discover_plugins() -> Dict[str, Any]:  # pragma: no cover - trivial wrapper
    """Return explicitly registered plugins.

    Future: optionally merge in entry-point based discovery. This is disabled
    by default to keep behavior predictable and CI fast.
    """
    return registry.list_plugins()


# Example (commented): entry-point discovery plan
#
# from importlib.metadata import entry_points
# PLUGIN_GROUP = "euv_sim.plugins"
# def discover_entrypoint_plugins() -> Dict[str, Any]:
#     out: Dict[str, Any] = {}
#     for ep in entry_points().select(group=PLUGIN_GROUP):
#         try:
#             out[ep.name] = ep.load()
#         except Exception:
#             # Keep discovery best-effort and non-fatal
#             continue
#     return out

