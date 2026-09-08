# Critical Shift Code Architecture & Code Health

> [!IMPORTANT]
> **Mandatory reading before creating or materially changing Unity/C# implementation.**
>
> This section defines the planned architecture, dependency boundaries, code-health rules, test strategy and cleanup gates for the future Critical Shift runtime. It exists specifically to prevent spaghetti architecture, duplicate systems and dead code from accumulating as implementation scales.

**Status:** Planning only. No Unity implementation is created by these documents.

**Engine context:** Unity 6000.4.3f1, C#, Built-in Render Pipeline, Unity 3D physics. Networking/Steam/voice remain intentionally unselected until their technical gates are passed.

## Read order

1. [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) — ownership, dependency direction, feature structure and Unity boundary.
2. [CODE_HEALTH_PLAN.md](CODE_HEALTH_PLAN.md) — dead-code policy, analysis, test gates, review rules and cleanup milestones.
3. [AGENT_CHECKLIST.md](AGENT_CHECKLIST.md) — short mandatory checklist for any agent adding or refactoring runtime code.

## Non-negotiable intent

Critical Shift should remain understandable after years of feature growth. The design therefore treats architecture and code hygiene as build constraints, not optional cleanup work.

The future implementation must aim for:

- one authoritative representation of each game state;
- explicit dependency direction enforced by assembly boundaries;
- game rules that are testable without loading a Unity scene wherever practical;
- thin Unity/physics/presentation adapters around deterministic game logic;
- feature ownership instead of a generic `Scripts/Managers/Utils` dumping ground;
- no giant global `GameManager`;
- no silent circular dependencies;
- no abandoned replacement implementations left beside the active one;
- no dead code, commented-out legacy implementations or orphaned assets accepted as normal repository state;
- automated compile, analysis, test and architecture gates before changes are accepted;
- explicit deletion and simplification passes during refactors and milestone reviews.

## Authority

For runtime implementation architecture, these documents complement:

- `design/GAME_SPEC.md` for gameplay requirements;
- `design/ENGINE_DECISION.md` for engine and technical-stack decisions;
- `design/ROADMAP.md` for production sequencing.

If a future implementation choice needs to violate a rule here, the exception must be deliberate, documented with the reason and scope, and accompanied by a plan to remove or formalize the exception. Convenience alone is not an architectural reason.

## Planning boundary

These files do **not** select the networking framework, Steam integration, voice stack, input implementation or final UI framework. Those dependencies must remain behind interfaces until their relevant technical decisions are recorded.
