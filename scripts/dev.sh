#!/bin/bash
# Start both backend and frontend dev servers
echo "Starting Healthcare Price Transparency dev servers..."

# Start backend
cd "$(dirname "$0")/../backend"
echo "Starting FastAPI backend on port 8000..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd "$(dirname "$0")/../frontend"
echo "Starting React frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

# Handle cleanup
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo ""
echo "Backend:  http://localhost:8000/docs"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."

wait
