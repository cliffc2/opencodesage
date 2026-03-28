# OpenCode + OpenSage Integration Skills

Skills for integrating OpenCode with OpenSage's Neo4j memory system and dynamic model bridge.

## Skills

- **opencode-opensage.md** - Complete integration guide
- **opensage-memory-api.md** - Memory API reference
- **opensage-local-setup.md** - OpenSage setup guide

## Quick Start

### 1. Start All Services (Recommended)
```bash
# From the OpenCodeSage root directory:
./start_opencodesage.sh
```
This starts Neo4j, Memory API, and Dynamic LLM Bridge with an interactive model selection menu.

### 2. Manual Start (Alternative)
```bash
# 1. Start Neo4j
brew services start neo4j
# or
/opt/homebrew/bin/neo4j start

# 2. Start Memory API (port 5555)
cd opensage
source .venv/bin/activate
python opensage_api.py &

# 3. Start Dynamic LLM Bridge (port 5557)
source .venv/bin/activate
python opencode_dynamic_bridge.py &
```

## Usage

### Memory Operations
```bash
# Store a memory item
!curl "http://localhost:5555/remember?key=notes&value=My notes"

# Retrieve a memory item
!curl "http://localhost:5555/recall?key=notes"

# List all memories
!curl "http://localhost:5555/list"

# Search memories
!curl "http://localhost:5555/search?q=API"
```

### Model Selection (Both OpenCode & OpenSage use the same model)
The startup script `./start_opencodesage.sh` provides an interactive menu:
- 1) minimax-m2.5-free (default, selected after 10 seconds)
- 2) nemotron-3-super-free
- 3) mimo-v2-pro-free
- 4) gpt-5-nano
- 5) Exit without launching OpenCode

**Direct file edit method:**
```bash
echo "opencode/minimax-m2.5-free" > ~/.opencode/current_model
```

**Direct command method:**
```bash
opencode --model opencode/minimax-m2.5-free
```

## Files

| File | Description |
|------|-------------|
| `opensage_api.py` | HTTP API for Neo4j memory (port 5555) |
| `opencode_dynamic_bridge.py` | LLM bridge with dynamic model (port 5557) |
| `opensage_memory.py` | CLI memory tool |
| `test_*.py` | Test scripts |

## Model Synchronization

Both OpenCode and OpenSage automatically use the same model defined in:
- `~/.opencode/current_model` (shared file)
- Updated by `bin/opencode` wrapper when using `--model` flag
- Read by `opencode_dynamic_bridge.py` to synchronize LLM usage

Default model: `opencode/minimax-m2.5-free`