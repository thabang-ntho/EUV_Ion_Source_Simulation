from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbsorptionModel(ABC):
    @abstractmethod
    def build(self, params: dict[str, Any]) -> Any:
        """Attach absorption/BCs to a given model object.

        This is a future-facing interface; current code paths call concrete
        builder functions directly. Subclasses may wrap existing functions.
        """
        raise NotImplementedError


class PhysicsVariant(ABC):
    @abstractmethod
    def configure(self, model: Any, params: dict[str, Any]) -> None:
        """Configure physics interfaces, couplings, and outputs on model.

        Pure scaffold for future consistency across Fresnel/Kumar variants.
        """
        raise NotImplementedError


# TODO(phase-3): plugin discovery via entry points
# Suggested approach (commented out to avoid runtime behavior changes):
#
# from importlib.metadata import entry_points
# PLUGIN_GROUP = "euv_sim.plugins"
#
# def discover_plugins() -> dict[str, object]:
#     """Discover registered plugins via entry points.
#
#     Returns a mapping name -> loaded object.
#     """
#     eps = entry_points().select(group=PLUGIN_GROUP)
#     out = {}
#     for ep in eps:
#         try:
#             out[ep.name] = ep.load()
#         except Exception:
#             # Intentionally swallow to keep discovery best-effort
#             continue
#     return out
