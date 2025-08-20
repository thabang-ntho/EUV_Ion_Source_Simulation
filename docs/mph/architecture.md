# MPh Architecture Overview

## Introduction

The MPh-based architecture represents a complete rewrite of the EUV droplet simulation codebase, transitioning from low-level Java API calls to high-level Python MPh API patterns. This improves maintainability, readability, and developer productivity.

## Key Benefits

### 1. Developer Productivity
- **Pythonic API**: Use `geometry.create()` instead of `java_model.geom().create()`
- **Type Safety**: Full type hints throughout the codebase
- **Better IDE Support**: Auto-completion and documentation
- **Reduced Complexity**: No Java knowledge required

### 2. Code Maintainability
- **Modular Design**: Separate modules for geometry, physics, materials, etc.
- **Clear Separation**: Variant-specific logic isolated in dedicated modules
- **Consistent Patterns**: Uniform API patterns across all components
- **Better Testing**: Mockable interfaces for unit testing

### 3. Error Handling
- **Meaningful Errors**: Custom exception types with context
- **Validation**: Parameter and geometry validation before building
- **Build Tracking**: Stage-by-stage progress monitoring
- **Graceful Cleanup**: Automatic COMSOL connection management

## Architecture Components

### Core Modules (`src/mph_core/`)

#### 1. ModelBuilder
- **Purpose**: Main orchestrator for model building
- **Key Features**:
  - Context manager for automatic cleanup
  - Build stage tracking
  - Error handling and recovery
  - Comprehensive model information reporting

```python
with ModelBuilder(params, 'fresnel') as builder:
    model_file = builder.build_complete_model()
    results = builder.solve_and_extract_results()
```

#### 2. GeometryBuilder
- **Purpose**: High-level geometry creation
- **Key Features**:
  - Parameter validation
  - Geometry constraint checking
  - Domain information reporting
  - MPh geometry.create() patterns

```python
builder = GeometryBuilder(model, params)
builder.create_domain()  # Creates rectangle + circle
info = builder.get_domain_info()  # Area calculations
```

#### 3. SelectionManager
- **Purpose**: Named selection creation and management
- **Key Features**:
  - Automatic selection generation
  - Selection validation
  - Entity dimension handling
  - Physics-ready selections

```python
manager = SelectionManager(model, geometry_builder)
selections = manager.create_all_selections()
# Creates: s_drop, s_gas, s_surf, s_laser, etc.
```

#### 4. PhysicsManager
- **Purpose**: Physics interface setup and coupling
- **Key Features**:
  - Variant-specific physics configuration
  - Boundary condition setup
  - Physics coupling validation
  - Material property integration

```python
physics = PhysicsManager(model, selections, materials)
interfaces = physics.setup_all_physics('fresnel')
# Creates: HT, TDS, ALE interfaces
```

#### 5. MaterialsHandler
- **Purpose**: Material property management
- **Key Features**:
  - Temperature-dependent properties
  - Material validation
  - Domain assignment
  - Property expression building

```python
materials = MaterialsHandler(model, params)
materials.create_all_materials()  # Tin + gas materials
materials.assign_materials_to_domains(selections)
```

#### 6. StudyManager
- **Purpose**: Study and solver configuration
- **Key Features**:
  - Transient and steady studies
  - Adaptive mesh generation
  - Solver configuration
  - Time stepping control

```python
studies = StudyManager(model, physics, params)
studies.create_all_studies()  # Mesh + studies
success = studies.run_study('transient')
```

#### 7. ResultsProcessor
- **Purpose**: Results extraction and export
- **Key Features**:
  - Multiple output formats (PNG, VTK, CSV)
  - Variant-specific extractions
  - Summary statistics
  - Time series data

```python
processor = ResultsProcessor(model, params)
results = processor.extract_all_results('fresnel')
# Generates: temperature fields, time series, summary stats
```

### Variant Models (`src/models/`)

#### FresnelModelBuilder
- **Focus**: Evaporation and species transport
- **Physics**: Heat Transfer + Transport of Diluted Species + ALE
- **Key Features**:
  - Gaussian laser heating profile
  - Hertz-Knudsen evaporation kinetics
  - Species diffusion in background gas
  - Temperature-dependent material properties

#### KumarModelBuilder  
- **Focus**: Fluid dynamics and thermal effects
- **Physics**: Heat Transfer + Single Phase Flow + ALE
- **Key Features**:
  - Volumetric heat generation
  - Marangoni stress effects
  - Surface tension modeling
  - Mesh deformation with ALE

## Configuration and Parameters

### Parameter Hierarchy
1. **Default Values**: Built into each variant
2. **Config Files**: Loaded from `data/` directory
3. **CLI Overrides**: Command-line parameter overrides
4. **Variant Defaults**: Variant-specific defaults applied

### Parameter Categories
- **Geometry**: Domain size, droplet radius, positioning
- **Materials**: Tin properties (density, conductivity, viscosity)
- **Physics**: Laser power, evaporation coefficients, flow parameters
- **Simulation**: Time stepping, solver tolerances, output control
- **Results**: Output formats, plot ranges, extraction settings

## Usage Examples

### Basic Model Building

```python
from src.models import build_fresnel_model

params = {
    'Domain_Width': 100e-6,
    'Domain_Height': 100e-6,
    'Droplet_Radius': 25e-6,
    'Laser_Power': 1e6,
    'Time_End': 100e-9
}

model_file = build_fresnel_model(params, output_path='fresnel_model.mph')
```

### Advanced Usage with Custom Builder

```python
from src.models import FresnelModelBuilder

params = load_config('data/global_parameters_pp_v2.txt')

with FresnelModelBuilder(params) as builder:
    # Build model
    model_file = builder.build_complete_model()
    
    # Get model information
    info = builder.get_model_info()
    print(f"Geometry: {info['geometry']}")
    print(f"Materials: {info['materials']}")
    
    # Solve and extract results
    results = builder.solve_and_extract_results()
    print(f"Results: {list(results.keys())}")
```

### CLI Usage

```bash
# Build Fresnel model with custom parameters
python -m src.mph_cli fresnel --config data/global_parameters_pp_v2.txt \
    --laser-power 2e6 --gas-type argon --solve

# Build Kumar model with volumetric heating
python -m src.mph_cli kumar --volumetric-heating 1e12 \
    --enable-marangoni --output kumar_model.mph

# List available parameters
python -m src.mph_cli fresnel --list-params

# Validate configuration
python -m src.mph_cli --validate-config data/global_parameters_pp_v2.txt
```

## Testing Strategy

### Unit Tests
- **Mock Objects**: All COMSOL interactions mocked
- **Parameter Validation**: Geometry constraints, material properties
- **Component Integration**: Builder interactions
- **Error Handling**: Exception scenarios

### Integration Tests  
- **End-to-End**: Complete model building workflow
- **Variant Comparison**: Fresnel vs Kumar differences
- **Result Validation**: Output format checking

### Migration Validation
- **Parameter Mapping**: Old vs new parameter handling
- **Numerical Equivalence**: Geometry calculations
- **Regression Tests**: Ensure no functionality loss

## Performance Considerations

### Memory Management
- **Context Managers**: Automatic COMSOL cleanup
- **Lazy Loading**: Components created only when needed
- **Parameter Caching**: Avoid redundant calculations

### Build Optimization
- **Stage Tracking**: Skip completed stages on restart
- **Validation Early**: Catch errors before COMSOL interaction
- **Parallel Capable**: Design allows future parallelization

## Error Handling

### Exception Hierarchy
- **ConfigurationError**: Invalid parameters or missing files
- **ModelBuildError**: COMSOL model building failures
- **ValidationError**: Geometry or physics validation failures

### Error Recovery
- **Build Stages**: Track progress for restart capability
- **Graceful Cleanup**: Always disconnect from COMSOL
- **Detailed Logging**: Comprehensive error context

## Migration from Old Implementation

### Comparison with Legacy Code

| Aspect | Old Implementation | New MPh Implementation |
|--------|-------------------|----------------------|
| API Style | `java_model.geom().create()` | `geometry.create()` |
| Error Handling | Basic try-catch | Comprehensive exception hierarchy |
| Testing | Limited mocking | Full mock support |
| Modularity | Monolithic build.py | Separate specialized modules |
| Type Safety | Minimal | Full type hints |
| Documentation | Limited | Comprehensive docstrings |

### Migration Strategy
1. **Parallel Development**: New implementation alongside old
2. **Validation Testing**: Ensure equivalent results
3. **Gradual Transition**: Component-by-component replacement
4. **Backward Compatibility**: Keep old CLI available during transition

## Future Enhancements

### Planned Features
- **Parameter Optimization**: Automated parameter tuning
- **Result Analysis**: Built-in analysis tools
- **Parallel Execution**: Multi-study parallel solving
- **Cloud Integration**: Remote COMSOL server support
- **GUI Interface**: Optional graphical interface

### Extension Points
- **Custom Physics**: Plugin system for new physics
- **Material Database**: Expandable material library
- **Result Processors**: Custom analysis modules
- **Geometry Generators**: Parametric geometry creation
