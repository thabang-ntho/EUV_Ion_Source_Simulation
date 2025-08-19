"""
Kumar variant builder.

For now, this delegates to src.pp_model.build_model with absorption_model="kumar",
which applies Kumar-specific boundary/source adjustments in-place. This module
exists to provide a clean variant entrypoint while we finish the split.
"""

from pathlib import Path
from typing import Optional


def build(no_solve: bool, params_dir: Optional[Path], out_dir: Optional[Path]):
    from ..core.build import build_model
    return build_model(no_solve=no_solve, params_dir=params_dir, out_dir=out_dir,
                       absorption_model="kumar", check_only=False)
