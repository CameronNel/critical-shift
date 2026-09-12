# Astra independent eng08 engineering review

**Verdict: FAIL.** All eight reactor seam clashes are resolved. The compact motor meets the requested dimensions and clears surrounding head/tray/architecture, but its cable retainer misses its stud. The lamp and cable-clamp backplates contact a crown infill whose rigid support path is incomplete. The requested complete-drive inspection also exposes retained drive-plate interpenetrations with the gate head, access cover and light backplate.

No art score, render acceptance or visual-cycle credit is given. The D05 preview was not used as engineering evidence.

## Authority

Fresh read-only Blender 5.2 factory-startup processes reopened the frozen `production/checkpoints/eng08/Fuel_Corridor.blend`: **7,815 objects**, **6,795 evaluated physical meshes/tubular curves** in the local contact probe. Flagged surface decals and text were excluded from its solid-body tests. Independent branch/handoff probes include their appropriate export inventory. No scene save, transform edit, rendering, GPU work or neighbor access occurred. The blend hash was verified unchanged afterward.

| Item | SHA-256 |
|---|---|
| Fuel_Corridor.blend | `abe82d28e3ac4d4f7c6215f7f5cb870863db658be667b2167805d60f0039502e` |
| build.py | `148f2152d89ee5b94cf7bac8ef143c7bce1c0af164553dc040c2a775390a3923` |
| valorant_details.py | `f3f2a1ce56e204179c30d370f89308911f02ffff31b3cb18e4e621f7a6af4cc9` |
| interface.json | `ce6ddfa16e0bbea71030e9c190f6507b8fa69fa2e489c548f3a04a3cd21a872e` |
| build_manifest.json | `4b9d7932cee4a96485a60d4f0c3176847f2a20e3ad353dea62911dd05dc93025` |
| handoff.json, file bytes | `08adb6d4e6c8d1b99e37b102e6dc3117903de8b622d92aba91859927d751d46c` |
| Canonical saved handoff | `8912cb8062321e6f5a69d8ee246872f4b2cf24f654dfa3ee2f75fd55a4f992dc` |

Source/detail/interface identities match the saved scene and manifest. Disk handoff matches saved handoff. Interface is byte-identical to eng07.

## Defects

### 1. Crown infill and ledge lack a rigid support path — moderate, blocking

`Motor_task_back` and `Motor_cable_clamp_back` each meet the front face of `Gate_crown_infill` exactly. The six lamp parts have a connected back/arm/hood/diffuser assembly. Therefore the problem is beyond the lamp's backplate, not a failure to reach its mounting face.

Actual evaluated gaps around the infill are **10.000 mm to `Gate_crown_beam`**, **20.000 mm to `Ceiling_crossmember.010`**, **25.001 mm to the nearby wall flange**, and **30.000 mm above `FREIGHT_GATE_upper_motor_cover`**. Its only other rigid external contact in the inspected neighborhood is the end of `Tray_penetration_lower_ledge`. That ledge itself only contacts the infill; it remains **20.000 mm above the motor cover** and approximately **25 mm from the wall flange**. Together they form an unsupported rigid island carrying the lamp and cable clamp. Merely registering this surface would not establish support.

The crown beam is **18.001 mm below the ceiling slab**, but it is **not wholly isolated**: it intersects `Ceiling_crossmember.010` over an approximately **75 × 4,400 × 110 mm** envelope and nearly touches recessed ceiling panels. That distinction matters when assessing the actual path. This review does not certify the load capacity or construction of that structural joint.

### 2. Cable retainer misses its stud — minor physical defect, blocking local assembly completion

`Motor_cable_retainer` intersects `Motor_supply_cable`, but has no contact with another rigid component. Its nearest stud surface is **1.535892 mm** away; the saved bounds independently establish that vertical gap. The retainer's back is **11.000 mm** from `Motor_cable_clamp_back`. `Motor_cable_clamp_stud` does contact the backplate, but misses the retainer it is meant to secure. This is a positive gap, not numeric contact rounding.

### 3. Retained complete-drive interpenetrations — moderate, blocking a clean whole-assembly verdict

These are actual evaluated triangle intersections, disclosed separately from the newly reconstructed motor. They were already present in the retained drive-plate geometry and must not be described as new motor regressions.

| Pair involving `Gate_drive_plate` | Positive world-axis overlap envelope |
|---|---|
| `FREIGHT_GATE_lintel_cheek` | 25 × 3,600 × 10 mm |
| `FREIGHT_GATE_lintel_roof` | 25 × 3,600 × 10 mm |
| `FREIGHT_GATE_drive_access` | 19 × 630 × 90 mm |
| `Transfer_gate_key_back` | 36 × 180 × 10 mm |

The complete group also intersects two existing drive-cover bolts. These are not the zero-depth seated contacts observed at the upper motor cover. The distinct access-cover and light-backplate crossings in particular prevent an unobstructed-fit claim. No replacement layout or coordinates are prescribed.

## Passing evidence and mechanical distinctions

- **Reactor seams:** all eight previously failing pairs now have no intersection. The seam bottoms measure approximately **2.540000 m**. Clearance is **109.999895 mm** above the identity fields and **32.500029 mm** above the middle stiffeners. Cap membership is unchanged.
- **Motor contract:** actual stator/end-bell combined axial length is **300.000191 mm**. Both end bells span **179.999828 × 180.000305 mm** across their radial axes. Sixteen connected cooling fins have **200.000301 mm** transverse span; the true corner-inclusive radial envelope is approximately **200.025 mm**. That 0.025 mm corner excess is disclosed, not treated as a meaningful scale failure. The vertical fin span is smaller because the top terminal region lacks fins.
- **New motor body clearance:** no new stator, end bell, fin, terminal, cable, reducer or motor-foot mesh intersects the surrounding head, tray or architecture. The vertical mounting back meets `FREIGHT_GATE_upper_motor_cover` at zero measured gap; the clamp back meets the infill at zero gap, subject to the support defect above.
- **Local construction:** end bells overlap the stator at their seated joints; all fins meet the casting; feet meet the bracket and connect to the lower casting/fins; terminal neck meets both stator and terminal box; lid, gland, boot and cable have contact continuity. The reducer input, casing/output foot and rail have a connected path. Own casting joints, foot/lug joints, fastener embedment, connected guard interfaces and intended plate/rail connections are not automatically scored as obstruction failures merely because their separately modeled solids overlap. This is not a certificate of internal gear motion, bolt shank depth, disassembly access or structural strength. The cable retainer gap remains a distinct unresolved rigid connection.
- **Camera near-field:** all **16 cameras / 4,624 frustum rays** have zero first hits within **0.12 m**. D05's central first hit is now `Motor_guard_service_plate` at **0.898991 m**. This verifies the sampled camera surroundings, not exposure, useful composition or the lighting of the motor front.
- **Approaches and export:** the separate independent replay found no blocked nominal/operating/branch/sign-region samples or floor discontinuities. Fixed portals remain inboard, with no F01/F02 shell/shoulder overrun above its 10 micrometre tolerance. Cap inventories remain **104 refinery / 177 reactor**; all **12 carriage records, 34 typed markers and 7,414 collision records** resolve consistently. Nominal widths agree with their contract within 0.8 micrometres. Moving leaves were filtered only for the specified operational-opening samples; open storage and travel were not simulated.

## Evidence and limits

Evidence files in this directory: `astra-eng08-motor-evidence.json`, `astra-eng08-crown-evidence.json`, `astra-eng08-branch-evidence.json`, `astra-eng08-branch-inventory.json`, and `astra-eng08-branch-shell-evidence.json`; corresponding scripts/logs preserve the independent read-only probes. The existing refinery-source reviewer performed the separate branch/handoff replay.

Contact conclusions use evaluated triangles and bounded containment supplements; proximity witnesses use finite vertex-to-surface samples, with explicit axis-gap corroboration for the retainer. Camera and approach lattices are finite. No continuous motion, neighboring scene, runtime controller, full manufacturing validation or rendered visual claim is included. Pending source corrections cannot change this frozen eng08 verdict.
