# S10 independent technical slice review

**LOCAL PASS — category 8 technical judgment: 96/100.** No critical local technical defect was found in the tested front-office/D1/check-in/reader/practical/utility slice. This does not approve full-room art, expansion by itself, source promotion or runtime integration.

Frozen source: `module_overhaul_R1.blend`, SHA-256 `f817b83c4d0bcf1dec88e6f3b7bf39ddc9100da66e74a1a1c5015ebbe52c5265`. All native probes ran in fresh Blender 5.2.2 processes using `--background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1`. Native source was never saved or changed. No earlier verdict/finding reports or author history were read. Existing measurement scripts were reused as methods; every result was recomputed from this source.

The existing validator, invoked with explicit `--interface ROOT/contracts/interface.json --expected-stage slice`, passes with 0 errors, 0 warnings, 6 passed checks and 5 explicit unverified checks. Its registration inventory contains 23 assemblies and 53 support-anchor rows, including all seven authored independent CD roots and the identity plate root.

## Actual support and construction witnesses

| Assembly | Native result |
|---|---|
| Rigid ID plate | All four spacers meet the enamel back and actual stepped pressed/door skin with 0 measured gap. All four captive heads meet the enamel front with 0 gap. Eight mount components have positive centered volumes and consistent outward winding. |
| Posts/infill/worktop | Both posts meet floor and folded worktop; all four sampled infill/post butt faces have 0 gap. Linoleum meets the worktop with 0 gap. |
| Speaking glazing | Both feet meet liner, both uprights meet feet; glazing seats 3.50mm into clamps and clamps engage uprights by 9.00mm. These are deliberate assembled seating, not coincident exposed planes. |
| Rubber/stamp/inkcase | Pad, stamp base and case bottom have 0 gap. Felt seats 0.50mm into the hollow case seat. Case pins, open lid and inner lip have actual engagement. |
| Cloth | Lower/middle layers meet with 0 gap; three upper drape samples have 0, 0 and 0.65mm gap. The top layer is a finite, closed thickness mesh. |
| Reader | Back meets wall, four cap regions meet the shell, and lens meets housing with 0 gap. Three rays pass through the genuine cap aperture and hit the lens first; two border rays hit the cap. |
| Trim returns | Both dado backs meet structural wall at Y3.52; both lower returns butt into lining at Z0.99 with 0 gap. |
| Utility | Junction back meets wall; lid/back separation is 3.00mm, within the 5mm default visible-gap allowance. Five actual conduit rim vertices lie inside the junction lid and four inside the reader receiver. Open tube ends are intentional. Both saddles meet wall and hold the conduit. |
| Hinges/practical | Door straps have a 1.00mm skin separation but engage the captive barrels. Barrels engage actual jamb/leaf by 16.85/10.78mm. Practical brackets meet wall; shade tabs engage brackets, and frosted lens seats into shade. |

Engaged clamps, pins, barrels and fixture tabs use simplified assembled geometry. Their penetrations were measured and classified rather than applying a universal 2mm solid-intersection veto. Complete screw threads, hollow receiver details, welds and moving hinge physics are not modeled/proven by this audit.

## Surface cleanliness, UVs and preservation

The positive-area coplanar triangle test includes object/object and within-mesh comparisons, the protective trim returns, sloped faces and exposure against actual architectural volumes. It found **0 exposed pairs at the tested witnesses**. Two covered pairs remain: junction back/saddle behind the structural wall, and liner/security-grille undersides inside the worktop. Opposed butt joints are excluded intentionally. Exposure is tested from intersection centroids; this is not an exhaustive proof of arbitrary hidden intersections.

All 970 local connected components have finite coordinates/normals, no collapsed triangles, no inconsistent shared-edge winding and no multiface edges. All 198 closed components have positive volume calculated in a centered numerical frame. The remaining components are 765 evaluated font components and seven deliberately open-ended tube components; their boundary edges are classified, not called universal manifold failures.

All consumed named UV layers exist along active shader output paths. Metric edges above 0.1mm range from 0.99310 to 1.00631 UV units/metre, inside the 1% relative tolerance. The local evaluated sample contains 19,190 axis-plane and 42,454 sloped/bevel triangles, including caps and sidewalls. Editable text uses three declared Object-metre shader variants. Repeating face-chart seams and overlaps are intentional; this is not a lightmap/bake or runtime shader proof.

All **1,077 inherited world matrices are exact**, all **five protected SHA values match**, and all **25 linked libraries are relative and resolve**. Floor geometry bounds and the combined architectural outer bounds match the native baseline exactly. Primary front wall face samples match within floating-point tolerance. D1 usable shell aperture samples (25) and hatch shell opening samples (35) are clear in both baseline and overhaul.

The added frame-headslot closure occupies Z2.30–2.35m, above the preserved 2.20m usable doorway. This is an explicit 50mm construction repair. Literal unchanged all-solid union is **not** claimed; edge profiles and redundant internal solids were also repaired.

## Counters and image inspection

Native local scene: **1,250 objects, 333,308 evaluated authoring triangles, 1,145 authoring material submeshes**. The triangle/submesh totals fit the final planning estimates of 450,000/1,150, with only five submeshes of current headroom. These are authoring counts, not runtime draw calls.

There are **48 used native material datablocks**: 23 retained legacy/context and 25 authored CD datablocks. The CD set represents 20 base families, includes three localized handling copies and three text-coordinate variants. Linoleum is represented only by its handled copy; coral and steel retain both base and handled copies. Datablocks and logical families are distinct. The ≤36 family goal applies to final full-room planning; full-room consolidation/accounting remains pending.

Ten actual images were opened: three s10 beauty views (`SLICE_ENTRY`, `SLICE_MATERIAL`, `SLICE_DOOR`), two s10 checker views (entry/door), the s10 neutral material view, and all four immutable spawn references (`VALIDATE_Material_A`, `VALIDATE_LockerDoor`, `VALIDATE_Spawn`, `BRIEFING_INDIRECT`). All three s10 render manifests are complete, identify the frozen source SHA and record no native save. Pixels show no local visible z-fighting or detached support veto at those views; small internal bearings are established by the native measurements above.

The supporting JSON/script/log files are in `slice-s10-technical/`. One initial `internal.py` invocation failed because the critic script lacked a `sha` helper; the helper was corrected and the fresh rerun passed. No native change occurred during that diagnostic retry.

Full-room routes/clearances, all out-of-slice assemblies, complete required full-room camera coverage, four full review cycles, stable final two cycles and cold-render comparison remain unverified here. Fresh cold native opening succeeded. Engine import, collision/navigation, interactions, physical hinge behavior, runtime material equivalence, draw calls, FPS and engine performance were not measured.
