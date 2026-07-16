#!/usr/bin/env bash
# Codex Cloud Environment — maintenance script (runs when a cached container resumes).
# Paste into: Codex → Environments → Maintenance script
# Keep this light so cache resumes stay fast; only re-verify / fill gaps.
set -euo pipefail

export TF_IN_AUTOMATION=1

ok=1
for cmd in git node pwsh terraform aws; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "missing $cmd — re-running setup"
    ok=0
    break
  fi
done

if [[ "$ok" -ne 1 ]]; then
  # Repo is already checked out at task branch when maintenance runs.
  if [[ -f .codex/cloud-setup.sh ]]; then
    bash .codex/cloud-setup.sh
  else
    echo "ERROR: toolchain missing and .codex/cloud-setup.sh not found" >&2
    exit 1
  fi
fi

# Best-effort wheelhouse refresh only. Never re-run full setup solely for
# wheels: a pip download 403 under set -e previously aborted maintenance and
# left Gate 6 tasks in ERROR with no agent output.
if [[ -f requirements-dev.lock && -f requirements-build.lock && -f .codex/cloud-setup.sh ]]; then
  wheelhouse="$HOME/.cache/arrivia-wheelhouse"
  stamp="$wheelhouse/locks.sha256"
  current_stamp="$(
    sha256sum requirements-dev.lock requirements-build.lock \
      | sha256sum \
      | awk '{print $1}'
  )" || current_stamp=""
  need_wheels=0
  if [[ -n "$current_stamp" ]]; then
    if [[ ! -f "$stamp" ]]; then
      need_wheels=1
    elif [[ "$(cat "$stamp" 2>/dev/null || true)" != "$current_stamp" ]]; then
      need_wheels=1
    fi
  fi
  if [[ "$need_wheels" -eq 1 ]]; then
    # Soft download only; never abort maintenance on PyPI/proxy 403.
    set +e
    mkdir -p "$wheelhouse"
    if python -m pip download --dest "$wheelhouse" -r requirements-dev.lock -r requirements-build.lock; then
      printf '%s\n' "$current_stamp" > "$stamp"
    else
      echo "WARN: wheelhouse refresh failed; continuing" >&2
    fi
    set -e
  fi
fi

# Optional: start Docker if the image provides it (ignore failures).
if command -v service >/dev/null 2>&1; then
  sudo service docker start 2>/dev/null || true
fi

echo "Codex cloud maintenance OK:"
node --version
pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'
terraform version -json 2>/dev/null | head -c 120 || terraform version
aws --version | head -n 1
