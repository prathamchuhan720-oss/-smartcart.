@echo off
title SmartCart E-Commerce & Admin Dashboard
color 0b

echo =========================================================
echo    SMARTCART - E-COMMERCE BACKEND & ADMIN DASHBOARD
echo =========================================================
echo.
echo Starting SmartCart development server...
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in %~dp0backend\venv
    pause
    exit /b 1
)

echo Activating Python Virtual Environment...
call venv\Scripts\activate.bat

echo Checking and applying database migrations...
python manage.py migrate --no-input

echo Launching browser to http://127.0.0.1:8000/ ...
start "" "http://127.0.0.1:8000/"

echo Starting Django Development Server on port 8000...
echo.
echo Website URL:       http://127.0.0.1:8000/
echo Swagger API Docs:  http://127.0.0.1:8000/api/docs/
echo Admin Panel:       http://127.0.0.1:8000/admin/
echo.
echo Pre-seeded Login Credentials:
echo   - Admin User:    admin@smartcart.com    (Password: Admin@12345)
echo   - Customer User: customer@smartcart.com (Password: Customer@12345)
echo.
echo [Press Ctrl+C to stop the server at any time]
echo =========================================================
python manage.py runserver 0.0.0.0:8000
pause
