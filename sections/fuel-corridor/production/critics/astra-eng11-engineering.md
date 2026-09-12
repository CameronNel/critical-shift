# Astra independent eng11 targeted engineering review

**Verdict: FAIL for a remaining motor-mount fastener engagement defect.** All eng08 blocking drive-plate, cable-retainer and crown-support findings are resolved in the actual saved geometry. No new external body obstruction, camera near-field failure, reactor seam clash, approach regression or handoff discrepancy was found. This is a bounded CPU engineering result, with no art score or visual-cycle credit.

## Frozen authority

Fresh Blender 5.2 factory-startup CPU probes reopened `production/checkpoints/eng11/Fuel_Corridor.blend`: **7,827 objects**. The local physical-body cache contains **6,801 evaluated meshes/tubular curves**, excluding text and surface decals. Separate branch/export inspection includes its appropriate geometry inventory. No scene transform, source, neighbor or scene file was changed; no rendering or GPU work occurred. File identity was asserted before and after the probes.

| Frozen item | SHA-256 |
|---|---|
| Fuel_Corridor.blend | `22cdfe2c2d8bf7c13070686a981118353f7d6c19dc7fbb89797102881cae7ae6` |
| build.py | `c78a856bfe4142c7df9471a00da37f25c442ded0c148eee24277d898b68dd51c` |
| valorant_details.py | `b2c597dcccc73b40da6c98ee36741829f467f4a3e4f5fb1070279204b24d7aed` |
| interface.json | `ce6ddfa16e0bbea71030e9c190f6507b8fa69fa2e489c548f3a04a3cd21a872e` |
| build_manifest.json | `9eb17b6db95d162653f0cbe7994dcedb05aa45bcaaf13aa673854627c1510cd4` |
| handoff.json, file bytes | `b45aa21a26820c830f7bdcc5721d47d7e275fef00d4d70098cf8ada74ed043ce` |
| Canonical saved handoff | `e629818f25533993d8f61154f4bd9199713243f1964bbd77abcee9ca4fdea0c6` |

Saved source/detail/interface values and all six manifest bindings agree. Interface bytes are unchanged from eng08. The probes are independent of the checkpoint validator.

## Remaining defect

**Minor assembly defect — `Motor_mount_anchor` and `.001` no longer engage the shortened backing plate.** Both rods occupy approximately **3.783938–3.796062 m** vertically, while the backing plate ends at **3.770000 m**, leaving a **13.937712 mm** minimum vertical gap. Their only local intersections are the vertical mount; `.001` additionally intersects `Gate_track_bearing.001`. Neither rod enters a backing segment. This is a modeled fastener termination issue rather than a floating motor or route obstruction.

The vertical mount body itself has a valid seated contact with `Gate_drive_plate.001` over a **220 × 50 mm** face, within **0.477 micrometres** numerical overlap. Its 36 mm distance from the motor cover is bridged by that backing plate. Therefore that 36 mm reading must not be misreported as a missing support-body connection. The separately visible rods still cannot be credited as anchors into the shortened backing. Pending eng12 changes are not evidence for eng11.

## Verified corrections

| Eng08 finding | Actual eng11 result |
|---|---|
| Backing plate intersects lintel cheek/roof | Both segmented plates are clear; no evaluated triangle intersection remains. |
| Backing plate intersects access cover/cover bolts | Both segments clear those separate components. |
| Backing plate intersects `Transfer_gate_key_back` | Clear. Saved plate vertical bounds are **3.675000–3.770000 m**. |
| Retainer misses its stud | Retainer connects to both ears; both studs intersect their ears and backplate. Both 11 mm spacers meet the ears and backplate at zero-depth contact. No spacer/stud intersects the cable. |
| Unsupported crown infill/ledge | Infill now meets crown beam within **0.477 micrometres**. Ledge remains connected to infill. Beam meets the existing ceiling crossmember at the registered support face. |

The two backing segments now have only zero-depth exterior contact with `FREIGHT_GATE_upper_motor_cover`. Complete drive-group inspection covers **84 physical members** and lamp inspection covers **six**. The only other exterior contacts are the cable-clamp and lamp backs against the crown infill. No positive-depth external body intersections remain in these two groups.

The crown's declared anchor resolves to **`Ceiling_crossmember.010`**. At the saved anchor, independent closest-surface queries return the same point on `Gate_crown_beam` and that crossmember, **zero distance** from each, with opposing X normals. This verifies real coplanar face contact even though the triangle-overlap routine does not classify coincident faces as penetration. The beam no longer penetrates the crossmember by the old 75 mm. `Freight_gate_crown` has the corresponding wall-support registration; the infill and ledge are its children. No ceiling shim was present or credited.

The revised lamp arm meets its back within 0.477 micrometres, connects into the hood, and the diffuser meets the hood at zero gap. Its physical assembly clears the surrounding motor, tray and architecture. These contacts do not judge the quality or direction of its emitted light.

## Regression results

- **Motor dimensions unchanged:** stator/end-bell combined axial length **300.000191 mm**; end-bell radial spans approximately **180.000 mm**; 16 fins with **200.000301 mm** transverse span and approximately **200.025 mm** corner-inclusive radial envelope. The tiny corner excess remains disclosed. Seated casting, terminal, gland, boot, cable and reducer connections remain present. Same-assembly casting and fastener joints are distinguished from obstruction failures.
- **All eight reactor seam pairs clear:** approximately **110.000 mm** above the identity inserts and **32.500 mm** above the relocated middle ribs.
- **Camera near-field:** all 16 saved cameras, **4,624 frustum rays**, have zero first hits within **0.12 m**. D05's center reaches `Motor_guard_caution` at **0.898772 m**. A clear sampled frustum is not an exposure or composition verdict.
- **Approaches and seams:** independent branch reviewer found zero hits across **32,056 nominal** and **15,400 operating** rays after the specified carriage exclusion, and no blocked branch/sign-region samples or sampled floor discontinuity. All five retained portals remain inboard. No F01/F02 shell or shoulder overrun was found, including outside the apertures.
- **Cap and handoff:** refinery **104** and reactor **177** presentation-cap members match carriage inventories. Each branch retains **104** moving geometry members without presentation-cap flags. All **34 typed markers, 12 carriage registrations and 7,424 collision records** agree with the saved scene, without missing, extra, duplicate or semantic mapping errors.

## Evidence and scope

Evidence files: `astra-eng11-motor-evidence.json`, `astra-eng11-crown-evidence.json`, `astra-eng11-branch-evidence.json`, `astra-eng11-branch-inventory.json`, and `astra-eng11-branch-shell-evidence.json`, with corresponding scripts/logs in this critics directory. The first crown evidence serialization encountered a reviewer-script JSON conversion error; that log is preserved separately, the conversion was corrected, and the fresh successful probe produced the cited evidence. No scene operation was affected.

This review verifies selected saved geometry, finite surface/ray samples and typed-data consistency. It does not certify internal transmission motion, hidden fastener design, structural strength, vehicle turning, external door storage, neighboring scenes, cooked colliders or runtime controllers. The remaining modeled anchor defect is explicitly limited in severity; the resolved body/support/route findings are not reopened by it.
