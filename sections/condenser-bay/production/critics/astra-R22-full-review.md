# Turbine Condenser Bay — R22 full independent review

**Reviewer:** independent Luna (gpt-5.6-luna) critic subagent  
**Date:** 2026-09-12  
**Revision:** R22  
**Disposition:** **REJECT**

I inspected every named R22 warm render in `production/renders/review/R22/` and its corresponding cold reopen in `production/renders/review/cold-R22/`: 18 warm plus 18 cold, all reported at 1920×1080. The cold set was separately reopened with process/PID evidence supplied for this pack; `production/validation/R22/cold-comparison.json` reports a worst mean channel delta of 0.000004501/255. The cold set is therefore visually stable for this review. That stability does not cure the visible contract defects or the failed saved-geometry audit.

## Three most consequential defects

1. **C04_EXHAUST.png (warm and cold) · underside/hood exhaust connection · blocker ·** the view is dominated by the dark hood/roof underside and a bright diagonal pipe; it does not show a real U04 receive opening, slab landing, neck, flange, seal, or support. **Consequence:** the assigned turbine exhaust handoff is unverified and the contract/specification category cannot pass.
2. **C01_ENTRY.png, W03_NW.png, W07_EAST_PULL.png (warm and cold) · entry/rear route and west/east clearance lanes · blocker ·** `production/validation/R22/astra-saved-audit.json` remains FAIL: U04 reveal lining intrudes into the nominal 2.5×1.5 opening, the extinguisher/sill test is not clear, the west designated cart lane touches the waterbox, and suction lines cross the pump approach. **Consequence:** the saved geometry contradicts a safe, serviceable receiving and circulation story even where the pixels look plausible.
3. **C06_COOLING.png (warm and cold) · cooling gauge/isolator assembly · major ·** the gauges are now authored and readable, but their long vertical rods disappear into the dark ceiling without a clearly visible structural landing or deliberate pipe/support termination. **Consequence:** cooling supply/return support and isolation remain visually incomplete, weakening machinery logic, construction, and fidelity.

## Other observed defects

- **C05_RETURN.png · lower return/pump handoff · major ·** the orange return assembly is a clear improvement, but its lower connection and final U02 handoff are partly hidden by the motor and foreground rail. **Consequence:** the return path cannot be followed continuously from collection to the turbine-owned interface.
- **W01_ENTRY_CORNER.png · recessed connector alcove · blocker ·** the wall remains an `UNBOUND CONNECTOR` placeholder with no visible socket, flange, threshold, or deliberate termination. **Consequence:** a required awkward-space/interface view is unresolved.
- **C09_ROOF.png · roof/ceiling and overhead services · major ·** the view is mostly dark underside slabs/opening with limited readable roof structure, fixtures, vents, and routing. **Consequence:** the complete room envelope and service roof are not evidenced.
- **W08_GALLERY_TURN.png · overhead gallery turn · major ·** dark rails, hoist pieces, and pipe ends read as partially supported or unfinished. **Consequence:** maintenance/lifting provision is not convincingly usable.
- **W03_NW.png · northwest corner · major ·** foreground pipe and posts occlude motors, condensers, and aisle relationships. **Consequence:** a player-height route and service approach remain difficult to read.
- **W06_WEST_AISLE.png · west aisle camera · major ·** the view is aimed largely at a wall and the shift log, with limited readable aisle depth or service approach. **Consequence:** it does not convincingly cover the named west circulation/awkward-space requirement.
- **C08_MAINTENANCE.png · maintenance bay · major ·** the image is very dark and the maintenance access/readability claim depends on silhouettes more than visible landings and service clearances. **Consequence:** maintenance coverage is weak in the view intended to prove it.
- **C10_MATERIALS.png · material close view · major ·** orange coupling, black guard, bolts, and motor fins are distinguishable, but many surfaces remain smooth and uniform and the close crop does not prove glass edges, floor/support contacts, or the full material family. **Consequence:** material-detail coverage is partial.
- **W04_NE.png, W07_EAST_PULL.png · floor clearance markings · major ·** the yellow/painted lane cues do not by themselves establish cart swept volume; the saved audit additionally records a cartlane/waterbox contact. **Consequence:** circulation cannot be credited from markings alone.
- **C04_EXHAUST.png, C09_ROOF.png · lighting/readability · major ·** the strongest contractual and envelope views are also among the darkest/least legible. **Consequence:** lighting fails to support the claims those views need to make.

## Ten-category strict scoring

The rubric requires every category to score strictly above 90. A score of 90 or lower, or an unverified claim, is REJECT.

| Category | Score | Disposition | Evidence basis |
|---|---:|---|---|
| Contract / specification coverage | 82 | REJECT | U04 receive is not visible; U02 return handoff is occluded; W01 connector is unbound; saved audit fails four relevant checks. |
| Scale / layout | 86 | REJECT | Worker-scale doors, stairs, rails, and equipment are plausible, but cramped/occluded routes and the failed cartlane/waterbox audit prevent acceptance. |
| Machinery logic | 84 | REJECT | Condenser, hotwell/pump forms, and cooling gauges read as an authored system, but U04 receipt is absent, suction crosses the pump approach, and supported cooling endpoints are not proven. |
| Circulation / readability | 82 | REJECT | C04 has no readable receiving approach; W03 is blocked by foreground services; W07 clearance is contradicted by saved geometry; W01 is unresolved. |
| Construction / detail | 84 | REJECT | Flanges, bolt rings, pump details, labels, and gauges improved, but U04 reveal/landing, roof structure, pipe supports, gallery ends, and contacts remain incomplete or unverified. |
| Materials | 88 | REJECT | Orange/ivory/charcoal differentiation and cast/painted machine cues are present, but broad surfaces are uniform and close crops do not prove the required glass, rubber, concrete, fabric, and contact detail coverage. |
| Lighting | 84 | REJECT | Warm practical accents work in hero/operator views, while C04, C08, C09, and W08 leave critical structure and interfaces too dark to verify. |
| Palette | 91 | PASS | Restrained ivory, charcoal, oxide-orange, and safety-yellow family is coherent; no teal/cyan decorative lighting theme was observed. This single passing category cannot rescue the review. |
| Storytelling / environmental specificity | 86 | REJECT | Shift log, labels, mug/tools, and maintenance dressing add context, but blank connector space, empty/dark envelope views, and unresolved handoffs weaken the facility story. |
| Valorant / reference fidelity | 84 | REJECT | The condenser silhouette is distinct and R22 adds specific gauges/return construction, but it remains below the turbine/cooling neighbor bar for support depth, route legibility, roof evidence, and finished industrial specificity. |

## Evidence and limits

The complete warm/cold camera set was inspected, including C01–C10 and W01–W08. The cold reopen is stable by the supplied separate-process evidence and the tiny measured image delta. The following claims remain unverified or failed: dimensioned saved clearance around the cart/handler lanes; visible U04 flange/neck/slab landing; complete U02 cap-side handoff; cooling remote endpoints and structural support landings; complete roof/services envelope; and several close crops required by the rubric (exhaust flange, floor/support contacts, door/access reveals, and glass edges). The saved audit failure is retained as binding evidence rather than overridden by the render appearance.

**Final decision: REJECT.** A future cycle needs new warm and cold pixels for every claimed fix; no R22 score is copied forward to R23.
