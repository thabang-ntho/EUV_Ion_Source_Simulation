from src.mph_core.selections import SelectionManager


class FakeNode:
    def __init__(self, tag='node'):
        self._tag = tag
        self._props = {}
    def tag(self): return self._tag
    def property(self, k, v=None):
        if v is None:
            return self._props.get(k)
        self._props[k] = v
    def select(self, *a, **k): pass
    def __truediv__(self, key):
        # Subnode
        node = FakeNode(f"{self._tag}/{key}")
        return node


class FakeContainer:
    def __init__(self):
        self._map = {}
    def create(self, *_a, name='created', **_k):
        node = FakeNode(name)
        self._map[name] = node
        return node
    def __truediv__(self, key): return self._map[key]


class FakeModel:
    def __init__(self):
        self._selections = FakeContainer()
    def __truediv__(self, key):
        if key == 'selections':
            return self._selections
        raise KeyError(key)


def test_selection_manager_creates_expected_names():
    model = FakeModel()
    geom = type('G', (), {'geom_params': type('P', (), {'domain_width':1.0,'domain_height':1.0})()})()
    params = {'Lx': 2.0e-4, 'Ly': 3.0e-4, 'R': 1.0e-5, 'x_beam': 1.0e-4, 'y_beam': 1.5e-4}
    mgr = SelectionManager(model, geom, params)
    sels = mgr.create_all_selections()
    assert 's_drop' in sels
    assert 's_gas' in sels
    assert 's_surf' in sels
    # Validate returns no errors for existence
    assert mgr.validate_selections() == []

