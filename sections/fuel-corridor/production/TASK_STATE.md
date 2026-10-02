# Fuel corridor overhaul state

Phase: owner-requested eerie/rundown atmosphere revision in progress; F12 is a historical accepted checkpoint.
Branch: `codex/fuel-corridor-overhaul-20261001` from `75983b9`.
Source: `sections/facility-assembly/sources/fuel-corridor/module.blend`.
Baseline SHA256: `f01b8647c4a87c88be859fce0659df8c9aaf41a91743f0c83705b8b8cfc0945c`.
Baseline saved at `checkpoints/fuel_corridor_baseline.blend`.

Historical result: F12ci was the selected editable module before the atmosphere revision. Pessimistic Luna's F11ci
and F12ci full reviews each score all seven categories and all nine areas 99,
using the actual reworked spawn reference as 100. These final two full cycles
are materially stable; the bounded F12 closure repair changes the recipe and
native bytes without a visible collateral art regression. Twelve full cycles
were completed, exceeding the four-cycle minimum. Historical development notes
below retain their original failures and pending states; the final F12 handoff
at the end records the current evidence. No aesthetic score was overridden.

The baseline has 7,978 objects, 34 materials, 16 cameras, 3 packed images and no
libraries. The task preserves exterior shell footprints/ports while replacing
visible asset construction. Native baseline entry, hero, bypass and reactor views
and the reworked spawn reference were captured from this base.

The initial `git lfs pull` failed because this runtime lacks usable LFS credentials.
Required public assets were downloaded through GitHub's public media endpoint and
verified against their LFS SHA256/size, including minimal whole-map dependencies
and frozen source snapshots. No scene was opened from a text pointer.

The S5 style slice passed the independent Luna development gate. Its final-quality
category scores remain 91–94; this does not accept the corridor. The full F1 module
has replaced the original visible assemblies and preserved the outer-wall bounds,
16 camera transforms, 34 interface markers and nominal route clearances.

F1 cold validation found four physical contact defects: a cable-ladder sample at a
panel joint, a luminaire mounting on a ceiling seam, a cabinet bracket at a lining
transition, and a floating pail label. They were corrected in F2. F1–F3 full reviews
are complete and remain below the target. Final acceptance requires every category and every
area strictly above 98, with at least four complete review cycles and two stable
final cycles. No final acceptance is claimed.

## Full review F1

Luna inspected all 16 fixed views. Category scores: 82 / 82 / 79 / 78 / 83 / 76 / 78.
Area scores: 83 / 87 / 80 / 80 / 77 / 77 / 72 / 78 / 77. Report:
`critics/luna-full-F1.md`. Full visual acceptance FAIL; no threshold achieved.

Five repair targets for F2: remove the coplanar floor/ceiling finishes at the frozen
plant/bypass cell overlap; introduce actual pressed/repaired wall panels and
impact protection plus warm/cool service zones; rebuild transfer-leaf subpanels,
compression hardware and human-height handles; improve practical light hierarchy;
add a specific handover/interlock installation and park the gate kit on a formed
rack. Close roof transition gaps revealed by the live-map render with fabricated
service bulkheads/roof closures. F2 geometry saved; cold checks precede rendering.
Comparison outcomes remain pending until the identical views are inspected.

F1 live map check loaded 353 owned objects at the existing identity placement,
hid the old fuel render cache and 51 old fuel lights, rendered C03 in the actual
main map, and preserved its SHA256 byte for byte. The canonical map contains old
missing-ID warnings in other room libraries; these are reported without claiming
that every legacy linked object was repaired. Main integration is not runtime
acceptance.

F2 cold checks PASS with zero failures: exterior/floor footprints, 16 fixed
cameras, 34 preserved interface-marker transforms, support/attachment contacts,
packed resources and sampled nominal route widths. 530,972 source triangles,
536,060 evaluated triangles, 292 mesh objects; these are authoring measurements,
not Unity performance. All 16 F2 views are rendering at 960×640 / 32 samples.
The standard `blender --python open_map.py` entrypoint was cold-opened successfully
and installed 390 live fuel objects, so this branch displays the updated source
through the existing map launcher. Main/native/cache files were not saved.

## Full review F2

Independent report `critics/luna-full-F2.md`; all 16 images and hash/settings
manifest inspected. Category scores 87 / 87 / 82 / 82 / 85 / 86 / 82; area scores
87 / 89 / 85 / 85 / 81 / 85 / 85 / 84 / 82. FAIL against >98 in every category
and area. All five F1 targets improved, none clearly regressed; construction and
light changes remain incomplete at whole-scene scale.

F3 targets: large functional service assemblies in empty architectural bays;
readable branch-specific wayfinding; stronger localized light/material separation;
object-specific door/cast details; downstream clean/plant/waste work evidence.
Add supplementary player-height waste/clean views without moving the original 16.
The waste camera is farther west than the reviewer's approximate suggestion to
frame the full portal; the clean camera sits 0.40m inside the wall rather than on
the frozen Y18 wall plane. A separate closed-pose leaf diagnostic will score the
otherwise correctly concealed freight leaves.

F3 native SHA256 `8d6af812aee50cfabe9d9dc5ceb12d64e3dbc5d9503134b8fecb0ad99c71140d`.
Cold validation PASS, zero failures, including new service assemblies and routes.
548,744 source / 553,832 evaluated triangles, 298 mesh objects. Render pack now
uses 1280×853 at 32 samples to improve inspection of surfacing. It includes the
original 16 plus three documented supplementary cameras. Independent F3 review
was completed. F3 is not accepted as final art.

## Full review F3 and current F4 development

Independent report `critics/luna-full-F3.md`; all 19 native-state images plus the
closed-pose freight diagnostic were opened and their hashes verified. Categories:
90 / 91 / 86 / 86 / 89 / 90 / 86. Areas:
89 / 92 / 91 / 87 / 89 / 90 / 89 / 89 / 85. FAIL against >98 throughout.
The reviewer accepted the builder's ray evidence correcting a false C03 floor
outline attribution: the dark frame belongs to the wall bay; pale lines beneath
the carrier identify its parking berth. Scores were not forced upward. The report
also corrects the clean-label attribution: white-on-cream direction text is in C07;
E02's white-on-dark portal header is weak through shadow and top-edge cropping.

F4 adds distinct physically tiled personnel and freight routes, revised tactile
plaster and paint response, a connected twin fuel-conditioning bank, a draped
canvas/respirator rack, hollow extraction/clean-air headers, a real portal-mounted
leaf-inspection hood, and a clean stock/log cluster with cloth, a canvas bag and
refill bottles. F4a exposed two mounting faults; F4b corrected them and passed
cold validation. F4c includes the complete clean cluster and is archived as
`fuel_full_F4.blend`, SHA256
`dabe7628ee596e93df007326373cf9ef05776a657e59ca77755b1dabee0d7278`.
Its official cold checks PASS with zero failures: 668,636 source / 673,724
evaluated triangles, 309 mesh objects. All 19 full views are rendering at
1280×853 / 32 samples; independent visual review remains pending. Build inputs are
now fingerprinted in the native collection and manifest; a build rejects inputs
that change while it runs. Historical cold checks can select the matching archived
manifest and output path explicitly. No visual acceptance is claimed.

The task is durably published in draft PR
https://github.com/CameronNel/critical-shift/pull/70 through verified Git Data API
blobs/tree/branch, with an exact match to the local committed tree. The draft is a
development checkpoint and ongoing iteration continues on the same branch.

## Full F4 review and F5 continuation

Luna completed the fourth full review against the spawn reference: categories
92 / 92 / 89 / 86 / 92 / 91 / 89; areas
91 / 93 / 92 / 89 / 91 / 91 / 91 / 91 / 90. Every score remains below the
strict >98 target. Four cycles are complete; two stable accepted final cycles
have not been achieved.

Factual challenges corrected the C07 sign attribution (dark ink, with a small
distance read) and the inspection hood (above the closed diagnostic crop; its
illumination improves leaf/glazing visibility). No scores were overridden.

F5 rebuilds staging and the visible east-turn wall as true blind service bays,
adds connected calibration/cooling assemblies, gives the clean route real ceramic
courses, and replaces reactor/plant/clean door hardware and apertures with distinct
construction. The plant hose reel, log placement, directed floor borders, formed
reactor sheets and open freight header address route-specific review findings.
The outer wall bounds and original review cameras remain protected.

The cloud executor disconnected during the last repair. The procedural continuation
has been recovered on this branch through the GitHub connector. Its new native
build and cold/visual evidence are pending a bounded hosted Blender run. The
published native remains the numerically verified F4 checkpoint until that run
passes its cold checks and completes all render manifests. No final art acceptance
is claimed.

## F5ci hosted execution

Native SHA256 5f7de9035b966bf1e152f338e25d9cab1b8d5922db36b1e49303b9562aee6536. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 746244, "evaluated_triangles": 751524, "mesh_objects": 318, "material_batch_upper_bound": 1243}.

## F5ci independent review and F6 target

F5ci hosted build, cold validation and all 19 full views plus the closed-leaf diagnostic passed evidence checks. Native SHA256 5f7de9035b966bf1e152f338e25d9cab1b8d5922db36b1e49303b9562aee6536. Independent Luna category scores: 95 / 95 / 93 / 89 / 94 / 94 / 92. Area scores: 94 / 96 / 93 / 94 / 93 / 93 / 93 / 94 / 95. No acceptance threshold reached. See critics/luna-full-F5ci.md.

F6 geometry targets: rebuild the lower freight header as an open formed channel, raise/enlarge the motor optic to soften the hotspot, stepped entry ceiling trays, distinct extraction shield wall masses, plant gallery baffles and formed vent guards on its doors, a real waste sealing/receipt step and a supported bypass coupler roll, legible clean signs with a physical reading optic, and distinct transfer/clean floor groups. Outer concrete footprints, fixed cameras, markers, floor cells and interfaces remain guarded.

Hosted rendering is split into three workers using the identical cold-checked native bytes, with all view/settings/hash checks performed before bounded publication. Technical status is not an art score. F6 is pending complete render and independent review.

## F6ci hosted execution

Native SHA256 ae37ef4b7011d32170ca6a95c461f255670df7db7fd9d8ce98db72a438824d0f. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 784028, "evaluated_triangles": 789308, "mesh_objects": 323, "material_batch_upper_bound": 1283}.

## F6ci independent review and F7 development

Luna independently opened all 19 full F6ci views, the closed-leaf diagnostic and the actual spawn reference, verifying the native and image hashes. Category scores: 96 / 96 / 94 / 90 / 95 / 95 / 93. Area scores: 95 / 96 / 94 / 95 / 95 / 94 / 94 / 95 / 96. No score reaches the strict >98 gate; see critics/luna-full-F6ci.md. The reviewer corrected the earlier continuous-solid-channel attribution: F6 physically and visibly has open bays; remaining support/value separation was a lighting issue. No visual score was overridden.

F7 rebuilds a physically suspended lower entry canopy under the unchanged roof, hollow service crowns over the crossing, a clean-air ceiling spine with gaps for the original fixtures, actual formed crossing-wall jackets and open folded entry heat-recovery fins. It also changes the reactor portal's pressure-jacket section, plant isolation/backflow assembly, supported purge handover position, waste B/017 receipt/bin relation and approach sign/optic construction. These are construction changes, not a material-only pass. The concrete exterior bounds, nominal interfaces, floor cells, fixed cameras and marker transforms remain guarded.

Focused native drafts were cold checked and rendered without changing the original cameras. Luna confirmed the motor fixture is now entirely inside D05, the freight lower channel is visibly open and internally lit, the C07 sign is readable, and the E01 IDs link bin and receipt. These draft observations are not final scores. Full F7ci render and independent review remain pending. The published F6ci native remains the selected remote module until the new hosted build passes its numerical checks and completes all 19+closed evidence records.

## F7ci hosted execution

Native SHA256 30e4ca9bc23c03c87fe460b5754f6abfc438853237e0c4253c7357bddb7ef3cb. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 872344, "evaluated_triangles": 877624, "mesh_objects": 327, "material_batch_upper_bound": 1312}.

## F7ci independent review and F8 construction

Luna opened and hash-verified all 19 F7ci views, the closed leaf and all four actual spawn references. Category scores: 97 / 97 / 95 / 92 / 96 / 97 / 94. Area scores: 97 / 97 / 97 / 96 / 97 / 96 / 96 / 96 / 97. All remain below the strict >98 gate. See critics/luna-full-F7ci.md. The review's F6 freight attribution was corrected: F6 already visibly has open lower bays; F7 retains those bays and improves motor framing and internal visibility. No visual score was overridden.

F8 develops connected process compositions: a complete split extraction bay with a caged impeller, replaceable filter drawer, folded collector hood, service instruments, age card, catch pan and continuous riser; fin-bank breaks with a closed access cassette and an exposed guarded copper coil; timber cart-impact repairs grouped with a handover board and retained ring spanners; a shallow used-linen return hood over an actually sagging sewn bag and draped towel; keyed cooling-return and reactor-arrival check stations. The bypass hose is shortened and parked above the open purge roll, preserving visible labels and working access. A real roof-supported inspection flood exposes freight rear supports without flattening the route lighting, and the inline plant valve is spaced away from the fluorescent. The redundant small clean direction plate becomes a wipe/log instruction; the large CLEAN arrow and bright S02 header remain.

Local drafts are development evidence only. An initial new extractor mount/kick-panel penetration and a 68 mm linen hood lane intrusion were caught by cold validation, then repaired by relocating the extractor onto the upper lining and manufacturing a shallower return enclosure. Final F8ci native, all-view evidence and independent scores are pending. F7ci remains the published selected native until the new hosted cycle passes all numerical and image-manifest checks. No final art acceptance or Unity readiness is claimed.

## F8ci hosted execution

Native SHA256 3629551c379a87f6ee2983f5ad535036b9a34f783cc0ba9365c210a2c05fa80a. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 895022, "evaluated_triangles": 900302, "mesh_objects": 333, "material_batch_upper_bound": 1358}.


## F8ci independent review and F9 construction

Luna opened the actual hosted F8ci native/render evidence and all four actual spawn references. Category scores: 98 / 98 / 97 / 97 / 98 / 98 / 97. Area scores: 98 / 98 / 98 / 98 / 97 / 98 / 98 / 98 / 98. Every score remains below the strictly greater-than-98 gate. See critics/luna-full-F8ci.md. There are no accepted stable cycles.

Factual challenges corrected two unsupported deductions: E03 has all route-essential cues and D05 supports are readable; the staging assemblies also read and foreground crop alone is analogous to spawn. The report preserves its independent scores/FAIL and now cites broader composition/material/light gaps. Cart boards are impact boards, not shelves, and deep freight recess/contact shadows require no additional fill. No art score was overridden.

F9 connects existing work groups through actual construction: a bounded, backed cart-service bay containing transfer checks, retained spanners, PPE and replaceable timber impact boards; a rolled washable linen-exchange bay combining the return hood, draped towel, stitched bag and retained log; a cooler-frame-supported return lockout rack with a formed primary state plate; and a spent sealed cartridge physically staged on the waste receipt pan with tied receipt and matching B/017 identity. The handover board is relocated within the fixed entry view, and key isolation/linen words grow while secondary engineering labels remain restrained.

A real F8 candidate main-map render, with canonical main, R17 and the required 11 current exterior libraries restored and LFS-hash verified, revealed small ceiling/wall corner light leaks. F9 adds internal folded junction closures without moving the protected exterior cores. A formed freight meeting astragal and compliant seal close the 16 mm closed-pose sightline. Runtime actuation is still unverified.

The first F9 draft exposed one unsupported PPE bracket outside the new bay backing; the backing was extended and a corrected build is undergoing cold and pixel checks. Local drafts remain development evidence. F8ci is the published selected native until F9 hosted checks and all-view manifests pass. Independent F9 review and final acceptance remain pending.

F9b local native SHA256 c290c555da23cae06fdd58a29468018d31b4521b6308285c299218e4f1e85b1b. Cold validation PASS with zero failures; 49 exterior cores, floor cells, original camera/marker transforms, support/attachment contacts, packed dependencies and sampled route envelopes remain guarded. Affected fixed-view drafts are rendering. No visual acceptance is claimed.


F9 pixel development corrected a new board/post intersection by placing the board between structural posts; the complete board is visible in both C01 and C04. The closed freight diagnostic shows the real meeting seal closing the sightline. The normal map launcher on the F9c candidate passed repeat-install idempotence, module/source/recipe pairing, identity placement and hiding 51 old fuel lights; canonical main/R17/spawn hashes remained unchanged. Its actual assembled C03 render proved the ceiling-corner closures worked, and exposed smaller residual slots beside the service bulkhead grille. Subsequent construction closes those slots by overlapping the side sheets with the grille/frame and adjoining sheet.

Later F9 construction gives the waste seal station and distribution cabinet their own rolled handoff bay, clearly separate from reactor RETURN; fits that frame between structural posts; integrates the existing delivery paperwork ledge into a rolled arrivals/receipt bay with retained papers and a practical; and groups reactor interlock, keyed isolation and fire equipment on a bounded cream arrival checkpoint. These are task-specific construction changes, leaving the intervening wall fields quiet. Final candidate cold/pixel/main integration and hosted F9ci evidence remain pending.

F9f candidate native SHA256 4840cad9bb84950f7da48b4077f035710c3c00674db63a7d9656c43b38cb6cd8, recipe e7e156f58000a37b3e161fd65caf63df37f486588f149675926ecc2329d0ac20. Cold validation PASS with zero failures. Root opened all six affected F9f fixed draft images and verified native/image hashes, plus both earlier unchanged C01/C04 corrections and the sealed freight diagnostic. Final candidate map integration is pending. Hosted F9ci will rebuild the identical recipe and produce its own cold-checked native and full 19+closed evidence; technical completion is not an art score.

## F9ci hosted execution

Native SHA256 68d9f2e66a8ed36fd395691a8f0ead9c726a619116000d6e04d6fdf7bbd7ac96. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 937758, "evaluated_triangles": 943038, "mesh_objects": 334, "material_batch_upper_bound": 1385}.

## F9ci independent review and F10 structural pass

Root and pessimistic Luna opened all 19 actual F9ci views, the closed freight diagnostic and all four frozen spawn references; all native/render hashes matched. Category scores remain 98 / 98 / 97 / 97 / 98 / 98 / 97. Area scores are 98 / 98 / 98 / 98 / 98 / 98 / 97 / 98 / 98. Formal decision FAIL; zero accepted stable cycles. See critics/luna-full-F9ci.md.

Luna credited the F9 task bays, full board clearance, separated reactor/waste circuits, mounted linen exchange and staged B/017 receipt. On factual challenge it clarified that fuel is judged against spawn's construction, composition, material/light refinement and purposeful occupancy in its own industrial use, without requiring briefing/locker rooms or new side openings. It identified no additional substantiated contact or fabrication failure; all remaining targets concern process-bay integration, clean-threshold architecture, localized construction/material continuity and route-level light progression. No score was overridden.

The unchanged broad category scores across F8/F9 trigger the authority's structural-pass rule. F10 replaces the orange field behind the existing extractor with an actual bounded, splayed folded-steel process enclosure and removable back pans; relocates the internal service stud out of that enclosure; adds a connected cart-height steel kick lining; rebuilds the existing bypass clean-check wall as a ceramic alcove with shallow formed returns; and continues a folded sanitary cornice along the existing clean wall returns. Protected concrete, route envelopes and external portals remain guarded. It reduces selected general ceiling fills and uses visible supported inspection practicals at extraction, bypass and plant tasks to establish approach/falloff. No unrelated prop count is added to substitute for architectural repair. Local cold/pixel checks and final hosted F10ci evidence are pending; no art or Unity acceptance is claimed.

F10a development review opened eight fixed-view drafts. Luna confirmed improvement in the four structural targets, with no new visible collision or lost cue except reduced contrast on C07's directional sign. F10c restores a dark, high-contrast CLEAN direction plaque; replaces the delivery/arrival wall's broad plaster field with formed removable wash-down steel panels, plus cart-impact timber in a separate side bay; and replaces clean-wall square rubber bases with actual curved sanitary coves. The stock rack is moved 60 mm off the cove so its rear feet do not intersect it; route validation remains required. No aesthetic score is assumed from these repairs.

The hosted view matrix expands from three to six balanced workers, retaining the exact same 19 cameras, 1280x853 resolution, 32 samples, cold-checked native and one closed freight diagnostic. AST/YAML checks verify complete ordered camera coverage and matching matrix IDs. This changes review latency, not the art bar or render quality.

Luna opened all five corrected F10c views and verified the actual evidence hashes. The CLEAN sign regression is repaired; delivery steel/impact timber reads as appropriate attached construction; the continuous sanitary cove and clear stock-rack feet are visible; reactor RETURN and waste HANDOFF remain separate. It identified no additional specific construction, lighting, material or composition defect and explicitly said the remaining quiet wall/tile fields do not warrant further dressing. This is draft feedback, not a formal gate score.

Normal-map development exposed 30 historical fuel material IDs still referenced by the hidden main cache, dropped when old visible art was replaced. F10d preserves those names as compatibility-only unassigned copies of the new materials, after orphan cleanup; the live mesh assignments remain unchanged. The portable normal-map validator now requires these linked IDs to resolve and no missing fuel materials. The frozen main/R17/spawn files are not rewritten. F10d native fbf03257241b03bf9237881f0da7c4e77de239d39bb18da0bedbdd27499d5144, recipe 1dbefb4c1d5dc85b33d2cc34f4619bb904b3e6c7f85264858503e2cb11af6311, cold PASS0. Final normal-map check and actual final-draft renders are pending before hosted source publication.

F10d final candidate proof: root opened all three actual final-draft PNGs (D04/C07/C08), all image/native hashes match, and the compatibility-only change retains the corrected visible result. The normal repository map launcher passes repeat-install identity/count/matrix checks, selected-source/recipe/cold pairing, all 30 historical fuel material IDs resolved and zero missing linked fuel materials. Frozen main/R17/spawn hashes remain exact. Other historical spawn/PPE object-ID warnings remain in the frozen main; no claim is made that all map-linked data are warning-free. Hosted F10ci will now rebuild this exact recipe and render all 19 views plus the closed diagnostic before independent formal scoring.

## F10ci hosted execution

Native SHA256 663b7addb307948dc9b65d095af34efc3281abe78ea0e27dacce4d097e82afd5. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 956554, "evaluated_triangles": 961834, "mesh_objects": 338, "material_batch_upper_bound": 1399}.

## F10ci independent acceptance and F11ci stability cycle

Root and pessimistic Luna opened all 19 actual F10ci full views, the closed freight diagnostic and all four frozen spawn references, verifying native and image hashes. After reopening the challenged views, Luna withdrew unsupported smooth-wall and generic coverage deductions: D04 visibly has formed steel pans, horizontal ribs and timber impact boards; C08's opposing clean-stock and linen tasks are linked by the ceiling spine; C06 is fabricated door detail; and C10 has a distinct plant baffle ceiling, water main, valves and fluted construction. No aesthetic grade was forced or overridden. The corrected independent report scores each of seven categories and each of nine areas 99. See critics/luna-full-F10ci.md. F10ci is the first accepted full visual cycle.

The actual published F10ci native 663b7addb307948dc9b65d095af34efc3281abe78ea0e27dacce4d097e82afd5 passes the normal open_map.py launcher: selected source/recipe/cold pairing, identity placement, repeat-install idempotence, 51 old fuel lights hidden, all 30 historical fuel material IDs resolved and zero missing fuel materials. Canonical main, R17 and spawn hashes remain exact. Historical unrelated spawn/PPE ID warnings remain; this does not certify the whole map as warning-free.

F11ci rebuilds the identical construction recipe 1dbefb4c1d5dc85b33d2cc34f4619bb904b3e6c7f85264858503e2cb11af6311 with no modeling, materials, lighting, camera or reviewer-standard change. It will cold-open, render all 19 fixed views and the closed diagnostic, rehash all evidence and receive a new pessimistic Luna review. Second-cycle acceptance and final main-map render proof remain pending. No Unity or final owner acceptance is claimed.

## F11ci hosted execution

Native SHA256 4de5ea95e03bd21d10e1771b926bbc63c3405dae6cd58d88a3d156bb9bdc2b65. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 956554, "evaluated_triangles": 961834, "mesh_objects": 338, "material_batch_upper_bound": 1399}.

## F11ci independent acceptance and final map closure repair

Fresh pessimistic Luna opened and independently hash-verified every actual F11ci view, the closed freight diagnostic and all four frozen spawn references. Each of seven categories and nine areas scores 99, with no substantiated defect in the standalone fixed views. See critics/luna-full-F11ci.md. F10/F11 provide two materially stable accepted standalone cycles; this does not waive the final assembled-map inspection. The critic correctly distinguishes native open freight views from the temporary closed diagnostic.

The exact F11ci native passes the normal launcher and renders in the actual main map while main/R17/spawn and 11 required current exterior libraries remain byte-exact. All 30 hidden-cache fuel material IDs resolve, with zero missing fuel IDs; 128 historical unrelated spawn/PPE IDs remain warned. The final main image exposed a narrow bright strip beside the waste portal's upper closure. Source rays proved a real sightline outside, rather than a designed viewport.

F12 completes only that existing closure: a wider folded pan covers its jambs, full-depth end/top/bottom returns bridge the 0.50 m inset to the original lining, a real rear sheet closes removable pan seams, and the backing overlaps the original header beam. The initial widened pan and short-return candidate still missed some rays, so they were not promoted. Final F12c candidate a96ff6d12dd333d9c3977bf19c2d9bac387e90e292c048cd7f19fafd0e021ecd, recipe 88857cf4e2d345469647886034c77b0de3fd35ac56f1c95296acd8569b569093, cold PASS0 and 30/30 sampled bright-strip rays hit actual corridor geometry. This is numerical development evidence, not visual acceptance.

No material, light, camera, work assembly, protected core, route or portal contract changes. Hosted F12ci will rebuild that exact recipe, cold-open and render all 19 views plus the closed diagnostic. Independent full review, stability against F11 and actual repaired main-map pixel inspection are required before final handoff.

## F12ci hosted execution

Native SHA256 0a13ff2fe1eadc8608223bd40810285a375a02edacfdfac615263cffe5196f87. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 956486, "evaluated_triangles": 961766, "mesh_objects": 338, "material_batch_upper_bound": 1399}.

## F12ci final visual and authoring-map handoff

The full hosted run [36991740812](https://github.com/CameronNel/critical-shift/actions/runs/36991740812) succeeded: native, six render groups and bounded publication. Root and the fresh pessimistic Luna reviewer opened the complete 19-view pack, closed freight diagnostic and all four frozen spawn references, rehashing the exact files. Earlier official artifact PNGs are byte-identical to the published files. All seven categories and all nine areas score 99. See [luna-full-F12ci.md](critics/luna-full-F12ci.md) and the preceding [F11ci report](critics/luna-full-F11ci.md). Both final full cycles are accepted and materially stable; the standards remain unchanged.

Selected native SHA256: `0a13ff2fe1eadc8608223bd40810285a375a02edacfdfac615263cffe5196f87`.
Recipe SHA256: `88857cf4e2d345469647886034c77b0de3fd35ac56f1c95296acd8569b569093`.
The selected source and [archived F12ci checkpoint](checkpoints/fuel_full_F12ci.blend) are byte-identical; current and archived build/cold reports agree. Cold validation PASS, zero failures. All 49 protected exterior cores have zero bounds change; 14 floor footprints, original 16 cameras, 34 interface transforms, attachments, support contacts, packed dependencies and sampled nominal route envelopes pass their existing checks. Authoring measurements are 956,486 source / 961,766 evaluated triangles and 338 mesh objects; these are not runtime performance measurements.

[F11_F12_STABILITY.json](F11_F12_STABILITY.json) compares all 20 matching frames, verifies identical camera transforms/lenses and available render settings, and records the single changed recipe input (`build_overhaul.py`). Its maximum per-view mean absolute RGB-channel difference is 0.442784 on an 8-bit scale. The record does not substitute for independent pixel inspection or aesthetic scores. Materials, lights, review cameras and work assemblies were not changed by the closure repair.

The exact published F12ci native passes the normal `open_map.py` launcher, including identity placement, repeat-install idempotence, 495 linked objects, 51 old fuel lights hidden and all 30 historical hidden-cache fuel material names resolved. See [MAP_LAUNCHER_VALIDATION.json](MAP_LAUNCHER_VALIDATION.json). Root opened the [actual assembled-map C03 render](renders/integration/F12ci_complete_main_C03_HERO.png); the former bright slit is gone. [MAIN_LINK_VALIDATION.json](MAIN_LINK_VALIDATION.json) pairs that PNG and the selected native. The PNG SHA256 is `7c2645794d3792d416147c517a32d416fcd525112f2183b9803a41a11a5f93f2`. [F12ci_EDGE_RAY_VALIDATION.json](F12ci_EDGE_RAY_VALIDATION.json) records 30/30 targeted rays hitting actual corridor geometry.

[MAIN_DEPENDENCY_VALIDATION.json](MAIN_DEPENDENCY_VALIDATION.json) verifies that canonical main, immutable R17, selected spawn and all 11 required current exterior libraries remain byte-exact. The map has zero missing fuel data IDs. Its 128 historical unrelated spawn/PPE ID warnings remain; this work does not accept every old map-linked cache or claim the whole map is warning-free. No canonical main or other room native was saved.

Successful local final commands (repository root, Blender 5.2.1 LTS):

```sh
blender -b -t 4 --factory-startup --disable-autoexec --python-exit-code 1 --python sections/fuel-corridor/blender/validate_live_map.py
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python open_fuel_overhaul.py -- --render C03_HERO --out sections/fuel-corridor/production/renders/integration/F12ci_complete_main_C03_HERO.png
```

The hosted cold/native/view commands and exact logs remain under `ci/F12ci/`, along with the exact final normal-map, assembled-render and ray-check logs. Read-only pixel comparisons and the targeted geometry rays passed; no PNG was retouched. The initial incomplete F12a/F12b closure candidates remain local development evidence and were not promoted. F12c's full closure recipe was selected only after cold and sightline checks, then rebuilt into F12ci and independently reviewed.

Published for independent review in [draft PR70](https://github.com/CameronNel/critical-shift/pull/70); no agent merge. Open the delivered module through `blender --python open_map.py`. Directly opening the canonical map file retains its historical cache. Visual/authoring acceptance does not certify Unity, motion/controllers, continuous collision, adjacent-room traversal or runtime performance. Owner art approval and merge remain separate.


## Owner atmosphere revision — F13 development

The owner requests gloomy, eerie, rundown and ominous atmosphere, failing and red lights, dark intervals, worn/missing tiles and open ceiling damage. Latest reactor WIP PR54 (`c555e4e0f08eeb73edcc9115f185223badc194e5`) is the atmosphere reference; reworked spawn remains the craft reference. The previous F12 scores do not approve this new revision. Native floor/wall footprints, original cameras and interfaces remain protected. F13a builds actual recessed missing/broken floor tiles and two bounded open ceiling service bays, isolates keyed failing optics/light energy and mounts three red alarm fixtures. New cold, visual and temporal checks are pending. No new acceptance score is claimed.

## F13ci hosted execution

Native SHA256 c51f6f1fc397de024fa90cbb3acc3578501a8cb3ae660ea8b40a8a6f810ccf2a. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 985390, "evaluated_triangles": 990670, "mesh_objects": 341, "material_batch_upper_bound": 1428}.


## F14 development: visible practical failure

F13c event inspection verified evaluated energy/emission changes but found the
entry camera's visible staging bar remained steady. Native camera projection
resolved an initial wrong-fixture attribution: the keyed Entry fluorescent is
above C01's frame; Staging main is the visible bar. F14 adds phased Staging main
and Bench practical keys without moving cameras or geometry. The staging base
reduces to 80 W; existing independent task lights retain route anchors. Luna
opened native F14a event frames 28/29/30/31 and 32/33/37/38 in C01/C03: staging
source dimming/dropout/recovery is visibly effective and routes remain legible.
Bench fluctuation is a subtle secondary variation, not the primary failure cue.
Cold checks and every-frame 1–241 evaluation pass. Timing review at target speed
and full F14 visual acceptance remain separate and pending. No score overridden.

## F13ci independent atmosphere review and F14 continuation

Pessimistic Luna opened/hash-verified all 19 published F13ci fixed views, closed
E03, all four actual spawn references and all five latest PR54 atmosphere
references. All seven categories and all nine areas score 99 for the requested
gloomy/rundown still-image set. Report: `critics/luna-full-F13ci.md`. No old F12
scores were carried into this decision. Native/cold/render SHA is
`c51f6f1fc397de024fa90cbb3acc3578501a8cb3ae660ea8b40a8a6f810ccf2a`.
Temporal cadence and whole-map art are outside this still-image decision.

F14 is a bounded temporal refinement, with no intended construction or camera
change. Full F14 review and comparison to the complete F13 set remain pending;
the final two full cycles must show no material regression before handoff.
Thirteen complete full cycles are recorded, including the fresh atmosphere
review; the protocol's four-cycle minimum remains exceeded.

## F14ci hosted execution

Native SHA256 650aec3f1e654e607de0442ae6f2fcf5544b99feb835ff1a709c2fb6b3641484. Cold validation PASS, zero failures.
All 19 full views and the closed-leaf diagnostic are rendered and hash-verified.
All workers used the identical cold-checked native bytes.
Independent visual review is pending; no art or Unity acceptance is claimed.

Authoring geometry: {"source_triangles": 985390, "evaluated_triangles": 990670, "mesh_objects": 341, "material_batch_upper_bound": 1428}.
