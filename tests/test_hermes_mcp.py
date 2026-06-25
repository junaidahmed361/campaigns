from campaigns import AgentOSMCPServer, HermesAdapter


def test_hermes_adapter_is_thin_client_to_campaign_kernel_state():
    adapter = HermesAdapter()
    result = adapter.create_campaign(
        "Dogfood through Hermes",
        {"per_campaign_limit_usd": 25, "prefer_local": True},
    )

    assert result["client_boundary"].startswith("Hermes is a thin client")
    assert result["execution_policy"]["per_campaign_limit_usd"] == 25
    assert result["provider_complexity_exposed"] is False


def test_mcp_server_exposes_required_hermes_tools():
    server = AgentOSMCPServer(HermesAdapter())
    tools = {tool["name"] for tool in server.list_tools()["tools"]}

    assert {
        "create_campaign",
        "list_campaigns",
        "campaign_status",
        "approve",
        "reject",
        "list_artifacts",
        "open_artifact",
        "receipt",
        "execution_policy_get",
        "execution_policy_update",
    } <= tools


def test_mcp_tool_call_returns_kernel_source_of_record():
    server = AgentOSMCPServer(HermesAdapter())
    result = server.call_tool("execution_policy_get")

    assert result["source_of_record"] == "campaign_kernel"
    assert result["result"]["name"] == "local-byok-default"
