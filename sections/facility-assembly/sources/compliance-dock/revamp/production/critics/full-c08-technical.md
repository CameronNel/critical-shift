# Compliance dock — independent full-cycle-08 category 8 review

**Category 8: 91.5/100.** Technical support gates remain unmet. This report scores only technical cleanliness, support contact, reproducibility and dependencies. It supplies no scores for categories 1–7 and no overall acceptance verdict.

The immutable native reviewed is `module_overhaul_R1.blend`, SHA256 `d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35`. All four supplied canonical recipe hashes match. Blender was 5.2.2 LTS, with one thread per probe. No builder ran, no native was saved, and no disposable native was edited. Six fresh read-only native probes completed successfully.

The score was released only after the complete 27 beauty, four neutral and four UV manifests were independently verified and all 35 current plus four approved reference PNGs were individually opened with `view_image`, detail `original`. Every PNG hash, current source/renderer hash, diagnostic camera matrix/lens/projection and approved-reference source hash matched. The complete per-image findings are in `full-c08-technical/imageaudit.json`.

## Deductions and gates

| Stable ID | Severity | Deduction | Finding |
|---|---|---:|---|
| TC08-SUP-01 | Critical technical gate defect | 5.0 | `Cable tray longitudinal -1.5` and its four cable bundles form an unsupported surface island. The tray spans 15.4 m. There is no geometric path from this island to rooted architecture. |
| TC08-SUP-02 | Critical technical gate defect | 3.0 | `P1 corridor overhead sign` and its text form a second unsupported island. The text touching the sign does not support the sign. |
| TC08-UV-01 | Minor | 0.5 | The actually consumed fabric charts retain localized anisotropic distortion on chair cushion edge bands and small textile details. The untouched metric face layer does not certify the consumed fabric chart. |

The technical veto ID is **TC08-TECH-SUPPORT-GATE**, caused by TC08-SUP-01 and TC08-SUP-02. This denotes the objective support/contact and registration gate, not a score or verdict on the other visual categories. Both support defects prevent the required zero-critical technical gate from being cleared even if their appearance is subtle in some fixed views.

### TC08-SUP-01: actual surfaces, not an overlap allegation

The complete evaluated object graph found the west tray and four bundles disconnected from the floor-rooted scene. A second graph split evaluated meshes into real topological pieces, including joined mesh contents and individual glyph pieces; it reproduced exactly the same island. Across all external geometry, its AABB distance lower bound is **68.5875 mm**, which rigorously excludes a possible 5 mm surface contact. This uses separation as a lower bound, not AABB overlap as proof of a defect.

Actual surface measurements additionally substantiate the result:

- Tray vertex to actual `P2 gate sign plate` triangle: **80.0495 mm**, at approximately `(-1.673, 15.600, 3.452)`.
- Upward ray from tray top `(-1.5, 2.2, 3.51)` to actual `Truss bot chord 2.2` underside: **90.0001 mm**, hit z `3.6000001`.
- The cables rest on the tray, but neither they nor the tray touch rooted geometry within tolerance.

`C10_ROOF_SERVICES` contains the service run, although dark overlaps make a precise gap difficult to judge in pixels. Corner cutaways remove the overhead assemblies and cannot clear this defect. The native measurements are decisive. These five objects are labelled `architectural`, have no registered supported assembly, and bypass the ordinary support-anchor checks. Required correction is a real rooted bearing/suspension path and its registered contact evidence; renaming or adding anchors alone cannot clear it.

### TC08-SUP-02: detached entry sign

The sign and 17 glyph pieces form an 18-part island. Every external geometry envelope is at least **125.3994 mm** away. The nearest actual sign vertex-to-door surface witness is **127.3553 mm**. An upward ray from `(0, -1.85, 2.45)` hits `P1 corridor ceiling` at z `2.6000001`, giving **150.0001 mm** of clearance above the sign. No hanger, bracket or wall bearing closes this gap.

The orange deep entry sign is visible in `PLAYER_REVERSE` and `WALL_SOUTH`; neither view supplies a support that is absent from the native. The nearer projecting locator is a separate object and cannot support this deep sign across the intervening space. The sign/text are labelled `architectural` and have no contact registration. Required correction is a physical mount connecting this sign to rooted geometry, then an actual surface-contact check.

### TC08-UV-01: distinguish the two UV contracts

All 1,115 evaluated mesh surfaces with `CD_Physical_1m` passed the independent edge metric test: no triangle edge above 0.1 mm deviated over 1%. This is a face-chart repeating material layer with intentional seams/overlaps, not a lightmap.

The `CD | fabric` and `CD | cotton` shader links actually consume `CD_Fabric_Cut_1m` for color, roughness and weave normal modulation. Independent triangle Jacobian singular values show:

| Consumed chart | Area with anisotropy >1.25 | Area-weighted p95 anisotropy |
|---|---:|---:|
| Chair seat cushion | 21.65% | 1.483 |
| Chair back lumbar | 19.11% | 1.493 |
| Chair back upper | 24.99% | 1.595 |
| Main draped tarp | 0% | 1.023 |
| Joined trolley cotton details | 66.67% of only 0.0315 m² | 1.999 |

The UV office original visibly changes checker proportions around chair cushion edge bands. The trolley original retains coherent broad checker flow; its main tarp is not a failed chart. Small textile straps/edge details retain compressed checker proportions. This is a minor localized technical deduction, not a claim of broad visible material failure. More measurements, including small folded cloth and welt charts, are retained in `details.json`.

## Independently established strengths

- **395,342 evaluated triangles / 450,000 cap; 1,143 used material submeshes / 1,150 cap; 35 local used material families / 36 cap.** Whole-file material datablocks from the read-only linked map are not local material families or draw-call measurements. The last two caps have little headroom but are met; no deduction is assigned merely for approaching a cap.
- All **1,077 original objects** are present. Their actual world matrices match the protected `module.blend`, with one numerical re-evaluation residue of `1.1920929e-7` on `Key box label` (approximately 0.12 micrometres). This is not a meaningful placement change.
- **1,142 geometry objects** split into **2,868 actual topological parts**. **2,845 parts** connect to `Floor slab` through **6,195 measured surface contact edges**. The remaining 23 parts are exactly the two defects above. Each edge has an actual triangle overlap or actual nearest-triangle surface witness within 5 mm. Shared object ownership and parent metadata were not treated as continuity.
- No evaluated degenerate triangles, missing material assignments, exact world-geometry duplicate objects, negative scales, inconsistent shared-edge winding or inward closed-mesh winding were found. Preliminary single-precision world-volume signs were rechecked with centered double-precision volume and were numerical cancellation, not normal defects.
- Thirty-four exact polygon coincidences were retained for scrutiny, principally trim junctions and closed P2/G1 mating geometry. The largest is a 0.07256 m² P2 steel mating face. Current originals show no established dominant coplanar flicker or destructive intersection there; these contacts are not assigned speculative deductions. General intentional assembly intersections are not defects merely because BVHs overlap.
- Direct evaluated-surface rays independently measured floor z `0`, side wall inner faces x approximately `±6.8`, P2 frame width `4.6000 m` and height `3.5000 m`, and D1/D2 frame widths `1.0500 m` and heights `2.2000 m`. Scanner midheight width is `1.2800 m`, with lintel underside at `2.6500 m`; measured source geometry is distinguished from contract minima/allowances. The P1 perimeter lintel sample is above its limiting corridor ceiling; it is not falsely advertised as 2.7 m usable headroom.
- The existing read-only validator, called with explicit `contracts/interface.json`, reports seven checks, zero errors, zero warnings, 46 registered assemblies and 93 measured anchors. It verifies static route/portal reservations in declared open poses. Its documented selection and ancestry limits remain real; its green result does not supersede the independent two-island finding.
- Local scene objects are editable and local, with separate components and only weighted-normal modifiers. Some inherited static curve-derived meshes retain world-coordinate origins; this is compatible with their current static procedural organization. Hinged leaves expose explicit hinge metadata, but animation binding and runtime pivots are not certified.
- All **25 relative linked libraries** resolve in the reviewed workspace. All **119 loaded image resources** are packed. The local room's consumed materials have no image texture nodes; their texture response is procedural. The used DejaVu font is packed, its relative source file exists, and its redistribution license is present at `revamp/art/fonts/LICENSE-DejaVu.txt`. The built-in font resolves. Packed linked-map resources are not claimed to be newly authored local room textures.
- Fresh Blender processes opened and evaluated the frozen source successfully; the source hash remained unchanged after every probe. Current renderer recipes remain hashed and reproducible without a live UI session. No process or file reader from this review remains open.

## Limits and delivery state

The contact graph establishes surface continuity within the 5 mm review tolerance, not engineering load capacity, stable center of mass or exhaustive per-triangle minimum distances for every connected pair. Nearest-surface searches were bounded for the full graph; the two failed islands received dedicated all-external separation bounds and actual surface-ray/nearest witnesses, so their conclusion does not depend on sampling misses. The review does not claim an exhaustive all-pair boolean intersection volume certification.

Runtime collision, navigation, interactions, physics, animation, curved cart/body movement, FPS, engine draw calls and Blender/engine equivalence remain unverified and are outside this art task. Authored sealed/openable leaves are not certified as runtime traversable simply because the offline validator tests declared open poses. Prior review-cycle stability and process history were intentionally not used to earn this score.

Root's isolated GitHub source-only cold-open and the forthcoming cold-pixel/publication delivery checks are separate gates. This critic performed fresh local source opens and current image provenance checks; it has not independently certified root's GitHub checkout or a final cold-pixel comparison. No cold-pixel pass is claimed here.

Probe scripts, successful logs, exploratory nonzero discovery-command evidence, quantitative JSON, manifest audit and all 39 per-image findings remain under `critics/full-c08-technical/`. The sole author remains root. Native and recipe SHA256 identities are unchanged; all review processes/readers are released.
