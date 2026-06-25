# AgentOS / Campaign Kernel Architecture

## 1. Product Thesis

AgentOS, internally powered by the Campaign Kernel, is a control plane for autonomous goal execution.

The user should not need to choose between Claude Code, Codex, Fugu, OpenAI, Anthropic, Gemini, LangGraph, CrewAI, OpenHands, local models, or future providers.

The user specifies:

- Goal
- Execution policy
- SLA
- Quality requirements
- Security constraints
- Deadline
- Budget/resource ceiling

The system decides how to accomplish the goal.

## 2. Naming Recommendation

Use these names intentionally:

- Campaign Kernel: core engine and open-source runtime.
- AgentOS: product/distribution built around the kernel.
- Dashboard: management UI.
- Hermes: conversational client.
- Drivers: replaceable provider/runtime integrations.

## 3. Core Abstraction

The primary abstraction is not a prompt, model, or agent.

The primary abstraction is:

```text
Goal
  -> Campaign
  -> Objectives
  -> Capabilities
  -> Work Units
  -> Evaluations
  -> Artifacts
  -> Receipts
```

## 4. Planes

### Presentation Plane

- AgentOS Dashboard
- Hermes client
- CLI
- SDK
- MCP server
- VSCode/IDE integrations later

### Control Plane

- Campaign Kernel
- Goal compiler
- Planner
- Scheduler
- Resource Manager
- Capability Router
- Policy Engine
- Approval Engine

### Knowledge Plane

- Shared memory
- Artifacts
- Evaluations
- Receipts
- Telemetry
- Benchmark history

### Execution Plane

- LangGraph runtime
- Provider drivers
- Coding-agent drivers
- Fugu/orchestrator drivers
- Local model drivers
- Tool/MCP drivers

### Infrastructure Plane

- PostgreSQL
- Redis
- pgvector where needed
- Object storage
- OpenTelemetry
- Prometheus/Grafana

## 5. Resource Manager Replaces Wallet in Core

The open-source Campaign Kernel does not contain a payment wallet.

It contains a Resource Manager.

The Resource Manager enforces:

- Dollar ceilings for API-based providers
- Token quotas
- Subscription usage preferences
- Monthly limits
- Per-campaign limits
- Per-work-unit limits
- Latency limits
- Retry budgets
- Local-first policies
- Provider allow/deny rules
- Human approval thresholds

Money is one resource, not the only resource.

### Example Execution Policy

```yaml
execution_policy:
  monthly_api_spend_limit_usd: 150
  per_campaign_limit_usd: 10
  per_work_unit_limit_usd: 1
  prefer_subscription_providers: true
  prefer_local: true
  reserve_percent: 20
  max_repair_iterations: 2
  require_approval_above_usd: 5

providers:
  claude_code:
    enabled: true
    pricing_model: subscription
    marginal_cost_usd: 0
    usage_limit_policy: conservative

  codex:
    enabled: true
    pricing_model: subscription
    marginal_cost_usd: 0

  openai_api:
    enabled: true
    pricing_model: token_api
    monthly_limit_usd: 50

  ollama:
    enabled: true
    pricing_model: local
    marginal_cost_usd: 0
```

## 6. Cloud Wallet Is a Separate Module

Cloud editions may implement:

```text
Resource Manager
  -> Billing Provider Interface
      -> Stripe / Apple Pay / invoices / managed provider credits
```

The Campaign Kernel should only depend on a generic interface:

```python
resource_manager.reserve(...)
resource_manager.release(...)
resource_manager.commit(...)
resource_manager.balance(...)
resource_manager.usage(...)
```

Cloud wallet, Apple Pay, Stripe, invoices, and managed credits are plugins/modules outside the open-source kernel.

## 7. Capability-Based Routing

Routing happens by capability, not provider.

Example:

```text
Capability: Repository Refactor

Eligible implementations:
- Claude Code driver
- Codex driver
- OpenHands driver
- Fugu driver
- Local SWE-agent driver
```

The router selects an implementation based on:

- Capability contract
- Execution policy
- Resource availability
- Benchmark intelligence
- Local historical performance
- Quality requirements
- Latency/deadline
- Security constraints
- Credential availability
- Provider health

## 8. Capability Contracts

Every capability must define:

```yaml
capability: backend_api

inputs:
  - repository
  - requirements
  - coding_standards

outputs:
  - source_code
  - tests
  - documentation
  - receipt

evaluators:
  - compile
  - unit_tests
  - security_scan
  - architecture_review

resource_constraints:
  supports_budget_reservation: true
  supports_retry: true
  supports_local_execution: false

quality_gates:
  min_test_coverage: 0.85
  max_lint_errors: 0
```

## 9. Evaluator and Bounded Self-Improvement Loop

Phase 0 must include a bounded improvement loop.

Lifecycle:

```text
Plan
  -> Execute Work Unit
  -> Evaluate
  -> Repair if:
       - budget/resource remains
       - max repair iterations not reached
       - expected quality gain exceeds threshold
  -> Evaluate again
  -> Accept / Escalate / Fail
```

This is not open-ended autonomous self-modification. It is bounded, auditable repair.

## 10. Benchmark Intelligence

Phase 0 should include basic benchmark-informed routing.

Sources can include:

- Public model/coding benchmarks
- Provider pricing metadata
- Local campaign telemetry
- Local evaluator outcomes
- User approval/rejection history

The router should benchmark implementations, not just providers.

An implementation is:

```text
Capability + Driver + Prompt/Policy + Runtime + Evaluator config
```

## 11. Credential Plane

Credentials are not owned by Hermes.

Credentials resolve through the Credential Plane.

Credential classes:

1. Platform credentials: Cloud-only, owned by AgentOS service.
2. User BYOK credentials: local/user-owned provider credentials.
3. Ephemeral credentials: OAuth sessions, temporary IAM roles, MCP sessions.

Open-source local mode should use OS keychain or encrypted local storage.

Drivers receive credential handles, not raw credentials.

## 12. Hermes Integration

Hermes should be a client, not a plugin host.

```text
Hermes
  -> AgentOS API / MCP
  -> Campaign Kernel
```

Hermes responsibilities:

- Chat interface
- Campaign creation UX
- Approval UX
- Artifact viewing
- Status rendering
- Credential settings UI

Campaign Kernel owns:

- Planning
- Routing
- Budget/resource enforcement
- Execution
- Evaluation
- Memory
- Receipts

## 13. Dashboard

AgentOS also needs its own minimal dashboard.

Initial pages:

- Dashboard
- Campaigns
- Work Units
- Resources
- Approvals
- Artifacts
- Evaluations
- Credentials
- Settings

The dashboard should be mission-control style, not chat-first.

## 14. Phase 0 Scope

Phase 0 includes:

- Campaign Kernel
- Goal-to-campaign API
- Capability registry
- Capability contracts
- Resource Manager
- Execution policies
- BYOK Credential Plane
- Benchmark-informed routing
- Budget/resource reservation ledger
- LangGraph runtime adapter
- Provider/coding-agent drivers
- Evaluator layer
- Bounded repair loop
- Artifact manager
- Immutable receipts
- Hermes client adapter
- Minimal AgentOS Dashboard
- Distributed-systems correctness primitives

## 15. Deferred

Defer until after dogfooding:

- World State
- Simulation
- WorldForge
- RL router
- Learned orchestration
- Capability marketplace
- Swarm coordination
- Managed wallet/cloud billing
- Apple Pay/Stripe/invoicing


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
