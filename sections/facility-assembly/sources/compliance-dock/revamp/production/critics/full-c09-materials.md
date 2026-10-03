# Compliance dock C09 — materials and colour review

Independent scoped review of categories 4 and 6. All 35 current originals and four approved spawn originals were individually opened after the ALL35 READY signal. No contact sheet replaced those openings. Previous reports, source recipe contents, builder reasoning and other critic scores were not consulted.

| Category | Score | Exact deductions | >93 gate |
|---|---:|---|---|
| 4. Tactile material identity and UV/texture discipline | **95.5/100** | 1.5 + 2.0 + 1.0 | Pass |
| 6. Approved spawn colour coherence and restrained accents | **99.0/100** | 1.0 | Pass |

These are two independent category scores, not an overall score or full-room acceptance. The overall 99 gate remains for the full review. No critical material/colour defect or dominant visual veto was observed within this remit.

## Material findings

Painted steel, controlled bare-metal highlights, matte plaster, flexible dark tunnel curtains, cream cloth/paper and rubber wheels are visibly separated. The room does not have a dominant glossy plastic response. Broad quiet wall and floor surfaces are appropriate and do not need indiscriminate noise. Cloth folds, folded counter textiles, utility conduit and restrained handle wear provide tactile detail.

The remaining deductions are localized:

### C09-MAT-001 — Textile weave is too fine for the inspection view

Category 4, **−1.5**, minor; critical: no; veto: no; confidence: high.

At original 1067x600 resolution the cream trolley skirt and close folded textile carry a very fine repeating diagonal/grid pattern. In C08 and the foreground of HERO_EVIDENCE the frequency becomes a visible shimmer-like banding pattern over the broad cloth mass. This is a still-image frequency concern; temporal shimmer is not tested. The broad cloth folds and matte response are otherwise convincing.

Evidence: `full-cycle-09/C08_CONCEALED_SUPPORT_H1.png`, `full-cycle-09/HERO_EVIDENCE.png`, `full-cycle-09/HERO_TROLLEY.png`, `full-cycle-09/DETAIL_CHECKIN.png`.

Concrete regions (original pixels): C08_CONCEALED_SUPPORT_H1 [435, 370, 1050, 586] — Broad cream hanging skirt under the four dark straps.; HERO_EVIDENCE [0, 343, 517, 592] — Near foreground cream cloth.; DETAIL_CHECKIN [231, 480, 456, 570] — Folded textile stack in front of the paper tray..

Repair: Reduce weave contrast and high-frequency bump, or filter the weave so broad folds and seam/hem thickness dominate these same cameras. Preserve the cream cloth colour and matte response.

### C09-MAT-002 — Office glazing has a generalized milky finish

Category 4, **−2.0**, minor; critical: no; veto: no; confidence: medium.

The large office panes read as a consistently diffuse, pale veil with broadly blurred forms behind them. It clearly reads as glazing, but the uniformly milky area suppresses the subtle reflective/transmissive variation that would make this conspicuous architectural material feel more deliberately finished. This is a limited craft deduction, not a claim that privacy glass is forbidden. The neutral image changes the balance of reflections/transmission, so no shader roughness value or defect cause is inferred.

Evidence: `full-cycle-09/C03_CHECKIN_COUNTER.png`, `full-cycle-09/C07_OFFICE_INTERIOR.png`, `full-cycle-09/C01_ENTRY.png`, `full-cycle-09/PLAYER_REVERSE.png`.

Concrete regions (original pixels): C07_OFFICE_INTERIOR [561, 0, 1067, 254] — Office panes over the desktop, especially large central pane.; C03_CHECKIN_COUNTER [623, 174, 973, 460] — Receding glazed office side wall..

Repair: Retain believable privacy if intended, while balancing haze, broad reflection and transmission so the panes show deliberate material variation rather than a uniform blur. Recheck both directions at the fixed beauty camera exposure.

### C09-MAT-003 — Paired cabinet handle wear repeats as cloudy strips

Category 4, **−1.0**, minor; critical: no; veto: no; confidence: high.

The two blue cabinet doors show nearly matching cloudy vertical wear concentrated around their handles. Localization is appropriate, but the matching placement and similar soft mottling make the pair feel patterned rather than separately used. Bare-metal conduit and pale electrical housings remain clearly differentiated; this is not a blanket anti-plastic defect.

Evidence: `full-cycle-09/HERO_UTILITIES.png`, `full-cycle-09-neutral/HERO_UTILITIES.png`, `full-cycle-09/WALL_NORTH.png`.

Concrete regions (original pixels): HERO_UTILITIES [32, 365, 265, 512] — Two blue cabinet handle regions at left..

Repair: Keep the same restrained palette and wear area, but vary the two contact masks and combine broad faded paint with one or two clearer local handle scuffs. Avoid adding photographic grunge across the doors.

### C09-COL-001 — North arrival apron is an unusually strong saturated field

Category 6, **−1.0**, minor; critical: no; veto: no; confidence: high.

The safety apron occupies a large, nearly unbroken saturated yellow foreground field in PLAYER_PINCH. Its purpose is legible, yet its colour weight outweighs the nearby muted gate and service props more strongly than the restrained accent balance elsewhere. The defect is slight because the yellow is functional and the room overall remains calm and coherent.

Evidence: `full-cycle-09/PLAYER_PINCH.png`, `full-cycle-09/CORNER_SE.png`, `full-cycle-09/CORNER_SW.png`.

Concrete regions (original pixels): PLAYER_PINCH [382, 444, 655, 600] — Large unbroken yellow floor apron surrounding the drain in foreground..

Repair: Retain the footprint, hazard role and legibility, but slightly reduce yellow chroma/value or add restrained broad wear variation so this field sits with the existing muted industrial palette. Do not move preserved interfaces or repaint the whole floor.

## Spawn colour comparison

The dock preserves the rose/off-white upper walls, charcoal/navy lower zone, blue-grey equipment, burnt-orange doors/signs/cargo case and cream paperwork present in the approved spawn images. Useful yellow lanes and small red/green controls remain isolated. The industrial dock can use more grey and less domestic timber than briefing; the brief permits a darker coercive mood. Neither difference is treated as a defect. The northern yellow apron is a small local accent-weight issue, not a colour-confetti veto.

## UV evidence and limits

The four checker originals show broad coverage on exposed machine/case fronts, sides and tops; trolley cloth and visible hem; electrical housings; office furniture; and visible tubular/wheel surfaces. Broad drape checks remain legible and follow folds. No conspicuous gross UV distortion or visible missing checker was established on those exposed surfaces.

Checker size differences across perspective, differently oriented surfaces and thin cylinders do **not** establish unequal physical world density. Numerical UV/world-area density, hidden faces/caps, UV overlap policy and topology were not measured or certified. Temporal shimmer is not tested; the textile concern is visible high-frequency patterning in still originals. Neutral-mode internal recipe contents were not read, so these images do not establish measured shader roughness or physical reflectance.

## Provenance and image audit

The companion `full-c09-materials-imageaudit.json` records each of 39 individually opened originals, its actual decoded size and SHA256, and the exact three current manifest sets (27 + 4 + 4). All current files fully decode to **1067 × 600** and match their manifest PNG hashes. All four reference originals fully decode to **1280 × 720** and match `reference-provenance.json`. Historic original reference paths are recorded as supplied provenance, not a fresh native capture.

The actual frozen native SHA256 is `6838d604ac4586da057a652e98e9c694f754a84e9f38ba70b83f1046e9ae6e9a`; renderer SHA256 is `38d50f5ec2f64755c9f1f2fe35d4e46e98f74dc71c3df327c9d32a18012e28ce`. Both independently match all three manifests. The four current recipe paths were inspected by hash only. No native scene was loaded, authored or saved; no recipe or render source was modified.

This review does not certify topology, support contact, technical cleanliness, engine performance, collision/navigation, Unity equivalence, cold-open reproducibility or final two-cycle stability. Those require their own evidence.

## Release

All PIL readers are closed. No Blender/native process or persistent reader was started. No owned render job or reader remains at handoff. Only the three assigned C09 materials critic outputs were written.
