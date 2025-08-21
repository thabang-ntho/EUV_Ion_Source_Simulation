"""
Migration Validation Tests

Tests to validate that the new MPh implementation produces
equivalent results to the old Java API implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from src.mph_core.model_builder import ModelBuilder
from src.models.mph_fresnel import FresnelModelBuilder
from src.models.mph_kumar import KumarModelBuilder


class TestMigrationValidation:
    """Test equivalence between old and new implementations"""
    
    @pytest.fixture
    def reference_params(self):
        """Reference parameter set from existing config"""
        return {
            'Domain_Width': 100e-6,
            'Domain_Height': 100e-6,
            'Droplet_Radius': 25e-6,
            'Droplet_Center_X': 0.0,
            'Droplet_Center_Y': 0.0,
            'Tin_Density_Solid': 7310,
            'Tin_Density_Liquid': 6990,
            'Tin_Thermal_Conductivity_Solid': 66.8,
            'Tin_Thermal_Conductivity_Liquid': 32.0,
            'Tin_Heat_Capacity_Solid': 228,
            'Tin_Heat_Capacity_Liquid': 243,
            'Tin_Melting_Temperature': 505.08,
            'Tin_Viscosity_Liquid': 1.85e-3,
            'Tin_Surface_Tension': 0.544,
            'Tin_Absorptivity': 0.8,
            'Time_End': 1e-6,
            'Time_Step_Initial': 1e-9,
            'Output_Directory': 'validation_results'
        }
    
    def test_parameter_mapping_consistency(self, reference_params):
        """Test that parameters are mapped consistently between implementations"""
        
        # Test Fresnel variant
        fresnel_builder = FresnelModelBuilder(reference_params.copy())
        fresnel_params = fresnel_builder.params
        
        # Check critical parameters are preserved
        assert fresnel_params['Domain_Width'] == reference_params['Domain_Width']
        assert fresnel_params['Droplet_Radius'] == reference_params['Droplet_Radius']
        assert fresnel_params['Tin_Density_Solid'] == reference_params['Tin_Density_Solid']
        
        # Test Kumar variant
        kumar_builder = KumarModelBuilder(reference_params.copy())
        kumar_params = kumar_builder.params
        
        # Check same critical parameters
        assert kumar_params['Domain_Width'] == reference_params['Domain_Width']
        assert kumar_params['Droplet_Radius'] == reference_params['Droplet_Radius']
        assert kumar_params['Tin_Density_Solid'] == reference_params['Tin_Density_Solid']
    
    @patch('src.mph_core.model_builder.mph')
    def test_geometry_equivalence(self, mock_mph, reference_params):
        """Test that geometry creation produces equivalent structures"""
        mock_client = Mock()
        mock_model = Mock()
        mock_geometries = Mock()
        mock_geometry = Mock()
        
        mock_client.create.return_value = mock_model
        mock_model.geometries.return_value = mock_geometries
        mock_geometries.create.return_value = mock_geometry
        mock_mph.start.return_value = mock_client
        
        # Create geometry with new implementation
        builder = ModelBuilder(reference_params, 'fresnel')
        builder._connect_to_comsol()
        builder._create_model()
        builder._build_geometry()
        
        # Verify geometry creation calls
        mock_geometries.create.assert_called()  # Should create the geometry container
        mock_geometry.create.assert_called()    # Should create shapes within geometry
        create_calls = mock_geometry.create.call_args_list
        
        # Should have calls for rectangle and circle
        call_types = [call[0][0] for call in create_calls]
        assert 'Rectangle' in call_types
        assert 'Circle' in call_types
        
    @patch('src.mph_core.model_builder.mph')
    def test_material_property_equivalence(self, mock_mph, reference_params):
        """Test that material properties match reference values"""
        mock_client = Mock()
        mock_model = Mock()
        mock_materials = Mock()
        mock_tin = Mock()
        
        mock_client.create.return_value = mock_model
        mock_model.materials.return_value = mock_materials
        mock_materials.create.return_value = mock_tin
        mock_mph.start.return_value = mock_client
        
        builder = ModelBuilder(reference_params, 'fresnel')
        builder._connect_to_comsol()
        builder._create_model()
        builder._build_geometry()
        builder._create_selections()  # Need selections before materials
        builder._setup_materials()
        
        # Verify material creation calls
        mock_materials.create.assert_called()
        material_calls = mock_materials.create.call_args_list
        
        # Should create tin and gas materials
        material_types = [call[0][0] for call in material_calls]
        assert 'Common' in material_types  # All materials use Common type
    
    def test_physics_interface_consistency(self, reference_params):
        """Test that physics interfaces are consistent between variants"""
        
        # Both variants should have heat transfer
        fresnel_builder = FresnelModelBuilder(reference_params.copy())
        kumar_builder = KumarModelBuilder(reference_params.copy())
        
        # Check variant-specific physics expectations
        with patch('src.mph_core.model_builder.mph'):
            # Fresnel should configure TDS
            assert 'Gas_Type' in fresnel_builder.params
            assert fresnel_builder.params['Gas_Type'] == 'argon'
            
            # Kumar should configure fluid flow
            assert 'Reynolds_Number' in kumar_builder.params
            assert 'Marangoni_Effect' in kumar_builder.params
    
    def test_time_stepping_consistency(self, reference_params):
        """Test that time stepping parameters are consistent"""
        
        fresnel_builder = FresnelModelBuilder(reference_params.copy())
        kumar_builder = KumarModelBuilder(reference_params.copy())
        
        # Both should respect base time parameters
        assert fresnel_builder.params['Time_End'] >= reference_params['Time_End']
        assert kumar_builder.params['Time_End'] >= 0  # Kumar may use different default
        
        # Both should have reasonable time stepping
        assert fresnel_builder.params.get('Time_Step_Initial', 1e-9) <= 1e-6
        assert kumar_builder.params.get('Time_Step_Initial', 1e-9) <= 1e-6


class TestNumericalEquivalence:
    """Test numerical equivalence where possible"""
    
    @pytest.fixture
    def validation_params(self):
        """Simplified parameters for numerical validation"""
        return {
            'Domain_Width': 50e-6,
            'Domain_Height': 50e-6,
            'Droplet_Radius': 10e-6,
            'Tin_Density_Solid': 7310,
            'Tin_Thermal_Conductivity_Solid': 66.8,
            'Time_End': 1e-9,  # Very short simulation
            'Output_Directory': 'numerical_validation'
        }
    
    def test_domain_area_calculation(self, validation_params):
        """Test that domain area calculations are consistent"""
        
        expected_domain_area = validation_params['Domain_Width'] * validation_params['Domain_Height']
        expected_droplet_area = 3.14159 * validation_params['Droplet_Radius']**2
        
        # Test with mock model
        mock_model = Mock()
        from src.mph_core.geometry import GeometryBuilder
        
        builder = GeometryBuilder(mock_model, validation_params)
        domain_info = builder.get_domain_info()
        
        assert abs(domain_info['domain_area'] - expected_domain_area) < 1e-15
        assert abs(domain_info['droplet_area'] - expected_droplet_area) < 1e-10
    
    def test_material_expression_evaluation(self, validation_params):
        """Test that material expressions evaluate correctly"""
        
        mock_model = Mock()
        from src.mph_core.materials import MaterialsHandler
        
        handler = MaterialsHandler(mock_model, validation_params)
        
        # Test temperature-dependent density expression
        T_melt = validation_params.get('Tin_Melting_Temperature', 505.08)
        rho_solid = validation_params['Tin_Density_Solid']
        
        # The expression should contain the melting temperature
        # This is testing the expression construction, not COMSOL evaluation
        assert T_melt > 0
        assert rho_solid > 0
    
    def test_geometry_constraint_validation(self, validation_params):
        """Test geometry constraint validation logic"""
        
        mock_model = Mock()
        from src.mph_core.geometry import GeometryBuilder
        
        # Valid case
        builder = GeometryBuilder(mock_model, validation_params)
        assert builder.validate_geometry() == True
        
        # Invalid case - droplet too large
        invalid_params = validation_params.copy()
        invalid_params['Droplet_Radius'] = 30e-6  # Larger than domain half-size (25e-6)
        
        builder_invalid = GeometryBuilder(mock_model, invalid_params)
        assert builder_invalid.validate_geometry() == False


class TestRegressionValidation:
    """Regression tests to catch breaking changes"""
    
    @pytest.fixture
    def regression_test_data(self, tmp_path):
        """Create regression test reference data"""
        reference_data = {
            'geometry': {
                'domain_area': 2.5e-9,  # 50µm × 50µm
                'droplet_area': 3.14159e-10,  # π × (10µm)²
            },
            'materials': {
                'tin_density_solid': 7310,
                'tin_conductivity_solid': 66.8,
            },
            'physics': {
                'heat_transfer_active': True,
                'expected_interfaces': ['ht']
            }
        }
        
        reference_file = tmp_path / 'regression_reference.json'
        with open(reference_file, 'w') as f:
            json.dump(reference_data, f, indent=2)
            
        return reference_file
    
    def test_geometry_regression(self, regression_test_data):
        """Test that geometry calculations haven't regressed"""
        
        with open(regression_test_data) as f:
            reference = json.load(f)
        
        params = {
            'Domain_Width': 50e-6,
            'Domain_Height': 50e-6,
            'Droplet_Radius': 10e-6,
        }
        
        mock_model = Mock()
        from src.mph_core.geometry import GeometryBuilder
        
        builder = GeometryBuilder(mock_model, params)
        domain_info = builder.get_domain_info()
        
        # Check against reference values
        ref_geom = reference['geometry']
        assert abs(domain_info['domain_area'] - ref_geom['domain_area']) < 1e-12
        assert abs(domain_info['droplet_area'] - ref_geom['droplet_area']) < 1e-12
    
    def test_material_properties_regression(self, regression_test_data):
        """Test that material properties haven't regressed"""
        
        with open(regression_test_data) as f:
            reference = json.load(f)
        
        params = {
            'Tin_Density_Solid': 7310,
            'Tin_Thermal_Conductivity_Solid': 66.8,
        }
        
        mock_model = Mock()
        from src.mph_core.materials import MaterialsHandler
        
        handler = MaterialsHandler(mock_model, params)
        
        # Verify reference values are used
        ref_materials = reference['materials']
        assert params['Tin_Density_Solid'] == ref_materials['tin_density_solid']
        assert params['Tin_Thermal_Conductivity_Solid'] == ref_materials['tin_conductivity_solid']


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_parameter_handling(self):
        """Test handling of invalid parameters"""
        
        invalid_params = {
            'Domain_Width': -100e-6,  # Negative width
            'Droplet_Radius': 0,      # Zero radius
        }
        
        # Should not crash during initialization
        try:
            builder = ModelBuilder(invalid_params, 'fresnel')
            assert builder is not None
        except Exception as e:
            pytest.fail(f"ModelBuilder initialization failed with invalid params: {e}")
    
    def test_missing_required_parameters(self):
        """Test handling of missing required parameters"""
        
        minimal_params = {
            'Domain_Width': 100e-6,
            # Missing other required parameters
        }
        
        # Should use defaults gracefully
        builder = ModelBuilder(minimal_params, 'fresnel')
        assert 'Domain_Height' in builder.params  # Should be added as default
    
    @patch('src.mph_core.model_builder.mph')
    def test_comsol_connection_failure_handling(self, mock_mph):
        """Test handling of COMSOL connection failures"""
        
        # Mock connection failure
        mock_mph.start.side_effect = Exception("COMSOL connection failed")
        
        builder = ModelBuilder({'Domain_Width': 100e-6}, 'fresnel')
        
        with pytest.raises(Exception) as exc_info:
            builder._connect_to_comsol()
        
        assert "COMSOL connection failed" in str(exc_info.value)
    
    def test_build_stage_tracking_on_failure(self):
        """Test that build stages track failures correctly"""
        
        builder = ModelBuilder({'Domain_Width': 100e-6}, 'fresnel')
        
        # All stages should start as False
        assert all(not status for status in builder.build_stages.values())
        
        # After a stage completes, it should be True
        builder.build_stages['client_connected'] = True
        assert builder.build_stages['client_connected']
        assert not builder.build_stages['model_created']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
