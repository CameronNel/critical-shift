# Refinery overhaul state

Owner authorized a full refinery interior overhaul on 2026-10-02: Valorant environmental principles, actual Spawn room quality reference, purposeful trinkets, sharper edges, and illumination from physical fixtures only. Branch: `codex/refinery-overhaul-20261002`. Primary author: Codex. Independent critics: GPT-6 Luna.

**Current phase: R15 authoring accepted by the fresh GPT-6 Luna review at 99 in every category and 99.0 weighted, with no veto. The additive review package is ready; repository promotion/merge remains separate.** Style slice v6 passed 8.3/10 before full expansion. Fourteen complete correction cycles follow R01. Both final visual comparisons (R13→R14 andR14→R15) preserve composition without material regression. Accepted checkpoint: `checkpoints/R15.blend`, SHA256 `3741cbdf4c5fe04135bbddaa79565502149111b5a2085917e93922e52ab4cc3a`.

| Review | Layout | Art | Hero | Materials | Lighting | Dressing | Technical | Weighted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R01 | 80 | 73 | 72 | 82 | 84 | 58 | 91 | 77.0 |
| R02 | 79 | 77 | 75 | 85 | 84 | 64 | 83 | 78.3 |
| R03 | 80 | 77 | 75 | 85 | 87 | 66 | 91 | 79.8 |
| R04 | 82 | 80 | 81 | 86 | 87 | 72 | 91 | 82.45 |
| R05 amended | 86 | 82 | 82 | 86 | 88 | 75 | 84 | 83.5 |
| R06 full amended | 83 | 80 | 80 | 84 | 86 | 76 | 80 | 81.4 |
| R06 fresh | 90 | 87 | 84 | 88 | 89 | 85 | 97 | 88.3 |
| R07 full amended | 84 | 83 | 84 | 88 | 87 | 78 | 96 | 85.3 |
| R08 full amended | 85 | 84 | 87 | 88 | 92 | 82 | 90 | 86.45 |
| R08 fresh amended | 94 | 89 | 86 | 90 | 91 | 88 | 90 | 89.90 |
| R09 full | 86 | 85 | 88 | 89 | 91 | 84 | 84 | 86.65 |
| R10 full | 86 | 86 | 90 | 89 | 91 | 86 | 94 | 88.35 |
| R10 fresh | 97 | 92 | 96 | 89 | 94 | 90 | 98 | 93.75 |
| R11 full | 86 | 87 | 91 | 89 | 91 | 87 | 82 | 87.60 |
| R12 fresh | 98 | 97 | 97 | 96 | 98 | 96 | 95 | 96.85 |
| R13 comparison | 98 | 97 | 98 | 97 | 98 | 96 | 98 | 97.45 |
| R14 comparison | 98 | 98 | 98 | 98 | 98 | 96 | 95 | 97.50 |
| R15 fresh acceptance | 99 | 99 | 99 | 99 | 99 | 99 | 99 | 99.0 |

Reports are in `critics/`. Historical automated PASS is bounded evidence, not exhaustive geometry certification. R06 fresh critic disclosed seeing historical scores accidentally before the review and excluded them. R06/R08/R09 audits found defects beyond the validator's declared anchor tolerance; scores were amended where relevant. R08 fresh review predates the completed context renders.

## Deliverables and boundaries

Editable additive candidate: `../module_overhaul_R1.blend`. Checkpoint names, hashes and scene revision identify each cycle; the candidate filename is intentionally constant. Original `../module.blend`, original assembled map, exterior, registry and frozen R17 are untouched. All 29 protected shell/port meshes and matrices match the original. Primary aisle remains clear. World illumination is exactly zero; all 21 AREA sources belong to physical lenses inside the room. No sun, exterior light, hidden fill or environmental lighting. Planar construction chamfers are one segment, up to 6 mm on new parts and 4 mm on inherited parts, with larger authored clipped profiles where construction warrants them.

`context/refinery_context_R10.blend` is a separate review-only actual-map wrapper: 2,895 existing nearby map objects, the candidate at the real refinery placement, all map light objects omitted, and only the candidate's 21 practicals. The three context views in `renders/R10_context` (completed) and completed `renders/R08_context` show real adjoining geometry beyond the open ports. The underlying current map has unrelated missing linked Spawn object IDs; this preview neither refreshes the full map nor certifies all map dependencies. Its visible candidate poses are separately compared against the checkpoint. Existing context surface finishes can overlap boundaries; only the standalone module is the authoring candidate.

## Correction history

- R02: thermal drum, angled controls, press glass, drain and maintenance cart.
- R03: contained ore, safe parent retirement, cleanup/eyewash cluster, threshold fixtures and ledger shelf.
- R04: stable rigid console groups, cast crusher yokes, functional gauges, mechanical hatch and return pipe, apron/sample rack.
- R05: outward ore winding and button-child transforms; measured wheel contacts; cool architectural wings; wood/metal surfaces; stainless inspection bench; crew board; recessed crusher controls and shutter guides. Audit caught 22.5 mm scanner-cheek gaps.
- R06: seated scanner pads, optical hood, thermal cover/filter tray, smaller gauges, aimed task heads, ceiling bearings and simpler route paint. Audit caught blocked wall/press sources and unmounted thermal clamps.
- R07: compact hood, analytic vessel normals, hydraulic press foundation, concave dryer saddles, radial thermal mounts, sample scoop, sharper control corners, open-bottom wall fixtures, correctly rolled apertures and extended bulkhead arms. All105 aperture rays clear except one intended sample receiver.
- R08: compact reader, pressure-bearing yokes, cantilever service ledge, filter cabinet, front-girder practicals, hearing protection and signed hatch tag. Audit caught 1 mm contacts and disconnected tag endpoints.
- R09: closed ledge/cabinet/diffuser contacts, physical retainers, continuous tag wire, correct yoke modifier order, stainless working surfaces, formed instrument carrier and local steam staining. Audit caught a parent-space error displacing tag writing and horizontal ear-cup ellipses.
- R10: exact-world tag marks and correct ear-cup axes; rear cantilever reader; folded crusher roof and recessed jaw; station-specific original control cases; broader real diffusers; actual interstage hose couplings and restrained contact wear. Independent audit found no concrete repair blocker; the roof bearing lacked an explicit registry entry. New printed-mark and ear-aspect checks pass.

- R11: distinct rolled enamel/cast powdercoat/thermal-jacket response; wheel gripping wear; larger primary captions seated on their actual control faces; shaped roof bearing strips and rear wall; visible hose compression nut; seated, specific PV-05 notices and radio feet. All eleven views complete. Audit caught capped solids in four new hose fittings and a short timber-polish fragment beyond the table edge; R11 remains unaccepted.
- R12: annular four-fitting bores; measured outlet/hose axis alignment and tapered adapter; evaluated hose/fitting interior and surface-overlap checks; tighter sheet chamfers; quieter secondary service trunk; wood polish clamped to the actual tabletop. All eleven views complete; fresh critic96.85. Four-fitting geometry passes, but independent audit finds4mm band squeeze and capped reducer transition. Fresh critic also identifies riser wedge/PV tonal transitions and remaining fabrication/worker cluster polish.

## Verification

Use Blender 5.2 LTS (`/workspace/scratch/blender-5.2.0-linux-x64/blender` in this environment). Build from the untouched original with `blender/build_overhaul.py -- 15`; validate the candidate with `blender/validate_overhaul.py -- R15`; create a checkpoint only after PASS; render all eleven views with `blender/render_overhaul.py -- R15`.

Formal views use CPU Cycles, 24 samples, 960×540, seed73, eight bounces, AgX Medium High Contrast. Cameras remain fixed across cycles. Rendering opens a fresh process and never saves its source. Manifests record camera pose/lens and source/image hashes. Checks cover protected interfaces, world/source constraints, physical lens associations, five-ray apertures, declared and inherited supports, closed-mesh winding, dependencies, route samples and evaluated triangle budget. No exhaustive intersection, Unity import, runtime collision or performance claim.

R10 cold-start preflight PASS: independent original-source rebuild matches every object/material/scene fingerprint, validates with no issues, and all eleven fixed-camera rendered images are pixel-identical to the unaccepted R10 checkpoint. Evidence: `coldstart/comparison_R10.json`, `coldstart/pixel_comparison_R10.json`, `validation_R10_cold.json`, `renders/R10_cold/manifest.json`. This is reproducibility evidence, not final acceptance.

- R13 authored: annular product tube profiles/end faces;0.5mm band squeeze and explicit support/section checks; sorted-feed vertical run centred inside its screw casing to remove the pixel-ray-identified grey wedge; real sheet-edge returns at press/reader service covers; existing glove moved beside alignment tools; one clipped crusher service record. Numerical validation PASS, including the new band sections and reducer-interface rays; all eleven views and the independent technical audit complete. Luna97.45: no new technical blocker, but manufactured layering and worker cues remain weak in the fixed pixels. Triangle total418890 now includes evaluated curve/font geometry (old reports counted native meshes only).

R13 cold-start preflight also PASS: every authoring fingerprint matches and all eleven fixed views are pixel-identical (max channel delta 0), with the same camera/settings. This is unaccepted-checkpoint reproducibility evidence.

R14 numerical PASS (420822 evaluated triangles, 201 explicit supports); all eleven fixed renders complete/source unchanged, independent visual 97.50; technical audit found original sensor screw mesh1mm off the replaced frame, corrected in R15. Changes: actual inset optical glass/camera frame and slotted folded channel behind the station label; pressed press-door centre and supported pull; larger signed crusher record, pale glove on an exposed deck shoulder, and a supported inspection wipe/caliper.

R15 authored: rigid glove/tool placement in actual ray-tested empty worktop shoulders, source sensor screws seated to the new frame front. R14 self-review confirmed that the first placements were occluded; no hidden geometry was awarded visual credit.


## Accepted R15 verification and handoff

`validation_R15.json` and `validation_R15_cold.json` PASS with no issues: 29 protected interfaces unchanged; world 0; 21 fixture-bound in-room AREA sources with 105 aperture samples; 201 new and 133 inherited contact checks; 965 positively wound closed-mesh checks; 38 printed-face checks; 420822 evaluated triangles including curves/fonts. The independent `critics/technical_R15.md` verifies the final screw seating, moved prop groups and local clearances. It found no remaining physical placement blocker within the audited scope.

The untouched-original rebuild matches all 2989 objects, 45 materials and scene-state fingerprints. All 11 cold-process views are pixel-identical to the accepted R15 checkpoint (maximum channel delta 0, identical settings/cameras). Evidence: `coldstart/comparison_R15.json`, `coldstart/pixel_comparison_R15.json`, `renders/R15/manifest.json`, `renders/R15_cold/manifest.json`. `blender/compare_coldstart.py R15` reproduces the state/pixel comparison using ordinary Python+Pillow.

Fresh reviewer `critics/R15_fresh.md` opened both actual Spawn references, all 11 native R15 images and all corresponding R14 images, with no prior score/author history. It scored all seven categories 99 and weighted 99.0, found no veto, and confirmed R14→R15 visual stability. The prior R14 report confirms R13→R14 macro stability. The reviewer explicitly did not award visible-story credit to the small glove/caliper; the visible nook and process dressing support its score. Their visibility remains optional polish, not a claimed completed improvement.

Next: submit PR1's additive source/evidence for repository review. Per MAP.md, canonical-module replacement and map-owner relinking belong to the later promotion process. No original module, registry, assembled map, exterior or frozen snapshot was modified; no merge was performed. Unity export/import, runtime collision and performance remain outside this authoring task.
