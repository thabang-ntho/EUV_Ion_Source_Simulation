#!/bin/bash
# COMSOL Environment Setup Script for EUV Simulation
# This script sets up all necessary environment variables for MPh library

echo "Setting up COMSOL environment for MPh library..."

# COMSOL installation paths
export COMSOL_ROOT=/home/xdadmin/comsol62/multiphysics
export COMSOL_BIN_DIR=${COMSOL_ROOT}/bin/glnxa64
export COMSOL_JAVA_HOME=${COMSOL_ROOT}/java/glnxa64/jre

# License configuration
export LMCOMSOL_LICENSE_FILE=${COMSOL_ROOT}/license/license.dat

# Add COMSOL to PATH (required for MPh discovery)
export PATH=${COMSOL_BIN_DIR}:${PATH}

# Java configuration for COMSOL
export JAVA_HOME=${COMSOL_JAVA_HOME}

# Library paths for COMSOL
export LD_LIBRARY_PATH=${COMSOL_ROOT}/lib/glnxa64:${COMSOL_ROOT}/java/glnxa64/jre/lib:${COMSOL_ROOT}/java/glnxa64/jre/lib/server:${LD_LIBRARY_PATH}

# MPh-specific environment
export COMSOL_HOME=${COMSOL_ROOT}

echo "✅ COMSOL environment configured successfully"
echo "   COMSOL_ROOT: $COMSOL_ROOT"
echo "   License: $LMCOMSOL_LICENSE_FILE"
echo "   PATH updated with COMSOL binary directory"

# Test COMSOL accessibility
if command -v comsol >/dev/null 2>&1; then
    echo "   ✅ COMSOL executable accessible: $(which comsol)"
else
    echo "   ❌ COMSOL executable not found in PATH"
fi
