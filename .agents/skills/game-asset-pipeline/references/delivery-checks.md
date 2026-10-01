# Delivery and budget checks

Read with [game-asset-pipeline](../SKILL.md). Existing A08 binding and section
contracts govern the handoff; this checklist does not define a replacement manifest.

## Contract and provenance

Record the source revision and selected module/object IDs, export/import settings,
scale/axes/origin, logical section/entity IDs, mesh/prefab mappings, material conversion,
collider/trigger roles, interaction/spawn points, state variants, licenses and the
runtime owner of each binding. Preserve source textures and art evidence. A debug
name, transport ID and logical gameplay ID are not interchangeable.

Use task-specific outputs. Round-trip in a clean scene, not on top of the source:
otherwise retained source geometry can conceal a missing export. Check missing files,
LFS pointers, external paths, tangents/normals, material slots and non-finite geometry.
A bounding-box check alone misses wrong pivots, mirrored transforms and lost children.
Use declared tolerances with units; do not silently choose a permissive percentage.

## Collision and interaction

Render meshes, colliders, triggers and navigation surfaces have distinct roles.
Validate support, intended clearances, door/lever pivots and interaction points in the
same space as the consuming runtime. A hidden mesh must not leave an unintended solid
barrier or remove a necessary collider. Verify the current engine's dynamic-body and
mesh-collider restrictions instead of turning every render mesh into a collider.
Do not add colliders or gameplay IDs to canonical art unless that task authorizes it.

## LOD and resource accounting

Use approved asset-class budgets and target-camera distances. When no budget has been
ratified, report the measured inventory and missing decision, not a fictional pass.
Measure evaluated/exported triangles and vertices, material slots, texture dimensions,
format/mips, bones/influences where applicable and collision complexity. Account for
instances separately from unique data. File size is not GPU residency.

Only create LODs when in scope. Preserve silhouette, material boundaries, UVs, pivots,
skinning and interaction semantics. Inspect transitions from the real gameplay camera;
do not prescribe universal ratios or collapse functional geometry blindly. Render
mesh count and material count are not measured draw calls. Use target-engine profiling
for frame time, memory, overdraw and batching; Blender render speed is not game FPS.

## Animation and material transfer

Record skeleton/rest pose, clip names, frame rate including fps_base, duration, loop
flags, root-motion intent and event/binding expectations. Never recreate a skeleton
just to make an exporter warning disappear. Recheck intermediate/contact poses and
playback as required by the animation specialist. Still images alone do not prove timing.

Record every material loss or bake/conversion. Keep lightmaps separate from base color
and distinguish baked lighting from actual realtime lights. Preserve approved visual
separation rather than replacing every material with a generic metallic shader.

Procedural or driver-based motion does not survive export. Ship a seconds-based runtime behaviour spec generated from the same
constants (target, formula in seconds, inputs such as stability, period) and record frame-rate independence evidence; never leave
the engine to guess timing from frame counts. Example: `sections/reactor-room/production/overhaul-R1/scripts/cr_runtime_spec.py`.

Reduce materials and lights before export, not after: pack image-with-UV-quad decals into one atlas (pad the cells, unify UV layer
names before joining), and decide which lights stay dynamic (a handful, at most two shadow casters) and which are baked at a rest value; record
the budget as a spec. Example: `sections/reactor-room/production/overhaul-R1/scripts/cr_atlas_decals.py` and `cr_rt_lights.py`.

## Evidence states

Use V00's labels and definitions from the existing validation plan: Planned, NotRun,
Passed, Failed, Blocked, NotApplicable. NotApplicable needs a scoped reason and reviewer.
Source authoring, export, Blender re-import, Unity import, Player validation and human
art acceptance are separate claims. Missing required tooling is Blocked, not Passed.
