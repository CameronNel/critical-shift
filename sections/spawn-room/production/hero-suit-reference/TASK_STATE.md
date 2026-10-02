# HZ-01 reference revision — 2026-10-01

Phase: final source and rendered evidence, awaiting owner art review.
Branch: `codex/hero-suit-reference-20261001`, based on `claude/spawn-polish`
at `178ba323126e4d1b5fdab2f4788b07ebef7f1d39` (PR #67).
One primary author; no merge or promotion to main.

## Review history

| Review | Opened pixels and observed defects | Correction |
| --- | --- | --- |
| Baseline | `baseline/baseline.png`: smooth generic hood, small kit details, broken slab/toe outlines | Preserve the worker/equip pipeline; replace hood construction and boot shapes |
| R01 | `review/R01/baseline.png`: mirrored sleeve labels, absent belt band, reflection over eyes | Fix projection handedness, construct continuous belt, improve stage and fabric |
| R02 | `review/R02/suit_turnaround.png`: pale yellow under AgX, broad visor reflections, sleeve creasing and boot proportions | Restore stronger yellow, add construction seams, warning panels and local wear |
| R03 | `review/R03/suit_hero.png`: mixed refracting/transmitting paths produced a double face | Use a thin surface visor with Fresnel reflection and clear transmission |
| R04 | `review/R04/suit_hero.png`: exposed yellow neck inside visor and poor leg-warning placement | Extend and fit the head inside the hood; relocate warning labels |
| Final refinements | First full-resolution hero exposed the lower head outside the hood; a large collar obscured the rim | Constrain the head behind the fabric opening and use a compact neck seal |
| Cuff cleanup | Owner crop showed dangling radial ribs below both wrist rings | Remove the rib geometry from both cuffs; rebuild both native scenes and rerender all fixed views |

Named hero/front/side/back cameras are saved in the wearable scene. Camera
transforms are fixed; lighting and colour changes between early experiments are
recorded by each validation report and are not strict material A/B comparisons.
No invented rubric score or whole-room acceptance is assigned.

## Technical evidence

The native scenes are generated in Blender 5.2.1 LTS. Faces are packed and labels
converted to meshes. Skin-region coverage, finite geometry, materials and missing
images are checked by `render_suit_reference.py`. Library placement is checked in
the actual linked room by `validate_suit_library.py`; room contact evidence uses
the existing `validate_contacts.py`. Final counts and measured coordinates are
in the JSON reports rather than copied from historical room statistics.

Cold-start status: PASS. The saved wearable scene reopened in a fresh process;
the 1086 x 1448 hero render at 48 Cycles CPU samples matches the final pixels
exactly (see `COLD_START_COMPARISON.json`).
Linked locker status: PASS, 4/4 instances, no missing libraries, no wearer inside
the empty library. Boot-dock gap is within floating-point precision (about
0.00000003 m); the original top/boot/pack coordinates are preserved.
Support-contact status from the initial reference revision: PASS, 208 tagged
objects, zero failures, using the unchanged existing validator in a task-owned
copy to preserve the room's report. This full-room report was not rerun for the
bounded cuff cleanup; the current four suit/dock contacts were checked again.
Final wearable authoring count: 117,310 source / 120,094 evaluated triangles;
21 visible meshes. This is not an engine budget or performance measurement.
Final hero/front/side/back turnaround and the linked `VALIDATE_Hero_A` locker
render were opened and inspected. Native final scenes contain packed textures
and mesh lettering; the source includes the licensed font for portable rebuilds.
Independent review: not performed; pixel inspection here is author self-review.
Owner art acceptance: pending. Exact pixel identity with the supplied image is
not claimed. Hidden surfaces are inferred from the visible garment construction.

The room module and accepted map are not saved by these checks. The source room
reports a newer Blender file subversion on load; it is used read-only. Its frozen
geometry and materials are not rewritten through this toolchain. The optimized
self-contained room derivative was regenerated afterwards from the linked module
with the locker LOD of this suit (22,371 triangles per suit); contacts, signatures
and the six-camera comparison were re-run on it (see `../optimise/README.md`).

## Publication

The review branch uses a single snapshot against `claude/spawn-polish`, published
through the authenticated GitHub Git Data API. Git LFS uploads still reject this
executor's credential, so the owner requested a workaround. The two suit native
files and this handoff's PNGs are stored as ordinary Git blobs, using three scoped
`.gitattributes` overrides. Each artifact is under 5 MB; the complete change is
about 36 MB. Existing LFS rules for other facility assets remain in force, including `module_optimised.blend`, which the follow-up PR #69 uploaded to LFS and verified from a fresh clone (SHA-256 equals the pointer OID). Clones
receive real suit files rather than pointers to unuploaded LFS objects.

The original three local commits and their LFS object versions are preserved in
the verified portable backup at `/workspace/exports/hero-suit-transfer.zip`. No
merge to main or whole-room acceptance is implied. Independent/owner review is
pending; the draft PR targets `claude/spawn-polish` to keep the revision scoped to
PR #67. The Git storage exception is a delivery tradeoff, not a runtime or art
approval. Re-enabling LFS later requires uploading the binaries before committing
new pointers.

## Glove cuff cleanup

Removed the 84 loose radial rib segments identified by the owner, retaining the
continuous wrist collars. Regenerated `crew_hazmat_reference.blend` and the shared
`hero_suit.blend`. All four fixed wearable views and the linked-locker view were
rerendered; `final/glove_cuffs.png` is a crop of the actual updated hero render.
The source passes Python compilation and the diff whitespace check. The rebuilt
scenes have complete skin coverage and no missing images. All four library
instances retain their attachment coordinates, and the fresh-process render
again matches the saved result exactly. Cameras, materials and room source are
unchanged. Visual checks are author self-review; independent/owner review and
merge to main remain pending. Publication uses the GitHub API workaround above.
