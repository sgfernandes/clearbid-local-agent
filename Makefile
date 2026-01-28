-include .env

.PHONY: create start stop status clean

VM_NAME := agent
PLAYWRIGHT_MCP_URL := http://host.lima.internal:8931/sse

create:
	limactl create --name=$(VM_NAME) sandbox.yaml
	limactl start $(VM_NAME)
	limactl shell $(VM_NAME) -- pip3 install --user --break-system-packages claude-agent-sdk
	limactl stop $(VM_NAME)

start:
	@test -n "$(ANTHROPIC_API_KEY)" || (echo "Error: ANTHROPIC_API_KEY not set" && exit 1)
	@echo "Starting Playwright MCP server..."
	@pkill -f "@playwright/mcp" 2>/dev/null || true
	@npx @playwright/mcp@latest --extension --port 8931 --host 0.0.0.0 --allowed-hosts '*' &
	@sleep 2
	@limactl start $(VM_NAME)
	@echo "Starting agent..."
	@limactl shell $(VM_NAME) -- ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY) PLAYWRIGHT_MCP_URL=$(PLAYWRIGHT_MCP_URL) nohup python3 /opt/agent/agent.py > /tmp/agent.log 2>&1 &
	@sleep 2
	@./client ping && echo "Ready. Use: ./client prompt '...'"

stop:
	@limactl stop $(VM_NAME) 2>/dev/null || true
	@pkill -f "@playwright/mcp" 2>/dev/null || true
	@echo "Stopped"

status:
	@limactl list | grep -E "NAME|$(VM_NAME)" || echo "VM not found"
	@lsof -i :8931 2>/dev/null | grep -q LISTEN && echo "Playwright MCP: running" || echo "Playwright MCP: stopped"

clean:
	@limactl stop $(VM_NAME) 2>/dev/null || true
	@limactl delete $(VM_NAME) -f 2>/dev/null || true
	@pkill -f "@playwright/mcp" 2>/dev/null || true
