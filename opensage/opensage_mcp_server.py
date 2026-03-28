#!/usr/bin/env python3
"""
OpenSage MCP Server - Exposes OpenSage tools to OpenCode.

Run this server, then add to OpenCode:
    opencode mcp add opensage "python /path/to/opensage_mcp_server.py"

Usage:
    python opensage_mcp_server.py
"""

import sys

sys.path.insert(0, "/Users/ghostgear/opensage/src")

from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase
import os

mcp = FastMCP("OpenSage Memory", port=1113, host="0.0.0.0")

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "callgraphn4j!"


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


@mcp.tool()
def remember(key: str, value: str) -> str:
    """Store important information in persistent memory."""
    with get_driver() as driver:
        driver.execute_query(
            "MERGE (m:Memory {key: $key}) SET m.value = $value, m.updated = timestamp()",
            key=key,
            value=value,
        )
    return f"✓ Remembered: {key}"


@mcp.tool()
def recall(key: str) -> str:
    """Recall stored information from memory."""
    with get_driver() as driver:
        result = driver.execute_query(
            "MATCH (m:Memory {key: $key}) RETURN m.value as value", key=key
        )
        records = list(result.records)
        if records and records[0]["value"]:
            return records[0]["value"]
    return f"No memory found for: {key}"


@mcp.tool()
def list_memories() -> str:
    """List all stored memories."""
    with get_driver() as driver:
        result = driver.execute_query(
            "MATCH (m:Memory) RETURN m.key as key, m.value as value ORDER BY m.updated DESC"
        )
        memories = [f"{r['key']}: {r['value']}" for r in result.records]
        if memories:
            return "\n".join(memories)
    return "No memories stored"


@mcp.tool()
def search_memories(query: str) -> str:
    """Search memories for a keyword."""
    with get_driver() as driver:
        result = driver.execute_query(
            "MATCH (m:Memory) WHERE m.value CONTAINS $query OR m.key CONTAINS $query RETURN m.key as key, m.value as value",
            query=query,
        )
        memories = [f"{r['key']}: {r['value']}" for r in result.records]
        if memories:
            return "\n".join(memories)
    return f"No memories found matching: {query}"


@mcp.tool()
def delete_memory(key: str) -> str:
    """Delete a memory by key."""
    with get_driver() as driver:
        driver.execute_query("MATCH (m:Memory {key: $key}) DELETE m", key=key)
    return f"✓ Deleted: {key}"


if __name__ == "__main__":
    print("Starting OpenSage MCP Server on http://0.0.0.0:1113")
    mcp.run(transport="sse")
