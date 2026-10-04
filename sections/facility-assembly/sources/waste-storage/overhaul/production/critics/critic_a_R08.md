# Critic A — whole-room cycle R08

## Scope and evidence

I inspected all 21 R08 fixed-camera images individually and paired them against R05. The R08 manifest is complete and its source hash matches `validation_R08.json`. Black beyond the module portal openings is expected; I assessed the authored jambs, threshold and approach. The scores cover editable Blender source and do not claim Unity runtime performance, collision or navmesh. The acceptance requirement remains >=99 in every category with no vetoes.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 79 | 20% | Receiving, spine, turns, cell approaches, booth and personnel access remain clear in the fixed views. The contract poses and cells are preserved; this score reflects the visible route only. |
| Art direction, architecture and silhouettes | 70 | 20% | The cask heads and quarantine skins have more specific construction and the quarantine bay has a stronger identity. Repetition remains high, and the left/east bay still has timber-like horizontal faces beside folded steel. |
| Waste-process hero equipment and functional clarity | 72 | 15% | The quarantine filter is now visible through a small pane and the cask heads are improved. The filter remains hard to identify through the dark pane, C08 inspection contents remain unreadable, and the extractor task sequence is unclear. |
| Materials and anti-plastic quality | 71 | 15% | Corrosion is narrower around many rims and the sharp wall paint loss has more plausible placement than R05's cloudy patches. Some paint loss still reads as angular cutout decals, cask body wear remains broad in W04, and the east-bay material family is inconsistent. |
| Fixture-only lighting and gloomy atmosphere | 72 | 10% | The existing practical pools and dark intervals hold. The gloom is maintained, but the dark extractor inspection area defeats its stated visual purpose, and the new wall damage does not yet convincingly vary by source or surface. |
| Purposeful dressing and human storytelling | 60 | 10% | The quarantine filter, clearer bay construction and more formed cask tops improve task identity. Cart restraints and desk handling wear do not read strongly; the seal-repair surface remains orderly and much of the room is still sparse. |
| Technical cleanliness, contacts and reproducibility | 89 | 10% | The complete 21-view manifest matches the validated source. Validation reports PASS, 477,941 evaluated triangles, world 0, 247 protected transforms unchanged, 249 new plus 57 inherited contacts, 24 fixture checks, 21 emissive-surface checks, six extractor-cavity rays, and no reported issues. These are bounded source-side checks. |

**Weighted total: 74/100** (73.65 before rounding). The process and construction improvements are real, but no visual category is close to the required 99. R08 is not accepted.

## Camera-by-camera comparison

| Camera | R05 → R08 pixel result |
|---|---|
| `C01_Entry` | Right-hand bay faces are cooler and more clearly folded steel, improving construction. Lower-wall damage has sharper, smaller shapes than R05's cloudy blotches. The opposing brown horizontal bay faces remain wood-like and inconsistent. |
| `C02_Casks` | Head faces are smoother and more distinctly crowned, with clearer formed perimeter construction. The differences read as an improvement, though the casks remain repeated near-identical units and body mottling is still visible. |
| `C03_Reverse` | The right bay now reads more convincingly as cool steel; left bay remains banded brown. Lane and light are stable. Wall chips are clearer but have angular, graphic silhouettes. |
| `C04_Route` | Route remains open. Steel bay faces are improved; chipped patches near the distant door are now sharper but appear as repeated gold shapes. The floor lane still provides more clarity than wheel wear. |
| `C05_Transfer` | Load remains seated and the cart is unchanged in a readily visible way. Restraints do not clearly read as fitted straps or retaining clamps from this close view; the load appears supported by the platform and side blocks. |
| `C06_Dry` | Head profile and shoes/recesses are more engineered. The new lid face is cleaner, though adjacent lids remain very pale; a large clean planar top still dominates the frame. |
| `C07_Quarantine` | New cool-steel side skins and the gasketed pane improve the bin. The filter is more visible than in R05, but only its crown and a dark partial body show; the pane does not yet make its pleated form unmistakable. |
| `C08_Extraction` | The image remains effectively unchanged from R05. No clear transmitted view of internal pleats or inspection state reads; the assembly still lacks a legible source-to-receiving operation. This is the largest unresolved process defect. |
| `C09_Inventory` | The new handling wear around the desk side/wall is visible and more localized. It still has a cutout-like shape; screen and work surface remain clear. |
| `C10_Workbench` | New wall loss is sharper and more localized than R05's diffuse patches. The bench remains a tidy, staged arrangement and the added damage has a low-poly cutout quality rather than convincing layered paint and substrate. |
| `W01_Personnel` | Portal frame and approach remain clear against expected black beyond. Small, sharper lower-wall chips replace R05's large diffuse marks; the damage silhouette is still angular. |
| `W02_ReceivingReturn` | Threshold, frame and approach remain readable. Lower-wall paint loss is better localized than R05, but still forms conspicuous triangular/irregular islands. |
| `W03_Dispatch` | Jamb and approach remain legible. Lower-wall chips have clearer edges and less cloudy spread; at this distance they read as repeated ornamental islands rather than specific impact/leak damage. |
| `W04_CellService` | The cask profile is not meaningfully visible from this close side angle. Broad body wear remains, so narrow-rim corrosion is not fully carried through this view. |
| `W05_ReceivingExterior` | Blue-steel panels unify the right-side bays and the aisle remains clear. Cart load is visible, but restraints are too small at this distance to establish how it is secured. Distant spalls appear more discrete. |
| `W06_PersonnelExterior` | No meaningful scene change from R05; the cart and route remain readable. Wheel rubs are faint at this scale, and the load restraints are not apparent. |
| `W07_DispatchExterior` | Right and central bay steel is more consistent; the far-left horizontal brown faces still look timber-like. Lane and route readability are stable. |
| `W08_BoothDoor` | Booth and task items are unchanged. Lower-wall damage remains largely outside the frame; the view still reads as a clean booth above a sharp paint boundary. |
| `W09_DrySouth` | Lid face is cleaner and several shoes/recesses now read as structural restraint points. The adjacent lid retains broad mottling; the wear family is not yet consistently confined to rims and seams. |
| `W10_ResidueService` | Pressed/cast head profile is substantially clearer and broad top speckle is reduced. Vessel bodies and controls remain repeated, and the far wall damage is minimal. |
| `D01_SealRepair` | Desk handling wear and props show essentially no meaningful change; ring, gloves, tray and overdue note remain legible. The arrangement is still neat and the wear is not conspicuous. |

## Highest-impact remaining pixel repairs

1. **Resolve the extractor view (`C08_Extraction`).** The fixed view still shows a dark, opaque-looking inspection area with no readable pleats. Make the mounted glass and internal material state visibly transmit under the existing practical lighting, then make the extraction/receiving path read as one operation.
2. **Expose more of the quarantine filter through `C07_Quarantine`.** The new pane is a real improvement, but the view shows only a crown and dark partial body. Increase contrast and visible pleated silhouette within the closure envelope so the stored state is recognizable without relying on a label.
3. **Unify the east-bay steel language.** Cool folded skins improve the right bay in `C01`, `C03`, `C04`, `W05`, and `W07`, but the opposing horizontal brown faces still look like timber boards. Carry one coherent steel construction/material family across those views.
4. **Make deterioration read as material failure, not cutout graphics.** `W01`–`W03`, `C09`, and `C10` show sharper loss than R05, but many patches have hard angular islands and similar warm color. Vary edge scale and substrate depth at plausible impacts/leaks; the cask bodies in `W04` also still carry broad mottling.
5. **Clarify how the cart load is restrained and give the maintenance desk handling evidence.** In `C05`/`W05`/`W06`, the load reads as seated but no obvious strap or clamp communicates retention. In `D01`, added desk wear is not strongly visible, so the work surface still feels staged.

## Bounded technical evidence

R08's manifest is complete for all 21 required cameras, and the source SHA matches `validation_R08.json`. The validation PASS lists 477,941 evaluated triangles, 247 protected transforms unchanged, 249 new and 57 inherited contacts, 24 fixture checks, 21 emissive-surface checks, six extractor-cavity checks, zero world strength, and no issues. The report explicitly limits sampled route/contact and fixture checks; no Unity runtime claim is made.
