#!/usr/bin/env bash
# Project bootstrap script: create/activate .venv, install deps, and run quick checks.
# Usage:
#   source ./bootstrap.sh            # recommended; keeps venv active in your shell
#   bash ./bootstrap.sh              # runs setup and tests in a subshell (venv not persisted)
#   source ./bootstrap.sh --no-tests # skip tests
#   source ./bootstrap.sh --runtime-only --no-smoke # install runtime deps only; skip smoke

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-${0}}")" && pwd)"

RUN_TESTS=1
RUN_SMOKE=1
DEV_EXTRAS=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-tests) RUN_TESTS=0; shift ;;
    --no-smoke) RUN_SMOKE=0; shift ;;
    --runtime-only) DEV_EXTRAS=0; shift ;;
    -h|--help)
      cat <<'HELP'
Options:
  --no-tests       Skip running pytest
  --no-smoke       Skip check-only CLI smoke (fresnel/kumar)
  --runtime-only   Install runtime deps only (omit dev extras)
HELP
      return 0 2>/dev/null || exit 0 ;;
    *) echo "[bootstrap] Unknown flag: $1" >&2; return 2 2>/dev/null || exit 2 ;;
  esac
done

# Avoid hardlink issues on some filesystems
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"

USE_UV=1
if ! command -v uv >/dev/null 2>&1; then
  echo "[bootstrap] 'uv' not found; will fall back to python -m venv + pip"
  USE_UV=0
fi

# Create .venv if missing
if [[ ! -d "$PROJECT_ROOT/.venv" ]]; then
  echo "[bootstrap] Creating .venv ..."
  if [[ $USE_UV -eq 1 ]]; then
    uv venv "$PROJECT_ROOT/.venv"
  else
    python3 -m venv "$PROJECT_ROOT/.venv"
  fi
fi

# Activate venv for this shell/subshell
# shellcheck disable=SC1091
source "$PROJECT_ROOT/.venv/bin/activate"

# Install dependencies
if [[ $DEV_EXTRAS -eq 1 ]]; then
  echo "[bootstrap] Installing dev dependencies ..."
  if [[ $USE_UV -eq 1 ]]; then
    uv pip install -e .[dev]
  else
    pip install -e .[dev]
  fi
else
  echo "[bootstrap] Installing runtime dependencies ..."
  if [[ $USE_UV -eq 1 ]]; then
    uv pip install -e .
  else
    pip install -e .
  fi
fi

# Run tests (fast) and smoke (no COMSOL)
if [[ $RUN_TESTS -eq 1 ]]; then
  echo "[bootstrap] Running tests ..."
  pytest -q
fi

if [[ $RUN_SMOKE -eq 1 ]]; then
  echo "[bootstrap] Running smoke (mph check-only) ..."
  python -m src.cli.mph_runner --dry-run --variant fresnel >/dev/null || true
fi

cat <<'DONE'
[bootstrap] Done.

To activate the environment in future shells:
  source .venv/bin/activate

Useful commands:
  make test          # fast unit tests
  make test-comsol   # COMSOL integration tests (requires license)
  make mph-dry-run   # smoke (no COMSOL)
DONE
