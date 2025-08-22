"""Config package (additive): Pydantic models and loader.

This package is optional and non-breaking. Existing legacy config paths
remain supported via src/core/params.py. Use this for structured YAML.
"""

from .models import RootConfig, Simulation, Laser, Absorption, Environment
from .loader import load_config, cache_config

__all__ = [
    "RootConfig",
    "Simulation",
    "Laser",
    "Absorption",
    "Environment",
    "load_config",
    "cache_config",
]
