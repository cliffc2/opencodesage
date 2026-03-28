#!/bin/bash
# OpenCode + OpenSage Startup Script
# Run: ./start_opencode_opensage.sh

set -e

echo "========================================="
echo "Starting OpenCode + OpenSage"
echo "========================================="

# 1. Start Neo4j
echo "[1/3] Starting Neo4j..."
/opt/homebrew/bin/neo4j start &
sleep 5

# Wait for Neo4j to be ready
echo "Waiting for Neo4j..."
for i in {1..30}; do
    if curl -s http://localhost:7474 > /dev/null 2>&1; then
        echo "Neo4j ready!"
        break
    fi
    sleep 1
done

# 2. Start Memory API
echo "[2/3] Starting Memory API (port 5555)..."
cd /Users/ghostgear/opensage
source .venv/bin/activate
python /Users/ghostgear/opensage/opensage_api.py > /dev/null 2>&1 &
sleep 2

# 3. Start Dynamic Bridge
echo "[3/3] Starting Dynamic LLM Bridge (port 5557)..."
python /Users/ghostgear/opensage/opencode_dynamic_bridge.py > /dev/null 2>&1 &
sleep 2

echo ""
echo "========================================="
echo "All services started!"
echo "========================================="
echo ""
echo "Services:"
echo "  Neo4j:      http://localhost:7474"
echo "  Memory API: http://localhost:5555"
echo "  LLM Bridge: http://localhost:5557"
echo ""
# Set default model if not set
if [ ! -f ~/.opencode/current_model ]; then
    echo "opencode/minimax-m2.5-free" > ~/.opencode/current_model
fi

echo "Current model: $(cat ~/.opencode/current_model)"
echo ""
echo "Usage:"
echo "  Memory: curl 'http://localhost:5555/remember?key=X&value=Y'"
echo "  Model:  echo 'opencode/gpt-5-nano' > ~/.opencode/current_model"
echo ""
