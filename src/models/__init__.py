"""
Model variants for absorption/BCs:
- Fresnel: direction-aware incidence and shadowing (default).
- Kumar: paper-faithful boundary conditions/fluxes adapted from COMSOL.

MPh-based implementations (new):
- mph_fresnel: High-level MPh API Fresnel variant
- mph_kumar: High-level MPh API Kumar variant

These modules progressively encapsulate the variant-specific builders.
"""

# MPh-based model builders (new implementation)
from .mph_fresnel import FresnelModelBuilder, build_fresnel_model
from .mph_kumar import KumarModelBuilder, build_kumar_model

__all__ = [
    'FresnelModelBuilder',
    'KumarModelBuilder', 
    'build_fresnel_model',
    'build_kumar_model'
]

