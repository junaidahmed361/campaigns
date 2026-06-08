from campaigns import CampaignCompiler, CampaignSpec, OrganizationBlueprint


def test_growth_campaign_compiles_to_accountable_org():
    campaign = CampaignSpec.from_dict(
        {
            "campaign": {
                "objective": "Increase recurring revenue by 30%",
                "budget": {"dollars": 5000},
                "timeline": {"days": 90},
                "metrics": ["revenue", "conversions"],
                "constraints": ["human approval for spend > $500"],
            }
        }
    )

    dossier = CampaignCompiler().compile(campaign)

    assert dossier.campaign.objective == "Increase recurring revenue by 30%"
    assert dossier.approval_gates == ("human approval for spend > $500",)
    assert dossier.organization.teams[0].agents[0].pod.lifecycle_owner() == "agentrl"


def test_default_growth_blueprint_contains_outsourcing_capable_agents():
    campaign = CampaignSpec.from_dict({"objective": "Grow my business revenue", "metrics": ["revenue"]})

    org = OrganizationBlueprint.default_for(campaign)

    agents = [agent for team in org.teams for agent in team.agents]
    assert {agent.role for agent in agents} >= {"manager", "acquisition", "analytics"}
    assert all(agent.review_obligations for agent in agents)
    assert all(agent.pod.project_path.startswith("agentrl://pods/") for agent in agents)
