# Full cycle 04 — spatial and functional composition review

Source: `sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend`; SHA-256 `2820ac1c7a79a28d739d0b953d73b4490f264c119775eeeef37c46bf6792a7c6`.

Fresh read-only critic. No prior scores/critics, author rationale, TASK_STATE/HANDOFF or builder code read. No native process run. Formal review began only after the manifest was complete with 27 shots and every image hash matched. All 27 current images and all four spawn references were actually opened.

| Category | Score /100 | Strict >93 |
|---|---:|---|
| 1 — Scale, layout and route readability | 95 | Pass |
| 3 — Inspection/check-in hierarchy and functional composition | 92 | **Fail** |

The assigned-category gate fails on category 3. The two-category mean is 93.5 and cannot hide that failure. The owner 99 overall gate is outside this review.

## Score reasons

The layout has believable human proportions, distinct worker and cargo lanes, useful quiet floor area and coherent office/support zoning. All four cutaways support this spatial reading. The bypass is clearly closed; it is not mistaken for an open route. No critical spatial obstruction is demonstrated in the current pixels. Category 1 loses five points mainly for check-in branch discoverability and overlapping route/focal cues.

The scanner and conveyor read as inspection equipment before reading text. The check-in countertop is a strong local cluster of transaction objects, and secondary storage/services stay subdued. Category 3 loses eight points because the check-in hatch disappears from the entry/wide functional read, scanner/arrival/roof line language overlaps, and the cargo operator point is partly buried behind the bypass post. The hatch quality in C03 and DETAIL_CHECKIN does not resolve its first-arrival discoverability.

## Repair targets

### 1. Make the off-axis check-in discoverable on first arrival

Evidence: C01_ENTRY, C02_HERO_DOCK, CORNER_NW, WALL_OFFICE_FRONT, VALIDATE_Spawn.png.

In the entry/wide views the left office reads mainly as glazing. The locally strong hatch is around the front face and contributes almost nothing to the first functional read. The orange scanner header and main lane visually imply inspection is the first destination.

Preserve the hatch, office wall and all object poses. Add one restrained perpendicular check-in locator at the existing office corner, or an equally concise physical station cue aligned with the existing side branch. Use a modest practical pool/reveal to connect that cue to the hatch. Avoid another large title panel or repeated text.

Verify: C01 and C02 should identify both the worker inspection destination and the check-in branch at a glance; C03, DETAIL_CHECKIN and WALL_OFFICE_FRONT must retain their local clarity.

### 2. Separate the worker arch from the arrival-door and ceiling backdrop

Evidence: C01_ENTRY, C02_HERO_DOCK, C04_SCANNER_APPROACH, HERO_SCANNER, C10_ROOF_SERVICES.

Scanner uprights, arrival door framing and ceiling crossings share dark navy/grey values. The orange scanner header and orange arrival header form competing stacked bands. The opening is readable, but hierarchy relies heavily on its title panel.

Keep native shapes/poses, openings and roof structure fixed. Tune local light direction and broad value separation so the scanner front edges/inner return are distinct from the dimmer arrival backdrop. Reduce conspicuous ceiling highlights directly behind its crown rather than adding emissive trim or decorative geometry.

Verify: Same fixed cameras should retain one immediate worker-arch silhouette while the arrival gate remains readable as the secondary endpoint.

### 3. Clarify the cargo operator point within the existing footprint

Evidence: C02_HERO_DOCK, C05_CONVEYOR_LEAD_TUNNEL, HERO_CARGO.

The orange crate and lit tunnel mouth identify the inspection process, but the smaller side operator controls sit behind the closed-bypass post and low-contrast housing. The machine reads more as a conveyor destination than a staffed examination point.

Preserve crate, gate, conveyor and operator-control poses. Use restrained local illumination and material/value separation on the control face and supporting arm; clarify its screen/control face hierarchy without adding another screen, large sign or moving the apparatus.

Verify: C02 and HERO_CARGO should reveal the operator point as a coherent subordinate function, without making it brighter than the tunnel mouth or worker arch.

## Critical defects and limits

No critical visual blocker is established in the assigned spatial/composition scope. The strict composition quality threshold still fails. These scores concern authored visual quality, not runtime collision, navigation or interactivity. Exact player/cart clearances, support contacts and geometry require separate evidence. This manifest has `cold_open=false`; no cold-open pass or last-two-cycle stability claim is made. All room boundaries, apertures, original object poses and layout must remain fixed during repairs.

## Inspected files and hashes

Every image below was opened through the image-viewing tool. Spawn provenance hashes also matched.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C01_ENTRY.png` — `6d7b17d544b4d0ebf6a4c34e15954db5ed38a430ce8e87fcf43d1cfd3d6541d6`
  Worker arch and closed cart lane read immediately. Check-in hatch is outside the visible frontal composition; office glazing gives little evidence of the required first service point.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C02_HERO_DOCK.png` — `0fe05c82c4e14c3712f05fa7cef9b8b837782e0282233b9a168c97ddc1de3182`
  Strong worker/cargo split and open approach. Crate and gate post dominate the cargo control-side silhouette. Check-in remains absent from the main functional composition.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C03_CHECKIN_COUNTER.png` — `4937a0346bea910039a4cfb1c20d0b7fa505dfea577a1022c4160e15376ce84c`
  Locally clear staffed transaction point: counter, grille, document tray and stamp form a coherent human-scale cluster. This clarity does not carry into the entry view.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C04_SCANNER_APPROACH.png` — `b82b5b357fc28851e3282b93090e6a8b390b0ffc47bff484340b518d6d516896`
  Unambiguous opening and threshold plate; route continues through the arch. Door ribs share navy/grey value language with the scanner behind it.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C05_CONVEYOR_LEAD_TUNNEL.png` — `a7822b05471ffb3809cced8ebec4de45317366898d639fc0cdde0d1dce748e9b`
  Conveyor, crate and curtain convey cargo inspection clearly. Operator housing is partly hidden by the near gate post and equipment body.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C06_CART_GATE_G1.png` — `4524265b77befbe89fc0d28f2fbfc3ec523e6dab3a30772e34fbd0112b17db40`
  Closed bypass is visibly closed, rather than falsely presented as a clear path. Rail and sliding leaves read as manufactured controls of a reserved cargo lane.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C07_OFFICE_INTERIOR.png` — `9cb75663563a5f1a7721587816e6f2265c200ec3d5f20fe7c2c490cfb0083656`
  Plausible desk, chair and staff door relationships with generous visual space. No visible furniture obstruction of the office door.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C08_CONCEALED_SUPPORT_H1.png` — `c28d26e314071e85bf890011bfdca48770f55fc7e08603ddf3c03807ef0a665c`
  Trolley is recognizable as a covered transfer assembly; screen and bay provide the secondary concealed function. This is a secondary pocket, not a route focal point.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C09_ARRIVAL_GATE_P2.png` — `d9f6d597484a5d836d4a2a5c7cea5d17df18393aca0dbf88a402b542a4862c0a`
  Major endpoint is legible. Its large dark/navy rib pattern and orange header also create the strong backdrop that competes with the smaller scanner.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C10_ROOF_SERVICES.png` — `00a57e57dadf140245469bda038ad7a376185fbc514e867922344d171649fc1f`
  Believable vertical scale cue and overhead construction. Bright structural crossings over the arch increase competing visual lines in the main inspection composition.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_SW.png` — `ed4e7eedb8b0772293940c92ce817c295823ddb6fe2e71cfbcfa4adb841ff185`
  Main approach and separate front check-in branch are visible from above. Counter occupies a sensible front corner; large central clearance is preserved.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_SE.png` — `d8a91f52102e77484c7553144db9ff74674828f1c936a69526f75b12eba0d844`
  Worker arch and cart bypass divide the same main approach without a prop obstacle in the open floor. Support bay remains secondary.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_NW.png` — `cf71b82ef7c2af8d5ae51e9bb59e922f05a4e40450cf2bfe36ecea9fc87fa7e5`
  Entry aperture, office hatch and inspection cluster relationship is clear in cutaway; hatch is around the side of the entry sightline.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_NE.png` — `fc43624ba292c9e33e7f1f2ad7a166487580c249b6dddc714ed2587f76930fa2`
  Open entry region and separate office/support pockets confirm quiet space and distinct functional zoning. Layout itself is not the discoverability defect.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_SOUTH.png` — `f381dd37bb321d5d27d7b5252075c390fd7890c60abddcdc27b7962ba6806f84`
  Entry aperture reads against a quiet wall; one poster avoids visual crowding. Dark aperture is an endpoint, not a demonstrated collision failure.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_NORTH.png` — `82fcbe8725e6eb0d65bc91535e0b78de0d02202b423b1edb43af495030a1fbcb`
  Arrival gate dominates a restrained elevation; secondary storage/cabinets do not obstruct it.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_EAST.png` — `0fe08518e9fe6d82db3279449ca9afdb8b3711cffe07c178377709a2d4c67511`
  Utilities are a contained secondary cluster. Large quiet bays preserve hierarchy.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_WEST.png` — `1583d41252f423ba43cb7fe10a4c18da24f69f98b7b3c213b2655711a308005a`
  Office/support separation is visually coherent; privacy screen occupies the intended secondary bay.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_SCANNER.png` — `52d10e1030ea3bad25acc1cf1a2cee0a3ca768dedda8f87335547862496f31ec`
  Arch has believable human scale and clear threshold; overlapping arrival-door ribs and ceiling members reduce isolated silhouette clarity.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_CARGO.png` — `b2b703ac584868c81398157879be65bbdea1848a88e9eaf040d9a07ea753e57b`
  Machine mouth, rollers and sealed crate are readable. Operator control housing is partly obscured and comparatively low contrast.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_EVIDENCE.png` — `d6361eb249efcdd67ba8d0b877d5ebabe12ee9e5d7a55d03ce668d2fe36e871a`
  Storage doors are readable and distinct from the trolley. Partial foreground trolley overlap is consistent with the pocket arrangement; no evidence of physical intersection is asserted.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_TROLLEY.png` — `d5e21462e2dfd7c5de934c4966e3ea38bbffea4c07a703c89394e853e5182d7a`
  Complete silhouette identifies a covered wheeled transfer unit; bay composition stays dim and subordinate.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_UTILITIES.png` — `5fde73eed84e76ae693a3b71ec358ef7b2ca069bdb770ed0c6d3612e98d5ea4c`
  Secondary utility identity is clear. Cabinet colours/status controls share some inspection vocabulary but remain away from the main approach.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/DETAIL_CHECKIN.png` — `85b1f12104f15b8c027325fc1967621bff31add41f55f2eb4a20ab759e006edd`
  Strong functional counter composition with bounded documents, tray, tether and stamp. Specific working objects support the transaction identity.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/PLAYER_REVERSE.png` — `a7ce31f28343c72c86ba989ea04f3ca7345ab852a6051b299d6333a43ec4957e`
  Worker opening remains legible from the rear. Cart lane closure is obvious; orange staff door and glazing offer a clearer office read than the entry approach.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/PLAYER_PINCH.png` — `61dee99542ebacc9ddef29196ea90bb4352a10efa24cbed07f142716e0da63b7`
  North return visually remains open between arrival gate, screen edge and equipment. Exact collision/body clearance cannot be established from this perspective.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_OFFICE_FRONT.png` — `f8efa667311b4071accf8407eb060d49c64af1d0e09dc73c3b82746e4ebc228b`
  Frontal hatch reads well under its practical. Orange staff door is visually stronger than the smaller hatch; header names institutional reassurance rather than identifying check-in at distance.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/BRIEFING_INDIRECT.png` — `8d03448f84845b16705c6acc3324364a4e0a51f36c34355f4c481e8957aef301`
  A quiet central hero screen is immediately readable; supporting props are clustered at one side. This supports focal hierarchy rather than uniform density.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/VALIDATE_LockerDoor.png` — `b8fd309f91cc15bfe6d183a253b81ba0f20a0033e08c63214c127e07e19879de`
  Bench/locker rows frame a clear central destination and open lane. Multiple functions remain recognizable before reading labels.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/VALIDATE_Material_A.png` — `47d3892f69b4b244bcbff32908a6445556c182b2090aba11b22be1fe274253f6`
  Specific locker construction and sparse personal effects support authored object identity without forcing every surface to become focal.

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/VALIDATE_Spawn.png` — `c84f368729c7e3ae1e6f1005ff5daae39020749316545bd208c972cee5b4e9ed`
  Clear main airlock destination with restrained, physically related branching-room identifiers. An off-axis room function is discoverable from the main approach.

Authority and manifest hashes are recorded in the companion JSON. Only `full-c04-spatial.json` and `full-c04-spatial.md` were written by this critic.
