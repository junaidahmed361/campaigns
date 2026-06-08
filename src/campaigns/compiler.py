from __future__ import annotations

from .models import (
    CampaignSpec,
    Contract,
    DecisionRecord,
    OrganizationBlueprint,
    PerformanceReview,
    ReviewDossier,
    TraceMonitor,
    WorkflowStep,
)


class CampaignCompiler:
    """Compile a campaign spec into an accountable DAG, organization, and review dossier."""

    def compile(self, campaign: CampaignSpec, organization: OrganizationBlueprint | None = None) -> ReviewDossier:
        organization = organization or OrganizationBlueprint.default_for(campaign)
        contracts = self._contracts(organization)
        decisions = self._initial_decisions(campaign, organization, contracts)
        workflow = self._workflow(campaign, contracts)
        approval_gates = tuple(c for c in campaign.constraints if "approval" in c.lower())
        if not approval_gates:
            approval_gates = ("human approval before external spend, outreach, publishing, or irreversible actions",)
        trace_monitor = TraceMonitor(scope="fleet_and_contract_agents", trace_paths=(".campaigns/traces/fleet/*.jsonl", ".campaigns/traces/contracts/*.jsonl"))
        performance_reviews = self._performance_reviews(organization)
        final_review_packet = (
            "campaign outcome summary",
            "fleet-agent decision log",
            "contract-agent deliverables and traces",
            "metric movement and confidence",
            "risks, unresolved questions, and approval requests",
            "recommended next campaign iteration",
        )
        return ReviewDossier(campaign, organization, workflow, decisions, contracts, trace_monitor, performance_reviews, approval_gates, final_review_packet)

    def _contracts(self, organization: OrganizationBlueprint) -> tuple[Contract, ...]:
        return tuple(contract for team in organization.teams for agent in team.agents for contract in agent.contracts)

    def _workflow(self, campaign: CampaignSpec, contracts: tuple[Contract, ...]) -> tuple[WorkflowStep, ...]:
        contract_step_ids = tuple(f"contract_{idx + 1}" for idx, _ in enumerate(contracts))
        return (
            WorkflowStep("create_harness", "Create targeted AgentRL harnesses", "user + AgentRL", "setup", outputs=("targeted agent harness", "attached RAG/tool/trace/eval components"), review_surface="harness readiness report"),
            WorkflowStep("define_campaign", "Define campaign goal, constraints, budget, timeline, and metrics", "user", "setup", depends_on=("create_harness",), outputs=("campaign spec",)),
            WorkflowStep("employ_fleet", "Employ selected harness-backed agents into the campaign fleet", "Campaigns", "organization", depends_on=("define_campaign",), outputs=("organization blueprint", "fleet accountability map")),
            WorkflowStep("plan", "Generate campaign operating plan and approval gates", "Campaign Manager", "planning", depends_on=("employ_fleet",), outputs=("campaign plan", "approval gates"), review_surface="plan review"),
            WorkflowStep("research", "Run market researcher and RAG harnesses for evidence gathering", "Market Researcher", "fleet_work", depends_on=("plan",), outputs=("market evidence", "competitor map", "audience assumptions"), review_surface="research trace"),
            WorkflowStep("contract", "Create bounded parallel contracts for specialist short-term work", "Fleet agents", "delegation", depends_on=("research",), outputs=("contract specs", "worker traces"), review_surface="contract queue"),
            *(
                WorkflowStep(step_id, contract.objective, "Contract Agent", "contract_work", depends_on=("contract",), outputs=("deliverable", "trace", "cost/time record"), review_surface="contract trace")
                for step_id, contract in zip(contract_step_ids, contracts)
            ),
            WorkflowStep("synthesize", "Synthesize fleet and contract work into one report", "Campaign Manager", "synthesis", depends_on=("research", *contract_step_ids), outputs=("final report", "decision log", "metric readout"), review_surface="final report draft"),
            WorkflowStep("performance_review", "Monitor traces and produce fleet-agent performance reviews", "Analytics Agent", "monitoring", depends_on=("synthesize",), outputs=("performance scorecards", "trace anomalies", "improvement recommendations"), review_surface="performance review dashboard"),
            WorkflowStep("ultimate_review", "Present final review packet instead of micromanagement steps", "user", "human_review", depends_on=("performance_review",), outputs=("approve", "revise", "stop", "launch next iteration"), review_surface="ultimate user review"),
            WorkflowStep("evolve", "Feed review and trace outcomes back into AgentRL lifecycle", "AgentRL", "lifecycle", depends_on=("ultimate_review",), outputs=("candidate harness improvements", "versions", "deployment/rollback records"), review_surface="AgentRL promotion gate"),
        )

    def _initial_decisions(self, campaign: CampaignSpec, organization: OrganizationBlueprint, contracts: tuple[Contract, ...]) -> tuple[DecisionRecord, ...]:
        team_names = ", ".join(team.name for team in organization.teams)
        metric_names = ", ".join(campaign.metrics) or "user-defined outcome metrics"
        return (
            DecisionRecord("Campaign Manager", f"Instantiate organization with teams: {team_names}", "A campaign needs accountable fleet agents before tasks are delegated or outsourced.", (f"objective: {campaign.objective}", f"metrics: {metric_names}"), "Generated structure may need human adjustment before execution.", True),
            DecisionRecord("Campaign Manager", "Bind every employed and contract agent to an AgentRL pod declaration.", "AgentRL owns harness lifecycle, evals, self-evolution, versions, and deployment records.", ("campaigns layer remains separate from runtime and harness lifecycle layers",), "Missing pod implementation blocks real execution but not planning/review.", False),
            DecisionRecord("Fleet Agents", f"Prepare {len(contracts)} bounded contract work items for parallel execution.", "Specialist contract agents can handle short-term work while employed agents remain accountable for synthesis and review.", tuple(contract.objective for contract in contracts), "Contract work must obey trace and approval constraints.", any("approval" in constraint.lower() for constraint in campaign.constraints)),
        )

    def _performance_reviews(self, organization: OrganizationBlueprint) -> tuple[PerformanceReview, ...]:
        return tuple(
            PerformanceReview(agent=agent.name, scorecard=("goal contribution", "decision quality", "trace completeness", "constraint compliance", "contract management"), evidence=(f"pod: {agent.pod.name}", f"eval_suite: {agent.pod.eval_suite}", "trace monitor signals"))
            for team in organization.teams
            for agent in team.agents
        )
