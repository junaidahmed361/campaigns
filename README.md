# Campaigns

[![PyPI version](https://badge.fury.io/py/campaigns-os.svg)](https://pypi.org/project/campaigns-os/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://pypi.org/project/campaigns-os/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/junaidahmed361/campaigns/blob/main/LICENSE)
[![CI](https://github.com/junaidahmed361/campaigns/actions/workflows/ci.yml/badge.svg)](https://github.com/junaidahmed361/campaigns/actions/workflows/ci.yml)
[![Package](https://github.com/junaidahmed361/campaigns/actions/workflows/package.yml/badge.svg)](https://github.com/junaidahmed361/campaigns/actions/workflows/package.yml)

Campaigns is an open-source campaign operating-system layer above AgentRL.

The design is inspired by multi-agent economies such as Qi et al., "Economy of Minds: Emerging Multi-Agent Intelligence with Economic Interactions" (2026), https://arxiv.org/pdf/2606.02859, especially the idea that capable agent societies need explicit interaction protocols, resource constraints, specialization, and outcome-oriented coordination rather than a flat task list.

## Architectural layer boundary

Campaigns intentionally models the layer above AgentRL:

```text
Layer 1: Runtime
  Question: How does one agent solve a task?
  Output: Trajectory
  Examples: Claude Code, OpenHarness, OpenHands, Codex, OpenCode

Layer 2: Harness Lifecycle
  Question: How do we improve, evaluate, evolve, version, and deploy agents?
  Output: Improved Agent System
  Owner: AgentRL

Layer 3: Swarm Operating System
  Question: How do we continuously execute business objectives through evolving agent organizations?
  Output: Campaign Outcome
  Owner: Campaigns
```

AgentRL powers Campaigns through deployable pods; Campaigns should not absorb AgentRL's lifecycle responsibilities.

AgentRL answers:

```text
How do we improve, evaluate, evolve, version, and deploy an agent harness?
```

Campaigns answers:

```text
How do we continuously execute a user's goal through an evolving autonomous organization?
```

The user does not micromanage every task. The user defines goals, reviews harnesses and approval gates, monitors traces when desired, and receives an ultimate final review packet across the fleet and contract agents.

## Dynamic workflow

```text
1. User creates a targeted AgentRL harness
   Example: Market Researcher with RAG, trace, decision-log, evaluation, memory, and approval-gate components.

2. User defines a campaign
   Example: run a marketing campaign using the Market Researcher and RAG Analyst harnesses.

3. Campaigns employs those harnesses as fleet agents
   Each employed agent has a mandate, decision rights, review obligations, and an AgentRL pod declaration.

4. Fleet agents plan and execute bounded work
   The Market Researcher runs RAG-grounded research. The Campaign Manager creates approval gates and operating cadence.

5. Fleet agents contract short-term specialist workers in parallel
   Example contracts: SEO Optimizer, Outreach Worker, Creative Worker, Analytics Worker.

6. Contract agents return deliverables, traces, costs, and evidence
   Employed agents remain accountable for synthesis and decisions.

7. Campaigns synthesizes a final report
   The user receives one final review packet across all fleet and contract agents instead of being forced to micromanage.

8. User monitors traces and performance reviews when desired
   Trace monitors expose decision quality, constraint compliance, contract outcomes, evidence quality, and cost/timeline drift.

9. User performs ultimate review
   Approve, revise, stop, or launch the next iteration.

10. AgentRL consumes traces and review outcomes
    Harnesses can evolve, be versioned, promoted, deployed, or rolled back.
```

## Campaign primitive

```yaml
campaign:
  objective: Increase recurring revenue by 30% for a local detailing business
  budget:
    dollars: 5000
  timeline:
    days: 90
  metrics:
    - recurring_revenue
    - conversion_rate
  constraints:
    - human approval for spend > $500
  employed_harnesses:
    - agent_name: Market Researcher
      role: market_researcher
      objective: Research demand, competitors, segments, and campaign risks
      components: [rag, trace, decision_log, evaluation]
    - agent_name: RAG Analyst
      role: rag_analyst
      objective: Retrieve and synthesize evidence for claims and assumptions
      components: [rag, trace, evaluation]
```

A campaign turns a user goal into an accountable operating structure:

```text
Campaign
  -> Workflow DAG
  -> Organization
  -> Team
  -> Employed Fleet Agent
  -> AgentRL Pod Instantiation
  -> Runtime / Harness
       -> Contracted Agents for short-term parallel work
  -> Trace Monitor
  -> Performance Reviews
  -> Ultimate User Review
  -> AgentRL Evolution / Promotion / Rollback
```

## Install

From PyPI after release:

```bash
pip install campaigns-os
```

From source:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run from GitHub Container Registry after package publication:

```bash
docker pull ghcr.io/junaidahmed361/campaigns:latest
docker run --rm ghcr.io/junaidahmed361/campaigns:latest --version
```

## Quick start

Create a review dossier from an example campaign:

```bash
campaigns compile examples/revenue-growth.yaml
```

Or from Python:

```python
from campaigns import CampaignSpec, CampaignCompiler

spec = CampaignSpec.from_dict({
    "objective": "Increase recurring revenue",
    "metrics": ["revenue", "conversions"],
    "employed_harnesses": [{
        "agent_name": "Market Researcher",
        "role": "market_researcher",
        "objective": "Research the market with RAG-grounded evidence",
        "components": ["rag", "trace", "decision_log", "evaluation"],
    }],
})

dossier = CampaignCompiler().compile(spec)
print(dossier.to_dict()["workflow"])
```

## Current primitives

- `AgentHarnessDefinition`: campaign-side reference to a user-created targeted AgentRL harness.
- `CampaignSpec`: user-defined goal, budget, timeline, success metrics, constraints, and employed harnesses.
- `ArchitectureLayer`: explicit Runtime / Harness Lifecycle / Swarm Operating System boundary so Campaigns stays above AgentRL.
- `WorldModelScenario`: simulated future with expected metrics, cost, risk, and rationale before execution.
- `AgentRLPodInstantiation`: portable declaration of an AgentRL pod used by an employed or contract agent.
- `EmployedAgent`: accountable fleet participant with role, mandate, decision rights, contracts, and review obligations.
- `Contract`: outsourced short-term specialist work with success criteria, trace requirements, and a contracted pod.
- `WorkflowStep`: DAG step for harness creation, campaign definition, fleet employment, contract work, synthesis, performance review, ultimate review, and AgentRL evolution.
- `TraceMonitor`: user-monitorable trace surface for fleet performance reviews.
- `PerformanceReview`: scorecard scaffold for reviewing employed agents without micromanagement.
- `ReviewDossier`: final artifact the user reviews before approving execution, accepting outcomes, or triggering another iteration.
- `CampaignAutorun`: simple `fit` / `transform` / `score` / `autorun` primitive for bounded observe-plan-act-verify-review loops.
- `AutorunPolicy`, `GoalCheck`, and `CampaignIteration`: `/goal`-style loop limits, stop conditions, second-model goal checks, independent final auditor hints, budget pause/resume state, and iteration records.
- `RetrospectiveFeedback`: continual-learning feedback that routes reinforcement to either Campaigns-owned next-iteration strategy or AgentRL-owned agent harness lifecycle updates.
- `CampaignAutorun.final_review(...)`: after the user gives final review, a retro agent traverses trace surfaces across all employed agents, attributes root cause, and plans AgentRL self-reinforcement for the relevant harness.

SDK retro example:

```python
from campaigns import CampaignAutorun

runner = CampaignAutorun().fit(campaign)
runner.autorun(max_loops=1)
retro = runner.retro({
    "summary": "The Market Researcher missed competitor pricing evidence.",
    "attention_level": "agentrl",
    "target": "Market Researcher",
    "reinforce": "Require competitor price citations before recommendations.",
})
```

## Boundary

Campaigns does not implement agent runtimes, model training, harness evaluation, harness evolution, or deployment. It records which AgentRL pod should own those lifecycle responsibilities and how the campaign organization composes them. AgentRL does not implement campaign autorun, campaign organizations, contracted-worker queues, performance-review dashboards, or marketing/business workflow policy; those belong in Campaigns.

## Claude-style loop autorun

Campaigns includes a simple scikit-learn-style autorun primitive for dynamic campaign workflows:

```python
from campaigns import CampaignAutorun

runner = CampaignAutorun().fit(spec)
dossier = runner.transform()
readiness = runner.score()
result = runner.autorun(max_loops=3)
```

The autorun loop is intentionally an operating plan, not an agent runtime:

```text
observe -> plan -> act -> verify -> review -> repeat until approval/stop/limit
```

It can select workflow steps dynamically across loops, preserve trace/review surfaces, and stop at ultimate user review. Runtime execution is delegated to agent systems; harness lifecycle feedback is handed to AgentRL.

CLI:

```bash
campaigns autorun examples/revenue-growth.yaml --loops 3
```

## Sister commercial app

The private sister repo is `campaigns-app`. It provides the commercial interface around the open-source core: hosted UI, billing, user workspaces, approvals, trace/performance dashboards, and integrations.
