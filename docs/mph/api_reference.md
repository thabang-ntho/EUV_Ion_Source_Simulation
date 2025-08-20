# MPh API Reference Guide

## 📋 **Overview**

This document provides the definitive reference for using the MPh Python library with COMSOL Multiphysics, based on successful implementation and `mph_example.py` analysis.

## 🎯 **Fundamental Patterns**

### **Container Access Pattern**

MPh uses a **container-based** approach, not method calls:

```python
# ✅ CORRECT: Container access with dictionary-like syntax
materials = model/'materials'
geometries = model/'geometries'
selections = model/'selections'
physics = model/'physics'
studies = model/'studies'
solutions = model/'solutions'

# ❌ INCORRECT: Method calls (these don't exist)
model.materials()    # Does not exist
model.geometries()   # Does not exist
model.selections()   # Does not exist
```

### **Object Creation Pattern**

All objects are created using the `.create()` method on containers:

```python
# Generic pattern
container = model/'container_name'
object = container.create('ObjectType', *args, name='object_name')

# Specific examples
material = materials.create('Common', name='tin')
geometry = geometries.create(2, name='geometry')  # 2D geometry
selection = selections.create('Disk', name='droplet')
physics = physics.create('HeatTransfer', geometry, name='ht')
```

## 🏗️ **Geometry Module**

### **Basic Geometry Creation**
```python
# Create geometry container and 2D geometry
geometries = model/'geometries'
geometry = geometries.create(2, name='geometry')

# Create geometric objects
rectangle = geometry.create('Rectangle', name='domain')
rectangle.property('pos', [x, y])
rectangle.property('size', [width, height])

circle = geometry.create('Circle', name='droplet')
circle.property('pos', [x, y])
circle.property('r', radius)

# Build geometry (CRITICAL step)
model.build(geometry)
```

### **Advanced Operations**
```python
# Boolean operations
difference = geometry.create('Difference', name='domain_minus_droplet')
difference.property('input', [rectangle, circle])
difference.property('interiorsettings', 'on')

# Geometry finalization
model.build(geometry)  # Always call after modifications
```

## 🎯 **Selections Module**

### **Domain Selections**
```python
selections = model/'selections'

# Disk selection for circular domains
droplet_sel = selections.create('Disk', name='droplet_domain')
droplet_sel.property('posx', x_center)
droplet_sel.property('posy', y_center)
droplet_sel.property('r', radius)

# Box selection for rectangular domains
domain_sel = selections.create('Box', name='gas_domain')
domain_sel.property('xmin', x_min)
domain_sel.property('xmax', x_max)
domain_sel.property('ymin', y_min)
domain_sel.property('ymax', y_max)
```

### **Boundary Selections**
```python
# Adjacent selection (finds boundaries of domains)
boundary_sel = selections.create('Adjacent', name='droplet_boundary')
boundary_sel.property('input', [droplet_sel])  # Reference to domain selection

# Explicit selection
explicit_sel = selections.create('Explicit', name='manual_selection')
explicit_sel.select([entity_ids])  # List of entity IDs
```

### **Selection Operations**
```python
# Union of selections
union_sel = selections.create('Union', name='combined')
union_sel.property('input', [selection1, selection2])

# Intersection
intersect_sel = selections.create('Intersection', name='overlap')
intersect_sel.property('input', [selection1, selection2])
```

## 🧪 **Materials Module**

### **Material Creation**
```python
materials = model/'materials'

# Create material
material = materials.create('Common', name='material_name')
material.property('family', 'custom')  # or 'metal', 'air', etc.
```

### **Property Setting (CRITICAL Pattern)**

Properties must be set on the **Basic sub-node**, not directly on the material:

```python
# ✅ CORRECT: Use Basic sub-node
basic = material/'Basic'
basic.property('density', '7310[kg/m^3]')
basic.property('thermalconductivity', '66.8[W/(m*K)]')
basic.property('heatcapacity', '228[J/(kg*K)]')

# ❌ INCORRECT: Direct property setting
material.property('density', value)  # Does not work
```

### **Temperature-Dependent Properties**
```python
# Use conditional expressions for temperature dependence
T_melt = 505.08  # Melting temperature in K
rho_solid = 7310  # Solid density
rho_liquid = 6990  # Liquid density

rho_expr = f"if(T<{T_melt}[K], {rho_solid}[kg/m^3], {rho_liquid}[kg/m^3])"
basic.property('density', rho_expr)
```

### **Material Assignment (CRITICAL Pattern)**

Materials are assigned to selections using `.select()`, not `.property()`:

```python
# ✅ CORRECT: Use .select() method
material.select(selection_object)
# or
material.select(model/'selections'/'selection_name')

# ❌ INCORRECT: Property assignment
material.property('selection', selection)  # Does not work
```

## ⚡ **Physics Module**

### **Physics Creation**
```python
physics = model/'physics'

# Create physics interface
ht = physics.create('HeatTransfer', geometry, name='heat_transfer')
ht.select(domain_selections)  # Apply to specific domains
```

### **Physics Properties**
```python
# Set physics properties
ht.property('property_name', value)

# Enable/disable features
ht.java.prop('property').set('value', setting)
```

### **Boundary Conditions**
```python
# Create boundary condition
bc = ht.create('TemperatureBoundary', 1, name='temperature_bc')
bc.select(boundary_selection)
bc.property('T0', 'T_initial')

# Heat flux boundary condition
flux_bc = ht.create('HeatFlux', 1, name='heat_flux')
flux_bc.select(boundary_selection)
flux_bc.property('q0', heat_flux_expression)
```

## 📊 **Studies Module**

### **Study Creation**
```python
studies = model/'studies'
solutions = model/'solutions'

# Create study
study = studies.create(name='transient_study')
study.java.setGenPlots(False)  # Disable automatic plots
study.java.setGenConv(False)   # Disable convergence plots
```

### **Study Steps**
```python
# Transient study step
step = study.create('Transient', name='time_dependent')
step.property('tlist', 'range(0, 0.01, 1)')  # Time range
step.property('activate', [
    physics/'heat_transfer', 'on',
    'frame:spatial1', 'on',
    'frame:material1', 'on',
])
```

### **Solution Configuration**
```python
# Create solution
solution = solutions.create(name='solution_name')
solution.java.study(study.tag())
solution.java.attach(study.tag())

# Solution components
solution.create('StudyStep', name='equations')
solution.create('Variables', name='variables')
solver = solution.create('Stationary', name='solver')
```

## 🔧 **Model Management**

### **Model Creation**
```python
import mph

# Start client
client = mph.start(cores=1)

# Create model
model = client.create('model_name')
```

### **Parameter Setting**
```python
# Set global parameters
model.parameter('param_name', 'value[unit]')
model.description('param_name', 'Parameter description')
```

### **Model Building**
```python
# Build geometry (required after geometry changes)
model.build(geometry)

# Save model
model.save('path/to/model.mph')
```

### **Client Management**
```python
# Clean shutdown
client.remove()  # Removes all models and shuts down
```

## 🛠️ **Advanced Patterns**

### **Property Access**
```python
# Access nested properties
model.java.prop('property_path').set('value', setting)

# Get property values
value = object.property('property_name')
```

### **Selection References**
```python
# Reference selections by name
selection_ref = model/'selections'/'selection_name'

# Use in other objects
boundary_condition.select(selection_ref)
```

### **Error Handling**
```python
try:
    # MPh operations
    model.build(geometry)
except Exception as e:
    logger.error(f"MPh operation failed: {e}")
    # Handle specific COMSOL errors
```

## 🚨 **Common Mistakes to Avoid**

### **1. Method Calls Instead of Containers**
```python
# ❌ WRONG
model.geometries()
model.materials()

# ✅ CORRECT  
model/'geometries'
model/'materials'
```

### **2. Direct Material Property Setting**
```python
# ❌ WRONG
material.property('density', value)

# ✅ CORRECT
(material/'Basic').property('density', value)
```

### **3. Property-Based Selection Assignment**
```python
# ❌ WRONG
material.property('selection', selection)

# ✅ CORRECT
material.select(selection)
```

### **4. Forgetting Geometry Build**
```python
# ❌ WRONG: Create geometry but don't build
geometry.create('Rectangle', name='rect')
# Missing: model.build(geometry)

# ✅ CORRECT: Always build after geometry changes
geometry.create('Rectangle', name='rect')
model.build(geometry)
```

## 📚 **Reference Implementation**

The `mph_example.py` file in the project root is the **authoritative reference** for all MPh API patterns. When in doubt, consult this file for exact syntax and usage patterns.

## 🔍 **Debugging Tips**

1. **Check Container Access**: Ensure you're using `/` syntax, not method calls
2. **Verify Property Paths**: Material properties go on Basic sub-node
3. **Selection Assignment**: Always use `.select()` for material assignments
4. **Build After Changes**: Call `model.build(geometry)` after geometry modifications
5. **Reference mph_example.py**: Use as the definitive pattern guide

## 🎯 **Success Patterns**

The following pattern has been validated as working:

```python
import mph

# 1. Start client
client = mph.start(cores=1)
model = client.create('test_model')

# 2. Create geometry
geometries = model/'geometries'
geometry = geometries.create(2, name='geometry')
rect = geometry.create('Rectangle', name='domain')
model.build(geometry)

# 3. Create selections
selections = model/'selections'
selection = selections.create('Disk', name='domain_sel')

# 4. Create materials
materials = model/'materials'
material = materials.create('Common', name='material')
(material/'Basic').property('density', '1000[kg/m^3]')
material.select(selection)

# 5. Clean shutdown
client.remove()
```

This reference guide represents the accumulated knowledge from successful MPh implementation and should be the go-to resource for all MPh API usage in the project.
