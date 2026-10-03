# R21 fresh visual acceptance review

Review basis: opened all 11 R21 images in `production/renders/R21`, then compared the corresponding all-view batches from R19 and R20. Also opened the Spawn references `VALIDATE_Hero_A.png` and `VALIDATE_Spawn.png` as construction/material-quality benchmarks. Scores reflect only the current candidate and evidence available at review time.

## Finding

R21 clearly reads dark, cold and neglected. The weak pools from visible room fixtures, the water streaks, oxide and service-area grime, and the interrupted night-shift nook support the requested mood. Equipment silhouettes and manufactured details are substantially authored; the crusher-to-dispatch chain and main walking lane remain recognizable. The Spawn references show stronger all-over form separation and surface legibility. R21’s darkness buries secondary equipment, controls and labels in several broad views, while floor markings remain cleaner and sharper than the surrounding neglected surfaces. Those pixels keep this from the 99 bar.

The highest-impact visible defect is lost separation in `CAM_REVERSE`, `CAM_PROCESS` and parts of `CAM_MINE_TO_CRUSHER`: secondary machines and controls merge into near-black regions. `CAM_MATERIAL` and `CAM_PINCH` show labels and small control details with weak contrast. The floor is readable and passable, but repeated pale “KEEP CLEAR” stencils and relatively uniform open concrete look orderly beside the localized wall drips and rust. A wider, restrained spread of service-track wear and dirt would support the mood without obstructing the aisle. In `CAM_WORK_NOOK`, the leak/night-shift records, gloves, cup, radio and tools communicate an interrupted shift; the small paper details are not fully legible at this distance, but the grouping reads without them.

All 11 R19/R20/R21 views were inspected for stability. Broad composition, route placement and machine silhouettes stay consistent. Pillow comparisons report a mean absolute pixel difference of 0.000 and equal RGB means for every R19/R20 pair, so those two batches are pixel-identical. R21 changes are subtle in the measured PROCESS, PINCH and ENTRY views (mean absolute differences of 0.092/255, 0.081/255 and 0.021/255 from R20, respectively). This comparison earns no automatic credit for unchanged geometry. I found no visual evidence of a changed room interface or blocked aisle. The two Spawn images support the target for shaped edges and finish control, not the refinery’s brightness or mood.

## Scores

| Category | Weight | Score | Pixel/evidence basis |
|---|---:|---:|---|
| Route readability | 20% | 95 | Open lane and floor path read well in ENTRY, MAIN_ROUTE and MINE_TO_CRUSHER; reverse and process views lose secondary silhouettes in deep shadow. |
| Art direction and silhouettes | 20% | 97 | Cold, run-down industrial direction reads; the broad equipment chain is distinctive, though extensive black regions reduce separation. |
| Hero process equipment | 15% | 98 | Strong pressure-vessel silhouette, gauges, flange, bolts, valves and attached service hardware in HERO_DETAIL; several secondary faces and labels remain hard to read. |
| Materials and anti-plastic quality | 15% | 96 | Oxide, damp marks, wall streaks and worn enamel are visible; grime coverage is localized and some control labels lack contrast. |
| Practical lighting and atmosphere | 10% | 97 | Gloomy isolated practical pools fit the direction and the visible sources appear attached to room fixtures. The available pixel evidence cannot certify every light source. |
| Purposeful dressing and worker story | 10% | 95 | Nook props and shift/leak records tell an interrupted-work story; details are small, and broader neglect evidence remains sparse. |
| Technical cleanliness and reproducibility | 10% | 91 | `validation_R21.json` reports PASS, 419,260 visible evaluated triangles, zero world strength, 29 protected objects unchanged and no route obstructions. Independent technical audit and full cold-rebuild/fingerprint/pixel-comparison evidence were still pending when scored, so this category is not independently closed. |

Weighted score: **95.8/100**. No visual critical veto observed. R21 does **not** meet the required 99 in every category or 99 weighted overall; it is not accepted. Technical acceptance remains open pending the independent audit and full cold proof.

## Render evidence

R21 batch manifest is complete and records all 11 fixed views at 960×540, CPU Cycles 24 samples, seed 73 and world strength zero. Reviewed views: `CAM_ENTRY`, `CAM_MAIN_ROUTE`, `CAM_REVERSE`, `CAM_PINCH`, `CAM_PROCESS`, `CAM_HERO_DETAIL`, `CAM_MATERIAL`, `CAM_MINE_TO_CRUSHER`, `CAM_ASSEMBLY`, `CAM_DISPATCH`, and `CAM_WORK_NOOK`. The R19 and R20 manifests were also complete for the all-view comparison. No runtime certification was performed.
