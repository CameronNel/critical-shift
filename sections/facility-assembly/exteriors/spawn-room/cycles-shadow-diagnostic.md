# Cycles shadow-property diagnostic — Blender 5.2

The proposed hidden `light.data.cycles.cast_shadow=False` distinction is **not present in this runtime**. Direct access raises AttributeError for every inspected light; CyclesLightSettings RNA has no shadow property and its ID-property keys are empty. The installed Cycles UI explicitly uses `sub.prop(light, "use_shadow", text="Cast Shadow")` at Blender 5.2/5.2/scripts/addons_core/cycles/ui.py:1677. Therefore `data.use_shadow` is the Cycles light Cast Shadow control here, not merely an EEVEE-only setting.

Read-only results:

- Spawn R04: 23 lights inspected, all data.use_shadow=True, including four local EEVEE_floor_bounce copies and linked source lights.
- Turbine R01: 23 lights inspected, all data.use_shadow=True.
- Across mesh objects in each file, no visible_shadow=False or is_holdout=True exception was found. Roof/ceiling records also have shadow visibility enabled; no object-level holdout bypass was found.

Actionable conclusion: do not add a nonexistent `cycles.cast_shadow` property or claim it fixes this. Current shadow flags do not explain the persistent white patches. My earlier R03 no-shadow-fill finding was real for that revision, but R04 confirms correcting it did not solve the rendered target. Continue causal inspection of evaluated light geometry/size, emitter intersection and actual shader/visibility paths; no sole-cause attribution or further asset mutation is justified by this diagnostic alone.

Evidence: cycles-shadow-rna.py and per-section cycles-shadow-rna-R04.json / cycles-shadow-rna-R01.json. Background CPU inspection only, no rendering, model edits or blend saves. Mesh holdout inspection is object-level, not an exhaustive audit of every collection/view-layer holdout and material holdout path.
