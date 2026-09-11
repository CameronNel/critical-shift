# Independent Luna scene review — M05 complete fixed pack and state views

Reviewer: Luna (independent)

Reviewed pixels:

- `production/renders/review/M05/` — all 14 fixed-camera renders
- `production/renders/states/M05/` — `S01_TRANSFER`, `S02_DROPPED_CART_BYPASS`, `S03_DECON_APRON`, `S04_ENTRY_CLOSED`, and `S05_RESERVE_SERVICE`

Comparators: approved constrained OCRU hero guidance in `art/concepts/M06-targeted-ocru.png`, approved rear-service guidance in `art/concepts/M05-rear-service.png`, approved component guidance in `art/concepts/M04-ocru-component.png`, the preserved R09 layout, and the medical/reanimation brief/spec.

This is a pixel review of the delivered room and designated evidence views. Cart/body absence is not penalized in material or close-up cameras whose designated coverage does not require those poses. Host runtime/navmesh/state implementation is outside the Blender art criterion. The review does assess visible state-pose correctness, physical envelope evidence, contact, labels, and the completeness of supplied art evidence.

## Independent category scores

| Category | Score /100 | Disposition |
|---|---:|---|
| Layout / scale / circulation | 94 | Pass |
| Machinery / operational readability | 93 | Pass |
| Material family separation | 92 | Pass |
| Lighting hierarchy / contact | 93 | Pass |
| Color discipline / no-teal | 98 | Pass |
| Environmental storytelling | 93 | Pass |
| Label / sign readability | 89 | **Fail** |
| State-pose / physical-envelope evidence | 87 | **Fail / incomplete** |

**M05 scene result: FAIL for the strict >90 gate.** The art pass is close and clears the broad room categories, but the decon label obstruction and the visibly incorrect S01 scissor-beam endpoint prevent approval. Final cold evidence is also still pending. The saved default cart geometry and the reported carry/bypass checks are not downgraded here; the S01 defect is specific to the rendered evidence pose.

## Fixed-camera view scores

Scores assess each camera’s designated coverage, rather than demanding every room feature in every image.

| View | Score /100 | Independent finding |
|---|---:|---|
| `CAM_ENTRY` | 94 | Strong room overview; OCRU, restart, cartridges, decon, recovery, and transfer apron read together. |
| `CAM_REVERSE` | 93 | Entry closure and reverse room relationship read clearly; OCRU and recovery remain legible at the sides. |
| `CAM_HERO` | 95 | M06 translation is visible: segmented berth, supports, front rail, `INSERT`, `SUIT`, `RELEASE`, and neutral task lights. |
| `CAM_ROUTE` | 94 | Best process overview; console, cartridge rack, decon, used-PPE bin, OCRU edge, and clear central route read together. |
| `CAM_CONSOLE` | 94 | `ARM`, `CONNECT`, and `RESTART` controls are separated and readable; state board and employee panel are legible. |
| `CAM_DECON` | 88 | Reel, 5 m marker, fittings, hose, grate, and used-PPE bin are convincing, but `WASH / BEFORE LOAD` loses its leading `W` behind the fixture. |
| `CAM_MAINT` | 90 | Reserve/power cabinet and decon edge are visible; the cabinet is serviceable and readable, but the cropped decon sign fragment weakens finish. |
| `CAM_MATERIALS` | 94 | Cart berth materials, graphite pads, painted skins, steel rail, orange straps, and contact shadows separate cleanly. |
| `CAM_PINCH` | 93 | Berth under-structure, rails, pads, and supports read at close range; no cart/body deduction is applicable to this construction view. |
| `CAM_RECOVERY` | 93 | Cot, rails, mattress, blanket, and recovery signage establish a practical monitored position. |
| `W01_ENTRY_OUTSIDE` | 95 | Entry-to-room transition and transfer/keep-clear apron are clearly framed. |
| `W02_CART` | 96 | Cart construction, scissor lift, casters, deck, and orange handles are clear in the designated cart view. |
| `W03_SUPPLIES` | 94 | Sink, supplies, shift log, work surface, and storage read as an operational support station. |
| `W04_REAR_SERVICE` | 95 | Cartridge inventory, rear service edge, power/isolate panel, decon threshold, and supply cabinet are legible. |
| `S01_TRANSFER` | 84 | Loaded transfer pose is present and the OCRU interface reads, but one scissor-beam endpoint is visibly mis-transformed in this evidence pose. **Reject pending corrected rerender.** |
| `S02_DROPPED_CART_BYPASS` | 94 | Dropped-cart obstruction and the remaining route around it are visually readable; no unrelated runtime requirement is imposed. |
| `S03_DECON_APRON` | 89 | Decon apron, cart relationship, reel/hose, cartridges, and recovery side read; the same small `WASH` label obstruction remains visible. |
| `S04_ENTRY_CLOSED` | 93 | Closed entry state is visibly distinct and the portal remains coherent. |
| `S05_RESERVE_SERVICE` | 95 | Open reserve cabinet, gauge, selector, handles, and service context match the M05 rear-service intent. |

## Layout / scale / circulation — 94

The fixed pack preserves the R09 arrangement: west OCRU, rear restart console and cartridge rack, rear decon, east recovery/supplies, southwest transfer staging, and the central transfer/keep-clear apron. `CAM_ENTRY`, `CAM_REVERSE`, `CAM_ROUTE`, and `W01_ENTRY_OUTSIDE` establish the room as one coherent working envelope. `S02_DROPPED_CART_BYPASS` also shows that the room retains a readable alternate route around the obstruction.

The views do not replace measured collision or navigation results. Reported carry, bypass, and contact checks may support this score, but no pixel review can invent unshown measurements. The preserved layout itself is visually consistent.

## Machinery / operational readability — 93

M05 now carries the M06 OCRU vocabulary into the room: the adult berth has a layered front rail, segmented pads, orange retention straps, two support stacks, and an open transfer face. The `INSERT` receiver has a recessed control face and lower release; the `SUIT` station has a collar, hose, and mounting hardware. The console has three guarded physical controls and a readable status board. The cartridge rack has grouped numbered stock, and the decon has a real reel, visible fittings, hose loop, grate, and used-PPE bin. The reserve cabinet is open and hollow in `CAM_MAINT`/`S05_RESERVE_SERVICE`, making service access credible.

The S01 pose defect is a state-evidence failure, not a claim that the saved default cart assembly is wrong. The actual host behavior, IDs, power ownership, and state transitions remain interface/runtime work.

## Material family separation — 92

Painted pale metal, graphite panels, black dry-rubber hose, steel rails and fasteners, orange safety hardware, glass-fronted storage, fabric blanket, and floor markings separate at gameplay image size. The M05 pass is calmer and more graphic than M01/M03, with restrained edge treatment and good broad value grouping. The berth and reserve cabinet benefit especially from this separation.

The image still has a clean generated/rendered finish in some broad wall and floor surfaces. This is acceptable for the current pass but should remain controlled during integration; preserve localized wear and avoid adding noisy photoreal grunge.

## Lighting hierarchy / contact — 93

Neutral overheads and task fixtures produce a clear station hierarchy: OCRU task lighting, console/rear wall, decon work light, and recovery side lighting each remain readable without teal/cyan glow. The darker OCRU interior and black console backing give the functional controls contrast. Cart, berth, cot, cabinet, and decon bin all cast useful contact shadows.

The known remaining berth under-light and restrained edge-finish concerns are visible as polish limitations rather than broad readability failures. They should be addressed in the final art pass, especially in the hero and pinch views.

## Color discipline / no-teal — 98

The complete pack contains no teal or cyan in materials, practical lights, or state views. Neutral grey, bone/pale manufactured surfaces, graphite, black, and restrained orange establish a consistent functional palette. Orange is used for controls, handles, straps, reel, cart accents, and safety floor boundaries rather than decorative neon.

## Environmental storytelling — 93

The room now communicates the chapter 5 sequence through distinct visible cues: transfer apron and cart, `WASH / BEFORE LOAD` decon assembly, used-PPE bin, `INSERT`/`SUIT`/`RELEASE` OCRU controls, numbered cartridges, console state board, mains/reserve service, and a prepared recovery cot. M05 aligns well with M05 rear-service and M06 OCRU guidance while retaining the R09 plan.

The story is weakened only where the decon sign is partially hidden and where S01’s pose error makes the transfer evidence look mechanically unresolved. Those are targeted corrections, not a reason to redesign the room.

## Label / sign readability — 89 — fail

Most labels are now readable: `INSERT`, `SUIT`, `RELEASE`, `RESTART`, `ARM`, `CONNECT`, `CARTRIDGES`, `DECON`, `RECOVERY`, `SUPPLIES`, `USED PPE`, `MED POWER`, and the console state text survive the fixed-camera framing. This is a clear correction over M03’s stem occlusion and tiny console labels.

The decon station’s intended `WASH / BEFORE LOAD` sign is visibly rendered as `ASH / BEFORE LOAD` in `CAM_DECON` and remains obstructed in `S03_DECON_APRON`. That is a real pixel defect in a designated process view and keeps the category below 90. Clear this small obstruction and rerender both affected views. Preserve the canonical machine identity as **Organic Continuity and Recommissioning Unit (OCRU)**; do not introduce an invented long name.

## State-pose / physical-envelope evidence — 87 — fail / incomplete

`S02_DROPPED_CART_BYPASS`, `S04_ENTRY_CLOSED`, and `S05_RESERVE_SERVICE` are useful visible evidence. `S01_TRANSFER` contains the expected loaded body/cart pose, but one scissor-beam endpoint is visibly transformed away from its assembly relationship. The defect is obvious in the rendered pose and must not be approved until the corrected pose source is rendered. The default cart geometry remains separately represented by `W02_CART` and is not rejected by this finding.

Final cold evidence is still pending, so the pack cannot yet claim complete state coverage. Contact/sign residuals should be rechecked after the corrected S01 render and the decon-label fix. No whole-map runtime implementation is required for this room-art review.

## Prioritized corrections before approval

1. Rerender `S01_TRANSFER` from the corrected pose source and verify both scissor-beam endpoints, support pivots, cart deck contact, and loaded-body support in pixels.
2. Clear the decon fixture from the leading `W` in `WASH / BEFORE LOAD`; rerender `CAM_DECON` and `S03_DECON_APRON`.
3. Address the remaining berth under-light and restrained edge-finish polish in the hero/pinch coverage without changing the preserved room layout or introducing teal.
4. Supply final cold evidence and recheck contact/sign residuals against the corrected renders.

**M05 is visually close and materially improved, but remains rejected at the strict >90 gate until the S01 transfer-pose defect, decon label obstruction, and pending cold evidence are resolved.**
