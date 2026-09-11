# Electrical Room requirements — takeover D

Authority read first: BUILD_BRIEF.md; briefs/electrical-room.md; complete GAME_SPEC.md (especially5,11.3,12,18,19,23-25,28-31); ART_DIRECTION.md, ART_REFERENCE_INDEX.md and production protocol from reactor-valorant/design. Latest user instructions override teal palette, Astra reviewers, slice-only expansion and arbitrary repeated polishing. This is original Blender local scenery and integration metadata, not engine simulation.

## Required functions and equipment

| Explicit requirement | Planned authored representation | Runtime boundary |
|---|---|---|
| Trace turbine input to distribution | Incoming isolator, metering, main bus, distinct feeder sequence and supported duct junctions | Host-owned electrical flow/output |
| Breakers and selective power reduction | Main, cooling, production and facility feeder operating handles, clear status | Load shedding, trips and blackout |
| Backup/transfer distribution | Physical manual transfer and priority selector | Restore backup; choose cooling or OCRU |
| Shared reserve | Reserve cabinets, charge indication, disconnect, portable power connection | Shared turbine reserve pool; no duplicate gameplay battery pool |
| Repair/manual recovery | Withdrawn isolated breaker, fuse service, equipped workbench | Damage, repair-while-live risk and inventory |
| Demand and machine health | Grouped clear analog/state indication | Dynamic load, warnings and maintenance state |
| Turbine to Electrical to Waste route | Two level2.4x2.7m portals and uninterrupted2.4m aisle | Reciprocal whole-map travel and carrier sweeps |
| Modular incident/audio/navigation hooks | Named empties, spatial boundaries and actions | Engine collision/navmesh, audio, networking and runtime validation |

## Design choices

Retain main11x16.4x4.8m hall and2.8x4.4x3.6m east reserve bay. Entry(0,0,0),+Y inward,+Z up. West switchgear envelope x-5.1..-3.55,y3.2..10.9;2.35m operating apron. Guarded dry transformer x3.05..5.3,y4.7..8.1;1.85m apron. Transfer x4.35..5.3,y9.45..11.15; clear of reserve approach y12..14.4. Reserve cabinets x7.35..8.15,y11.7..14.7;1.6m apron. Rear-west repair bench x-5.25..-3.55,y12.6..15.2. No stair or mezzanine. Backup generator is an external essential-supply interface; local reserve/transfer hardware is built. No fictional voltage, current, capacity or certified safety rating inferred from shape.

Original S05 turquoise/teal palette rejected. New cream, charcoal, oxide orange and restrained safety yellow/red palette; specific folded/cast geometry; no photorealistic grunge, plastic gloss, borrowed branding or meaningless machinery. Concepts guide visual decisions but cannot change dimensions or required functions.

## Boundaries

Turbine R07 saved geometry is measured read-only. Waste remains a partial saved section; its existing receiving doorway is measured without edits. Proposed transforms and exact mating faces belong in CONNECTIONS.md. No scene imports or neighbour modifications. Engine state, audio, incidents, player physics and whole-map assembly remain explicit handoff work.

