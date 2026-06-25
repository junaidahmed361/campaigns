# ADR 0004: Evaluator Before Execution

Status: Accepted

## Context

AgentOS is evolving from a project into a platform. Future coding agents need rationale that preserves architectural boundaries.

## Decision

Evaluation specs are created before execution. Bounded repair loops depend on measurable artifact acceptance criteria.

## Consequences

- Implementation must prefer boundary preservation over feature breadth.
- Tests should encode this decision when practical.
- Future changes should create a superseding ADR rather than silently changing philosophy.
