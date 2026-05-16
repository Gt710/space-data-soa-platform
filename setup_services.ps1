$pythonServices = @("astro-objects", "space-weather", "mission-data", "user-service")

foreach ($service in $pythonServices) {
    Write-Host "------------------------------------------" -ForegroundColor Yellow
    Write-Host "Setting up service: $service" -ForegroundColor Cyan
    $servicePath = "services/$service"
    
    if (-not (Test-Path "$servicePath/venv")) {
        Write-Host "Creating venv..."
        python -m venv "$servicePath/venv"
    }

    $reqFile = "$servicePath/requirements.txt"
    if (-not (Test-Path $reqFile)) {
        "fastapi`nuvicorn`nrequests`npydantic`npython-dotenv" | Out-File -FilePath $reqFile -Encoding utf8
    }

    $mainFile = "$servicePath/main.py"
    if (-not (Test-Path $mainFile)) {
        "from fastapi import FastAPI`n`napp = FastAPI()`n`n@app.get('/')`ndef read_root():`n    return {'service': '$service', 'status': 'online'}" | Out-File -FilePath $mainFile -Encoding utf8
    }

    Write-Host "Installing packages for $service..."
    & "$servicePath/venv/Scripts/pip" install -r $reqFile
}

Write-Host "------------------------------------------" -ForegroundColor Yellow
Write-Host "Done! All Python services are configured." -ForegroundColor Green
