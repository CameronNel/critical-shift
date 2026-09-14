# Compliance exterior R06 — independent bounded technical review

Verdict: R05 inward-normal and visibly unsupported-holder defects are repaired. Scoped geometry/source-preservation checks PASS. Full protocol technical acceptance remains unverified because support registrations/anchor checks are still absent; no engine implementation is required for this Blender exterior asset review.

Fresh Blender 5.2 background CPU inspection opened R06, reran the existing audit with EXTERIOR_SECTION=compliance-dock and EXTERIOR_REVISION=R06, and opened accepted.blend for comparison. No blend saves, rendering, GPU work or source edits occurred.

## Verified

- All **211 evaluated additive meshes** have positive signed volume, zero nonmanifold edges, zero inconsistent adjacent winding edges and zero degenerate faces. Shared box winding defect is fixed.
- Both added Marker holder attachment shoes exist and bridge backing-to-holder space. Their evaluated bounds overlap backing and holder. The former 37.5 mm direct backing gap is now an intentional standoff with intervening supports, not an unsupported-holder defect.
- Portal/reserved-volume audit reruns PASS with zero intrusions. Conservative interior-core AABB probe also reports none; exact every-surface intersection testing remains outside scope.
- All **1,077** linked original objects match accepted object type/world transform; original meshes match raw vertices and polygon topology. Original source instance remains linked with identity transform. Source-owned rear closure was not changed.
- Original and accepted SHA still match SOURCES.json: e803c7da17dc60b7f7f8c3983d6414eb18c9adc86329ca86112d2d3358fb974f. Module SHA remains 0cdae8b3d302459d75569cb6bf3a463f24b30ea373c2bcdf430360033d7b0947. R06 SHA: 8061cd001d5b7ac268574de6d3541e37897f77bced17e056cd77b0c7410fe833. All four files remained unchanged during audit.
- Unit scale remains 1 m; additive scales are identity. Relative module dependency resolves. No image datablocks/dependencies are present. Four 32 mm perspective cameras, DETAIL at 1.65 m, 1600x900, 32 samples and AgX are retained in inspected settings.

## Remaining source-side precision and evidence work

Support probes are evaluated directional AABB measurements, not a registered anchor/raycast validation system. No additive object has support metadata. This is a concrete missing final-validation deliverable, not evidence that every prop floats.

- Each new shoe penetrates backing about **2.50 mm**, slightly beyond the canonical default 2 mm allowance. Adjust the mating face by about 0.5 mm or explicitly document/validate this intended join tolerance. Holder-to-shoe AABB overlap is 26 mm because the shoe joins a cylinder; it cannot be treated as a scalar flat-face penetration failure.
- Clipboard-to-backing is approximately **5.00 mm** gap, at the default limit (numerical result 5.001 mm). Verify the intended mounting/contact anchors rather than failing on this approximately 1 micron excess.
- Sheet-to-board gap is **1.50 mm**; stamp base contacts shelf within numerical precision. These limited probes are favorable, not complete support PASS evidence.
- Shelf-to-backing overlap is **12.50 mm** in AABB space. Record its intended fixed/welded support join and check appropriate anchors; the generic flat-face 2 mm rule cannot silently certify that overlap.

No further major mesh/source-preservation blocker was found in this bounded check. Resolve/document the shoe tolerance and supply the scoped support-contact registry/report for full source technical acceptance. Material/visual regression review is pending separately; normals changing can affect rendered shading.

Runtime leaf binding strings remain import instructions for closed-pose gate ribs/wear. Animation/collision acceptance belongs to later engine integration, and is not a blocker to delivering the Blender exterior asset. This review does not verify runtime behavior, cold-start rerender/rebuild equivalence, complete dependency relocation, modifiers/material/animation preservation or exhaustive intersections.

Evidence: technical-audit-R06.py/json, support-probes-R06.py/json, rerun audit-R06.json. Earlier R05 helper methodology and exact scope still apply.
