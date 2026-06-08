from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .compiler import CampaignCompiler
from .models import CampaignSpec, ReviewDossier, WorkflowStep


@dataclass(frozen=True)
class AutorunPolicy:
    """Loop policy for Claude-style campaign autorun.

    Campaigns owns the operating cadence and review surface only. The actual
    agent execution remains in runtime systems, while harness lifecycle changes
    remain in AgentRL.
    """

    max_loops: int = 3
    stop_when: tuple[str, ...] = ("objective_satisfied", "approval_required", "budget_exhausted", "human_stop")
    require_ultimate_review: bool = True
    dynamic_step_kinds: tuple[str, ...] = ("observe", "plan", "act", "verify", "review")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CampaignIteration:
    """One observe-plan-act-verify-review autorun loop."""

    index: int
    phase: str
    selected_steps: tuple[str, ...]
    stop_reason: str | None
    review_packet: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutorunResult:
    """Result of running a loop-based campaign operating plan."""

    campaign: CampaignSpec
    dossier: ReviewDossier
    policy: AutorunPolicy
    iterations: tuple[CampaignIteration, ...]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CampaignAutorun:
    """Scikit-learn-style primitive for loop-based campaign autorun.

    `fit` compiles the campaign into a dynamic workflow and stores the learned
    operating plan. `transform` returns the review dossier. `score` reports a
    simple readiness score. `autorun` advances bounded observe/plan/act/verify/
    review loops without implementing the underlying agent runtime.
    """

    def __init__(self, policy: AutorunPolicy | None = None, compiler: CampaignCompiler | None = None):
        self.policy = policy or AutorunPolicy()
        self.compiler = compiler or CampaignCompiler()
        self.campaign_: CampaignSpec | None = None
        self.dossier_: ReviewDossier | None = None
        self.iterations_: tuple[CampaignIteration, ...] = ()

    def fit(self, campaign: CampaignSpec | dict[str, Any]) -> "CampaignAutorun":
        self.campaign_ = campaign if isinstance(campaign, CampaignSpec) else CampaignSpec.from_dict(campaign)
        self.dossier_ = self.compiler.compile(self.campaign_)
        self.iterations_ = ()
        return self

    def transform(self, campaign: CampaignSpec | dict[str, Any] | None = None) -> ReviewDossier:
        if campaign is not None:
            self.fit(campaign)
        if self.dossier_ is None:
            raise ValueError("CampaignAutorun must be fit before transform")
        return self.dossier_

    def fit_transform(self, campaign: CampaignSpec | dict[str, Any]) -> ReviewDossier:
        return self.fit(campaign).transform()

    def score(self, campaign: CampaignSpec | dict[str, Any] | None = None) -> float:
        dossier = self.transform(campaign)
        checks = (
            bool(dossier.workflow),
            bool(dossier.organization.teams),
            bool(dossier.trace_monitor.trace_paths),
            bool(dossier.final_review_packet),
            any(step.kind == "human_review" for step in dossier.workflow),
        )
        return sum(1 for check in checks if check) / len(checks)

    def autorun(self, campaign: CampaignSpec | dict[str, Any] | None = None, max_loops: int | None = None) -> AutorunResult:
        dossier = self.transform(campaign)
        loop_count = max_loops if max_loops is not None else self.policy.max_loops
        iterations: list[CampaignIteration] = []
        for index in range(1, loop_count + 1):
            selected = self._select_dynamic_steps(dossier.workflow, index)
            stop_reason = self._stop_reason(index, loop_count)
            iterations.append(
                CampaignIteration(
                    index=index,
                    phase="observe_plan_act_verify_review",
                    selected_steps=selected,
                    stop_reason=stop_reason,
                    review_packet=dossier.final_review_packet,
                )
            )
            if stop_reason:
                break
        self.iterations_ = tuple(iterations)
        status = "awaiting_ultimate_review" if self.policy.require_ultimate_review else "completed"
        return AutorunResult(self.campaign_, dossier, self.policy, self.iterations_, status)  # type: ignore[arg-type]

    def _select_dynamic_steps(self, workflow: tuple[WorkflowStep, ...], iteration: int) -> tuple[str, ...]:
        if iteration == 1:
            preferred = {"create_harness", "define_campaign", "employ_fleet", "plan", "research", "contract"}
        else:
            preferred = {"research", "contract", "synthesize", "performance_review", "ultimate_review", "evolve"}
        return tuple(step.id for step in workflow if step.id in preferred or step.id.startswith("contract_"))

    def _stop_reason(self, index: int, loop_count: int) -> str | None:
        if self.policy.require_ultimate_review and index == loop_count:
            return "approval_required"
        return None
