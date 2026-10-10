# 677c hoist tasklight: independent fit and preview review

**Candidate:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Candidate SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`  
**Parent source:** 5fd `5fd5f7b0f21383348f8fa450609057be01f17cd9426758bfe7ab6ada48565779`  
**Scope:** inspect only the three added aperture-edge tasklight objects, their seat and material assignments, the aimed light, and attachment to the moving trolley. This is not full-view acceptance or a lighting review of the full scene.

## Saved-geometry findings

The saved delta declares exactly three additions (`RH hoist anchor tasklight housing`, `RH hoist anchor tasklight lens`, and `RH hoist anchor maintenance LED`), zero retained-object changes, 1,951 unchanged objects, and no removals or unexpected changes. Its comparison covers object matrices/parents, mesh surfaces/material indices, material graphs, existing light settings, and cameras.

The housing is a closed positive-volume mesh (24 vertices, 26 faces, 48 edges; no boundary or non-manifold edges) assigned throughout to the retained galvanised-steel material. Its two registered points meet the inspection-aperture frame within 0.48 μm. The closed lens (8 vertices, 6 faces) uses the retained practical diffuser material, with all faces assigned; both registered lens-to-housing contacts are coincident at the measured plane. Neither mesh has a material-less face.

All three new objects parent to `R2 crane trolley crane IRON`. At frames 1, 150, 450, and 900, each keeps the same transform relative to that parent (maximum matrix delta 0); the parent translates over this interval. This confirms the fixture follows the trolley in the sampled saved rig poses.

The added source is a rectangular AREA light: 1.2 W, color `(1.00, 0.94, 0.86)`, dimensions `0.38 × 0.01 m`, aimed down and into the aperture. Its emission axis is 42.1°–44.9° from the line to the two clamp top centers, and direct scene rays first hit the corresponding clamp. This is a local, aimed fixture; it does not alter the prior lights or materials.

## Preview judgment

I inspected the actual 480×270 calibration preview at `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/calibration/green/70/70_hoist_rope_anchors.png` (SHA-256 `0239e3369d38ede37e0fa038e1f76fa259223024e5c8a6b8ebca08aeb339d453`; manifest SHA-256 `e52b714212a37e46ffaacb34ca6bb45dc68151328cf5e7769a0320236f35a842`). Both end clamps now separate from the darker drum surfaces, and the clamp faces and fasteners read more clearly. The small warm-neutral source stays localized; it does not wash the aperture frame. The framing and lighting are adequate to proceed with the full-quality view70 render.

This preview does not close issue 116. Final readability, complete fastener visibility, and the rope-end retention appearance remain pending the exact-source full-quality view70. The saved 677c warm and cold candidates subsequently passed all 14 authored checks and the independent control-room check. The cold owned-scope comparison passed 93 declared comparisons; this is bounded repeatability evidence, not a whole-scene equivalence claim. These technical passes do not close issue 116 or replace its required full-quality view70.

## Probe provenance

Read-only Blender 5.2.2 probe: `review/evidence/LUNA_HOA_677C_TASKLIGHT_PROBE.py` (SHA-256 `4431ec375a7246f0a52734ca290b948fb97bbd2205d7e9fc95aa643871c58142`). Its output is `review/evidence/LUNA_HOA_677C_TASKLIGHT_PROBE.json` (SHA-256 `ceb40cf5e7624ea2512b19950f6de0f63a8a92530755529e68956db2adf7b297`); execution log SHA-256 `886ed62d2ca836985c27fd3eaf5b1e72ea9584fcb86d3e29d13a1be634ed58b5`. The probe opens and hash-checks the saved blend; it makes no saved scene changes.
