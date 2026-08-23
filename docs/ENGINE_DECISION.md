# Engine Decision

**Status:** Selected for prototype — Unity
**Selected version:** Unity 6000.4.3f1
**Decision owner:** Cameron
**Recorded:** 2026-08-23
**Confidence:** 72%

## Decision

Use Unity, C#, the Built-in Render Pipeline, and Unity's 3D physics for the
proof-of-fun and networked-physics spikes.

Primary reason: the working repository now demonstrates repeatable scene
assembly, Blender FBX import, deterministic EditMode tests, Windows builds, and
a physical rigidbody production-room prototype in the selected engine.

Supporting evidence:

- Unity 6000.4.3f1 imports and runs the complete playable route inside the
  fourteen-zone facility: Gullet mine, physical cart haulage, six-stage
  refinery, fuel corridor, reactor startup, grid delivery and recovery.
- Batch-mode compilation, tests, scene generation, screenshot capture and
  Windows builds are automated from the command line.
- The project already has external Unity MCP integration and a validated
  Blender-to-FBX-to-Unity asset path.

Known disadvantages:

- Serialized scene and package changes require disciplined validation.
- Networked held objects and ragdolls remain the highest technical risk.
- Steam networking and voice will introduce dependency and debugging cost.

This decision is intentionally provisional at the production gate. It must be
reopened if the required two-client contention, disconnect cleanup, cart
knockdown and body-dragging spike cannot remain stable during a 20-minute soak,
or if Steam/proximity-voice integration proves materially less viable than the
Godot alternative.

## Current technical stack

- Engine: Unity 6000.4.3f1
- Language: C#
- Renderer: Built-in Render Pipeline, low graphics defaults, no ray tracing
- Physics: Unity 3D physics
- Networking: not installed; next gate is host-authoritative selection/spike
- Steam: not selected
- Voice: not selected
- MCP: vendored `com.coplaydev.unity-mcp`
- Tests: Unity Test Framework EditMode tests
- CI/build: local batch-mode validation today; CI multiplayer smoke is pending
- Repository: engine assets under `Assets/`, packages under `Packages/`, project
  settings under `ProjectSettings/`, source art under `art/`

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
