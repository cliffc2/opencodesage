# OpenCodeSage

Portable AI coding assistant combining OpenCode (frontend/TUI) with OpenSage (backend with Neo4j memory) and dynamic model synchronization.

## Overview

OpenCodeSage is a self-contained folder that combines:
- **OpenCode**: An open-source AI coding agent with a terminal UI and free models
- **OpenSage**: An AI agent framework with persistent memory (Neo4j) and agent orchestration
- **Dynamic LLM Bridge**: A service that keeps both OpenCode and OpenSage using the same model
- **Memory API**: A REST API for persistent storage via Neo4j
- **One-command startup script**: Starts all services (Neo4j, Memory API, LLM Bridge)

## Features

- ✅ **Model Synchronization**: Changing the model via `opencode --model` updates both OpenCode and OpenSage automatically
- ✅ **Persistent Memory**: Neo4j graph database stores memories across sessions
- ✅ **Portability**: Everything self-contained in one folder (except Neo4j and OpenCode binary which users build/install)
- ✅ **One-command startup**: `./start_opencodesage.sh` handles Neo4j, Memory API, and LLM Bridge
- ✅ **Secure**: Neo4j password required via environment (not hardcoded)
- ✅ **Free Models**: Uses OpenCode's built-in free providers (no API keys needed for basic usage)

## Quick Start

### Prerequisites

1. **Neo4j** (graph database)
   - Install via Homebrew: `brew install neo4j`
   - Or download from https://neo4j.com/download/
   - Neo4j must be running on `bolt://127.0.0.1:7687`

2. **OpenCode** (the AI coding agent)
   - You need to build or install OpenCode from source
   - The wrapper expects the real OpenCode binary at `.opencode/bin/opencode_real`
   - Build instructions: https://github.com/cliffc2/opencode (your fork)
   - After building, place the binary at `.opencode/bin/opencode_real`

3. **Python 3.12+** (for the bridge and API)
   - The project includes a virtual environment setup helper, but you can also use system Python
   - Required packages: `neo4j`, `litellm` (installed via the virtual environment if you use the provided setup)

### Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/cliffc2/OpenCodeSage.git
   cd OpenCodeSage
   ```

2. **Build/OpenCode**
   - Follow the instructions in your OpenCode fork to build the binary
   - Place the built binary at: `.opencode/bin/opencode_real`
   - Make sure it's executable: `chmod +x .opencode/bin/opencode_real`

3. **Set up environment (optional but recommended)**
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to set your Neo4j password:
     ```bash
     NEO4J_PASSWORD=your_secure_password_here
     ```
   - You can also adjust other settings like ports if needed.

4. **Initialize the model file (done automatically on first run)**
   - The default model is `opencode/minimax-m2.5-free`
   - To change the default, edit `.opencode/current_model` or use the opencode wrapper with `--model`

### Running

#### One-command startup (recommended)
```bash
./start_opencodesage.sh
```

This script will:
1. Check/start Neo4j (using Homebrew or PATH)
2. Start the Memory API on port 5555
3. Start the Dynamic LLM Bridge on port 5557
4. Display status and usage information

#### Manual startup
If you prefer to start services individually:

1. **Start Neo4j** (if not already running)
   ```bash
   # Homebrew
   brew services start neo4j
   # or
   /opt/homebrew/bin/neo4j start
   ```

2. **Start Memory API**
   ```bash
   source .opencode/.venv/bin/activate 2>/dev/null || echo "Using system python"
   python opensage_api.py
   ```

3. **Start Dynamic LLM Bridge**
   ```bash
   source .opencode/.venv/bin/activate 2>/dev/null || echo "Using system python"
   python opencode_dynamic_bridge.py
   ```

### Usage Examples

#### Switching the model (used by both OpenCode and OpenSage)

**Method 1: Direct file edit**
```bash
echo "opencode/gpt-5-nano" > .opencode/current_model
```

**Method 2: Via opencode command (RECOMMENDED)**
```bash
bin/opencode --model opencode/gpt-5-nano --version
# or any opencode command with --model flag
```

Both OpenCode and OpenSage will use the new model automatically.

#### Using the Memory API (from within OpenCode terminal)
In your OpenCode session, you can use the Memory API to store and recall information:

```bash
# Store a note
!curl "http://localhost:5555/remember?key=project_notes&value=The API endpoint is at /api/v1/users"

# Recall a note
!curl "http://localhost:5555/recall?key=project_notes"

# List all memories
!curl "http://localhost:5555/list"

# Search memories
!curl "http://localhost:5555/search?q=API"
```

#### Using the LLM Bridge directly
```bash
curl -X POST http://localhost:5557/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Explain how to create a REST API in Python using Flask"}]}'
```

## Architecture

```
┌─────────────┐     HTTP API      ┌──────────────────┐
│  OpenCode   │ ◄──────────────► │  OpenSage        │
│  (Frontend) │    Dynamic        │  (Backend)       │
│             │    Bridge         │                  │
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

## Design Highlights

- **Model Synchronization**: Changing model via `bin/opencode --model` updates `.opencode/current_model`, which the LLM bridge reads automatically
- **Persistent Memory**: Neo4j stores memories across sessions (configurable via environment variables)
- **Portability**: Everything self-contained in the `OpenCodeSage` folder (except Neo4j and OpenCode binary)
- **One-command startup**: `start_opencodesage.sh` handles Neo4j, Memory API, and LLM Bridge
- **Secure**: Neo4j password required via environment (not hardcoded in source)
- **Free Models**: Uses OpenCode's built-in free providers (no API keys needed for basic usage)

## Files

| File/Directory | Description |
|----------------|-------------|
| `start_opencodesage.sh` | One-command startup script |
| `opensage_api.py` | Memory API (REST endpoint for Neo4j) |
| `opencode_dynamic_bridge.py` | LLM bridge (synchronizes model with OpenCode) |
| `bin/opencode` | Wrapper that updates the shared model file when using `--model` |
| `.opencode/current_model` | Shared model file (default: opencode/minimax-m2.5-free) |
| `.opencode/` | OpenCode configuration, skills, etc. |
| `opensage/` | OpenSage source code |
| `.env.example` | Template for environment variables |
| `.env` | (Optional) Actual environment variables (copy from .env.example) |

## Environment Variables (optional)

Create a `.env` file (copy from `.env.example`) to override defaults:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_PASSWORD` | **Required** Neo4j password | *(must be set)* |
| `NEO4J_URI` | Neo4j connection URI | `bolt://127.0.0.1:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `OPENSAGE_API_PORT` | Port for Memory API | `5555` |
| `OPENCODE_BRIDGE_PORT` | Port for LLM Bridge | `5557` |
| `OPENCODE_HOME` | Directory containing current_model | `~/.opencode` |
| `OPENCODE_CMD` | Binary to invoke for OpenCode | `opencode` (on PATH) |

## Test Results

All core functionalities have been tested and are working:
- ✅ Memory (Neo4j): PASS
- ✅ Docker Sandbox: PASS (if Docker is installed)
- ✅ OpenSage Agent: PASS
- ✅ Bash Tool: PASS
- ✅ Dynamic Sub-agents: PASS
- ✅ LLM Models (1655 available via litellm): PASS
- ✅ Web Search: PASS
- ✅ Agent Ensemble: PASS
- ✅ Neo4j Tools: PASS
- ✅ Coding Tasks: PASS

## Troubleshooting

### Neo4j not running
- Ensure Neo4j is installed and running: `brew services start neo4j` or `/opt/homebrew/bin/neo4j start`
- The startup script will wait for Neo4j to be ready before proceeding

### Memory API fails to start
- Check that `NEO4J_PASSWORD` is set in your environment or `.env` file
- Verify Neo4j is accessible at `bolt://127.0.0.1:7687`

### LLM Bridge not responding
- Ensure the OpenCode wrapper (`bin/opencode`) works and can build the `opencode_real` binary
- Verify the model file `.opencode/current_model` exists and contains a valid model

### Model not switching
- Verify you're using the wrapped `bin/opencode` command, not the system opencode
- Check that `.opencode/current_model` is updated after running a command with `--model`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Built upon [OpenCode](https://github.com/cliffc2/opencode) (your fork)
- Built upon [OpenSage](https://github.com/cliffc2/opensage)
- Uses [litellm](https://github.com/BerriAI/litellm) for LLM abstraction
- Uses [Neo4j](https://neo4j.com/) for persistent graph storage
- Powered by free AI models: Minimax 2.5 Free and Nemotron 3 Super Free

---
**Ready to use**: Clone, build OpenCode, set Neo4j password, run `./start_opencodesage.sh`, and start coding with persistent memory and synchronized models!