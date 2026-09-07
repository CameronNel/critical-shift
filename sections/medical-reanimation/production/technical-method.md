# Static geometry validation method

`blender/validate_geometry.py` supplies `validate_geometry(scene)` for the room validator. It measures geometry and returns Boolean checks, evidence and limitations. It does not award rubric points, perform physical simulation or establish room acceptance.

When `scene['phase']=='slice'`, the helper measures the same real entry opening, the slice's floor/ceiling/west-wall surfaces, and conservative 0.60 m standing routes from the inside entry to arrival (0,2.65) and wash approach (−2.55,1.65). Navigation stays within y=0…3.20. The full-room dimensions, OCRU berth and internal obstruction scenarios are explicitly untested in that mode; their absence cannot masquerade as passed full-room checks.

## Evaluated geometry

The helper obtains every mesh, curve, text, surface and metaball object's dependency-graph evaluation, converts it to a temporary mesh, transforms its vertices into world space and computes its bounds. Modifiers and curve thickness therefore contribute to collisions. Hidden objects are included. Failure to evaluate an object fails the geometry check. Unrealized dependency-graph instances also fail explicitly, because separate instance-transform collision support is not implemented; they may not be silently omitted. Temporary meshes are cleared and the scene is not changed. Metric units with scale length 1.0 are required.

## Personnel clearance

The person model is a 0.60 m square in plan and 1.80 m tall. A square conservatively encloses a 0.60 m diameter standing body. The collision slab is z=0.035…1.835 m, allowing floor details up to 35 mm while reserving 1.80 m above that allowance. Engine step and snag behaviour remains untested.

Every evaluated object intersecting that vertical slab contributes its entire XY world bounding rectangle. The validator searches a 0.10 m cardinal grid within the L-shaped floor outline and tests the continuous swept square for every segment against those rectangles. Segment endpoints are not the sole collision test. Short connections to the exact specified interaction approach points use a conservative enclosing swept rectangle. A passed path avoids all evaluated bounding geometry in that slab. Conservative bounds can falsely reject passage around curved, hollow or rotated objects; the grid may also miss a valid path. Investigate failures instead of exempting inconvenient objects.

The inside entry start is (0,0.40). Required approach points are loading (0.55,4.0), controls (−1.65,5.8), rear service (0.60,8.35), recovery (4.30,6.50) and battery (−2.95,8.0). Full path coordinates, lengths and conservative swept-clearance results are saved. Downward floor and upward headroom rays are sampled at each path node and midpoint. These samples demonstrate local supporting floor and overhead geometry, but do not prove a watertight floor between samples.

If a downward ray lands on the steep bevel of a floor feature above 2 mm and within the 35 mm step allowance, the validator seeks an actual flat upward-facing support surface within 20 mm. The report retains the original bevel hit and the successful offset support hit. A missing floor is never rescued by this rule; it applies only to an observed low step edge. This matches the documented step allowance and still requires measured nearby support.

## Dimensions and entry

Distributed `scene.ray_cast` probes measure the main-room west/east/front/rear walls, floor and ceiling; and the recovery alcove's outer walls, floor and ceiling. Measured finished faces are checked against the 8×9×3.6 m main room and 2.2×3.8×3.15 m alcove, with 2 mm numerical/construction tolerance. A probe records the actual hit object, surface location and inward normal. These observations do not prove every part of the shell is continuous or watertight.

The entry test casts horizontally at six heights across three depth positions and upward at five lateral positions across those same depth positions. The smallest sampled surface-to-surface dimensions must meet the contract's 2.20 m width and 2.50 m height. Rubber seals and frame trim count. This is a distributed opening measurement; a local protrusion between probes can be missed, so full cart swept-volume validation remains an engine task.

The adult patient support requires one object with custom property `geometry_role='ocru_patient_support'`, or an unambiguous name containing `patient support`/`patient berth`. Its actual evaluated world bounds must be 0.88×2.15 m, centred at (0.55,6.20), with surface z=0.78 m. These extents do not by themselves establish usable mattress area or loading motion.

## Obstruction scenarios

The validator imports the exact authored footprint rectangles from `scenery/interface.json`: a dropped 1.80×0.70 m body at y=1.55…2.25 and a transverse 2.00×0.75 m cart at y=2.525…3.275. Each is a conservative temporary mathematical obstacle; no proxy objects are inserted in the scene. Required personnel routes are tested with each obstruction separately and both together. The report does not label this a ragdoll or cart simulation. These chosen arrival placements leave the specified loading target outside the obstacle bounds; an arbitrary obstruction at the loading point itself requires clearing and cannot be called passable.

A separate doorway disclosure reports the remaining side gaps for a 2.00 m transverse cart centred in the sole entrance. A nominal 2.20 m opening leaves 0.10 m on each side, insufficient for the 0.60 m body. Internal bypass success therefore does not establish continued exterior access. Clearing and dragging, door trapping and network ownership require engine validation.

## Support-contact coverage

The original main validator checks registered support anchors. The new `register_supports.py` augmentation is intended to supply explicit per-object host classification, real evaluated source-surface anchors, target BVH contact evidence and a directed support chain for every object/component. It is currently **diagnostic and unfinished**; see [support-audit-s08-diagnostic.md](critics/support-audit-s08-diagnostic.md) for the completed run, detected method issues and exact resume steps.

`validate_geometry.py` inventories registrations and fails any object explicitly marked `support_required=True` without a `support_target`. Its new required `exhaustive_support_contacts` gate needs a passing support-chain report whose fingerprints match the current evaluated world vertices and polygon topology. Missing or stale evidence fails. Generic construction strings and the original limited single-anchor registry are not exhaustive support proof. This new freshness integration was saved but has not been rerun since the usage wind-down instruction.

Every wall-, floor- and ceiling-supported prop still needs explicit support classification, target, direction, permitted gap/penetration, orientation tolerance and suitable anchors, including components whose connected support cannot otherwise be proven. The current section has no exhaustive support-contact PASS.

## Integration and cold reopen

Import the helper by its file path or add the room's `blender` directory to `sys.path`, then call `validate_geometry(scene)` after setting the scene phase. Merge its `checks` into the main validator under a `geometry_` prefix, and retain the complete returned report. A fresh Blender background process reopening the authoritative `.blend` should run the same checks. Read `support_registration_audit` and `limitations` independently of the helper's static `pass` value.

No runtime collision mesh, navmesh, interaction reach test, cart turning/loading sweep, ragdoll, multiplayer ownership, grabbing/dragging, door animation or facility exterior connection is validated here.
