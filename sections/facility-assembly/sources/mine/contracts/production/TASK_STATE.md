# Gullet mine — task state

Current scene: `blender/gullet/Gullet_Valorant.blend`.
Revision: `valorant-delivery-final`, 9 September 2026.
Blender authoring pass complete. Luna's final presentation review passes all delivery categories at 92–95 in `critics/valorant_delivery_final_scorecard.md`. Unity integration remains separate.

The user requested one coherent pass on the existing mine and delegated selection of screenshot-based ChatGPT concepts. The older minimum-four-cycle protocol was superseded for this task. Six concepts were generated; the slate heading and complementary area references were selected. The reactor was not edited.

## Delivered

- Painted angular slate, dark steel, gunmetal, restrained white and orange accents, with no teal.
- Darker underground mood with warm local beacons and readable routes.
- Refined moving gate panels, cabinet, tool station, connected services, route identifiers, dry/wet excavation faces, sump and collapse dressing.
- Packed slate, damp slate and fresh mineral textures with provenance, alongside the original CC0 materials.
- Twelve actual final renders: ten preserved audit cameras and two clear bay presentation cameras.
- Ordered replay scripts, validated structured shader patches, graph readbacks and file hashes.

## Verification

Fresh-process Blender 5.2.0 LTS validation: PASS, 9,047 assertions, zero issues. This checks real bpy state/gate controls, independent sector progression, 22 removable rubble pieces per sector, packed images, finite meshes, UVs, IDs, cameras and 61 sampled standing-route rays.

Supplemental approach audit: wet branch and sump maintenance-loop rays clear; two low dry-branch rays hit original collectible ore. These hits remain explicitly recorded, not erased. No unexpected structural or new-dressing blockers were found. This is sampled authoring clearance, not a Unity character-controller test.

Original foundation SHA-256: `0d256a170aa6324c3298aec3bbe98f0fd3112b7d814650b9cd063b1962eff97b`, unchanged.
Final scene SHA-256: `1cfa3923bb4c4b82fac99563dfe5a27747f5eb97155a3161726d4746ed973a31`.
All ten original camera transforms and lenses compare equal to the verified source set.

Render settings: Eevee, ray tracing off, 1728 × 1080, 48 samples, 1024 MB shadow pool. The cold-start report's inherited `renderer: Cycles` field is historical; the validation command does not render. Render manifests explicitly record Eevee.

## Review evidence

`critics/valorant_acceptance_scorecard.md` passed all substantive art categories at 92–95. Its sole presentation failure was the original bay camera's foreground support occlusion (89). That original view is preserved in the comparison appendix; a clear elevated `bay_delivery` camera was added for delivery and independently rated 95. The final scorecard reviewed all twelve images and passed every final delivery category at 92–95. The occluded audit view remains honestly recorded at 89 and is not used as final presentation. Historical rejected scores and renders remain available.

## Open and reproduce

Read `../AGENT_READ_FIRST.md` and `VALORANT_REPLAY.md`. After reopening, run `blender/gullet/register_controls.py` to restore the Gullet sidebar without rebuilding. `VALORANT_GALLERY.md` separates real scene renders from generated concepts. `valorant-delivery-manifest.json` verifies files and camera preservation.

## Engine boundary

Unity material baking/recreation, collision and navigation, interactions, cart/rubble physics, networking, audio/VFX, LOD/batching and target-hardware profiling remain engine work. No runtime frame-rate or completed Unity gameplay claim is made. Visible base meshes total about 398k triangles; this is not evaluated modifier geometry or draw-call count.
