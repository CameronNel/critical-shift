# Critical Shift Agent Entry Rules

## Start here

Respect the current task's scope. A planning-only task changes documentation, not runtime/test code, Unity projects, packages, workflows, scenes/assets or repository settings. Proposed file paths and test names in a plan are not permission to implement them.

The repository's [GAME_SPEC](design/GAME_SPEC.md), section 32.6, requires **one task branch, one primary author, no direct main edits and no agent merging its own work**. Submit bounded changes for independent review. Do not claim that written policy means branch protection is already configured.

## Runtime, Unity, C#, packages and architecture

Read [the code-architecture entrypoint](design/code-architecture/README.md) and [agent checklist](design/code-architecture/AGENT_CHECKLIST.md) before work. On first entry, read the complete linked plan. On subsequent tasks, reread the affected contracts, validation cases, open decisions and actual gate state.

For the actual offline implementation, also read [runtime/README.md](runtime/README.md). It identifies the single consolidated integration route, canonical source, review repairs and retained historical PR heads. Inspect the live PR/ref state; do not reconstruct or separately merge an earlier partial implementation while ignoring its later fixes. This navigation rule does not change the independent-review or merge policy.

The canonical planning section is `design/code-architecture/`:

- [Architecture](design/code-architecture/ARCHITECTURE_PLAN.md): dependency allowlist, feature boundaries and composition.
- [State and contracts](design/code-architecture/STATE_AND_CONTRACTS.md): mutation owners, host intentions, claims, transactions and lifecycle.
- [Code health](design/code-architecture/CODE_HEALTH_PLAN.md): removal, serialization, diagnostics and review.
- [Validation](design/code-architecture/VALIDATION_PLAN.md): test IDs, failure conditions, fixtures and evidence.
- [Delivery](design/code-architecture/DELIVERY_PLAN.md): minimum implementation sequence and roadmap gates.
- [Decisions and risks](design/code-architecture/DECISIONS_AND_RISKS.md): proposed ADRs, open choices, risks and sources.

Also read [ENGINE_DECISION](design/ENGINE_DECISION.md), the relevant gameplay specification and current repository state. Historical prototype evidence is not proof of a currently runnable Unity project. Do not silently select networking, Steam, voice, input/UI or persistence infrastructure. A package trial needs an explicit bounded decision before installation.

## Environment and Blender section work

Read the global art/build authority under `design/` and the relevant section-local `AGENT_READ_FIRST.md`, scenery specification and production state. For runtime exports, also read the architecture plan's authoring-to-runtime boundary. Original visual source, licensed materials and art-review evidence are not dead runtime assets to be removed by an unused-code sweep.

## Change and handoff rules

Search for the existing implementation and consumers before adding a replacement. Establish one mutation owner, explicit lifetime and allowed dependencies. Migrate consumers and remove obsolete active paths; inspect serialized/dynamic references before deleting Unity code or assets.

Report what changed, what deliberately did not, what actually ran, what was not run or blocked, and the independent review/merge status. Missing tests, unavailable Unity and unmeasured performance must not be presented as passes. Keep these entry links current; do not create another competing hidden architecture guide.
