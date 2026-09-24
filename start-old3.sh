#!/bin/bash

set -e

APP_DIR="$HOME/SDLC-ReverseEngineer-v2"
BACKEND="$APP_DIR/backend"
FRONTEND="$APP_DIR/frontend"

MIN_NODE_MAJOR=20
MIN_NODE_MINOR=9

echo "=========================================="
echo " SDLC ReverseEngineer production startup"
echo "=========================================="

# --------------------------------------------------
# 1. Check Node.js version
# --------------------------------------------------

if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: Node.js is not installed."
    exit 1
fi

NODE_VERSION=$(node --version | sed 's/^v//')
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
NODE_MINOR=$(echo "$NODE_VERSION" | cut -d. -f2)

echo "Node.js version: $NODE_VERSION"

if [ "$NODE_MAJOR" -lt "$MIN_NODE_MAJOR" ] || \
   { [ "$NODE_MAJOR" -eq "$MIN_NODE_MAJOR" ] && [ "$NODE_MINOR" -lt "$MIN_NODE_MINOR" ]; }; then
    echo "ERROR: Node.js >= 20.9.0 is required."
    echo "Installed version: $NODE_VERSION"
    exit 1
fi

echo "Node.js version check: OK"

# --------------------------------------------------
# 2. Verify application directories
# --------------------------------------------------

if [ ! -d "$BACKEND" ]; then
    echo "ERROR: Backend directory not found: $BACKEND"
    exit 1
fi

if [ ! -d "$FRONTEND" ]; then
    echo "ERROR: Frontend directory not found: $FRONTEND"
    exit 1
fi

if [ ! -x "$BACKEND/.venv/bin/python" ]; then
    echo "ERROR: Backend virtual environment not found."
    echo "Expected: $BACKEND/.venv/bin/python"
    exit 1
fi

# --------------------------------------------------
# 3. Build Next.js production application
# --------------------------------------------------

echo ""
echo "=== Building Next.js production application ==="

cd "$FRONTEND"

npm run build

echo "Next.js production build: OK"

# --------------------------------------------------
# 4. Create FastAPI systemd service
# --------------------------------------------------

echo ""
echo "=== Creating FastAPI systemd service ==="

sudo tee /etc/systemd/system/sdlc-backend.service > /dev/null <<EOF
[Unit]
Description=SDLC Reverse Engineer FastAPI Backend
After=network.target

[Service]
User=ec2-user
WorkingDirectory=$BACKEND
Environment="DEBUG_AGENT=true"
ExecStart=$BACKEND/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# --------------------------------------------------
# 5. Create Next.js production systemd service
# --------------------------------------------------

echo ""
echo "=== Creating Next.js systemd service ==="

sudo tee /etc/systemd/system/sdlc-frontend.service > /dev/null <<EOF
[Unit]
Description=SDLC Reverse Engineer Next.js Frontend
After=network.target sdlc-backend.service

[Service]
User=ec2-user
WorkingDirectory=$FRONTEND
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run start -- --hostname 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# --------------------------------------------------
# 6. Reload systemd
# --------------------------------------------------

echo ""
echo "=== Reloading systemd ==="

sudo systemctl daemon-reload

# --------------------------------------------------
# 7. Enable services at boot
# --------------------------------------------------

echo ""
echo "=== Enabling services at boot ==="

sudo systemctl enable sdlc-backend
sudo systemctl enable sdlc-frontend

# --------------------------------------------------
# 8. Start services
# --------------------------------------------------

echo ""
echo "=== Starting backend ==="

sudo systemctl restart sdlc-backend

echo ""
echo "=== Starting frontend ==="

sudo systemctl restart sdlc-frontend

# --------------------------------------------------
# 9. Show status
# --------------------------------------------------

echo ""
echo "=== Backend status ==="

sudo systemctl --no-pager --full status sdlc-backend

echo ""
echo "=== Frontend status ==="

sudo systemctl --no-pager --full status sdlc-frontend

# --------------------------------------------------
# 10. Done
# --------------------------------------------------

echo ""
echo "=========================================="
echo " SDLC application is running"
echo "=========================================="
echo ""
echo "Frontend:"
echo "http://3.87.44.100:3000"
echo ""
echo "Backend:"
echo "http://3.87.44.100:8000"
echo ""
echo "Backend logs:"
echo "sudo journalctl -u sdlc-backend -f"
echo ""
echo "Frontend logs:"
echo "sudo journalctl -u sdlc-frontend -f"
echo ""