# Independent Luna component review — M04 OCRU assembly

Reviewer: Luna (independent)

Asset reviewed: `art/concepts/M04-ocru-component.png`

Comparators: inherited R09 OCRU envelope and saved room views in `production/renders/existing-R09/CAM_HERO.png`, `CAM_ENTRY.png`, and `CAM_REVERSE.png`.

The inherited assembly contract is 4.30 m length along the wall, 2.50 m depth into the room, with the berth long axis along the wall. The existing R09 room placement remains authoritative. M04 is reviewed as a component assembly study; it cannot change the room footprint, world orientation, or interface contract.

## Independent depicted-component scores

| Category | Score /100 | Disposition |
|---|---:|---|
| Inherited footprint / orientation consistency | 94 | Approved guidance |
| Transfer and cart orientation | 95 | Approved guidance |
| Machinery construction / specificity | 97 | Approved guidance |
| Human-scale handling readability | 93 | Approved guidance |
| Material family separation | 94 | Approved guidance |
| Lighting / component readability | 93 | Approved guidance |
| Strict Valorant / no-teal fidelity | 95 | Approved guidance |

**M04 result: APPROVED AS CONSTRAINED OCRU COMPONENT GUIDANCE.** Every applicable depicted category clears 90. It is compatible with the inherited long-axis arrangement and materially strengthens the OCRU assembly language. No room relocation or geometry recipe is authorized by this review.

## Inherited footprint and orientation — 94

Both hero views present a substantial machine with its berth running horizontally across the opening. The transfer bridge and cart extend outward from the mouth toward the viewer, so the transfer direction is normal to the machine face while the berth’s long axis remains along the machine/wall length. That relationship is consistent with the inherited 4.30 m wall length and 2.50 m depth envelope.

The image is a component sheet without a wall datum, room corner, scale bar, or world-axis marker. It therefore cannot prove exact placement, the saved R09 bounds, rear service clearance, or the east bypass. Those remain actual Blender and collision checks. The depicted orientation itself does not conflict with the inherited layout.

## Transfer and cart orientation — 95

The deployed view shows a full-width rolling transfer cart aligned with the opening and supported by a folding bridge. The parked view shows the bridge/cart stowed at the machine face. Wheels, handles, tray rails, and the gap-crossing support make the intended load/unload sequence readable. The cart is presented as approaching the OCRU from the room, rather than turning the berth lengthwise into the chamber, which is the correct conceptual relationship for the inherited long-axis berth.

M04 does not show the southwest parking bay, portal turn, a loaded ragdoll, or obstruction behavior. It should not be credited as proof of those room-level tests. The cart/bridge assembly is nevertheless a coherent component cue for the existing layout.

## Machinery construction and specificity — 97

M04 is the strongest OCRU machinery study so far. The main views show layered sheet-metal fascia, deep jambs, panel breaks, captive access treatment, lower plinth/supports, service routing, and a mechanically supported berth. The component strip explicitly depicts a rolled access shutter and gasket track, tray support rail and adjustable cradle, folding transfer bridge, suit-service hose and coupling, capped medical cartridge receiver, guarded emergency release, and removable service-access panel. These are distinct constructed parts rather than a cyan display case or repeated bevelled boxes.

The component plate does not define exact interaction IDs, host ownership, power draw, restart sequencing, or failure states. Those remain interface/runtime responsibilities. Its physical vocabulary is sufficiently specific and legible for constrained Blender guidance.

## Human-scale handling readability — 93

The adult berth, transfer cart, caster wheels, handles, rail height, hose coupling, and guarded release are proportioned as equipment a worker could operate. The cart deck and bridge communicate a continuous supported transfer surface, addressing the earlier R09 concern that the berth read as a thin pallet. There is no human or known body datum in the image, so exact reach, load clearance, and ragdoll collision remain unproven. The component relationships still read at practical industrial scale.

## Material family separation — 94

Painted light metal, darker graphite housings, black rubber hoses and seals, bare-looking rail/caster hardware, and orange functional accents separate cleanly. The plate uses broad quiet panels with localized fasteners and edge wear rather than a universal satin-plastic finish. The neutral background and absence of colored chamber glow keep the material read clear.

The image retains a polished generated product-sheet finish and mild photographic surface variation. Translate the families with controlled roughness and authored localized wear; do not import photographic grunge or exact surface marks.

## Lighting and component readability — 93

Neutral studio illumination keeps both front views and all seven detail crops readable. Shadows under the cart, bridge, and lower frame establish contact. Dark gasket tracks and hoses contrast against the light fascia, while orange handles and couplings identify functional interaction points. This is an assembly study, so the lighting is intentionally even; it does not establish the room’s final practical-light hierarchy.

## Strict Valorant and no-teal fidelity — 95

M04 uses believable manufactured construction, strong silhouettes, broad graphite/bone value grouping, restrained orange utility accents, and a specific industrial object vocabulary. No teal or cyan appears in the OCRU, berth, cart, hoses, controls, or lighting. The plate avoids holograms, decorative neon, generic sci-fi motifs, and hospital/morgue styling.

The exact header and bottom labels are concept annotations. The canonical machine name remains **Organic Continuity and Recommissioning Unit (OCRU)**; the plate’s shorter `OCRU` mark is compatible. Descriptors such as `EMPLOYEE REANIMATION CHAMBER`, `SUIT SERVICE HOSE & COUPLING`, and `MEDICAL CARTRIDGE RECEIVER` are guidance labels, not replacements for the game’s canonical interface names.

## Limits before Blender adoption

- Preserve the existing R09 OCRU placement and inherited 4.30 m × 2.50 m envelope.
- Preserve the berth long axis along the wall; use the M04 bridge/cart relationship as the component cue.
- Keep the shown deep jamb, gasket/shutter, tray support, coupling, guarded release, cartridge receiver, and service-panel distinctions.
- Recheck actual cart parking, portal passage, loaded-body obstruction, east bypass, and rear service clearance from fixed-camera pixels and collision tests.
- Keep all runtime state, power, cartridge, host-hook, and failure semantics in the interface contract.
- Retain the strict no-teal/no-cyan palette and controlled, non-photoreal wear during translation.

**M04 is approved only as constrained OCRU assembly guidance. It does not supersede the saved room, and it provides no room-level runtime or collision proof.**

