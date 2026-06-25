# Coding Agent Handoff Prompt

You are implementing the first architecture repository and Phase 0 scaffold for AgentOS / Campaign Kernel.

## Product Thesis

The user gives a goal, execution policy, SLA, and quality constraints. The system accomplishes the goal without exposing provider complexity.

The user should not have to choose Claude, Codex, OpenAI, Anthropic, Gemini, Fugu, LangGraph, CrewAI, or local models. Those are implementation details.

## Naming

Use:

- Campaign Kernel for the open-source core engine.
- AgentOS for the product/distribution.
- Resource Manager instead of Wallet in the open-source core.
- Wallet/Billing only as optional Cloud modules.
- Execution Policy as the user-facing constraint bundle.

## Critical Revision

Do not implement a wallet in the open-source core.

The open-source edition should support BYOK and subscription/local providers through execution policies.

Examples:

- Claude Code subscription
- Codex subscription
- OpenAI API key with monthly limit
- Anthropic API key with monthly limit
- Local Ollama/vLLM with marginal cost zero

The Resource Manager tracks and enforces limits but does not process payments.

## Required Phase 0 Modules

1. Campaign Kernel
2. Execution Policy model
3. Resource Manager
4. Resource reservation ledger
5. Capability registry
6. Capability contracts
7. Benchmark-informed routing scaffold
8. Credential Plane
9. Provider/coding-agent driver interface
10. LangGraph runtime adapter
11. Planner
12. Evaluator framework
13. Bounded repair loop
14. Artifact manager
15. Immutable receipt engine
16. Event bus/outbox
17. Hermes adapter
18. Minimal dashboard

## Hard Constraints

- Hermes is a client, not the system of record.
- LangGraph is a runtime, not the system of record.
- Providers are drivers, not product abstractions.
- Credentials resolve only through the Credential Plane.
- No provider call can happen without a Resource Manager reservation.
- Every mutating API must support idempotency.
- Every accepted artifact must pass evaluation or receive human approval.
- Every campaign must produce an immutable receipt.
- World State and simulation are deferred.
- Wallet, Apple Pay, Stripe, and invoices are Cloud-only modules.

## First Implementation Task

Create a repo scaffold with:

```text
campaign-kernel/
  src/
    kernel/
      api/
      campaigns/
      work_units/
      capabilities/
      resources/
      credentials/
      routing/
      planning/
      execution/
      evaluation/
      repair/
      artifacts/
      receipts/
      events/
      telemetry/
      drivers/
      runtime/
  tests/
  docs/
```

Add:

- SQLAlchemy/Pydantic models for Campaign, WorkUnit, Capability, CapabilityImplementation, ExecutionPolicy, ResourceReservation, ResourceLedgerEntry, CredentialHandle, Artifact, Evaluation, Receipt, Event.
- Idempotency middleware.
- Resource reservation service.
- Driver interface.
- Capability contract validator.
- Dummy providers for subscription, token API, and local execution.
- Evaluator interface and simple quality gate.
- Bounded repair loop with max iterations and resource checks.
- Receipt generation.
- Unit tests for all hard constraints.

## Architectural Priority

When choosing between more features and stronger boundaries, choose stronger boundaries.


# Hermes Dogfooding Mode (Phase 0)

## Objective

Hermes is the primary day-1 user interface for dogfooding. Do NOT fork Hermes or embed Campaign Kernel logic into Hermes.

Architecture:

Hermes (client)
    -> AgentOS MCP Server (preferred)
       or REST API
    -> Campaign Kernel

## Required Integration

Implement a thin Hermes adapter exposing:

- create_campaign(goal, execution_policy)
- list_campaigns()
- campaign_status(id)
- approve(id)
- reject(id)
- list_artifacts(id)
- open_artifact(id)
- receipt(id)
- execution_policy_get()
- execution_policy_update()

Hermes should only render state returned by AgentOS.

## MCP

Expose Campaign Kernel functionality through an MCP server in Phase 0 so Hermes can consume it as tools without custom orchestration logic.

## Deferred UI

Do NOT build a sophisticated dashboard initially.

A minimal React dashboard is sufficient for:
- Campaign list
- Campaign timeline
- Resources
- Pending approvals
- Artifacts
- Receipts
- Credentials

Hermes remains the primary interaction surface during dogfooding.
