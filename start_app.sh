#!/bin/bash

# Configuration
CONTAINER_NAME="neo4j-football"
VENV_PATH="./venv"
STREAMLIT_APP="football_kg_chatbot.py"

echo "🚀 Starting Football KG Chatbot Stack..."

# 1. Check if Podman Machine is running
if [[ $(podman machine inspect --format '{{.State}}' default 2>/dev/null) != "running" ]]; then
    echo "📦 Starting Podman machine..."
    podman machine start
else
    echo "✅ Podman machine is already running."
fi

# 2. Check and Start Neo4j Container
if [ "$(podman ps -aq -f name=${CONTAINER_NAME})" ]; then
    if [ "$(podman ps -q -f name=${CONTAINER_NAME})" ]; then
        echo "✅ Neo4j container '${CONTAINER_NAME}' is already running."
    else
        echo "🔄 Starting existing Neo4j container: ${CONTAINER_NAME}..."
        podman start ${CONTAINER_NAME}
    fi
else
    echo "✨ Creating and starting new Neo4j container: ${CONTAINER_NAME}..."
    podman run -d \
      --name ${CONTAINER_NAME} \
      -p 7474:7474 -p 7687:7687 \
      -e NEO4J_AUTH=neo4j/password123 \
      -e NEO4J_PLUGINS='["apoc", "genai"]' \
      -e NEO4J_dbms_security_procedures_unrestricted=apoc.*,genai.* \
      -e NEO4J_dbms_security_procedures_allowlist=apoc.*,genai.* \
      neo4j:5
fi

# 3. Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to initialize (this may take 15-20 seconds)..."
# Simple wait, can be improved by checking bolt port 7687
sleep 15

# 4. Start the Streamlit Chatbot
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Starting Chatbot UI via virtual environment..."
    $VENV_PATH/bin/streamlit run $STREAMLIT_APP
else
    echo "⚠️  Virtual environment not found at $VENV_PATH. Trying system streamlit..."
    streamlit run $STREAMLIT_APP
fi
