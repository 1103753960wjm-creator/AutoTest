@echo off
setlocal

echo ========================================
echo   [TestHub] Starting Services...
echo ========================================

:: 1. Cleanup ports (8000, 3000) using a simple PowerShell command
echo [1/3] Cleaning up ports 8000 and 3000...
powershell -Command "$p=Get-NetTCPConnection -LocalPort 8000,3000 -ErrorAction 0; if($p){$p.OwningProcess | Stop-Process -Force -ErrorAction 0}"

:: 2. Start Backend (Django)
echo [2/3] Starting Backend (Django)...
set DEBUG=
start /B "" ".\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000 > backend.log 2>&1
echo      - Backend log redirected to: backend.log

:: 3. Start Frontend (Vite)
echo [3/3] Starting Frontend (Vite)...
cd frontend
npm run dev

pause
