# Study Physics Activation Plan

## Summary

After successfully debugging the `StudyManager` implementation, we need to properly implement physics activation in the study step. This document outlines the plan for implementing this feature.

## Current Status

- ✅ Direct creation of mesh, study, and solution is working
- ✅ Study and solution are properly linked
- ✅ Core workflow tests are passing with physics activation disabled
- ❌ Physics activation in study step is not working

## Reference Implementation (from mph_example.py)

```python
step.property('activate', [
    physics/'electrostatic', 'on',
    physics/'electric currents', 'off',
    'frame:spatial1', 'on',
    'frame:material1', 'on',
])
```

## Error Messages

When attempting to activate physics interfaces:

```
Invalid property value.
- Property: activate (Use in this study)

'Use in this study' is an array of strings.
- : An array of alternating keys and values
```

## Experiments Tried

1. Using direct physics interfaces objects:
```python
activation_list = []
for tag, interface in self.physics.items():
    activation_list.extend([interface, 'on'])
```

2. Using string paths:
```python
activation_list = []
for tag, interface in self.physics.items():
    physics_path = f"physics/{interface.tag()}"
    activation_list.extend([physics_path, 'on'])
```

## Plan for Implementation

1. Investigate the exact format expected by COMSOL for physics activation
   - Review mph_example.py more carefully
   - Check if there are any differences in how we're accessing physics interfaces

2. Try the following approaches:
   - Use the COMSOL path syntax: `model/'physics'/interface_tag`
   - Check if interfaces need to be referenced by tag rather than path
   - Verify that all referenced physics interfaces exist

3. Add debugging information:
   - Print the exact types of objects in the mph_example.py activation list
   - Compare with our implementation

4. Once physics activation is working, re-enable solving:
   - Implement the proper approach to run the solver
   - Add error handling for solver failures

## Implementation Plan

```python
# Activate physics interfaces
# Following the pattern from mph_example.py
physics = self.model/'physics'
activation_list = []

# Add each physics interface
for tag, interface in self.physics.items():
    # Try using the physics container to access the interface
    physics_ref = physics/interface.tag()
    activation_list.extend([physics_ref, 'on'])

# Add frame activations as in mph_example.py
activation_list.extend(['frame:spatial1', 'on', 'frame:material1', 'on'])

logger.info(f"Setting physics activation: {activation_list}")
step.property('activate', activation_list)
```
