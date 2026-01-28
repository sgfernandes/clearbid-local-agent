# local-agent

Sandboxed AI agent with browser automation. Agent runs in a Lima VM and controls Chrome via Playwright MCP.

## Requirements

- macOS
- [Lima](https://lima-vm.io/): `brew install lima`
- Chrome with Playwright MCP Bridge extension
- Anthropic API key

## Setup

```bash
# 1. Create VM (one-time)
make create
```

2. Install the [Playwright MCP Bridge](https://github.com/microsoft/playwright-mcp/releases) Chrome extension: download the latest release, unzip, and load unpacked in `chrome://extensions`.

```bash
# 3. Configure API key
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

## Run

```bash
make start
./client prompt "go to google news and summarize the headlines in /mnt/desktop/news.txt"
```

## Commands

```bash
make create          # Create VM and install SDK (one-time)
make start           # Start Playwright MCP + VM + agent
make stop            # Stop everything
make status          # Show status
make clean           # Delete VM
./client ping        # Health check
./client prompt "…"  # Send prompt to agent
```
