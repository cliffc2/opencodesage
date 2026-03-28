# OpenSage Memory API

Use OpenSage's Neo4j-powered persistent memory from any tool.

## API Server
Start the memory API server:
```bash
# From the OpenCodeSage root directory:
cd opensage
source .venv/bin/activate
python opensage_api.py &
```

Server runs on: `http://localhost:5555`

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/remember?key=<key>&value=<value>` | Store a memory |
| `/recall?key=<key>` | Retrieve a memory |
| `/list` | List all memories |
| `/search?q=<query>` | Search memories |

## Usage Examples

### Remember something
```bash
curl "http://localhost:5555/remember?key=project_name&value=MyProject"
```

### Recall something
```bash
curl "http://localhost:5555/recall?key=project_name"
```

### List all
```bash
curl "http://localhost:5555/list"
```

### Search
```bash
curl "http://localhost:5555/search?q=project"
```

## Requirements
- Neo4j running on bolt://127.0.0.1:7687
- Password: Set via NEO4J_PASSWORD environment variable
