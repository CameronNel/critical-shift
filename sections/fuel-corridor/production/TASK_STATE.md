# Fuel corridor overhaul state

Phase: full-scene development and independent iteration.
Branch: `codex/fuel-corridor-overhaul-20261001` from `75983b9`.
Source: `sections/facility-assembly/sources/fuel-corridor/module.blend`.
Baseline SHA256: `f01b8647c4a87c88be859fce0659df8c9aaf41a91743f0c83705b8b8cfc0945c`.
Baseline saved at `checkpoints/fuel_corridor_baseline.blend`.

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
