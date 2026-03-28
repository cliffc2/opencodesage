#!/usr/bin/env python3
"""
Dynamic OpenCode LLM Bridge for OpenSage

This bridge automatically uses the same model as OpenCode's current model.
It reads from a config file that OpenCode can update.

Usage:
    1. Start bridge: python opencode_dynamic_bridge.py
    2. Set model: echo "opencode/mimo-v2-pro-free" > ~/.opencode/current_model
    3. OpenSage uses whatever model is in that file

The model syncs automatically - change model in one place, both use it.
"""

import subprocess
import json
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler


MODEL_FILE = os.path.expanduser("~/.opencode/current_model")
DEFAULT_MODEL = "opencode/minimax-m2.5-free"


def get_current_model():
    """Read current model from file."""
    try:
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, "r") as f:
                model = f.read().strip()
                if model:
                    return model
    except:
        pass
    return DEFAULT_MODEL


def set_model(model):
    """Set current model (call this when OpenCode changes model)."""
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    with open(MODEL_FILE, "w") as f:
        f.write(model)


class OpenCodeLLM:
    """OpenCode CLI wrapper with dynamic model."""

    def complete(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        model = get_current_model()
        cmd = ["opencode", "run", "--model", model, prompt]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {str(e)}"


llm = OpenCodeLLM()


class Handler(BaseHTTPRequestHandler):
    """HTTP handler for OpenAI-compatible API."""

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
            messages = request.get("messages", [])
            temperature = request.get("temperature", 0.7)

            # Use model from file (dynamic!)
            model = get_current_model()

            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

            response = llm.complete(prompt, temperature)

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

    def do_GET(self):
        """Return current model info."""
        model = get_current_model()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"current_model": model, "model_file": MODEL_FILE}).encode()
        )


def main():
    # Set default model
    set_model(DEFAULT_MODEL)

    port = 5557
    server = HTTPServer(("127.0.0.1", port), Handler)

    print(f"Dynamic OpenCode Bridge running on http://127.0.0.1:{port}")
    print(f"Model file: {MODEL_FILE}")
    print(f"Current model: {get_current_model()}")
    print("\nTo change model:")
    print(f'  echo "opencode/gpt-5-nano" > {MODEL_FILE}')
    print(f"\nTo check current model:")
    print(f"  curl http://127.0.0.1:{port}/")
    print("\nAPI endpoint:")
    print(f"  POST http://127.0.0.1:{port}/v1/chat/completions")

    server.serve_forever()


if __name__ == "__main__":
    main()
