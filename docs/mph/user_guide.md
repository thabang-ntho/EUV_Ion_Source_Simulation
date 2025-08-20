# MPh API User Guide

## Quick Start

### Installation Requirements
- Python 3.10+
- COMSOL Multiphysics 6.2+
- MPh Python package
- EUV simulation dependencies (see `pyproject.toml`)

### Basic Usage

1. **Simple Model Building**:
```bash
python -m src.mph_cli fresnel --config data/global_parameters_pp_v2.txt --solve
```

2. **Custom Parameters**:
```bash
python -m src.mph_cli fresnel \
    --laser-power 2e6 \
    --laser-spot-radius 15e-6 \
    --gas-type argon \
    --solve --extract-results
```

3. **Programmatic Usage**:
```python
from src.models import build_fresnel_model

params = {
    'Domain_Width': 100e-6,
    'Droplet_Radius': 25e-6,
    'Laser_Power': 1e6
}

model_file = build_fresnel_model(params)
print(f"Model saved: {model_file}")
```

## Command Line Interface

### Basic Commands

#### Build Fresnel Model
```bash
python -m src.mph_cli fresnel [options]
```

#### Build Kumar Model  
```bash
python -m src.mph_cli kumar [options]
```

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `-c, --config` | Configuration file | `--config data/params.txt` |
| `-o, --output` | Output .mph file | `--output my_model.mph` |
| `--output-dir` | Output directory | `--output-dir results` |
| `--solve` | Solve after building | `--solve` |
| `--extract-results` | Extract results | `--extract-results` |
| `-v, --verbose` | Increase verbosity | `-vv` |
| `--dry-run` | Show actions without executing | `--dry-run` |

### Parameter Overrides

Override any parameter from command line:
```bash
python -m src.mph_cli fresnel \
    --param Domain_Width=200e-6 \
    --param Droplet_Radius=30e-6 \
    --param Time_End=50e-9
```

### Utility Commands

#### Validate Configuration
```bash
python -m src.mph_cli --validate-config data/global_parameters_pp_v2.txt
```

#### List Default Parameters
```bash
python -m src.mph_cli fresnel --list-defaults
```

#### List All Parameters
```bash
python -m src.mph_cli fresnel --config data/params.txt --list-params
```

## Configuration Files

### Parameter File Format
```
# Comments start with #
Domain_Width = 100e-6
Domain_Height = 100e-6
Droplet_Radius = 25e-6

# Temperature-dependent properties
Tin_Density_Solid = 7310
Tin_Density_Liquid = 6990
Tin_Melting_Temperature = 505.08

# Simulation settings
Time_End = 1e-6
Time_Step_Initial = 1e-9
```

### Parameter Categories

#### Geometry Parameters
- `Domain_Width`: Simulation domain width (m)
- `Domain_Height`: Simulation domain height (m)  
- `Droplet_Radius`: Initial droplet radius (m)
- `Droplet_Center_X`: Droplet center X coordinate (m)
- `Droplet_Center_Y`: Droplet center Y coordinate (m)

#### Material Properties
- `Tin_Density_Solid`: Solid tin density (kg/m³)
- `Tin_Density_Liquid`: Liquid tin density (kg/m³)
- `Tin_Thermal_Conductivity_Solid`: Solid thermal conductivity (W/(m·K))
- `Tin_Thermal_Conductivity_Liquid`: Liquid thermal conductivity (W/(m·K))
- `Tin_Heat_Capacity_Solid`: Solid heat capacity (J/(kg·K))
- `Tin_Heat_Capacity_Liquid`: Liquid heat capacity (J/(kg·K))
- `Tin_Melting_Temperature`: Melting temperature (K)
- `Tin_Viscosity_Liquid`: Liquid viscosity (Pa·s)
- `Tin_Surface_Tension`: Surface tension (N/m)

#### Fresnel-Specific Parameters
- `Laser_Power`: Laser intensity (W/m²)
- `Laser_Spot_Radius`: Laser spot radius (m)
- `Laser_Pulse_Duration`: Pulse duration (s)
- `Evaporation_Coefficient`: Evaporation coefficient (0-1)
- `Gas_Type`: Background gas ('argon', 'nitrogen', 'helium')
- `Tin_Diffusivity_Gas`: Tin diffusion in gas (m²/s)

#### Kumar-Specific Parameters
- `Volumetric_Heat_Generation`: Heat generation rate (W/m³)
- `Reynolds_Number`: Characteristic Reynolds number
- `Weber_Number`: Characteristic Weber number
- `Marangoni_Effect`: Enable Marangoni convection (true/false)
- `Surface_Tension_Temperature_Coeff`: dσ/dT (N/(m·K))

#### Simulation Control
- `Time_End`: Simulation end time (s)
- `Time_Step_Initial`: Initial time step (s)
- `Time_Step_Max`: Maximum time step (s)
- `Output_Time_Points`: Number of output time points
- `Relative_Tolerance`: Solver relative tolerance
- `Absolute_Tolerance`: Solver absolute tolerance

## Programmatic API

### Basic Model Building

```python
from src.models import FresnelModelBuilder, KumarModelBuilder

# Load configuration
from src.core.config.loader import load_config
params = load_config('data/global_parameters_pp_v2.txt')

# Build Fresnel model
with FresnelModelBuilder(params) as builder:
    model_file = builder.build_complete_model()
    results = builder.solve_and_extract_results()

# Build Kumar model  
with KumarModelBuilder(params) as builder:
    model_file = builder.build_complete_model()
    info = builder.get_kumar_info()
    print(f"Reynolds number: {info['kumar_specific']['reynolds_number']}")
```

### Advanced Usage

#### Custom Parameter Setup
```python
from src.models import FresnelModelBuilder

# Start with defaults
builder = FresnelModelBuilder({})

# Customize parameters
builder.params.update({
    'Domain_Width': 150e-6,
    'Droplet_Radius': 30e-6,
    'Laser_Power': 2e6,
    'Gas_Type': 'nitrogen'
})

# Build and solve
with builder:
    model_file = builder.build_complete_model()
    if builder.solve_and_extract_results():
        print("Simulation completed successfully")
```

#### Component-Level Access
```python
from src.mph_core import GeometryBuilder, MaterialsHandler

# Direct component usage (for advanced users)
with FresnelModelBuilder(params) as builder:
    builder._connect_to_comsol()
    builder._create_model()
    
    # Access individual components
    geom_builder = GeometryBuilder(builder.model, params)
    domain_info = geom_builder.get_domain_info()
    
    materials = MaterialsHandler(builder.model, params)
    material_info = materials.get_material_info()
```

#### Error Handling
```python
from src.core.errors import ModelBuildError, ConfigurationError

try:
    with FresnelModelBuilder(params) as builder:
        model_file = builder.build_complete_model()
        
except ConfigurationError as e:
    print(f"Configuration issue: {e}")
except ModelBuildError as e:
    print(f"Model building failed: {e}")
    
    # Check build status
    status = builder.get_build_status()
    failed_stage = next(stage for stage, done in status.items() if not done)
    print(f"Failed at stage: {failed_stage}")
```

## Result Analysis

### Generated Files

After successful simulation, the following files are generated:

#### Model Files
- `{variant}_model.mph`: COMSOL model file
- `summary_statistics.json`: Summary statistics

#### Visualization  
- `temperature_field.png`: Temperature contour plot
- `temperature_field.vtk`: VTK file for ParaView
- `velocity_field.png`: Velocity field (Kumar only)
- `concentration_field.png`: Species concentration (Fresnel only)

#### Data Files
- `temperature_time_series.csv`: Temperature vs time at probe points
- `temperature_field.csv`: Temperature field on regular grid
- `evaporation_rate.csv`: Evaporation rate vs time (Fresnel only)

### Result Processing

```python
from src.mph_core.postprocess import ResultsProcessor

# Load solved model
with FresnelModelBuilder(params) as builder:
    # ... build and solve ...
    
    # Custom result extraction
    processor = ResultsProcessor(builder.model, params)
    
    # Extract specific results
    temp_png = processor.extract_temperature_field('png')
    temp_csv = processor.extract_temperature_field('csv')
    time_series = processor.extract_temperature_time_series()
    stats = processor.extract_summary_statistics()
```

### Data Analysis Example

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load time series data
df = pd.read_csv('results/temperature_time_series.csv')

# Plot temperature evolution
plt.figure(figsize=(10, 6))
for col in df.columns[1:]:  # Skip time column
    plt.plot(df['Time[s]'], df[col], label=col)

plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.legend()
plt.title('Temperature Evolution at Probe Points')
plt.show()

# Load summary statistics
import json
with open('results/summary_statistics.json') as f:
    stats = json.load(f)

print(f"Maximum temperature: {stats['max_temperature']:.1f} K")
print(f"Simulation time: {stats['final_time']:.2e} s")
```

## Troubleshooting

### Common Issues

#### COMSOL Connection Issues
```
Error: Failed to connect to COMSOL
```
**Solution**: 
1. Ensure COMSOL is installed and licensed
2. Check that MPh package can find COMSOL installation
3. Try starting COMSOL manually first

#### Parameter Validation Errors
```
ConfigurationError: Invalid geometry parameters
```
**Solution**:
1. Check that droplet fits within domain
2. Ensure all required parameters are positive
3. Use `--validate-only` to check parameters

#### Memory Issues
```
OutOfMemoryError during mesh generation
```
**Solution**:
1. Reduce mesh density parameters
2. Decrease domain size
3. Increase COMSOL memory allocation

#### Convergence Issues
```
Study 'transient' failed: Solver did not converge
```
**Solution**:
1. Reduce time step size
2. Increase solver tolerances  
3. Check initial conditions
4. Use steady-state study for initialization

### Debug Mode

Enable debug logging for detailed troubleshooting:
```bash
python -m src.mph_cli fresnel -vvv --log-file debug.log --config params.txt
```

### Validation Workflow

Before running expensive simulations:
```bash
# 1. Validate configuration
python -m src.mph_cli --validate-config data/params.txt

# 2. Check parameters
python -m src.mph_cli fresnel --config data/params.txt --list-params

# 3. Dry run
python -m src.mph_cli fresnel --config data/params.txt --dry-run

# 4. Validation only (no COMSOL)
python -m src.mph_cli fresnel --config data/params.txt --validate-only

# 5. Build only (no solving)
python -m src.mph_cli fresnel --config data/params.txt --build-only
```

## Performance Tips

### Optimization Guidelines
1. **Start Small**: Begin with coarse mesh and short simulation time
2. **Parameter Studies**: Use parameter overrides for quick variations
3. **Incremental Building**: Use build stages to restart from failures
4. **Result Monitoring**: Extract results periodically during long runs

### Recommended Workflow
```bash
# 1. Quick validation run
python -m src.mph_cli fresnel --param Time_End=1e-9 --param Global_Mesh_Size=coarse

# 2. Medium resolution test  
python -m src.mph_cli fresnel --param Time_End=10e-9 --param Global_Mesh_Size=fine

# 3. Production run
python -m src.mph_cli fresnel --solve --extract-results
```

## Advanced Topics

### Custom Variants

Create custom variants by extending base builders:
```python
from src.models.mph_fresnel import FresnelModelBuilder

class CustomFresnelBuilder(FresnelModelBuilder):
    def _setup_custom_physics(self):
        # Add custom physics interfaces
        pass
    
    def _setup_physics(self):
        super()._setup_physics()
        self._setup_custom_physics()
```

### Batch Processing
```python
import itertools
from src.models import build_fresnel_model

# Parameter sweep
powers = [5e5, 1e6, 2e6]
radii = [20e-6, 25e-6, 30e-6]

for power, radius in itertools.product(powers, radii):
    params = base_params.copy()
    params.update({
        'Laser_Power': power,
        'Droplet_Radius': radius,
        'Output_Directory': f'results_P{power:.0e}_R{radius:.0e}'
    })
    
    model_file = build_fresnel_model(params)
    print(f"Completed: P={power:.0e}, R={radius:.0e}")
```
