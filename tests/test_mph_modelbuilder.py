import os
from pathlib import Path
from unittest.mock import patch, Mock

from src.mph_core.model_builder import ModelBuilder


def test_connect_uses_host_port_env(monkeypatch):
    monkeypatch.setenv('COMSOL_HOST', '127.0.0.1')
    monkeypatch.setenv('COMSOL_PORT', '2036')
    with patch('src.mph_core.model_builder.mph') as mock_mph:
        mock_client = Mock()
        mock_mph.start.return_value = mock_client
        b = ModelBuilder({'Output_Directory':'results'}, 'fresnel')
        b._connect_to_comsol()
        mock_mph.start.assert_called_with(host='127.0.0.1', port=2036)


def test_build_complete_model_saves_file(tmp_path, monkeypatch):
    # Patch mph.start
    with patch('src.mph_core.model_builder.mph') as mock_mph:
        class FakeModel:
            def __init__(self): self.saved=None
            def name(self): return 'fake'
            def save(self, p): self.saved = p
            def __truediv__(self, key):
                # Provide minimal containers for _create_model() component ensure
                class C:
                    def __truediv__(self, _k):
                        # cause exception to trigger create path
                        raise Exception('missing')
                    def create(self, *_a, **_k): return object()
                return C()
        class FakeClient:
            def create(self, name): return FakeModel()
            def disconnect(self): pass
        mock_mph.start.return_value = FakeClient()

        # Patch heavy steps to avoid deep dependencies
        b = ModelBuilder({'Output_Directory': str(tmp_path)}, 'fresnel')
        b._build_geometry = lambda: b.build_stages.__setitem__('geometry_built', True)
        b._create_selections = lambda: b.build_stages.__setitem__('selections_created', True)
        b._setup_materials = lambda: b.build_stages.__setitem__('materials_assigned', True)
        b._setup_physics = lambda: b.build_stages.__setitem__('physics_setup', True)
        b._create_studies = lambda: b.build_stages.__setitem__('studies_created', True)

        out = b.build_complete_model(tmp_path/'out.mph')
        assert Path(out).name == 'out.mph'
        assert b.build_stages['client_connected'] is True
        assert b.build_stages['model_created'] is True
        assert b.build_stages['studies_created'] is True

