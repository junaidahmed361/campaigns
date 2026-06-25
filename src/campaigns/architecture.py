from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


IMMUTABLE_LAWS: tuple[str, ...] = (
    "The user specifies outcomes, never implementations.",
    "Every decision made by AgentOS must be explainable and reproducible.",
    "Every artifact must be measurable before it is accepted.",
)


@dataclass(frozen=True)
class CapabilityContract:
    """Provider-independent API surface for a unit of outcome-producing work."""

    name: str
    purpose: str
    requires: tuple[str, ...]
    produces: tuple[str, ...]
    evaluators: tuple[str, ...]
    artifact_schema: str
    acceptance_metrics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityImplementation:
    """Benchmarkable Capability x Driver x Prompt x Evaluator x Runtime binding."""

    contract: CapabilityContract
    driver: str
    prompt_profile: str
    runtime: str = "langgraph"
    evaluator_config: str = "default"
    provider: str | None = None

    @property
    def implementation_id(self) -> str:
        provider = self.provider or "provider-agnostic"
        return "::".join((self.contract.name, self.driver, provider, self.prompt_profile, self.evaluator_config, self.runtime))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["implementation_id"] = self.implementation_id
        return payload


@dataclass(frozen=True)
class ArtifactSpec:
    """Every capability, including planning, produces measurable artifacts."""

    name: str
    kind: str
    produced_by_capability: str
    measurable_by: tuple[str, ...]
    immutable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationSpec:
    """Evaluation exists before execution and gates acceptance and repair."""

    name: str
    target_artifact: str
    metric: str
    threshold: float
    repairable: bool = True
    evaluator_driver: str = "campaign-kernel"

    def accepts(self, score: float) -> bool:
        return score >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ImmutableReceipt:
    """Append-only provenance for a decision, run, or repair iteration."""

    receipt_id: str
    sequence: int
    subject: str
    artifact_ids: tuple[str, ...]
    evaluator_results: tuple[str, ...]
    parent_receipt_id: str | None = None
    supersedes: tuple[str, ...] = ()

    def append_repair(self, receipt_id: str, artifact_ids: tuple[str, ...], evaluator_results: tuple[str, ...]) -> "ImmutableReceipt":
        return ImmutableReceipt(
            receipt_id=receipt_id,
            sequence=self.sequence + 1,
            subject=self.subject,
            artifact_ids=artifact_ids,
            evaluator_results=evaluator_results,
            parent_receipt_id=self.receipt_id,
            supersedes=(self.receipt_id,),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CostOfQualitySample:
    """Quality gain per marginal dollar spent by a repair/evaluation iteration."""

    iteration: int
    quality_score: float
    cumulative_cost: float

    def marginal_gain_per_dollar(self, previous: "CostOfQualitySample") -> float:
        delta_quality = self.quality_score - previous.quality_score
        delta_cost = self.cumulative_cost - previous.cumulative_cost
        if delta_cost <= 0:
            return float("inf") if delta_quality > 0 else 0.0
        return delta_quality / delta_cost

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RoutingObjective:
    """Optimization target for capability routing: expected user value per dollar."""

    expected_user_value: float
    expected_cost: float
    rationale: str

    @property
    def euv_per_dollar(self) -> float:
        if self.expected_cost <= 0:
            return float("inf") if self.expected_user_value > 0 else 0.0
        return self.expected_user_value / self.expected_cost

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["euv_per_dollar"] = self.euv_per_dollar
        return payload


def phase0_capability_contracts() -> tuple[CapabilityContract, ...]:
    """Canonical starter contracts for Phase 0 AgentOS / Campaign Kernel work."""

    return (
        CapabilityContract(
            name="planning.dag",
            purpose="Convert an outcome request into an executable, budgeted DAG.",
            requires=("objective", "budget", "constraints", "quality_requirements"),
            produces=("dag", "budget_allocation", "routing_rationale"),
            evaluators=("dag_is_acyclic", "all_steps_have_artifacts", "budget_reservations_exist"),
            artifact_schema="PlanningArtifact.v1",
            acceptance_metrics=("coverage", "feasibility", "cost_bound"),
        ),
        CapabilityContract(
            name="backend.api",
            purpose="Produce backend source code, tests, and run evidence for a bounded API task.",
            requires=("repository", "task_spec", "acceptance_criteria"),
            produces=("source_code", "tests", "execution_receipt"),
            evaluators=("compile", "unit_tests", "contract_tests"),
            artifact_schema="SourceChangeArtifact.v1",
            acceptance_metrics=("test_pass_rate", "contract_coverage"),
        ),
        CapabilityContract(
            name="evaluation.quality_gate",
            purpose="Score artifacts before execution acceptance and before repair loop exit.",
            requires=("artifact", "evaluation_spec", "receipt_history"),
            produces=("evaluation_result", "repair_recommendation", "quality_delta"),
            evaluators=("threshold_check", "regression_check", "cost_of_quality"),
            artifact_schema="EvaluationArtifact.v1",
            acceptance_metrics=("score", "marginal_gain_per_dollar"),
        ),
    )


def phase0_artifact_specs() -> tuple[ArtifactSpec, ...]:
    return (
        ArtifactSpec("Planning DAG", "dag", "planning.dag", ("dag_is_acyclic", "steps_have_contracts", "budget_allocated")),
        ArtifactSpec("Routing Rationale", "decision_record", "planning.dag", ("explainable", "reproducible", "capability_contract_selected"), immutable=True),
        ArtifactSpec("Execution Receipt", "receipt", "backend.api", ("append_only", "links_artifacts", "links_evaluations"), immutable=True),
        ArtifactSpec("Evaluation Result", "quality_measurement", "evaluation.quality_gate", ("threshold_met", "repair_needed", "cost_of_quality_delta"), immutable=True),
    )
