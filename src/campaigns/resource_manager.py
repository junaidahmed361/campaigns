from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionPolicy:
    """User-facing resource and execution constraints.

    The open-source Campaign Kernel uses a Resource Manager, not a payment
    wallet. Money is one resource among subscription quota, tokens, local
    compute, repair iterations, latency, and human approvals.
    """

    name: str = "local-byok-default"
    monthly_api_spend_limit_usd: float | None = None
    per_campaign_limit_usd: float | None = None
    per_work_unit_limit_usd: float | None = None
    prefer_subscription_providers: bool = True
    prefer_local: bool = True
    reserve_percent: float = 20.0
    max_repair_iterations: int = 2
    require_approval_above_usd: float | None = None
    provider_rules: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def default_local_byok(cls, campaign_limit_usd: float | None = 25.0) -> "ExecutionPolicy":
        return cls(
            per_campaign_limit_usd=campaign_limit_usd,
            per_work_unit_limit_usd=2.5 if campaign_limit_usd is None else min(2.5, campaign_limit_usd),
            provider_rules={
                "claude_code": {"enabled": True, "pricing_model": "subscription", "marginal_cost_usd": 0},
                "codex": {"enabled": True, "pricing_model": "subscription", "marginal_cost_usd": 0},
                "ollama": {"enabled": True, "pricing_model": "local", "marginal_cost_usd": 0},
                "openai_api": {"enabled": False, "pricing_model": "token_api"},
                "anthropic_api": {"enabled": False, "pricing_model": "token_api"},
            },
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ExecutionPolicy":
        if not data:
            return cls.default_local_byok()
        payload = data.get("execution_policy", data)
        return cls(
            name=payload.get("name", "local-byok-default"),
            monthly_api_spend_limit_usd=payload.get("monthly_api_spend_limit_usd"),
            per_campaign_limit_usd=payload.get("per_campaign_limit_usd", payload.get("max_campaign_spend_usd")),
            per_work_unit_limit_usd=payload.get("per_work_unit_limit_usd"),
            prefer_subscription_providers=payload.get("prefer_subscription_providers", True),
            prefer_local=payload.get("prefer_local", True),
            reserve_percent=payload.get("reserve_percent", 20.0),
            max_repair_iterations=payload.get("max_repair_iterations", 2),
            require_approval_above_usd=payload.get("require_approval_above_usd"),
            provider_rules=payload.get("provider_rules", payload.get("providers", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResourceReservation:
    reservation_id: str
    resource_type: str
    requested_amount: float
    reserved_amount: float
    remaining_amount: float
    unit: str
    accepted: bool
    real_payment_processor: bool = False
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ResourceManager:
    """Phase 0 resource manager: fixed limits, append-only reservation records.

    This intentionally does not process payments. Cloud wallets, Stripe, Apple
    Pay, invoices, and managed credits are separate modules layered behind this
    interface in managed editions.
    """

    def __init__(self, policy: ExecutionPolicy):
        self.policy = policy
        self._reservations: list[ResourceReservation] = []

    @property
    def reservations(self) -> tuple[ResourceReservation, ...]:
        return tuple(self._reservations)

    def reserve_usd(self, amount: float, reservation_id: str = "resource-reservation-0001") -> ResourceReservation:
        ceiling = self.policy.per_campaign_limit_usd
        if ceiling is None:
            accepted = amount >= 0
            remaining = 0.0
        else:
            committed = sum(r.reserved_amount for r in self._reservations if r.resource_type == "usd" and r.accepted)
            accepted = 0 <= amount <= max(ceiling - committed, 0.0)
            remaining = round(ceiling - committed - amount, 2) if accepted else round(ceiling - committed, 2)
        reservation = ResourceReservation(
            reservation_id=reservation_id,
            resource_type="usd",
            requested_amount=amount,
            reserved_amount=amount if accepted else 0.0,
            remaining_amount=remaining,
            unit="usd",
            accepted=accepted,
            real_payment_processor=False,
            reason=None if accepted else "reservation exceeds execution policy resource ceiling",
        )
        self._reservations.append(reservation)
        return reservation

    def usage(self) -> dict[str, Any]:
        return {
            "policy": self.policy.to_dict(),
            "reservations": [reservation.to_dict() for reservation in self._reservations],
            "real_payment_processor": False,
        }


# Backward-compatible aliases for the earlier Phase 0 dogfood name. New code
# should use ResourceManager/ResourceReservation/ExecutionPolicy.
BudgetReservation = ResourceReservation


@dataclass(frozen=True)
class FixedWallet:
    """Compatibility shim over ResourceManager; not a core wallet primitive."""

    balance_dollars: float

    def reserve(self, amount_dollars: float, reservation_id: str = "resource-reservation-0001") -> ResourceReservation:
        return ResourceManager(ExecutionPolicy.default_local_byok(self.balance_dollars)).reserve_usd(amount_dollars, reservation_id)
