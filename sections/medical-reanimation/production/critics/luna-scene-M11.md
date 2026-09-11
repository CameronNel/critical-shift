# Independent Luna final scene review — M11 complete pack

Reviewer: Luna (independent)

Revision: **M11**  
Blend SHA-256: `35d278c93cf8f385258da9e5b93ab6709d8166552ef204aca41b97231c04eb9a`

## Scope and evidence reviewed

I reviewed the complete M11 fixed pack in `production/renders/final/` (14 images), the six designated state images in `production/renders/states/M11/`, and cold spot checks for `CAM_ENTRY`, `CAM_DECON`, and `CAM_MAINT` in `production/renders/cold/`. The final and cold manifests identify M11 and the requested blend hash. The state manifest contains `S01_TRANSFER`, `S02_DROPPED_CART_BYPASS`, `S03_DECON_APRON`, `S04_ENTRY_CLOSED`, `S05_RESERVE_SERVICE`, and `S06_CART_EXTRACTION`.

The visual comparators were the approved constrained `M03`/`M04`/`M05` guidance, especially `M06-targeted-ocru.png` and `M05-rear-service.png`, the preserved R09 arrangement, and the medical/reanimation brief and chapter 5 procedure contract. The room remains the inherited layout: west OCRU, rear console/cartridge bank, rear decon, east recovery/supply, southwest cart staging, and a central transfer/keep-clear apron. I found no reason in the pixels to relocate any station.

This is a pixel review of the supplied room art and designated static evidence. A close-up is judged on its designated coverage; a material or machinery close-up is not penalized for omitting an unrelated body pose. The technical and interaction reports support static envelope and authored-hook readiness. They do not prove host runtime authority, navmesh, replication, ragdoll physics, or state-machine behavior, and this review does not claim those systems are implemented.

## Decision

**M11 scene: PASS at the strict greater-than-90 gate.** Every relevant category below is strictly greater than 90, and every fixed or state view is strictly greater than 90. The prior consequential defects are visibly resolved: the transfer pose has a coherent scissor mechanism, the fixture-level decon plaque is gone, `CAM_MAINT` has no clipped sign fragment, and the revised entry hardware no longer presents the earlier constrained extraction risk in the supplied evidence. The `DECON` / `BEFORE LOADING` header is judged in `CAM_ENTRY` and `CAM_ROUTE`; `CAM_DECON` and `CAM_MAINT` judge the unobstructed reel/wand/PPE and service machinery views.

## Independent category scores

| Category | Score /100 | Finding |
|---|---:|---|
| Scale / circulation | 95 | Full-room and route views establish an adult-scale chamber with a broad central apron, coherent station spacing, and a readable entry-to-rear process. |
| Shape / art direction | 94 | The OCRU, cart, console, rack, decon bay, cabinet, and recovery berth have authored layered silhouettes and the quieter graphic Valorant treatment requested by the approved concepts. |
| Hierarchy / gameplay readability | 94 | OCRU remains the landmark; console, cartridges, decon, recovery, supply, and reserve stations read as distinct secondary work zones. |
| Materials | 93 | Pale painted shell, graphite/black machine surfaces, rails, rubber hose, orange functional hardware, glass/stock, cloth, and floor markings separate at player-view scale. |
| Lighting | 94 | Neutral overhead and task lighting gives the OCRU, console, decon, reserve, and recovery areas usable pools and contact shadows without a cyan/teal wash. |
| Color discipline / no-teal | 98 | The complete fixed, cold, and state pack stays in neutral grey, pale manufactured, graphite, black, cream, and restrained orange; no teal or cyan is present. |
| Environmental storytelling | 94 | The room communicates retrieve, decon, load, suit, power, cartridge, restart, and recovery through visible equipment, labels, stock, used-PPE handling, and work artifacts. |
| Technical correctness / evidence | 96 | M11 technical checks pass 13/13, interaction checks pass 5/5, contact candidates are empty, manifests/hash/source evidence are tied to M11, and the supplied images agree with the static evidence. |
| Spec / procedure fidelity | 96 | The visible stations and process order match the medical/reanimation brief and chapter 5 contract while retaining the inherited room plan. |
| Equipment completeness | 96 | OCRU, adult berth, cart, restart console, cartridge bank, reserve power, recovery berth, supply bench/supplies, decon, and handwash are all present and visually legible. |
| Construction specificity | 94 | The M06/M04 guidance is carried into segmented berth pads, rails/straps, supports, physical controls, grouped cartridge stock, connected decon service hardware, cabinet interiors, and authored work details. |
| Label / sign readability | 94 | `INSERT`, `SUIT`, `RELEASE`, `RESTART`, `ARM`, `CONNECT`, `CARTRIDGES`, `DECON`, `BEFORE LOADING`, `RECOVERY`, `SUPPLIES`, `USED PPE`, `MED POWER`, and `ISOLATE` are readable in their designated coverage. |
| State-pose / physical-envelope evidence | 94 | All six supplied state views are coherent; transfer, bypass, decon apron, closed entry, reserve service, and cart extraction are visibly represented. Static measurements and five cart paths supplement the pixels. |
| Reference fidelity / strict Valorant | 95 | M11 preserves the approved concept silhouette and graphic value grouping, with restrained orange accents and practical wear instead of drifting into teal-heavy or photoreal-grunge treatment. |
| Camera coverage / readability | 94 | Fourteen player-height fixed cameras cover the room, machinery, materials, route, entry, outside approach, supplies, and rear service with no unresolved designated-view obstruction. |
| Integration hooks / static envelope | 95 | Authored roots, markers, connections, state poses, preserved neighbor ownership, corrected entry envelope, and documented host-hook boundaries are ready for local integration review. |

All category values are greater than 90. The integration score is limited to saved-art hooks and static envelope evidence; it is not a runtime implementation score.

## View-by-view pixel scores

Scores assess each image against its designated coverage.

| View | Score /100 | Independent pixel finding |
|---|---:|---|
| `CAM_CONSOLE` | 95 | `RESTART`, `ARM`, and `CONNECT` are distinct; both screens and the console body read as a service station with useful orange control accents. |
| `CAM_DECON` | 94 | Tight reel, 5 m marker, wand, hose, fittings, grate, and used-PPE bin are clear and unobstructed. This crop does not show the threshold header, so it is not used to judge that sign. |
| `CAM_ENTRY` | 95 | Complete room overview: OCRU, console, cartridges, decon, recovery, supply, central apron, and entry relationship all read together; `DECON` and `BEFORE LOADING` are visible on the threshold backing. |
| `CAM_HERO` | 95 | OCRU berth construction is strong: layered pads, support structure, orange retention hardware, dark chamber, and `INSERT`/`SUIT`/`RELEASE` controls survive the hero framing. |
| `CAM_MAINT` | 94 | Reel/decon edge, `MED POWER`, `ISOLATE`, and the supply cabinet read as a serviceable maintenance zone; the former clipped fragment is gone. Header coverage is not assigned to this close-up. |
| `CAM_MATERIALS` | 94 | Reserve cabinet, gauge, selector, handles, and surrounding material families show controlled painted metal, graphite, orange, and contact separation. |
| `CAM_PINCH` | 94 | Berth pads, rails, supports, and scissor-track construction read at close range with useful shadow/contact; unrelated cart/body state is outside this camera's coverage. |
| `CAM_RECOVERY` | 94 | Recovery cot, mattress, pillow, rail, cloth blanket, floor contact, and recovery cue establish a prepared monitored position. |
| `CAM_REVERSE` | 95 | Reverse view confirms the default parked-open leaves flanking the dark portal and the room's west/east station balance without losing OCRU or recovery readability. |
| `CAM_ROUTE` | 95 | The process overview connects entry, OCRU, console, cartridges, decon, recovery, and supply; the threshold `DECON` / `BEFORE LOADING` sign is correctly attributed here. |
| `W01_ENTRY_OUTSIDE` | 95 | Exterior-to-room approach clearly frames the threshold, central transfer/keep-clear apron, and preserved room ownership. |
| `W02_CART` | 96 | Cart deck, three pads, rails, scissor lift, casters, handles, and orange functional details are clearly constructed in the designated cart view. |
| `W03_SUPPLIES` | 95 | Sink, packets, tools/gloves, shift log, work surface, and storage establish an operational supply station. |
| `W04_REAR_SERVICE` | 95 | Grouped cartridges 01–12, reserve/power service, supply cabinet, rear relationships, and console edge are legible as a coherent service band. |
| `S01_TRANSFER` | 94 | Loaded body/cart transfer pose is coherent; the scissor tracks and endpoints remain assembled and the OCRU interface is visible. |
| `S02_DROPPED_CART_BYPASS` | 94 | Dropped cart at left, recovery berth at right, and the open central bypass route are visually clear. The image is judged as static arrangement evidence, not runtime navmesh proof. |
| `S03_DECON_APRON` | 94 | Cart-to-decon apron relationship, cartridge rack, reel/hose, grate, and PPE handling read clearly. The top crop is not treated as header proof. |
| `S04_ENTRY_CLOSED` | 93 | The closed opposed leaves and their vertical glazing-frame members are visibly distinct and coherent for the designated closed-entry state. |
| `S05_RESERVE_SERVICE` | 94 | Open reserve cabinet, gauge, internal service volume, handles, and adjacent console work surface provide convincing service-state evidence. |
| `S06_CART_EXTRACTION` | 93 | The cart is shown in the corrected lateral extraction pose between the entry structures with no visible collision or bent mechanism; static measured clearance and padded sweep evidence supplement this view. |

Every view score is greater than 90. The designated state views are supplemental evidence for static pose and envelope; host handling remains a separate integration responsibility.

## Cold and replay evidence

The M11 cold comparison reports `render_comparison_pass=true` for all 14 fixed cameras. Maximum channel difference is 1/255, with 146–231 changed pixels out of 1,296,000 per camera, consistent with documented GPU rounding rather than a perceptual change. I spot-checked the cold `CAM_ENTRY`, `CAM_DECON`, and `CAM_MAINT` images: they preserve the same visible composition, header attribution, machinery, palette, and label outcomes as the final pack. The six state images were independently inspected from the M11 state folder; the supplied state fingerprints for `cold-A`, `cold-B`, and `source-replay` are identical (`ee095b626465ef2941833261aae7433e973503400651823553c9d838c926b68e`).

This cold/replay result confirms reproducible saved-art evidence. It does not turn a static render into proof of runtime state transitions, authority, navmesh, or collision behavior.

## Remaining integration boundaries

No pixel defect remains that justifies rejecting the room or changing its inherited layout. The technical reports correctly keep runtime ownership with the host: authority and replication, occupancy, power/cartridge state, contamination/compliance locks, ragdoll handling, navmesh, temporary debuffs, and recovery/repositioning. The static M11 evidence is ready for local integration review within those boundaries.

**Final disposition: PASS.**
