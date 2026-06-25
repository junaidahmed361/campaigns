from campaigns import DogfoodExecutionRunner, OutcomeRequest


def test_dogfood_exec_reserves_resources_and_returns_provider_response_with_custom_driver():
    result = DogfoodExecutionRunner().run(
        OutcomeRequest(
            goal="Produce a provider response artifact for onboarding",
            budget_dollars=25,
            constraints=("no real payment", "do not expose provider choice"),
            quality_requirements=("provider response returned", "receipt produced"),
        ),
        resource_limit_dollars=25,
        reserve_dollars=2.5,
        driver_command="printf 'PROVIDER_RESPONSE: capability artifact accepted'",
    )

    assert result.status == "provider_response_received"
    assert result.reservation.accepted is True
    assert result.reservation.real_payment_processor is False
    assert result.driver_response.usable is True
    assert "PROVIDER_RESPONSE" in result.driver_response.provider_response
    assert result.plan.provider_complexity_exposed is False


def test_dogfood_exec_blocks_when_resource_reservation_exceeds_policy_limit():
    result = DogfoodExecutionRunner().run(
        OutcomeRequest(goal="Do too much", budget_dollars=1),
        resource_limit_dollars=1,
        reserve_dollars=2,
        driver_command="printf should-not-run",
    )

    assert result.status == "blocked_budget_reservation"
    assert result.reservation.accepted is False
    assert result.driver_response.usable is False
