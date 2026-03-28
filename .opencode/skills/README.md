# OpenCode + OpenSage Integration Skills

Skills for integrating OpenCode with OpenSage's Neo4j memory system and dynamic model bridge.

## Skills

- **opencode-opensage.md** - Complete integration guide (READ THIS FIRST)
- **opensage-memory-api.md** - Memory API reference  
- **opensage-local-setup.md** - OpenSage setup guide

## Quick Start

### 1. Start All Services (Recommended)
```bash
cd /Users/ghostgear/opencodesage
./start_opencodesage.sh
```
This will start Neo4j, Memory API, and Dynamic LLM Bridge with an interactive model selection menu.

### 2. Manual Start (Alternative)
```bash
# 1. Start Neo4j
brew services start neo4j
# or
/opt/homebrew/bin/neo4j start

# 2. Start Memory API (port 5555)
cd /Users/ghostgear/opensage
source .venv/bin/activate
python opensage_api.py &

# 3. Start Dynamic LLM Bridge (port 5557)
source .venv/bin/activate
python opencode_dynamic_bridge.py &
```

## Usage

### Memory
```bash
!curl "http://localhost:5555/remember?key=notes&value=My notes"
!curl "http://localhost:5555/recall?key=notes"
```

### Switch Models (both OpenCode & OpenSage use same model)
```bash
# Change model - both will use it!
echo "opencode/gpt-5-nano" > ~/.opencode/current_model
```

## Files

| File | Description |
|------|-------------|
| `opensage_api.py` | HTTP API for Neo4j memory (port 5555) |
| `opencode_dynamic_bridge.py` | LLM bridge with dynamic model (port 5557) |
| `opensage_memory.py` | CLI memory tool |
| `test_*.py` | Test scripts |
