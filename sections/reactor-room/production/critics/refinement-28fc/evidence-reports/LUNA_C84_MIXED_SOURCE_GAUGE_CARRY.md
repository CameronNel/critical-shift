# C84 bounded carry: mixed-source gauge panels

## Finding

Issues **#16 (gauge information readability)** and **#30 (gauge housing depth)** remain accepted as a historical mixed-source visual disposition bound to C84. This is not a claim that the panels are C84 renders. All sixteen original native panels were independently inspected and accepted in [the C82 mixed-source gauge review](LUNA_C82_MIXED_SOURCE_GAUGE_ACCEPTANCE.md); this report records why that visual result still applies to the exact C84 candidate.

## Exact source chain and scoped comparison

| Save | Source SHA-256 | Relationship relevant to the gauges |
|---|---|---|
| C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | Source of 14 rendered panels listed below. |
| C80 | `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051` | Source of panels07 and08 listed below. |
| C82 | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | Intermediate reviewed candidate; exact C79→C82 and C80→C82 scoped comparisons below. |
| C84 | `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06` | Current candidate; exact C82→C84 comparison below. |

- C79→C82 `/workspace/scratch/reactor-refinement-cycle82/cumulative-c79-scene-delta.json` passes: it identifies the crane identity and six door-hardware meshes as changed, adds three crane identity support/plate objects, and leaves 1,910 objects unchanged. It compares object type, world transform, parent, render visibility, drivers/action names, mesh arrays/material indices/smoothing, text fields, material graph socket/link/driver hashes, light settings, and camera optics. It does not claim dynamic keyframe or all custom-property equivalence.
- C80→C82 `/workspace/scratch/reactor-refinement-cycle82/scene-delta.json` passes: only six door-leaf STEEL meshes changed, no objects added/removed, 1,914 unchanged. It uses the same declared comparison scope.
- C82→C84 `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json` passes: only the five named drum meshes changed (`RH refine legacy drums GALV`, `RH refine legacy drums RED`, `RH stations props GALV`, `RH stations props RED`, `RH stations props YELLOW`), 1,915 unchanged, no objects added/removed/unexpected. Its comparator additionally includes mesh edge indices and sharp flags.

Across these bounded comparisons, the gauge meshes, dials/ink/needles/retainers, related material graphs, direct-view camera objects, lighting settings and view definitions are unchanged. The five C84 drum meshes do not enter or occlude any of the sixteen gauge-panel views. This evidence supports a narrow transfer for #16 and #30; it does not transfer unrelated lighting, material-family, or whole-room judgments.

## Original image set

The original panel selection is 14 C79 images plus the two C80 panels07/08. All were rendered at native 640×360, Cycles CPU, 96 maximum/32 minimum adaptive samples, 16-bit; original manifests and review are linked above. Their image hashes and source-specific image paths are reproduced here; no image has been renamed as a C84 render.

| Panel | Original source | Source SHA-256 | Image SHA-256 | Image |
|---|---|---|---|---|
| 01_gauge_coolant_pump | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `cd0326f74d1b14fe2477a3d7269fc63d74b22639baf5fbed6be5d7d9dbd2b7a9` | [01_gauge_coolant_pump.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/01_gauge_coolant_pump.png>) |
| 02_gauge_ec_1 | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `9a34d661c44e3f87a49837b1dc634f32eaec06db9568866b9d9293a6cf51ac41` | [02_gauge_ec_1.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/02_gauge_ec_1.png>) |
| 03_gauge_ec_2 | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `03d979ecb79a6d28eb8e812366f704422dc934198c1e208405764f86c9dab49c` | [03_gauge_ec_2.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/03_gauge_ec_2.png>) |
| 04_gauge_pool_sample | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `d44957582ee131bba66c950003488dc5522cd8976700911708b4336175d848db` | [04_gauge_pool_sample.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/04_gauge_pool_sample.png>) |
| 05_gauge_turbine_left | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `a67aa775c798eb90dfe2ce2a1b880a9a9c2e8f8421f4afe5841b8c8dd781506e` | [05_gauge_turbine_left.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/05_gauge_turbine_left.png>) |
| 06_gauge_turbine_right | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `2207acb41563081e49641c84bcc9979646672eba40907969709483ad5d5c9926` | [06_gauge_turbine_right.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/06_gauge_turbine_right.png>) |
| 09_gauge_waste_cask | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `1fda5e20b5b863006e1dd0f5b9b19ae3de9ae8b1d01079bf6bfbd1ccf5c6d8f4` | [09_gauge_waste_cask.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/09_gauge_waste_cask.png>) |
| 10_gauge_coolant_chain | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `022a462d8a700c50c3911b52e14b251247fe1022e8a5b9b2af44c77ef85c4922` | [10_gauge_coolant_chain.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/10_gauge_coolant_chain.png>) |
| 11_gauge_ec_1_injection | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `32dcbfaafdb30d486d8af788b65cc779927680bf9785d46deb4d40df1f084db8` | [11_gauge_ec_1_injection.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/11_gauge_ec_1_injection.png>) |
| 12_gauge_ec_2_injection | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `335987c62076c781b1315422f0652104312b3e7518583b7864b727d85d4c69fe` | [12_gauge_ec_2_injection.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/12_gauge_ec_2_injection.png>) |
| 13_gauge_pump_discharge | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `71d12acbe4c283c8191ab5cde6f67296ee9871d8cd1ec9e533bd90b245dd6261` | [13_gauge_pump_discharge.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/13_gauge_pump_discharge.png>) |
| 14_gauge_steam_supply | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `166d3b67265beff7e2c926e3f9cc8311bb570691f4619f094174c325602194ed` | [14_gauge_steam_supply.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/14_gauge_steam_supply.png>) |
| 15_gauge_waste_vent | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `2559b9d22033f964301abfff585697878a1f0721edcf43669e1ae012eccec472` | [15_gauge_waste_vent.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/15_gauge_waste_vent.png>) |
| 16_gauge_fire_main | C79 | `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` | `6a5cfd9c71c66cb360789ce09ca03332bd8cf4580ee2a95de845a0a902d4255c` | [16_gauge_fire_main.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79/gauge-sheet/16_gauge_fire_main.png>) |
| 07_gauge_turbine_oil | C80 | `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051` | `2c8fea4b9d33fb42b938a0789b415d6eafb5916d5d595bfb29781746c5d076cb` | [07_gauge_turbine_oil.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/gauge-sheet/07_gauge_turbine_oil.png>) |
| 08_gauge_steam_riser | C80 | `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051` | `93f1d7b66346703d392ac0f90fdd16c77d2e3ab00ba5a99093ac61279efa5ea1` | [08_gauge_steam_riser.png](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/gauge-sheet/08_gauge_steam_riser.png>) |

## Limits

The original C82 panel review found panels01 and13 marginal but legible at native size; they are not represented as ideal illumination. This carry does not establish all ten fresh C84 main views, does not set an overall/area score, and does not claim all-scene mesh equivalence.
