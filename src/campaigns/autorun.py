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
    step_budget: int | None = None
    stop_when: tuple[str, ...] = ("objective_satisfied", "approval_required", "budget_exhausted", "human_stop")
    require_ultimate_review: bool = True
    dynamic_step_kinds: tuple[str, ...] = ("observe", "plan", "act", "verify", "review")
    second_model_evaluator: str = "goal_satisfaction_check"
    independent_final_auditor: str = "ultimate_review_auditor"
    save_resume_state: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GoalCheck:
    question: str
    met: bool
    evaluator: str
    rationale: str

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
    goal_check: GoalCheck
    audit: str | None = None

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
    resume_state: dict[str, Any] | None = None

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
        requested_loops = max_loops if max_loops is not None else self.policy.max_loops
        loop_count = min(requested_loops, self.policy.step_budget) if self.policy.step_budget else requested_loops
        iterations: list[CampaignIteration] = []
        stop_reason: str | None = None
        for index in range(1, loop_count + 1):
            selected = self._select_dynamic_steps(dossier.workflow, index)
            goal_check = self._goal_check(dossier, index)
            stop_reason = self._stop_reason(index, requested_loops, goal_check)
            iterations.append(
                CampaignIteration(
                    index=index,
                    phase="observe_plan_act_verify_review",
                    selected_steps=selected,
                    stop_reason=stop_reason,
                    review_packet=dossier.final_review_packet,
                    goal_check=goal_check,
                    audit=self.policy.independent_final_auditor if stop_reason in {"objective_satisfied", "approval_required"} else None,
                )
            )
            if stop_reason:
                break
        if not stop_reason and loop_count < requested_loops:
            stop_reason = "budget_exhausted"
            if iterations:
                last = iterations[-1]
                iterations[-1] = CampaignIteration(
                    index=last.index,
                    phase=last.phase,
                    selected_steps=last.selected_steps,
                    stop_reason=stop_reason,
                    review_packet=last.review_packet,
                    goal_check=last.goal_check,
                    audit=last.audit,
                )
        self.iterations_ = tuple(iterations)
        resume_state = self._resume_state(dossier, requested_loops, loop_count, stop_reason) if stop_reason == "budget_exhausted" else None
        if stop_reason == "budget_exhausted":
            status = "paused_budget_exhausted"
        else:
            status = "awaiting_ultimate_review" if self.policy.require_ultimate_review else "completed"
        return AutorunResult(self.campaign_, dossier, self.policy, self.iterations_, status, resume_state)  # type: ignore[arg-type]

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

    def final_review(self, accepted: bool, feedback: str) -> RetrospectiveResult:
        """Accept user final review, then let a retro agent traverse traces.

        The user supplies the final judgment. After that, the campaign retro agent
        owns trace traversal across all employed agents, attributes a root cause,
        and emits AgentRL reinforcement for the responsible harness.
        """

        dossier = self.transform()
        root_cause = self._trace_root_cause(feedback, dossier)
        result = RetrospectiveResult(
            feedback=RetrospectiveFeedback(
                summary=feedback,
                attention_level="agentrl",
                target=root_cause["target"],
                outcome="accepted" if accepted else "needs_improvement",
                reinforce=f"Root cause: {root_cause['summary']}. Reinforce from final review: {feedback}",
                evidence=tuple(root_cause["trace_paths"]),
            ),
            actions=(
                ReinforcementAction(
                    owner="agentrl",
                    target=root_cause["target"],
                    instruction=f"Root cause: {root_cause['summary']}. Reinforce from final review: {feedback}",
                    reinforcement_targets=("evaluation", "memory", "prompts"),
                    agentrl_project_path=root_cause.get("agentrl_project_path"),
                ),
            ),
            status="self_reinforcement_planned",
            context={"root_cause": root_cause, "accepted": accepted},
        )
        self.retrospectives_ = self.retrospectives_ + (result,)
        return result

    def _trace_root_cause(self, feedback: str, dossier: ReviewDossier) -> dict[str, Any]:
        text = feedback.lower()
        agents = [agent for team in dossier.organization.teams for agent in team.agents]
        target_agent = None
        for agent in agents:
            if agent.name.lower() in text or agent.role.lower() in text:
                target_agent = agent
                break
        if target_agent is None:
            target_agent = agents[0] if agents else None
        summary = "trace evidence gap"
        if "competitor" in text and "pricing" in text:
            summary = "competitor pricing evidence gap"
        elif "evidence" in text or "citation" in text:
            summary = "evidence citation gap"
        elif "metric" in text or "analytics" in text:
            summary = "measurement quality gap"
        return {
            "target": target_agent.name if target_agent else "campaign",
            "summary": summary,
            "trace_paths": dossier.trace_monitor.trace_paths,
            "agentrl_project_path": target_agent.pod.project_path if target_agent else None,
            "traversed_agents": tuple(agent.name for agent in agents),
        }

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

    def _goal_check(self, dossier: ReviewDossier, index: int) -> GoalCheck:
        done = bool(dossier.final_review_packet) and not self.policy.require_ultimate_review and index >= self.policy.max_loops
        rationale = "Goal still needs independent final review or more evidence."
        if done:
            rationale = "Done criteria and final review requirements are satisfied."
        return GoalCheck(
            question="Has the campaign goal been met?",
            met=done,
            evaluator=self.policy.second_model_evaluator,
            rationale=rationale,
        )

    def _resume_state(self, dossier: ReviewDossier, requested_loops: int, completed_loops: int, stop_reason: str | None) -> dict[str, Any]:
        return {
            "saved": self.policy.save_resume_state,
            "stop_reason": stop_reason,
            "completed_loops": completed_loops,
            "requested_loops": requested_loops,
            "next_step": "resume_goal_loop",
            "what_is_left": (
                "Continue autonomous observe-plan-act-verify-review loops, run the goal satisfaction check again, "
                "and submit the final packet to the independent final auditor."
            ),
            "campaign_objective": dossier.campaign.objective,
        }

    def _select_dynamic_steps(self, workflow: tuple[WorkflowStep, ...], iteration: int) -> tuple[str, ...]:
        if iteration == 1:
            preferred = {"create_harness", "define_campaign", "employ_fleet", "plan", "research", "contract"}
        else:
            preferred = {"research", "contract", "synthesize", "performance_review", "ultimate_review", "evolve"}
        return tuple(step.id for step in workflow if step.id in preferred or step.id.startswith("contract_"))

    def _stop_reason(self, index: int, loop_count: int, goal_check: GoalCheck | None = None) -> str | None:
        if goal_check and goal_check.met:
            return "objective_satisfied"
        if self.policy.require_ultimate_review and index == loop_count:
            return "approval_required"
        return None
