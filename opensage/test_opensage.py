#!/usr/bin/env python3
"""
OpenSage Backend Test Suite

Tests various OpenSage backend capabilities:
1. Memory (Neo4j) - ✓ Working
2. Dynamic Agents
3. Tools (bash, file ops)
4. Sandbox execution

Run: python test_opensage.py
"""

import sys

sys.path.insert(0, "/Users/ghostgear/opensage/src")

from neo4j import GraphDatabase
import subprocess
import os

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "callgraphn4j!"


def test_neo4j():
    """Test Neo4j connection and memory."""
    print("\n=== Test 1: Neo4j Memory ===")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    # Store test memory
    driver.execute_query(
        "MERGE (m:Memory {key: $key}) SET m.value = $value",
        key="test_run",
        value="OpenSage test successful",
    )

    # Recall
    result = driver.execute_query(
        "MATCH (m:Memory {key: $key}) RETURN m.value as value", key="test_run"
    )
    records = list(result.records)
    value = records[0]["value"] if records else None

    driver.close()
    print(f"✓ Memory test: {value}")
    return True


def test_docker_sandbox():
    """Test Docker sandbox availability."""
    print("\n=== Test 2: Docker Sandbox ===")
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True
    )
    containers = result.stdout.strip().split("\n")
    print(f"✓ Running containers: {containers}")
    return True


def test_openSage_modules():
    """Test importing OpenSage modules."""
    print("\n=== Test 3: OpenSage Modules ===")

    try:
        from opensage.agents.opensage_agent import OpenSageAgent

        print("✓ OpenSageAgent available")
    except Exception as e:
        print(f"✗ OpenSageAgent: {e}")

    try:
        from opensage.toolbox.general.bash_tool import bash_tool_main

        print("✓ bash_tool available")
    except Exception as e:
        print(f"✗ bash_tool: {e}")

    try:
        from opensage.toolbox.general.dynamic_subagent import create_subagent

        print("✓ dynamic_subagent available")
    except Exception as e:
        print(f"✗ dynamic_subagent: {e}")

    return True


def test_litellm():
    """Test litellm with available models."""
    print("\n=== Test 4: LLM Models ===")
    import litellm

    # Check available free models
    models = [
        m for m in litellm.model_list if "free" in m.lower() or "opencode" in m.lower()
    ]
    print(f"Available models: {models[:5]}")

    return True


def list_all_memories():
    """List all stored memories."""
    print("\n=== All Memories ===")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    result = driver.execute_query(
        "MATCH (m:Memory) RETURN m.key as key, m.value as value"
    )

    for record in result.records:
        print(f"  {record['key']}: {record['value']}")

    driver.close()


if __name__ == "__main__":
    print("OpenSage Backend Test Suite")
    print("=" * 40)

    test_neo4j()
    test_docker_sandbox()
    test_openSage_modules()
    test_litellm()
    list_all_memories()

    print("\n=== Done ===")
