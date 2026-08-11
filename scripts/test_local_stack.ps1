$ErrorActionPreference = "Stop"

$checks = @(
    @{ Name = "model"; Url = "http://127.0.0.1:8000/health" },
    @{ Name = "backend"; Url = "http://127.0.0.1:8200/health" },
    @{ Name = "frontend proxy"; Url = "http://127.0.0.1:4000/api/health" }
)

foreach ($check in $checks) {
    $response = Invoke-RestMethod -Uri $check.Url -TimeoutSec 10
    if ($response.status -ne "ok") {
        throw "$($check.Name) health check failed."
    }
    Write-Output "OK: $($check.Name)"
}

$pageResponse = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:4000/" -TimeoutSec 10
if ($pageResponse.StatusCode -ne 200) {
    throw "Frontend page returned HTTP $($pageResponse.StatusCode)."
}
Write-Output "OK: frontend page"

$payload = @{
    messages = @(@{
        role = "user"
        content = "Return only the result of 3+4 inside an <Answer> tag."
    })
    session_id = "local-stack-smoke"
    stream = $true
} | ConvertTo-Json -Depth 5

$chatResponse = Invoke-WebRequest `
    -UseBasicParsing `
    -Uri "http://127.0.0.1:4000/api/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $payload `
    -TimeoutSec 180

if ($chatResponse.StatusCode -ne 200 -or $chatResponse.Content -notmatch "<Answer>") {
    throw "The real model request through the frontend proxy failed."
}
Write-Output "OK: frontend -> backend -> local DeepAnalyze model"
