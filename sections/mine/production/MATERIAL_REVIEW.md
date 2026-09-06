# Gullet material review: 6 September 2026

## Executed environment

Blender 5.2.1 LTS / Cycles on CPU. The official Blender archive passed its published SHA-256 check before execution. Six CC0 material sets were downloaded from Poly Haven and ambientCG, and all 24 map hashes were checked. This revision's build and render evidence uses neither Three.js nor VTK.

## Review 01: first actual Cycles material pass

The first downloaded-material entry render exposed overly bright concrete, insufficient rock relief and teal rolled supports that had escaped the initial material remapping. It was not accepted as the correction.

## Review 02: separation and geological relief

Added the fractured-rock and quarry material sets, controlled saturation and bump strength, separated darker floor concrete from wall concrete, remapped structural arches to charcoal steel and applied bounded geological relief while protecting floor/arch contact bands. All ten fixed cameras were rendered and inspected in the authoring environment. The wet-work views still showed an excessively cyan water treatment.

## Review 03: groundwater and final evidence

Replaced the groundwater material and retained separate dry/damp/fresh stone responses. The final standalone package includes entry, route and sump views at 1280 x 800 / 32 samples, and the remaining seven cameras at 896 x 560 / 16 samples. Denoising is enabled; fixed camera transforms were not moved to conceal defects. All ten image files decoded and matched their recorded SHA-256 hashes.

The repository runner independently rebuilt the committed source, rendered entry/main_route/sump at 1280 x 800 / 32 samples, reopened the saved scene, ran the cold-start checks and rendered entry again. Those independent repo-generated frames are committed under `renders/review/cc0-materials/`; their reports and logs are in `checkpoints/cc0-materials/`. The other views can be reproduced with the canonical builder's `--render all` option.

## Fresh-process result

The independent repository cold-start report records **PASS**, 7,472 checks, and no reported issues. Checks include real bpy sector/gate/rubble state functions, packed scene-used images, unique IDs, finite geometry, UV presence, ten named cameras and 61 standing-clearance rays through visible geometry along the main walkway. The test restores the original scene state after exercising the controls.

These checks are not a complete capsule-controller sweep, a rigid-body simulation, a runtime benchmark or an artistic score.

## Remaining limitations

Some excavation-face and collapse geometry remains simplified and repetitive. Exterior integration ends at the defined facility handoff. Further silhouette/detail-density decisions should be made against the global art bible, not by adding random surface noise. The Blender box-projected materials must be baked or recreated in Unity; a normal FBX/glTF export does not reproduce this node graph or Cycles lighting automatically.

Unity interactions, cart/rubble physics, multiplayer, navigation, collider preparation, audio/VFX and target-Radeon performance remain unverified. This focused three-stage material review does **not** claim completion of the full four-cycle production acceptance protocol. Final art approval remains pending.

The older VTK images are diagnostic history, not Blender evidence or an approved visual target.
