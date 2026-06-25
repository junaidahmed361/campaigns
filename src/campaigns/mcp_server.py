from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .hermes_adapter import HermesAdapter, TOOL_NAMES


class AgentOSMCPServer:
    """In-process facade used by tests and the FastMCP tool handlers."""

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


_server = AgentOSMCPServer()
mcp = FastMCP("agentos")


@mcp.tool()
def create_campaign(goal: str, execution_policy: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create an AgentOS campaign from a goal and execution policy."""

    return _server.call_tool("create_campaign", {"goal": goal, "execution_policy": execution_policy})


@mcp.tool()
def list_campaigns() -> dict[str, Any]:
    """List campaigns owned by the Campaign Kernel."""

    return _server.call_tool("list_campaigns")


@mcp.tool()
def campaign_status(campaign_id: str) -> dict[str, Any]:
    """Read campaign status from the Campaign Kernel."""

    return _server.call_tool("campaign_status", {"campaign_id": campaign_id})


@mcp.tool()
def approve(approval_id: str) -> dict[str, Any]:
    """Approve a pending Campaign Kernel approval gate."""

    return _server.call_tool("approve", {"approval_id": approval_id})


@mcp.tool()
def reject(approval_id: str) -> dict[str, Any]:
    """Reject a pending Campaign Kernel approval gate."""

    return _server.call_tool("reject", {"approval_id": approval_id})


@mcp.tool()
def list_artifacts(campaign_id: str) -> dict[str, Any]:
    """List artifacts for a campaign."""

    return _server.call_tool("list_artifacts", {"campaign_id": campaign_id})


@mcp.tool()
def open_artifact(artifact_id: str) -> dict[str, Any]:
    """Open artifact metadata/content from the Campaign Kernel."""

    return _server.call_tool("open_artifact", {"artifact_id": artifact_id})


@mcp.tool()
def receipt(campaign_id: str) -> dict[str, Any]:
    """Read an immutable campaign receipt."""

    return _server.call_tool("receipt", {"campaign_id": campaign_id})


@mcp.tool()
def execution_policy_get() -> dict[str, Any]:
    """Read the active execution policy."""

    return _server.call_tool("execution_policy_get")


@mcp.tool()
def execution_policy_update(execution_policy: dict[str, Any]) -> dict[str, Any]:
    """Update an execution policy through the Campaign Kernel boundary."""

    return _server.call_tool("execution_policy_update", {"execution_policy": execution_policy})


def main() -> int:
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
