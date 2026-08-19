@echo off
setlocal enabledelayedexpansion

echo === Checking prerequisites ===

:: Check Python 3.10+
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo OK Python %PYTHON_VER%

:: Check Node.js 18+
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Install from https://nodejs.org
    exit /b 1
)
for /f "tokens=1" %%v in ('node --version') do set NODE_VER=%%v
echo OK Node.js %NODE_VER%

:: Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm not found
    exit /b 1
)
for /f "tokens=1" %%v in ('npm --version') do set NPM_VER=%%v
echo OK npm %NPM_VER%
echo.

:: Database — default to SQLite
if not defined DATABASE_URL set DATABASE_URL=sqlite:///./verizon_credit.db
echo Database: %DATABASE_URL%

:: Find available port (Windows)
set BACKEND_PORT=9000
:find_backend_port
netstat -an | find ":%BACKEND_PORT% " >nul 2>&1
if not errorlevel 1 (
    echo Port %BACKEND_PORT% in use, trying next...
    set /a BACKEND_PORT+=1
    goto find_backend_port
)

set FRONTEND_PORT=5173
:find_frontend_port
netstat -an | find ":%FRONTEND_PORT% " >nul 2>&1
if not errorlevel 1 (
    echo Port %FRONTEND_PORT% in use, trying next...
    set /a FRONTEND_PORT+=1
    goto find_frontend_port
)

:: Backend setup
set BACKEND_DIR=backend
echo.
echo === Setting up backend ===
cd %BACKEND_DIR%

:: Create virtual environment
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies (NOT pip install -e .)
echo Installing backend dependencies...
if exist "pyproject.toml" (
    pip install . -q
)

:: Initialize database
echo Initializing database...
python -m app.database

:: Run seed data
echo Loading seed data...
python -m app.seed

:: Update .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env >nul 2>&1
)

:: Start backend
echo Starting backend on http://localhost:%BACKEND_PORT%
start "" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% > backend.log 2>&1"

:: Wait a moment for backend to start, then capture PID
timeout /t 1 /nobreak >nul

:: Save backend PID (find most recent python.exe running uvicorn)
for /f "skip=1 tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" /NH') do (
    echo %%p > ..\pids.txt
    goto backend_started
)
:backend_started

cd ..

:: Frontend setup
set FRONTEND_DIR=frontend
echo.
echo === Setting up frontend ===
cd %FRONTEND_DIR%

:: Install dependencies
echo Installing frontend dependencies...
call npm install -q

:: Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env >nul 2>&1
)

:: Update frontend .env with backend URL
powershell -Command "(Get-Content .env) -replace 'VITE_API_URL=.*', 'VITE_API_URL=http://localhost:%BACKEND_PORT%' | Set-Content .env" 2>nul

:: Start frontend
echo Starting frontend on http://localhost:%FRONTEND_PORT%
start "" cmd /c "npm run dev -- --port %FRONTEND_PORT% > frontend.log 2>&1"

:: Wait a moment for frontend to start, then capture PID
timeout /t 1 /nobreak >nul

:: Save frontend PID (find most recent node.exe)
for /f "skip=1 tokens=2" %%p in ('tasklist /FI "IMAGENAME eq node.exe" /NH') do (
    echo %%p >> ..\pids.txt
    goto frontend_started
)
:frontend_started

cd ..

:: Update shared_config.json with ports
if exist "shared_config.json" (
    python -c "import json; cfg = json.load(open('shared_config.json')); cfg.setdefault('ports', {})['backend'] = %BACKEND_PORT%; cfg['ports']['frontend_web'] = %FRONTEND_PORT%; json.dump(cfg, open('shared_config.json', 'w'), indent=2)" 2>nul
)

:: Wait for services to be ready
echo.
echo Waiting for services to start...
timeout /t 3 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Verizon Customer Credit Platform v1.0                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo === Services Running ===
echo   Backend API:    http://localhost:%BACKEND_PORT%
echo   API Docs:       http://localhost:%BACKEND_PORT%/docs
echo   Frontend Web:   http://localhost:%FRONTEND_PORT%
echo   Health Check:   http://localhost:%BACKEND_PORT%/health
echo.
echo === Default Credentials ===
echo   Analyst:        analyst@example.com / password123
echo   CSM:            csm@example.com / password123
echo   Manager:        manager@example.com / password123
echo   VP Sales:       vp@example.com / password123
echo.
echo Press Ctrl+C to stop, or run stop.bat
pause
