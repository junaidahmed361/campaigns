from campaigns import CampaignAutorun, CampaignSpec


def test_campaign_autorun_uses_sklearn_style_fit_transform_score():
    campaign = CampaignSpec.from_dict(
        {
            "objective": "Run a marketing campaign with researcher and RAG harnesses",
            "metrics": ["qualified_leads"],
            "employed_harnesses": [
                {
                    "agent_name": "Market Researcher",
                    "role": "market_researcher",
                    "objective": "Research market demand with RAG evidence",
                    "components": ["rag", "trace", "decision_log", "evaluation"],
                },
                {
                    "agent_name": "RAG Analyst",
                    "role": "rag_analyst",
                    "objective": "Retrieve evidence for campaign assumptions",
                    "components": ["rag", "trace", "evaluation"],
                },
            ],
        }
    )

    runner = CampaignAutorun().fit(campaign)
    dossier = runner.transform()

    assert runner.score() == 1.0
    assert dossier.workflow[0].id == "create_harness"
    assert {agent.name for team in dossier.organization.teams for agent in team.agents} >= {"Market Researcher", "RAG Analyst"}


def test_autorun_records_claude_style_dynamic_loops_without_runtime_overlap():
    result = CampaignAutorun().fit({"objective": "Run a marketing campaign", "metrics": ["revenue"]}).autorun(max_loops=2)

    assert result.status == "awaiting_ultimate_review"
    assert [iteration.phase for iteration in result.iterations] == [
        "observe_plan_act_verify_review",
        "observe_plan_act_verify_review",
    ]
    assert result.iterations[-1].stop_reason == "approval_required"
    assert "performance_review" in result.iterations[-1].selected_steps
    assert "campaign outcome summary" in result.iterations[-1].review_packet
