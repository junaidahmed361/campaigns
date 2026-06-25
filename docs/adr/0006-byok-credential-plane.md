# ADR 0006: BYOK Credential Plane

Status: Accepted

## Context

AgentOS is evolving from a project into a platform. Future coding agents need rationale that preserves architectural boundaries.

## Decision

Credentials resolve through scoped handles in the Credential Plane. Clients and chat never become secret stores.

## Consequences

- Implementation must prefer boundary preservation over feature breadth.
- Tests should encode this decision when practical.
- Future changes should create a superseding ADR rather than silently changing philosophy.
