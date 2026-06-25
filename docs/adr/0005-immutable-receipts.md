# ADR 0005: Immutable Receipts

Status: Accepted

## Context

AgentOS is evolving from a project into a platform. Future coding agents need rationale that preserves architectural boundaries.

## Decision

Receipts are append-only. Repair creates a new receipt with parent/supersedes links.

## Consequences

- Implementation must prefer boundary preservation over feature breadth.
- Tests should encode this decision when practical.
- Future changes should create a superseding ADR rather than silently changing philosophy.
