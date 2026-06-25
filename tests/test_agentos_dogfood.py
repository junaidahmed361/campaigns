from campaigns import AgentOSDogfoodRunner, OutcomeRequest


def test_agentos_dogfood_accepts_outcome_budget_constraints_quality_without_provider():
    result = AgentOSDogfoodRunner().run(
        OutcomeRequest(
            goal="Ship an evaluated backend API for campaign receipts",
            budget_dollars=25,
            constraints=("no provider selection in user prompt", "immutable receipts"),
            quality_requirements=("tests pass", "receipt provenance is replayable"),
            sla="same day",
        )
    )

    assert result.status == "awaiting_user_review"
    assert result.provider_complexity_exposed is False
    assert "backend.api" in result.selected_capabilities
    assert result.request.goal.startswith("Ship an evaluated backend API")
    assert result.routing_objective.euv_per_dollar > 0
    assert result.receipt.artifact_ids
    assert any(artifact.kind == "evaluation_plan" for artifact in result.artifacts)


def test_agentos_dogfood_outputs_measurable_artifacts_and_receipt():
    result = AgentOSDogfoodRunner().run(
        {
            "agentos": {
                "goal": "Launch a local growth campaign",
                "budget": {"dollars": 10},
                "constraints": ["human approval before spend"],
                "quality_requirements": ["all artifacts measurable"],
            }
        }
    )

    assert all(artifact.measurable_by for artifact in result.artifacts)
    assert result.receipt.sequence == 1
    assert "provider_complexity_exposed:false" in result.receipt.evaluator_results
    assert "planning.dag" in result.selected_capabilities
    assert "evaluation.quality_gate" in result.selected_capabilities
