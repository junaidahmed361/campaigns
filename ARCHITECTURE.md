# Architecture

Campaigns is the campaign operating-system layer above AgentRL.

## Layers

```text
Layer 3: Campaigns
  Campaign -> Organization -> Team -> Employed Agent -> Contracts -> Review Dossier

Layer 2: AgentRL
  Harness definitions -> evaluation -> self-evolution -> versions -> deployment records

Layer 1: Runtimes
  Claude Code, OpenHarness, OpenHands, Codex, OpenCode, local tools
```

## Design commitments

1. Campaigns are outcome-centric, not task-centric.
2. Every employed agent has explicit accountability and a review surface.
3. Every employed agent is backed by an AgentRL pod instantiation.
4. Outsourcing is represented as contracts with objective, budget, deadline, success criteria, and trace obligations.
5. Human approval boundaries are first-class constraints.
6. Domain-specific organizations are generated from goals but remain inspectable and editable.

## AgentRL boundary

Campaigns stores references to AgentRL pods but does not evolve harnesses directly. A pod declaration identifies:

- pod name
- semantic version
- domain
- local project path or package
- harness entrypoint
- eval suite
- deployment channel

AgentRL owns whether that pod is good, improved, deployable, or rolled back.
