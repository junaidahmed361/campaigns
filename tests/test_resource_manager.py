from campaigns import ExecutionPolicy, ResourceManager


def test_resource_manager_reserves_without_payment_wallet():
    manager = ResourceManager(ExecutionPolicy.default_local_byok(campaign_limit_usd=25))
    reservation = manager.reserve_usd(2.5)

    assert reservation.accepted is True
    assert reservation.real_payment_processor is False
    assert reservation.resource_type == "usd"
    assert reservation.remaining_amount == 22.5
    assert manager.usage()["real_payment_processor"] is False


def test_resource_manager_blocks_over_policy_limit():
    manager = ResourceManager(ExecutionPolicy.default_local_byok(campaign_limit_usd=1))
    reservation = manager.reserve_usd(2.5)

    assert reservation.accepted is False
    assert reservation.reserved_amount == 0
    assert "resource ceiling" in (reservation.reason or "")


def test_execution_policy_models_subscription_and_local_providers():
    policy = ExecutionPolicy.default_local_byok(campaign_limit_usd=25)

    assert policy.provider_rules["claude_code"]["pricing_model"] == "subscription"
    assert policy.provider_rules["codex"]["pricing_model"] == "subscription"
    assert policy.provider_rules["ollama"]["pricing_model"] == "local"
    assert policy.prefer_subscription_providers is True
