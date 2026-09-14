# Compliance exterior R05 — independent bounded technical review

Verdict: TECHNICAL HOLD. Visual style approval does not authorize propagation of the current mesh builder unchanged. Two concrete source-side issues need repair: inverted box winding and incomplete support-contact construction/validation. No source/model edits, rendering or GPU use occurred in this audit.

## Verified evidence

- Fresh Blender 5.2 background process opened R05 and its relative module library. The original and accepted files both hash to `e803c7da17dc60b7f7f8c3983d6414eb18c9adc86329ca86112d2d3358fb974f`, matching SOURCES.json. Module hash is `0cdae8b3d302459d75569cb6bf3a463f24b30ea373c2bcdf430360033d7b0947`; SOURCES.json does not pin this derived file separately.
- Exterior SHA is `f88176d92cf674a02ca89436c2bb56ab501d34f5502375d4bd685b6fefa888fb`, matching the R05 render manifest. Original, accepted, module and exterior SHA values stayed unchanged through the audit.
- All **1,077** linked original objects match accepted-file object type and world transform; mesh objects additionally match raw vertices and polygon topology. The original collection is genuinely library linked, instanced with an identity matrix. No original geometry/transform mutation was found. This comparison does not fingerprint modifiers, material node graphs, animations or non-mesh geometry data.
- Scene unit scale is 1 m. All new object scales are identity. The exterior is authored in module-local coordinates; the layout transform is translation (-49,16,0), Z rotation 90 degrees, scale (1,1,1). The rerun auditor applies that transform for world reservations; actual master import was not inspected.
- Reran the unchanged `audit_exterior.py` with EXTERIOR_SECTION=compliance-dock and EXTERIOR_REVISION=R05: PASS, zero portal-solid and reserved-volume intrusions. An additional conservative interior-core box [-6.7,.4,.05] to [6.7,15.7,4.3] found zero new mesh AABB intrusions. This is not exact intersection coverage of every boundary/interior surface.
- Four perspective cameras exist, all 32 mm with 0.1–300 m clipping: FRONT (0,32,2.5), OBLIQUE (-19,31,9), REVERSE (17,-14,8), DETAIL (5.5,21,1.65). DETAIL provides human-height evidence. Saved settings: 1600x900 at 100%, Cycles 32 samples, AgX. No rerender or prior-camera transform comparison was performed.
- No image datablocks exist in this loaded package, so there are no packed/external image dependencies to fail. The relative module library resolves. No complete fonts/sounds/cache/dependency relocation test was performed.

## Concrete source blockers

1. **180 of 209 evaluated additive meshes have negative signed volume.** All 209 have zero nonmanifold edges, inconsistent adjacent winding edges and degenerate faces, so these are coherent closed solids whose box-family face winding points inward. `box()` in build_exteriors.py defines inward faces; rod-family volumes are positive. Reverse box face order/recalculate outward normals at construction, rebuild, then verify all solid volumes and rerender. Double-sided Cycles beauty pixels conceal this; engine backface culling/export can expose it. Do not defer this as runtime polish.
2. **Support-contact gate is incomplete.** No additive objects expose support metadata, and the existing auditor checks only portal/reservation boxes. A targeted evaluated-AABB probe finds Marker holder 37.5 mm in front of its presumed Inspection station backing support, with no connecting mount in the builder. Clipboard board is about 5 mm off the backing; sheet about 1.5 mm off its board; stamp base touches its shelf; shelf penetrates backing by 12.5 mm. These are directional bounding-box probes, not full anchor/raycast results. Correct the unsupported holder, register intended supports and validate the prescribed gap/penetration/orientation tolerances; document intentional welded/mated joins rather than applying naive AABB penetration rules to them. Do not claim a support-contact PASS from the current report.

## Deferred runtime checks and scope

Gate ribs and wear carry runtime_binding strings naming their leaf. They remain closed-pose review geometry; those strings are not an implemented parent/animation binding. Engine import must bind them, test movement and clearance, and ensure the portal auditor's binding exemption does not hide static collision. This is explicitly deferred runtime work, distinct from the source mesh/support defects above. Existing rear closure is source-owned and must stay closed until connector integration.

Cold-start opening and dependency availability passed for this machine, but cold-start rendering/rebuild equivalence, full normal export, exact all-surface intersections, material preservation, asset portability and runtime acceptance remain unverified. No full technical score or PASS is awarded.

Evidence files: technical-audit-R05.py/json, support-probes-R05.py/json and rerun audit-R05.json. Both helper scripts inspect only and do not save blend files. Invoke with Blender --background --factory-startup --python followed by the absolute script path.
