# Codex Cloud Environment (arrivia-agentic-travel-recommendations-api)

Wire once in **Codex → Environments → this repository**:

1. Caching **On**
2. Setup: `bash .codex/cloud-setup.sh`
3. Maintenance: `bash .codex/cloud-maintenance.sh`
4. Save, then warm once (Paste block C from `PROMPT-SPEED-ADDENDUM.md`)
5. Register locally (never commit the id):

```powershell
pwsh -File scripts/Register-CodexCloudEnvironment.ps1 `
  -Repo 'nathanielecon/arrivia-agentic-travel-recommendations-api' `
  -EnvId '<ENV_ID_FROM_CODEX_UI>'
```

6. Before Cloud work: `pwsh -File scripts/Invoke-CodexCloudWarm.ps1 -Repo nathanielecon/arrivia-agentic-travel-recommendations-api`

This Environment is **per-repository**. Do not reuse `aws-landing-zone-lab` / `dailydigits` env ids for this repo.
