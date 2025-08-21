from src.mph_core.physics import PhysicsManager


class FakeNode:
    def __init__(self, tag='node'):
        self._tag = tag
        self._selected = None
        self._children = {}
    def tag(self): return self._tag
    def typename(self): return 'HeatTransfer'
    def select(self, sel): self._selected = sel
    def __truediv__(self, key):
        if key not in self._children:
            self._children[key] = FakeNode(f"{self._tag}/{key}")
        return self._children[key]
    def create(self, *_a, **_k):
        node = FakeNode('created')
        self._children['created'] = node
        return node
    def isActive(self): return True


class FakeContainer:
    def __init__(self): self.created = []
    def create(self, *_a, **_k):
        node = FakeNode(_k.get('name','heat_transfer'))
        self.created.append(node)
        return node
    def __truediv__(self, key): return FakeNode(key)


class FakeModel:
    def __init__(self):
        self._physics = FakeContainer()
    def __truediv__(self, key):
        if key == 'physics':
            return self._physics
        if key == 'geometries':
            return FakeContainer()
        raise KeyError(key)


def test_physics_manager_creates_ht_and_selects_drop():
    model = FakeModel()
    selections = {'s_drop': FakeNode('s_drop')}
    materials = {'tin': FakeNode('tin')}
    pm = PhysicsManager(model, selections, materials)
    physics = pm.setup_all_physics('fresnel')
    assert 'ht' in physics
    ht = physics['ht']
    assert isinstance(ht, FakeNode)
    assert ht._selected is selections['s_drop']

