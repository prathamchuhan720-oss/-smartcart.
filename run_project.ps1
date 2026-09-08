# SmartCart 1-Click PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "SmartCart E-Commerce & Admin Dashboard"
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "   SMARTCART - E-COMMERCE BACKEND & ADMIN DASHBOARD" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$scriptDir\backend"

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Checking and applying database migrations..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" manage.py migrate --no-input

Write-Host "Launching web browser to http://127.0.0.1:8000/ ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000/"

Write-Host ""
Write-Host "Website URL:       http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Swagger API Docs:  http://127.0.0.1:8000/api/docs/" -ForegroundColor Green
Write-Host "Admin Panel:       http://127.0.0.1:8000/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Pre-seeded Login Credentials:" -ForegroundColor Magenta
Write-Host "  - Admin User:    admin@smartcart.com    (Password: Admin@12345)"
Write-Host "  - Customer User: customer@smartcart.com (Password: Customer@12345)"
Write-Host ""
Write-Host "[Press Ctrl+C to stop the server at any time]" -ForegroundColor DarkGray
Write-Host "=========================================================" -ForegroundColor Cyan

& ".\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
