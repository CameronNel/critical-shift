---
name: game-asset-pipeline
description: Use for Critical Shift Blender-to-runtime asset delivery, scoped FBX or GLB exports, re-import validation, pivots, scale, colliders, LODs and binding manifests. Not for generic modeling, unrelated code or automatic map promotion.
---

# Critical Shift: game asset delivery

Read [AGENTS.md](../../../AGENTS.md),
[blender-headless](../blender-headless/SKILL.md), and the authoring-to-runtime
boundary A08 in [the architecture](../../../design/code-architecture/ARCHITECTURE_PLAN.md).
For map work, resolve current sources and ownership through
[MAP.md](../../../MAP.md) and [MAP.json](../../../MAP.json).
Read the affected section's current handoff; approval is not inferred from a filename.

## Establish the actual destination

Inspect [runtime status](../../../runtime/README.md), current source files and the
existing exporter/importer before choosing output format or engine settings. A
source-only Unity foundation is not a validated Player. Do not assume GLB is supported
by the current Unity project, install an importer or resurrect a historical pipeline.
Use the approved route. An unresolved route blocks engine acceptance, not safe authoring.

Record source revision, allowed object set, output location, physical scale, axes,
origin/pivots, material mapping and expected consumer. Reuse the existing binding
manifest and naming conventions. Missing contract fields are explicit unresolved
items, not permission to generate a competing schema or invent runtime ownership.

## Prepare only the delivery derivative

Preserve the canonical blend, immutable modules, caches, source hashes and world
placement. Apply export-only transforms, modifier evaluation, triangulation or material
conversion to a copy when required by the approved route. Do not apply transforms
blindly to a rig or reset authored pivots. Exclude reference planes, diagnostic cameras,
control-only rig objects and unrelated geometry while retaining required dependencies.

Use [delivery and budget checks](references/delivery-checks.md) for the affected
asset. UV/material work uses [the surfacing skill](../blender-uv-texturing/SKILL.md);
animated assets also use [blender-animation](../blender-animation/SKILL.md).

## Validate at separate boundaries

1. Run the existing scoped exporter and record its version, options, logs and outputs.
2. Re-import into an empty disposable Blender scene/process. Compare expected bounds,
   orientation, pivots, object/mesh/material structure, texture references and, when
   relevant, bones, clips and representative evaluated poses. Inspect re-import renders.
3. Explain expected importer differences such as split vertices or mesh partitioning;
   do not demand identical raw counts or silently accept missing parts.
4. When a working target is available and import is in scope, use
   [unity-validation](../unity-validation/SKILL.md) to select an authorized asset-specific
   validator for engine import, bindings, materials, collision and representative
   Player behavior. Verify that its workspace, scene/build and assertions exercise
   the changed asset. The stock WP-01 foundation runner does not import the map and
   cannot pass these claims. Blender round-trip success is
   not a substitute for this step. Missing tooling or asset-specific coverage makes
   the affected engine acceptance Blocked, not Passed.
5. Promote only through the existing reviewed section/map/runtime process. A delivery
   check cannot upgrade source art approval or advance a runtime production gate.

## Handoff

Report source/output revisions and hashes; exact conversion settings; comparison
results and tolerances; inspected images; collider/LOD/binding status; remaining
losses; technical, visual and engine evidence separately. Preserve failure artifacts.

No new rigs, automatic decimation, package changes, gameplay rewrites, whole-map
exports or performance claims are authorized merely by activating this skill.
