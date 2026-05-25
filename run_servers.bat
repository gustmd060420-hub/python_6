@echo off
echo ===== Py-Pass Server Start =====

echo Installing packages...
pip install fastapi uvicorn requests pandas --quiet

echo Starting servers...

start "Central Server :8000" cmd /k "cd /d C:\Users\bob\AndroidStudioProjects\ParkingApp\smart-parking-system\app\central_server && python central_server.py"

timeout /t 2 /nobreak > nul

start "Mock PG :9000" cmd /k "cd /d C:\Users\bob\AndroidStudioProjects\ParkingApp\smart-parking-system\app\mock_pg && python mock_pg_server.py"

echo.
echo Central Server : http://localhost:8000
echo Mock PG Server : http://localhost:9000
echo API Docs       : http://localhost:8000/docs
echo =======================================
pause
