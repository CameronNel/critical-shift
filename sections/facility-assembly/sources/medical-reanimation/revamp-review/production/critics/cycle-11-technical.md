# Cycle 11 — independent technical review

**8.3/10 — FAIL. Minimum 8.5/10. One critical acceptance blocker. Visual /90 unscored.**

Source: `module_overhaul_R2.blend`, SHA-256 `ef097c0052c95bf23c8a4d542db661cb151566f8618c287931f4ffa163015ff7`. Blender 5.2.2 LTS, fresh factory processes, autoexec disabled, one thread. Source, original module, accepted snapshot, map, interface, layout, MAP.json and approved spawn remained unchanged. No scene save, rebuild, render, merge or promotion by this critic.

## Blocking contact defect

`MED_R2 | Clinical cabinet stock 0` through `11` contain eight disconnected `MED | Charcoal print` barcode cuboids each. All **96** are **8.49986–8.50010 mm** from their intended `Sealed supply case` through `.011`, exceeding the protocol's 5 mm maximum. The assembly's single closest contact witness passes elsewhere and does not validate those printed strokes.

Stock-0 exact witness: barcode point `(3.41149998, 8.16750050, 1.46300006)`; case surface `(3.41999984, 8.16750050, 1.46300006)`; normal `(-1,0,0)`. Stock-0 nearby-room search leaves five bars farther than 5 mm from every alternative nearby support; three happen to approach the case tab, not the intended case face. The case faces are around parent-local `Y=-0.19000018`; barcode centres are `Y=-0.199`. Thus the source's general assembly-support PASS is bounded, not exhaustive.

Minimal measured correction: move all barcode strokes **+8.25 mm in SUPPLY_CABINET local Y**, equivalent to **+8.25 mm in world X**. In `clinical_stock`, use `y-.23075` instead of `y-.239`, keeping the 1 mm stroke thickness. This targets 0.25 mm nearest gap / 1.25 mm outer gap. Rebuild and reraycast actual faces. Register per-component printed-stroke witnesses. The adjacent identification/expiry text at `y-.238` should also be measured and attached; it was not counted as a separate blocker here.

Exact 96-component witnesses: `/workspace/scratch/medical-cycle11-technical/cabinet-barcode-witnesses.json`.

## Bounded mapping defect

`Sealed consumable carton`, `.001` and `.002` have only `UVMap`, while their active `MED | Unbleached folded carton` graph requests `MED_Physical_1m` into the procedural Noise Vector. Include these actual material users in physical UV assignment, or name and scale their existing UV channel explicitly. Used poster and bottle-label image faces are valid: 8 poster faces and 48 label faces, finite nonzero UV coverage, packed sRGB images.

## Passing evidence

- Cold open and root objective rerun pass: 1,203 inherited objects, no missing objects or unapproved transform/dimension changes above 1e-6; 102 declared support pairs / 111 anchors, ten all-vertex sewn surfaces and two reserve identification components pass.
- Independent mesh audit: 1,126 evaluated meshes / 433,314 triangles; 156 authored or revised meshes / 179,626 triangles. No nonfinite coordinates, invalid material indices, negative transform determinants, authored winding errors or exact visible-mesh duplicates. All 156 physical UV layers are finite and nonzero.
- All 25 linked libraries resolve through relative repository paths. All 124 file images are packed and have valid loaded dimensions. Fonts are built-in; no cache files. The whole-file map context requires the repository dependency tree, not a standalone copied room file.
- Added meshes clear the broad rescue lane. Five unchanged inherited west fittings project at most about 17 cm into its AABB while leaving about 3.63 m to the eastern boundary; no new route obstruction is certified from this. Floor/walls/portal/utilities preserve inherited transforms and dimensions, with unchanged interface/layout hashes.
- Cart guard follows `CART_LIFT_DECK`; cabinet faces follow their sliding panes; no parent cycles found.
- Completed cycle-11 contains exactly 24 decodable 1067×600 PNGs and matches the current source/renderer hashes, Cycles 24-sample cold mode. Camera matrices match native/independent recipe within 2.83e-7; all prior-camera matrices are identical. All 24 decoded RGB arrays equal cycle 10 exactly, although PNG file bytes differ. The renderer snapshot changes only by an explicit dependency-graph update before provenance; no art recipe change. HIDDEN_BAG alone declares the temporary 2 W inspection fill.
- Invalid renderer diagnostic correctly throws before scene load/render and exits 1 with `--python-exit-code 1`. Verifier report writes were redirected to scratch and no source was saved.

## Scope and limits

This scores the current immutable source, not an unexecuted rebuild or runtime package. No relocation/ZIP extraction, full procedural rebuild, Unity conversion, gameplay collision, interactions, navigation, measured performance or draw-call test ran. Mesh triangles exclude FONT/CURVE conversion. Global self-intersection/watertightness was not certified. Nine joined assemblies received independent small-part searches, followed by all 96 cabinet barcode strokes; other disconnected islands are not exhaustively certified.

Evaluated zero-area polygons remain on six inherited-name Impact wall lining meshes (168 each), Supply bench top (248) and Blanket institutional tag (5); none appear in the 156 authored/revised cohort. Their modifier/export effect is a bounded unchecked residual. Intended open printing/seam/shell surfaces were not failed solely for being open.

`HERO_CABINET.png` and `DETAIL_SUPPLIES.png` were opened for technical context; no visual score is assigned. Prior critics, scores, acceptance and TASK_STATE contents were not read. Full commands, hashes, observations and scratch evidence paths are in the companion JSON.

Score deduction: 1.4 for repeated mandatory contact failure and inadequate component coverage; 0.3 for the active carton UV mismatch. The cold evidence does not remove that blocker.
