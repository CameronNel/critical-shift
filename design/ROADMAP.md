# Roadmap

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


This roadmap is stage-gated. Later work begins only when the previous gate is demonstrated in a playable build.

## Gate 0: Engine and Agent Tooling

- Select engine through `design/ENGINE_DECISION.md`
- Install and validate external MCP
- Add engine-specific ignore rules
- Establish local build and test command
- Add CI smoke validation

**Exit evidence:** An agent can make a bounded scene change, run the project, read errors, and produce a validated commit.

## Gate 1: Networked Physics Room

- Two to four clients
- Character movement
- Grab and release
- Object contention
- Cart collision
- Ragdoll and recovery
- Body dragging
- Disconnect ownership cleanup

**Exit evidence:** A 20-minute multiplayer soak test without permanent desynchronisation.

## Gate 2: Radioactive Shoebox

- Ore
- Conveyor
- Crusher
- Fuel
- Reactor
- Cooling valve
- Rising demand
- One shortcut
- One delayed consequence
- Restart

**Exit evidence:** Friends naturally communicate, blame, laugh, or panic during the loop.

## Gate 3: Social Pressure

- One disguised infiltrator
- One legitimate suspicious worker
- One compliance officer
- Evidence and hiding
- Nonlethal bonking
- Audit escalation

**Exit evidence:** Players do not automatically attack every visitor, and the audit produces choices rather than pure annoyance.

## Gate 4: Complete Shift

- Briefing
- Preparation
- Safe production
- Shortcut temptation
- Scrutiny
- Cascading failures
- Reanimation
- Shutdown or meltdown
- Causal debrief

**Exit evidence:** One complete 20 to 35 minute round that resets cleanly.

## Gate 5: Vertical Slice

- Small mine
- Three refinery machines
- Reactor hall
- Three-shift operation
- Tutorial
- Steam connectivity proof
- Proximity voice proof
- Basic progression

**Exit evidence:** Private external testers request another session.

## Gate 6: Alpha

- Additional incidents
- Operations
- Saves
- Menus
- Controller support
- Accessibility foundation
- Automated multiplayer tests
- Crash reporting

## Gate 7: Early Access

- Content expansion
- Performance work
- Public-facing onboarding
- Store assets
- Trailer capture
- External playtesting
- Release automation

## Scope Rule

No stage may be accelerated by adding content before its core risk has passed. More rooms, tools, machines, enemies, or cosmetics cannot compensate for unstable carrying, weak causality, or a boring production loop.


---

## Autonomous section production gate

Before any room can advance from scenery planning into production:

- scenery specification exists;
- room-specific prompt exists;
- production/TASK_STATE.md exists;
- production/RUBRIC.md exists;
- production/CAMERAS.md exists;
- production/CHECKLIST.md exists;
- headless Blender entrypoint is planned;
- the room adopts [AUTONOMOUS_SECTION_BUILD_PROTOCOL.md](AUTONOMOUS_SECTION_BUILD_PROTOCOL.md).

Before any room can be called complete:
- at least four full correction cycles;
- >=90/100 overall;
- >=85% of points in every rubric category;
- zero critical failures;
- final two cycles materially stable;
- cold-start Blender validation PASS.


## Mandatory art-direction reset stage

Before further room-scale environment production:

1. Build a small Spawn Room validation slice.
2. Judge it from fixed gameplay cameras.
3. Pass the hard vetoes in `ART_DIRECTION.md`.
4. Approve geometry, proportions, materials, wear, colour, lighting and prop density.
5. Turn that slice into the canonical facility kit.
6. Only then expand the Spawn Room or apply the language to the Reactor Room.

No roadmap milestone may treat the current generic low-poly visual pass as reusable finished art merely because it already exists.
