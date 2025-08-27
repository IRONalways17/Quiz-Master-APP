#!/bin/bash

echo "Quiz Master V2 - Installation and Setup Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check and install system dependencies
print_status "Checking system dependencies..."

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 not found. Attempting to install..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv
fi

# Check if node is available
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Attempting to install..."
    sudo apt install -y nodejs npm
fi

# Check if redis-server is available
if ! command -v redis-server &> /dev/null; then
    print_warning "Redis not found. Attempting to install..."
    sudo apt install -y redis-server
fi

print_success "System dependencies check completed"

# Setup backend
print_status "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Failed to install Python dependencies"
    print_status "Trying alternative installation method..."
    pip3 install --user -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success "Created .env file from env.example"
    fi
fi

cd ..

# Setup frontend
print_status "Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install frontend dependencies"
        cd ..
        exit 1
    fi
fi

cd ..

# Start Redis if not running
print_status "Starting Redis server..."
if ! pgrep redis-server > /dev/null; then
    redis-server --daemonize yes
    sleep 2
fi

# Start backend
print_status "Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || true
python3 run.py &
BACKEND_PID=$!
cd ..

sleep 5

# Start frontend
print_status "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

print_success "Application started!"
print_status "Backend: http://localhost:5000"
print_status "Frontend: http://localhost:5175 (when available)"
print_status "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    print_status "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "python.*run.py" 2>/dev/null || true
    pkill -f "npm.*dev" 2>/dev/null || true
    print_success "Services stopped"
    exit 0
}

trap cleanup INT

# Wait for processes
wait
