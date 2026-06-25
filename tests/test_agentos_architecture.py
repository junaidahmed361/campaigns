from campaigns import (
    CostOfQualitySample,
    ImmutableReceipt,
    RoutingObjective,
    phase0_artifact_specs,
    phase0_capability_contracts,
)


def test_phase0_capabilities_are_contracts_not_providers():
    contracts = phase0_capability_contracts()
    backend = next(contract for contract in contracts if contract.name == "backend.api")

    assert "repository" in backend.requires
    assert "source_code" in backend.produces
    assert "compile" in backend.evaluators
    assert all("provider" not in contract.name for contract in contracts)


def test_every_phase0_capability_produces_measurable_artifacts():
    contracts = phase0_capability_contracts()
    artifacts = phase0_artifact_specs()
    producing_capabilities = {artifact.produced_by_capability for artifact in artifacts}

    assert {contract.name for contract in contracts} <= producing_capabilities
    assert all(artifact.measurable_by for artifact in artifacts)


def test_receipts_are_append_only_repair_chain():
    first = ImmutableReceipt(
        receipt_id="receipt-1",
        sequence=1,
        subject="backend.api/customer-endpoint",
        artifact_ids=("artifact-code-1",),
        evaluator_results=("tests:fail",),
    )
    repair = first.append_repair("receipt-2", ("artifact-code-2",), ("tests:pass",))

    assert first.sequence == 1
    assert repair.sequence == 2
    assert repair.parent_receipt_id == "receipt-1"
    assert repair.supersedes == ("receipt-1",)


def test_cost_of_quality_and_euv_are_first_class_metrics():
    before = CostOfQualitySample(iteration=1, quality_score=81, cumulative_cost=0.40)
    after = CostOfQualitySample(iteration=2, quality_score=92, cumulative_cost=0.65)
    objective = RoutingObjective(expected_user_value=120, expected_cost=3, rationale="highest accepted quality per dollar")

    assert round(after.marginal_gain_per_dollar(before), 2) == 44.0
    assert objective.euv_per_dollar == 40
