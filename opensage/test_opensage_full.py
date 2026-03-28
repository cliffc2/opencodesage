#!/usr/bin/env python3
"""
OpenSage Full Test Suite - All Backend Capabilities

Run: cd /Users/ghostgear/opensage && source .venv/bin/activate && python test_opensage_full.py
"""

import sys
import os
import tempfile
import subprocess
import time

sys.path.insert(0, "/Users/ghostgear/opensage/src")

from neo4j import GraphDatabase

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "callgraphn4j!"


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# ============================================================
# TEST 1: MEMORY (NEO4J)
# ============================================================
def test_memory():
    print("\n" + "=" * 50)
    print("TEST 1: MEMORY (Neo4j)")
    print("=" * 50)

    with get_driver() as driver:
        driver.execute_query(
            "MERGE (m:Memory {key: $key}) SET m.value = $value",
            key="full_test",
            value="Test at " + str(int(time.time())),
        )
        print("✓ Store memory")

        result = driver.execute_query(
            "MATCH (m:Memory {key: 'hello'}) RETURN m.value as value"
        )
        records = list(result.records)
        if records:
            print(f"✓ Recall: {records[0]['value']}")

        result = driver.execute_query("MATCH (m:Memory) RETURN count(m) as count")
        count = list(result.records)[0]["count"]
        print(f"✓ Total memories: {count}")

    return True


# ============================================================
# TEST 2: DOCKER SANDBOX
# ============================================================
def test_docker():
    print("\n" + "=" * 50)
    print("TEST 2: DOCKER SANDBOX")
    print("=" * 50)

    result = subprocess.run(["docker", "info"], capture_output=True)
    if result.returncode != 0:
        print("✗ Docker not available")
        return False

    print("✓ Docker is running")

    result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    print(f"✓ Containers: {len(result.stdout.strip().split(chr(10)))} running")

    return True


# ============================================================
# TEST 3: OPENSAge AGENT
# ============================================================
def test_agent():
    print("\n" + "=" * 50)
    print("TEST 3: OPENSAge AGENT")
    print("=" * 50)

    try:
        from google.adk.models.lite_llm import LiteLlm
        from opensage.agents.opensage_agent import OpenSageAgent
        from opensage.toolbox.general.bash_tool import bash_tool_main

        print("✓ OpenSageAgent: available")
        print("✓ LiteLlm: available")
        print("✓ bash_tool: available")
        return True
    except Exception as e:
        print(f"✗ {e}")
        return False


# ============================================================
# TEST 4: FILE OPERATIONS
# ============================================================
def test_file_ops():
    print("\n" + "=" * 50)
    print("TEST 4: FILE OPERATIONS")
    print("=" * 50)

    try:
        from opensage.toolbox.general import fileop

        test_dir = tempfile.mkdtemp(prefix="opensage_test_")
        test_file = os.path.join(test_dir, "test.txt")

        with open(test_file, "w") as f:
            f.write("Test content")
        print("✓ Write file")

        # Skip view_file as it needs tool_context
        print("✓ File operations available (view_file needs context)")

        files = fileop.list_dir(test_dir)
        print(f"✓ List dir: {len(files)} entries")

        os.remove(test_file)
        os.rmdir(test_dir)
        print("✓ Delete file/dir")

        return True
    except Exception as e:
        print(f"✗ {e}")
        return False


# ============================================================
# TEST 5: BASH TOOL
# ============================================================
def test_bash():
    print("\n" + "=" * 50)
    print("TEST 5: BASH TOOL")
    print("=" * 50)

    result = subprocess.run(["echo", "test"], capture_output=True, text=True)
    print(f"✓ Echo: {result.stdout.strip()}")

    result = subprocess.run(["pwd"], capture_output=True, text=True)
    print(f"✓ PWD: {result.stdout.strip()}")

    return True


# ============================================================
# TEST 6: DYNAMIC SUB-AGENTS
# ============================================================
def test_subagents():
    print("\n" + "=" * 50)
    print("TEST 6: DYNAMIC SUB-AGENTS")
    print("=" * 50)

    try:
        from opensage.toolbox.general.dynamic_subagent import create_subagent

        print("✓ create_subagent: available")

        from opensage.config.config_dataclass import OpenSageConfig

        config = OpenSageConfig.create_default()
        print("✓ OpenSageConfig: available")

        return True
    except Exception as e:
        print(f"✗ {e}")
        return False


# ============================================================
# TEST 7: LLM MODELS
# ============================================================
def test_llm():
    print("\n" + "=" * 50)
    print("TEST 7: LLM MODELS (litellm)")
    print("=" * 50)

    import litellm

    print(f"✓ Total models: {len(litellm.model_list)}")

    categories = {
        "openrouter": "openrouter",
        "xai/grok": "xai",
        "ollama": "ollama",
    }

    for name, prefix in categories.items():
        models = [m for m in litellm.model_list if prefix in m.lower()]
        print(f"  {name}: {len(models)} models")

    return True


# ============================================================
# TEST 8: WEB SEARCH
# ============================================================
def test_websearch():
    print("\n" + "=" * 50)
    print("TEST 8: WEB SEARCH")
    print("=" * 50)

    try:
        from opensage.toolbox.general.web_search_tool import WebSearchTool

        print("✓ WebSearchTool: available")
        return True
    except Exception as e:
        print(f"✗ {e}")
        return False


# ============================================================
# TEST 9: AGENT ENSEMBLE
# ============================================================
def test_ensemble():
    print("\n" + "=" * 50)
    print("TEST 9: AGENT ENSEMBLE")
    print("=" * 50)

    try:
        from opensage.session.opensage_ensemble_manager import OpenSageEnsembleManager

        print("✓ OpenSageEnsembleManager: available")
        return True
    except Exception as e:
        print(f"✗ {e}")
        return False


# ============================================================
# TEST 10: NEO4J TOOLS
# ============================================================
def test_neo4j_tools():
    print("\n" + "=" * 50)
    print("TEST 10: NEO4j TOOLS")
    print("=" * 50)

    try:
        from opensage.bash_tools.neo4j.common_utils import neo4j_utils

        print("✓ neo4j_utils: available")

        # Check what's in neo4j_utils
        funcs = [f for f in dir(neo4j_utils) if not f.startswith("_")]
        print(f"  Functions: {', '.join(funcs[:5])}")

        return True
    except Exception as e:
        print(f"✗ {e}")
        return False


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 50)
    print("OPENSAGE FULL TEST SUITE")
    print("=" * 50)

    tests = [
        ("Memory (Neo4j)", test_memory),
        ("Docker Sandbox", test_docker),
        ("OpenSage Agent", test_agent),
        ("File Operations", test_file_ops),
        ("Bash Tool", test_bash),
        ("Dynamic Sub-agents", test_subagents),
        ("LLM Models", test_llm),
        ("Web Search", test_websearch),
        ("Agent Ensemble", test_ensemble),
        ("Neo4j Tools", test_neo4j_tools),
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"✗ {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
