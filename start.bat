@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo   [TestHub] Starting Services...
echo ========================================

:: 1. Cleanup ports (8000, 3000) using a simple PowerShell command
echo [1/4] Cleaning up ports 8000 and 3000...
powershell -Command "$p=Get-NetTCPConnection -LocalPort 8000,3000 -ErrorAction 0; if($p){$p.OwningProcess | Stop-Process -Force -ErrorAction 0}"

:: 2. Start Backend (Django)
echo [2/4] Starting Backend (Django)...
set DEBUG=
start /B "" ".\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000 > backend.log 2>&1
echo      - Backend log redirected to: backend.log

:: 3. Wait until backend is ready before starting frontend.
echo [3/4] Waiting for Backend on 127.0.0.1:8000...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddSeconds(60); while((Get-Date) -lt $deadline){ $client=[Net.Sockets.TcpClient]::new(); try { $task=$client.ConnectAsync('127.0.0.1',8000); if($task.Wait(1000) -and $client.Connected){ $client.Dispose(); exit 0 } } catch {} finally { if($client){$client.Dispose()} }; Start-Sleep -Milliseconds 500 }; exit 1"
if errorlevel 1 (
  echo      - Backend did not become ready within 60 seconds.
  echo      - Please check backend.log for the real error.
  pause
  exit /b 1
)
echo      - Backend is ready.

:: 4. Start Frontend (Vite)
echo [4/4] Starting Frontend (Vite)...
cd frontend
npm run dev

pause
