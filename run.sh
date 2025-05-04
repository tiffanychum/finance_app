#!/bin/bash
# Run script for the Finance App

# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if required tools are installed
if ! command_exists node; then
  echo "Error: Node.js is not installed. Please install it to continue."
  exit 1
fi

if ! command_exists npm; then
  echo "Error: npm is not installed. Please install it to continue."
  exit 1
fi

if ! command_exists python; then
  echo "Error: Python is not installed. Please install it to continue."
  exit 1
fi

# Check for required Python packages
if ! command_exists pip; then
  echo "Error: pip is not installed. Please install it to continue."
  exit 1
fi

# Check if the virtual environment exists
if [ ! -d "backend/.venv" ]; then
  echo "Creating Python virtual environment..."
  cd backend
  python -m venv .venv
  cd ..
fi

# Activate the virtual environment and install dependencies
echo "Installing/updating Python dependencies..."
cd backend
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
pip install fastapi uvicorn yahooquery
cd ..

# Install frontend dependencies if needed
echo "Installing/updating frontend dependencies..."
cd frontend
npm install
cd ..

# Start both services
echo "Starting services..."

# Start backend in the background
echo "Starting backend API server..."
cd backend
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
python main.py &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Function to clean up on exit
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

echo "Services are running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Press Ctrl+C to stop all services"

# Wait for user to press Ctrl+C
wait 