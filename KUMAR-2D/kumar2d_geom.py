#!/usr/bin/env python3
"""
Kumar 2D Geometry Only - MPh Translation
Creates just the geometry (rectangle + circle) and saves as kumar2d_geom.mph
Based on mph_example.py patterns and Kumar_2D_demo_v5.java geometry section.
"""

import sys
from pathlib import Path

def load_parameters(param_file='parameters.txt'):
    """Load parameters from parameters.txt file"""
    params = {}
    param_path = Path(__file__).parent / param_file
    
    if not param_path.exists():
        raise FileNotFoundError(f"Parameters file not found: {param_path}")
    
    with open(param_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('%') and not line.startswith('#'):
                try:
                    # Split on first whitespace, then take first two parts
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0]
                        value = parts[1]
                        params[key] = value
                except (ValueError, IndexError):
                    continue
    
    return params

def build_geometry_only(params, out_path='kumar2d_geom.mph'):
    """Build only the geometry and save the model"""
    
    # Import mph here to allow --dry-run without mph
    import mph
    
    # Connect to COMSOL (following mph_example.py pattern)
    try:
        client = mph.start()
    except Exception as e:
        print(f"Failed to start MPh client: {e}")
        # Try again without special session options
        client = mph.start()

    try:
        model = client.create('Kumar_2D_Geom')

        # Parameters (minimal set needed for geometry)
        model.parameter('W_dom', params.get('W_dom', '100[um]'))
        model.parameter('H_dom', params.get('H_dom', '100[um]'))  
        model.parameter('R_drop', params.get('R_drop', '25[um]'))

        # Containers
        components = model/'components'
        components.create(True, name='comp1')
        geometries = model/'geometries'
        geometry = geometries.create(2, name='geom1')

        # Geometry: rectangle (vacuum domain) + circle (droplet)
        # Set length unit to micrometers (crucial for proper scaling)
        geometry.java.lengthUnit("µm")
        
        # Rectangle for vacuum domain
        rect = geometry.create('Rectangle', name='r1')
        rect.property('size', [params['W_dom'], params['H_dom']])
        
        # Circle for droplet at center
        circle = geometry.create('Circle', name='c1') 
        circle.property('pos', [f"{params['W_dom']}/2", f"{params['H_dom']}/2"])
        circle.property('r', params['R_drop'])
        
        # Build geometry (following mph_example.py)
        model.build(geometry)

        # Save model
        model.save(str(out_path))
        print(f"Geometry-only model saved as: {out_path}")

    finally:
        client.disconnect()

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Kumar 2D Geometry Builder')
    parser.add_argument('--dry-run', action='store_true', help='Print parameters without running COMSOL')
    parser.add_argument('--output', '-o', default='kumar2d_geom.mph', help='Output file name')
    
    args = parser.parse_args()
    
    # Load parameters
    try:
        params = load_parameters()
        print(f"Loaded {len(params)} parameters")
        
        if args.dry_run:
            print("DRY RUN - Parameters:")
            for k, v in params.items():
                print(f"  {k} = {v}")
            print("Would create geometry with:")
            print(f"  Domain: {params.get('W_dom', '?')} x {params.get('H_dom', '?')}")
            print(f"  Droplet radius: {params.get('R_drop', '?')}")
            return 0
        
        # Build geometry
        out_path = Path(args.output)
        build_geometry_only(params, out_path)
        print("Done")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
