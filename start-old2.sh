#!/bin/bash

set -e

APP_DIR="$HOME/SDLC-ReverseEngineer-v2"
BACKEND="$APP_DIR/backend"
FRONTEND="$APP_DIR/frontend"

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

echo "=== Creating Next.js systemd service ==="

sudo tee /etc/systemd/system/sdlc-frontend.service > /dev/null <<EOF
[Unit]
Description=SDLC Reverse Engineer Next.js Frontend
After=network.target sdlc-backend.service

[Service]
User=ec2-user
WorkingDirectory=$FRONTEND
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run dev -- --hostname 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "=== Reloading systemd ==="

sudo systemctl daemon-reload

echo "=== Enabling services at boot ==="

sudo systemctl enable sdlc-backend
sudo systemctl enable sdlc-frontend

echo "=== Restarting services ==="

sudo systemctl restart sdlc-backend
sudo systemctl restart sdlc-frontend

echo "=== Backend status ==="

sudo systemctl status sdlc-backend --no-pager

echo "=== Frontend status ==="

sudo systemctl status sdlc-frontend --no-pager

echo ""
echo "=========================================="
echo "SDLC application services are running."
echo "Frontend: http://3.87.44.100:3000"
echo "Backend:  http://3.87.44.100:8000"
echo "=========================================="
echo ""
echo "Backend logs:"
echo "sudo journalctl -u sdlc-backend -f"
echo ""
echo "Frontend logs:"
echo "sudo journalctl -u sdlc-frontend -f"