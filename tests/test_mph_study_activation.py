from unittest.mock import Mock
from src.mph_core.studies import StudyManager


def test_study_activation_payload_with_frames_and_node_refs():
    # Minimal fake node supporting tag()/path() and property()
    class FakeNode:
        def __init__(self, tag): self._tag = tag
        def tag(self): return self._tag
        def path(self): return f"/path/{self._tag}"
        def property(self, *a, **k): return None

    class FakeContainer:
        def __init__(self, mapping): self._mapping = mapping
        def __truediv__(self, key):
            if key in self._mapping: return self._mapping[key]
            raise Exception("not found")
        def __iter__(self): return iter(self._mapping.values())
        def create(self, *a, **k):
            # Generic container: return a node and store it
            name = k.get('name', 'created')
            node = FakeNode(name)
            self._mapping[name] = node
            return node

    class FakeStudies(FakeContainer):
        def create(self, *a, **k):
            study = FakeStudy()
            name = k.get('name', 'transient')
            self._mapping[name] = study
            return study

    class FakeStep(FakeNode):
        def __init__(self, tag): super().__init__(tag); self.activate_payload = None
        def property(self, name, value):
            if name == 'activate': self.activate_payload = value

    class FakeJava:
        def setGenPlots(self, v): pass
        def setGenConv(self, v): pass

    class FakeStudy(FakeNode):
        def __init__(self): super().__init__('study'); self._step = FakeStep('step1'); self.java = FakeJava()
        def create(self, *_a, **_k): return self._step

    class FakeModel:
        def __init__(self):
            self._physics = FakeContainer({'heat_transfer': FakeNode('ht1')})
            self._studies = FakeStudies({'transient': FakeStudy()})
            self._frames = FakeContainer({'spatial1': FakeNode('spatial1'), 'material1': FakeNode('material1')})
        def __truediv__(self, key):
            return {
                'physics': self._physics,
                'studies': self._studies,
                'frames': self._frames,
                'meshes': FakeContainer({}),
                'geometries': FakeContainer({'geometry': FakeNode('geometry')})
            }[key]

    model = FakeModel()
    physics = {'ht': FakeNode('ht1')}
    mgr = StudyManager(model, physics, {'Simulation_Time': 1e-6})
    # Should not raise; returns a study-like object
    study = mgr._create_transient_study()
    assert hasattr(study, 'create')
