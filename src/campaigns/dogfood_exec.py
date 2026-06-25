from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .cli_driver import CliDriverResponse, resolve_cli_driver
from .dogfood import AgentOSDogfoodResult, AgentOSDogfoodRunner, OutcomeRequest
from .resource_manager import ExecutionPolicy, ResourceManager, ResourceReservation


@dataclass(frozen=True)
class DogfoodExecutionResult:
    plan: AgentOSDogfoodResult
    reservation: ResourceReservation
    driver_response: CliDriverResponse
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan": self.plan.to_dict(),
            "reservation": self.reservation.to_dict(),
            "driver_response": self.driver_response.to_dict(),
            "status": self.status,
        }


class DogfoodExecutionRunner:
    """Resource Manager + local-CLI dogfood execution harness."""

    def run(
        self,
        request: OutcomeRequest,
        *,
        resource_limit_dollars: float | None = None,
        wallet_dollars: float | None = None,
        reserve_dollars: float,
        driver: str = "auto",
        driver_command: str | None = None,
        cwd: str | Path | None = None,
    ) -> DogfoodExecutionResult:
        plan = AgentOSDogfoodRunner().run(request)
        resource_ceiling = resource_limit_dollars if resource_limit_dollars is not None else wallet_dollars
        if resource_ceiling is None:
            resource_ceiling = request.budget_dollars or reserve_dollars
        reservation = ResourceManager(ExecutionPolicy.default_local_byok(resource_ceiling)).reserve_usd(reserve_dollars)
        if not reservation.accepted:
            response = CliDriverResponse(driver="none", command=(), returncode=1, stdout="", stderr=reservation.reason or "reservation rejected", provider_response="")
            return DogfoodExecutionResult(plan, reservation, response, "blocked_budget_reservation")
        prompt = self._provider_prompt(request, plan, reservation)
        response = resolve_cli_driver(driver, driver_command).run(prompt, cwd=cwd)
        status = "provider_response_received" if response.usable else "blocked_cli_driver"
        return DogfoodExecutionResult(plan, reservation, response, status)

    def _provider_prompt(self, request: OutcomeRequest, plan: AgentOSDogfoodResult, reservation: ResourceReservation) -> str:
        return (
            "You are a local CLI driver behind AgentOS. Do not ask the user to choose a provider. "
            "Return a concise provider response artifact only.\n\n"
            f"Goal: {request.goal}\n"
            f"Resource reservation: {reservation.reserved_amount} {reservation.unit} from a {request.budget_dollars} USD campaign resource ceiling.\n"
            f"Constraints: {', '.join(request.constraints) or 'none'}\n"
            f"Quality requirements: {', '.join(request.quality_requirements) or 'none'}\n"
            f"Selected capabilities: {', '.join(plan.selected_capabilities)}\n"
            "Required response shape:\n"
            "1. Provider response artifact\n"
            "2. How the artifact satisfies quality requirements\n"
            "3. Confirmation that provider complexity stayed hidden\n"
        )
