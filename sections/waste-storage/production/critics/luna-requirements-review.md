# Luna requirements and integration review

Status: bounded pre-concept extraction only. No visual score or approval is issued because no new concept or rendered review set was supplied.

Reviewer: Luna. Scope: Waste Storage only. The user override is authoritative: strict Valorant-influenced grounded stylized semi-realism, no teal, complete-room early integration readiness, independent Luna review, auto-approve only when every relevant category is actually qualifying, and no endless polishing of minor details.

## Explicit requirements

### Function and gameplay

- Build the canonical Waste Storage section from the Waste Storage brief and GAME_SPEC waste handling, radiation, transport, and compliance gameplay.
- Show a receiving threshold; segregated storage cells; original casks/containers; cart transfer and turning space; controlled access; monitoring; ventilation; maintenance; and safe readable movement.
- The room is a maintained working facility. Use selective use/wear and functional storytelling; do not fill it with random barrels or abandoned-bunker grunge.
- Waste is a networked gameplay object. The environment must make inventory, transfer, temporary storage, concealment, contamination, compliance inspection, and dispatch legible without asserting runtime simulation in Blender.
- Preserve adult worker scale and believable handles, access depth, door operation, cart handling, two-person carrying, and maintenance posture.

### Spatial contract (local metres)

- Local origin is the main receiving doorway threshold centre `(0,0,0)`; `+Y` goes inward and `+Z` is up. Planned envelope is `[-6,0,0]` to `[6,18,4.8]`; nominal wall thickness is `0.25 m`.
- `WS_RECEIVING`: centre `(0,0,0)`, outward normal `-Y`, clear `3.0 x 3.2 m`, overhead sectional door parked open; accommodates waste carts, two-person carry, workers, and inspection.
- `WS_PERSONNEL`: centre `(6,2.4,0)`, outward normal `+X`, clear `1.2 x 2.3 m`, outward egress swing reserved outside the module; intended future clean medical/reanimation connection.
- `WS_DISPATCH`: centre `(0,18,0)`, outward normal `+Y`, clear `2.4 x 2.8 m`, overhead sectional door parked open; sealed cart and inspection route.
- `WS_MONITOR_BOOTH`: internal aperture centre `(-2.4,2.2,0)`, normal `+X`, clear `1.1 x 2.3 m`, inward glazed leaf held at 90 degrees open. Its parked leaf and sweep reservation are inside the booth at the north end of the aperture.
- Planned zones: receiving `[-6,0]..[6,4.5]`; monitoring `[-5.7,.4]..[-2.4,3.8]`; west front sealed process-residue overpacks; west rear shielded hot-waste cask storage; east front dry contaminated tools/filters/consumables; east rear quarantine/inventory hold; rear service `y=14.5..18` for ventilation isolation, filter maintenance, and dispatch.
- Keep the central cart route `x=-1.8..1.8`, `y=4.5..14.5`, minimum clear height `2.4 m`. Cart envelope is `1.0 x 1.8 x 1.8 m`; receiving turn circle is diameter `3.6 m` centred `(0,2.5)`; rear turn circle is diameter `3.0 m` centred `(0,16)`.
- Preserve `1.0 m` walking width, `1.8 m` two-person carry route width, `1.4 m` storage-cell access, and `0.9 m` maintenance working depth. Do not use shelves, casks, containers, door leaves, pipes, or dressing to consume these clearances.
- Utility contracts: `WS_POWER` at `(5.75,17.75,3.6)` (facility low-voltage feed); `WS_EXTRACT` at `(-4.8,18,4.0)` (controlled extract boundary); `WS_DATA` at `(-5.75,.25,2.8)` (inventory/exposure/door-state telemetry).

### Visual direction

- Use grounded stylized semi-realism: believable construction and human scale, simplified but specific forms, broad value/colour grouping, restrained surface noise, selective wear, tactile painted metal/concrete/rubber/glass/fabric/plastic, and practical lighting hierarchy.
- Valorant is a principle reference only: readable silhouettes, controlled materials, purposeful architecture, and strong colour blocking. Do not copy assets, symbols, layouts, branding, or distinctive designs.
- The user explicitly vetoes teal. Avoid teal/cyan as a dominant or accent family, including inherited/reference language that names cyan as a hero landmark. Keep any status colour choice warm or otherwise clearly outside teal.
- Shape must carry the read before labels and textures. Avoid universal cube-plus-bevel construction, uniform satin/gloss, noisy procedural grunge, toy PPE, random greebles, excessive screens/signage, flat even lighting, or AAA photoreal texture noise.
- The room should communicate material separation and use: painted steel, structural/bare metal, concrete, rubber seals/wheels, glass instruments, paper/labels, and controlled emissive indicators should each have distinct visible responses.
- A style-validation slice is required before broad expansion: believable wall transition, door, primary prop cluster, practical light, utility element, and 3–5 human-use props from gameplay camera height.

## Integration pitfalls and required cautions

1. **Legacy scene is incomplete.** The old saved artifact is a 12 x 4.6 m receiving/style slice (r03) with four review cameras. It is not the 12 x 18 m room, has no full-room ten-camera evidence, no cold-start acceptance, and no full route/count/connectivity validation. The paused partial r04 source was unbuilt and unrendered. Do not present inherited slice evidence as full-room acceptance.

2. **Measured receiving wall overrides paper thickness.** The old JSON says `0.25 m`, but the saved receiving walls measure `0.32 m` thick, with inner X faces `-1.5/+1.5`, wall Y bounds about `-.32..0`, and lintel underside `z=3.2`. The receiving aperture is therefore physically `3.0 x 3.2 m`. The receiving threshold has a measured `2 mm` lip at `z≈.002`; retain and document this neighbour condition for engine traversal rather than silently changing the completed neighbour.

3. **Electrical-to-Waste seam is a measured proposal, not a whole-map approval.** Electrical `CONNECTIONS.md` proposes Waste origin `(0,16.97,0)` in Electrical coordinates, with Electrical north exterior `y=16.65` meeting Waste exterior `y=16.65`. Electrical D02 remains a `2.4 x 2.7 m` opening while Waste WS_RECEIVING is `3.0 x 3.2 m`; the seam widens across the adjoining wall thickness. Electrical owns its level seam slab from `y=16.4..16.97`. Do not move or remodel Electrical, add a scenic connector, or claim reciprocal facility assembly.

4. **Do not falsely mate power interfaces.** Electrical U02 at `(-4.32,16.65,3.88)` is an unbound outgoing distribution bus. It is explicitly separate from Waste `WS_POWER` at the far north-east. Waste must expose its own interface and leave the electrical distribution relationship to the integrator; no fabricated cable, rating, or neighbour transform should be treated as verified.

5. **Door and sweep failures are easy to hide.** Receiving and dispatch overhead leaves must be parked clear of routes. Personnel egress swings outward beyond the module. The monitor leaf must be visibly parked at 90 degrees inside the booth and its sweep must not intersect equipment, route, or the booth corner. Validate evaluated geometry, not marker names.

6. **Central route is the gameplay spine.** Storage cells can look plausible while blocking carts or two-person carry. Review both empty and dressed states for the stated cart envelope, turn circles, clear height, cell access, and maintenance depth. A flattering hero camera cannot substitute for route evidence.

7. **Contamination and compliance need visible affordances.** GAME_SPEC allows contamination through waste, carts, tools, carried objects, bodies, and unsealed suits; Compliance scans waste, inventory, logs, and selected access points, and can punish unauthorised or misplaced waste. If the rendered room has no readable monitoring/segregation/inspection logic, storytelling and gameplay readability are deficient even if props exist.

8. **Technical support contacts are mandatory.** Wall, floor, ceiling, cask, cart, pipe, sign, and fixture supports require registered anchors, target surfaces, direction, gap/penetration tolerance, and evaluated-geometry checks. The old slice had anchor-registration failures on panel tie plugs/floor wear and a lid pivot outside its lid bounds; these are regression warnings, not cosmetic details.

9. **Integration readiness has a strict boundary.** Blender can prove authored geometry, named interfaces, portals, cameras, materials, and reproducible source. Unity/runtime owns collision, navmesh, interactions, networking, audio, incident state, dose/contamination simulation, and whole-facility travel. Report these as pending handoff items rather than claiming runtime PASS.

10. **Review evidence must be pixel-grounded.** Freeze valid cameras before formal comparison and cover entry, hero, reverse, route, pinch/cramped areas, machinery/casks, monitoring, ventilation/maintenance, receiving/dispatch, and materials. Score scale/circulation, shape/art direction, hierarchy, materials, lighting, colour, environmental storytelling, and visible technical correctness independently out of 100. Reject the concept if any relevant category is below 90 or if a critical failure is visible; never issue an approval without the actual rendered pixels.

## Sources read

- `ops/facility-run/BUILD_BRIEF.md`
- `ops/facility-run/briefs/waste-storage.md`
- `design/GAME_SPEC.md`
- `design/ART_DIRECTION.md`
- `design/ART_REFERENCE_INDEX.md`
- `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`
- `design/CANON.md`, `design/ENGINE_DECISION.md`, `design/ROADMAP.md`
- legacy `sections/waste-storage/interface.json` and saved receiving survey
- current Electrical `sections/electrical-room/interface.json` and `architecture/CONNECTIONS.md`

