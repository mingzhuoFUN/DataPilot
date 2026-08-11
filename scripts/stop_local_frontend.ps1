$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $repoRoot ".local-logs\frontend.pid"

if (-not (Test-Path $pidFile)) {
    Write-Output "No DataPilot frontend PID file found."
    exit 0
}

$frontendPid = [int](Get-Content $pidFile)
$process = Get-CimInstance Win32_Process -Filter "ProcessId=$frontendPid" -ErrorAction SilentlyContinue
if ($process -and $process.CommandLine -match "next" -and $process.CommandLine -match "start") {
    Stop-Process -Id $frontendPid
    Wait-Process -Id $frontendPid -ErrorAction SilentlyContinue
    Write-Output "Stopped DataPilot frontend PID $frontendPid"
} elseif ($process) {
    throw "PID $frontendPid no longer belongs to DataPilot frontend; refusing to stop it."
} else {
    Write-Output "DataPilot frontend process $frontendPid is not running."
}
Remove-Item -LiteralPath $pidFile -Force
