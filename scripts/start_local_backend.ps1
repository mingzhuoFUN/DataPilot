$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $repoRoot
$backendDir = Join-Path $repoRoot "demo\chat_v2"
$python = if ($env:DATAPILOT_PYTHON) {
    $env:DATAPILOT_PYTHON
} else {
    Join-Path $workspaceRoot "runtimes\deepanalyze\Scripts\python.exe"
}
$logDir = Join-Path $repoRoot ".local-logs"
$port = 8200

if (-not (Test-Path $python)) {
    throw "DataPilot Python environment not found: $python"
}
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $port is already in use."
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$env:DATAPILOT_MODEL_PROVIDER = "local"
$env:DATAPILOT_MODEL_API_BASE = "http://127.0.0.1:8000/v1"
$env:DATAPILOT_MODEL_NAME = "DeepAnalyze-8B"
$env:DATAPILOT_MODEL_API_KEY = ""
$env:DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG = "false"
$env:DATAPILOT_EXECUTION_MODE = "local"
$env:DATAPILOT_BACKEND_HOST = "127.0.0.1"
$env:DATAPILOT_BACKEND_PORT = "$port"
$env:DATAPILOT_WORKSPACE_BASE = Join-Path $workspaceRoot "workspaces"
$env:NO_PROXY = "localhost,127.0.0.1"
$env:no_proxy = "localhost,127.0.0.1"

$launcher = Start-Process -FilePath $python `
    -ArgumentList @("backend.py") `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput (Join-Path $logDir "backend.stdout.log") `
    -RedirectStandardError (Join-Path $logDir "backend.stderr.log") `
    -WindowStyle Hidden `
    -PassThru

$deadline = (Get-Date).AddSeconds(30)
do {
    Start-Sleep -Seconds 2
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
} while (-not $listener -and (Get-Date) -lt $deadline)
if (-not $listener) {
    throw "DataPilot backend did not start. Check $logDir\backend.stderr.log"
}
$listener.OwningProcess | Set-Content -Path (Join-Path $logDir "backend.pid") -Encoding ascii
Write-Output "DataPilot backend started with PID $($listener.OwningProcess)"
Write-Output "Health: http://127.0.0.1:$port/health"
