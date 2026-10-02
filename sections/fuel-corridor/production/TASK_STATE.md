# Fuel corridor overhaul state

Phase: full-scene development and independent iteration.
Branch: `codex/fuel-corridor-overhaul-20261001` from `75983b9`.
Source: `sections/facility-assembly/sources/fuel-corridor/module.blend`.
Baseline SHA256: `f01b8647c4a87c88be859fce0659df8c9aaf41a91743f0c83705b8b8cfc0945c`.
Baseline saved at `checkpoints/fuel_corridor_baseline.blend`.

The source has 7,978 objects, 34 materials, 16 cameras, 3 packed images and no
libraries. The task preserves exterior shell footprints/ports while replacing
visible asset construction. Native baseline entry, hero, bypass and reactor views
have been captured. The reworked spawn reference is being rendered from this base.

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
transition, and a floating pail label. Construction fixes are in progress while
all 16 immutable F1 views render. Full-scene visual scoring and main-map live-link
validation remain pending. Final acceptance requires every category and every
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
remains pending. The current native is not accepted as final art.
