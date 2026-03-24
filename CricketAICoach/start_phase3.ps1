$ErrorActionPreference = "Stop"

$root = "C:\CricketCoach"

$services = @(
    @{ Name = "player_service"; Port = 8001 },
    @{ Name = "match_service"; Port = 8002 },
    @{ Name = "analytics_service"; Port = 8003 },
    @{ Name = "ai_service"; Port = 8004 },
    @{ Name = "video_service"; Port = 8005 },
    @{ Name = "gateway"; Port = 8000 }
)

foreach ($svc in $services) {
    $path = Join-Path $root $svc.Name
    if (-not (Test-Path $path)) {
        Write-Host "Skipping $($svc.Name): path not found ($path)" -ForegroundColor Yellow
        continue
    }

    $cmd = "Set-Location '$path'; uvicorn main:app --reload --port $($svc.Port)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd | Out-Null
    Write-Host "Started $($svc.Name) on port $($svc.Port)" -ForegroundColor Green
}

Write-Host "All start commands issued." -ForegroundColor Cyan
