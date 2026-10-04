# Critical Shift Agent Entry Rules

## Existing assembled map

**Owner plan (2026-10-03): the current assembled map (`facility_environment.blend`) will be retired.** Do not start new work to promote rooms into it, relink it, or extend it. The room modules and overhaul files on `main` are the source of truth for whatever replaces it. Nothing here deletes the map yet, and the instructions below still describe how it works.

When asked to "build on this map" or continue map/environment work, start with [MAP.md](MAP.md) and [MAP.json](MAP.json). Use their current full-map authoring scene and portable source modules. Do not start from an older standalone room branch or the historical A04 master. Run `git lfs pull` before opening Blender assets. This is an in-progress authoring map, not final art acceptance or a Unity build.


## Map area status (as of 2026-10-03)

Three labels, applied to the version that is on `main` today. **Done and dusted** is an owner declaration (2026-10-03; medical-reanimation and compliance-dock added the same day on the owner's word): the room is finished and gets no more art passes unless the owner reopens it; it says nothing about review scores or whether the room is promoted into the map yet. **Ready for merge to map** means the room has an overhauled or accepted
version on `main` that passed independent review at the repository's bar and its own validation, with its interface unchanged, so
only the promotion step in [MAP.md](MAP.md) ("Overhauling a room", PR 2) remains. **Built but not ready** is everything else: it
failed or never faced that review, has open defects, is unreviewed, or is an original build with no overhaul. "In map" says whether
the assembled map ([facility_environment.blend](sections/facility-assembly/blender/facility_environment.blend)) shows the room today.
Because the owner plans to retire the current map, "promotion" below means the old MAP.md procedure and is **not** being pursued; it is kept only to record which rooms were ready for it. Only the map owner edits the map file. This table is a record of evidence, not an approval; the owner can change a label.

| Area | In map | Status | Evidence and caveats |
|---|---|---|---|
| spawn-room | Yes (linked from `sources/spawn-room/module.blend`) | **Ready for merge to map** | Quality reference the other rooms are scored against. Late polish PRs (#64, #67) describe themselves as "not accepted"; owner to confirm. |
| refinery | No (additive `module_overhaul_R1.blend`) | **Done and dusted** (owner); ready for merge to map | R24 reviewed 99.10, all 29 interfaces pass. The R25 finish (#76) is on top and **unreviewed**; R24 is the commit `87ef343`. |
| electrical-room | No (candidate scene beside the map) | **Done and dusted** (owner); ready for merge to map | R11 and R12 reviewed 99 in all seven categories. The T1 texture finish (#74) is on top and **unreviewed**; the reviewed file is `overhaul/checkpoints/full-R11.blend`. |
| fuel-corridor | Launcher only (`open_map.py`); the canonical map file is unchanged | **Ready for merge to map** | F22ci and F23ci reviewed 99. The AAA finish (#77) is on top and **unreviewed**; F23ci is `production/checkpoints/fuel_full_F23ci.blend`. 678,692 triangles, decimation held as modifiers. |
| turbine-room | No (original `module.blend`) | **Done and dusted** (owner) | Full rebuild merged (#63, `rebuild/turbine_room_v2_geo.blend`), declared done by the owner. `module.blend` is still the original room, and a promotion attempt (draft #82, closed unmerged) was abandoned because the old map is being retired. Its only review is the builder's own agent review (about 79/100, no view above 84, one model's opinion), so it has not met the bar the "ready" rooms met. |
| reactor-room | No (additive `module_overhaul_R1.blend`) | Built but not ready | Dark "dead shift" R1 merged unpromoted (#49). Control-room redo is open (#53, #54). No independent score found that meets the bar. |
| medical-reanimation | No | **Done and dusted** (owner) | Additive `module_overhaul_R2.blend` merged to `main` (#65, with my unreviewed finish #78 inside it); not promoted. Its own reviews scored 91.1 and 91.7, below the 99 bar. Its review images and scenes went in as ordinary Git blobs, not LFS (about 1.6M added lines). |
| compliance-dock | No | **Done and dusted** (owner) | Additive overhaul merged to `main` (#66, with my unreviewed finish #79 inside it) on the owner's instruction although it **failed its recorded gate** (C9 88.625 against 99); not promoted. Cloth chart distortion and the shape-language and storytelling deductions remain. |
| mine | Yes (original) | Built but not ready | Original delivery, Luna 92 to 95. No overhaul; not held to the 99 bar. |
| cooling-plant | Yes (original) | Built but not ready | Original R10, Luna 91 to 95. Additive AAA finish `module_aaa_A1.blend` (314,609 triangles) is **unreviewed**, no validator run; the map still shows the original. |
| condenser-bay | Yes (original) | Built but not ready | Original R34, Luna 91 to 94. Additive dark AAA finish `module_aaa_A1.blend` (386,490 triangles) is **unreviewed**, no validator run; reach check in `reach-check.json` shows the overhead cooling-water valves unreachable; the map still shows the original. |
| waste-storage | Yes (original) | Built but not ready | Original W22, Luna 91 to 93. Additive AAA finish `module_aaa_A1.blend` (351,868 triangles) is **unreviewed**, no validator run, reach check in `reach-check.json`; the map still shows the original. |
| Exterior / terrain | Yes | Built but not ready | `MAP.json`: art acceptance REJECT, exterior categories below 93. |
| Connections | Yes | Built but not ready | Built and walk-checked (A06) but not independently accepted; whole-map R17 review was lighting 90, materials 88, professional finish 82. |
| Vertical access | Yes | Built but not ready | Same as Connections (A08 handoff); no separate acceptance record. |
| Roof services | Yes | Built but not ready | Same as Connections (A13 handoff); no separate acceptance record. |
| Facility network | Yes | Built but not ready | Same as Connections (A07 handoff); no separate acceptance record. |

Notes for agents:
- The finishes for refinery, electrical, fuel, reanimation and dock were merged on the owner's instruction **without independent review**, against the rule above that no agent merges its own work. Treat them as unreviewed until a review says otherwise, and never describe them as accepted.
- Do not edit a "done and dusted" room's files or start another art pass on it (refinery, electrical, turbine, medical-reanimation, compliance-dock) without the owner reopening it. Do not promote any room into the current map; see the owner plan at the top.
- Triangle counts: the fuel corridor (678,692), turbine rebuild (about 387k) and dock (398,352) are near or above 400k; include text curves when counting, as the room validators do.
- When a room changes state, update this table in the same PR and cite the review or validation file.

## Start here

Respect the current task's scope. A planning-only task changes documentation, not runtime/test code, Unity projects, packages, workflows, scenes/assets or repository settings. Proposed file paths and test names in a plan are not permission to implement them.

The repository's [GAME_SPEC](design/GAME_SPEC.md), section 32.6, requires **one task branch, one primary author, no direct main edits and no agent merging its own work**. Submit bounded changes for independent review. Do not claim that written policy means branch protection is already configured.

## Runtime, Unity, C#, packages and architecture

Read [the code-architecture entrypoint](design/code-architecture/README.md) and [agent checklist](design/code-architecture/AGENT_CHECKLIST.md) before work. On first entry, read the complete linked plan. On subsequent tasks, reread the affected contracts, validation cases, open decisions and actual gate state.

The canonical planning section is `design/code-architecture/`:

- [Architecture](design/code-architecture/ARCHITECTURE_PLAN.md): dependency allowlist, feature boundaries and composition.
- [State and contracts](design/code-architecture/STATE_AND_CONTRACTS.md): mutation owners, host intentions, claims, transactions and lifecycle.
- [Code health](design/code-architecture/CODE_HEALTH_PLAN.md): removal, serialization, diagnostics and review.
- [Validation](design/code-architecture/VALIDATION_PLAN.md): test IDs, failure conditions, fixtures and evidence.
- [Delivery](design/code-architecture/DELIVERY_PLAN.md): minimum implementation sequence and roadmap gates.
- [Decisions and risks](design/code-architecture/DECISIONS_AND_RISKS.md): proposed ADRs, open choices, risks and sources.

Also read [ENGINE_DECISION](design/ENGINE_DECISION.md), the relevant gameplay specification and current repository state. Historical prototype evidence is not proof of a currently runnable Unity project. Do not silently select networking, Steam, voice, input/UI or persistence infrastructure. A package trial needs an explicit bounded decision before installation.

## Environment and Blender section work

Read the global art/build authority under `design/` and the relevant section-local `AGENT_READ_FIRST.md`, scenery specification and production state. For runtime exports, also read the architecture plan's authoring-to-runtime boundary. Original visual source, licensed materials and art-review evidence are not dead runtime assets to be removed by an unused-code sweep.

For Blender authoring, materials, lighting, rendering or visual QA, read the
[shared headless skill](.agents/skills/blender-headless/SKILL.md). It routes to the
existing authorities and tools; it does not replace them or relax section acceptance.
Load its diagnostic references only as needed. Integration and cloud usage are in
[the skill guide](design/blender-headless/README.md).

For Blender animation, existing-rig posing, keyframes, drivers, shape keys,
NLA clips or camera motion, also read the
[animation specialist](.agents/skills/blender-animation/SKILL.md).
It extends the shared headless workflow; static tasks do not need it.
[Animation integration and provenance](design/blender-animation/README.md).

## Focused production specialists

Load only the specialist needed by the current task:
- [UV and materials](.agents/skills/blender-uv-texturing/SKILL.md) for UVs,
  atlases, decals, texture maps and final-step baking, alongside the headless skill.
  Baking lighting (lightmaps, baked shadows/AO) is the last step: author geometry,
  materials and live lighting first; bake only after they are accepted, in a separate derivative.
- [Game asset delivery](.agents/skills/game-asset-pipeline/SKILL.md) for scoped
  exports, round-trip checks, colliders, LODs and runtime binding evidence.
- [Unity validation](.agents/skills/unity-validation/SKILL.md) for runtime
  readiness, existing offline/native checks, builds and measured profiling.

These extend the existing authorities; they do not install tools, select packages,
change art direction or advance acceptance gates. See the
[production skills guide](design/production-skills/README.md).

## Change and handoff rules

Search for the existing implementation and consumers before adding a replacement. Establish one mutation owner, explicit lifetime and allowed dependencies. Migrate consumers and remove obsolete active paths; inspect serialized/dynamic references before deleting Unity code or assets.

Report what changed, what deliberately did not, what actually ran, what was not run or blocked, and the independent review/merge status. Missing tests, unavailable Unity and unmeasured performance must not be presented as passes. Keep these entry links current; do not create another competing hidden architecture guide.
