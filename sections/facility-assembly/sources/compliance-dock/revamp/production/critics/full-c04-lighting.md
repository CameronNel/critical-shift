# Full cycle 04 — lighting and depth review

**Category 5: 90/100 — FAIL against strictly >93.** No lighting-specific critical veto. Overall 99/100 acceptance is assessed separately.

Fresh independent pixel review of all 27 current renders and all four approved spawn reference PNGs. Formal review began only after the manifest was complete and all 27 image hashes verified. The native file SHA256 independently matches `2820ac1c7a79a28d739d0b953d73b4490f264c119775eeeef37c46bf6792a7c6`. No Blender process or scene/code edit was performed.

## Assessment

A competent and readable lighting pass with useful warm/cool zoning, but not yet exceptionally resolved. The support bay is too bright on its backdrop and too dark on its lower assembly; office focus and the inspection-to-roof highlight hierarchy need refinement. The bleak institutional mood is present but broad beige fill weakens secondary-space depth.

The route remains readable in every player-facing view. The check-in has a clear warm pool, credible small-object contact shadow and restrained practical lighting. The cooler dock, dark ceiling and local cargo task light establish useful zoning. This is not dominated by flat even lighting, and important apertures remain visible.

## Highest-impact repairs

1. **Concealed support bay value hierarchy is reversed: the broad beige wall is conspicuously bright while the trolley lower frame, shelf and casters collapse toward black.** Evidence: `C08_CONCEALED_SUPPORT_H1`, `HERO_TROLLEY`, `HERO_EVIDENCE`, `CORNER_NW`, `CORNER_NE`. Reduce the existing bay practical spill on the upper wall and use a restrained, fixture-motivated grazing component over the trolley rail/canvas edge and floor contact. Keep the bay lower in total value than the inspection route; preserve readable caster, shelf and frame boundaries. Do not raise global exposure. Success: The trolley reads as a complete supported assembly against a quieter backdrop in both bay views, with storage visibly secondary to inspection.

2. **Office illumination is broad and almost uniformly warm; blank wall and floor compete with the paperwork/terminal composition.** Evidence: `C07_OFFICE_INTERIOR`, `WALL_WEST`, `CORNER_SW`, `CORNER_SE`. Tighten the existing office practical toward the desk work plane and chair; reduce broad wall/floor fill while retaining soft secondary fill beneath the desk. Preserve the warm office/cool dock distinction and present desk/chair contact shadows without losing the legs. Success: Desk, terminal and work papers become the first read; wall and door stay quieter, and the floor still explains chair support.

3. **Cool highlights on the scanner sign/header and overhead steel are more assertive than useful secondary construction response; cargo remains relatively low in value in the wide view.** Evidence: `C02_HERO_DOCK`, `HERO_SCANNER`, `HERO_CARGO`, `C10_ROOF_SERVICES`, `PLAYER_REVERSE`. Rebalance the existing inspection practical directions so the scanner columns retain edge/body separation while the cargo lip and crate receive a modest localized lift. Reduce the brightest cool ceiling/header spill; preserve the already convincing cargo lip task light and small indicators. Success: Wide inspection views establish scanner and cargo as related functional heroes without the roof/sign highlights dominating; navy housings retain material shape.

4. **Arrival gate depth relies strongly on painted value outlines; dark vertical frame/reveal components have weak light separation against the navy door.** Evidence: `C04_SCANNER_APPROACH`, `C09_ARRIVAL_GATE_P2`, `WALL_NORTH`, `PLAYER_PINCH`. Angle or soften the nearby existing arrival practical to produce a restrained cross-light across one reveal and the folded door ribs. Retain the gate darker than inspection and keep the beacon restrained; do not flood the entire rear wall. Success: Door leaf, reveal and frame can be distinguished by light response as well as colour blocking in the frontal and oblique fixed views.

All repairs must preserve current layout, source poses, footprints and apertures. Recheck the same fixed cameras after any lighting adjustment.

## Evidence and limits

Source: `sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend`; SHA256 `2820ac1c7a79a28d739d0b953d73b4490f264c119775eeeef37c46bf6792a7c6`.

Manifest: `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/manifest.json`; complete=true, 27/27 hashes verified; 1067 × 600 Cycles renders, cold_open=false.

Actually opened current PNGs:

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C01_ENTRY.png` — SHA256 `6d7b17d544b4d0ebf6a4c34e15954db5ed38a430ce8e87fcf43d1cfd3d6541d6`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C02_HERO_DOCK.png` — SHA256 `0fe05c82c4e14c3712f05fa7cef9b8b837782e0282233b9a168c97ddc1de3182`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C03_CHECKIN_COUNTER.png` — SHA256 `4937a0346bea910039a4cfb1c20d0b7fa505dfea577a1022c4160e15376ce84c`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C04_SCANNER_APPROACH.png` — SHA256 `b82b5b357fc28851e3282b93090e6a8b390b0ffc47bff484340b518d6d516896`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C05_CONVEYOR_LEAD_TUNNEL.png` — SHA256 `a7822b05471ffb3809cced8ebec4de45317366898d639fc0cdde0d1dce748e9b`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C06_CART_GATE_G1.png` — SHA256 `4524265b77befbe89fc0d28f2fbfc3ec523e6dab3a30772e34fbd0112b17db40`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C07_OFFICE_INTERIOR.png` — SHA256 `9cb75663563a5f1a7721587816e6f2265c200ec3d5f20fe7c2c490cfb0083656`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C08_CONCEALED_SUPPORT_H1.png` — SHA256 `c28d26e314071e85bf890011bfdca48770f55fc7e08603ddf3c03807ef0a665c`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C09_ARRIVAL_GATE_P2.png` — SHA256 `d9f6d597484a5d836d4a2a5c7cea5d17df18393aca0dbf88a402b542a4862c0a`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/C10_ROOF_SERVICES.png` — SHA256 `00a57e57dadf140245469bda038ad7a376185fbc514e867922344d171649fc1f`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_SW.png` — SHA256 `ed4e7eedb8b0772293940c92ce817c295823ddb6fe2e71cfbcfa4adb841ff185`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_SE.png` — SHA256 `d8a91f52102e77484c7553144db9ff74674828f1c936a69526f75b12eba0d844`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_NW.png` — SHA256 `cf71b82ef7c2af8d5ae51e9bb59e922f05a4e40450cf2bfe36ecea9fc87fa7e5`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/CORNER_NE.png` — SHA256 `fc43624ba292c9e33e7f1f2ad7a166487580c249b6dddc714ed2587f76930fa2`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_SOUTH.png` — SHA256 `f381dd37bb321d5d27d7b5252075c390fd7890c60abddcdc27b7962ba6806f84`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_NORTH.png` — SHA256 `82fcbe8725e6eb0d65bc91535e0b78de0d02202b423b1edb43af495030a1fbcb`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_EAST.png` — SHA256 `0fe08518e9fe6d82db3279449ca9afdb8b3711cffe07c178377709a2d4c67511`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_WEST.png` — SHA256 `1583d41252f423ba43cb7fe10a4c18da24f69f98b7b3c213b2655711a308005a`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_SCANNER.png` — SHA256 `52d10e1030ea3bad25acc1cf1a2cee0a3ca768dedda8f87335547862496f31ec`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_CARGO.png` — SHA256 `b2b703ac584868c81398157879be65bbdea1848a88e9eaf040d9a07ea753e57b`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_EVIDENCE.png` — SHA256 `d6361eb249efcdd67ba8d0b877d5ebabe12ee9e5d7a55d03ce668d2fe36e871a`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_TROLLEY.png` — SHA256 `d5e21462e2dfd7c5de934c4966e3ea38bbffea4c07a703c89394e853e5182d7a`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/HERO_UTILITIES.png` — SHA256 `5fde73eed84e76ae693a3b71ec358ef7b2ca069bdb770ed0c6d3612e98d5ea4c`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/DETAIL_CHECKIN.png` — SHA256 `85b1f12104f15b8c027325fc1967621bff31add41f55f2eb4a20ab759e006edd`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/PLAYER_REVERSE.png` — SHA256 `a7ce31f28343c72c86ba989ea04f3ca7345ab852a6051b299d6333a43ec4957e`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/PLAYER_PINCH.png` — SHA256 `61dee99542ebacc9ddef29196ea90bb4352a10efa24cbed07f142716e0da63b7`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/full-cycle-04/WALL_OFFICE_FRONT.png` — SHA256 `f8efa667311b4071accf8407eb060d49c64af1d0e09dc73c3b82746e4ebc228b`.

Actually opened approved spawn reference PNGs:

- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/BRIEFING_INDIRECT.png` — SHA256 `8d03448f84845b16705c6acc3324364a4e0a51f36c34355f4c481e8957aef301`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/VALIDATE_LockerDoor.png` — SHA256 `b8fd309f91cc15bfe6d183a253b81ba0f20a0033e08c63214c127e07e19879de`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/VALIDATE_Material_A.png` — SHA256 `47d3892f69b4b244bcbff32908a6445556c182b2090aba11b22be1fe274253f6`.
- `sections/facility-assembly/sources/compliance-dock/revamp/production/renders/spawn-reference/VALIDATE_Spawn.png` — SHA256 `c84f368729c7e3ae1e6f1005ff5daae39020749316545bd208c972cee5b4e9ed`.

Authorities read: `AGENTS.md`, `.agents/skills/blender-headless/SKILL.md`, `design/ART_DIRECTION.md`, `design/ART_REFERENCE_INDEX.md`, `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`, `sections/facility-assembly/sources/compliance-dock/revamp/scenery/OVERHAUL_BRIEF.md`, `sections/facility-assembly/sources/compliance-dock/revamp/production/RUBRIC.md`.

No old critics, scores, TASK_STATE, HANDOFF, author rationale or implementation code was consulted. Prior-cycle stability, cold-open equivalence, objective geometry/support contact and runtime lighting remain outside this category review.
