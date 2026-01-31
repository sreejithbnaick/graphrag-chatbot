#!/bin/bash

# Configuration
CONTAINER_NAME="neo4j-football"

echo "🛑 Stopping Football KG Chatbot Stack..."

# 1. Stop the Streamlit App
echo "⏹ Stopping Streamlit processes..."
pkill -f "streamlit run football_kg_chatbot.py" || echo "Streamlit was not running."

# 2. Stop the Neo4j Container
if [ "$(podman ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "⏹ Stopping Neo4j container: ${CONTAINER_NAME}..."
    podman stop ${CONTAINER_NAME}
else
    echo "✅ Neo4j container is already stopped or doesn't exist."
fi

3. Optional: Stop Podman Machine
# Comment the following lines if you dont want to shut down the entire virtual machine as well.
echo "⏹ Stopping Podman machine..."
podman machine stop

echo "✨ All services stopped successfully."
