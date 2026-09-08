# Critical Shift Agent Entry Rules

This repository contains authoritative design, art and future runtime implementation rules. Do not treat it as an unstructured asset dump.

## Runtime / Unity / C# work

Before creating, changing or refactoring runtime code, read:

1. `design/ENGINE_DECISION.md`
2. `design/code-architecture/README.md`
3. `design/code-architecture/ARCHITECTURE_PLAN.md`
4. `design/code-architecture/CODE_HEALTH_PLAN.md`
5. `design/code-architecture/AGENT_CHECKLIST.md`

The code-architecture section is mandatory. Its purpose is to prevent duplicate systems, dead code, global-state sprawl and dependency spaghetti as implementation grows.

Do not select undecided networking, Steam, voice or other major runtime infrastructure silently. Record the technical decision first.

## Environment / Blender section work

Read the global art/build authority under `design/` and the relevant section-local `AGENT_READ_FIRST.md` / production state before editing a physical game section.

## General rule

Search for the authoritative existing implementation/specification before adding a replacement. If a change supersedes something, migrate and remove the obsolete path rather than leaving parallel versions in the active tree.
