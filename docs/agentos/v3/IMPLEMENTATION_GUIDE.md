# Implementation Guide

## 1. Build Order

Build in this order:

1. Data model and migrations
2. ExecutionPolicy and Resource Manager
3. Idempotency middleware
4. Capability registry and contracts
5. Credential Plane
6. Provider/coding-agent driver interface
7. Benchmark intelligence scaffold
8. Campaign Kernel API
9. Planner
10. LangGraph runtime adapter
11. Resource reservation gateway
12. Evaluator framework
13. Bounded repair loop
14. Artifact manager
15. Immutable receipts
16. Hermes adapter
17. Minimal dashboard

## 2. Reuse Policy

Use compatible MIT/Apache components where appropriate.

Likely reusable:

- LangGraph for durable execution/checkpointing
- Hermes as conversational client
- Public benchmark metadata integrations
- Selected provider pricing catalogs
- OpenTelemetry ecosystem
- Existing local secret storage libraries

Do not adopt any framework in a way that makes it the system of record.

## 3. Non-Negotiable Architectural Boundaries

- Campaign Kernel owns state.
- Hermes is a client.
- LangGraph is a runtime.
- Providers are drivers.
- Credentials resolve only through the Credential Plane.
- Resource Manager is the only authority for spend/quota reservations.
- Evaluators are mandatory for accepted work.
- Receipts are immutable.

## 4. Distributed Systems Guarantees

Every mutating request must support idempotency.

Every external side effect must be behind:

1. Idempotency key
2. Resource reservation
3. Credential resolution
4. Driver invocation
5. Reconciliation
6. Ledger write
7. Event write

Use:

- Atomic DB transactions for reservations
- Row locks for resource counters
- Append-only ledger
- Outbox pattern
- Dead-letter queue
- Task leases
- Retry with dedupe
- Circuit breakers
- Provider health checks
- Explicit state machines

## 5. Open-Source vs Cloud Split

### Community/Open Source

Includes:

- Campaign Kernel
- Resource Manager
- BYOK credentials
- Local Dashboard
- Hermes integration
- Local execution policies
- Provider drivers
- Evaluator and repair loop
- Receipts

Does not include required payment wallet.

### Cloud/Managed

May include:

- Wallet
- Apple Pay
- Stripe
- Invoices
- Managed provider access
- Hosted benchmark intelligence
- Team accounts
- RBAC
- SSO
- Shared organization budgets

## 6. Resource Manager Rules

Before invoking a provider or coding agent:

1. Estimate cost/resource usage.
2. Reserve from the execution policy ledger.
3. Block if limit exceeded.
4. Execute through driver.
5. Reconcile actual usage.
6. Release unused reservation.
7. Commit actual usage to ledger.

No driver may call external APIs without a reservation.

## 7. Subscription Provider Handling

Some providers are not per-token API providers.

Examples:

- Claude Code
- Codex
- Cursor-like tools
- Local models

Represent these as subscription or local resources.

The router should prefer low marginal cost subscription/local providers when they satisfy quality/SLA constraints.

## 8. Testing Requirements

Must include tests for:

- Idempotent campaign creation
- Duplicate request dedupe
- Resource reservation enforcement
- Subscription provider routing
- API provider budget blocking
- Credential handle resolution
- Capability contract validation
- Evaluator pass/fail
- Bounded repair loop stopping
- Immutable receipt creation
- Outbox event publication


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
