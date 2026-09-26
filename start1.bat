@echo off
setlocal
set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"
set "VENV=%ROOT%.venv"
set "DEBUG_AGENT=true"
set "PATH=%APPDATA%\npm;%PATH%"

if not exist "%VENV%\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -3 -m venv "%VENV%"
  if errorlevel 1 exit /b 1
)

echo Installing/updating Python dependencies...
"%VENV%\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 exit /b 1

if not exist "%FRONTEND%\package.json" (
  echo ERROR: frontend\package.json is missing from this branch.
  echo The FastAPI backend can be started, but the Next.js frontend cannot.
  exit /b 1
)

if not exist "%FRONTEND%\node_modules" (
  pushd "%FRONTEND%"
  call npm install
  if errorlevel 1 ( popd & exit /b 1 )
  popd
)

start "Financial-Dossier FastAPI" cmd /k "cd /d "%ROOT%" && set DEBUG_AGENT=true && "%VENV%\Scripts\python.exe" -m uvicorn app.main:app --reload"
start "Financial-Dossier Next.js" cmd /k "cd /d "%FRONTEND%" && npm run dev"
echo Servers launched.
endlocal
