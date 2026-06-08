from campaigns import CampaignAutorun, AutorunPolicy


def test_goal_driven_loop_owns_progress_checks_and_saves_resume_state_on_budget():
    runner = CampaignAutorun(
        policy=AutorunPolicy(max_loops=3, step_budget=1, require_ultimate_review=True)
    ).fit(
        {
            "objective": "Launch a car detailing campaign that books 10 appointments",
            "metrics": ["10 booked appointments", "human approved campaign packet"],
            "employed_harnesses": [
                {
                    "agent_name": "Market Researcher",
                    "role": "market_researcher",
                    "objective": "Research local demand with trace evidence",
                    "agentrl_project_path": "agentrl://targeted-agents/market-researcher",
                }
            ],
        }
    )

    result = runner.autorun()

    assert result.status == "paused_budget_exhausted"
    assert result.policy.second_model_evaluator == "goal_satisfaction_check"
    assert result.policy.independent_final_auditor == "ultimate_review_auditor"
    assert result.iterations[0].goal_check.question == "Has the campaign goal been met?"
    assert result.iterations[0].goal_check.met is False
    assert result.resume_state is not None
    assert result.resume_state["next_step"] == "resume_goal_loop"
    assert "what_is_left" in result.resume_state


def test_final_review_triggers_agent_driven_trace_retro_and_reinforcement_plan():
    runner = CampaignAutorun().fit(
        {
            "objective": "Run a marketing campaign with traceable research",
            "employed_harnesses": [
                {
                    "agent_name": "Market Researcher",
                    "role": "market_researcher",
                    "objective": "Research local demand with RAG evidence",
                    "agentrl_project_path": "agentrl://targeted-agents/market-researcher",
                },
                {
                    "agent_name": "Analytics Agent",
                    "role": "analytics",
                    "objective": "Track booking outcomes",
                    "agentrl_project_path": "agentrl://targeted-agents/analytics-agent",
                },
            ],
        }
    )
    runner.autorun(max_loops=1)

    retro = runner.final_review(
        accepted=False,
        feedback="Final review found weak competitor pricing evidence in the Market Researcher trace.",
    )

    assert retro.status == "self_reinforcement_planned"
    assert retro.actions[0].owner == "agentrl"
    assert retro.actions[0].target == "Market Researcher"
    assert retro.actions[0].agentrl_project_path == "agentrl://targeted-agents/market-researcher"
    assert "root_cause" in retro.context
    assert "competitor pricing evidence" in retro.actions[0].instruction
    assert "trace_paths" in retro.context["root_cause"]
