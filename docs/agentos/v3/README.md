# AgentOS / Campaign Kernel Architecture Package

This package contains the revised architecture scaffold for a provider-agnostic campaign execution platform.

## Product Thesis

A user should be able to specify:

- A goal
- An execution policy
- A fixed campaign cost ceiling or resource limit
- SLA requirements
- Design/code quality requirements
- Security and privacy constraints

The system should then plan, route, execute, evaluate, repair, and deliver artifacts without requiring the user to choose providers, models, agents, or orchestration frameworks.

## Core Product Language

Recommended external positioning:

> One goal. One execution policy. Every provider.

or

> The control plane for autonomous goal execution.

## Key Architectural Decision

The open-source edition should not include a payment wallet as a core primitive.

Instead, the core system uses a Resource Manager that enforces budgets, quotas, subscriptions, token limits, latency bounds, local execution preferences, and provider usage policies.

Cloud/managed editions may add:

- Wallet
- Apple Pay
- Stripe
- Invoicing
- Managed provider access
- Hosted benchmark intelligence
- Team/enterprise billing

## Documents

- ARCHITECTURE.md
- API_SPEC.md
- DATA_MODEL.md
- IMPLEMENTATION_GUIDE.md
- SEQUENCE_DIAGRAMS.md
- CODING_AGENT_PROMPT.md


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
