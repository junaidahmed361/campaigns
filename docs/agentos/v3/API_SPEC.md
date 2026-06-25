# API Specification

## 1. Principles

The API exposes goals, campaigns, execution policies, resources, capabilities, artifacts, evaluations, and receipts.

It should not expose provider selection as a first-class user concern.

All mutating requests require an Idempotency-Key.

## 2. Campaigns

### POST /campaigns

Create a new campaign.

```json
{
  "goal": "Build OAuth support for my app",
  "execution_policy_id": "default-local-byok",
  "deadline": "2026-07-01T18:00:00-07:00",
  "sla": {
    "quality": "enterprise",
    "max_latency_seconds": 3600,
    "min_test_coverage": 0.9
  },
  "constraints": {
    "prefer_local": true,
    "allow_paid_api": true,
    "max_campaign_spend_usd": 10,
    "require_human_approval": true
  }
}
```

### GET /campaigns/{id}

Returns campaign state.

### GET /campaigns/{id}/timeline

Returns event timeline.

### POST /campaigns/{id}/pause

Pause campaign.

### POST /campaigns/{id}/resume

Resume campaign.

### POST /campaigns/{id}/cancel

Cancel campaign.

## 3. Work Units

### GET /campaigns/{id}/work-units

List work units.

### GET /work-units/{id}

Read work unit details.

### POST /work-units/{id}/retry

Retry failed work unit with idempotency key.

## 4. Approvals

### GET /approvals

List pending approvals.

### POST /approvals/{id}/approve

Approve execution, repair, provider fallback, or higher resource usage.

### POST /approvals/{id}/reject

Reject approval.

## 5. Capabilities

### GET /capabilities

List registered capabilities.

### GET /capabilities/{name}

Read capability contract.

### POST /capabilities/register

Register capability or implementation.

## 6. Execution Policies and Resource Manager

### GET /execution-policies

List policies.

### POST /execution-policies

Create policy.

```json
{
  "name": "local-byok-default",
  "monthly_api_spend_limit_usd": 150,
  "per_campaign_limit_usd": 10,
  "per_work_unit_limit_usd": 1,
  "prefer_subscription_providers": true,
  "prefer_local": true,
  "provider_rules": {
    "claude_code": {"enabled": true, "pricing_model": "subscription"},
    "codex": {"enabled": true, "pricing_model": "subscription"},
    "openai_api": {"enabled": true, "monthly_limit_usd": 50},
    "ollama": {"enabled": true, "pricing_model": "local"}
  }
}
```

### GET /resources/usage

Returns current usage across providers and policies.

### GET /resources/reservations

Returns active reservations.

### POST /resources/reservations

Internal-only API for reserving resources before execution.

## 7. Credentials

### GET /credentials

List credential handles, never raw secrets.

### POST /credentials

Create a provider credential handle.

### DELETE /credentials/{id}

Remove credential.

## 8. Benchmarks

### GET /benchmarks/capabilities

Read benchmark radar.

### POST /benchmarks/local-result

Record local evaluator outcome.

## 9. Artifacts

### GET /campaigns/{id}/artifacts

List artifacts.

### GET /artifacts/{id}

Read artifact metadata or signed download URL.

## 10. Evaluations

### GET /work-units/{id}/evaluations

List evaluations.

### POST /evaluations/run

Run evaluator on artifact or work unit.

## 11. Receipts

### GET /campaigns/{id}/receipt

Read immutable campaign receipt.

### GET /receipts/{id}

Read receipt version.

## 12. Event Stream

### GET /events/stream

SSE/WebSocket stream.

Events include:

- campaign.created
- campaign.planned
- work_unit.created
- resource.reserved
- implementation.selected
- work_unit.started
- work_unit.completed
- evaluation.completed
- repair.started
- artifact.created
- approval.requested
- campaign.completed
