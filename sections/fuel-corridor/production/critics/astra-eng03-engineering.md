# Astra independent engineering audit — eng03 / frozen P07 interface

Date: 2026-09-11. **Targeted acceptance: FAIL.** The previous opposing-roller, pipe-routing and seam-shoulder defects are resolved in the evaluated save. New physical details introduce a nominal reactor-approach obstruction, an unsupported guide and several fixture/wall intersections. No visual score or full-scene art-cycle credit is assigned to this geometry-only checkpoint.

Frozen authority: `production/checkpoints/eng03/Fuel_Corridor.blend`, **7,619 objects**, SHA-256 `bf22ed9f5ef31b52a4cb7031c7055080d111396a515cd145c160126c1d85e31a`. Fresh factory-started Blender 5.2 CPU inspection preserved this hash. No scene save, render, GPU operation, object transform mutation, neighbor import or neighbor edit occurred. Earlier evidence is preserved. Mutable source and planned corrections were not used as evidence.

## Remaining defects and new regressions

### 1. Major — added reactor lights narrow the declared 5 m approach

The independent branch probe finds **18 blocked rays out of 15,876** through F02's retained 5.00 × 5.00 m approach envelope: nine on each new `Reactor_left_key_hood` and `Reactor_right_key_hood`. Their evaluated bounds are:

| Hood | X bounds | Shared Y bounds | Shared Z bounds |
|---|---|---|---|
| Left | 11.50–11.80 m | 22.585–23.015 m | 2.515–2.635 m |
| Right | 16.60–16.90 m | 22.585–23.015 m | 2.515–2.635 m |

A transverse witness measures **4.800001 m** between the hoods. The frame opening itself remains 5 m wide; the obstruction is in its approach. The smaller **2.40 × 2.20 m** operating envelope remains clear. This is a new regression from eng02, supported by actual ray hits rather than nominal dimensions alone. Frozen `valorant_details.py:329–333,632–633` identifies the lights.

Both hoods also positively intersect their wall assemblies' `vertical_flange.003`, separately recorded in the detail probe. The measurement does not prove a collision with any neighboring scene.

### 2. Major — one newly authored low guide has no backing at its declared mount

`Route_guide_04` records `UNRESOLVED_SUPPORT`. Its actual back face is at the declared anchor, but an independent ray finds no architectural backing there. Evaluated assembly bounds are X12.000–12.070, Y18.250–18.550 and Z0.255–0.385 m. Its intended wall support is therefore not established, and it is above the floor. This is an authored mounting failure, not a visual inference from an unrendered object. The probe does not claim an exhaustive search for hypothetical alternative support directions.

### 3. Moderate — ten low guides are embedded in the washable wall lining

For every other `Route_guide_00`–`10`, the actual wall-facing assembly back remains at the nominal wall plane while the visible washable lining lies approximately **28 mm in front of that plane**. Both back and housing have actual evaluated intersections with the lining. For example, `Route_guide_00_housing` shares bounds of about **17 × 290 × 120 mm** with `Wall_E16.4_0_7_washable_lower`.

Guides 05, 08 and 10 additionally intersect local steelwork; guide 10's glass intersects `Wall_N18.6_0_-5.4_vertical_web.001`. These are positive housing/glass conflicts, not merely deliberate screw embedment. A short anchor ray from inside the lining can miss the true outer support face; the independent ray here starts 100 mm in front of the nominal plane.

### 4. Moderate — other newly mounted equipment intersects structural wall details

The strongest actual evaluated witnesses are:

| Assembly | Confirmed physical conflict |
|---|---|
| `Clean_distribution` | Folded shell, gasket, door and hinges intersect `Wall_S18.0_0_1.2_vertical_web.004`; shell also intersects `vertical_flange.008`. Shell/web shared bounds are about 70 × 70 × 490 mm; door/web about 64 × 20 × 448 mm. |
| `Bypass_first_aid` | The case intersects `Wall_E1.2_0_13.2_vertical_flange.004`, shared bounds about 16 × 20 × 400 mm. |
| `Bypass_isolation` | Back and folded shell intersect the local capping and `vertical_flange.002`. |
| `Plant_work_permit` | Card intersects `Wall_S16.2_0_-5.4_vertical_flange.002`, about 51 × 4 × 310 mm of shared bounds; pen/clip also intersect its nearby web. |
| `East_distribution` | Back and folded shell intersect washable lining/capping; packet holder intersects the capping. |

The supporting wall and assembly backs coincide at each inspected central anchor. That **does not establish fit across the complete mounting face**. The intersections above occur away from that single point. All are supported by evaluated triangle intersections; bounding extents identify their scale, not intersection volumes. Additional shallow backplate/seam and fastener contacts are retained in the evidence but are not all treated as equally severe defects.

### 5. Moderate — complete recessed station still conflicts with wall construction

The **rerouted pipe and feed branch now clear architecture**, but expanded checking of the complete `Service_air_station` finds residual non-pipe conflicts:

- Its mounting frame intersects `Wall_W-1.65_0_14.3_washable_lower`, `capping`, `upper_rail`, `utility_band` and `panel_cross_seam`. Frame/upper-rail shared bounds are about 50 × 840 × 180 mm.
- Its dust cap intersects that wall's `vertical_flange.001` and `frame_anchor.003`; cap/flange shared bounds are about 10 × 43 × 56 mm.
- Its hose-hook foot intersects the lower lining/capping.

The station's central anchor/back face has real zero-gap contact. Its distributed mounting fit still fails. These non-pipe witnesses were **not covered by the earlier pipe-specific eng02 test**, so they are reported as residual conflicts found by expanded coverage, not automatically as new regressions. Fastener/rail contacts are recorded separately from the substantial mounting-frame and dust-cap conflicts.

## Checks now supported by passing evidence

- **Opposing rollers:** zero intersections in the freight gate's 39 main states and eight additional near-closed probes. All five saved closed external/branch doors also have zero opposing-roller intersections. The eng02 roller conflict is resolved.
- **Roller/rail contact:** all four freight rollers have direct support-ray contact through all 39 states; signed numerical gaps are below 0.1 micrometre in magnitude, with zero positive vertical penetration. Rotation/friction was not simulated.
- **Freight gate surround:** no positive moving-part/static-solid penetration was found. Four rivet/track contacts near 84.2% opening remain zero-thickness tangencies. Hangers, leaves and pocket surrounds remain clear in the sampled states.
- **Overhead integration:** no actual crown/overhead, tray/overhead or tray/crown intersections. All five external/branch door assemblies clear the authored ceiling slab/panel/crossmember/height-step geometry.
- **Recess pipe:** station pipe and branch have no architecture/ceiling intersections. Branch-to-station and branch-to-loop centerline gaps are exactly zero and tube surfaces meet. Reserved/capped supply ends do not constitute a simulated operating air system.
- **Other apertures and operating routes:** F01 and all three branch nominal grids have zero obstruction; all tested operating grids and 12,645 branch walk-up rays plus floor samples pass. F02's full nominal approach fails only as separately described above. Saved branch/cap leaves remain closed; filtering moving members is counterfactual clearance testing, not proof of opening/storage motion or neighbor passage.
- **Seam ownership:** the complete nearby-geometry scan finds no object crossing either freight seam, including the formerly outboard shoulders. F01 shoulder masonry now occupies Y0–0.30 and F02 Y23.70–24.00. This resolves the known corridor-side ownership overrun without certifying assembled neighbor fit.
- **Handoff:** all 12 carriage records, 34 markers, targets and 7,232 collision records agree with saved geometry/properties. Each F01/F02 cap has exactly 104 flagged moving members. Explicit assembly, port, owner, cap/removal and coordinate-space semantics remain correct. Frozen source, disk export, scene and manifest identities agree. Runtime implementation remains pending.

The new D04–D06 cameras exist as additional inspection provision; no claim about their framing quality or visible results is made before actual image review. Original cameras were not changed by this audit.

## Method and limits

The gate/service/head probe evaluates world-space geometry from the exact checkpoint; moving states are copied-vertex translations, not object mutations. Main motion samples are 48.7 mm apart, supplemented near closure. Tests combine actual BVH triangle intersections, bounded containment samples, overlap-thickness classification and direct support rays. A separate probe checks 22 complete revised/new physical assemblies against nearby architecture and their declared mounting anchors.

The mount probe's architecture-only support ray is deliberately narrower than the main validator's possible support graph. In particular, `Refinery_approach_key` declares the door motor cover as its support; a missing architecture ray there is **not** reported as an unsupported light. Complete intra-assembly support, all-direction attachment paths, continuously swept motion, branch storage motion, runtime physics and a global facility assembly remain outside this targeted review. No main-validator result was inherited.

Evidence: `astra-eng03-engineering-probe.py/.json`, `astra-eng03-details-probe.py` / `astra-eng03-details-evidence.json`, and the independent `astra-eng03-branch-*` audit, shell and hood evidence/logs. All reside in this critic directory and bind to the unchanged checkpoint hash.

| Frozen file | SHA-256 |
|---|---|
| build.py | `9bc7eb787e03541f89d329361c7deff4363c9b546111264176db601f5d15a41f` |
| valorant_details.py | `568b6ff1d36bdefabfaf6bf5ce3d14a91aa01b0c4857f7ea0064f99bfe4305fd` |
| interface.json | `d410821c4fec77fa8cf49dfc9ba3f7acd7e34ebcd80559cd3513e1b5c731fcb7` |

