# Campaigns

Campaigns is an open-source swarm operating-system layer above AgentRL.

AgentRL answers:

```text
How do we improve, evaluate, evolve, version, and deploy an agent harness?
```

Campaigns answers:

```text
How do we continuously execute a user's goal through an evolving autonomous organization?
```

The core primitive is not a task or workflow. It is a campaign:

```yaml
campaign:
  objective: Increase recurring revenue
  budget:
    dollars: 5000
  timeline:
    days: 90
  metrics:
    - revenue
    - conversions
  constraints:
    - no cold email
    - human approval for spend > $500
```

A campaign turns a user goal into an accountable operating structure:

```text
Campaign
  -> Organization
  -> Team
  -> Employed Agent
  -> AgentRL Pod Instantiation
  -> Runtime / Harness
       -> Contracted Agents when work is outsourced
```

## Why this is separate from AgentRL

AgentRL should remain the harness lifecycle layer: definitions, evals, trajectories, self-evolution, versions, and deployment records for agent systems.

Campaigns sits above it. It composes AgentRL-powered pods into autonomous organizations that pursue outcomes across domains like business, marketing, research, and software.

## Install locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick start

Create a review dossier from an example campaign:

```bash
campaigns compile examples/revenue-growth.yaml
```

Or from Python:

```python
from campaigns import CampaignSpec, OrganizationBlueprint, CampaignCompiler

spec = CampaignSpec.from_dict({
    "objective": "Increase recurring revenue",
    "budget": {"dollars": 5000},
    "timeline": {"days": 90},
    "metrics": ["revenue", "conversions"],
    "constraints": ["no cold email", "human approval for spend > $500"],
})

blueprint = OrganizationBlueprint.default_for(spec)
dossier = CampaignCompiler().compile(spec, blueprint)
print(dossier.to_dict())
```

## Current primitives

- `CampaignSpec`: user-defined goal, budget, timeline, success metrics, and constraints.
- `AgentRLPodInstantiation`: a portable declaration of an AgentRL pod used by a campaign.
- `EmployedAgent`: an accountable campaign participant with a role, mandate, decision rights, and review obligations.
- `Contract`: outsourced work from an employed agent to a contracted agent or external pod.
- `OrganizationBlueprint`: org/team/agent layout generated from a campaign goal.
- `DecisionRecord`: auditable decisions for ultimate human review.
- `ReviewDossier`: the artifact a user reviews before approving execution or accepting outcomes.

## Boundary

Campaigns does not implement agent runtimes, model training, or harness evolution. It records which AgentRL pod should own those lifecycle responsibilities.

## Sister commercial app

The intended private sister repo is `campaigns-app`. It should provide hosted UI, billing, user workspaces, approvals, and commercial integrations while keeping these core campaign primitives open source.
