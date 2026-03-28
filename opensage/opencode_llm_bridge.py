#!/usr/bin/env python3
"""
OpenCode LLM Provider Bridge for OpenSage

Allows OpenSage to use OpenCode's free models via CLI bridge.
This routes LLM calls through opencode run command.

Usage:
    1. Start this bridge: python opencode_llm_bridge.py
    2. Use in OpenSage config or code

The bridge provides an OpenAI-compatible API at http://localhost:5556
"""

import subprocess
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse


class OpenCodeLLM:
    """OpenCode CLI wrapper for LLM calls."""

    def __init__(self, model="opencode/mimo-v2-pro-free"):
        self.model = model

    def complete(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        """Call OpenCode CLI and return the response."""
        cmd = ["opencode", "run", "--model", self.model, prompt]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {str(e)}"


# Global LLM instance
llm = OpenCodeLLM()


class Handler(BaseHTTPRequestHandler):
    """HTTP handler for OpenAI-compatible API."""

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        # Read request
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
            messages = request.get("messages", [])
            model = request.get("model", "opencode/mimo-v2-pro-free")
            temperature = request.get("temperature", 0.7)

            # Build prompt from messages
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

            # Call OpenCode
            llm.model = model
            response = llm.complete(prompt, temperature)

            # Return OpenAI-compatible response
            result = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": response},
                        "finish_reason": "stop",
                    }
                ],
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        pass  # Suppress logging


def test_opencode():
    """Test OpenCode CLI directly."""
    print("Testing OpenCode CLI...")

    # Test with different models
    models = [
        "opencode/mimo-v2-pro-free",
        "opencode/minimax-m2.5-free",
        "opencode/gpt-5-nano",
    ]

    for model in models:
        print(f"\n--- Testing {model} ---")
        llm.model = model
        result = llm.complete("Say 'test successful' in 3 words")
        print(f"Result: {result[:100]}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_opencode()
    else:
        # Start server
        port = 5556
        server = HTTPServer(("127.0.0.1", port), Handler)
        print(f"OpenCode LLM Bridge running on http://127.0.0.1:{port}")
        print("Endpoints:")
        print(f"  POST http://127.0.0.1:{port}/v1/chat/completions")
        print("\nExample curl:")
        print(f"curl -X POST http://127.0.0.1:{port}/v1/chat/completions \\")
        print('  -H "Content-Type: application/json" \\')
        print(
            '  -d \'{"model": "opencode/mimo-v2-pro-free", "messages": [{"role": "user", "content": "Hi"}]}\''
        )
        server.serve_forever()
