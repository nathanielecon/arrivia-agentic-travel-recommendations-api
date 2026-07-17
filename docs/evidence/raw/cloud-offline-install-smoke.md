# Cloud Offline Locked Install Smoke

- UTC time: 2026-07-17T00:46:42Z
- HEAD: `790fb42d1db5bee13ac2c65cde613bbd58979e3d`
- Python version: `Python 3.12.13`
- Wheelhouse: `vendor/python-wheels`
- Offline installer: `scripts/install-locked-offline.sh`
- Verdict: **PASS** — `offline_install_ok`; `122 tests collected`. pytest/ruff/fastapi/mcp importable (use `ruff --version`, not `ruff.__version__`).

## Command outputs

### 1. HEAD and wheel count

```console
$ git rev-parse HEAD
790fb42d1db5bee13ac2c65cde613bbd58979e3d
$ ls vendor/python-wheels/*.whl | wc -l
47
```

### 2. Locked offline install

```console
$ bash scripts/install-locked-offline.sh /tmp/offprove
offline_install_ok 9.1.1 83.0.0
VENV=/tmp/offprove
```

### 3. Pytest collection

```console
$ /tmp/offprove/bin/python -m pytest -q --collect-only | tail -n 3

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
122 tests collected in 1.66s
```

Cloud task: `task_e_6a597b38c7a0832b9a273e859f5574e7` (GPT-5.4).
