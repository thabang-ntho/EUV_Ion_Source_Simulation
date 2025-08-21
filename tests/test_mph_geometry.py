from unittest.mock import Mock
from src.mph_core.geometry import GeometryBuilder


def test_geometry_builder_create_geometry_calls_build(tmp_path):
    # Fake model with container access via '/' and a build() method
    class FakeNode:
        def __init__(self, tag='node'): self._tag = tag
        def create(self, *a, **k): return FakeNode('created')
        def property(self, *a, **k): return None
        def __truediv__(self, key): return FakeNode(key)

    class FakeModel(FakeNode):
        def __init__(self): super().__init__('model'); self._built = False
        def build(self, node): self._built = True

    model = FakeModel()
    params = {'Lx': 2.0e-4, 'Ly': 3.0e-4, 'R': 1.35e-5, 'x_beam': 1.0e-4, 'y_beam': 1.5e-4}
    gb = GeometryBuilder(model, params)
    gb.create_geometry(model)
    assert model._built is True

