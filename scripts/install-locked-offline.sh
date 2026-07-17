#!/usr/bin/env bash
# Offline locked install for Codex Cloud / Linux (no PyPI).
# Uses committed wheels under vendor/python-wheels.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${1:-/tmp/arrivia-offline-venv}"
WH="$ROOT/vendor/python-wheels"

if [[ ! -d "$WH" ]] || ! compgen -G "$WH/*.whl" >/dev/null; then
  echo "ERROR: missing wheels in $WH — regenerate per vendor/python-wheels/README.md" >&2
  exit 1
fi

python3.12 -m venv "$VENV" 2>/dev/null || python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install -q --upgrade pip
python -m pip install -q --no-index --find-links="$WH" \
  -r "$ROOT/requirements-build.lock" \
  -r "$ROOT/requirements-dev.lock"
python -m pip install -q --no-deps -e "$ROOT"
python -c "import pytest,ruff; print('offline_install_ok', pytest.__version__)"
echo "VENV=$VENV"
