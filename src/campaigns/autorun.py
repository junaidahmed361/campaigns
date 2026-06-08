from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .compiler import CampaignCompiler
from .models import CampaignSpec, ReviewDossier, WorkflowStep


@dataclass(frozen=True)
class RetrospectiveFeedback:
    """Human or metric feedback for continual campaign learning.

    attention_level routes the learning: `campaign` updates campaign strategy and
    future iterations, while `agentrl` produces lifecycle reinforcement directives
    for the owning AgentRL harness/pod.
    """

    summary: str
    attention_level: str = "campaign"
    target: str = "campaign"
    outcome: str = "needs_review"
    reinforce: str = ""
    evidence: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetrospectiveFeedback":
        return cls(
            summary=data["summary"],
            attention_level=data.get("attention_level", "campaign"),
            target=data.get("target", "campaign"),
            outcome=data.get("outcome", "needs_review"),
            reinforce=data.get("reinforce", ""),
            evidence=tuple(data.get("evidence", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReinforcementAction:
    owner: str
    target: str
    instruction: str
    reinforcement_targets: tuple[str, ...]
    agentrl_project_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetrospectiveResult:
    feedback: RetrospectiveFeedback
    actions: tuple[ReinforcementAction, ...]
    status: str
    context: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
        self.retrospectives_: tuple[RetrospectiveResult, ...] = ()

    def fit(self, campaign: CampaignSpec | dict[str, Any]) -> "CampaignAutorun":
        self.campaign_ = campaign if isinstance(campaign, CampaignSpec) else CampaignSpec.from_dict(campaign)
        self.dossier_ = self.compiler.compile(self.campaign_)
        self.iterations_ = ()
        self.retrospectives_ = ()
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

    def retro(self, feedback: RetrospectiveFeedback | dict[str, Any]) -> RetrospectiveResult:
        """Plan continual-learning reinforcement from a campaign retrospective.

        Campaign-level feedback stays in Campaigns as next-iteration operating
        guidance. Agent-level feedback is converted into an AgentRL directive with
        the owning pod/project path so AgentRL can reinforce the harness.
        """

        dossier = self.transform()
        item = feedback if isinstance(feedback, RetrospectiveFeedback) else RetrospectiveFeedback.from_dict(feedback)
        action = self._retro_action(item, dossier)
        result = RetrospectiveResult(
            feedback=item,
            actions=(action,),
            status="reinforcement_planned",
            context={
                "campaign_objective": dossier.campaign.objective,
                "available_agents": tuple(agent.name for team in dossier.organization.teams for agent in team.agents),
                "attention_level": item.attention_level,
            },
        )
        self.retrospectives_ = self.retrospectives_ + (result,)
        return result

    def _retro_action(self, feedback: RetrospectiveFeedback, dossier: ReviewDossier) -> ReinforcementAction:
        instruction = feedback.reinforce or feedback.summary
        if feedback.attention_level.lower() in {"agentrl", "agent", "harness", "pod"}:
            agent = self._find_agent(feedback.target, dossier)
            project_path = agent.pod.project_path if agent else None
            return ReinforcementAction(
                owner="agentrl",
                target=feedback.target,
                instruction=instruction,
                reinforcement_targets=("evaluation", "memory", "prompts"),
                agentrl_project_path=project_path,
            )
        return ReinforcementAction(
            owner="campaigns",
            target="campaign_strategy",
            instruction=f"Apply retrospective to the next campaign iteration: {instruction}",
            reinforcement_targets=("playbook", "metrics", "guardrails", "workflow"),
        )

    def _find_agent(self, target: str, dossier: ReviewDossier):
        lowered = target.lower()
        for team in dossier.organization.teams:
            for agent in team.agents:
                if agent.name.lower() == lowered or agent.role.lower() == lowered:
                    return agent
        return None

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
