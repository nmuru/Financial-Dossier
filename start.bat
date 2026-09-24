@echo off

set "BACKEND=C:\ReverseEngineer-SDLC-v2\ReverseEngineer-SDLC\SDLC-Reverse-Engineer\backend"
set "FRONTEND=C:\ReverseEngineer-SDLC-v2\ReverseEngineer-SDLC\SDLC-Reverse-Engineer\frontend"

set "DEBUG_AGENT=true"
set "PATH=C:\Users\n_mur\AppData\Roaming\npm;%PATH%"

cd /d "%BACKEND%"

if not exist .venv (
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

cd /d "%FRONTEND%"

if not exist node_modules (
    npm install
)

start "FastAPI" cmd /k "cd /d "%BACKEND%" && set DEBUG_AGENT=true && set PATH=C:\Users\n_mur\AppData\Roaming\npm;%%PATH%% && .venv\Scripts\python.exe -m uvicorn app.main:app --reload"

start "Next.js" cmd /k "cd /d "%FRONTEND%" && npm run dev"