# ADR 0008: Defer World State, Simulation, Learned Router, and RL

Status: Accepted

## Context

AgentOS is evolving from a project into a platform. Future coding agents need rationale that preserves architectural boundaries.

## Decision

Those features require real campaign, repair, routing, evaluator, and receipt history before they can be principled.

## Consequences

- Implementation must prefer boundary preservation over feature breadth.
- Tests should encode this decision when practical.
- Future changes should create a superseding ADR rather than silently changing philosophy.
