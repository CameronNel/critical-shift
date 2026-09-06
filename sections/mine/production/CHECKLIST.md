# Gullet Mine — Production Checklist

## Source and structure

- [x] Section lives under `sections/mine/`.
- [x] Agent entrypoint exists: `AGENT_READ_FIRST.md`.
- [x] Authoritative scenery specification exists.
- [x] Deterministic Blender source is versioned.
- [x] Asset generation is deterministic and offline.
- [x] Fixed review cameras are defined.
- [x] Unity/runtime boundary is documented.

## Geometry / gameplay-readability targets

- [x] Shallow downhill mine, no elevator.
- [x] Facility-side staging/dispatch bay.
- [x] Blast gate and operator station.
- [x] Cart rail route and pedestrian path.
- [x] Multiple independent mineable sectors.
- [x] Progressive shallow / extended / deep states.
- [x] Collapse state with separately removable rubble.
- [x] Wet sector with pump and sump.
- [x] Supports, ventilation, cables and drainage.
- [x] Tools, cart, instructions and charge-issue staging.

## Validation still required

- [ ] Generate repo-local assets from a clean checkout.
- [ ] Run full Blender build successfully.
- [ ] Render all ten fixed cameras.
- [ ] Inspect the pixels against art direction.
- [ ] Record first scored rubric.
- [ ] Complete at least four visual correction cycles.
- [ ] Recheck all state variants after visual changes.
- [ ] Run fresh-process cold-start reopen and render.
- [ ] Confirm no missing packed textures/images.
- [ ] Export state variants and collision package.
- [ ] Import to Unity and validate scale/material separation.
- [ ] Implement/test cart physics and collision.
- [ ] Implement/test pickup/state/rubble interactions.
- [ ] Validate multiplayer/network authority.
- [ ] Validate navigation, VFX and audio.

Do not mark this section complete simply because Blender saves a file. Humanity has tried that sort of optimism before; the protocol exists for a reason.
