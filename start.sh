#!/bin/bash
# start.sh — Start the Verizon Customer Credit Platform (backend + frontend)
set -e
trap 'echo "Shutting down..."; [ -f .pids ] && while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < .pids; rm -f .pids; exit 0' SIGINT SIGTERM

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Portable sed (macOS + Linux)
portable_sed() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Port detection
find_available_port() {
    local port=$1
    while lsof -iTCP:$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        echo "Port $port in use, trying $((port+1))..." >&2
        port=$((port+1))
    done
    echo $port
}

# === Prerequisite checks ===
check_prerequisites() {
    local errors=0
    echo "=== Checking prerequisites ==="

    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
            echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Python $PYTHON_VERSION"
        fi
    else
        echo "❌ Python 3 not found. Install from https://python.org"
        errors=$((errors+1))
    fi

    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        if [ "$NODE_MAJOR" -lt 18 ]; then
            echo "❌ Node.js 18+ required (found $NODE_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Node.js $NODE_VERSION"
        fi
    else
        echo "❌ Node.js not found. Install from https://nodejs.org"
        errors=$((errors+1))
    fi

    if ! command -v npm &>/dev/null; then
        echo "❌ npm not found"
        errors=$((errors+1))
    else
        echo "✓ npm $(npm --version)"
    fi

    if [ $errors -gt 0 ]; then
        echo ""
        echo "❌ $errors prerequisite(s) missing. Please install them and retry."
        exit 1
    fi
    echo ""
}

check_prerequisites

# === Backend Setup ===
BACKEND_DIR="backend"
echo "=== Setting up backend ==="
cd "$BACKEND_DIR"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (NOT -e .)
echo "Installing backend dependencies..."
if [ -f "pyproject.toml" ]; then
    pip install . -q
fi

# Initialize database
echo "Initializing database..."
export DATABASE_URL="${DATABASE_URL:-sqlite:///./verizon_credit.db}"
python3 -m app.database

# Run seed data
echo "Loading seed data..."
python3 -m app.seed

# Detect available ports
BACKEND_PORT=$(find_available_port 9000)
export API_PORT=$BACKEND_PORT

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
fi

# Update .env with detected port
if [ -f ".env" ]; then
    portable_sed "s/API_PORT=.*/API_PORT=$BACKEND_PORT/" .env
fi

# Start backend
echo "Starting backend on http://localhost:$BACKEND_PORT"
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# === Frontend Setup ===
FRONTEND_DIR="frontend"
echo ""
echo "=== Setting up frontend ==="
cd "$FRONTEND_DIR"

# Install dependencies
echo "Installing frontend dependencies..."
npm install -q

# Detect available port
FRONTEND_PORT=$(find_available_port 5173)

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
fi

# Update .env with backend URL
if [ -f ".env" ]; then
    portable_sed "s|VITE_API_URL=.*|VITE_API_URL=http://localhost:$BACKEND_PORT|" .env
else
    echo "VITE_API_URL=http://localhost:$BACKEND_PORT" > .env
fi

# Start frontend
echo "Starting frontend on http://localhost:$FRONTEND_PORT"
npm run dev -- --port $FRONTEND_PORT > frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# === Update shared config ===
if [ -f "shared_config.json" ]; then
    python3 -c "
import json, sys
try:
    with open('shared_config.json') as f: 
        cfg = json.load(f)
    cfg.setdefault('ports', {})
    cfg['ports']['backend'] = int(sys.argv[1])
    cfg['ports']['frontend_web'] = int(sys.argv[2])
    with open('shared_config.json', 'w') as f: 
        json.dump(cfg, f, indent=2)
except:
    pass
" "$BACKEND_PORT" "$FRONTEND_PORT" 2>/dev/null || true
fi

# Update backend CORS
if [ -f "$BACKEND_DIR/.env" ]; then
    portable_sed "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:$FRONTEND_PORT|" "$BACKEND_DIR/.env" 2>/dev/null || true
fi

# Save PIDs
echo "$BACKEND_PID" > .pids
echo "$FRONTEND_PID" >> .pids

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 3

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Verizon Customer Credit Platform v1.0                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "=== Services Running ==="
echo "  Backend API:    http://localhost:$BACKEND_PORT"
echo "  API Docs:       http://localhost:$BACKEND_PORT/docs"
echo "  Frontend Web:   http://localhost:$FRONTEND_PORT"
echo "  Health Check:   http://localhost:$BACKEND_PORT/health"
echo ""
echo "=== Default Credentials ==="
echo "  Analyst:        analyst@example.com / password123"
echo "  CSM:            csm@example.com / password123"
echo "  Manager:        manager@example.com / password123"
echo "  VP Sales:       vp@example.com / password123"
echo ""
echo "Press Ctrl+C to stop all services"
wait
