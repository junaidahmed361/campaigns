from campaigns import CampaignAutorun, RetrospectiveFeedback


def test_campaign_retro_routes_campaign_level_learning_to_next_iteration():
    runner = CampaignAutorun().fit({"objective": "Get more booked detailing appointments", "metrics": ["booked_appointments"]})
    result = runner.autorun(max_loops=1)

    retro = runner.retro(
        RetrospectiveFeedback(
            summary="The campaign strategy was too broad for mobile car detailing buyers.",
            attention_level="campaign",
            target="Local Lead Generation",
            outcome="underperformed",
            reinforce="Narrow audience to mobile detailing searches and add stronger booking CTA.",
        )
    )

    assert retro.status == "reinforcement_planned"
    assert retro.feedback.attention_level == "campaign"
    assert retro.actions[0].owner == "campaigns"
    assert retro.actions[0].target == "campaign_strategy"
    assert "next campaign iteration" in retro.actions[0].instruction
    assert result.dossier.campaign.objective in retro.context["campaign_objective"]


def test_campaign_retro_routes_agent_attention_to_agentrl_reinforcement():
    runner = CampaignAutorun().fit(
        {
            "objective": "Run a marketing campaign with a market researcher",
            "employed_harnesses": [
                {
                    "agent_name": "Market Researcher",
                    "role": "market_researcher",
                    "objective": "Research local demand with RAG evidence",
                    "components": ["rag", "trace", "evaluation"],
                    "agentrl_project_path": "agentrl://targeted-agents/market-researcher",
                }
            ],
        }
    )
    runner.autorun(max_loops=1)

    retro = runner.retro(
        {
            "summary": "Research missed competitor pricing evidence.",
            "attention_level": "agentrl",
            "target": "Market Researcher",
            "outcome": "needs_improvement",
            "reinforce": "Require competitor price citations before recommendations.",
        }
    )

    assert retro.actions[0].owner == "agentrl"
    assert retro.actions[0].target == "Market Researcher"
    assert retro.actions[0].agentrl_project_path == "agentrl://targeted-agents/market-researcher"
    assert retro.actions[0].reinforcement_targets == ("evaluation", "memory", "prompts")
    assert "competitor price citations" in retro.actions[0].instruction
