# # Start RAG API Server
# Write-Host "Starting RAG API Server..." -ForegroundColor Green
# Write-Host ""

# # Check if virtual environment exists
# if (Test-Path ".venv\Scripts\Activate.ps1") {
#     Write-Host "Activating virtual environment..." -ForegroundColor Yellow
#     & .venv\Scripts\Activate.ps1
# }

# # Check if python-dotenv is installed
# $dotenvInstalled = python -c "import dotenv" 2>$null
# if ($LASTEXITCODE -ne 0) {
#     Write-Host "Installing required packages..." -ForegroundColor Yellow
#     pip install -q python-dotenv fastapi uvicorn
# }

Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Open your browser and navigate to http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
