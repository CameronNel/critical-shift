# Luna independent pixel review — Cooling Plant R06

Date: 2026-09-11
Reviewer: Luna, independent reviewer
Evidence: `production/renders/review/R06/`, C01–C10 fixed cameras plus W01–W08 eye-height views

This review uses the actual R06 pixels and the supplied R06 objective/walkthrough reports. No later R07 camera or source changes are credited.

## Category scores

| Category | Score /100 | R06 verdict |
|---|---:|---|
| Specification coverage | 92 | Pass at current visual evidence |
| Layout / flow | 92 | Pass |
| Machinery | 93 | Pass |
| Navigation / readability | 89 | Fail pending W08 replacement |
| Construction | 92 | Pass |
| Materials | 90 | Pass at threshold |
| Lighting | 90 | Pass at threshold |
| Reference fidelity | 92 | Pass |

**R06 overall: NOT YET ACCEPTED.** Seven categories reach 90+, but navigation/readability is 89 because W08 remains too close and visually dominated by a neutral gray boundary, and W06’s floor withdrawal wording reads reversed from its camera. The final cold-start render comparison is also still pending even though the current objective reports pass.

## Objective evidence

- `R06-validation.json`: **PASS**, zero failures, matching saved/current source hashes.
- `R06-walkthrough.json`: **PASS**, all eight conservative routes pass with zero collision samples, including the permanent cart return, both pump service paths, alcove/bench path, HX aisle, exact 3.5m withdrawal-bay path, reserve/mine-water path and secondary rear service access.
- The exact 3.5m withdrawal condition is checked as an empty reserved volume by the report; W06 provides the wider side-view pixel evidence. Neither alone proves runtime extraction, but together they are credible authored-scene evidence.

## Per-view observations

### Fixed cameras

- **C01_ENTRY:** Strong integrated overview. Two pumps, central route, rear service alcove, exchanger, hoist and drains read together. HX-01 marking is now legible; reserve/mine-water hardware remains outside the main composition.
- **C02_HERO:** Good exchanger silhouette, correct HX-01 ID, clear flange/gauge/saddle/hoist relationship. Close framing still hides the complete rear reserve and lane context.
- **C03_REVERSE:** Clear return orientation with pumps right and HX left. The reactor boundary is intentionally neutral/unassembled and must remain so; the blank gray panel provides little connection readability, but no invented corridor is required.
- **C04_ROUTE:** Central lane and service alcove frame read cleanly. It remains sparse and does not show every recovery control, but route value/edge treatment is consistent.
- **C05_PUMP_A:** Strong pump detail, guards, gauges, flange, plinth and material separation. Operator clearance is inferred from the measured route rather than visible in this close frame.
- **C06_EXCHANGER:** Strong exchanger construction and improved ID legibility. The close crop continues to hide the full withdrawal length and side service relationship.
- **C07_PINCH:** Pump B and D02 service door read clearly. The door/alcove approach remains visually tight, although the objective route now passes.
- **C08_WORKSHOP:** Bench, vise, tools, rag, seal and note communicate maintenance. Lower storage remains dark and cleanly staged; tactile wear is restrained to the point of slight sterility.
- **C09_BUNDLE_BAY:** Rear exchanger face, pipework and bay edge read. The frame still does not show the complete 3.5m path; W06 is the necessary wider evidence view.
- **C10_MATERIALS:** Excellent close read of oxide casing, charcoal motor, yellow guard, coupling and hardware. Materials are mostly smooth and low-wear but remain clearly separated.

### Eye-height views

- **W01_ENTRY_APPROACH:** Strong eye-height whole-room read, with central lane, both pumps, HX and workshop zone. Useful integration evidence, though exact entry opening/headroom remain measured checks.
- **W02_RESERVE_APRON:** Reserve restart and backup-water signage are now separated and legible. Valve, cabinet and wall labels read as distinct functions; no visible teal contamination remains. The view is close enough that full route context is limited.
- **W03_PUMP_OPERATOR:** Good operator-height pump/coupling and gauge read. The adjacent door is visible behind the machine, but service clearance remains easier to trust from the walkthrough than from this crop.
- **W04_ALCOVE_APPROACH:** Now a valid, useful view: open D02 leaf, jamb, workshop bench, tools and standing area read together. The door dominates the left foreground but the approach is no longer an evidence void.
- **W05_WORKSHOP_ROUTE:** Workshop and route relationship read with bench, note, tools and right-side return window. Lower shelf remains dark; a prop tray at the edge is secondary and does not visibly block the route.
- **W06_WITHDRAWAL_CLEAR:** Wider side view shows the empty rear exchanger work volume, wall clearance, floor boundaries and overhead hook. This complements the measured empty-volume check. The floor “BUNDLE PULL / KEEP CLEAR” text is reversed/upside down from this view and should face the aisle for readable navigation.
- **W07_SECONDARY_SERVICE:** Side service strip, wall-connected secondary pipework, valve and HX support read. It remains visually narrow and pipe-dense, but the measured rear sweep passes and no blue/teal contamination is apparent.
- **W08_RETURN_THRESHOLD:** Camera is no longer blank, but it is still too close: almost the entire frame is the neutral gray unassembled boundary framed by the jamb, with no readable route, machinery or interior connector context. This is the remaining pixel-level navigation/readability blocker and justifies the planned wider replacement.

## Category rationale

**Specification coverage — 92.** The full image set visibly covers the pumps, HX, hoist, workshop/alcove, central lane, reserve restart, backup-water service, drains and maintenance routes. R06’s measured reports cover all eight walkthrough routes and the exact 3.5m withdrawal empty volume. The neutral boundary and close views still leave remote/assembled neighbour context intentionally unclaimed.

**Layout / flow — 92.** C01/W01 establish a coherent pump-left / route-center / HX-right organization, and the measured route set passes. The exchanger withdrawal condition is now supported by W06 plus the report. W08 remains weak for reverse-threshold communication but does not negate the broader layout.

**Machinery — 93.** Pump and exchanger forms are specific and consistently readable, with guards, flanges, gauges, saddles, supports and hoist components. R06’s close views are strong; remaining limitation is that integration views cannot show every service control simultaneously.

**Navigation / readability — 89.** Route markings, wall signs and functional labels are generally clear, and W04/W06 materially improve evidence. W08 still fails as a useful return-threshold view, while W06’s floor wording is reversed from the camera. These are concrete, localized defects rather than a room-wide failure.

**Construction — 92.** Visible plinths, pipe bends/supports, wall panels, drains, hoist, flanges and service hardware read as plausibly assembled. Objective geometry and support checks pass. The unassembled neutral neighbour boundary is correctly treated as a boundary, not a missing invented corridor.

**Materials — 90.** R06 holds the required warm ivory, charcoal, muted oxide orange and yellow safety palette with no visible teal. Distinct families read in close and overview views. Surface variation and wear remain restrained/clean enough to verge on synthetic in C10/C08, so this is a threshold pass rather than a high score.

**Lighting — 90.** Practical warm pools and broad neutral fill support pump, HX, workshop and route readability. C08 lower storage and W07 side service are darker, while W08’s neutral boundary is visually flat. No severe blown highlights, cyan glow or flat-room wash is present.

**Reference fidelity — 92.** The room now follows R05/R06/R07’s no-teal Valorant direction: broad silhouettes, controlled color grouping, restrained labels, practical warm lighting and tactile but simplified machinery. The deliberate neutral unassembled boundary is compatible with the coordination state and must not be “fixed” by inventing a reactor corridor.

## Remaining blockers before final acceptance

1. Replace W08 with the planned wider return-threshold view and confirm that the enclosed interior threshold, central route and neutral boundary read together without inventing neighbour geometry.
2. Reorient the W06 floor withdrawal wording toward the aisle so the warning is readable from the review camera.
3. Preserve the current objective PASS and matching source hash through the next rebuild; no later camera/source fixes are credited until their pixels are reviewed.
4. Complete the required final cold-start render comparison. R06’s objective PASS is not itself cold-start art evidence.
