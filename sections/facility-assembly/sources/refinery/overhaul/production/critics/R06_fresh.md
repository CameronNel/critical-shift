# Refinery overhaul R06 — fresh visual and technical review

**Result: not accepted.** The scene has a cohesive grounded industrial palette, a clearly open central route, more specific process hardware, and one convincing worker-use nook. Current pixels still fall well short of the owner's 99/100 minimum in every category. I observed no automatic visual veto in the current views; that does not offset the category threshold failure.

## Evidence reviewed

- All eleven complete R06 fixed-camera renders: `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_PROCESS`, `CAM_REVERSE`, `CAM_PINCH`, `CAM_MATERIAL`, `CAM_ASSEMBLY`, `CAM_DISPATCH`, `CAM_MINE_TO_CRUSHER`, `CAM_HERO_DETAIL`, and `CAM_WORK_NOOK`.
- The actual Spawn reference pixels `VALIDATE_Hero_A.png` and `VALIDATE_Spawn.png`, used as the requested quality comparison.
- R06's completed render manifest and `validation_R06.json` for technical evidence only.

## Scores

| Category | Score | Weight | Weighted points | Pixel/evidence basis |
|---|---:|---:|---:|---|
| Route readability | 90 | 20% | 18.00 | The broad floor lane reads clearly in `CAM_ENTRY` and `CAM_MAIN_ROUTE`; route markings and equipment edge keep the movement zone legible. Black port openings interrupt the room boundary in `CAM_REVERSE` and `CAM_DISPATCH`, and process direction is not immediately clear from the route views. |
| Art direction and silhouettes | 87 | 20% | 17.40 | The oxide-orange/green/charcoal palette and industrial rhythm are coherent. `CAM_ASSEMBLY`, `CAM_MATERIAL`, and `CAM_PINCH` still show many control boxes on repeated square-post supports, leaving some kit-built/blocky reads. The construction language is less resolved than Spawn's authored bay, door, and chamber silhouettes. |
| Hero process equipment | 84 | 15% | 12.60 | The pressure vessel has a useful hatch, gauges, pipework, and task controls (`CAM_PROCESS`, `CAM_HERO_DETAIL`), but its body has visibly uneven dents/creases that read as a surface/shading defect. The overall receiving-to-dispatch progression is not yet self-evident in broad views. |
| Materials and anti-plastic quality | 88 | 15% | 13.20 | Concrete, painted machine colors, dark steel, glass, and floor read as separate families, particularly in `CAM_MATERIAL`. Several orange shells retain a smooth, slightly molded response, and localized use/wear remains subtle across the larger room. |
| Practical lighting and atmosphere | 89 | 10% | 8.90 | `CAM_ENTRY`, `CAM_PROCESS`, and `CAM_WORK_NOOK` show visible practicals with contact shadows and useful darker equipment undersides. The room remains broadly warm and evenly readable, with weak separation between some work zones. The technical light audit is strong (see below), but pixels do not yet show a more deliberate hierarchy comparable to the Spawn reference. |
| Purposeful dressing and worker storytelling | 85 | 10% | 8.50 | `CAM_WORK_NOOK` is a specific, successful cluster: shift notes, radio, mug, and food suggest an occupied break point. Most other views read as clean equipment presentation; there is little visible evidence of workers servicing or sampling the process elsewhere. Fine control labels are also difficult to read at gameplay distance. |
| Technical cleanliness and reproducibility | 97 | 10% | 9.70 | R06 validation reports PASS, no issues, no route obstructions, 29 protected interfaces unchanged, zero world strength, 21 bound in-room lights, all 79 new and 157 inherited support checks passing, and 845 closed-mesh checks passing. The manifest records all eleven views and hashes. The validator explicitly does not prove exhaustive self-intersection, buried-volume, or runtime-collision correctness. |
| **Weighted total** |  | **100%** | **88.30 / 100** | **Below the required 99.00.** |

## Veto review

**Automatic visual vetoes: none observed.** The scene is not dominated by blockout primitives, plastic response, flat illumination, random clutter, or blocked circulation. The open ports are preserved module interfaces and are not treated as altered geometry or a veto; they do render as black cut-outs in this standalone evidence set. Technical validation reports no light/interface/route veto: all 21 lights are inside the room and bound to physical lenses, world strength is 0, protected changes are empty, and route obstructions are empty.

## Highest-impact defects to address

1. **Black open-port cut-outs weaken the room boundary** — `CAM_REVERSE`, `CAM_DISPATCH`. The adjoining area disappears into featureless black, so two views read as unfinished openings and lose depth/context. Keep the ports and their coordinates unchanged; make sure the actual connected map volume, threshold continuation, and its physically grounded practical lighting are present in the integrated review context.
2. **The main vessel surface reads dented or melted** — `CAM_HERO_DETAIL`, `CAM_PROCESS`. Broad irregular depressions on the orange shell do not follow a clear access, weld, or formed-panel logic. Smooth the body and reserve shape changes for intentional seams, ribs, and service panels; inspect the same fixed detail view after correction.
3. **Process order is not immediately legible** — `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_MINE_TO_CRUSHER`, `CAM_DISPATCH`. The crusher/conveyor entry reads, but the following stations form a dense row whose input/output handoffs are hard to trace at gameplay distance. Strengthen the visible material path and distinct stage silhouettes so a player can follow receiving → feeder → crusher → sorter → processor → dryer → assembly → inspection → dispatch without relying on small labels.
4. **Repeated post-mounted control boxes remain generic** — `CAM_MATERIAL`, `CAM_ASSEMBLY`, `CAM_PINCH`. Several teal panels use similar flat faces and thin square posts. Give each station's operator interface a construction-specific housing, bracket, or pedestal that clearly carries its weight and relates to that machine, while retaining restrained controls.
5. **Human use is concentrated in one nook and fine text is too faint** — `CAM_WORK_NOOK`, `CAM_PROCESS`, `CAM_ASSEMBLY`. The nook is strong, but the rest of the room has little evidence of maintenance or production work, and small control captions blur into their panels. Add only a few useful, localized work traces at relevant stations (for example, a sample tag/jar or a tool at a service point) and improve the size/value hierarchy of essential labels; keep the central aisle and quiet surfaces clear.

## Technical evidence limits

`validation_R06.json` records 2,486 visible meshes and 283,760 evaluated triangles. The 79 new support contacts and 157 inherited support checks pass; the 845 closed-mesh winding/volume checks pass; missing images and libraries are empty. These are useful bounded checks, not proof of every intersection, hidden overlap, final map-context appearance, or runtime collision behavior. This review did not award technical points from image appearance alone.
