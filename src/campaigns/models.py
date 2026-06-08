from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Budget:
    """Resource limits for a campaign or outsourced contract."""

    dollars: float | None = None
    compute_hours: float | None = None
    human_hours: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Budget":
        data = data or {}
        return cls(
            dollars=data.get("dollars"),
            compute_hours=data.get("compute_hours"),
            human_hours=data.get("human_hours"),
        )


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
class CampaignSpec:
    """A user-defined outcome request."""

    objective: str
    budget: Budget = field(default_factory=Budget)
    timeline: Timeline = field(default_factory=Timeline)
    metrics: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    domain: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CampaignSpec":
        payload = data.get("campaign", data)
        return cls(
            objective=payload["objective"],
            budget=Budget.from_dict(payload.get("budget")),
            timeline=Timeline.from_dict(payload.get("timeline")),
            metrics=tuple(payload.get("metrics", ())),
            constraints=tuple(payload.get("constraints", ())),
            domain=payload.get("domain"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentRLPodInstantiation:
    """Declaration that an employed agent is backed by an AgentRL-managed pod."""

    name: str
    version: str = "0.1.0"
    domain: str = "general"
    project_path: str | None = None
    harness_entrypoint: str | None = None
    eval_suite: str | None = None
    deployment_channel: str = "local"

    def lifecycle_owner(self) -> str:
        return "agentrl"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Contract:
    """Outsourced work managed by an employed agent."""

    objective: str
    budget: Budget = field(default_factory=Budget)
    deadline: str | None = None
    success_criteria: tuple[str, ...] = ()
    trace_required: bool = True
    contracted_pod: AgentRLPodInstantiation | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EmployedAgent:
    """An accountable agent employed by a campaign goal."""

    name: str
    role: str
    mandate: str
    pod: AgentRLPodInstantiation
    decision_rights: tuple[str, ...] = ()
    review_obligations: tuple[str, ...] = (
        "record material decisions",
        "surface uncertainty and tradeoffs",
        "provide traceable evidence for user review",
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
            teams = _growth_teams()
        elif any(token in domain for token in ("software", "code", "app", "product")):
            teams = _software_teams()
        else:
            teams = _general_campaign_teams()
        return cls(name="Campaign Organization", teams=teams)

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
    organization: OrganizationBlueprint
    decisions: tuple[DecisionRecord, ...]
    approval_gates: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _pod(name: str, domain: str, eval_suite: str) -> AgentRLPodInstantiation:
    slug = name.lower().replace(" ", "-")
    return AgentRLPodInstantiation(
        name=name,
        domain=domain,
        project_path=f"agentrl://pods/{slug}",
        harness_entrypoint=f"{slug}:run",
        eval_suite=eval_suite,
    )


def _agent(name: str, role: str, mandate: str, domain: str, eval_suite: str, rights: tuple[str, ...]) -> EmployedAgent:
    return EmployedAgent(
        name=name,
        role=role,
        mandate=mandate,
        pod=_pod(name=f"{role} Pod", domain=domain, eval_suite=eval_suite),
        decision_rights=rights,
    )


def _growth_teams() -> tuple[TeamBlueprint, ...]:
    return (
        TeamBlueprint(
            name="Growth Team",
            mission="Find and operate the highest-leverage paths to measurable revenue growth.",
            agents=(
                _agent("Campaign Manager", "manager", "Convert the user goal into strategy, operating cadence, and approval gates.", "growth", "campaign-manager-evals", ("prioritize initiatives", "request contracts")),
                _agent("Acquisition Agent", "acquisition", "Plan SEO, paid, partner, and content acquisition experiments.", "marketing", "acquisition-evals", ("propose campaigns", "draft acquisition assets")),
                _agent("Analytics Agent", "analytics", "Define metrics, instrumentation, forecasts, and experiment readouts.", "analytics", "analytics-evals", ("select metrics", "flag invalid measurements")),
            ),
        ),
        TeamBlueprint(
            name="Conversion Team",
            mission="Improve landing pages, offers, onboarding, and retention loops.",
            agents=(
                _agent("Conversion Agent", "conversion", "Generate and evaluate funnel improvements.", "growth", "conversion-evals", ("draft landing page changes", "propose funnel experiments")),
                _agent("Retention Agent", "retention", "Design follow-up, upsell, and retention plays within constraints.", "customer-success", "retention-evals", ("propose retention sequences",)),
            ),
        ),
    )


def _software_teams() -> tuple[TeamBlueprint, ...]:
    return (
        TeamBlueprint(
            name="Product Engineering Team",
            mission="Turn outcome goals into software milestones, implementation, validation, and deployment evidence.",
            agents=(
                _agent("Product Agent", "product", "Translate campaign objectives into product bets and acceptance criteria.", "product", "product-evals", ("prioritize features",)),
                _agent("Engineering Agent", "engineering", "Build and verify scoped software increments.", "software", "engineering-evals", ("modify code", "run tests")),
                _agent("QA Agent", "qa", "Audit behavior, regressions, and release risk.", "quality", "qa-evals", ("block risky releases",)),
            ),
        ),
    )


def _general_campaign_teams() -> tuple[TeamBlueprint, ...]:
    return (
        TeamBlueprint(
            name="Strategy Team",
            mission="Decompose the campaign into measurable workstreams and managed risks.",
            agents=(
                _agent("Campaign Manager", "manager", "Own campaign operating plan and review cadence.", "general", "manager-evals", ("prioritize initiatives", "request contracts")),
                _agent("Research Agent", "research", "Gather evidence, options, and risk signals for campaign decisions.", "research", "research-evals", ("summarize evidence", "recommend options")),
                _agent("Operations Agent", "operations", "Coordinate execution steps and status reporting.", "operations", "operations-evals", ("assign tasks", "track execution")),
            ),
        ),
    )
