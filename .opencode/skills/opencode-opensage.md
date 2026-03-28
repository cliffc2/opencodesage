# OpenCode + OpenSage Integration

Complete integration: OpenCode (frontend) ↔ OpenSage (backend with Neo4j memory)

## Architecture

```
┌─────────────┐     HTTP API     ┌──────────────────┐
│  OpenCode   │ ◄──────────────► │  OpenSage        │
│  (Frontend) │    Dynamic       │  (Backend)       │
│             │    Bridge        │                  │
│  - TUI      │    port 5557     │  - Neo4j Memory  │
│  - Models   │                  │  - Agents        │
└─────────────┘                  │  - Tools         │
                                  └──────────────────┘
                                          │
                                          ▼
                                  ┌──────────────────┐
                                  │  Neo4j           │
                                  │  (Graph DB)      │
                                  └──────────────────┘
```

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

# 2. Start OpenSage Memory API (port 5555)
cd /Users/ghostgear/opensage
source .venv/bin/activate
python opensage_api.py &

# 3. Start Dynamic Bridge (port 5557)
cd /Users/ghostgear/opensage
source .venv/bin/activate
python opencode_dynamic_bridge.py &
```

## Usage

### Memory (from OpenCode)
```bash
# Store
curl "http://localhost:5555/remember?key=notes&value=Important info"

# Recall  
curl "http://localhost:5555/recall?key=notes"

# List
curl "http://localhost:5555/list"

# Search
curl "http://localhost:5555/search?q=project"
```

### Switch Models (for both OpenCode & OpenSage)
The startup script `./start_opencodesage.sh` provides an interactive menu to select the model:
- 1) minimax-m2.5-free (default)
- 2) nemotron-3-super-free
- 3) mimo-v2-pro-free
- 4) gpt-5-nano
- 5) Exit without launching OpenCode

**Method 1: Via Startup Script (Recommended)**
```bash
./start_opencodesage.sh
# Select option 1-4 to launch OpenCode with chosen model
```

**Method 2: Direct File Edit**
```bash
echo "opencode/minimax-m2.5-free" > ~/.opencode/current_model
```

**Method 3: Via OpenCode Command**
```bash
opencode --model opencode/minimax-m2.5-free
```

**Available Models:**
- `opencode/minimax-m2.5-free` (default)
- `opencode/nemotron-3-super-free`
- `opencode/mimo-v2-pro-free`
- `opencode/gpt-5-nano`

**Check Current Model**
```bash
curl http://localhost:5557/
```

### Test the LLM Bridge
```bash
curl -X POST http://localhost:5557/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Files

| File | Port | Description |
|------|------|-------------|
| `opensage_api.py` | 5555 | Neo4j memory HTTP API |
| `opencode_dynamic_bridge.py` | 5557 | LLM bridge with dynamic model |
| `test_opensage.py` | - | Basic backend tests |
| `test_opensage_full.py` | - | Full test suite |
| `test_coding_tasks.py` | - | Coding task tests |

## Neo4j Credentials

- URL: bolt://127.0.0.1:7687
- HTTP: http://localhost:7474
- User: neo4j
- Password: callgraphn4j!

## API Endpoints

### Memory API (5555)
| Endpoint | Description |
|----------|-------------|
| `GET /remember?key=X&value=Y` | Store memory |
| `GET /recall?key=X` | Retrieve memory |
| `GET /list` | List all memories |
| `GET /search?q=X` | Search memories |

### LLM Bridge (5557)
| Endpoint | Description |
|----------|-------------|
| `GET /` | Get current model |
| `POST /v1/chat/completions` | LLM chat (OpenAI compatible) |

## Test Results

- Memory (Neo4j): ✓ PASS
- Docker Sandbox: ✓ PASS  
- OpenSage Agent: ✓ PASS
- Bash Tool: ✓ PASS
- Dynamic Sub-agents: ✓ PASS
- LLM Models (1655): ✓ PASS
- Web Search: ✓ PASS
- Agent Ensemble: ✓ PASS
- Neo4j Tools: ✓ PASS
- Coding Tasks: ✓ PASS

## Skills Location

Skills in: `~/.opencode/skills/`

To push to GitHub:
```bash
cd ~/opencode-skills
git add .
git commit -m "Add OpenCode + OpenSage integration with dynamic bridge"
git push origin main
```
