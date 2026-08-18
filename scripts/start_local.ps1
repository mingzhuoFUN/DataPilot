$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    & (Join-Path $PSScriptRoot "start_local_model.ps1")
    $deadline = (Get-Date).AddMinutes(3)
    do {
        Start-Sleep -Seconds 3
        try {
            $healthy = (Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3).status -eq "ok"
        } catch {
            $healthy = $false
        }
    } while (-not $healthy -and (Get-Date) -lt $deadline)
    if (-not $healthy) {
        throw "Local model did not become healthy. Check $repoRoot\.local-logs\local-model.stderr.log"
    }
}

if (-not (Get-NetTCPConnection -LocalPort 8200 -State Listen -ErrorAction SilentlyContinue)) {
    & (Join-Path $PSScriptRoot "start_local_backend.ps1")
}

if (-not (Get-NetTCPConnection -LocalPort 4000 -State Listen -ErrorAction SilentlyContinue)) {
    & (Join-Path $PSScriptRoot "start_local_frontend.ps1")
}

Write-Output "DataPilot is ready: http://127.0.0.1:4000"
