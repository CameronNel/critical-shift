# Fuel Corridor F10 independent review

Revision `final-F10` was reviewed from the complete 1440×960/32-sample image set in `production/renders/review/final-F10`, the matching canonical cold pack in `final-F10-cold`, and the twelve 1200×800/1.70 m player-eye approaches in `final-F10-walkthrough`. Reviewer: grok-4.6 independent critic. This is not a Luna review.

F10’s only geometry change versus F09 is the first-aid mark: `Bypass_first_aid_cross_h` and `Bypass_first_aid_cross_v` were replaced by one `Bypass_first_aid_cross`. Direct C07 pixels show a continuous solid orange cross. Canonical cold16 reports every view max ≤1/255.

## Result

**PASS.** Every one of the 17 categories, 16 fixed views, and 12 player-eye views is strictly above 90.

## Category scores

| Category | Score | Evidence and bounded limitation |
|---|---:|---|
| Specification coverage | 93 | Required doors, service station, staging, freight, workbench, carrier, and route identity are represented. Neighboring unassembled room fit remains out of scope. |
| Facility/process logic | 93 | F01/F02/S01/S02/S03 identity, service-air operation, waste/plant/clean sequencing, and staging workflow read coherently. Runtime controls are out of scope. |
| Human scale | 94 | Door, rail, workbench, carrier, valve, and service hardware read at believable worker scale. |
| Player circulation | 94 | Floor lines and arrows keep the route readable; the twelve player-eye approaches confirm continuity. |
| Freight/cart handling | 94 | Parked FC-07 carrier, marked bay, restraint hardware, and turn/approach framing support the handling story. |
| Maintenance access | 94 | Workbench, tools, grease, gloves, service-air regulator/gauge/hose, and access panels provide a complete maintenance read. |
| Interface consistency | 91 | Local F01/F02 and reserved S01/S02/S03 contracts are authored and labelled. Exact neighboring assembly fit is not claimed. |
| Machinery construction | 94 | Carrier, straps, feet, rollers, motor, gate, air regulator, pipe joints, access panels, and fasteners read as assembled mechanisms. |
| Physical support/contact | 93 | F10 support audit passes; motion replay reports only zero-depth contact/tangency events. This is bounded finite evidence, not a continuous engine collision proof. |
| Valorant shape language | 93 | Dark structural frame, ivory panels, orange safety accents, bevels, readable silhouettes, and restrained industrial props match the grounded Valorant direction. |
| Material separation/anti-plastic | 93 | Painted panel, dark steel, rubber, cloth, brushed metal, and carrier surfaces separate clearly. |
| Lighting/readability | 92 | Practical fixtures produce useful contrast; C08/W12 remain quieter service corridors rather than underlit voids. |
| No-teal color discipline | 95 | Palette stays in ivory, charcoal, steel, orange, and restrained warm utility tones. |
| Signage/numbering | 91 | Door labels, advance cues, floor arrows, bay marking, and service labels are readable. The wayfinding audit still reports the transparent FIRST AID lid as a type obstruction; the cross itself is scene-readable. |
| Environmental storytelling | 93 | Tool wall, consumables, check tags, carrier restraint, service-air hardware, warning placards, and access wear support a working facility. |
| Camera coverage | 94 | All ten mandatory, six diagnostic, and twelve player-eye purposes are covered. |
| Saved-artifact/source/dependency reproducibility | 94 | F10 SHA, source replay, material/UV/packed-texture replay, branch/handoff, and all 16 cold pairs agree. PNGs are not claimed byte-identical. |

## Fixed views

| View | Score | Direct pixel finding |
|---|---:|---|
| C01_ENTRY | 93 | Clear service/bypass and F02/reactor identity, freight arrow, trolley bay, and readable route depth. |
| C02_PRIMARY_ROUTE | 93 | S03 waste and F02 reactor boards, floor turn arrow, and passage margins read cleanly. |
| C03_HERO | 91 | Strong staging/workbench/carrier/service composition; FG01/FREIGHT header is cropped by the camera frame. |
| C04_REVERSE | 93 | Refinery doors and sign are clear. No beam-edge sparkle from the F09 cold exception remains visible. |
| C05_EAST_TURN | 93 | Waste turn, advance sign, panel construction, and floor line are legible. |
| C06_REACTOR_THRESHOLD | 94 | Close threshold view clearly shows F02/reactor identity, bolted access panels, contact wear, and handles. |
| C07_BYPASS | 93 | S01/plant and S02/clean cues, arrow, electrical panel, and a single-piece first-aid cross. Clear lid remains a bounded type caveat. |
| C08_SERVICE_JUNCTION | 93 | S02/clean cue, orange floor line, support bays, and rear-wall construction read cleanly. |
| C09_MATERIALS | 94 | Carrier shell, orange straps, rings, clamps, feet, rails, wheels, bay border, and labels. |
| C10_PLANT_HEADER | 94 | S01/plant header and paired doors are centered and legible. |
| D01_CARRIER_OPERATION | 94 | Detailed carrier supports, brakes, wheels, straps, rings, and restraint labels. |
| D02_WORKBENCH | 91 | Tools, gloves, grease, case, shelf, and bench construction are clear; upper housekeeping text is cropped. |
| D03_UTILITY | 94 | Service-air regulator, gauge, valve, hose, pipe elbows, supports, and labels. |
| D04_REACTOR_WIDE | 94 | Near-black header is legible; complete reactor threshold composition is readable. |
| D05_GATE_MECHANISM | 91 | Motor, bracket, warning plate, and transmission housing read sharply; the large lower sign is clipped. |
| D06_SERVICE_RECESS | 94 | Service-air recess is centered with a complete pipe/regulator/gauge/hose assembly. |

## Player-eye views

| View | Score | Direct pixel finding |
|---|---:|---|
| W01_REFINERY_APPROACH | 93 | Centered F01/refinery doors, stand-clear plates, and transfer identity. |
| W02_SERVICE_ENTRY | 93 | Bypass header, S02/clean board, F02 cue, and orange floor line from standing height. |
| W03_PLANT_APPROACH | 94 | S01/plant doors, work-permit board, and rails at human scale. |
| W04_PLANT_RETURN | 92 | Return into the bypass with first-aid kit, S02/clean advance, and floor arrow. |
| W05_CLEAN_APPROACH | 93 | S02/clean doors and stand-clear plates; header is tight to the top of frame. |
| W06_WASTE_APPROACH | 93 | S03/waste doors plus the adjacent waste-transfer board. |
| W07_DELIVERY_RETURN | 92 | Waste doors on the left, F02 freight-approach board, and return arrow. |
| W08_EAST_TURN_RETURN | 92 | Return toward staging with workbench and carrier visible in depth. |
| W09_BENCH_ACCESS | 93 | Full tool board including TOOLS / RETURN AFTER USE, bench dressing, and under-bench cases. |
| W10_GATE_APPROACH | 93 | FG01/freight threshold into the signed S03/F02 turn. |
| W11_CARRIER_ACCESS | 94 | Standing access to FC-07, straps, flange, and staged bay. |
| W12_CLEAN_TURN | 93 | S02/clean hanging sign and orange floor line through the service junction. |

## Historical evidence

F00 was rejected for the black floor overlap, competing/hidden wayfinding, weak reactor header, and sparse door leaves. F05’s broad visual pack passed, then canonical C08 failed a coplanar flange/lining strip. F06–F08 were failed or partial engineering candidates. F09 cleared visual categories but failed canonical cold C07 (overlapping first-aid bars, max 31/255) and C04 (four beam-edge pixels). F10 is the bounded correction of that cold failure.

Runtime behavior, engine controller operation, and assembled neighboring scenes remain outside this section review.
