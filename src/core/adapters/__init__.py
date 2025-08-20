"""Adapters layer (scaffold, additive).

The goal is to isolate vendor-specific surfaces (e.g., MPh/COMSOL) behind
minimal, mockable interfaces for integration tests and future portability.

Current code paths do not depend on this package by default; it is provided
for Phase 2 scaffolding and can be wired in incrementally.
"""

