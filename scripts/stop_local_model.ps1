$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $repoRoot ".local-logs\local-model.pid"

if (-not (Test-Path $pidFile)) {
    Write-Output "No local model PID file found."
    exit 0
}

$modelPid = [int](Get-Content $pidFile)
$process = Get-CimInstance Win32_Process -Filter "ProcessId=$modelPid" -ErrorAction SilentlyContinue
if ($process -and $process.CommandLine -match "llama-server\.exe" -and $process.CommandLine -match "DeepAnalyze-8B-Q4_K_M\.gguf") {
    Stop-Process -Id $modelPid
    Wait-Process -Id $modelPid -ErrorAction SilentlyContinue
    Write-Output "Stopped local DeepAnalyze server PID $modelPid"
} elseif ($process) {
    throw "PID $modelPid no longer belongs to the local DeepAnalyze server; refusing to stop it."
} else {
    Write-Output "Local model process $modelPid is not running."
}
Remove-Item -LiteralPath $pidFile -Force
