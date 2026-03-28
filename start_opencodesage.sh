#!/bin/bash
# OpenCodeSage startup script - starts all services
# Run from the OpenCodeSage root directory: ./start_OpenCodeSage.sh

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Base directory: $BASE_DIR"

# Optional secrets / env (NEO4J_PASSWORD, etc.)
if [[ -f "$BASE_DIR/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$BASE_DIR/.env"
  set +a
fi

OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.opencode}"
DEFAULT_MODEL="${DEFAULT_MODEL:-opencode/minimax-m2.5-free}"
mkdir -p "$OPENCODE_HOME"
if [[ ! -f "$OPENCODE_HOME/current_model" ]] || [[ ! -s "$OPENCODE_HOME/current_model" ]]; then
  echo "$DEFAULT_MODEL" > "$OPENCODE_HOME/current_model"
fi

NEO4J_BIN=""
if [[ -x /opt/homebrew/bin/neo4j ]]; then
  NEO4J_BIN=/opt/homebrew/bin/neo4j
elif command -v neo4j >/dev/null 2>&1; then
  NEO4J_BIN="$(command -v neo4j)"
fi

# 1. Start Neo4j
if [[ -n "$NEO4J_BIN" ]]; then
  echo "[1/3] Starting Neo4j..."
  "$NEO4J_BIN" start &
  sleep 5
  echo "Waiting for Neo4j..."
  for _ in {1..30}; do
    if curl -sf http://localhost:7474 >/dev/null 2>&1; then
      echo "Neo4j ready!"
      break
    fi
    sleep 1
  done
else
  echo "[1/3] Skipping Neo4j start (neo4j not found in PATH or /opt/homebrew/bin)."
fi

# 2. Start Memory API
echo "[2/3] Starting Memory API (port ${OPENSAGE_API_PORT:-5555})..."
cd "$BASE_DIR"
if [[ -f "$BASE_DIR/opensage/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$BASE_DIR/opensage/.venv/bin/activate"
elif [[ -f "$BASE_DIR/opensage/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$BASE_DIR/opensage/.venv/bin/activate"
else
  echo "Note: no venv at opensage/.venv or opensage/.venv — using system python"
fi
export OPENSAGE_API_PORT="${OPENSAGE_API_PORT:-5555}"
python3 "$BASE_DIR/opensage_api.py" >/dev/null 2>&1 &
sleep 2

# 3. Start Dynamic Bridge
echo "[3/3] Starting Dynamic LLM Bridge (port ${OPENCODE_BRIDGE_PORT:-5557})..."
export OPENCODE_HOME
python3 "$BASE_DIR/opencode_dynamic_bridge.py" >/dev/null 2>&1 &
sleep 2

echo ""
echo "========================================="
echo "All services started!"
echo "========================================="
echo ""
echo "Services:"
echo "  Neo4j:      http://localhost:7474"
echo "  Memory API: http://localhost:${OPENSAGE_API_PORT:-5555}"
echo "  LLM Bridge: http://localhost:${OPENCODE_BRIDGE_PORT:-5557}"
echo ""
echo "Current model: $(cat "$OPENCODE_HOME/current_model" 2>/dev/null || echo "$DEFAULT_MODEL")"
echo ""
echo "Usage:"
echo "  Memory: curl 'http://localhost:${OPENSAGE_API_PORT:-5555}/remember?key=X&value=Y'"
echo "  Model:  echo 'opencode/gpt-5-nano' > '$OPENCODE_HOME/current_model'"
echo ""
echo "Set NEO4J_PASSWORD in $BASE_DIR/.env (see .env.example) before starting if the memory API exits."
echo ""
