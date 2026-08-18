$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $repoRoot ".local-logs\backend.pid"

if (-not (Test-Path $pidFile)) {
    Write-Output "No DataPilot backend PID file found."
    exit 0
}

$backendPid = [int](Get-Content $pidFile)
$process = Get-CimInstance Win32_Process -Filter "ProcessId=$backendPid" -ErrorAction SilentlyContinue
if ($process -and $process.CommandLine -match "backend\.py") {
    Stop-Process -Id $backendPid
    Wait-Process -Id $backendPid -ErrorAction SilentlyContinue
    Write-Output "Stopped DataPilot backend PID $backendPid"
} elseif ($process) {
    throw "PID $backendPid no longer belongs to DataPilot backend; refusing to stop it."
} else {
    Write-Output "DataPilot backend process $backendPid is not running."
}
Remove-Item -LiteralPath $pidFile -Force

