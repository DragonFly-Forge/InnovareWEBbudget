@echo off
echo [1/3] Starting Flask Server...
start cmd /k "python app.py"

echo [2/3] Waiting for server to wake up...
timeout /t 5

echo [3/3] Seeding March Income Data...
python test_income.py

echo.
echo ==========================================
echo DEMO READY: Refresh http://127.0.0.1:5000/api/smart-summary/1
echo ==========================================
pause