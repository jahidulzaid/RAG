#!/bin/bash

# Start RAG API Server
echo "Starting RAG API Server..."
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo ""
echo "Starting server on http://localhost:8000"
echo "Open your browser and navigate to http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
