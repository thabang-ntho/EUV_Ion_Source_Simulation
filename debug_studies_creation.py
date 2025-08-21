#!/usr/bin/env python3
"""
Debug Studies Creation
Minimal test focusing on studies creation only
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mph

def debug_studies_creation():
    """Debug studies creation step by step"""
    print("🔍 Debugging Studies Creation...")
    
    try:
        # Connect to COMSOL
        print("\n📡 Connecting to COMSOL...")
        client = mph.start()
        model = client.create('debug_studies')
        print("✓ Connected to COMSOL")
        
        # Create minimal geometry
        print("\n📐 Creating minimal geometry...")
        geometries = model/'geometries'
        geometry = geometries.create(2, name='geometry')
        
        # Create a simple rectangle
        rect = geometry.create('Rectangle', name='domain')
        rect.property('size', ['100[um]', '100[um]'])
        rect.property('pos', ['0', '0'])
        
        # Build geometry
        model.build(geometry)
        print("✓ Minimal geometry created and built")
        
        # Test mesh creation directly
        print("\n🕸️ Testing mesh creation...")
        meshes = model/'meshes'
        print(f"Meshes container: {meshes}")
        
        try:
            mesh = meshes.create(geometry, name='mesh')
            print(f"✓ Mesh created: {mesh}")
            print(f"Mesh tag: {mesh.tag()}")
        except Exception as mesh_error:
            print(f"❌ Mesh creation failed: {mesh_error}")
        
        # Check meshes container after creation
        mesh_count = 0
        mesh_tags = []
        try:
            for m in meshes:
                mesh_count += 1
                mesh_tags.append(m.tag())
        except:
            pass
        print(f"Meshes in container: {mesh_count} - {mesh_tags}")
        
        # Test study creation directly
        print("\n📊 Testing study creation...")
        studies = model/'studies'
        print(f"Studies container: {studies}")
        
        try:
            study = studies.create(name='test_study')
            print(f"✓ Study created: {study}")
            print(f"Study tag: {study.tag()}")
            
            # Try to create a study step
            step = study.create('Stationary', name='stationary_step')
            print(f"✓ Study step created: {step}")
            
        except Exception as study_error:
            print(f"❌ Study creation failed: {study_error}")
        
        # Check studies container after creation
        study_count = 0
        study_tags = []
        try:
            for s in studies:
                study_count += 1
                study_tags.append(s.tag())
        except:
            pass
        print(f"Studies in container: {study_count} - {study_tags}")
        
        # Test solution creation directly
        print("\n💡 Testing solution creation...")
        solutions = model/'solutions'
        print(f"Solutions container: {solutions}")
        
        try:
            solution = solutions.create(name='test_solution')
            print(f"✓ Solution created: {solution}")
            print(f"Solution tag: {solution.tag()}")
        except Exception as solution_error:
            print(f"❌ Solution creation failed: {solution_error}")
        
        # Check solutions container after creation
        solution_count = 0
        solution_tags = []
        try:
            for s in solutions:
                solution_count += 1
                solution_tags.append(s.tag())
        except:
            pass
        print(f"Solutions in container: {solution_count} - {solution_tags}")
        
        print("\n✅ Debug studies creation completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
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
    success = debug_studies_creation()
    sys.exit(0 if success else 1)
