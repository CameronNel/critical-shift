# Gullet Mine — Task State

**Read first:** `../AGENT_READ_FIRST.md`  
**Current phase:** Blender execution + fixed-camera visual review  
**Section source status:** committed / deterministic  
**Visual acceptance:** **NOT YET EARNED**

## Completed

- Section-specific scenery specification authored.
- Deterministic Blender builder source committed under `../blender/gullet/`.
- Deterministic geology/material/signage generator committed.
- Covered preparation/dispatch bay, facility connection and blast gate authored.
- 2.5% downhill adit with rail haulage, pedestrian route and return/service loop authored.
- Dry, wet and deep sectors authored with progressive state alternatives.
- Collapse variants and individually removable rubble authored.
- Pump, sump, ventilation, cable, drainage, supports, workstations, carts and tools authored.
- Ten fixed review cameras defined.
- Non-Blender geometry/state audits passed in the original generation environment.

## Required next actions

1. Run `python tools/prepare_assets.py` from `../blender/gullet/`.
2. Run the Blender builder from a fresh Blender process.
3. Render all ten fixed cameras with the same settings.
4. Inspect actual pixels against `design/ART_DIRECTION.md` and this section spec.
5. Record visible defects, fix the deterministic source, rerender and compare.
6. Perform at least four full correction cycles after first visual completion as required by the global protocol.
7. Run `tools/cold_start_check.py` from a fresh Blender process reopening the saved `.blend`.
8. Only after those gates, begin/complete Unity import and runtime validation.

## Known limitations / risks

- The initial authoring session did not have Blender installed, therefore it did not produce trustworthy Blender render evidence.
- Unity physics, multiplayer authority, navigation, pickups, cart handling, rubble interaction, audio and VFX are not implemented by this Blender package.
- Procedural Blender water/scuff material response may require a separate Unity material implementation.
- GPU selection should be measured on the supplied RX 9070 XT rather than assumed.

## Last known non-Blender checks

- geometry/state audit: PASS in generation environment;
- state-control assertions: PASS in generation environment;
- actual Blender build: pending;
- fixed-camera Blender render review: pending;
- cold-start Blender validation: pending;
- Unity runtime validation: pending.

## Hardware target supplied by Cameron

- AMD Radeon RX 9070 XT
- AMD Ryzen 7 5800X
- 32 GB DDR4
