# Full cycle 01 — independent lighting / atmosphere review

**Category 5: 80/100 — FAIL.** The requirement is strictly greater than 93/100. Every fixed view must also pass, with zero critical defects. This review does not approve the room or any other category.

Reviewed on 1 October 2026. Source SHA-256: `dc608cae0a42303e614f2db3dc0cd9d50e4366dc738ac57c35957c6df34e0331`.

All 26 actual labelled dock PNGs in `production/renders/full-cycle-01/` were opened individually with the image-reading tool, including recovered `DETAIL_CHECKIN`, `PLAYER_REVERSE` and `PLAYER_PINCH`. All are 1067 × 600 and match the completed manifest image hashes. The four actual approved references opened were `VALIDATE_Material_A`, `VALIDATE_LockerDoor`, `VALIDATE_Spawn` and `BRIEFING_INDIRECT` in `production/renders/spawn-reference/`. Judgments below come from pixels. No scene code, author history or prior critic verdict was used.

Authorities read: repository `AGENTS.md`; `.agents/skills/blender-headless/SKILL.md`; `design/ART_DIRECTION.md`, `ART_REFERENCE_INDEX.md`, `AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`; this revamp's `scenery/OVERHAUL_BRIEF.md` and `production/RUBRIC.md`.

## Judgment

The warm check-in/office area against the cooler dock is a useful hierarchy. Counter papers, the intercom, chair, desk and controlled green CRT are exposed clearly. Warm off-white walls, dark blue structural elements, muted blue equipment, orange doors and yellow route markings remain within the approved spawn's institutional colour grammar. Deep storage shadows and the covered transfer trolley create a coercive mood. Small indicators and fluorescent practicals avoid broad neon bloom; highlights on the counter are restrained. There is no dominant whole-room flat-even-lighting or excessive-emissive veto.

The principal shortfall is light direction. Too much of the dock's useful illumination lands on the floor, walls and the cargo housing's upper surfaces. The scanner/cart fronts stay close to black from multiple worker-height views. Their outer silhouettes can be found against the pale floor and walls, but recesses, face changes, controls and lower construction merge together. Dark paint alone does not require this loss of form: the approved locker and airlock references retain lit edges, face gradients and distinguishable construction while keeping dark secondary space. Raising the entire scene exposure would weaken the currently successful check-in area.

The cargo housing has readable cool planes and rib shadows, yet its pale roof becomes the brightest equipment mass in all four cutaways. The inspection arch is weaker, and some front intake/roller construction disappears in shadow. The support bay can remain dim, but the trolley's undercarriage, lower shelf and wheels merge into the floor shadow even in its dedicated hero frame. The roof-services view similarly exposes luminous tubes and a few beam faces while much of the service network becomes a black field. These are visibility losses, not proof that the underlying geometry is missing.

Exposure is visually consistent across the views and recovered tail; the same regions remain dark rather than a single camera appearing to receive a different exposure. There is useful soft falloff and contact shadow. The problem is distribution and orientation of illumination, with inadequate fill on specific important forms.

## Critical acceptance blocker and veto scope

**HERO_SCANNER fails the every-fixed-view hard gate.** A close beige wall occupies roughly the left three fifths of the frame and obscures most of the arch. The remaining scanner/cart pieces are dark. This cannot serve as a hero evidence view. Repairing this proven camera obstruction requires a documented rebaseline; it is not a lighting score bonus or evidence that the scanner is acceptable elsewhere.

The recurring under-read scanner/cart geometry is a major category-5 defect. I do not assert a whole-room unreadable-silhouette veto: their outer silhouettes remain detectable in several views. I also do not assert a flat-even-lighting, glare, uniform-plastic or technical veto from this lighting-only review. The camera hard-gate failure alone prevents acceptance, independently of the category score.

## Every inspected view

PASS below means the relevant forms remain readable for lighting review. It does not certify another category or the room. All stated FAILs remain unresolved.

| View | Lighting result | Pixel evidence |
| --- | --- | --- |
| C01_ENTRY | FAIL | Scanner uprights, cart leaves and control housings merge into dark masses; floor lanes and status dots carry the read. |
| C02_HERO_DOCK | PASS | Warm counter is legible and separated from the cool dock. Rear equipment is subdued; glazing reflection softens it but does not obscure the counter. |
| C03_CHECKIN_COUNTER | PASS | Intercom, stamps, paper and counter edge have controlled local contrast. Black lower fascia is subordinate. Small bright glazing reflection is not a dominant glare failure. |
| C04_SCANNER_APPROACH | FAIL | Near-black columns/control housings expose almost no construction; the illuminated lane behind them is much clearer than the inspection equipment. |
| C05_CONVEYOR_LEAD_TUNNEL | PASS, repair desirable | Cool housing planes/ribs and cargo colour blocks read. Intake interior and lower rollers remain weak; preserve the dark tunnel while revealing its lip and mechanical support. |
| C06_CART_GATE_G1 | FAIL | Gate leaves, side assemblies and posts merge; orange patches and indicator dots carry most of the functional contrast. |
| C07_OFFICE_INTERIOR | PASS | Warm practical pool gives clear chair/desk contact and a restrained screen focal point. Rear dock remains cooler. |
| C08_CONCEALED_SUPPORT_H1 | FAIL | Covered upper volume is faintly legible, but rail, shelf and lower chassis merge into black; insufficient separation for a functional support view. |
| C09_ARRIVAL_GATE_P2 | FAIL | Large gate face is too uniformly dark. Ribs are only faintly separable and header lettering has weak contrast; beacons do not sufficiently reveal the gate construction. |
| C10_ROOF_SERVICES | FAIL | Light tubes and selected beam edges read, but much of the overhead routing and structure disappears into a near-black field. |
| CORNER_SW | PASS, hierarchy repair | Warm office/cool dock division and contact shadows read. Cargo roof is disproportionately bright; arch face lighting is weaker. |
| CORNER_SE | PASS, hierarchy repair | Functional zones are visible. Bright cargo roof competes with check-in, while the support bay becomes a dark cluster. |
| CORNER_NW | PASS, hierarchy repair | Local warm office and cool cargo pools are visible. Cargo top dominates equipment; support lower forms are subdued. |
| CORNER_NE | PASS, hierarchy repair | Broad spatial depth survives. Pale cargo top attracts more attention than the arch; dim support hardware is difficult to distinguish. |
| WALL_SOUTH | FAIL | Arch outline is visible against the rear wall, but its front construction and cart leaves remain too dark beneath the practical. |
| WALL_NORTH | FAIL | Scanner fronts read mainly as dark posts plus bright dots; header and rear gate lack sufficient separation. |
| WALL_EAST | PASS, repair desirable | Cargo/service wall has readable cool planes and controlled lights. Foreground scanner face remains almost black. |
| WALL_WEST | PASS | Warm office wall, drawers, desk and counter read with soft falloff. Foreground scanner and white partition dominate framing, but a lighting failure of the office is not established. |
| HERO_SCANNER | FAIL — critical evidence blocker | Foreground wall obscures most of the intended subject; remaining inspection pieces are dark. Mandatory hero coverage is invalid. |
| HERO_CARGO | PASS, repair desirable | Housing ribs, container planes and conveyor silhouette read. Intake lip/front face and lower mechanics need a restrained oblique fill. |
| HERO_EVIDENCE | PASS | Dim blue doors, frames, locks and restrained paper cue remain distinguishable. Preserve this lower hierarchy. |
| HERO_TROLLEY | FAIL | Covered form and cabinet faces read, but rail, underdeck and wheels disappear into the floor/contact-shadow mass. |
| HERO_UTILITIES | PASS | Cool housings, conduits and cabinet faces are distinguishable, with restrained status glow and plausible wall shadows. |
| DETAIL_CHECKIN | PASS | Counter paperwork, metal edges, folded item and stamp remain readable without hot highlights; good local work-light exposure. |
| PLAYER_REVERSE | FAIL | Rear-facing arch/cart construction remains too dark. Bright floor/wall behind supplies the outline but does not reveal important faces. |
| PLAYER_PINCH | PASS | Gate ribs, floor transition/drain, cart outline and utility cluster remain readable with a subdued practical pool. |

## Five lighting repairs, in priority order

1. **Reveal scanner/cart construction with an oblique practical key and restrained bounce.** Target the upright faces, recessed controls, cart-leaf edges, side housings and lower rails. Keep charcoal values, dark overhead space and limited indicators. Recheck C01, C04, C06, WALL_NORTH, WALL_SOUTH and PLAYER_REVERSE: construction must read without depending on bright dots or yellow paint.
2. **Redirect cargo illumination from its roof to the intake and work surfaces.** Lower the pale top's dominance in all four cutaways and provide soft angled light across the intake lip, adjacent control housings and roller edges. Keep the deep examination tunnel dark. C05/HERO_CARGO should reveal front depth while the check-in and worker arch remain primary.
3. **Give the support trolley a small, motivated side/bounce pool.** Separate the cover from the rail and reveal caster/lower-shelf boundaries in C08 and HERO_TROLLEY. Keep evidence storage and surrounding walls darker than the check-in; preserve the bleak covered-volume read.
4. **Let overhead practicals reveal nearby services with faint grazing/bounce light.** C10 needs a legible hierarchy of beam, duct/routing and background, rather than luminous tubes against missing structure. Keep the ceiling predominantly dark and avoid adding decorative glowing service lines.
5. **Strengthen falloff and gate-face depth along the dock route.** Shape existing pools so occupied inspection positions are brighter than the intervals between them, and graze the arrival gate enough to show rib/reveal depth in C09. Avoid an overall exposure increase: papers and warm counter are already adequately exposed. Verify PLAYER_PINCH still reads and no floor hotspot replaces the scanner as the focal area.

Separate evidence repair: move/re-aim the obstructed HERO_SCANNER camera into a valid unobstructed position, document why the fixed view was invalid, establish the replacement baseline and rerender it alongside the unchanged mandatory worker views.

Only this report and its paired JSON are authored by this critic. No source, geometry, materials, lights, cameras or production acceptance state were edited. No technical, cold-start, cycle-stability or runtime claim is made.
