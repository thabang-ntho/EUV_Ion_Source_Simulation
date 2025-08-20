# MPh API Migration Plan

## Objective
Complete migration from low-level Java API to high-level MPh API for improved productivity, maintainability, and code clarity.

## Migration Strategy

### Phase 1: Core Infrastructure (Week 1)
**Goal**: Establish new MPh-based architecture foundations

#### 1.1 New Core Modules
- [ ] `src/mph_core/` - New MPh-focused core modules
  - [ ] `geometry.py` - High-level geometry builders
  - [ ] `physics.py` - Physics interface managers  
  - [ ] `materials.py` - Material property handlers
  - [ ] `selections.py` - Selection utilities
  - [ ] `studies.py` - Study and solver configuration
  - [ ] `postprocess.py` - Results extraction and export

#### 1.2 Model Builder Refactor
- [ ] `src/mph_core/model_builder.py` - Main model construction class
- [ ] Replace `src/core/build.py` with MPh API equivalents
- [ ] Maintain same parameter injection and configuration loading

#### 1.3 Testing Framework
- [ ] `tests/mph_integration/` - New test suite for MPh API
- [ ] Mock MPh objects for unit testing
- [ ] Comparison tests between old and new implementations

### Phase 2: Geometry & Selections (Week 2)  
**Goal**: Convert geometry creation and selection management

#### 2.1 Geometry Builder (`src/mph_core/geometry.py`)
```python
class GeometryBuilder:
    def __init__(self, model, params):
        self.model = model
        self.params = params
        self.geometry = None
    
    def create_domain(self) -> None:
        """Create rectangular domain with circle droplet"""
        
    def create_selections(self) -> Dict[str, Any]:
        """Create named selections for physics assignment"""
```

#### 2.2 Selection Manager (`src/mph_core/selections.py`)
```python
class SelectionManager:
    def create_droplet_selections(self, geometry) -> Dict[str, Any]:
        """Create s_drop, s_surf, s_gas selections"""
        
    def create_boundary_selections(self, geometry) -> Dict[str, Any]:
        """Create domain boundary selections"""
```

### Phase 3: Physics & Materials (Week 3)
**Goal**: Convert physics interfaces and material assignments

#### 3.1 Physics Manager (`src/mph_core/physics.py`)
```python
class PhysicsManager:
    def setup_heat_transfer(self, model, selections, variant='fresnel'):
        """Setup HT physics with variant-specific BCs"""
        
    def setup_species_transport(self, model, selections, variant='fresnel'):
        """Setup TDS physics"""
        
    def setup_fluid_flow(self, model, selections, variant='fresnel'):
        """Setup SPF + ALE physics"""
```

#### 3.2 Materials Handler (`src/mph_core/materials.py`)
```python
class MaterialsHandler:
    def assign_tin_properties(self, model, selections):
        """Assign tin material to droplet domain"""
        
    def assign_gas_properties(self, model, selections, gas_type='none'):
        """Assign gas material properties"""
```

### Phase 4: Studies & Postprocessing (Week 4)
**Goal**: Convert solver setup and results extraction

#### 4.1 Study Manager (`src/mph_core/studies.py`)
```python
class StudyManager:
    def create_transient_study(self, model, physics_list):
        """Create time-dependent study"""
        
    def setup_mesh(self, model, geometry, selections):
        """Configure mesh with boundary layers"""
```

#### 4.2 Results Processor (`src/mph_core/postprocess.py`)
```python
class ResultsProcessor:
    def extract_temperature_field(self, model, output_dir):
        """Extract and save temperature PNG"""
        
    def extract_time_series(self, model, output_dir):
        """Extract CSV time series data"""
```

### Phase 5: Integration & Validation (Week 5)
**Goal**: Complete integration and validation

#### 5.1 Main Model Builder
- [ ] `src/mph_core/model_builder.py` - Orchestrate all components
- [ ] Update `src/pp_model.py` to use new MPh architecture
- [ ] Maintain CLI compatibility

#### 5.2 Validation & Testing
- [ ] Side-by-side result comparison (old vs new)
- [ ] Performance benchmarking
- [ ] Integration with existing config system
- [ ] CI/CD pipeline updates

## File Structure After Migration

```
src/
├── mph_core/                 # New MPh-based core
│   ├── __init__.py
│   ├── model_builder.py      # Main orchestrator
│   ├── geometry.py           # Geometry creation
│   ├── selections.py         # Selection management  
│   ├── physics.py            # Physics interfaces
│   ├── materials.py          # Material properties
│   ├── studies.py            # Studies and mesh
│   └── postprocess.py        # Results extraction
├── models/                   # Variant-specific logic
│   ├── mph_fresnel.py        # Fresnel variant (MPh API)
│   └── mph_kumar.py          # Kumar variant (MPh API)
├── core/                     # Keep existing scaffolds
│   ├── config/               # Configuration (unchanged)
│   ├── logging_utils.py      # Logging (unchanged)
│   └── errors.py             # Errors (unchanged)
└── pp_model.py               # Updated CLI entry point
```

## Testing Strategy

### Unit Tests
- [ ] Mock MPh model objects for isolated testing
- [ ] Test each MPh core module independently
- [ ] Parameter validation and error handling

### Integration Tests  
- [ ] End-to-end model building tests
- [ ] Fresnel vs Kumar variant comparison
- [ ] Config system integration

### Validation Tests
- [ ] Result comparison: old API vs new API
- [ ] Performance benchmarks
- [ ] Memory usage analysis

### CI/CD Updates
- [ ] Update test markers for MPh-based tests
- [ ] Maintain COMSOL-free testing capability
- [ ] Add MPh API smoke tests

## Documentation Updates

### Technical Documentation
- [ ] `docs/mph_architecture.md` - New architecture overview
- [ ] `docs/mph_api_guide.md` - MPh usage patterns
- [ ] `docs/migration_notes.md` - Changes from old implementation

### Code Documentation
- [ ] Comprehensive docstrings for all MPh modules
- [ ] Type hints throughout MPh core
- [ ] Example usage in docstrings

### User Documentation  
- [ ] Update README with new architecture notes
- [ ] CLI usage remains unchanged
- [ ] Troubleshooting guide for MPh-specific issues

## Success Criteria

1. **Functionality**: All existing features work with MPh API
2. **Performance**: No significant performance regression
3. **Maintainability**: Code is more readable and Pythonic
4. **Reliability**: Better error handling and debugging
5. **Testing**: Comprehensive test coverage for new implementation

## Risk Mitigation

- Maintain `mph_dev` branch until validation complete
- Keep old implementation accessible for comparison
- Incremental testing at each phase
- Performance monitoring throughout migration

## Timeline: 5 Weeks Total
- Week 1: Infrastructure & planning
- Week 2: Geometry & selections  
- Week 3: Physics & materials
- Week 4: Studies & postprocessing
- Week 5: Integration & validation
