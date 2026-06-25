from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .architecture import ImmutableReceipt, RoutingObjective, phase0_capability_contracts
from .compiler import CampaignCompiler
from .models import CampaignSpec


@dataclass(frozen=True)
class OutcomeRequest:
    """User-facing AgentOS intake: outcomes and constraints, never providers."""

    goal: str
    budget_dollars: float | None = None
    constraints: tuple[str, ...] = ()
    quality_requirements: tuple[str, ...] = ()
    sla: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OutcomeRequest":
        payload = data.get("agentos", data)
        budget = payload.get("budget", {})
        execution_policy = payload.get("execution_policy", {})
        if isinstance(budget, dict):
            dollars = budget.get("dollars")
        else:
            dollars = budget
        if dollars is None and isinstance(execution_policy, dict):
            dollars = execution_policy.get("per_campaign_limit_usd", execution_policy.get("max_campaign_spend_usd"))
        return cls(
            goal=payload["goal"],
            budget_dollars=dollars,
            constraints=tuple(payload.get("constraints", ())),
            quality_requirements=tuple(payload.get("quality_requirements", payload.get("quality", ()))),
            sla=payload.get("sla"),
        )

    def to_campaign(self) -> CampaignSpec:
        metrics = self.quality_requirements or ("accepted_artifacts",)
        return CampaignSpec.from_dict(
            {
                "objective": self.goal,
                "budget": {"dollars": self.budget_dollars} if self.budget_dollars is not None else {},
                "metrics": list(metrics),
                "constraints": list(self.constraints),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentOSArtifact:
    name: str
    kind: str
    produced_by: str
    measurable_by: tuple[str, ...]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentOSDogfoodResult:
    """Replayable dry-run proving the user does not need provider complexity."""

    request: OutcomeRequest
    status: str
    routing_objective: RoutingObjective
    selected_capabilities: tuple[str, ...]
    artifacts: tuple[AgentOSArtifact, ...]
    receipt: ImmutableReceipt
    user_review_packet: tuple[str, ...]
    provider_complexity_exposed: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["routing_objective"] = self.routing_objective.to_dict()
        payload["receipt"] = self.receipt.to_dict()
        return payload


class AgentOSDogfoodRunner:
    """Deterministic Phase 0 dogfood path for AgentOS product philosophy.

    This does not call commercial providers. It proves the kernel-facing product
    contract: a user submits goal/budget/constraints/quality, then AgentOS returns
    capability-routed artifacts, evaluations, and an immutable receipt without
    asking the user to pick providers.
    """

    def __init__(self, compiler: CampaignCompiler | None = None):
        self.compiler = compiler or CampaignCompiler()

    def run(self, request: OutcomeRequest | dict[str, Any]) -> AgentOSDogfoodResult:
        outcome = request if isinstance(request, OutcomeRequest) else OutcomeRequest.from_dict(request)
        campaign = outcome.to_campaign()
        dossier = self.compiler.compile(campaign)
        contracts = phase0_capability_contracts()
        selected = ("planning.dag", "evaluation.quality_gate")
        if any(token in outcome.goal.lower() for token in ("api", "backend", "code", "repo", "build")):
            selected = selected + ("backend.api",)

        artifacts = (
            AgentOSArtifact(
                name="Outcome-normalized campaign dossier",
                kind="review_dossier",
                produced_by="planning.dag",
                measurable_by=("goal_present", "budget_respected", "constraints_preserved", "quality_requirements_mapped"),
                summary=f"Compiled goal into {len(dossier.workflow)} workflow steps and {len(dossier.final_review_packet)} review-packet items.",
            ),
            AgentOSArtifact(
                name="Capability routing rationale",
                kind="routing_rationale",
                produced_by="planning.dag",
                measurable_by=("capability_contracts_selected", "no_provider_required", "euv_per_dollar_computed"),
                summary="Selected provider-independent capability contracts before any driver/provider decision.",
            ),
            AgentOSArtifact(
                name="Evaluation gate plan",
                kind="evaluation_plan",
                produced_by="evaluation.quality_gate",
                measurable_by=("all_artifacts_have_measures", "repair_loop_bounded", "receipt_append_only"),
                summary="Every artifact has measurable acceptance checks before execution is considered accepted.",
            ),
        )
        artifact_ids = tuple(artifact.name for artifact in artifacts)
        receipt = ImmutableReceipt(
            receipt_id="agentos-dogfood-0001",
            sequence=1,
            subject=outcome.goal,
            artifact_ids=artifact_ids,
            evaluator_results=("provider_complexity_exposed:false", "artifact_measures:present", "receipt:immutable"),
        )
        expected_value = 100.0 + (10.0 * len(outcome.quality_requirements))
        expected_cost = outcome.budget_dollars if outcome.budget_dollars and outcome.budget_dollars > 0 else 1.0
        routing = RoutingObjective(
            expected_user_value=expected_value,
            expected_cost=expected_cost,
            rationale="Optimize accepted user value per dollar using capability contracts; provider choice is hidden behind drivers.",
        )
        contract_names = {contract.name for contract in contracts}
        return AgentOSDogfoodResult(
            request=outcome,
            status="awaiting_user_review",
            routing_objective=routing,
            selected_capabilities=tuple(name for name in selected if name in contract_names),
            artifacts=artifacts,
            receipt=receipt,
            user_review_packet=dossier.final_review_packet,
            notes=(
                "User supplied outcome, budget, constraints, and quality requirements only.",
                "AgentOS selected capabilities, artifacts, evaluation gates, and receipt without provider selection.",
                "Real execution drivers remain deferred behind capability implementations.",
            ),
        )
