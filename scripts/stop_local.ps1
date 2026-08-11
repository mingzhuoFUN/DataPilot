$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "stop_local_frontend.ps1")
& (Join-Path $PSScriptRoot "stop_local_backend.ps1")
& (Join-Path $PSScriptRoot "stop_local_model.ps1")

Write-Output "DataPilot local services have stopped."
