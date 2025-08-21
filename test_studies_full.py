#!/usr/bin/env python3
"""
Test Studies Module
Complete test of the studies module functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mph
from mph_core.materials import MaterialsHandler
from mph_core.geometry import GeometryBuilder  
from mph_core.selections import SelectionManager
from mph_core.physics import PhysicsManager
from mph_core.studies import StudyManager

def test_studies_module():
    """Test the complete studies module workflow"""
    print("Testing Studies Module...")
    
    try:
        # Connect to COMSOL
        print("Connecting to COMSOL...")
        client = mph.start()
        model = client.create('test_studies')
        print("✓ Connected to COMSOL")
        
        # Load parameters
        import yaml
        with open('data/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Add minimal physics config for testing
        config['physics'] = {
            'heat_transfer': {
                'enabled': True,
                'T_init': 300.0,
                'boundary_conditions': {}
            }
        }
        
        # Create managers
        print("\nCreating managers...")
        geom_mgr = GeometryBuilder(model, config['geometry'])
        geom_mgr.create_geometry(model)
        
        sel_mgr = SelectionManager(model, geom_mgr.geometry, config['geometry'])  # Pass geometry params
        sel_mgr.create_all_selections()
        
        mat_mgr = MaterialsHandler(model, config['materials'])
        mat_mgr.create_all_materials()
        
        phys_mgr = PhysicsManager(model, sel_mgr.selections, mat_mgr.materials)
        phys_mgr.setup_all_physics()
        
        studies_mgr = StudyManager(
            model,
            phys_mgr.physics_interfaces,
            config.get('studies', {})
        )
        print("✓ All managers created")
        
        # Test mesh creation
        print("\nTesting mesh creation...")
        mesh = studies_mgr._create_mesh()
        print(f"✓ Mesh created: {mesh}")
        
        # Test study creation
        print("\nTesting study creation...")
        study = studies_mgr._create_transient_study()
        print(f"✓ Study created: {study}")
        
        # Test solution creation
        print("\nTesting solution creation...")
        solution = studies_mgr._create_solution(study)
        print(f"✓ Solution created: {solution}")
        
        # Test complete workflow
        print("\nTesting complete workflow...")
        result = studies_mgr.create_study_and_solve()
        print(f"✓ Complete workflow result: {result}")
        
        # Validate components
        print("\nValidating components...")
        print(f"Mesh: {result['mesh'].tag()}")
        print(f"Study: {result['study'].tag()}")
        print(f"Solution: {result['solution'].tag()}")
        
        # Test mesh info
        meshes = model/'meshes'
        if meshes:
            mesh_names = [m.tag() for m in meshes]
            print(f"Available meshes: {mesh_names}")
        
        # Test study info  
        studies = model/'studies'
        if studies:
            study_names = [s.tag() for s in studies]
            print(f"Available studies: {study_names}")
            
        # Test solution info
        solutions = model/'solutions'
        if solutions:
            solution_names = [s.tag() for s in solutions]
            print(f"Available solutions: {solution_names}")
        
        print("\n✓ Studies module test completed successfully!")
        
    except Exception as e:
        print(f"✗ Studies module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            client.disconnect()
            print("Disconnected from COMSOL")
        except:
            pass
    
    return True

if __name__ == '__main__':
    success = test_studies_module()
    sys.exit(0 if success else 1)
