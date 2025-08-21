from src.mph_core.materials import MaterialsHandler


class FakeNode:
    def __init__(self, tag='node'):
        self._tag = tag
        self._props = {}
        self._children = {}
    def tag(self): return self._tag
    def name(self): return self._tag
    def property(self, k, v=None):
        if v is None:
            return self._props.get(k)
        self._props[k] = v
    def __truediv__(self, key):
        if key not in self._children:
            self._children[key] = FakeNode(f"{self._tag}/{key}")
        return self._children[key]
    def select(self, *_a, **_k): pass


class FakeMaterials:
    def __init__(self): self.created = {}
    def create(self, *_a, name='created', **_k):
        node = FakeNode(name)
        self.created[name] = node
        return node


class FakeModel:
    def __init__(self): self._materials = FakeMaterials()
    def __truediv__(self, key):
        if key == 'materials':
            return self._materials
        raise KeyError(key)


def test_materials_handler_defines_basic_properties():
    model = FakeModel()
    params = {
        'Tin_Density_Solid': 7310,
        'Tin_Density_Liquid': 6990,
        'Tin_Thermal_Conductivity_Solid': 66.8,
        'Tin_Thermal_Conductivity_Liquid': 32.0,
        'Tin_Heat_Capacity_Solid': 228,
        'Tin_Heat_Capacity_Liquid': 243,
        'Tin_Melting_Temperature': 505.08,
    }
    mh = MaterialsHandler(model, params)
    mats = mh.create_all_materials()
    assert 'tin' in mats
    basic = mats['tin']/'Basic'
    # Properties should have been set
    assert basic.property('density') is not None
    assert basic.property('thermalconductivity') is not None
    assert basic.property('heatcapacity') is not None
    # Validate materials sees required props
    validation = mh.validate_materials()
    assert validation.get('tin') is True

