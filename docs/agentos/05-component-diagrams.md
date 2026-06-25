# Component Diagrams

Core components: Campaign API, Planner, Capability Registry, Capability Router, Budget Engine, Resource Manager, Credential Plane, Evaluator, Repair Loop, Artifact Store, Receipt Store, Event Bus, Hermes Adapter, MCP Server, and LangGraph Runtime Adapter.

## Boundary rules

- Strengthen architectural boundaries before adding functionality.
- Keep the core flow: Goal -> Campaign Kernel -> Capability -> Implementation -> Evaluation -> Artifact.
- Providers are interchangeable device drivers behind implementations.
- LangGraph is runtime/checkpoints/streaming only; it is not the system of record.
- Hermes, dashboards, SDKs, and MCP clients are clients, not databases.

## Phase 0 implications

- Define contracts and evaluators before expanding execution features.
- Emit measurable artifacts and immutable receipts for every material decision.
- Prefer relational state; use vectors only for semantic retrieval needs.
- Track Expected User Value per Dollar and Cost of Quality where routing or repair decisions are made.
