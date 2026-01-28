# CLAUDE.md

Sandboxed AI agent running in a Lima VM with TCP-based RPC.

## Structure

```
local-agent/
├── client              # CLI tool (Python, runs on host)
├── sandbox/
│   └── agent.py        # Agent server (runs in VM at /opt/agent)
├── sandbox.yaml        # Lima VM config (Ubuntu 24.04, 2 CPU, 4GB RAM)
├── Makefile            # VM lifecycle commands
├── LIMITATIONS.md      # Known limitations and next steps
├── .env                # ANTHROPIC_API_KEY (git-ignored)
└── .env.example        # Template for .env
```

## Makefile Commands

```bash
make create       # Create Lima VM from sandbox.yaml
make start        # Start VM, launch agent, verify with ping
make stop         # Stop VM gracefully
make status       # Show VM status
make clean        # Stop and delete VM
make install-sdk  # Install claude-agent-sdk in VM
```

## Client Commands

```bash
./client ping              # Health check
./client exec <command>    # Run shell command in sandbox (30s timeout)
./client prompt <text>     # Send prompt to Claude (needs SDK)
./client chat              # Interactive multi-turn conversation
```

## Protocol

TCP on 127.0.0.1:9999 with length-prefixed JSON frames (4-byte big-endian).

**Request types:**
- `{"type": "ping"}`
- `{"type": "exec", "command": "...", "cwd": "..."}`
- `{"type": "prompt", "prompt": "..."}`

**Agent SDK tools:** Read, Write, Edit, Bash, Glob, Grep (acceptEdits mode)

## Mounts

The VM has minimal mounts for security:
- `/mnt/desktop` - User's `~/Desktop` (writable)
- `/opt/agent` - Agent code (read-only)

See LIMITATIONS.md for dynamic mount limitations.

## Setup

1. `cp .env.example .env` and add your API key
2. `brew install lima`
3. `make create && make start`
4. `make install-sdk` (for prompt/chat commands)
