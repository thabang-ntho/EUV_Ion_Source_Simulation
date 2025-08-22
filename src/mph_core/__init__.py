"""
MPh Core Package

High-level MPh API-based modules for COMSOL model building.
Replaces low-level Java API with Pythonic MPh interfaces.
"""

from .model_builder import ModelBuilder
from .geometry import GeometryBuilder
from .selections import SelectionManager
from .physics import PhysicsManager
from .materials import MaterialsHandler
from .studies import StudyManager
from .postprocess import ResultsProcessor

__all__ = [
    'ModelBuilder',
    'GeometryBuilder', 
    'SelectionManager',
    'PhysicsManager',
    'MaterialsHandler',
    'StudyManager',
    'ResultsProcessor'
]
