Write-Host "Starting all space-data SOA services..." -ForegroundColor Cyan

# 1. Satellite Tracker (Python) - Port 8080
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services\satellite-tracker-py; .\venv\Scripts\activate; uvicorn main:app --reload --port 8080"

# 2. Space Weather (Python) - Port 8001
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services\space-weather; .\venv\Scripts\activate; uvicorn main:app --reload --port 8001"

# 3. Astro Objects (Python) - Port 8002
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services\astro-objects; .\venv\Scripts\activate; uvicorn main:app --reload --port 8002"

# 4. Mission Data (Python) - Port 8003
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services\mission-data; .\venv\Scripts\activate; uvicorn main:app --reload --port 8003"

# 5. User Service (Python) - Port 8004
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services\user-service; .\venv\Scripts\activate; uvicorn main:app --reload --port 8004"

# 6. Frontend (Python HTTP Server) - Port 3000
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python serve.py"

Write-Host "All services have been started in separate windows!" -ForegroundColor Green
Write-Host "Ports map:"
Write-Host "8080 - Satellite Tracker (Python)"
Write-Host "8001 - Space Weather"
Write-Host "8002 - Astro Objects"
Write-Host "8003 - Mission Data"
Write-Host "8004 - User Service"
Write-Host "3000 - Frontend (Web UI)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Open http://localhost:3000 in your browser!" -ForegroundColor Cyan
