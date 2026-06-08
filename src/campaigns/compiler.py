from __future__ import annotations

from .models import CampaignSpec, DecisionRecord, OrganizationBlueprint, ReviewDossier


class CampaignCompiler:
    """Compile a campaign spec into an accountable organization and review dossier."""

    def compile(
        self,
        campaign: CampaignSpec,
        organization: OrganizationBlueprint | None = None,
    ) -> ReviewDossier:
        organization = organization or OrganizationBlueprint.default_for(campaign)
        decisions = self._initial_decisions(campaign, organization)
        approval_gates = tuple(c for c in campaign.constraints if "approval" in c.lower())
        if not approval_gates:
            approval_gates = ("human approval before external spend or irreversible actions",)
        return ReviewDossier(
            campaign=campaign,
            organization=organization,
            decisions=decisions,
            approval_gates=approval_gates,
        )

    def _initial_decisions(
        self,
        campaign: CampaignSpec,
        organization: OrganizationBlueprint,
    ) -> tuple[DecisionRecord, ...]:
        team_names = ", ".join(team.name for team in organization.teams)
        metric_names = ", ".join(campaign.metrics) or "user-defined outcome metrics"
        return (
            DecisionRecord(
                agent="Campaign Manager",
                decision=f"Instantiate organization with teams: {team_names}",
                rationale="A campaign needs accountable teams before tasks are delegated or outsourced.",
                evidence=(f"objective: {campaign.objective}", f"metrics: {metric_names}"),
                risk="Generated structure may need human adjustment before execution.",
                requires_human_approval=True,
            ),
            DecisionRecord(
                agent="Campaign Manager",
                decision="Bind every employed agent to an AgentRL pod declaration.",
                rationale="AgentRL owns harness lifecycle, evals, self-evolution, versions, and deployment records.",
                evidence=("campaigns layer remains separate from runtime and harness lifecycle layers",),
                risk="Missing pod implementation blocks real execution but not planning/review.",
                requires_human_approval=False,
            ),
        )
