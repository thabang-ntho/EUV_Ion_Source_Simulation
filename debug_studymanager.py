#!/usr/bin/env python3
"""
Debug StudyManager vs Direct Creation
Compare direct creation with StudyManager creation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mph
from mph_core.studies import StudyManager

def compare_creation_methods():
    """Compare direct creation vs StudyManager creation"""
    print("🔍 Comparing Creation Methods...")
    
    try:
        # Connect to COMSOL
        print("\n📡 Connecting to COMSOL...")
        client = mph.start()
        model = client.create('compare_creation')
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
        
        # Create minimal physics (needed for study)
        print("\n⚡ Creating minimal physics...")
        physics = model/'physics'
        
        # Create a simple heat transfer physics interface
        # The second parameter is the geometry tag - make sure it matches the geometry we created
        ht = physics.create('HeatTransfer', 'geometry', name='ht')
        
        # In MPh, physics are automatically applied to all domains
        # We don't need to explicitly select domains for this simple test
        print("✓ Minimal physics created")
        
        # Method 1: Direct creation
        print("\n🔬 Method 1: Direct Creation")
        
        # Direct mesh
        meshes = model/'meshes'
        direct_mesh = meshes.create(geometry, name='direct_mesh')
        print(f"Direct mesh: {direct_mesh} (tag: {direct_mesh.tag()})")
        
        # Direct study
        studies = model/'studies'
        direct_study = studies.create(name='direct_study')
        direct_step = direct_study.create('Stationary', name='step')
        print(f"Direct study: {direct_study} (tag: {direct_study.tag()})")
        
        # Direct solution
        solutions = model/'solutions'
        direct_solution = solutions.create(name='direct_solution')
        print(f"Direct solution: {direct_solution} (tag: {direct_solution.tag()})")
        
        # Check containers after direct creation
        print("\nContainers after direct creation:")
        mesh_tags = [m.tag() for m in meshes]
        study_tags = [s.tag() for s in studies]  
        solution_tags = [s.tag() for s in solutions]
        print(f"  Meshes: {mesh_tags}")
        print(f"  Studies: {study_tags}")
        print(f"  Solutions: {solution_tags}")
        
        # Method 2: StudyManager creation
        print("\n🏗️ Method 2: StudyManager Creation")
        
        # Create StudyManager with minimal physics
        physics_interfaces = {'ht': ht}
        params = {'Simulation_Time': 1e-6}
        
        study_mgr = StudyManager(model, physics_interfaces, params)
        
        # Use StudyManager methods
        mgr_mesh = study_mgr._create_mesh()
        print(f"StudyManager mesh: {mgr_mesh} (tag: {mgr_mesh.tag() if hasattr(mgr_mesh, 'tag') else 'No tag method'})")
        
        mgr_study = study_mgr._create_transient_study()
        print(f"StudyManager study: {mgr_study} (tag: {mgr_study.tag() if hasattr(mgr_study, 'tag') else 'No tag method'})")
        
        mgr_solution = study_mgr._create_solution(mgr_study)
        print(f"StudyManager solution: {mgr_solution} (tag: {mgr_solution.tag() if hasattr(mgr_solution, 'tag') else 'No tag method'})")
        
        # Check containers after StudyManager creation
        print("\nContainers after StudyManager creation:")
        mesh_tags = [m.tag() for m in meshes]
        study_tags = [s.tag() for s in studies]  
        solution_tags = [s.tag() for s in solutions]
        print(f"  Meshes: {mesh_tags}")
        print(f"  Studies: {study_tags}")
        print(f"  Solutions: {solution_tags}")
        
        print("\n✅ Comparison completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")
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
    success = compare_creation_methods()
    sys.exit(0 if success else 1)
