# ADR 0007: Resource Manager, not Wallet, in the Open-Source Core

## Status
Accepted

## Context
AgentOS needs hard limits before provider calls, but a payment wallet is a cloud/business concern. The open-source Campaign Kernel must support BYOK, subscription providers such as Claude Code and Codex, local providers such as Ollama/vLLM, and token API providers with monthly limits.

## Decision
Use **Resource Manager** as the open-source core primitive.

The Resource Manager owns:

- execution policy interpretation
- resource reservations
- quota/spend ceilings
- subscription/local-provider preferences
- repair-iteration limits
- ledger entries
- reconciliation

Wallet, Apple Pay, Stripe, invoices, managed provider credits, and team billing are optional Cloud modules layered behind Resource Manager interfaces.

## Consequences
- No provider or coding-agent driver call can happen without a Resource Manager reservation.
- The kernel can dogfood through existing Claude/Codex subscription CLI auth without implementing billing.
- Hermes and dashboards display resource state returned by Campaign Kernel; they do not own budget logic.
