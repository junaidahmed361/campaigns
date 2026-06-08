# Architecture

Campaigns is the campaign operating-system layer above AgentRL.

## Layers

```text
Layer 3: Campaigns
  Campaign -> Workflow DAG -> Organization -> Team -> Employed Agent -> Contracts -> Trace Monitor -> Performance Review -> Ultimate User Review

Layer 2: AgentRL
  Targeted harness definitions -> evaluation -> self-evolution -> versions -> deployment/rollback records

Layer 1: Runtimes
  Claude Code, OpenHarness, OpenHands, Codex, OpenCode, local tools
```

## Dynamic DAG

```text
create_harness
  ↓
define_campaign
  ↓
employ_fleet
  ↓
plan
  ↓
research
  ↓
contract
  ├─ contract_1: SEO optimization
  ├─ contract_2: outreach/follow-up preparation
  └─ contract_n: other bounded specialist work
  ↓
synthesize
  ↓
performance_review
  ↓
ultimate_review
  ↓
evolve
```

## Design commitments

1. Campaigns are outcome-centric, not task-centric.
2. Harness creation happens in AgentRL first; Campaigns employs harness-backed agents.
3. Every employed fleet agent has explicit accountability and a review surface.
4. Contract agents are short-term outsourced workers; employed agents remain accountable for synthesis and decisions.
5. Outsourcing is represented as contracts with objective, budget, deadline, success criteria, trace requirements, and deliverables.
6. Human approval boundaries are first-class constraints.
7. Final review is aggregated across the full fleet and contract graph.
8. Trace monitoring supports performance reviews without forcing user micromanagement.
9. AgentRL consumes traces and review outcomes for harness evolution, promotion, deployment, or rollback.

## AgentRL boundary

Campaigns stores references to AgentRL pods but does not evolve harnesses directly. A pod declaration identifies:

- pod name
- semantic version
- domain
- local project path or package
- harness entrypoint
- eval suite
- deployment channel
- attached harness components

AgentRL owns whether that pod is good, improved, deployable, or rolled back.

## Commercial app boundary

The private `campaigns-app` repo should own hosted and commercial surfaces:

- campaign intake UI
- harness/fleet selection UI
- approval queue
- trace and performance dashboards
- billing and quotas
- workspace permissions
- commercial integrations

The OSS repo should remain the reusable primitive layer.
