# Cooling Plant — verified local integration package R10

Complete original Blender room:11×13m clear footprint,5.8m ceiling plane, paired pump trains, heat exchanger, extraction hoist, maintenance workshop, reserve restart, backup-water services, drains, lighting and navigation. Ivory/charcoal/oxide-orange/yellow Valorant direction; no teal. All machinery, supports and procedural materials are authored from scratch.

## Review and saved-file evidence

Independent Luna actual-pixel review: all eight categories meet90. Full report: [Luna R10](critics/luna-R10-full-review.md).

| Category | Score /100 |
|---|---:|
| specification_coverage | 94 |
| layout_flow | 94 |
| machinery | 95 |
| navigation_readability | 91 |
| construction | 93 |
| materials | 92 |
| lighting | 92 |
| reference_fidelity | 93 |

Saved-scene evaluated geometry audit: PASS, zero failures/review items, matching source hash. Eight conservative player/cart sweeps: PASS, zero collision samples. Ten primary cameras rendered again in a fresh Blender process: unchanged saved artifact and independently verified visual stability; tiny numerical differences remain, so bit-exact output is not claimed. Materials, geometry, native text, cameras and interfaces survive reopening; no missing linked/external textures are required. Evidence: [geometry](technical/R10-validation.json), [routes](technical/R10-walkthrough.json), [cold-start comparison](technical/R10-cold-survival.md).

Saved Blender SHA256: `cdc0b48a5af6cb11bae6a4511074cc4b9aacf4dce687503e55d3891a49bb2693`. Reproducible source SHA256: `861ffec531f93ed3375064070bfeac45e31557cdd0fa121497101ed09acae406`. Exact source/scene checkpoint: checkpoints/R10/.

Live Blender inspection is recorded in technical/R10-live-inspection.json and its viewport screenshot. The dependency tool reports Blender's native Bfont `<builtin>` sentinel as a missing literal filesystem path; the raw flag is retained, while the native text is visibly verified in fresh-process renders. This is not an external font file. The live scene was not resaved, and its control lease was released.

## Inspection and assembly

Open ../blender/cooling_plant.blend. All10 C cameras and8 W cameras are saved. [Image gallery](renders/final/gallery.html) and [dimensioned plan](../architecture/floorplan.png) provide review coverage. [Requirements](REQUIREMENTS.md), [concept provenance](../art/concepts/PROVENANCE.md), [correction history](CORRECTION_HISTORY.md) and [camera transforms](CAMERAS.md) retain the full evidence chain.

Local origin is CP-P01 at(0,0,0),+Y inward,+Z up, metres. Main opening5×5m; internal CP-D02 at(-4.1,9.9,0),1.2×2.2m. Permanent center lane2.2m; exchanger withdrawal2.6×3.5m; bench standing strip0.9m. Full machine/service envelopes, normals, elevations and eight utility socket coordinates are in [interface.json](../interface.json) and [connection contracts](../architecture/CONNECTIONS.md). Do not scale the scene.

Proposed Cooling→reactor placement is Rz(-135°), translation(11.0162950904,-11.0162950904,0), at the OUTER end of the existing reactor-owned3.7m stub. This transform is documented, not applied. Topology is refinery→Fuel Corridor→reactor→Cooling. No neighbouring section was moved, rebuilt or imported.

## Remaining integration uncertainties

The reactor's existing static closed cooling door blocks assembled traversal; its owner/integrator must resolve it. Remote coolant/secondary-water, reserve-power and drainage endpoints remain unassigned. Fuel Corridor S01_PLANT is a reserved header, not an installed Cooling link. Reconcile final global module placement and turbine fit when assembling the facility. Read-only neighbour measurements preserve before/after hashes; recheck contracts if neighbours change.

This is integration-ready Blender scenery and interface evidence, not final whole-map polish, pressure-vessel certification, game-engine collision or interaction validation. Pumps, valve hold, repair, reserve sharing, battery/water attachment and hydraulic values still need host-authoritative gameplay integration. The conservative saved-scene route sweeps do not replace engine physics.

Commit/push receipt and live inspection evidence are recorded separately after packaging. No merge to main is authorized by this package.
