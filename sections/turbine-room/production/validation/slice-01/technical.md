# Turbine room technical validation

Revision: slice-01. Phase: slice. Result: **FAIL**.

Fresh-process saved-blend CPU inspection; no mutation and no rendering.

Blender 5.2.0 LTS; 237 objects; 205 evaluated surfaces.

This is objective geometry evidence, not an art score or a full cold-start render PASS.

| Check | Result | Evidence |
|---|---|---|
| configuration.revision | PASS | slice-01 |
| configuration.cameras | PASS | Ten camera transforms and lenses compared with external contract |
| configuration.render | PASS | Saved render/metric configuration; no render performed |
| configuration.file | PASS | C:\Users\Camer\.codex\worktrees\2566\critical-shift\sections\turbine-room\blender\turbine-room.blend |
| configuration.private_resources | PASS | C:\Users\Camer\.codex\worktrees\2566\critical-shift\sections\turbine-room\.blender-user |
| dependencies | PASS | File-backed images, libraries and fonts checked |
| materials.assignment | PASS | Every render-visible mesh/curve/font has non-null materials; shader statistics are not visual acceptance |
| geometry.finite | PASS | All object matrices and evaluated world vertices finite, transforms nonsingular |
| geometry.normals | PASS | Nondegenerate evaluated face normals finite and unit-length; outward winding is not generally proven |
| geometry.degenerates | FAIL | Zero-area evaluated polygons |
| geometry.topology | REVIEW | Boundary/nonmanifold edges reported; intended open cloth/text surfaces need interpretation |
| geometry.exact_duplicates | PASS | Coincident evaluated point sets and triangle counts |
| geometry.hidden | PASS | Hidden render geometry requires explicit intent review |
| support.SUPPORT_D02 electrical sign | FAIL | No explicit visible prop association in registry or anchor parent; False registry: visible prop targets itself |
| support.SUPPORT_bench foot -3.620.05 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_bench foot -3.622.65 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_bench foot -2.1520.05 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_bench foot -2.1522.65 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_vise | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_bearing cradle | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_mug | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_rag | FAIL | No explicit visible prop association in registry or anchor parent; Anchor is detached from associated visible prop |
| support.SUPPORT_clipboard | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_tool rail | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_task lamp | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_conduit saddle 1.8 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_conduit saddle 3.2 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_conduit saddle 3.8 | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_lubrication chart | FAIL | No explicit visible prop association in registry or anchor parent |
| support.SUPPORT_oil stand | FAIL | No explicit visible prop association in registry or anchor parent |
| support.coverage | FAIL | All enumerated support roots require explicit records; general arbitrary assembly support is not automatically inferred |
| clearance.main_route | FAIL | Evaluated triangle clipping against open clearance volume, with enclosed-volume fallback |
| clearance.east_service_aisle | PASS | Evaluated triangle clipping against open clearance volume, with enclosed-volume fallback |
| clearance.north_crossover | PASS | Evaluated triangle clipping against open clearance volume, with enclosed-volume fallback |
| clearance.south_crossover | NOT_APPLICABLE | Outside built slice |
| clearance.west_equipment_apron | PASS | Evaluated triangle clipping against open clearance volume, with enclosed-volume fallback |
| clearance.portal.D01 | NOT_APPLICABLE | Outside built slice |
| clearance.portal.D02 | FAIL | Evaluated triangle clipping against open clearance volume, with enclosed-volume fallback |
| machine.shaft_alignment | NOT_APPLICABLE | No turbine in slice |

Detailed measured contacts and intrusions are in the adjacent technical.json.

Limitations:
- No visual score or full cold-start render acceptance
- No engine collision/navmesh/physics proof
- General arbitrary inter-object collision and assembly strength are not proven
- Neighbor alignment remains unbound; tested local geometry only
- Support extrema check establishes contact at sampled authored support points, not mechanical stability
