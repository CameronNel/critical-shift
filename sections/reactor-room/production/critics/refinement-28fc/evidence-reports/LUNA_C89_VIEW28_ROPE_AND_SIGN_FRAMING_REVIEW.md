# C89 view28 rope-path and crane-sign review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
**Source SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`

## Original full-quality image

- Image: `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/28/28_main_rope_path.png`
- Image SHA-256: `cd6d598dc873ced43a6b4f679051d5b0ed67f19c41fb431978e609e9884a327f`
- Manifest: `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/28/render_manifest.json`
- Manifest SHA-256: `93b74dcd78dcb4c217c3d36b470cb925db55e080cdf2ceaac488735ee62ce2b3`
- Render: original 1280×720 Cycles CPU, 96 max/32 min adaptive samples, OIDN, 12 bounces, 16-bit output.

## Visual disposition

The image establishes a useful partial for #108: the overhead trolley and visible drum area connect to the suspended rope legs, sheave/block, and hook in one view. The upper motor/drum assembly is small, dark, and partly clipped by this camera, so this frame does not settle the motor/drum construction detail. Keep #108 partial and pending views26/27.

The crane identity text is on the **front face**, but the dark shape at screen right is not a physical blocker over the visible face. View28 looks obliquely along that face and crops it at the camera view boundary. The image shows the line through “CAPACITY” while the remaining text falls outside this view. This is a framing result for a rope-path camera; it does not establish a new sign-placement defect. Keep the room-wide #139 audit open until the other mapped sign views have been reviewed.

The first visual-only read suggested that the dark shape might mask the final words. That was a preliminary hypothesis; the exact front-face ray query below supersedes it. No source or mesh change is justified by view28 alone.

## Saved-scene front-face and support query

The read-only paired probe is `evidence/C89_CRANE_IDENTITY_VIEW28_OCCLUSION_PROBE.py` with result `evidence/C89_CRANE_IDENTITY_VIEW28_OCCLUSION_PROBE.json` (SHA-256 `ed6d5ac3a6728b75d8e5d3f437daeda7946d2582c59f7024ff238f6007156b02`). It loaded the exact C89 blend, checked the image and manifest hashes above, and used the recorded camera poses without saving or changing the scene.

At the saved plate center x=−4.2 m, the evaluated font front is 2.48872 m wide; the plate is 2.65 m wide, leaving 81.9 mm and 79.4 mm end margins. Thus the phrase fits on the physical plate. In view28, 2,232 of 3,628 front-font samples and 216 of 369 plate-grid samples fall inside the camera frame; **zero** in-frame glyph samples and **zero** in-frame plate samples have an intervening mesh first hit. Only two of the four plate corners are in-frame. By comparison, the exact main07 and main08 camera preflight includes all font samples and all four plate corners at the current location, with no sampled front-face occlusion. These are placement/camera probes, not full-pixel acceptances of main07/08 or a room-wide #139 pass.

All four current nameplate stand-off rays hit the actual bridge web at y=4.25 m with outward normal −Y; none is intercepted by a bridge rib. An in-memory x-center sweep found that moving the sign to x=−5.4 m would bring all font samples and plate corners into view28, but in the main07 camera 106 of 3,628 font samples and 13 of 369 plate-face samples then ray-hit `RH refine bridge web service -6.0 housing STEEL` (bounds x=−6.093…−5.907 m, y=3.780…3.960 m, z=15.074…15.286 m). I do not recommend that relocation from this evidence: it trades a peripheral crop in view28 for a real obstruction in the primary crane camera.

The probe tests one sign and three relevant camera poses only. It neither closes #139 nor waives the remaining #108 motor/drum evidence.

## Review update: C89 view27

View27 is now complete and provides a close view of the hoist drum, flanges, wound ropes and braided cable surface. It complements view28's rope/block/hook path. The upper motor housing and its connection to the trolley remain incompletely framed, so #108 stays partial pending view26. See `LUNA_C89_VIEW27_TROLLEY_DRUM_REVIEW.md` for the full hash-bound review of view27. Its image SHA-256 is `34ec531ee22a2392f60ee2cc64b5f399c0797d44f483050c1de1ad488f847a8f`; its manifest SHA-256 is `721b2c6b5ec16804cfcf529a962e62a86f0fb7dc766b585fba077acbd3000edf`.


## Later C89 composite disposition

This view-specific report predates completion of C89 views26 and27. The upper motor/trolley detail is supplied by the bounded historical C82 view52, while current C89 views26/27/28 cover the hook, crane-hoist drum and lower reeving. #108 is now accepted as that explicitly scoped composite in [LUNA_C89_HOIST_COMPOSITE_REVIEW.md](LUNA_C89_HOIST_COMPOSITE_REVIEW.md); this older report remains a view28-only record.
