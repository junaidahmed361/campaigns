# ADR 0003: LangGraph as Runtime Only

Status: Accepted

## Context

AgentOS is evolving from a project into a platform. Future coding agents need rationale that preserves architectural boundaries.

## Decision

LangGraph owns execution, checkpoints, and streaming. Campaign Kernel owns state, memory, budgets, receipts, artifacts, and decisions.

## Consequences

- Implementation must prefer boundary preservation over feature breadth.
- Tests should encode this decision when practical.
- Future changes should create a superseding ADR rather than silently changing philosophy.
