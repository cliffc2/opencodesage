# OpenSage Memory Skill

Use this skill to access persistent memory powered by Neo4j graph database.

## Commands

### Remember something important
```
/remember key: value
```
Example: `/remember project_notes: The login API is at /api/auth/login`

### Recall stored information
```
/recall key
```
Example: `/recall project_notes`

### Search memories
```
/search query
```
Example: `/search login`

### List all memories
```
/memories
```

### Delete a memory
```
/forget key
```

## Notes
- Memories persist across sessions via Neo4j
- Use for storing: API endpoints, configuration, important context
- Accessible from any OpenCode session
