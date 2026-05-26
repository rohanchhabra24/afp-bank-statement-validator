#!/bin/bash
echo "Starting AFP Validator Backend..."
# Kill any existing uvicorn process
pkill -f uvicorn
# Start backend in background
uvicorn backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Streamlit Frontend..."
streamlit run frontend_streamlit/app.py

# When streamlit is killed, kill backend
kill $BACKEND_PID
