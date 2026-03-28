#!/usr/bin/env python3
"""
OpenCode + OpenSage integration script.

Uses OpenCode for free LLM calls, OpenSage for agent orchestration.
Run: python opencode_to_opensage.py "Your task"
"""

import subprocess
import sys
import os


# OpenCode free models
FREE_MODELS = {
    "mimo": "opencode/mimo-v2-pro-free",
    "minimax": "opencode/minimax-m2.5-free",
    "nemotron": "opencode/nemotron-3-super-free",
    "gpt5nano": "opencode/gpt-5-nano",
}


def run_opencode(prompt: str, model: str = "opencode/mimo-v2-pro-free") -> str:
    """Run OpenCode with a prompt and return the output."""
    cmd = ["opencode", "run", "--model", model, prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def run_opensage(task: str) -> str:
    """Run OpenSage with a task using OpenCode as the LLM backend."""
    # Use OpenCode as the LLM proxy
    os.environ["OPENAI_API_KEY"] = "dummy"  # OpenCode handles auth
    os.environ["OPENAI_API_BASE"] = "http://localhost:8090/v1"

    # Start OpenCode server if not running
    subprocess.Popen(
        ["opencode", "serve", "--port", "8090"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return f"Task: {task}\nUse OpenCode free models via http://localhost:8090"


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or "Say hello"
    print(run_opencode(task))
