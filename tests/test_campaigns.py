from campaigns import CampaignCompiler, CampaignSpec, OrganizationBlueprint


def test_growth_campaign_compiles_to_accountable_dag_with_contract_agents():
    campaign = CampaignSpec.from_dict(
        {
            "campaign": {
                "objective": "Increase recurring revenue by 30%",
                "budget": {"dollars": 5000},
                "timeline": {"days": 90},
                "metrics": ["revenue", "conversions"],
                "constraints": ["human approval for spend > $500"],
                "employed_harnesses": [
                    {
                        "agent_name": "Market Researcher",
                        "role": "market_researcher",
                        "objective": "Research the market with RAG-grounded evidence",
                        "components": ["rag", "trace", "decision_log", "evaluation"],
                    }
                ],
            }
        }
    )

    dossier = CampaignCompiler().compile(campaign)

    assert dossier.campaign.objective == "Increase recurring revenue by 30%"
    assert dossier.approval_gates == ("human approval for spend > $500",)
    assert dossier.contracts
    assert {step.id for step in dossier.workflow} >= {
        "create_harness",
        "employ_fleet",
        "contract",
        "synthesize",
        "performance_review",
        "ultimate_review",
        "evolve",
    }
    assert dossier.trace_monitor.scope == "fleet_and_contract_agents"
    assert "contract-agent deliverables and traces" in dossier.final_review_packet


def test_default_growth_blueprint_employs_user_harness_and_agentrl_pods():
    campaign = CampaignSpec.from_dict(
        {
            "objective": "Grow my business revenue",
            "metrics": ["revenue"],
            "employed_harnesses": [
                {
                    "agent_name": "Market Researcher",
                    "role": "market_researcher",
                    "objective": "Support a campaign with RAG research",
                    "components": ["rag", "trace", "evaluation"],
                }
            ],
        }
    )

    org = OrganizationBlueprint.default_for(campaign)

    agents = [agent for team in org.teams for agent in team.agents]
    assert "Market Researcher" in {agent.name for agent in agents}
    assert all(agent.review_obligations for agent in agents)
    assert all(agent.pod.lifecycle_owner() == "agentrl" for agent in agents)
    market = next(agent for agent in agents if agent.name == "Market Researcher")
    assert market.pod.harness_components == ("rag", "trace", "evaluation")


def test_workflow_contract_steps_are_parallel_after_contract_phase():
    campaign = CampaignSpec.from_dict({"objective": "Run a marketing campaign", "metrics": ["qualified_leads"]})

    dossier = CampaignCompiler().compile(campaign)
    contract_steps = [step for step in dossier.workflow if step.id.startswith("contract_")]

    assert contract_steps
    assert all(step.depends_on == ("contract",) for step in contract_steps)
    synthesize = next(step for step in dossier.workflow if step.id == "synthesize")
    assert all(step.id in synthesize.depends_on for step in contract_steps)
