from __future__ import annotations

import json
import sys
from typing import Any

from .hermes_adapter import HermesAdapter, TOOL_NAMES


class AgentOSMCPServer:
    """Tiny stdio JSON tool server scaffold for Phase 0 Hermes dogfooding.

    This is intentionally minimal and dependency-free. It exposes the same thin
    Hermes adapter methods that a full MCP server should publish; the Campaign
    Kernel remains the state owner behind the adapter.
    """

    def __init__(self, adapter: HermesAdapter | None = None):
        self.adapter = adapter or HermesAdapter()

    def list_tools(self) -> dict[str, Any]:
        return {
            "tools": [
                {"name": name, "description": f"AgentOS Campaign Kernel tool: {name}"}
                for name in TOOL_NAMES
            ]
        }

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if name not in TOOL_NAMES:
            return {"error": f"unknown tool: {name}"}
        method = getattr(self.adapter, name)
        arguments = arguments or {}
        result = method(**arguments)
        return {"tool": name, "result": result, "source_of_record": "campaign_kernel"}

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        method = message.get("method")
        if method in {"tools/list", "list_tools"}:
            return self.list_tools()
        if method in {"tools/call", "call_tool"}:
            params = message.get("params", {})
            return self.call_tool(params.get("name", ""), params.get("arguments", {}))
        return {"error": f"unknown method: {method}"}


def main() -> int:
    server = AgentOSMCPServer()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = server.handle(json.loads(line))
        except Exception as exc:  # pragma: no cover - defensive stdio server boundary
            response = {"error": str(exc)}
        print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
