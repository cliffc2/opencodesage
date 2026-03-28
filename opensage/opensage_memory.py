#!/usr/bin/env python3
"""
OpenSage Memory CLI - Use Neo4j memory from any tool.

Usage:
    python opensage_memory.py remember <key> <value>
    python opensage_memory.py recall <key>
    python opensage_memory.py list
"""

import sys
import os

# Add OpenSage to path
sys.path.insert(0, "/Users/ghostgear/opensage/src")

from neo4j import GraphDatabase


NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "callgraphn4j!"


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def remember(key: str, value: str):
    with get_driver() as driver:
        driver.execute_query(
            "MERGE (m:Memory {key: $key}) SET m.value = $value, m.updated = timestamp()",
            key=key,
            value=value,
        )
    print(f"✓ Remembered: {key}")


def recall(key: str):
    with get_driver() as driver:
        result = driver.execute_query(
            "MATCH (m:Memory {key: $key}) RETURN m.value as value", key=key
        )
        records = list(result.records)
        if records and records[0]["value"]:
            print(records[0]["value"])
        else:
            print(f"No memory found for: {key}")


def list_memories():
    with get_driver() as driver:
        result = driver.execute_query(
            "MATCH (m:Memory) RETURN m.key as key, m.value as value ORDER BY m.updated DESC"
        )
        for record in result.records:
            print(f"{record['key']}: {record['value']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "remember" and len(sys.argv) >= 4:
        remember(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "recall" and len(sys.argv) >= 3:
        recall(sys.argv[2])
    elif cmd == "list":
        list_memories()
    else:
        print(__doc__)
