#!/bin/bash

set -e

APP_DIR="$HOME/SDLC-ReverseEngineer-v2"
BACKEND="$APP_DIR/backend"
FRONTEND="$APP_DIR/frontend"

export DEBUG_AGENT=true

echo "=== Starting FastAPI ==="
cd "$BACKEND"
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "=== Starting Next.js ==="
cd "$FRONTEND"
npm run dev -- --hostname 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "FastAPI: http://0.0.0.0:8000"
echo "Next.js: http://0.0.0.0:3000"

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' EXIT

wait