# Astra interface recheck — 10 September 2026

**Result: P01 is stale at the refinery seam and in reactor payload dimensions. The reactor architectural seam remains source-consistent with P01. No assembled or runtime passage approval is earned.**

Read-only audit completed at approximately 19:26 UTC / 21:26 SAST. Author: `/root/astra_reviewer`; independent refinery source check: `/root/astra_reviewer/refinery_source_recheck`. Only this report was written. No adjacent source, scene or live Blender session was changed; no Blender process or GPU render was run. Coordinates below are measurements/derivations from existing source, not instructions to relocate adjacent rooms.

## Scope and authority

Compared this section's `interface.json` revision P01 and `architecture/CONNECTION_CONTRACTS.md` with the current adjacent source pipelines and stored evidence.

- **RF:** `C:/Users/Camer/Games/critical-shift/worktrees/refinery-compact/sections/refinery/`
- **RR:** `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/sections/reactor-room/`

Source expressions, stored measurements, and current saved-file hashes are distinguished below. Current saved scenes were hashed but not opened/evaluated by this audit. Their stored reports are evidence with the stated limitations, not fresh independent clearance measurements.

### Current provenance

| Authority | Verified current identity / limitation |
|---|---|
| RF authoritative saved scene | `blender/Refinery.blend` SHA256 `7d62a7e609f2abae566f6be364e8a284176e12a722739f780083cb3b91e02cd2`; matches `production/layout_spacing050_manifest.json` and hash-bound `cold_start_spacing050.json`. Latest completed layout is spacing050. |
| RF newer source | `blender/build_refinery.py` SHA256 `645cea921aa6005f138e0ca1f9f1099d30f1c060a35b5677c0ef4956881308ca`; differs from the spacing050 manifest's build source. It now applies cobalt additions after layout/spacing. `Refinery_cobalt_candidate.blend` exists, but cobalt reviews remain in progress and no corresponding completed geometry/cold-start report was found. |
| RR authoritative saved scene | `blender/reactor_scene.blend` SHA256 `5c62f8f6fbe66322148aec53c9f272d40ca5c6ad13223961465c6bfc86714f52`; matches the active palette-amber-02 record. `production/WALL_ACTIVE.md` and `PALETTE_STATUS.md` supersede older TASK_STATE history. |
| RR current factory helper source | `blender/build_scene.py` SHA256 `b4dd705e17c1544f63085dc010e98b96390b4aeadaf73d34d6656a37a6e9160b`. P01's `9c2d57...` art-08 source is historical. The active scene includes later incremental machinery and palette passes; this factory file alone is not current-scene reproduction authority. |

RR's current palette documentation explicitly says all teal/cyan was removed in favor of white, neutral gunmetal, orange and amber energy. This supersedes its earlier A05/cyan saved-scene state. This report does not perform visual scoring or reinterpret the user's reference choice; it flags the changed adjacent authority for the builder.

## 1. Refinery architectural interfaces: positions changed

RF `blender/config.py:7–14` defines `S = sqrt(1.15)`, `DX = 7*(S-1) = 0.506663706334526`, `DY = 6*(S-1) = 0.434283176858165`. `build_refinery.py:40,53–54` applies the original modules followed by expansion, spacing and newer art. `layout_expansion.py:102–103,120–122,169–171` moves physical portals and route markers; `spacing_adjustment.py:24–27` excludes route markers from later station movement.

| Port | P01 threshold | Current source-derived threshold | Current external seam |
|---|---|---|---|
| REACTOR / corridor F01 | `(7,-3.65,0)` | `(7.506663706,-4.084283177,0)` | `(8.606663706,-4.084283177,0)` |
| MINE | `(-7,-3.65,0)` | `(-7.506663706,-4.084283177,0)` | `(-8.606663706,-4.084283177,0)` |
| ENTRY | `(-1.8,-6,0)` | `(-1.8,-6.434283177,0)` | No long external sill |

Stored RF `production/machine_manifest.json:107–111` corroborates the REACTOR marker at `(7.506663799,-4.084283352,0)` within float precision. The F01 seam displacement from P01 is **`(+0.506663706,-0.434283177,0)`**.

The independent F01 mapping keeps rotation **−90°**, but its source-consistent translation is now **`(8.606663706,-4.084283177,0)`**. This is a corrected local alignment equation, not proof of a global three-module fit. P01's `F01_REFINERY.adjacent_source_local_face`, refinery threshold/seam values, and F01 matrix translation no longer describe the current source.

**Unchanged construction:** RF `architecture.py:54–56,63–87` retains REACTOR/MINE nominal **2.60 × 3.00 m**, ENTRY **2.40 × 2.60 m**, side sill **1.10 m**, floor **Z0**, lintel underside **Z3.00**, soffit underside **Z3.01**. The moved REACTOR sill occupies X **7.506663706..8.606663706**, Y **−5.384283177..−2.784283177**. Bollard inner faces are Y **−5.329283177 / −2.839283177**, leaving **2.49 m** below **Z1.04**. Expansion translates these components without resizing them.

The room plan is now source-derived **15.013327413 × 12.868566354 m**, **193.2 m²**, with **2.80 m** central aisle (`config.py:7–14`). P01's reference to the old **2.20 m** central route is historical.

## 2. Reactor architectural interfaces: seam dimensions unchanged

RR `build_scene.py:72–79` defines the local transform, `:755` the same octagon, `:897–923` the port/stub construction, and `:934–937` the opening definitions. The current incremental machinery sources operate on machinery groups; their reviewed scope preserves main architecture. The palette-amber-02 audit reports all **13,044** objects' geometry unchanged, signature `96a85d1f2cbf2dbc26a05f5a1bb9271697776895434006f4a9f91e22c440a135` before and after palette work.

| Reactor item | P01 | Current source-derived result |
|---|---|---|
| FUEL HANDLING threshold / normal | `(0,10.8,0)` / `+Y` | Unchanged |
| Nominal width × height | `5.00 × 5.00 m` | Unchanged |
| Stub ownership / outer seam | `3.70 m` / `(0,14.5,0)` | Unchanged |
| Stub finished floor | `Z0` | Unchanged; floor center Z−.16, thickness .32 |
| Throat bumper width | `4.98 m` below Z1.35 | Unchanged source-derived minimum |
| Central headlight underside | `Z4.85` | Unchanged |
| Closed slab Y bounds | `14.39..14.49` | Unchanged |
| Main visible leaf Y bounds | `14.33..14.39` | Unchanged |
| F02 independent mapping | Z rotation180°, translation `(14.2,38.5,0)` | Still maps corridor F02 to the source seam |

Current door dressing includes formed infills, stiffeners and meeting strips (`:913–919`); the latter reach Y **14.253** on their hall-facing side. These details are inside the existing stub and do not move the outer seam. P01's slab/leaf ranges must not be read as the bounds of every door detail.

The distant fuel closure is still static source geometry. No fuel-portal opening animation/controller was found in the inspected pipeline. Other animated reactor gates/doors are different objects. **The authored fuel-link passage therefore remains blocked; no opening-state approval is implied.**

Other P01 architectural values also remain source-consistent: MAIN ACCESS threshold `(-10.8,0,0)`, **6×5.5 m**, outer seam `(-14.5,0,0)`; COOLING PLANT threshold `(8.4,-8.4,0)`, **5×5 m**, outer seam approximately `(11.016295,-11.016295,0)`; CONTROL ACCESS `(10.8,3.6,0)`, **4×5 m**, with its dedicated vestibule instead of an external stub. These are source checks, not fresh evaluated-bound measurements.

## 3. Reactor fuel payload: replacement geometry, different envelope

P01's **1.95 m body / Ø.46 body / Ø.52 closure** derives from historical factory equipment. The active incremental pipeline replaced it. RR `production/build_machinery_flow.py:32` erases inventory groups01/02/03/08/19; `:35–40` constructs the same new cartridge for receiving, storage and the fuel cart. The later wall passes retain payload sizes.

| Property | Current source | Change from P01 envelope |
|---|---|---|
| Sealed body | **1.18 m long × Ø.310 m** | Body length −.77 m; body diameter −.15 m |
| Closures | Centers ±.605 m along axis; thickness .035 m; **Ø.340 m** | Closure diameter −.18 m |
| Complete payload | **1.245 m long × Ø.340 m maximum** | Overall length −.705 m relative to P01's 1.95 m; maximum diameter −.18 m |
| Orange bands | Ø.314 m, .065 m axial width | Within closure diameter |
| Receiving / storage / cart count | 3 / 6 / 2 | One shared payload family inside the reactor |

The length derivation is `2*.605 + .035 = 1.245`. `machinery-flow-08/player-probes.json:656–699` independently stored evaluated body lengths **1.1799999475 m** for all eleven new payloads. Those probes predate later rigid relocations; the subsequent A/F source explicitly preserves cartridge size.

**Current placement and saddles, reactor-local:** `build_wall_machinery_A.py:15–26` changes receiving/storage orientation and packs their centers while preserving each payload/cradle/saddle size. Receiving centers are X **−3.804, −3.43, −3.056**, Y **9.73**, Z **1.10**. Storage centers are X **−5.105, −4.72, −4.335**, Y **9.73**, Z **.64 / 1.64**. Cartridge axes are along reactor Y. Two saddle stations remain at **±.43 m along each cartridge axis**, **.86 m separation**, from `build_machinery_flow.py:41–43,51–53,63–67`.

The two-payload cart from `build_machinery_flow.py:115–129,161–167` is moved rigidly by `build_wall_machinery_F.py:13–15` to frame **`(-9,7.45,0)`, Z rotation45°**. Its payload centers are cart-local **`(0,±.19,.66)`**; cradles are local **`(±.43,±.19,.46)`**, source size **`.18×.34×.08 m`**. Payload world centers are approximately **`(-8.865650,7.315650,.66)`** and **`(-9.134350,7.584350,.66)`**. Stored evaluated complete cart envelope is **1.245000780 × .842000484 × 1.132677674 m** in its local frame (`player-probes.json:651–655`). F02–F04 adjust dock/sample details rather than resizing the cart or payloads.

The old “sample caddy” cited by P01 is historical: inventory19 was replaced by this genuine two-cartridge fuel cart. This does not mean the corridor must copy that cart. Its **2.20×.90×1.30 m** carrier may remain an explicitly original design allowance, but can no longer be described as required by the current reactor's old 1.95×Ø.52 payload. Compatibility of any new cradle with the current payload remains an authored/source and support-contact question.

## 4. Refinery fuel / trolley and process compatibility

RF's base trolley deck remains **world X.80 × Y1.20 m**, handle top approximately **Z1.155** (`machines.py:215–220,319–337`). After expansion/spacing, its map is `(a,b,z) → (5.856663706+b,-5.384283177-a,z)`. The stored pivot agrees to float precision; parenting preserves world coordinates, so pivot Z.20 does not add .20 m to geometry height.

Base refinery fuel is still **Ø.170 casing, Ø.184 retention bands, .480 m length**, six units. Newer, not yet equivalently validated cobalt source adds retention locks (`cobalt_art.py:363–371`): nominal opposing source-box span **.196 m**, not a proved evaluated circumdiameter. Thus Ø.184 describes the base/spacing save, not the complete newest source payload. Cobalt also adds caster forks/hubs/pedals (`:401–420`); no complete updated trolley envelope is supplied.

**Cross-department process equivalence remains unresolved.** Refinery's .480 m units and reactor's new 1.245 m cartridges are still different authored objects. No packing/conversion/assembly/ownership contract or loading interaction was found. Reactor-internal cartridge consistency does not establish refinery-to-reactor interchange.

## 5. Validation gaps that remain

1. **No combined assembly proof.** F01/F02 are separate local mappings. Authoritative shared room poses, sill/stub overlap, collision, floor join and cross-section navigation remain unverified. The refinery translation correction does not authorize moving its room.
2. **Refinery ray evidence is narrow.** Hash-bound `cold_start_spacing050.json:3319–3325,3672–3674` passes 104 rays and fresh reopen. `validate.py:141–154` samples offsets −1.19..+1.19, heights Z.18..2.20, and only .64 m-long rays. It does not prove the full 2.60×3 opening, the complete 1.10 m sill, floor-level transport or a cart sweep. Local mechanical interface/standing-route audits are separate from freight passage.
3. **Reactor fuel doors remain a physical barrier.** RR's old art-08 “pass/cold_start” source reference is stale. Newer machinery player probes are static, use small body/cart proxies, and include a fuel corridor region only to Y12 (`check_machinery_walk.py:65–74`), before the distant closure at Y14.39. They do not establish passage to F02. Later machinery moves also require their own current-route evidence.
4. **Current source/save divergence matters.** RF cobalt is newer than its hash-bound spacing save. RR factory source alone predates current incremental machinery/palette authority. Neither old factory validation should be presented as validating today's entire source pipeline.
5. **Travel remains an estimate.** Corridor 38.2 m, sill 1.1 m and reactor stub 3.7 m retain the P01 path-length assumptions. At 1.5 m/s that remains 25.47 s connector-only / 28.67 s including owned sill+stub, excluding interior legs, turns, closed doors and handling. No runtime timing verifies the 15–30 s target.
6. **External service destinations remain reservations.** S01/S02/S03 have no newly verified destination seam/level/clearance in this bounded refinery/reactor audit. No mine geometry, lift, decline or room was modified or newly certified.

No visual category scores or technical acceptance score are assigned by this interface audit. The concrete P01 corrections are the refinery seam/alignment, refinery route provenance, reactor payload/sample-cart provenance, and both neighbors' validation/source identities. Existing unverified-state caveats must remain explicit.

### Additional reproducibility hashes

- RF `architecture.py`: `8e10a96054ffebc1265bca9980e3100c21a0b3ea78992408f120d2903d34f9de`
- RF `machines.py`: `434d0a1ba1ad7947f8a0291f5a0dfdf9739be07b941cf00dfd4aea0eda5de8aa`
- RF `layout_expansion.py`: `59d6d50b289e1c39ec556527725a18cc42ee4c1b1851632daff4b87904712e20`
- RF `spacing_adjustment.py`: `739768dce45b2cbe1af5e6621acb3826bd5bcb2788438b48957da64c53e97de6`
- RF `cobalt_art.py`: `5c2ab74e548eec672a424e32de814eeec7dc0696f095cc7168bf57470130f1f1`
- RR `build_machinery_flow.py`: `2c18168ff9c8e6d35c4d73bb8d3f32f5036f4bb57d02f3047cba39c42acb98e6`
- RR `build_wall_machinery_A.py`: `55b73fe46552c8b64e13196428a0489b76a6e092a3bce8b997ea6fa2d6419288`
- RR `build_wall_machinery_F.py`: `1e76272ca0a492510028d7c66d888b0607f58a2590ceca6fdb6f57e3e8e124c6`
