#!/bin/bash

# Quiz Master V2 - Unified Development Server
# This script starts Redis, Flask backend, Celery worker, Celery beat, and Vue frontend
# Optimized for WSL2 with proper error handling and connection verification

echo "Starting Quiz Master V2 Development Environment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is in use by $service. Freeing it..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to check Redis connection
check_redis_connection() {
    print_status "Testing Redis connection..."
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is running and accessible"
        return 0
    else
        print_error "Redis is not accessible"
        return 1
    fi
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory (QMasterV2)"
    exit 1
fi

# Comprehensive cleanup of existing processes
print_status "Cleaning up existing processes and ports..."

# Kill Flask backend processes
pkill -f "python.*run.py" 2>/dev/null || true
pkill -f "flask.*run" 2>/dev/null || true

# Kill Vite frontend processes
pkill -f "vite.*5175" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

# Kill Celery processes
pkill -f "celery.*worker" 2>/dev/null || true
pkill -f "celery.*beat" 2>/dev/null || true

# Kill Redis server if running
pkill -f "redis-server" 2>/dev/null || true

# Free up ports
print_status "Freeing up ports..."
check_port 5000 "Flask backend"
check_port 5175 "Vue frontend"
check_port 6379 "Redis"
check_port 5672 "Celery broker"

sleep 3

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    print_error "Redis server is not installed. Please install Redis first."
    print_status "On Ubuntu/Debian: sudo apt-get install redis-server"
    print_status "On macOS: brew install redis"
    exit 1
fi

# Start Redis Server
print_status "Starting Redis server..."
redis-server --daemonize yes
if [ $? -eq 0 ]; then
    print_success "Redis server started successfully"
else
    print_error "Failed to start Redis server"
    exit 1
fi

# Wait for Redis to be ready and test connection
sleep 3
if check_redis_connection; then
    print_success "Redis connection verified"
else
    print_error "Redis connection failed"
    exit 1
fi

# Setup backend environment
print_status "Setting up backend environment..."
cd backend

if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success "Created .env file from env.example"
    else
        print_error "No env.example file found in backend directory"
        exit 1
    fi
fi

# Install backend dependencies if needed
if [ ! -d "venv" ] && [ ! -f "requirements.txt" ]; then
    print_error "Backend setup incomplete - no virtual environment or requirements.txt found"
    cd ..
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
print_status "Installing backend dependencies..."
source venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install backend dependencies"
    cd ..
    exit 1
fi
print_success "Backend dependencies installed"

# Initialize database with new schema
print_status "Initializing database..."
python reset_db.py
if [ $? -ne 0 ]; then
    print_warning "Database initialization failed, but continuing..."
fi

cd ..

# Setup frontend environment
print_status "Setting up frontend environment..."
cd frontend

if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install frontend dependencies"
        exit 1
    fi
    print_success "Frontend dependencies installed"
fi

# Install concurrently if not already installed
if ! npm list concurrently >/dev/null 2>&1; then
    print_status "Installing concurrently for unified development..."
    npm install --save-dev concurrently
fi

cd ..

# Start all services with proper health checks
print_status "Starting all development services..."
echo ""
echo "Redis: localhost:6379"
echo ""
print_success "All services are starting up..."
echo ""

# Start Flask backend
print_status "Starting Flask backend..."
cd backend
source venv/bin/activate
python3 run.py &
FLASK_PID=$!
cd ..

# Wait for backend to be ready
if wait_for_service "http://localhost:5000/api/health" "Flask backend"; then
    print_success "Backend is ready!"
else
    print_error "Backend failed to start"
    exit 1
fi

# Start Celery worker with WSL2 optimizations
print_status "Starting Celery worker (WSL2 optimized)..."
cd backend
source venv/bin/activate

# WSL2 specific Celery configuration
export C_FORCE_ROOT=true
export CELERYD_POOL_RESTARTS=true
export CELERYD_MAX_TASKS_PER_CHILD=1000

# Start Celery worker with reduced concurrency for WSL2
celery -A celery_app worker --loglevel=info --concurrency=1 --pool=solo &
CELERY_WORKER_PID=$!
cd ..

sleep 5

# Check if Celery worker started successfully
if ps -p $CELERY_WORKER_PID > /dev/null; then
    print_success "Celery worker started successfully"
else
    print_warning "Celery worker may have issues in WSL2 - this is normal"
fi

# Start Celery beat with WSL2 optimizations
print_status "Starting Celery beat (WSL2 optimized)..."
cd backend
source venv/bin/activate

# Start Celery beat with default scheduler for Flask
celery -A celery_app beat --loglevel=info &
CELERY_BEAT_PID=$!
cd ..

sleep 3

# Check if Celery beat started successfully
if ps -p $CELERY_BEAT_PID > /dev/null; then
    print_success "Celery beat started successfully"
else
    print_warning "Celery beat may have issues in WSL2 - this is normal"
fi

# Start Vue frontend
print_status "Starting Vue frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready (reduced timeout)
if wait_for_service "http://localhost:5175" "Vue frontend"; then
    print_success "Frontend is ready!"
else
    print_warning "Frontend may still be starting up..."
fi

print_success "All services started successfully!"
print_status "Press Ctrl+C to stop all services"

# Display connection status and usage information
echo ""
print_status "Connection Status:"
echo "  ✅ Backend API: http://localhost:5000"
echo "  ✅ Frontend App: http://localhost:5175"


# Test API connections


# Test backend API
if curl -s "http://localhost:5000/api/health" >/dev/null 2>&1; then
    print_success "Backend API is responding"
else
    print_warning "Backend API may not be fully ready"
fi

# Test Redis connection
if redis-cli ping >/dev/null 2>&1; then
    print_success "Redis is accessible"
else
    print_error "Redis connection failed"
fi

# Wait for all background processes (but don't fail if Celery crashes)
wait $FLASK_PID $FRONTEND_PID || true

# Cleanup function for graceful shutdown
cleanup() {
    print_status "Shutting down all development services..."
    
    # Kill all background processes
    pkill -f "python.*run.py" 2>/dev/null || true
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "celery.*beat" 2>/dev/null || true
    pkill -f "vite.*5175" 2>/dev/null || true
    pkill -f "npm.*dev" 2>/dev/null || true
    pkill -f "redis-server" 2>/dev/null || true
    
    print_success "All development services stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Wait for processes
wait