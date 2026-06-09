from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ArchitectureLayer:
    """Boundary marker for Campaigns as an operating-system layer above AgentRL."""

    level: int
    name: str
    question: str
    output: str
    owner: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Budget:
    """Resource limits for a campaign or outsourced contract."""

    dollars: float | None = None
    compute_hours: float | None = None
    human_hours: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Budget":
        data = data or {}
        return cls(dollars=data.get("dollars"), compute_hours=data.get("compute_hours"), human_hours=data.get("human_hours"))


@dataclass(frozen=True)
class Timeline:
    """Timebox for a campaign or contract."""

    days: int | None = None
    deadline: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Timeline":
        data = data or {}
        return cls(days=data.get("days"), deadline=data.get("deadline"))


@dataclass(frozen=True)
class AgentHarnessDefinition:
    """User-created targeted harness intent before a campaign employs the agent."""

    agent_name: str
    role: str
    objective: str
    components: tuple[str, ...] = ()
    agentrl_project_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentHarnessDefinition":
        return cls(
            agent_name=data["agent_name"],
            role=data["role"],
            objective=data["objective"],
            components=tuple(data.get("components", ())),
            agentrl_project_path=data.get("agentrl_project_path"),
        )

    def to_pod(self) -> "AgentRLPodInstantiation":
        slug = _slug(self.agent_name)
        return AgentRLPodInstantiation(
            name=f"{self.agent_name} Pod",
            domain=self.role,
            project_path=self.agentrl_project_path or f"agentrl://targeted-agents/{slug}",
            harness_entrypoint=f"{slug}-harness:run",
            eval_suite=f"{slug}-evals",
            harness_components=self.components,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CampaignSpec:
    """A user-defined outcome request plus the initial employed harnesses."""

    objective: str
    budget: Budget = field(default_factory=Budget)
    timeline: Timeline = field(default_factory=Timeline)
    metrics: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    domain: str | None = None
    employed_harnesses: tuple[AgentHarnessDefinition, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CampaignSpec":
        payload = data.get("campaign", data)
        harnesses = payload.get("employed_harnesses", payload.get("agents", ()))
        return cls(
            objective=payload["objective"],
            budget=Budget.from_dict(payload.get("budget")),
            timeline=Timeline.from_dict(payload.get("timeline")),
            metrics=tuple(payload.get("metrics", ())),
            constraints=tuple(payload.get("constraints", ())),
            domain=payload.get("domain"),
            employed_harnesses=tuple(AgentHarnessDefinition.from_dict(item) for item in harnesses),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorldModelScenario:
    """A simulated future considered before campaign execution."""

    name: str
    strategy: str
    expected_metrics: tuple[str, ...]
    expected_cost: str
    expected_risk: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentRLPodInstantiation:
    """Declaration that an employed or contract agent is backed by an AgentRL-managed pod."""

    name: str
    version: str = "0.1.0"
    domain: str = "general"
    project_path: str | None = None
    harness_entrypoint: str | None = None
    eval_suite: str | None = None
    deployment_channel: str = "local"
    harness_components: tuple[str, ...] = ()

    def lifecycle_owner(self) -> str:
        return "agentrl"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Contract:
    """Outsourced short-term work managed by an employed fleet agent."""

    objective: str
    budget: Budget = field(default_factory=Budget)
    deadline: str | None = None
    success_criteria: tuple[str, ...] = ()
    trace_required: bool = True
    parallelizable: bool = True
    contracted_pod: AgentRLPodInstantiation | None = None
    status: str = "proposed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EmployedAgent:
    """An accountable fleet agent employed by a campaign goal."""

    name: str
    role: str
    mandate: str
    pod: AgentRLPodInstantiation
    decision_rights: tuple[str, ...] = ()
    review_obligations: tuple[str, ...] = (
        "record material decisions",
        "surface uncertainty and tradeoffs",
        "provide traceable evidence for user review",
        "summarize contracted-agent work instead of forcing user micromanagement",
    )
    contracts: tuple[Contract, ...] = ()

    def outsource(self, contract: Contract) -> "EmployedAgent":
        return EmployedAgent(
            name=self.name,
            role=self.role,
            mandate=self.mandate,
            pod=self.pod,
            decision_rights=self.decision_rights,
            review_obligations=self.review_obligations,
            contracts=self.contracts + (contract,),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TeamBlueprint:
    name: str
    mission: str
    agents: tuple[EmployedAgent, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrganizationBlueprint:
    """Campaign-generated autonomous organization layout."""

    name: str
    teams: tuple[TeamBlueprint, ...]

    @classmethod
    def default_for(cls, campaign: CampaignSpec) -> "OrganizationBlueprint":
        domain = (campaign.domain or campaign.objective).lower()
        if any(token in domain for token in ("revenue", "marketing", "growth", "sales", "business")):
            teams = _growth_teams(campaign)
        elif any(token in domain for token in ("software", "code", "app", "product")):
            teams = _software_teams(campaign)
        else:
            teams = _general_campaign_teams(campaign)
        return cls(name="Campaign Organization", teams=teams)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkflowStep:
    id: str
    name: str
    actor: str
    kind: str
    depends_on: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    review_surface: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TraceMonitor:
    """What the user can monitor without micromanaging the fleet."""

    scope: str
    trace_paths: tuple[str, ...]
    review_cadence: str = "on-demand performance review"
    signals: tuple[str, ...] = ("decision quality", "constraint compliance", "contract outcomes", "evidence quality", "cost and timeline drift")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PerformanceReview:
    agent: str
    scorecard: tuple[str, ...]
    evidence: tuple[str, ...]
    recommended_action: str = "continue with monitoring"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionRecord:
    agent: str
    decision: str
    rationale: str
    evidence: tuple[str, ...] = ()
    risk: str | None = None
    requires_human_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewDossier:
    """The user-facing artifact for ultimate campaign review."""

    campaign: CampaignSpec
    architecture_layers: tuple[ArchitectureLayer, ...]
    organization: OrganizationBlueprint
    simulated_futures: tuple[WorldModelScenario, ...]
    selected_future: WorldModelScenario
    workflow: tuple[WorkflowStep, ...]
    decisions: tuple[DecisionRecord, ...]
    contracts: tuple[Contract, ...]
    trace_monitor: TraceMonitor
    performance_reviews: tuple[PerformanceReview, ...]
    approval_gates: tuple[str, ...]
    final_review_packet: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slug(value: str) -> str:
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def default_architecture_layers() -> tuple[ArchitectureLayer, ...]:
    return (
        ArchitectureLayer(1, "Runtime", "How does one agent solve a task?", "Trajectory", "OpenHarness / Claude Code / Codex / other runtimes"),
        ArchitectureLayer(2, "Harness Lifecycle", "How do we improve, evaluate, evolve, version, and deploy agents?", "Improved agent system", "AgentRL"),
        ArchitectureLayer(3, "Swarm Operating System", "How do we continuously execute business objectives through evolving agent organizations?", "Campaign outcome", "Campaigns"),
    )


def _pod(name: str, domain: str, eval_suite: str, components: tuple[str, ...] = ()) -> AgentRLPodInstantiation:
    slug = _slug(name)
    return AgentRLPodInstantiation(
        name=name,
        domain=domain,
        project_path=f"agentrl://pods/{slug}",
        harness_entrypoint=f"{slug}:run",
        eval_suite=eval_suite,
        harness_components=components,
    )


def _agent(name: str, role: str, mandate: str, domain: str, eval_suite: str, rights: tuple[str, ...], components: tuple[str, ...] = ()) -> EmployedAgent:
    return EmployedAgent(name=name, role=role, mandate=mandate, pod=_pod(f"{role} Pod", domain, eval_suite, components), decision_rights=rights)


def _harness_agents(campaign: CampaignSpec) -> tuple[EmployedAgent, ...]:
    return tuple(
        EmployedAgent(
            name=h.agent_name,
            role=h.role,
            mandate=h.objective,
            pod=h.to_pod(),
            decision_rights=("perform assigned campaign work", "request bounded contracts", "produce evidence-backed recommendations"),
        )
        for h in campaign.employed_harnesses
    )


def _contract_agent(name: str, role: str, objective: str, success: tuple[str, ...]) -> Contract:
    return Contract(
        objective=objective,
        success_criteria=success,
        contracted_pod=_pod(f"{name} Contract Pod", role, f"{_slug(name)}-contract-evals", ("trace", "decision_log", "evaluation")),
    )


def _growth_teams(campaign: CampaignSpec) -> tuple[TeamBlueprint, ...]:
    user_agents = _harness_agents(campaign)
    researcher = user_agents or (
        _agent("Market Researcher", "market_researcher", "Produce RAG-grounded market, competitor, and audience research.", "marketing", "market-research-evals", ("summarize evidence", "request contracts"), ("rag", "trace", "decision_log", "evaluation")),
    )
    manager = _agent("Campaign Manager", "manager", "Convert the user goal into strategy, operating cadence, contract boundaries, and approval gates.", "growth", "campaign-manager-evals", ("prioritize initiatives", "approve internal delegation", "request contracts"), ("trace", "decision_log", "evaluation", "approval_gate"))
    acquisition = _agent("Acquisition Agent", "acquisition", "Plan SEO, paid, partner, outreach, and content experiments.", "marketing", "acquisition-evals", ("propose campaigns", "draft acquisition assets", "request contract workers"), ("tool_use", "trace", "approval_gate"))
    acquisition = acquisition.outsource(_contract_agent("SEO Optimizer", "seo", "Optimize campaign pages and content briefs for qualified search demand.", ("keyword map delivered", "traceable recommendations", "no publishing without approval")))
    acquisition = acquisition.outsource(_contract_agent("Outreach Worker", "outreach", "Draft compliant outreach and follow-up sequences for approved audiences.", ("sequence draft delivered", "constraint compliance", "human approval before sending")))
    return (
        TeamBlueprint("Campaign Management Team", "Own the goal, campaign plan, fleet accountability, and final user review packet.", (manager,)),
        TeamBlueprint("Research Team", "Ground campaign choices in retrieved evidence and market analysis.", researcher),
        TeamBlueprint("Growth Execution Team", "Run acquisition experiments through employed agents and short-term contract workers.", (acquisition,)),
        TeamBlueprint("Measurement Team", "Monitor traces, metrics, and fleet performance reviews.", (_agent("Analytics Agent", "analytics", "Define metrics, instrumentation, forecasts, and performance readouts.", "analytics", "analytics-evals", ("select metrics", "flag invalid measurements", "run performance reviews"), ("trace", "evaluation", "decision_log")),)),
    )


def _software_teams(campaign: CampaignSpec) -> tuple[TeamBlueprint, ...]:
    return (TeamBlueprint("Product Engineering Team", "Turn outcome goals into software milestones, implementation, validation, and deployment evidence.", _harness_agents(campaign) or (_agent("Product Agent", "product", "Translate campaign objectives into product bets and acceptance criteria.", "product", "product-evals", ("prioritize features",), ("trace", "evaluation")), _agent("Engineering Agent", "engineering", "Build and verify scoped software increments.", "software", "engineering-evals", ("modify code", "run tests"), ("tool_use", "trace", "evaluation")), _agent("QA Agent", "qa", "Audit behavior, regressions, and release risk.", "quality", "qa-evals", ("block risky releases",), ("trace", "evaluation")))),)


def _general_campaign_teams(campaign: CampaignSpec) -> tuple[TeamBlueprint, ...]:
    return (TeamBlueprint("Strategy Team", "Decompose the campaign into measurable workstreams and managed risks.", _harness_agents(campaign) or (_agent("Campaign Manager", "manager", "Own campaign operating plan and review cadence.", "general", "manager-evals", ("prioritize initiatives", "request contracts"), ("trace", "decision_log")), _agent("Research Agent", "research", "Gather evidence, options, and risk signals for campaign decisions.", "research", "research-evals", ("summarize evidence", "recommend options"), ("rag", "trace")), _agent("Operations Agent", "operations", "Coordinate execution steps and status reporting.", "operations", "operations-evals", ("assign tasks", "track execution"), ("trace", "evaluation")))),)
