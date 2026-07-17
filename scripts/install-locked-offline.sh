#!/usr/bin/env bash
# Offline locked install for Codex Cloud / Linux (no PyPI).
# Uses committed wheels under vendor/python-wheels.
#
# Critical: never `pip install --upgrade pip` and never allow build-isolation
# to reach the index — Cloud proxy returns HTTP 403 for /simple/*.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${1:-/tmp/arrivia-offline-venv}"
WH="$ROOT/vendor/python-wheels"

if [[ ! -d "$WH" ]] || ! compgen -G "$WH/*.whl" >/dev/null; then
  echo "ERROR: missing wheels in $WH — regenerate per vendor/python-wheels/README.md" >&2
  exit 1
fi

# Force every nested pip invocation offline (build isolation, pep517, etc.).
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$WH"
export PIP_DISABLE_PIP_VERSION_CHECK=1

python3.12 -m venv "$VENV" 2>/dev/null || python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# Do NOT upgrade pip from PyPI. Install build + runtime locks from wheels only.
python -m pip install -q --no-index --find-links="$WH" \
  -r "$ROOT/requirements-build.lock" \
  -r "$ROOT/requirements-dev.lock"

# Editable install without build isolation (setuptools/wheel already present).
python -m pip install -q --no-index --find-links="$WH" --no-deps --no-build-isolation -e "$ROOT"

python -c "import pytest,ruff,setuptools; print('offline_install_ok', pytest.__version__, setuptools.__version__)"
echo "VENV=$VENV"
