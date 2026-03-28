# Agents in opencodesage

This document describes how to create, configure, and use agents in opencodesage.

## What is an Agent?

An **agent** is an AI-powered entity that:
- Uses an LLM (Large Language Model) to reason about tasks
- Has access to tools (bash, file operations, web search, etc.)
- Maintains persistent memory (via Neo4j)
- Can execute code and commands in sandboxes
- Learns from past experiences

In opencodesage, agents are the "brains" that do the actual work:
- **OpenCode Agent**: Terminal UI for interactive development
- **OpenSage Agent**: Backend agent with memory and orchestration

---

## Architecture

### Agent Stack

```
┌──────────────────────────┐
│   User (Terminal/Chat)   │
└────────────┬─────────────┘
             │
┌────────────▼──────────────┐
│   OpenCode Agent          │
│   (Terminal UI)           │
│                           │
│  • Reasoning              │
│  • Tool Selection         │
│  • Code Execution         │
└────────────┬──────────────┘
             │ HTTP API
┌────────────▼──────────────┐
│  Dynamic Model Bridge     │  Reads from ~/.opencode/current_model
│  (Model Synchronization)  │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐
│   OpenSage Agent          │
│   (Backend)               │
│                           │
│  • Reasoning              │
│  • Tool Selection         │
│  • Code Execution         │
│  • Memory Management      │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐
│   Memory API              │
│   (Neo4j Interface)       │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐
│   Neo4j Database          │
│   (Persistent Memory)     │
└───────────────────────────┘
```

### Agent Communication Flow

```
User: "Build me a login form"
  ↓
OpenCode Agent (LLM decides what to do)
  ├─ Thinks: "I need React + validation"
  ├─ Uses: bash_tool → npm create-react-app
  ├─ Uses: file_tool → write LoginForm.jsx
  ├─ Uses: bash_tool → npm test
  └─ Stores memory: "Created login form with validation"
      ↓
      Memory API
      ↓
      Neo4j (persists)
  ↓
User: "Help with email validation"
  ↓
Agent searches memory: "email validation issue fixed before"
  ↓
Finds: "Used regex pattern X successfully"
  ↓
Applies solution immediately
```

---

## Built-in Agents

### 1. OpenCode Agent

**Purpose:** Terminal UI for interactive AI-assisted coding

**Location:** `bin/opencode` (wrapper) → `.opencode/bin/opencode_real` (real binary)

**Capabilities:**
- Interactive coding assistance
- Real-time tool selection
- Command execution
- File manipulation
- Model selection with `--model` flag

**Usage:**
```bash
# Start OpenCode via startup script (interactive model selection)
./start_opencodesage.sh

# Or start OpenCode directly with specific model
opencode --model opencode/minimax-m2.5-free

# Run specific command
opencode run "Build a React component for login"

# With custom port
opencode --port 3000
```

**Models Available (Free):**
- `opencode/minimax-m2.5-free` (default)
- `opencode/gpt-5-nano`
- `opencode/nemotron-3-super-free`
- `opencode/mimo-v2-pro-free`

**Configuration:**
- Location: `~/.opencode/` (or set `$OPENCODE_HOME`)
- Current model: `.opencode/current_model`
- Skills: `.opencode/skills/`
- Config: `.opencode/.opencode.json` (advanced)

### 2. OpenSage Agent

**Purpose:** Backend agent with memory, orchestration, and sandboxing

**Location:** `opensage/` (source code)

**Capabilities:**
- Multi-turn reasoning with memory
- Tool orchestration
- Sandbox execution (Docker)
- Neo4j memory persistence
- Agent ensembles
- Dynamic sub-agents

**Usage:**
```python
from opensage.agents.opensage_agent import OpenSageAgent
from google.adk.models.lite_llm import LiteLlm

# Create agent
agent = OpenSageAgent(
    name="my_agent",
    model=LiteLlm(
        model="opencode/minimax-m2.5-free",
        api_base="http://localhost:5557",  # Dynamic bridge
    ),
    description="My AI coding assistant",
    instruction="Help the user build web applications",
    tools=[bash_tool_main, file_tool, web_search_tool],
)

# Run agent
result = agent.run("Build a REST API with FastAPI")
print(result)
```

**Configuration:**
- Location: `opensage/config.toml`
- Memory: Neo4j (bolt://localhost:7687)
- Sandbox: Docker (native backend)
- Models: Any LiteLLM-compatible model

**Supported Tools:**
- `bash_tool_main` - Execute bash commands
- `file_tool` - Read/write files
- `web_search_tool` - Search the web
- `neo4j_tool` - Query memory
- `docker_tool` - Docker operations
- Custom tools (define your own)

---

## Creating Custom Agents

### Method 1: Simple Python Agent

**File:** `my_agents.py`

```python
from opensage.agents.opensage_agent import OpenSageAgent
from google.adk.models.lite_llm import LiteLlm
from opensage.toolbox.general.bash_tool import bash_tool_main

def create_frontend_agent(session_id: str) -> OpenSageAgent:
    """Agent specialized in frontend development"""
    return OpenSageAgent(
        name="frontend_agent",
        model=LiteLlm(
            model="opencode/minimax-m2.5-free",
            api_base="http://localhost:5557",
        ),
        description="Frontend development specialist",
        instruction="""You are expert in React, Vue, Svelte.
        Create responsive, accessible UIs.
        Use TypeScript and modern tooling.
        Always add proper error handling.""",
        tools=[bash_tool_main],
    )

def create_backend_agent(session_id: str) -> OpenSageAgent:
    """Agent specialized in backend development"""
    return OpenSageAgent(
        name="backend_agent",
        model=LiteLlm(
            model="opencode/minimax-m2.5-free",
            api_base="http://localhost:5557",
        ),
        description="Backend development specialist",
        instruction="""You are expert in Python, Node.js, Go.
        Build scalable, secure APIs.
        Use best practices for databases and caching.
        Always add logging and monitoring.""",
        tools=[bash_tool_main],
    )

# Usage
if __name__ == "__main__":
    frontend = create_frontend_agent("session-123")
    backend = create_backend_agent("session-123")
    
    print(frontend.run("Create a React login form"))
    print(backend.run("Build a FastAPI REST API"))
```

### Method 2: Agent with Custom Tools

```python
from opensage.agents.opensage_agent import OpenSageAgent
from google.adk.models.lite_llm import LiteLlm

def my_custom_tool(context, request: str) -> str:
    """Custom tool that does something specific"""
    return f"Processing: {request}"

def create_custom_agent(session_id: str) -> OpenSageAgent:
    return OpenSageAgent(
        name="custom_agent",
        model=LiteLlm(
            model="opencode/minimax-m2.5-free",
            api_base="http://localhost:5557",
        ),
        description="Agent with custom tools",
        instruction="Use available tools to solve problems",
        tools=[my_custom_tool],  # Your custom tool
    )
```

### Method 3: Agent Ensemble

```python
from opensage.session.opensage_ensemble_manager import OpenSageEnsembleManager

# Create multiple agents
frontend_agent = create_frontend_agent(session_id)
backend_agent = create_backend_agent(session_id)
devops_agent = create_devops_agent(session_id)

# Manage as ensemble
ensemble = OpenSageEnsembleManager(
    agents=[frontend_agent, backend_agent, devops_agent],
    memory_manager=memory_manager,
)

# Agents collaborate
result = ensemble.run("Build a complete web application")
```

---

## Agent Configuration

### config.toml

Located at: `opensage/config.toml`

```toml
[agent]
name = "my_agent"
description = "My AI agent"
instruction = "You are helpful assistant"

[model]
model = "opencode/minimax-m2.5-free"
api_base = "http://localhost:5557"
temperature = 0.7
max_tokens = 2048

[sandbox]
backend = "native"

[sandbox.sandboxes.main]
image = "ubuntu:24.04"

[memory]
neo4j_uri = "bolt://127.0.0.1:7687"
neo4j_user = "neo4j"
neo4j_password = "your_password"

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Environment Variables

```bash
# Model configuration
OPENCODE_MODEL="opencode/minimax-m2.5-free"
OPENCODE_BRIDGE_PORT="5557"
OPENCODE_HOME="$HOME/.opencode"

# Neo4j configuration
NEO4J_URI="bolt://127.0.0.1:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your_password"

# Memory API
OPENSAGE_API_PORT="5555"

# Agent settings
AGENT_NAME="my_agent"
AGENT_TIMEOUT="300"
```

---

## Agent Tools Reference

### Built-in Tools

#### 1. bash_tool_main
Execute bash commands in sandbox

```python
from opensage.toolbox.general.bash_tool import bash_tool_main

# In agent
tools=[bash_tool_main]

# Used automatically when agent needs to run commands
agent.run("Install npm packages")
# Agent executes: npm install
```

#### 2. file_tool
Read/write files

```python
from opensage.toolbox.general.file_tool import file_tool_main

tools=[file_tool_main]

# Agent can now read/write files
agent.run("Create a new file called app.py with hello world")
```

#### 3. web_search_tool
Search the web

```python
from opensage.toolbox.general.web_search_tool import web_search_tool_main

tools=[web_search_tool_main]

# Agent can search the web
agent.run("Find the latest React best practices")
```

#### 4. neo4j_tool
Query memory database

```python
from opensage.toolbox.general.neo4j_tool import neo4j_query_tool

tools=[neo4j_query_tool]

# Agent can access memory
agent.run("What did we learn about authentication?")
```

#### 5. docker_tool
Docker operations

```python
from opensage.toolbox.general.docker_tool import docker_tool_main

tools=[docker_tool_main]

# Agent can manage containers
agent.run("Start a PostgreSQL database")
```

### Custom Tool Template

```python
from opensage.toolbox.tool_normalization import tool_parameter
from typing import Any

@tool_parameter(tool_name="my_tool")
def my_custom_tool(
    context: Any,
    param1: str = "",
    param2: int = 0,
) -> str:
    """
    Custom tool description
    
    Args:
        context: Tool context
        param1: First parameter
        param2: Second parameter
        
    Returns:
        Result string
    """
    # Your implementation here
    return f"Result: {param1} + {param2}"

# Register with agent
tools=[my_custom_tool]
```

---

## Memory Management

### Storing Information

```bash
# Via OpenCode (in chat)
!curl "http://localhost:5555/remember?key=auth_pattern&value=Use JWT tokens in Authorization header"

# Via Python (in agent)
memory_api.remember(key="auth_pattern", value="Use JWT tokens...")
```

### Retrieving Information

```bash
# Via OpenCode
!curl "http://localhost:5555/recall?key=auth_pattern"

# Via Python
memory_api.recall(key="auth_pattern")
```

### Searching Memory

```bash
# Via OpenCode
!curl "http://localhost:5555/search?q=authentication"

# Via Python
memory_api.search(query="authentication")
```

### Direct Neo4j Queries

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))

with driver.session() as session:
    result = session.run(
        "MATCH (m:Memory) WHERE m.value CONTAINS $q RETURN m",
        q="authentication"
    )
    for record in result:
        print(record["m"])
```

---

## Model Synchronization

### How It Works

1. **Current Model File**: `~/.opencode/current_model`
   ```
   opencode/minimax-m2.5-free
   ```

2. **OpenCode Wrapper** updates this file when you use `--model`:
   ```bash
   opencode --model opencode/gpt-5-nano run "Build something"
   # Updates ~/.opencode/current_model to "opencode/gpt-5-nano"
   ```

3. **Dynamic Bridge** reads this file:
   ```python
   # opencode_dynamic_bridge.py
   def get_current_model():
       with open(MODEL_FILE) as f:
           return f.read().strip()
   ```

4. **Both Systems Use Same Model**:
   - OpenCode uses it
   - OpenSage uses it
   - Perfect synchronization ✅

### Changing Models

**Method 1: Direct File Edit**
```bash
echo "opencode/gpt-5-nano" > ~/.opencode/current_model
```

**Method 2: Via OpenCode**
```bash
opencode --model opencode/gpt-5-nano run "task"
```

**Method 3: Via Script**
```bash
# Set default model for new sessions
export OPENCODE_MODEL="opencode/gpt-5-nano"
opencode
```

### Available Models

**Free Models (No API Keys):**
- `opencode/minimax-m2.5-free` (default, recommended)
- `opencode/gpt-5-nano`
- `opencode/nemotron-3-super-free`
- `opencode/mimo-v2-pro-free`

**Paid Models (Requires API Key):**
- `gpt-4` (OpenAI)
- `claude-3-opus` (Anthropic)
- `gemini-pro` (Google)
- Any LiteLLM-supported model

---

## Multi-Agent Collaboration

### Agent Ensemble

Create multiple specialized agents that work together:

```python
from opensage.session.opensage_ensemble_manager import OpenSageEnsembleManager

# Create specialized agents
agents = {
    "frontend": create_frontend_agent(session_id),
    "backend": create_backend_agent(session_id),
    "devops": create_devops_agent(session_id),
}

# Ensemble manages them
ensemble = OpenSageEnsembleManager(agents=list(agents.values()))

# Task: Build complete application
result = ensemble.run("""
Build a complete web application:
1. Frontend: React with TypeScript
2. Backend: FastAPI with PostgreSQL
3. DevOps: Docker + Kubernetes setup
""")
```

### Agent Communication

Agents share memory automatically:

```
Frontend Agent:
  • Creates React components
  • Stores: "Created login form component"
  
Backend Agent (later):
  • Reads memory: "Frontend has login form"
  • Creates matching API endpoints
  • Stores: "Created /auth endpoints"
  
DevOps Agent (later):
  • Reads memory from both
  • Creates deployment config
  • All three coordinated without explicit messaging
```

### Memory-based Coordination

```python
# Frontend agent stores
memory.remember("ui_components", "LoginForm at src/components/LoginForm")

# Backend agent retrieves
components = memory.search("ui_components")
# Creates matching API

# DevOps agent retrieves both
frontend_info = memory.search("frontend")
backend_info = memory.search("backend")
# Creates deployment that coordinates both
```

---

## Agent Lifecycle

### Creation

```python
agent = OpenSageAgent(
    name="my_agent",
    model=LiteLlm(...),
    description="...",
    instruction="...",
    tools=[...],
)
```

### Initialization

```python
# Agent prepares:
# - Loads configuration
# - Initializes Neo4j connection
# - Creates sandboxes
# - Loads tools
```

### Execution

```python
# User input
result = agent.run("Build a login form")

# Agent:
# 1. Reasons about task
# 2. Selects tools
# 3. Executes commands
# 4. Gets results
# 5. Updates memory
# 6. Returns output
```

### Memory Persistence

```python
# Results stored in Neo4j
Memory nodes:
  • What was requested
  • What was tried
  • What succeeded
  • What failed
  • Final solution

# Searchable and accessible by future agents
```

---

## Best Practices

### 1. Agent Specialization

Create agents with specific purposes:

```python
# ✅ Good: Specialized agents
frontend_agent = create_agent(instruction="Frontend specialist...")
backend_agent = create_agent(instruction="Backend specialist...")
devops_agent = create_agent(instruction="DevOps specialist...")

# ❌ Avoid: Generic agents for everything
agent = create_agent(instruction="Do anything")
```

### 2. Clear Instructions

Provide specific, actionable instructions:

```python
# ✅ Good: Clear instruction
instruction = """
You are a React specialist.
- Use TypeScript
- Implement error boundaries
- Use React Context for state
- Follow React best practices
"""

# ❌ Avoid: Vague instruction
instruction = "Build things"
```

### 3. Tool Management

Only add tools agents actually need:

```python
# ✅ Good: Only needed tools
tools = [bash_tool_main, file_tool_main]

# ❌ Avoid: All possible tools
tools = [all_tools]
```

### 4. Memory Usage

Store important decisions and solutions:

```python
# ✅ Good: Store learnings
memory.remember("auth_pattern", "JWT in headers works best")
memory.remember("db_choice", "PostgreSQL for relational data")

# ❌ Avoid: Store everything
memory.remember("random_output", debug_info)
```

### 5. Error Handling

Provide good error messages:

```python
# ✅ Good: Helpful error
try:
    result = agent.run(task)
except Exception as e:
    logger.error(f"Agent failed on {task}: {e}")
    # Suggest fixes

# ❌ Avoid: Silent failures
try:
    result = agent.run(task)
except:
    pass
```

---

## Troubleshooting

### Agent Not Responding

**Symptom:** Agent hangs or doesn't respond

**Solution:**
```bash
# Check if services are running
curl http://localhost:7474  # Neo4j
curl http://localhost:5555  # Memory API
curl http://localhost:5557  # LLM Bridge

# Check agent logs
tail -f ~/.opencode/.logs/agent.log
```

### Model Not Syncing

**Symptom:** OpenCode and OpenSage using different models

**Solution:**
```bash
# Check current model
cat ~/.opencode/current_model

# Reset to default
echo "opencode/minimax-m2.5-free" > ~/.opencode/current_model

# Restart services
./start_opencodesage.sh
```

### Memory Not Persisting

**Symptom:** Agent can't recall previous work

**Solution:**
```bash
# Check Neo4j connection
cypher-shell -u neo4j -p password "MATCH (m:Memory) RETURN COUNT(m)"

# Check memory API
curl http://localhost:5555/list

# Verify Neo4j is running
brew services info neo4j
```

### Tool Execution Failures

**Symptom:** Tools fail to execute

**Solution:**
```bash
# Check sandbox
docker ps -a

# Test bash tool directly
curl "http://localhost:5555/remember?key=test&value=works"

# Check permissions
ls -la ~/.opencode/bin/opencode_real
chmod +x ~/.opencode/bin/opencode_real
```

---

## Examples

### Example 1: Build a Full-Stack App

```bash
opencode --model opencode/minimax-m2.5-free

# In OpenCode chat:
"Build me a complete todo app with:
- React frontend with TypeScript
- FastAPI backend
- PostgreSQL database
- Docker setup"

# Agent will:
# 1. Create React app structure
# 2. Create FastAPI server
# 3. Set up database
# 4. Create Docker files
# 5. Store all decisions in memory
```

### Example 2: Fix a Bug

```bash
# Start with memory of previous work
opencode

# In chat:
"I'm getting CORS errors. How did we solve this before?"

# Agent will:
# 1. Search memory for CORS solutions
# 2. Find previous fix
# 3. Apply to current code
# 4. Test solution
# 5. Update memory with result
```

### Example 3: Multi-Agent Project

```python
# From Python
session = OpenSageSession()

frontend = create_frontend_agent(session.id)
backend = create_backend_agent(session.id)

# Frontend builds UI
frontend.run("Create user dashboard")

# Backend builds API
backend.run("Create /users endpoint")

# Both read memory and coordinate automatically
# No explicit communication needed!
```

---

## Summary

Agents in opencodesage are powerful AI entities that:
- ✅ Reason about complex tasks
- ✅ Execute code and commands
- ✅ Remember past work
- ✅ Collaborate through shared memory
- ✅ Specialize in specific domains
- ✅ Learn and improve over time

**Start with:** `./start_opencodesage.sh` (select model via interactive menu) then `opencode`

**Learn more:** Read CODE_REVIEW_OPENCODESAGE.md and INTEGRATION_COMPLETE.md

**Get help:** Check troubleshooting section or review code examples
