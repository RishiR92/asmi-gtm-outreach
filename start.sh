#!/bin/bash
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║      Cold Outreach System v1.0       ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found."
    echo "Install from: https://www.python.org/downloads/"
    exit 1
fi

# Force ARM64 Python execution on Apple Silicon Macs
PYTHON_CMD="python3"
if [[ $(uname -m) == "arm64" ]]; then
    PYTHON_CMD="arch -arm64 python3"
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $PYTHON_VERSION"

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is required but not found."
    echo "Install from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "Node:   $NODE_VERSION"
echo ""

# Get script directory (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create .env if missing
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    cp "$SCRIPT_DIR/backend/.env.example" "$SCRIPT_DIR/backend/.env"
    echo "✓ Created backend/.env from .env.example"
    echo "  → Open backend/.env and fill in your Gmail credentials before sending emails."
    echo ""
fi

# Backend setup
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
fi

source venv/bin/activate
echo "Installing backend dependencies..."
pip install -q -r requirements.txt --upgrade
echo "✓ Backend dependencies installed"
echo ""

echo "Starting backend on http://localhost:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to boot
sleep 2

# Frontend setup
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (first run — takes ~30s)..."
    npm install
    echo "✓ Frontend dependencies installed"
fi

echo ""
echo "Starting frontend on http://localhost:3001 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "════════════════════════════════════════"
echo "  Cold Outreach System is running!"
echo ""
echo "  Frontend: http://localhost:3001"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services."
echo "════════════════════════════════════════"
echo ""

cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    # Also kill any child processes
    pkill -P $BACKEND_PID 2>/dev/null || true
    pkill -P $FRONTEND_PID 2>/dev/null || true
    echo "Done. Goodbye!"
    exit 0
}

trap cleanup INT TERM
wait
