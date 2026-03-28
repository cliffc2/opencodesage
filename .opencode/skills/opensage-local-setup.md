name: OpenSage Local Setup
description: Set up OpenSage AI agent framework with local Ollama models

# Prerequisites
- Python >= 3.12
- uv (dependency manager)
- Docker (for sandbox backend)
- Ollama (for local models)

# Steps

## 1. Install Python 3.12
```bash
uv python install 3.12
```

## 2. Clone and setup OpenSage
```bash
git clone https://github.com/opensage-agent/opensage.git
cd opensage
uv python install
uv sync
```

## 3. Pin litellm version (security fix)
The litellm library had a supply chain attack in versions 1.82.7-1.82.8. Pin to safe version:

Edit `pyproject.toml` line 26:
```toml
litellm>=1.74.7,<1.82.0
```

Then update lock file:
```bash
uv lock && uv sync
```

## 4. Ensure Docker is running
```bash
open -a Docker
```

## 5. Create agent with local Ollama model
Create agent directory:
```bash
mkdir -p opensage/examples/agents/my_ollama_agent
```

Create `agent.py`:
```python
import os
from google.adk.models.lite_llm import LiteLlm
from opensage.agents.opensage_agent import OpenSageAgent
from opensage.toolbox.general.bash_tool import bash_tool_main


def mk_agent(opensage_session_id: str):
    return OpenSageAgent(
        name="my_ollama_agent",
        model=LiteLlm(
            model="ollama/qwen2.5:0.5b",  # or your model
            api_base="http://localhost:11434",
        ),
        description="A simple agent using local Ollama model.",
        instruction="You are a helpful coding assistant. Use bash_tool_main to run commands.",
        tools=[bash_tool_main],
    )
```

Create `__init__.py` (empty file):
```bash
touch opensage/examples/agents/my_ollama_agent/__init__.py
```

Create `config.toml`:
```toml
# Sandbox configuration
[sandbox]
backend = "native"
image = "opensage/main:latest"

[model]
```

## 6. Test litellm with Ollama
```bash
cd opensage && uv run python -c "
import litellm
response = litellm.completion(
    model='ollama/qwen2.5:0.5b',
    messages=[{'role': 'user', 'content': 'say hi'}],
    api_base='http://localhost:11434'
)
print(response.choices[0].message.content)
"
```

## 7. Run OpenSage web UI
```bash
cd opensage
uv run opensage web --agent examples/agents/my_ollama_agent --config examples/agents/my_ollama_agent/config.toml --port 8000
```

## 8. Access the UI
Open http://localhost:8000/dev-ui/ in your browser.

# Checking installed models
```bash
ollama list
```

# Troubleshooting
- Ensure Ollama is running: `pgrep -fl ollama`
- Check Docker is running: `docker info`
- Dependency check: `uv run opensage dependency-check`
