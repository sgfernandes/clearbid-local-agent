#!/usr/bin/env python3
"""Sandboxed Agent Server - runs inside Lima VM, listens on TCP port 9999"""

import asyncio
import json
import os

PORT = 9999
HOST = "0.0.0.0"


async def handle_prompt(prompt: str) -> dict:
    """Process a prompt using Claude Agent SDK."""
    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            ResultMessage,
            TextBlock,
            query,
        )
    except ImportError:
        return {"type": "error", "error": "claude-agent-sdk not installed"}

    mcp_servers = {}
    playwright_url = os.environ.get("PLAYWRIGHT_MCP_URL")
    if playwright_url:
        mcp_servers["playwright"] = {"type": "sse", "url": playwright_url}

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        mcp_servers=mcp_servers,
        cwd=os.getcwd(),
    )

    response_text = []
    total_cost = 0.0

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text.append(block.text)
            elif isinstance(message, ResultMessage):
                total_cost = message.total_cost_usd or 0.0

        return {
            "type": "response",
            "text": "\n".join(response_text),
            "cost_usd": total_cost,
        }
    except Exception as e:
        return {"type": "error", "error": str(e)}


async def handle_message(msg: dict) -> dict:
    """Route incoming messages to appropriate handlers."""
    msg_type = msg.get("type")
    if msg_type == "ping":
        return {"type": "pong"}
    elif msg_type == "prompt":
        return await handle_prompt(msg.get("prompt", ""))
    else:
        return {"type": "error", "error": f"Unknown message type: {msg_type}"}


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle a connected client."""
    try:
        while True:
            length_bytes = await reader.readexactly(4)
            length = int.from_bytes(length_bytes, "big")
            data = await reader.readexactly(length)
            msg = json.loads(data.decode("utf-8"))

            response = await handle_message(msg)

            response_bytes = json.dumps(response).encode("utf-8")
            writer.write(len(response_bytes).to_bytes(4, "big"))
            writer.write(response_bytes)
            await writer.drain()
    except asyncio.IncompleteReadError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"Agent listening on {HOST}:{PORT}", flush=True)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
