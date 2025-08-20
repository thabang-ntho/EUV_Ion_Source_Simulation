"""
MPh Integration Tests

Test suite for the new MPh-based implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from src.mph_core import (
    ModelBuilder, GeometryBuilder, SelectionManager,
    PhysicsManager, MaterialsHandler, StudyManager, ResultsProcessor
)
from src.models.mph_fresnel import FresnelModelBuilder
from src.models.mph_kumar import KumarModelBuilder


class TestMPhCoreModules:
    """Test MPh core module functionality with mocked COMSOL"""
    
    @pytest.fixture
    def mock_model(self):
        """Mock MPh model object"""
        model = Mock()
        model.parameter = Mock()
        model.property = Mock()
        model.geometry = Mock(return_value=Mock())
        model.selections = Mock(return_value=Mock())
        model.materials = Mock(return_value=Mock())
        model.physics = Mock(return_value=Mock())
        model.studies = Mock(return_value=Mock())
        model.meshes = Mock(return_value=Mock())
        model.results = Mock(return_value=Mock())
        model.save = Mock()
        return model
    
    @pytest.fixture
    def test_params(self):
        """Test parameter dictionary"""
        return {
            'Domain_Width': 100e-6,
            'Domain_Height': 100e-6,
            'Droplet_Radius': 25e-6,
            'Droplet_Center_X': 0.0,
            'Droplet_Center_Y': 0.0,
            'Tin_Density_Solid': 7310,
            'Tin_Thermal_Conductivity_Solid': 66.8,
            'Time_End': 1e-6,
            'Output_Directory': 'test_results'
        }
    
    def test_geometry_builder_initialization(self, mock_model, test_params):
        """Test GeometryBuilder initialization"""
        builder = GeometryBuilder(mock_model, test_params)
        
        assert builder.model == mock_model
        assert builder.params == test_params
        assert builder.geom_params.domain_width == 100e-6
        assert builder.geom_params.droplet_radius == 25e-6
    
    def test_geometry_validation(self, mock_model, test_params):
        """Test geometry parameter validation"""
        builder = GeometryBuilder(mock_model, test_params)
        
        # Valid geometry
        assert builder.validate_geometry() == True
        
        # Invalid geometry - droplet too large
        test_params['Droplet_Radius'] = 60e-6  # Larger than domain half-size
        builder = GeometryBuilder(mock_model, test_params)
        assert builder.validate_geometry() == False
    
    def test_geometry_creation(self, mock_model, test_params):
        """Test geometry creation calls"""
        mock_geometry = Mock()
        mock_model.geometry.return_value = mock_geometry
        
        builder = GeometryBuilder(mock_model, test_params)
        builder.create_domain()
        
        # Check that geometry methods were called
        mock_geometry.create.assert_called()
        mock_geometry.run.assert_called_once()
    
    def test_selection_manager_initialization(self, mock_model, test_params):
        """Test SelectionManager initialization"""
        mock_geometry_builder = Mock()
        mock_geometry_builder.geom_params = Mock()
        mock_geometry_builder.geom_params.domain_width = 100e-6
        mock_geometry_builder.geom_params.domain_height = 100e-6
        
        manager = SelectionManager(mock_model, mock_geometry_builder)
        
        assert manager.model == mock_model
        assert manager.geometry == mock_geometry_builder
        assert isinstance(manager.selections, dict)
    
    def test_materials_handler_tin_creation(self, mock_model, test_params):
        """Test tin material creation"""
        mock_materials = Mock()
        mock_tin = Mock()
        mock_materials.create.return_value = mock_tin
        mock_model.materials.return_value = mock_materials
        
        handler = MaterialsHandler(mock_model, test_params)
        materials = handler.create_all_materials()
        
        # Check tin material was created
        assert 'tin' in materials
        mock_materials.create.assert_called_with('Material', tag='tin')
        mock_tin.property.assert_called()
    
    def test_physics_manager_heat_transfer(self, mock_model, test_params):
        """Test heat transfer physics setup"""
        mock_physics = Mock()
        mock_ht = Mock()
        mock_physics.create.return_value = mock_ht
        mock_model.physics.return_value = mock_physics
        
        selections = {'s_drop': Mock(), 's_surf': Mock(), 's_laser': Mock()}
        materials = {'tin': Mock()}
        
        manager = PhysicsManager(mock_model, selections, materials)
        physics_interfaces = manager.setup_all_physics('fresnel')
        
        # Check heat transfer was created
        assert 'ht' in physics_interfaces
        mock_physics.create.assert_called()
        mock_ht.create.assert_called()
    
    def test_study_manager_transient_study(self, mock_model, test_params):
        """Test transient study creation"""
        mock_studies = Mock()
        mock_study = Mock()
        mock_studies.create.return_value = mock_study
        mock_model.studies.return_value = mock_studies
        
        physics_interfaces = {'ht': Mock()}
        
        manager = StudyManager(mock_model, physics_interfaces, test_params)
        studies = manager.create_all_studies()
        
        # Check study was created
        assert 'transient' in studies
        mock_studies.create.assert_called()
        mock_study.create.assert_called()


class TestVariantBuilders:
    """Test variant-specific model builders"""
    
    @pytest.fixture
    def test_params(self):
        """Test parameters for variants"""
        return {
            'Domain_Width': 100e-6,
            'Domain_Height': 100e-6,
            'Droplet_Radius': 25e-6,
            'Output_Directory': 'test_results'
        }
    
    @patch('src.models.mph_fresnel.mph')
    def test_fresnel_builder_initialization(self, mock_mph, test_params):
        """Test FresnelModelBuilder initialization"""
        builder = FresnelModelBuilder(test_params)
        
        assert builder.variant == 'fresnel'
        assert 'Laser_Power' in builder.params  # Fresnel default added
        assert 'Evaporation_Coefficient' in builder.params
    
    @patch('src.models.mph_kumar.mph') 
    def test_kumar_builder_initialization(self, mock_mph, test_params):
        """Test KumarModelBuilder initialization"""
        builder = KumarModelBuilder(test_params)
        
        assert builder.variant == 'kumar'
        assert 'Volumetric_Heat_Generation' in builder.params  # Kumar default added
        assert 'Reynolds_Number' in builder.params
    
    def test_fresnel_defaults(self, test_params):
        """Test Fresnel-specific defaults are applied"""
        builder = FresnelModelBuilder(test_params)
        
        # Check Fresnel-specific parameters exist
        assert builder.params['Laser_Power'] == 1e6
        assert builder.params['Gas_Type'] == 'argon'
        assert builder.params['Time_End'] == 100e-9
    
    def test_kumar_defaults(self, test_params):
        """Test Kumar-specific defaults are applied"""
        builder = KumarModelBuilder(test_params)
        
        # Check Kumar-specific parameters exist
        assert builder.params['Volumetric_Heat_Generation'] == 1e12
        assert builder.params['Marangoni_Effect'] == True
        assert builder.params['Time_End'] == 50e-9


class TestModelBuilder:
    """Test main ModelBuilder orchestration"""
    
    @pytest.fixture
    def test_params(self):
        return {
            'Domain_Width': 100e-6,
            'Domain_Height': 100e-6,
            'Droplet_Radius': 25e-6,
            'Output_Directory': 'test_results'
        }
    
    @patch('src.mph_core.model_builder.mph')
    def test_model_builder_build_stages(self, mock_mph, test_params):
        """Test build stage tracking"""
        mock_client = Mock()
        mock_model = Mock()
        mock_client.create.return_value = mock_model
        mock_mph.start.return_value = mock_client
        
        builder = ModelBuilder(test_params, 'fresnel')
        
        # Initial state
        assert not builder.build_stages['client_connected']
        assert not builder.build_stages['model_created']
        
        # Test connection
        builder._connect_to_comsol()
        assert builder.build_stages['client_connected']
        
        # Test model creation
        builder._create_model()
        assert builder.build_stages['model_created']
    
    @patch('src.mph_core.model_builder.mph')
    def test_model_builder_context_manager(self, mock_mph, test_params):
        """Test ModelBuilder as context manager"""
        mock_client = Mock()
        mock_mph.start.return_value = mock_client
        
        with ModelBuilder(test_params, 'fresnel') as builder:
            assert builder is not None
            
        # Check cleanup was called
        mock_client.disconnect.assert_called_once()


class TestResultsProcessor:
    """Test results extraction functionality"""
    
    @pytest.fixture
    def mock_model_with_results(self):
        """Mock model with solved results"""
        model = Mock()
        
        # Mock results interface
        mock_results = Mock()
        model.results.return_value = mock_results
        
        # Mock dataset and plot creation
        mock_dataset = Mock()
        mock_plot = Mock()
        mock_results.create.side_effect = lambda type_name, **kwargs: {
            'Dataset': mock_dataset,
            'PlotGroup2D': mock_plot,
            'Export': Mock()
        }.get(type_name, Mock())
        
        return model
    
    @pytest.fixture
    def test_params(self):
        return {
            'Output_Directory': 'test_results',
            'Temperature_Min_Plot': 300,
            'Temperature_Max_Plot': 2000
        }
    
    def test_results_processor_initialization(self, mock_model_with_results, test_params):
        """Test ResultsProcessor initialization"""
        processor = ResultsProcessor(mock_model_with_results, test_params)
        
        assert processor.model == mock_model_with_results
        assert processor.params == test_params
        assert processor.output_dir == Path('test_results')
    
    def test_temperature_field_extraction(self, mock_model_with_results, test_params):
        """Test temperature field extraction"""
        processor = ResultsProcessor(mock_model_with_results, test_params)
        
        # Test PNG extraction
        output_file = processor.extract_temperature_field('png')
        
        assert output_file.suffix == '.png'
        assert 'temperature_field' in output_file.name
    
    def test_summary_statistics_extraction(self, mock_model_with_results, test_params, tmp_path):
        """Test summary statistics extraction"""
        test_params['Output_Directory'] = str(tmp_path)
        processor = ResultsProcessor(mock_model_with_results, test_params)
        
        # Mock model evaluation methods
        mock_model_with_results.evaluate.return_value = 1500.0  # Example temperature
        
        output_file = processor.extract_summary_statistics()
        
        assert output_file.exists()
        assert output_file.suffix == '.json'
        
        # Check JSON content
        with open(output_file) as f:
            stats = json.load(f)
            
        assert 'max_temperature' in stats
        assert 'simulation_info' in stats


class TestIntegration:
    """Integration tests combining multiple components"""
    
    @pytest.fixture
    def integration_params(self):
        """Complete parameter set for integration testing"""
        return {
            'Domain_Width': 100e-6,
            'Domain_Height': 100e-6,
            'Droplet_Radius': 25e-6,
            'Droplet_Center_X': 0.0,
            'Droplet_Center_Y': 0.0,
            'Tin_Density_Solid': 7310,
            'Tin_Thermal_Conductivity_Solid': 66.8,
            'Tin_Heat_Capacity_Solid': 228,
            'Tin_Melting_Temperature': 505.08,
            'Time_End': 1e-6,
            'Time_Step_Initial': 1e-9,
            'Output_Directory': 'test_results',
            'Gas_Type': 'argon'
        }
    
    @patch('src.mph_core.model_builder.mph')
    def test_complete_model_build_flow(self, mock_mph, integration_params):
        """Test complete model building flow without COMSOL"""
        mock_client = Mock()
        mock_model = Mock()
        
        # Setup mock chain
        mock_client.create.return_value = mock_model
        mock_mph.start.return_value = mock_client
        
        # Mock all model methods
        mock_model.parameter = Mock()
        mock_model.property = Mock()
        mock_model.coordinate = Mock()
        mock_model.save = Mock()
        
        # Mock component creators
        for component in ['geometry', 'selections', 'materials', 'physics', 'studies', 'meshes']:
            getattr(mock_model, component).return_value.create = Mock(return_value=Mock())
        
        builder = ModelBuilder(integration_params, 'fresnel')
        
        # Test build stages
        builder._connect_to_comsol()
        assert builder.build_stages['client_connected']
        
        builder._create_model()
        assert builder.build_stages['model_created']
        
        builder._set_parameters()
        assert builder.build_stages['parameters_set']
        
        # Mock geometry builder to pass validation
        with patch.object(builder, 'geometry_builder') as mock_geom:
            mock_geom.validate_geometry.return_value = True
            mock_geom.create_domain.return_value = None
            builder._build_geometry()
            assert builder.build_stages['geometry_built']


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests"""
    
    def test_large_parameter_set_handling(self):
        """Test handling of large parameter sets"""
        large_params = {f'param_{i}': i * 0.001 for i in range(1000)}
        large_params.update({
            'Domain_Width': 100e-6,
            'Domain_Height': 100e-6,
            'Droplet_Radius': 25e-6
        })
        
        # Should not raise memory errors
        builder = ModelBuilder(large_params, 'fresnel')
        assert len(builder.params) >= 1000
    
    def test_parameter_validation_performance(self):
        """Test parameter validation performance"""
        import time
        
        params = {f'param_{i}': f'value_{i}' for i in range(100)}
        params.update({
            'Domain_Width': 100e-6,
            'Droplet_Radius': 25e-6
        })
        
        start_time = time.time()
        builder = ModelBuilder(params, 'fresnel')
        end_time = time.time()
        
        # Should complete quickly
        assert (end_time - start_time) < 1.0  # Less than 1 second


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
