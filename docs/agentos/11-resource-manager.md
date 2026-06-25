# Resource Manager

The open-source Campaign Kernel does **not** contain a payment wallet.

It contains a Resource Manager that enforces execution policies across multiple resource types:

- API dollar ceilings
- token quotas
- subscription-provider usage preferences
- local execution preferences
- monthly, campaign, and work-unit limits
- latency and retry budgets
- repair-iteration limits
- human-approval thresholds

Money is one resource, not the product abstraction. Cloud/managed AgentOS editions may add Wallet, Apple Pay, Stripe, invoices, managed provider access, team billing, and hosted benchmark intelligence as optional modules behind the Resource Manager interface.

Provider calls must follow this sequence:

```text
Execution Policy
  -> Resource Manager reservation
  -> Credential Plane handle resolution
  -> Capability implementation / driver invocation
  -> evaluation
  -> reconciliation
  -> ledger entry
  -> immutable receipt
```

No provider call can happen without a Resource Manager reservation, and every accepted artifact must be evaluated or explicitly approved.
