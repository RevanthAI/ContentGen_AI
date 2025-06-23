#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Start the ADK API server in the background.
# It will listen on an internal-only port (8001).
echo "Starting ADK API server in the background..."
adk api_server &

# Wait a few seconds to ensure the server is ready before Gradio starts.
sleep 5

# Start the Gradio web server in the foreground.
# This will be the main process that keeps the container running.
# It listens on the port specified by the PORT environment variable (default 8080).
echo "Starting Gradio server in the foreground..."
python main.py