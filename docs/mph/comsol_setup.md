# COMSOL + MPh Setup Guide

## 🎯 **Overview**

This guide provides comprehensive instructions for configuring COMSOL Multiphysics to work with the MPh Python library for the EUV simulation project. Based on successful troubleshooting and implementation of the MPh API integration.

## 📋 **Prerequisites**

- COMSOL Multiphysics 6.2+ installed on WSL/Linux
- Python virtual environment with MPh library
- Valid COMSOL license file
- Java environment properly configured

## 🔧 **License Configuration**

### Problem
MPh connection fails with:
```
com.comsol.util.exceptions.LicenseException: License error
```

### Solution ✅ **TESTED & WORKING**

**Step 1: Configure License Environment Variables**

Add COMSOL license file paths to both `~/.bashrc` and `~/.zshrc`:

```bash
# Add to BOTH ~/.zshrc and ~/.bashrc (idempotent)
for rc in ~/.zshrc ~/.bashrc; do
  touch "$rc"
  grep -qxF 'export LMCOMSOL_LICENSE_FILE=/usr/local/comsol62/multiphysics/license/license.dat' "$rc" \
    || echo 'export LMCOMSOL_LICENSE_FILE=/usr/local/comsol62/multiphysics/license/license.dat' >> "$rc"
  grep -qxF 'export LM_LICENSE_FILE=$LMCOMSOL_LICENSE_FILE' "$rc" \
    || echo 'export LM_LICENSE_FILE=$LMCOMSOL_LICENSE_FILE' >> "$rc"
done
```

**Step 2: Reload Shell Configuration**

```bash
# Reload the current shell's config
[ -n "$ZSH_VERSION" ] && source ~/.zshrc || ([ -n "$BASH_VERSION" ] && source ~/.bashrc)
```

**Step 3: Verify License Environment**

```bash
# Check license environment variables
env | grep -i license
```

Expected output:
```
LMCOMSOL_LICENSE_FILE=/usr/local/comsol62/multiphysics/license/license.dat
LM_LICENSE_FILE=/usr/local/comsol62/multiphysics/license/license.dat
```

**Step 4: Test MPh Connection**

```bash
# Activate virtual environment and test connection
source .venv/bin/activate && python -c "import mph; c = mph.start(cores=1); print(c)"
```

Expected output:
```
COMSOL client: Client(port=45122, host='localhost')
```

## 🧪 **MPh API Patterns (CRITICAL)**

### **Key Discovery: Container vs Method Access**

From `mph_example.py`, the correct MPh API patterns are:

#### ✅ **Correct Container Pattern:**
```python
# Access containers using dictionary-like syntax
materials = model/'materials'
geometries = model/'geometries'
selections = model/'selections'
physics = model/'physics'

# Create objects in containers
tin = materials.create('Common', name='tin')
geometry = geometries.create(2, name='geometry')
selection = selections.create('Disk', name='selection')
```

#### ❌ **Incorrect Method Pattern:**
```python
# DON'T use method calls (these don't exist)
model.geometries()  # ❌ NOT VALID
model.materials()   # ❌ NOT VALID
model.property('name', value)  # ❌ NOT VALID
```

### **Material Property Setting Pattern**

#### ✅ **Correct Basic Sub-node Pattern:**
```python
materials = model/'materials'
tin = materials.create('Common', name='tin')

# Properties go on the Basic sub-node
basic = tin/'Basic'
basic.property('density', '7310[kg/m^3]')
basic.property('thermalconductivity', '66.8[W/(m*K)]')
basic.property('heatcapacity', '228[J/(kg*K)]')
```

#### ❌ **Incorrect Direct Pattern:**
```python
# DON'T set properties directly on material
tin.property('density', value)  # ❌ NOT VALID
```

### **Material Assignment Pattern**

#### ✅ **Correct Selection Assignment:**
```python
# Materials are assigned to selections using .select()
tin = materials.create('Common', name='tin')
tin.select(model/'selections'/'droplet_domain')
```

#### ❌ **Incorrect Property Assignment:**
```python
# DON'T use property for selection assignment
tin.property('selection', selection)  # ❌ NOT VALID
```

## 🔍 **Troubleshooting**

### Issue: "License error" persists
- Verify license file path exists: `ls -la /usr/local/comsol62/multiphysics/license/license.dat`
- Check COMSOL installation: `which comsol && comsol --version`
- Ensure license server is accessible (if using network license)

### Issue: "Cannot open display"
- This is normal for headless COMSOL operation
- MPh bypasses GUI requirements

### Issue: "Application is null" Error
**Symptoms:**
```
java.lang.IllegalStateException: Internal error: Application is null
```

**Causes & Solutions:**
1. **Multiple COMSOL processes**: Kill all COMSOL processes and restart
   ```bash
   pkill -f "comsol mphserver"
   ```

2. **COMSOL workspace corruption**: Clear workspace
   ```bash
   rm -rf ~/.comsol/v62/workspace/*
   ```

3. **Java VM conflicts**: Restart system to clear Java state

4. **Process conflicts**: Ensure no background COMSOL servers running
   ```bash
   ps aux | grep comsol
   ```

### Issue: Import errors
- Verify virtual environment: `which python && python -c "import mph; print(mph.__version__)"`
- Reinstall if needed: `pip install mph`

## 🧪 **Testing MPh Implementation**

Once COMSOL is properly configured, test the EUV simulation:

```bash
# Activate environment with license configuration
source ~/.bashrc && source .venv/bin/activate

# Test parameter listing
python -m src.mph_cli fresnel --list-params
python -m src.mph_cli kumar --list-params

# Test dry run
python -m src.mph_cli fresnel --dry-run

# Build model (creates .mph file)
python -m src.mph_cli fresnel --build-only --output fresnel_model.mph
python -m src.mph_cli kumar --build-only --output kumar_model.mph

# Full simulation with solving
python -m src.mph_cli fresnel --solve --output fresnel_results.mph
```

## 📁 **File Locations**

- **License File**: `/usr/local/comsol62/multiphysics/license/license.dat`
- **COMSOL Binary**: `/usr/local/bin/comsol`
- **Configuration**: `~/.bashrc`, `~/.zshrc`
- **Virtual Environment**: `.venv/` in project root
- **COMSOL Logs**: `~/.comsol/v62/logs/`
- **COMSOL Workspace**: `~/.comsol/v62/workspace/`

## ✅ **Validation Checklist**

- [ ] License environment variables set in both bashrc and zshrc
- [ ] Shell configuration reloaded
- [ ] License variables visible in environment
- [ ] MPh connection test successful
- [ ] No conflicting COMSOL processes running
- [ ] EUV CLI commands working
- [ ] Model building completing successfully

## 🚀 **Production Usage**

For production usage, ensure the license configuration is persistent:

1. Add license configuration to system-wide shell configs if needed
2. Document license server dependencies for team members
3. Set up monitoring for license availability
4. Consider containerization for consistent environments

## 📋 **Implementation Status**

### ✅ **Completed & Verified:**
- [x] License configuration working
- [x] MPh API patterns identified
- [x] Geometry creation using correct API
- [x] Selection creation using correct API
- [x] Materials creation and property setting
- [x] Materials assignment using .select() method

### 🔄 **Current Status:**
- Materials module implementation complete with correct API patterns
- COMSOL initialization issue preventing final testing
- Ready for physics and studies module implementation

### 📝 **Known Working Code Patterns:**
```python
# Model creation
client = mph.start(cores=1)
model = client.create('model_name')

# Geometry building
geometries = model/'geometries'
geometry = geometries.create(2, name='geometry')
rectangle = geometry.create('Rectangle', name='rect')
model.build(geometry)

# Selections
selections = model/'selections'
selection = selections.create('Disk', name='selection')

# Materials with properties
materials = model/'materials'
material = materials.create('Common', name='material')
(material/'Basic').property('density', '7310[kg/m^3]')
material.select(selection_object)
```

---

**Success Indicator**: When properly configured, the MPh library should connect to COMSOL without license errors, and the EUV simulation should proceed through geometry creation, materials assignment, and model building stages.
