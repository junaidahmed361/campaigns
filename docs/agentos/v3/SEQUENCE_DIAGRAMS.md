# Sequence Diagrams

## 1. Local BYOK Campaign Execution

```text
User
  -> Hermes/Dashboard: submit goal + execution policy
  -> Campaign API: POST /campaigns
  -> Campaign Kernel: create campaign
  -> Planner: create work units
  -> Resource Manager: check policy limits
  -> Capability Router: select implementation
  -> Credential Plane: resolve credential handle
  -> Resource Manager: reserve resources
  -> Runtime Adapter: execute work unit
  -> Driver: invoke provider/coding agent
  -> Resource Manager: reconcile actual usage
  -> Artifact Manager: store artifact
  -> Evaluator: score artifact
  -> Repair Loop: repair if needed and allowed
  -> Receipt Engine: create immutable receipt
  -> Event Stream: notify Hermes/Dashboard
```

## 2. Resource Reservation

```text
Work Unit Executor
  -> Resource Manager: estimate + reserve
  -> DB: SELECT policy/usage FOR UPDATE
  -> DB: insert reservation
  -> Executor: invoke driver
  -> Driver: execute
  -> Resource Manager: reconcile
  -> DB: append ledger entry
  -> DB: mark reservation committed/released
```

## 3. Bounded Repair Loop

```text
Execution Result
  -> Evaluator: evaluate artifact
  -> Quality Gate: pass?
      yes -> accept artifact
      no -> check repair policy
  -> Resource Manager: repair budget remains?
  -> Repair Planner: create repair work unit
  -> Executor: run repair
  -> Evaluator: re-evaluate
  -> Stop when:
      pass
      max iterations reached
      budget/resource exhausted
      marginal quality gain too low
      human approval required
```

## 4. Hermes Integration

```text
Hermes
  -> AgentOS API/MCP: create campaign
  <- Event Stream: campaign planned
  <- Event Stream: approval requested
  -> AgentOS API/MCP: approve/reject
  <- Event Stream: artifact produced
  <- Event Stream: receipt ready
```

## 5. Cloud Wallet Optional Flow

This is not part of the open-source kernel.

```text
User
  -> AgentOS Cloud: Apple Pay top-up
  -> Stripe: payment
  -> Billing Service: webhook confirms payment
  -> Cloud Resource Manager: enable managed credits
  -> Campaign Kernel: uses Resource Manager interface
```
