# Roadmap

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
