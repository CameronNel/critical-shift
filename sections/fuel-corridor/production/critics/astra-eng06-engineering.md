# Astra independent targeted engineering follow-up — eng06

Date: 2026-09-11. **Targeted result: PASS.** The eng05 mounting/body conflicts are resolved in the evaluated eng06 save. The new plant sign and reactor leaf details introduce no failure in the checks below. This is a bounded engineering pass, not full-scene visual acceptance, continuous-motion certification or a runtime integration certificate.

## Frozen authority and method

Fresh factory-started Blender 5.2 CPU processes opened `production/checkpoints/eng06/Fuel_Corridor.blend`: **7,679 objects**, SHA-256 `caf0c11a33347cbd1655c16f06c981b7fb1aad02eb343b3231508488ccf9bb20`. Source, detail source, interface, saved properties, manifest and typed handoff identities were independently compared and agree. The same blend hash was retained after inspection.

The body-fit probe evaluated **6,709 local mesh/tubular-curve bodies**, excluding font-only objects and flagged surface decals. It checked the complete physical membership of **26 mounted assemblies** against other nearby physical bodies, including architecture, door hardware and equipment. A supplementary probe checked the two new reactor borders and eight fasteners individually against their own leaf/carriage and outside geometry. Independent branch probes checked nominal openings, approaches, floors, seam ownership and handoff integrity. No checkpoint validator code was imported as a substitute for these independent probes.

No scene save, rendering, GPU operation, transform mutation, neighbor import or neighbor edit occurred. Earlier reports and evidence remain preserved.

## Corrected eng05 findings

| Subject | Fresh evaluated result |
|---|---|
| Clean suspended sign | **Pass.** No intersections with lintel cheeks, running rails, roof, north-wall rail, flange or gusset; no other outside-body intersections found. Both ceiling feet contact actual ceiling geometry, and both drops meet the panel within 0.24 micrometres. |
| Guide 08 | **Pass.** Back, housing and fastener clear the former vertical-web conflict. Central mounting contact remains zero-gap. All eleven guides now clear surrounding bodies and have actual backing. |
| First-aid and bypass permit spacers | **Pass.** The shorter spacers no longer intersect the panel cross seam. They retain actual wall backing and contact their supported mounting bodies. No intentional spacer/trim penetration is waived. |
| Relocated reactor turn light | **Pass.** Complete back, arm, hood and diffuser clear the former panel-joint/seam conflicts and surrounding geometry. Actual backing is within one micrometre of its declared mount. |

The previously corrected service-board, distribution-box, first-aid case and permit-body fits remain clear. Three service-board spacers and their feet still contact the wall and board. The station's most aisleward physical point remains X−1.10950 m, approximately **109.5 mm outside** the X−1.00 m edge of the declared centered 2 m west-bypass envelope. The station pipe, branch and union clear architecture; centerline connection errors remain no larger than **0.12 micrometres**, with connecting tube surfaces. The recess task light retains actual ceiling/diffuser contact and has no outside-body intersection.

## New geometry

**Plant branch blade sign — pass.** The complete assembly occupies X−0.650–0.650, Y15.950–16.050 and Z2.340–3.000 m. Both ceiling feet contact actual ceiling panels, both drops meet the sign exactly at evaluated precision, and no outside-body intersection was found. Its bottom is **140 mm above** the 2.20 m operating height. The independent underpass crosshatch has **0 blockers in 2,790 rays** and no sampled floor discontinuity failure.

**Moved clean sign — pass.** Complete bounds are X4.900–5.000, Y19.690–20.810 and Z2.450–3.000 m. Its independent 2 × 2.2 m underpass crosshatch has **0 blockers in 2,880 rays**, with passing floor samples. These route results supplement the separate complete-body and attachment checks.

**Reactor pressed borders and fasteners — pass for the saved closed leaves.** Each border belongs to its correct reactor carriage, retains its presentation-cap flag and contacts its own leaf along all 16 evaluated back-face vertices within **1.91 micrometres**. Neither border intersects the other carriage or outside geometry. Each of the eight fasteners intersects only its own leaf by approximately **3.00 mm**, consistent with a fastener entering that sheet; none intersects outside geometry. This intentional fastener-to-own-leaf embedment is explicitly recorded and is not a spacer conflict exemption. Joining strength and actual pressing/fastening manufacture are not simulated.

## Approaches, seams and handoff

- All five nominal opening grids (**32,056 rays**) and smaller operating-envelope grids pass. **F02 has 0 blockers in 15,876 rays** through its full 5 × 5 m nominal approach after filtering the moving presentation-cap assemblies. Shallow hood separation remains **5.20 m**.
- All **12,645 straight branch walk-up rays** pass, with sampled floor discontinuities within 5 mm. The two new sign-region crosshatches add the separate passing coverage described above.
- All five fixed portal assemblies remain inboard. Wider F01/F02 scans find no geometry crossing the seam, including masonry shoulders. This checks local ownership bounds, not live neighboring geometry.
- All **12 carriage records**, **34 markers** and **7,284 collision records** resolve consistently. The reactor presentation-cap roster increases from 104 to **114** members, including the ten new leaf details. Refinery cap membership remains 104. Saved properties, disk export, cap/removal semantics, coordinate space, navigation data and manifest bindings agree.
- Interface semantics differ from eng05 only in the declared pocket length **1.50 → 1.65 m** and two explanatory strings. Ports, floor cells, route centerlines, handling and travel data are unchanged. The revised service-feed description agrees with the evaluated inlet/branch positions. The movement-status text accurately distinguishes earlier sampled geometry checks from pending engine operation.

The ten formal camera definitions are unchanged. Saved camera positions/lenses agree with the current manifest. D05 alone has a new diagnostic framing definition; this audit does not judge its unrendered composition or treat it as a pixel-identical comparison with the earlier D05.

## Numerical contacts and limits

The plant permit spacer and seven clean-distribution spacers retain approximately **1.91-micrometre** panel overlaps at otherwise coincident support faces. These are floating-point contact effects, disclosed rather than treated as substantial penetration. They are distinct from the millimetre-scale spacer/trim conflicts rejected in eng05. One bypass termination contact missed by the raw triangle-overlap test was verified at **0.12 micrometres** with nearest-surface evidence.

Surface-overlap tests use evaluated triangles plus bounded containment samples. Support rays, explicit mounting-piece contacts and nearest-surface witnesses establish geometric contact, not structural load capacity or every internal fastener's function. Freight-gate motion was not replayed for this targeted follow-up. External/branch stored-open poses, continuous collision sweeps, controller behavior, collider cooking, live neighbor fit, runtime traversal and visual quality remain outside this pass. Filtering closed caps/leaves for clear-opening tests does not demonstrate their storage motion. No visual score or accepted full art-cycle credit is assigned here.

Evidence: `astra-eng06-mesh-core.py`, `astra-eng06-details-probe.py`, `astra-eng06-details-evidence.json`, `astra-eng06-new-details-probe.py`, `astra-eng06-new-details-evidence.json` and log; independent `astra-eng06-branch-evidence.json`, `astra-eng06-branch-shell-evidence.json`, `astra-eng06-branch-detail-evidence.json` and their scripts/logs.

| Frozen identity | SHA-256 |
|---|---|
| build.py | `90d006135f88cda5b35fc47f45c8a4844c3003843dcd5344cb1032b7181e37cb` |
| valorant_details.py | `bbac0d7d33904474924d7f5d8843c182b7c81ad3f4f78b8adec62dda21356b59` |
| interface.json | `ce6ddfa16e0bbea71030e9c190f6507b8fa69fa2e489c548f3a04a3cd21a872e` |
| handoff.json, raw file | `78131d22315e649e8584454186a369e6e7e9a702f5170c0f2df51e531d02055f` |
| Canonically encoded handoff | `15b6eaec79e6d20b21820016403fbde9dcd47ba8e3f9c7ac7dbf91404f70f661` |
