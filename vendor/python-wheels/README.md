# Vendored Python wheels (Linux / CloudWarm)

Committed Linux (`manylinux`, CPython 3.12) wheels for locked deps so Codex Cloud
agents can create a fresh venv **without PyPI egress**.

Cloud agent-phase (and previously setup-phase) `pip` hits proxy **HTTP 403** on
PyPI. Do **not** put `pip download` / wheelhouse network fetches in
`.codex/cloud-setup.sh` or `.codex/cloud-maintenance.sh`.

## Regenerate (local / Docker, working PyPI)

```bash
docker run --rm -v "$PWD":/w -w /w python:3.12-slim bash -lc '
  python -m pip install -q --upgrade pip
  rm -rf vendor/python-wheels && mkdir -p vendor/python-wheels
  python -m pip download -r requirements-dev.lock -r requirements-build.lock -d vendor/python-wheels
'
```

## Fresh Cloud / Linux install (offline)

```bash
# Pin Codex Environment Python to 3.12. Never pip-upgrade from PyPI.
bash scripts/install-locked-offline.sh /tmp/g6v
# Script sets PIP_NO_INDEX=1 and uses --no-build-isolation for editable install.
```

Pin the Codex Environment runtime to **Python 3.12** (matches these wheels).
`pywin32` is marker-gated to Windows and is skipped on Linux.
