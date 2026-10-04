# Independent visual review — R49

## Verdict

R49’s targeted coating changes make localized handling wear readable on the casks without reproducing R46’s cloudy camouflage patches or adding a decal-like perimeter. I found no visual veto. Six visual categories meet the working 99 threshold. The overall gate remains **provisional** because the selected R49 cold pixel comparison for all 21 main views and both details is still running; technical evidence is scored 98.5 provisionally.

| Category | Score | Weight | Evidence |
|---|---:|---:|---|
| Layout, scale and route readability | 99.5 | 20% | Protected process routes and cell approaches remain legible in the wide views; repeated cask/cell forms remain clear. |
| Art direction, architecture and silhouettes | 99.0 | 20% | Pressed and folded construction, distinct cell silhouettes, and subdued industrial hierarchy hold across the fixed coverage. |
| Waste-process hero equipment and functional clarity | 99.0 | 15% | Cask collars, lifting hardware, gauges, segregated storage, and room-air extraction read as separate functions. |
| Materials and anti-plastic quality | 98.5 | 15% | R49’s small shell exposures now read as contact wear at normal size, but the broad lit SC01/SC02 body faces remain predominantly smooth and even; the new chips are too sparse to break up the large uniform coating. Other material families remain distinct. |
| Fixture-only lighting and gloomy atmosphere | 99.0 | 10% | Modeled practical pools and dark intervals sustain the brief while keeping the route and work faces readable. |
| Purposeful dressing and human storytelling | 99.0 | 10% | The supported work, transfer, seal-service and shift-log clusters tell the maintenance story without cluttering protected routes. |
| Technical cleanliness, contacts and reproducibility | 99.0 | 10% | R49 original-source authoring state is PASS with 3,065 objects, 290 materials, and identical scene state; hot/cold validation passes at 579,788 evaluated triangles with 335 new and 57 inherited supports, zero disabled material links, and zero issues. All 21 main and both detail warm/cold images are exact RGB matches. |

Weighted total: **99.025**. Materials remains 98.5, below the per-category 99 gate, so R49 **fails** the working acceptance gate despite a weighted total above 99. There is no critical veto. Technical is now final for the package evidence reviewed here; no evidence transfers to R50.

## Actual paired-view evidence

I individually opened all 21 R49 main images and both R49 details with their corresponding R45 images. The full warm manifests are complete and source-unchanged; `comparison_R45_R49.json` verifies paired image hashes, fixed camera matrices/lenses and render settings. The render-state audit reports the 3,058 pre-existing objects’ evaluated mesh positions, polygon/material assignments and ray visibility unchanged; render/Cycles/view settings and frame/layer visibility are unchanged. The only R49 additions in that audit are the seven shell chips and their two changed cask materials plus two new materials. I judge the paired pixels directly despite that state evidence.

| Camera | R45 → R49 observation |
|---|---|
| C01_Entry | Same route and cell hierarchy; R49’s cask chips are faintly visible at the left work area, with no consequential composition or lighting regression. |
| C02_Casks | Clear improvement: small irregular exposures appear at SC01/SC02 collar and carrier contact zones. They read as undercoat chips, not clouding, outlines, or decals. However, most of each broad lit vertical shell remains smooth and evenly coated; the small losses do not yet give the main surfaces the aged variation seen on the refinery hero equipment. |
| C03_Reverse | Same aisle, cells and overhead extraction context; no consequential regression. |
| C04_Route | Protected center route and clearance remain clear; no consequential regression. |
| C05_Transfer | Same loaded transfer cart and route clearance; no consequential regression. |
| C06_Dry | Same folded dry-store construction and restraints; no consequential regression. |
| C07_Quarantine | Same open inspection state and containment framing; no consequential regression. |
| C08_Extraction | Same extraction equipment, duct and service face; no consequential regression. |
| C09_Inventory | Same readable inventory station and work surface; no consequential regression. |
| C10_Workbench | Same seal bench and supported tools. R49 shows faint right-wall tonal variation below the lamp; at this view’s normal size it does not read as a hard patch or materially weaken the wall finish. |
| W01_Personnel | Same personnel opening and visible approach; no route obstruction or material regression. |
| W02_ReceivingReturn | The opening remains clear. R49’s upper receiving-frame area and nearby text have lower contrast in the paired pixels, but the fixed pose and authored geometry are unchanged and the route remains legible. This is a minor tonal/readability fluctuation, not a material gate defect. |
| W03_Dispatch | Same clear dispatch opening and frame; no consequential regression. |
| W04_CellService | Clear improvement: localized SC01 body chips near the collar/carrier are visible without R46’s cloudy treatment or a graphic perimeter. The broad central shell face remains mostly even, reinforcing the same residual material deduction. |
| W05_ReceivingExterior | Same open route and transfer context. Some small signage/edge contrast differs in the paired pixels; no route or functional reading is lost. |
| W06_PersonnelExterior | Same personnel approach and spatial separation. The deep booth lettering is less legible in R49 than R45, but remains secondary context and does not impair the approach or its use. |
| W07_DispatchExterior | Same dispatch route, overhead crane and cask placement; no consequential regression. |
| W08_BoothDoor | Same booth contents and door framing; no consequential regression. |
| W09_DrySouth | Same folded lid and restraints; no consequential regression. |
| W10_ResidueService | Same residue-cell array, controls and labels; R49’s cask contact wear is restrained and does not read as a stamp. |
| D01_SealRepair | Same bench task arrangement and retained replacement seal; no consequential regression. |
| D02_CaptureService | Same capture/header context and cask tops; no consequential regression. |
| D03_ExtractionRun | Same room-air extraction run and service equipment; localized cask wear is visible but does not change the process read. |

The R45→R49 pair introduces no material art regression in my review. The earlier R39→R45 review also found no material regression. These are visual comparisons, not an inference from code or authoring fingerprints.

## Highest-impact remaining observation

The highest-impact remaining visual defect is the broad coating uniformity on SC01/SC02’s lit shell faces in C02 and SC01 in W04: the new contact chips are legible, but most of the visible body still reads as a smooth, evenly coated surface next to the stronger aged surface variation in the refinery reference. This keeps Materials at 98.5. The separate paired differences are limited to subtle contrast/readability variation on secondary wall signage in W02, W05 and W06 and faint tonal variation on the C10 wall; they do not create a route obstruction, a changed frame, or a hard-edged material patch and do not affect the other category scores.

## Technical scope

The R49 selected original-source state comparison passes with zero changed objects, materials, or scene-state fields between checkpoint and original-source rebuild; their blend-file SHA-256 values differ by serialization. Both 21-view main and 2-view detail manifests are complete, source-unchanged, and matched to their respective checkpoint/rebuild fingerprints. I independently compared all 23 warm/cold image pairs: settings, camera matrices and lenses match, each file hash matches its manifest, and every RGB pixel is identical. Hot and cold validation pass at 579,788 evaluated triangles, with 335 new and 57 inherited supports, zero disabled material links, and zero validation issues. This yields Technical 99.0; the package’s sampled support/route checks do not certify Unity collision, navmesh, runtime lighting, or performance.
