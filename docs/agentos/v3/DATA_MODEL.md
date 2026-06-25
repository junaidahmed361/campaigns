# Data Model

## 1. Core Entities

- Campaign
- Objective
- WorkUnit
- Capability
- CapabilityImplementation
- ExecutionPolicy
- ResourceReservation
- ResourceLedgerEntry
- CredentialHandle
- ProviderDriver
- RuntimeDriver
- Artifact
- Evaluation
- Receipt
- Event
- Approval

## 2. Campaign

```sql
campaigns (
  id UUID PRIMARY KEY,
  goal TEXT NOT NULL,
  status TEXT NOT NULL,
  execution_policy_id UUID NOT NULL,
  deadline TIMESTAMP NULL,
  sla JSONB NOT NULL,
  constraints JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

## 3. Work Units

```sql
work_units (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  capability TEXT NOT NULL,
  status TEXT NOT NULL,
  inputs JSONB NOT NULL,
  expected_outputs JSONB NOT NULL,
  dependencies JSONB NOT NULL,
  max_repair_iterations INT DEFAULT 2,
  repair_iteration INT DEFAULT 0,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

## 4. Execution Policies

```sql
execution_policies (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  monthly_api_spend_limit_usd NUMERIC NULL,
  per_campaign_limit_usd NUMERIC NULL,
  per_work_unit_limit_usd NUMERIC NULL,
  prefer_subscription_providers BOOLEAN DEFAULT true,
  prefer_local BOOLEAN DEFAULT false,
  require_approval_above_usd NUMERIC NULL,
  policy JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

## 5. Resource Reservations

```sql
resource_reservations (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  work_unit_id UUID NULL,
  capability TEXT NOT NULL,
  implementation_id UUID NULL,
  resource_type TEXT NOT NULL,
  reserved_amount NUMERIC NOT NULL,
  actual_amount NUMERIC NULL,
  unit TEXT NOT NULL,
  status TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL,
  UNIQUE(idempotency_key)
);
```

Resource types:

- usd
- tokens
- subscription_quota
- gpu_seconds
- wall_clock_seconds
- repair_iterations
- human_approval

## 6. Resource Ledger

```sql
resource_ledger_entries (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  work_unit_id UUID NULL,
  reservation_id UUID NULL,
  resource_type TEXT NOT NULL,
  delta NUMERIC NOT NULL,
  unit TEXT NOT NULL,
  reason TEXT NOT NULL,
  metadata JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

The ledger is append-only.

## 7. Capability Implementations

```sql
capability_implementations (
  id UUID PRIMARY KEY,
  capability TEXT NOT NULL,
  driver_name TEXT NOT NULL,
  runtime_name TEXT NULL,
  pricing_model TEXT NOT NULL,
  marginal_cost_usd NUMERIC NULL,
  supports_local BOOLEAN DEFAULT false,
  supports_streaming BOOLEAN DEFAULT false,
  supports_cancellation BOOLEAN DEFAULT false,
  quality_score NUMERIC NULL,
  latency_score NUMERIC NULL,
  reliability_score NUMERIC NULL,
  metadata JSONB NOT NULL
);
```

Pricing models:

- subscription
- token_api
- local
- managed_cloud
- external_orchestrator

## 8. Credentials

```sql
credential_handles (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  provider_name TEXT NOT NULL,
  handle_uri TEXT NOT NULL,
  credential_type TEXT NOT NULL,
  storage_backend TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

Never store raw credentials in normal tables.

## 9. Evaluations

```sql
evaluations (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  work_unit_id UUID NOT NULL,
  artifact_id UUID NULL,
  evaluator_name TEXT NOT NULL,
  score NUMERIC NULL,
  status TEXT NOT NULL,
  findings JSONB NOT NULL,
  recommended_action TEXT NULL,
  created_at TIMESTAMP NOT NULL
);
```

## 10. Artifacts

```sql
artifacts (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  work_unit_id UUID NULL,
  artifact_type TEXT NOT NULL,
  uri TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  metadata JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

## 11. Receipts

```sql
receipts (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  version INT NOT NULL,
  content JSONB NOT NULL,
  content_hash TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  UNIQUE(campaign_id, version)
);
```

Receipts are immutable. New changes create new receipt versions.

## 12. Events / Outbox

```sql
events (
  id UUID PRIMARY KEY,
  aggregate_type TEXT NOT NULL,
  aggregate_id UUID NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  idempotency_key TEXT NULL,
  created_at TIMESTAMP NOT NULL,
  published_at TIMESTAMP NULL
);
```
