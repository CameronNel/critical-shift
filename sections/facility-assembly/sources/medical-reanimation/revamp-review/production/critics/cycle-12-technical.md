# Cycle12 independent technical review

**FAIL —7.8/10**, below8.5/10 minimum. Visual90points are unscored.

Source: `/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation/module_overhaul_R2.blend`
SHA256: `e90d540600a9ec180f3a3bf71a89da4bf0f29a156b0ac3c8bcff2f59d0a63199`. Source remained unchanged; no source, builder, art or native saves were made.

## Acceptance blocker

**TECH-12-C1:28floating hardware islands across7joined assemblies.** The102registered whole-object supports and111anchors pass, but their witnesses do not establish support for every disconnected small part. The following measured gaps exceed the protocol's5mm tolerance. Evaluated surface witnesses, disjoint support-axis bounds, ray-parity enclosure checks and triangle-overlap checks distinguish these pieces from legitimate enclosed or mutually joined detail.

| Object | Evaluated island IDs | Intended support | Gap |
|---|---|---|---:|
| Medical cabinet fabricated face, both suffixes |5–8each | matching sliding pane |14.0mm; own supported frames25.495mm away |
| Manufactured underbench drawers |4/11 | own fronts1/8 |11.5mm |
| Manufactured underbench drawers |5/6/12/13 | own fronts1/8 |5.5mm |
| Jamb service cassette−1/+1 |2/3each | own backing0 |6.0mm |
| OCRU external pressure service−1/+1 |2each | own guide1 |7.0mm |
| OCRU external pressure service−1/+1 |12–13and14–15pairs | own backing0 |10.5mm per paired group |

All object names above begin `MED_R2 |`. Cabinet first suffix is empty with a trailing space. Island IDs are polygon-connected vertex groups in evaluated polygon traversal; world bounds in the JSON preserve exact identities. Dial ring/insert pairs contact each other but float together off backing. Add construction-appropriate component contact witnesses and coverage. Thick hardware does not require every exterior vertex to touch backing.

Read-only correction vectors for all28pieces are in `/workspace/scratch/medical-cycle12-technical-independent/hardware-translation-vectors.json`. They are suggestions targeting a1mm gap; remeasure actual component contact after correcting creator placements.

## Independent checks and scope

-1,312room-scene objects;1,126evaluated meshes;141new/skill-revised meshes including102new joined assemblies;433,314evaluated triangles.
-1,203inherited object transform/dimension comparisons: no unexpected changes. Original map, medical module and approved spawn source hashes unchanged. Added mesh bounds do not enter the reserved rescue lane.
-No finite-geometry errors, exact world-geometry duplicates, inconsistent winding edges or inward closed components across the1,126mesh objects. This is not an exhaustive self-intersection or runtime collision test.
-Fresh Blender5.2.2LTS cold open with autoexec disabled: editable room scene local; all25loaded library paths resolve; all124FILEimages packed and loaded with nonzero size. Correct loaded paths are recorded in followup evidence, superseding an initial probe interpretation that incorrectly reapplied library-parent context.
-102support pairs/111directional anchors replayed independently. Ten sewn-surface objects/10,362vertices and26declared case/battery components/8,638vertices pass. The deeper scan covers1,825disconnected islands; whole-object passes do not override the28confirmed failures.
-Named UV-map consumers have their layers.34material/assigned-face UV records are finite and nondegenerate where consumed. Generic unused atlas/label face degeneracy is not treated as a shader defect. Image graphs/default-map behavior and actual material users were inspected separately from layer existence.
-Cart guards parent to `CART_LIFT_DECK`; both fabricated cabinet faces parent to their corresponding sliding panes. No animation, interaction or runtime mechanism certification.

## Complete camera evidence

The current hot manifest is **complete=true**,24/24expected IDs, exact source SHA and current renderer SHA. Every PNG decodes at1067×600; Cycles24samples, nondiagnostic evidence. All six inherited camera matrices/lenses match source exactly. Generated positions match the renderer recipe within0.000000191m; target direction differences are at most0.0141degrees from float precision. All24camera transforms and lenses, projections and corner ortho scales match the prior-cycle camera manifest exactly. All four cutaway projections contain the full contracted footprint. HIDDEN_BAG's2Wfill is explicitly inspection-only; cutaway hides and camera-attached labels are temporary unsaved renderer operations.

All24current images were inspected in four contact sheets at `/workspace/scratch/medical-cycle12-technical-independent`, alongside decoded PNG metadata. This establishes coverage and technical evidence, not90-point visual approval or exhaustive subpixel support contact.

## Qualified remaining coverage

Body-bag islands1/4/56/58 form an internally connected group, but nearest sampled bridges to a supported island reach only5.504mm. Exact irregular-surface edge distance and authored seam intent were not established, so this is a contact-coverage issue requiring a witness, not an additional firm floating blocker. Tray island74 intersects `Inventory clipboard`; it is excluded from the floating subset.

An exploratory all-vertex printed-substrate scan covered36objects/19,358vertices. It flags candidate outliers in cartridge print, the raised artwork/frame, restart docket and packaging; its target set does not resolve every alternative inherited packaging substrate or intentional raised frame. The declared26case/battery component checks pass, but remaining printed islands should not be declared exhaustively supported from those checks alone. Exact candidate measurements and limitations are in the JSON and `uv-print-probe.json`.

## Commands and limits

All Blender probes used `/workspace/tools/blender-5.2.2-linux-x64/blender -b --factory-startup --disable-autoexec -t1 --python-exit-code1 --python`, with argument spacing as recorded in JSON. Scripts: `probe.py`, `followup.py`, `uv_print_probe.py`, `translation_vectors.py` under `/workspace/scratch/medical-cycle12-technical-independent`. Logs and successful exit codes are preserved; the first UV probe failed on a temporary mesh lifetime error and was corrected/replayed without source mutation. Camera audit: `python /workspace/scratch/medical-cycle12-technical-independent/camera_audit.py`.

No full rebuild or renders were launched by this critic. Cold open/dependencies were independently verified; cold RGB rerender/comparison was not performed. Runtime import, collision/navmesh, host/gameplay behavior, draw calls and performance remain unchecked.433,314triangles and1,343mesh/material bindings are authoring counts, not runtime budget certification. No merge, promotion, runtime change or outside communication occurred.
