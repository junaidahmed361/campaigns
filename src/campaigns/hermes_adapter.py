from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dogfood import AgentOSDogfoodRunner, OutcomeRequest
from .resource_manager import ExecutionPolicy


@dataclass(frozen=True)
class HermesAdapter:
    """Thin Hermes-facing adapter over Campaign Kernel state.

    Hermes is the primary Phase 0 dogfooding interface, but it is only a client.
    This adapter returns kernel-owned state and intentionally contains no
    planning, routing, resource, evaluation, or receipt business logic.
    """

    def create_campaign(self, goal: str, execution_policy: dict[str, Any] | None = None) -> dict[str, Any]:
        policy = ExecutionPolicy.from_dict(execution_policy)
        request = OutcomeRequest(
            goal=goal,
            budget_dollars=policy.per_campaign_limit_usd,
            constraints=("execution policy enforced by Campaign Kernel",),
            quality_requirements=("Hermes receives kernel state only",),
        )
        result = AgentOSDogfoodRunner().run(request).to_dict()
        result["execution_policy"] = policy.to_dict()
        result["client_boundary"] = "Hermes is a thin client/tool consumer; Campaign Kernel is system of record."
        return result

    def list_campaigns(self) -> dict[str, Any]:
        return {"campaigns": [], "source_of_record": "campaign_kernel"}

    def campaign_status(self, campaign_id: str) -> dict[str, Any]:
        return {"id": campaign_id, "status": "unknown_in_phase0_scaffold", "source_of_record": "campaign_kernel"}

    def approve(self, approval_id: str) -> dict[str, Any]:
        return {"id": approval_id, "decision": "approved", "source_of_record": "campaign_kernel"}

    def reject(self, approval_id: str) -> dict[str, Any]:
        return {"id": approval_id, "decision": "rejected", "source_of_record": "campaign_kernel"}

    def list_artifacts(self, campaign_id: str) -> dict[str, Any]:
        return {"campaign_id": campaign_id, "artifacts": [], "source_of_record": "campaign_kernel"}

    def open_artifact(self, artifact_id: str) -> dict[str, Any]:
        return {"id": artifact_id, "artifact": None, "source_of_record": "campaign_kernel"}

    def receipt(self, campaign_id: str) -> dict[str, Any]:
        return {"campaign_id": campaign_id, "receipt": None, "source_of_record": "campaign_kernel"}

    def execution_policy_get(self) -> dict[str, Any]:
        return ExecutionPolicy.default_local_byok().to_dict()

    def execution_policy_update(self, execution_policy: dict[str, Any]) -> dict[str, Any]:
        return ExecutionPolicy.from_dict(execution_policy).to_dict()


TOOL_NAMES = (
    "create_campaign",
    "list_campaigns",
    "campaign_status",
    "approve",
    "reject",
    "list_artifacts",
    "open_artifact",
    "receipt",
    "execution_policy_get",
    "execution_policy_update",
)
