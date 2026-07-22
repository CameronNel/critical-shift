# Engine Decision

**Status:** Open  
**Candidates:** Unity and Godot  
**Decision owner:** Cameron  
**Decision method:** Evidence from a focused implementation spike, not engine preference

## Required Spike

Build the smallest equivalent test needed to resolve the technical risk:

- Two locally running clients
- Responsive stylised adult human controller
- Host-authoritative crate grabbing
- Two-player object contention
- Mine-cart impact causing recoverable ragdoll
- Body dragging
- Conveyor movement
- Physical lever controlling a replicated machine state
- Disconnect while holding an object
- Automated smoke test
- Runtime error capture
- Screenshot capture through external AI tooling

## Evaluation Criteria

Score each engine on:

1. Networked physics stability
2. Ragdoll setup and recovery
3. Multiplayer debugging
4. Steam path
5. Proximity voice path
6. External MCP capability
7. AI-safe scene editing
8. Automated testing
9. Iteration speed
10. Beginner maintainability
11. Package and dependency risk
12. Probability of reaching Early Access

## Decision Record

When a decision is made, record:

- Selected engine and version
- Language
- Renderer
- Physics system
- Networking framework
- Steam integration
- Voice solution
- External MCP
- Test framework
- Confidence percentage
- Evidence from the spike
- Known disadvantages
- Conditions that would reopen the decision

No production content should be built before this decision is recorded.
