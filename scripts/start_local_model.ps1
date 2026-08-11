$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $repoRoot
$server = if ($env:DATAPILOT_LLAMA_SERVER) {
    $env:DATAPILOT_LLAMA_SERVER
} else {
    Join-Path $workspaceRoot "runtimes\llama-vulkan\llama-server.exe"
}
$modelPath = if ($env:DATAPILOT_MODEL_PATH) {
    $env:DATAPILOT_MODEL_PATH
} else {
    Join-Path $workspaceRoot "models\DeepAnalyze-8B-GGUF\DeepAnalyze-8B-Q4_K_M.gguf"
}
$logDir = Join-Path $repoRoot ".local-logs"

if (-not (Test-Path $server)) {
    throw "llama.cpp server not found: $server"
}
if (-not (Test-Path $modelPath)) {
    throw "Quantized DeepAnalyze model not found: $modelPath"
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$arguments = @(
    "--model", "`"$modelPath`"",
    "--alias", "DeepAnalyze-8B",
    "--device", "Vulkan1",
    "--gpu-layers", "all",
    "--ctx-size", "4096",
    "--batch-size", "256",
    "--ubatch-size", "128",
    "--parallel", "1",
    "--flash-attn", "auto",
    "--jinja",
    "--special",
    "--reasoning-format", "none",
    "--host", "127.0.0.1",
    "--port", "8000"
)

$process = Start-Process -FilePath $server `
    -ArgumentList $arguments `
    -WorkingDirectory (Split-Path -Parent $server) `
    -RedirectStandardOutput (Join-Path $logDir "local-model.stdout.log") `
    -RedirectStandardError (Join-Path $logDir "local-model.stderr.log") `
    -WindowStyle Hidden `
    -PassThru

$process.Id | Set-Content -Path (Join-Path $logDir "local-model.pid") -Encoding ascii
Write-Output "Local DeepAnalyze llama.cpp server started with PID $($process.Id)"
Write-Output "Health: http://127.0.0.1:8000/health"
Write-Output "Logs: $logDir"
