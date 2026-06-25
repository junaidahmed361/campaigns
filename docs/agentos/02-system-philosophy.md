# System Philosophy

AgentOS is an operating system for campaigns, not an agent framework. The stable flow is Goal -> Campaign Kernel -> Capability -> Implementation -> Evaluation -> Artifact. Agents are implementation details behind capabilities.

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
