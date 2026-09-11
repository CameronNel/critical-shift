# Luna independent pixel review — Cooling Plant R04

Date: 2026-09-11
Reviewer: Luna, independent reviewer
Evidence: `production/renders/review/R04/`, ten fixed cameras C01–C10 plus eight eye-height views W01–W08

This review covers the actual R04 pixels only. I do not credit the subsequent R05 corrections. The approved visual direction is R05/R06/R07: warm ivory, charcoal steel, muted oxide orange, yellow safety accents, clean Valorant environmental forms, restrained surface frequency and readable practical lighting.

## Category scores

| Category | Score /100 | R04 verdict |
|---|---:|---|
| Specification coverage | 85 | Fail |
| Layout / flow | 87 | Fail |
| Machinery | 91 | Pass at visual level |
| Navigation / readability | 82 | Fail |
| Construction | 88 | Fail |
| Materials | 84 | Fail |
| Lighting | 86 | Fail |
| Reference fidelity | 88 | Fail |

**R04 overall: NOT ACCEPTED.** The pump/HX machinery reads well, but the evidence set has an unusable W08 frame, a low-information W04 frame, visible palette contamination, signage/ID defects and insufficient proof of several service volumes. No category score is a substitute for the required technical and cold-start gates.

## Per-view issues

### Fixed cameras

- **C01_ENTRY:** Strong whole-room organization and central route. Pumps and HX are cropped at the edges; HX ID is visibly malformed/buried on the shell, and reserve/backup service is not shown.
- **C02_HERO:** Good exchanger silhouette and hoist relationship, but it is too close to prove route and rear withdrawal. HX ID text on the shell is malformed and the pull-out sign is partly clipped.
- **C03_REVERSE:** Clear return orientation and pump/exchanger relationship. The reactor-facing boundary is a featureless gray/neutral plane with little connector information; the floor text is reversed/faint and cannot carry wayfinding.
- **C04_ROUTE:** Central lane and drains read, but the composition is sparse and partial equipment/signs are cropped. It does not prove reserve, mine-water or pump-service operations.
- **C05_PUMP_A:** Strongest pump detail and material separation. Close framing hides operator clearance and the second pump relationship; the panel/screen at left is only partly legible.
- **C06_EXCHANGER:** Good flange, barrel and support read. The exchanger fills frame; rear extraction, side reach and full piping remain unproven. HX lettering is visibly malformed/buried.
- **C07_PINCH:** Pump B and D02 door read with useful scale. Door/alcove approach remains visually tight; full swing and standing strip are not self-evident from the image.
- **C08_WORKSHOP:** Bench props and maintenance story are present. Lower shelf is near-black and materials lose information; dressing remains staged and the view cannot show the adjacent approach defect.
- **C09_BUNDLE_BAY:** Exchanger rear and overhead hook establish intent, but the 3.5m reserve is not visible as a complete working volume. The close framing makes the hook/extraction relationship ambiguous.
- **C10_MATERIALS:** Pump, oxide casing, guard and charcoal motor separate cleanly. Surfaces are smooth and nearly wear-free; dark motor planes suppress detail and the crop hides broader material context.

### Eye-height views

- **W01_ENTRY_APPROACH:** Best eye-height overview: central route, two pumps, HX, alcove and hoist read together. It still crops the entry threshold and reserve service and leaves exact lane clearance to measurement.
- **W02_RESERVE_APRON:** Intended reserve/restart view is compromised by overlapping labels running across the cabinet and by visible blue/teal pipe/handwheel accents that violate the latest palette. Operator context is tight and the sign hierarchy is unclear.
- **W03_PUMP_OPERATOR:** Pump service side and gauges are readable, but the camera is dominated by one pump and provides little route or service-lane context. The door appears behind the machine rather than as a clearly accessible approach.
- **W04_ALCOVE_APPROACH:** Unusable as evidence: nearly the entire frame is blank wall with a cropped door/jamb. It does not show the approach, standing strip, pump relationship or route and should not support a passing navigation/flow score.
- **W05_WORKSHOP_ROUTE:** Useful bench/workshop context and a partial return toward the room. Lower shelving is very dark, the composition is cramped at the right edge, and a parked prop tray intrudes into the visual route story.
- **W06_WITHDRAWAL_CLEAR:** Exchanger end and floor marking are visible, but the crop does not expose the full withdrawal travel or hoist working envelope. The nearby gray boundary reads neutral and gives no direct connector context.
- **W07_SECONDARY_SERVICE:** Shows the exchanger-side service strip and wall-connected utilities, but the strip reads narrow and crowded. Blue/teal pipe bands and handwheel are visible against the no-teal requirement; secondary pipes visually cross the rear access region pending correction.
- **W08_RETURN_THRESHOLD:** Flat gray image with no recoverable room pixels. This is a hard evidence failure for return-threshold readability and makes this camera invalid for acceptance until a fresh render exists.

## Category rationale

**Specification coverage — 85.** R04 visually includes the two pumps, HX, central route, workshop/alcove, hoist, drains and reserve-related components. The entry/return connector, reserve/mine-water functions, complete exchanger withdrawal volume and several service accesses remain hidden, ambiguous or unproven across the set; W08 contributes no evidence.

**Layout / flow — 87.** The room’s pump-left / route-center / HX-right organization is clear in C01/W01. The rear service and withdrawal compositions are too close or incomplete, W04 is unusable and W08 is blank. Labels state 3.5m clearance but do not visually prove the working volume.

**Machinery — 91.** Pumps and HX have authored silhouettes, guards, flanges, gauges, supports and distinct masses. Several close views are strong. Whole-room and service views still hide operating relationships and access context.

**Navigation / readability — 82.** The central lane and yellow edge language help. W04 and W08 are hard failures for fixed-view readability; W02 label collisions, clipped/malformed HX IDs, the neutral return boundary and dark workshop shelf reduce actionable orientation. Color cannot be the only route signal.

**Construction — 88.** Plinths, supports, pipe bends, panel joints, drains, hoist and hardware look plausibly assembled in visible views. The R04 technical report has one reproducibility failure because the saved scene source hash differs from current files; root also reports the source hash is pending rebuild. Known reserve label, cable/sign, trench paint, pipe crossing and instrument/bench corrections remain uncredited here.

**Materials — 84.** Ivory/charcoal/oxide/yellow grouping is generally successful, but W02/W07 visibly retain blue/teal components after the user’s explicit rejection. Smooth clean surfaces, minimal wear and dark workshop/motor regions weaken tactile separation.

**Lighting — 86.** Warm practical fixtures and broad readable illumination work in C01/W01 and machinery views. W08 is flat gray, W04 is low-information, and C08/W05 lower shelving becomes near-black. Several close views flatten falloff and hierarchy.

**Reference fidelity — 88.** R04 preserves Valorant-style broad forms and the no-teal palette in most hero views, but visible blue/teal accents, smooth generic surfaces, sparse world evidence and failed eye-height frames keep the set below the approved target. R05/R06/R07 remain the visual authority; no external branding is present in this batch.

## Objective status and separation from later work

`production/technical/R04-validation.json` reports one failure: `saved_scene_source_differs_from_current_files`. The physical geometry/support/clearance checks otherwise report pass in the current R04 audit, but the source-hash mismatch must be resolved by rebuilding before reproducibility can pass. This review does not credit the R05 label, cable, trench, pipe, instrument or camera repairs before seeing their pixels.

## Highest-impact blockers

1. Produce a valid W08 return-threshold render and a useful W04 alcove-approach render before using those cameras as evidence.
2. Remove all visible blue/teal material contamination and repair reserve-label and HX-ID readability.
3. Verify the rear secondary-pipe changes against the service sweep and make the 3.5m withdrawal/hoist volume readable in a wider eye-height view.
4. Restore detail in dark workshop/motor regions while retaining the clean, broad Valorant surface language.
5. Rebuild from the current source so the saved-scene hash matches, then obtain a fresh ten-camera plus eight eye-height batch before re-scoring.
