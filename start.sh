#!/bin/bash

set -e

# ============================================================
# SDLC ReverseEngineer - Linux / AWS-style startup
#
# Designed for:
#   - AWS EC2 / Lightsail Amazon Linux 2023
#   - Ubuntu
#   - WSL with systemd enabled
#
# Creates two systemd services:
#   sdlc-backend
#   sdlc-frontend
# ============================================================

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$APP_DIR/backend"
FRONTEND="$APP_DIR/frontend"

RUN_USER="$(id -un)"
RUN_GROUP="$(id -gn)"

BACKEND_SERVICE="/etc/systemd/system/sdlc-backend.service"
FRONTEND_SERVICE="/etc/systemd/system/sdlc-frontend.service"

MIN_NODE_MAJOR=20
MIN_NODE_MINOR=9

export DEBUG_AGENT="${DEBUG_AGENT:-true}"

echo "=========================================="
echo " SDLC ReverseEngineer Linux startup"
echo "=========================================="
echo "Application : $APP_DIR"
echo "Linux user  : $RUN_USER"
echo ""

# ------------------------------------------------------------
# 0. Detect Linux distribution / install prerequisites
# ------------------------------------------------------------

if command -v dnf >/dev/null 2>&1; then

    echo "Amazon Linux / dnf detected."

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "OS          : ${PRETTY_NAME:-unknown}"
    fi

    echo ""
    echo "=== Installing AWS/Linux prerequisites ==="

    sudo dnf update -y

    # Amazon Linux 2023 default Node may be 18.x.
    # The application requires >= 20.9, so explicitly install Node 22.
    echo ""
    echo "=== Installing Node.js 22 ==="

    sudo dnf remove -y nodejs npm >/dev/null 2>&1 || true
    sudo dnf install -y nodejs22

    echo "Node.js after installation: $(node --version)"
    echo "npm after installation: $(npm --version)"

    echo ""
    echo "=== Installing Python 3.11 and Git ==="

    sudo dnf install -y git python3.11 python3.11-pip

else
    echo "dnf not detected; using existing system packages."
fi

# ------------------------------------------------------------
# 1. Check systemd
# ------------------------------------------------------------

if ! command -v systemctl >/dev/null 2>&1; then
    echo "ERROR: systemctl is not available."
    exit 1
fi

if ! systemctl is-system-running >/dev/null 2>&1; then
    echo "ERROR: systemd is not running."
    echo "This script requires systemd."
    exit 1
fi

echo "systemd: OK"

# ------------------------------------------------------------
# 2. Select Python
# ------------------------------------------------------------

if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3.11)"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    echo "ERROR: Python 3 is not installed."
    exit 1
fi

echo "Python: $("$PYTHON_BIN" --version)"

# ------------------------------------------------------------
# 3. Check Node.js
# ------------------------------------------------------------

if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: Node.js is not installed."
    echo "Required: Node.js >= ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}"
    exit 1
fi

NODE_BIN="$(command -v node)"
NPM_BIN="$(command -v npm)"

NODE_VERSION=$(node --version | sed 's/^v//')
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
NODE_MINOR=$(echo "$NODE_VERSION" | cut -d. -f2)

echo "Node.js: $NODE_VERSION"
echo "Node path: $NODE_BIN"

if [ "$NODE_MAJOR" -lt "$MIN_NODE_MAJOR" ] || \
   { [ "$NODE_MAJOR" -eq "$MIN_NODE_MAJOR" ] && [ "$NODE_MINOR" -lt "$MIN_NODE_MINOR" ]; }; then
    echo "ERROR: Node.js >= ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0 is required."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm is not installed."
    exit 1
fi

echo "npm: $(npm --version)"
echo "npm path: $NPM_BIN"

# ------------------------------------------------------------
# 4. Verify application directories
# ------------------------------------------------------------

if [ ! -d "$BACKEND" ]; then
    echo "ERROR: Backend directory not found:"
    echo "$BACKEND"
    exit 1
fi

if [ ! -d "$FRONTEND" ]; then
    echo "ERROR: Frontend directory not found:"
    echo "$FRONTEND"
    exit 1
fi

# ------------------------------------------------------------
# 5. Python virtual environment
# ------------------------------------------------------------

if [ ! -x "$BACKEND/.venv/bin/python" ] || \
   ! "$BACKEND/.venv/bin/python" -c "import uvicorn" >/dev/null 2>&1; then

    echo ""
    echo "=== Creating/recreating Python virtual environment ==="

    rm -rf "$BACKEND/.venv"

    "$PYTHON_BIN" -m venv "$BACKEND/.venv"

    "$BACKEND/.venv/bin/python" -m pip install --upgrade pip
    "$BACKEND/.venv/bin/python" -m pip install -r "$BACKEND/requirements.txt"

else
    echo "Python virtual environment: OK"
fi

# ------------------------------------------------------------
# 6. Frontend dependencies
# ------------------------------------------------------------

cd "$FRONTEND"

if [ ! -x "$FRONTEND/node_modules/.bin/next" ] || \
   ! "$FRONTEND/node_modules/.bin/next" --version >/dev/null 2>&1; then

    echo ""
    echo "=== Installing frontend dependencies ==="

    rm -rf "$FRONTEND/node_modules"

    npm ci

else
    echo "Frontend node_modules: OK"
fi

# ------------------------------------------------------------
# 7. Build frontend
# ------------------------------------------------------------

echo ""
echo "=== Building Next.js production application ==="

npm run build -- --webpack

echo "Next.js production build: OK"

# ------------------------------------------------------------
# 8. Create backend systemd service
# ------------------------------------------------------------

echo ""
echo "=== Creating backend systemd service ==="

sudo tee "$BACKEND_SERVICE" > /dev/null <<EOF
[Unit]
Description=SDLC Reverse Engineer FastAPI Backend
After=network.target

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_GROUP
WorkingDirectory=$BACKEND
Environment="DEBUG_AGENT=$DEBUG_AGENT"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$BACKEND/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ------------------------------------------------------------
# 9. Create frontend systemd service
# ------------------------------------------------------------

echo ""
echo "=== Creating frontend systemd service ==="

NODE_DIR="$(dirname "$NODE_BIN")"

sudo tee "$FRONTEND_SERVICE" > /dev/null <<EOF
[Unit]
Description=SDLC Reverse Engineer Next.js Frontend
After=network.target sdlc-backend.service

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_GROUP
WorkingDirectory=$FRONTEND
Environment="NODE_ENV=production"
Environment="NEXT_TELEMETRY_DISABLED=1"
Environment="PATH=$NODE_DIR:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$NPM_BIN run start -- --hostname 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ------------------------------------------------------------
# 10. Reload systemd
# ------------------------------------------------------------

echo ""
echo "=== Reloading systemd ==="

sudo systemctl daemon-reload

# ------------------------------------------------------------
# 11. Enable services
# ------------------------------------------------------------

echo ""
echo "=== Enabling services ==="

sudo systemctl enable sdlc-backend
sudo systemctl enable sdlc-frontend

# ------------------------------------------------------------
# 12. Start backend
# ------------------------------------------------------------

echo ""
echo "=== Starting backend ==="

sudo systemctl restart sdlc-backend

sleep 2

# ------------------------------------------------------------
# 13. Start frontend
# ------------------------------------------------------------

echo ""
echo "=== Starting frontend ==="

sudo systemctl restart sdlc-frontend

sleep 2

# ------------------------------------------------------------
# 14. Show service status
# ------------------------------------------------------------

echo ""
echo "=========================================="
echo " Service status"
echo "=========================================="

echo ""
echo "--- Backend ---"
sudo systemctl --no-pager --full status sdlc-backend || true

echo ""
echo "--- Frontend ---"
sudo systemctl --no-pager --full status sdlc-frontend || true

# ------------------------------------------------------------
# 15. Instructions
# ------------------------------------------------------------

echo ""
echo "=========================================="
echo " SDLC application services are running"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend : http://localhost:8000"
echo ""
echo "Open separate terminals for logs:"
echo ""
echo "  sudo journalctl -u sdlc-backend -f"
echo ""
echo "  sudo journalctl -u sdlc-frontend -f"
echo ""
echo "Service status:"
echo ""
echo "  sudo systemctl status sdlc-backend"
echo "  sudo systemctl status sdlc-frontend"
echo ""
echo "Stop services:"
echo ""
echo "  sudo systemctl stop sdlc-backend sdlc-frontend"
echo ""