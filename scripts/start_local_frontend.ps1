$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "demo\chat_v2\frontend"
$pathNode = Get-Command node.exe -ErrorAction SilentlyContinue
$bundledNode = Join-Path ([Environment]::GetFolderPath("UserProfile")) ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$node = if ($env:DATAPILOT_NODE) {
    $env:DATAPILOT_NODE
} elseif ($pathNode) {
    $pathNode.Source
} else {
    $bundledNode
}
$next = "node_modules/next/dist/bin/next"
$logDir = Join-Path $repoRoot ".local-logs"
$port = 4000

if (-not (Test-Path $node)) {
    throw "Bundled Node.js was not found: $node"
}
if (-not (Test-Path (Join-Path $frontendDir $next))) {
    throw "Frontend dependencies were not found. Run pnpm install in $frontendDir first."
}
if (-not (Test-Path (Join-Path $frontendDir ".next\BUILD_ID"))) {
    throw "Frontend production build was not found. Run next build first."
}
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $port is already in use."
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$env:DATAPILOT_BACKEND_INTERNAL_URL = "http://127.0.0.1:8200"
$env:NO_PROXY = "localhost,127.0.0.1"
$env:no_proxy = "localhost,127.0.0.1"

$launcher = Start-Process -FilePath $node `
    -ArgumentList @($next, "start", "-H", "127.0.0.1", "-p", "$port") `
    -WorkingDirectory $frontendDir `
    -RedirectStandardOutput (Join-Path $logDir "frontend.stdout.log") `
    -RedirectStandardError (Join-Path $logDir "frontend.stderr.log") `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 5
$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $listener) {
    throw "DataPilot frontend did not start. Check $logDir\frontend.stderr.log"
}
$listener.OwningProcess | Set-Content -Path (Join-Path $logDir "frontend.pid") -Encoding ascii
Write-Output "DataPilot frontend started with PID $($listener.OwningProcess)"
Write-Output "Open: http://127.0.0.1:$port"
