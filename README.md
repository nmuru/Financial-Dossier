# Financial Dossier

Financial Dossier analyzes a public company's financial information and produces a structured financial dossier from SEC filings and related company data.

## V1 scope

The current version is a practical first release focused on financial analysis. It supports company-level analysis, progressive streaming of completed analysis phases, rerunning selected phases within the same workspace, and OpenRouter/OpenAI providers through the OpenAI Agents SDK.

The application is designed to gather public financial information, perform research and analysis, and present the results as a structured dossier. Actual runtime, model usage, and cost depend on the company, selected analysis scope, model/provider behavior, retries, and provider pricing or free-tier limits.

## Providers and model input

V1 intentionally exposes the providers implemented by the backend: OpenRouter and OpenAI. The model field is passed through to the selected provider. There is no automatic model fallback in this V1 release. A rate limit, unavailable model, authentication failure, or provider error is surfaced as an analysis failure rather than silently switching to a different model.

## Run control and refresh resilience

A running analysis is independent of the browser tab. The workspace stores work_id and lightweight run metadata in browser local storage; API keys are not stored. On refresh, the frontend reconnects to the backend status endpoint for that work_id, recovers completed artifacts, and resumes the same progressive-results view.

The workspace includes a stop control for the selected analysis run. Completed results remain available and can be inspected while the run is stopped or while later work is still in progress.

## Output retention and runtime mode

Run diagnostics and generated artifacts are written under output-content/{work_id}. The generic runtime_mode setting controls their lifecycle and defaults to evaluation.

- evaluation — retain per-run output for diagnostics, evaluation, and troubleshooting.
- production — allow an explicit UI close/cleanup request to remove that run's output. If the run is still active, the backend cancels it first and removes the folder after cancellation completes.

Set RUNTIME_MODE=production in the backend environment when production retention behavior is desired. Browser refresh does not trigger cleanup.

## Rate limits and failures

The analysis endpoint is an event stream. Backend validation and execution errors are returned as an analysis_failed event so the frontend can display a useful message instead of waiting indefinitely.

This is a V1 demo/evaluation application and not every edge case has been exhaustively tested. If a run encounters an unexpected provider, SEC, repository-access, or processing error, the affected analysis can be rerun from the workspace.

## Financial data and SEC access

Financial Dossier uses public financial information and SEC filing data. SEC access requires an EDGAR identity containing a name and email address.

Set the identity in the terminal before starting the backend, for example:

    set EDGAR_IDENTITY=Your Name your.email@example.com

## Demo

The application includes pre-generated demonstration data under frontend/public/vercel-demo/. Demo content is documentation only and does not consume API credits when viewed.

## Security and workspace model

External company or repository data used during an analysis is handled in a temporary analysis workspace for that run. API keys are supplied per request and are not persisted by the frontend.

## Diagnostics

Resource and agent diagnostics are recorded to support engineering diagnostics and performance investigation. Logs may include runtime samples, phase lifecycle events, provider/model names, trace identifiers, tool-call counts, timing information, retry information, and cancellation events. Prompts and generated content are not intended to be logged as diagnostic content.

## Local development

Start the backend from backend/ with the project's Python environment and start the frontend from frontend/.

The frontend normally expects the backend at:

    http://localhost:8000

The frontend normally runs at:

    http://localhost:3000

Before using the application, provide the required provider/model/API credentials and company information in the UI.

## Run locally on Windows

You can simulate the application on a Windows desktop by cloning the repository and running start.bat. The script creates the Python virtual environment, installs backend dependencies, installs frontend npm dependencies, and starts the FastAPI backend and Next.js frontend.

Before running start.bat, make sure the following are installed:

- Git
- Python 3.11+ with python available on PATH
- Node.js 20.9+ with npm available on PATH

Set the EDGAR identity before starting the application:

    set EDGAR_IDENTITY=Your Name your.email@example.com

Then:

    git clone https://github.com/nmuru/Financial-Dossier.git
    cd Financial-Dossier
    set EDGAR_IDENTITY=Your Name your.email@example.com
    start.bat

The frontend runs on the local Next.js development server, normally at http://localhost:3000. The backend runs on http://localhost:8000.

Windows note: the current start.bat may contain machine-specific paths from the author's development environment. If those paths do not match your machine, use the commands below instead:

    cd backend
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    cd ..\frontend
    npm install

Then start the backend in one terminal:

    cd backend
    set EDGAR_IDENTITY=Your Name your.email@example.com
    .venv\Scripts\python.exe -m uvicorn app.main:app --reload

and the frontend in another:

    cd frontend
    npm run dev
