# ADR 0001: Use Campaign Kernel as the Core Repository Concept

Status: Accepted

## Context

AgentOS is evolving from a project into a platform. Future coding agents need rationale that preserves architectural boundaries.

## Decision

The repo should not be named agentos. Campaign Kernel remains independently testable and AgentOS packages dashboard, SDK, MCP, docs, and drivers around it.

## Consequences

- Implementation must prefer boundary preservation over feature breadth.
- Tests should encode this decision when practical.
- Future changes should create a superseding ADR rather than silently changing philosophy.
