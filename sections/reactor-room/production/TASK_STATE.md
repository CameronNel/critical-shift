# Reactor Room — Task State

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


**Current phase:** Reviewed hall refinement delivered for the owner’s 140-item task; Git handoff prepared.
**Current overall score:** 91/100, independently reviewed by Luna; areas 88–93.
**Open task criteria:** 0 of 140.
**Authoritative source:** [../blender/reactorroom.blend](../blender/reactorroom.blend).
**Source SHA-256:** `28fc09a259369b685ca1f96ad78cfd19bc0992f4ae67b200cb2143d9272905e3`.
**Recorded cold status:** 14 finite checks and separate control-room aggregate pass; 124 declared owned comparisons pass.
**Map/runtime status:** Not integrated into the combined map; Unity performance and runtime export not validated.

## Entry points

- [Handoff and commands](HANDOFF.md).
- [Ten original full-quality 1280×720 views](renders/final/refinement-28fc/gallery.html).
- [Independent final review](critics/refinement-28fc/LUNA_28FC_FINAL_REVIEW.md).
- [File identities and scope](checkpoints/refinement-28fc/handoff.json).

## Completed

The hall refinements cover machinery, floor, control rods, roof, walls, signs, props, materials and support geometry. The last correction moved the complete generator plaque 400 mm forward on fitted stand-offs to clear a conduit in the actual west-wall view. All ten main originals use the accepted source and canonical renderer. Current proof37 shows the full corrected sign. Historical fixture82 retains its original source identity.

## Hall fixes after the reviewed handoff (unreviewed)

A follow-up pass changed the saved scene. **Everything in the sections above describes the earlier reviewed scene (`28fc09a2…`), not this one.** The 91/100 review, the ten gallery renders and the portable verifier all refer to that earlier file; `verify_refinement_handoff.py` now fails on the source hash by design and has not been regenerated.

- Scene SHA-256 now `c80786683c33ddda5005ecbe48c3d2e346b082c83dbc323218e48b3e5bb2d1a4`.
- Wet floor concrete and both wall concretes darkened. The floor has puddle patches and drag streaks: darker, near-mirror smooth, with a clear coat for lamp and pool reflections.
- Lighting moodier: broad wash lights cut to about 40% and tinted cool, uplights reduced, roof shafts and roof-bay lights lifted, six warm roof accent spots added so girders and crane keep structure, world strength 0.16 to 0.05.
- Wall numbers `N-1`..`N-5`, `S-`, `E-`, `W-` (round geometric face with every corner rounded, no stencil cuts, bright chipped paint, 2.4 m x 0.8 m on the panel-field centres) are a texture stencil layer in the two wall concrete materials (packed 3840x1024 atlas, keyed to world position and wall normal, no added geometry). Stencils sit at 3.3 to 4.1 m. `check_wall_number_visibility.py` (finite sample, not a view check): most bays are partly hidden by signs, trim, doors or equipment; N-3 and W-3 sit on door openings, and N-1, N-5, S-1, S-5, E-1, E-5, W-1, W-4 and W-5 have two or fewer of nine samples clear. Placement is not yet adjusted per bay.
- Evaluated triangles (meshes, curves and text, render-visible objects) went from 1,478,532 to 1,165,073 by decimating fifteen-plus over-tessellated, non-interactive meshes. The saved scene is under 1.2 million; the earlier reviewed scene was not.
- Reproduce with `overhaul-R1/scripts/make_wall_number_atlas.py` then `rh_hall_moody_fixes.py` on the reviewed scene.
- Checked with 480x270 Cycles CPU previews of the fixed views plus five inspection close-ups of decimated parts (trolley, bank suspension, turbine base, hook, drums); no damage seen. The Cycles warning 'Maximum number of closures exceeded: 96 > 64' also appears when rendering the reviewed scene, so it is not new. No full-quality render, no independent review, no collision or interface re-check, no Unity measurement. The committed gallery renders do not show this look.

## Review limits and next actions

Use the saved scene as the next authoring baseline. The task’s ≥90 overall / ≥85 area bar is satisfied; this does not advance map-owner or other repository acceptance gates. The broad floor puddle is a recorded minor finish weakness. Registered finite geometry checks do not prove exhaustive access or collision freedom; the control-room aggregate passes while individual front-access subchecks may be BLOCKED.

Read the handoff, hydrate only its LFS files, and run its portable verifier. Further map placement follows the current combined-map instructions when requested by the owner. No fresh whole-pipeline equivalence is asserted. The historic build and render commands retain their original workspace paths in the immutable evidence.
