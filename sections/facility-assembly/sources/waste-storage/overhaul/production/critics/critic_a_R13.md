# Critic A — whole-room cycle R13

## Scope and evidence

I inspected all 21 R13 fixed-camera images individually and paired each with its R08 image. The R13 manifest is complete; its source SHA matches `validation_R13.json`. I also reviewed the actual accepted Spawn `VALIDATE_Hero_A.png` and `VALIDATE_Spawn.png`, plus refinery R24 `CAM_ENTRY.png`, `CAM_HERO_DETAIL.png` and `CAM_WORK_NOOK.png`. Black beyond module portal openings is expected; I judged the authored frame, jambs, threshold and approach. Scores cover editable Blender source only. Cold-state proof remains pending, and these scores make no Unity runtime, collision or navmesh claim. The unchanged acceptance bar remains >=99 in every category with no vetoes.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 79 | 20% | Required four-cell plan and protected poses remain intact; receiving, freight spine, turns, cell approaches, personnel and booth access are clear in the required views. No route-layout defect is inferred from required repetition. |
| Art direction, architecture and silhouettes | 72 | 20% | The overhead capture header adds a more specific process silhouette, and folded steel, cask heads and quarantine details are stronger. The room still has highly repeated cask silhouettes and many same-value teal boxes; the new header's relationship to each station and its exhaust route is not fully resolved in camera. |
| Waste-process hero equipment and functional clarity | 81 | 15% | Quarantine filter pleats are visible through the window; C08 shows bright internal pleated elements; cask heads and C05 restraints read better. The capture-to-duct path remains visually ambiguous, cart ratchets are hidden under the load, and the incoming/extraction/receiving sequence is not clearly one operation. |
| Materials and anti-plastic quality | 72 | 15% | Brown straps and the grooved seal ring add distinct material/form cues. Lower-wall spalls remain angular, similarly colored islands, cask-body mottling remains broad in W04, and some surfaces are clean, flat slabs. Metal, cloth, rubber, wood, paper and glass are not yet uniformly reference-level. |
| Fixture-only lighting and gloomy atmosphere | 74 | 10% | The scene retains dark intervals and localized fixture pools. Inspection elements in C08 now separate from the dark plate. The cask/hood area remains mostly broad, subdued ambient surfaces and the new internal elements verge on isolated bright slits rather than a fully readable inspection task. |
| Purposeful dressing and human storytelling | 64 | 10% | The tension straps, cask service details, repair gasket and inspection window strengthen task cues. C09 is still mainly a monitor and meter; D01 remains a neat arrangement without an active repair state, and the room lacks the specific lived-in cues seen in refinery R24 WORK_NOOK. |
| Technical cleanliness, contacts and reproducibility | 90 | 10% | The complete 21-view manifest matches the validated source. Validation PASS reports 483,346 evaluated triangles, 247 protected poses unchanged, 256 new plus 57 inherited contacts, 26 fixture pairs, 23 emissive surfaces, six extractor-cavity rays, six header-to-hood air-path checks, no sampled route obstructions and no listed issues. Cold-state proof is pending; sampled checks are not exhaustive. |

**Weighted total: 76/100** (75.6 before rounding). R13 makes substantive progress in process cues and silhouette, but is still far below the 99-per-category bar. No layout veto is observed. The principal visual veto-level concern is that the extraction operation remains incompletely legible in the fixed views, despite stronger inspection-window contents.

## Camera-by-camera comparison

| Camera | R08 → R13 pixel result |
|---|---|
| `C01_Entry` | A new louvered header appears above the left cask/work area, adding a large process cue but projecting into the upper-left room silhouette. It reads as a dark grille/box; this wide view does not show a convincing support or duct transition. Aisle stays clear. |
| `C02_Casks` | Header and hood form a more coherent overhead silhouette above the two vessels. However, the pair still repeats the same body, fittings and material state, and the header has no readily visible branches to individual stations or duct path. Cask badges remain tiny at this camera distance. |
| `C03_Reverse` | No material scene change. The aisle and mandated four-cell structure remain clear. The brown horizontal faces at left still differ from the cool folded-steel language across the right bay. |
| `C04_Route` | No material scene change. Route is open. The hood/capture relationship is not visible from this angle, and small lane marks are doing more work than the floor's wheel-wear story. |
| `C05_Transfer` | Warm tan webbing is now clearly visible across the canister compared with R08's unrestrained-looking load. Strap runs down the near face; the tensioner and bed anchors are hidden below/behind the raised load plate. The load reads seated and tied, but the hardware path is incomplete at the actual pixel scale. |
| `C06_Dry` | No meaningful change. Formed lids and restraint shoes remain more specific than earlier cycles, but broad pale lid faces still dominate and adjacent lid wear is not consistently confined to narrow rims. |
| `C07_Quarantine` | Filter is brighter and pleated body is now clearly visible through the front viewport, a strong functional improvement. Its lower body remains occluded behind the bin lip, leaving the window to reveal only part of the object. Angular wall chips remain visible in the background. |
| `C08_Extraction` | Two inspection openings now show bright internal cylindrical/pleated elements; the maintenance state is much more credible than R08. They remain narrow high-contrast slits, and the broad extraction assembly still does not show an unambiguous source, process step and contained destination. |
| `C09_Inventory` | Display and dose meter remain readable. Wall chips are more localized but tiny at this crop; no larger hold/discrepancy state is visible to make the operator's current task clear. |
| `C10_Workbench` | No material scene change. The workbench remains locally readable but tidy; gasket and gloves do not show a new active repair relationship from this camera. Wall damage remains angular. |
| `W01_Personnel` | No material change. Jamb, lintel and approach remain legible; black past the portal is expected. |
| `W02_ReceivingReturn` | No material change. Opening and approach remain clear. Existing lower-wall islands are still angular and warm colored. |
| `W03_Dispatch` | No material change. Portal threshold and authored frame are readable; expected black beyond remains outside the critique. Wall chips are small and similarly shaped. |
| `W04_CellService` | No material cask change. The close vessel body still carries broad mottling below its head, so wear is not fully confined to rims, shoes and service contacts. |
| `W05_ReceivingExterior` | No meaningful scene change. Route and cart stay readable, but the new strap hardware is too small to see from this camera. The repeated box forms remain a large portion of the view. |
| `W06_PersonnelExterior` | No material change. Cart, booth and route are legible; at this distance strap anchors and any load state details disappear. Wheel rub is faint. |
| `W07_DispatchExterior` | No material change. Route remains clear; cask/box silhouettes and bay pattern repeat. Left horizontal brown faces continue to read as a different material family. |
| `W08_BoothDoor` | No material change. Booth panel, door and desk remain visible; the view has little maintenance storytelling beyond the existing equipment. |
| `W09_DrySouth` | No material change. Head/panel construction is clear, but adjacent broad light lid faces and rim staining remain visually dominant. |
| `W10_ResidueService` | No material change. Cask crowns and service fittings are readable, but the repeated vessels have little differentiation in contents/state or handling evidence. |
| `D01_SealRepair` | Ring now has a stepped/grooved cross-section that reads as a made component rather than a plain torus. Bench is still cleanly staged; gloves and ring have no obvious active contact/repair sequence or residue. |

## Highest-impact remaining pixel repairs

1. **Complete the capture story around `C01`/`C02`.** Keep the header's useful silhouette, but make its intake and exhaust path visibly continuous and supported, and show how it serves the cask stations. Avoid a floating grille above the vessels; keep the fixed cask poses and route unchanged.
2. **Expose `C05` tensioner/anchor hardware at full-view scale.** The webbing is present and readable, but the camera cannot see how it tightens to the cart. Bring one ratchet/buckle and the near bed anchor into the visible front/right edge region of the load plate, retaining a taut path and the seated load.
3. **Differentiate the required cask/cell lineup through authored state.** R13 has a useful new overhead capture cue, but C02/W10 still read as cloned casks and C01/C03/W07 repeat the same bay faces. Preserve the four-cell layout and protected poses; distinguish cell states with a few mid-scale construction/material cues, status windows, seals or work hardware that survive at the specified camera resolution.
4. **Replace repeated angular paint-loss islands with layered, localized damage.** The spalls in W01–W03/C09 are sharper than R08 but remain similar warm cutout shapes. Vary paint edge depth, scale and leak direction at plausible joints; reduce broad body mottling still visible in W04 and rim wear on W09.
5. **Make D01 and C09 show an active operator state.** The grooved ring is a better asset, but D01 still looks like a clean display of parts. Add a clear interaction cue at useful scale (e.g. old and replacement seal relationship, engaged hand/tool or contact residue); give C09 a visible hold/discrepancy state through a physical tag or clear panel indicator rather than more small text.

## Bounded technical evidence

The complete R13 manifest has 21 views and its source SHA matches the validation blend hash. Validation PASS lists 483,346 evaluated triangles; protected count 247 with zero changes; 256 new and 57 inherited contacts; 26 fixture pairs and 23 emissive surfaces; six cavity and six capture-air-path checks; zero sampled route obstructions; no unregistered supports; and no reported issues. These are source-side checks. Cold-state proof remains pending; the report explicitly limits anchor and lane rays, and I make no runtime integration claim.

## Layout-score audit and correction

After rechecking the 21 R13 views against the rubric's layout anchor, I cannot substantiate the original 79 score with a camera-specific layout defect. That score was too low and its rationale did not name an observed flaw. The visible evidence supports **99/100 for Layout, scale and route readability**: C01/C03/C04 show an open receiving/freight spine and readable turns; C02/W04 show plausible cask and cell approach spacing; W01–W03 show readable personnel/receiving/dispatch openings and thresholds; C09/W08 show booth access; C05/W05/W06 show the cart and its route without blocking the visible lane. These fixed poses and the four-cell arrangement are contract requirements, not defects. No required camera visibly demonstrates a blocked approach, implausible scale, or route ambiguity. Validation reports no sampled route obstruction; I use that only as corroboration, not as exhaustive runtime proof. There is no layout veto or additional layout repair supported by the current pixels.

This correction supersedes the 79 layout row above while preserving the review history. The other six category scores are unchanged. The corrected weighted total is **80/100** (79.6 before rounding). This layout score does not alter the overall non-acceptance verdict: the other visual categories remain below 99, and cold-state proof is pending.
