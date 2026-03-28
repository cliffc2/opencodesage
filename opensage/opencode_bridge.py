"""OpenCode provider bridge for OpenSage.

Uses OpenCode's provider system as an LLM backend for OpenSage agents.
OpenCode handles free provider switching; OpenSage handles agent orchestration.
"""

import asyncio
import json
import subprocess
from typing import Optional


class OpenCodeProviderBridge:
    """Bridge OpenCode's free provider switching into OpenSage."""

    def __init__(self, model: str = "xai/grok-4-1-fast"):
        self.model = model

    async def call(self, messages: list, temperature: float = 0.7) -> str:
        """Call OpenCode's run command with messages."""
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

        cmd = ["opencode", "run", "--model", self.model, prompt]

        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"OpenCode error: {stderr.decode()}")

        return stdout.decode().strip()


# Usage example:
# bridge = OpenCodeProviderBridge(model="anthropic/claude-sonnet-4")
# response = await bridge.call([{"role": "user", "content": "Fix this bug"}])
