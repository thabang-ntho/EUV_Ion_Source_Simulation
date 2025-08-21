#!/usr/bin/env python3
"""
Debug StudyManager - Minimal Test
Test StudyManager without physics dependencies
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mph
from mph_core.studies import StudyManager

def test_studymanager_minimal():
    """Test StudyManager with minimal setup"""
    print("🔍 Testing StudyManager (Minimal)...")
    
    try:
        # Connect to COMSOL
        print("\n📡 Connecting to COMSOL...")
        client = mph.start()
        model = client.create('studymanager_minimal')
        print("✓ Connected to COMSOL")
        
        # Create minimal geometry (needed for mesh)
        print("\n📐 Creating minimal geometry...")
        geometries = model/'geometries'
        geometry = geometries.create(2, name='geometry')
        rect = geometry.create('Rectangle', name='domain')
        rect.property('size', ['100[um]', '100[um]'])
        rect.property('pos', ['0', '0'])
        model.build(geometry)
        print("✓ Minimal geometry created")
        
        # Create StudyManager with empty physics (to test creation logic)
        print("\n🏗️ Creating StudyManager...")
        physics_interfaces = {}  # Empty physics to avoid physics errors
        params = {'Simulation_Time': 1e-6}
        
        study_mgr = StudyManager(model, physics_interfaces, params)
        print("✓ StudyManager created")
        
        # Test mesh creation
        print("\n🕸️ Testing StudyManager mesh creation...")
        try:
            mgr_mesh = study_mgr._create_mesh()
            print(f"✓ StudyManager mesh: {mgr_mesh}")
            print(f"Mesh tag: {mgr_mesh.tag() if hasattr(mgr_mesh, 'tag') else 'No tag method'}")
            
            # Check if mesh appears in container
            meshes = model/'meshes'
            mesh_count = sum(1 for _ in meshes)
            mesh_tags = [m.tag() for m in meshes]
            print(f"Meshes in container: {mesh_count} - {mesh_tags}")
            
        except Exception as mesh_error:
            print(f"❌ StudyManager mesh creation failed: {mesh_error}")
        
        # Test study creation (without physics activation)
        print("\n📊 Testing StudyManager study creation...")
        try:
            mgr_study = study_mgr._create_transient_study()
            print(f"✓ StudyManager study: {mgr_study}")
            print(f"Study tag: {mgr_study.tag() if hasattr(mgr_study, 'tag') else 'No tag method'}")
            
            # Check if study appears in container
            studies = model/'studies'
            study_count = sum(1 for _ in studies)
            study_tags = [s.tag() for s in studies]
            print(f"Studies in container: {study_count} - {study_tags}")
            
        except Exception as study_error:
            print(f"❌ StudyManager study creation failed: {study_error}")
        
        # Test solution creation
        print("\n💡 Testing StudyManager solution creation...")
        try:
            if 'mgr_study' in locals():
                mgr_solution = study_mgr._create_solution(mgr_study)
                print(f"✓ StudyManager solution: {mgr_solution}")
                print(f"Solution tag: {mgr_solution.tag() if hasattr(mgr_solution, 'tag') else 'No tag method'}")
                
                # Check if solution appears in container
                solutions = model/'solutions'
                solution_count = sum(1 for _ in solutions)
                solution_tags = [s.tag() for s in solutions]
                print(f"Solutions in container: {solution_count} - {solution_tags}")
            else:
                print("⚠️ Skipping solution test - study creation failed")
                
        except Exception as solution_error:
            print(f"❌ StudyManager solution creation failed: {solution_error}")
        
        print("\n✅ StudyManager minimal test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ StudyManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            client.disconnect()
            print("\n📡 Disconnected from COMSOL")
        except:
            pass

if __name__ == '__main__':
    success = test_studymanager_minimal()
    sys.exit(0 if success else 1)
