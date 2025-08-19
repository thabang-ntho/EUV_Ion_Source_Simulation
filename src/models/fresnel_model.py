"""
Fresnel variant wrapper.

Currently uses the in-module builder in src.pp_model to construct the model
with direction-aware incidence and optional shadowing. This file provides a
stable import path for future refactors and for external tools.
"""

from pathlib import Path
from typing import Optional


def build(no_solve: bool, params_dir: Optional[Path], out_dir: Optional[Path]):
    from ..core.build import build_model
    return build_model(no_solve=no_solve, params_dir=params_dir, out_dir=out_dir,
                       absorption_model="fresnel", check_only=False)
