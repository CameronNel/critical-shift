# Luna independent corrected walkthrough review — wayfinding-walk01

**Decision: HOLD / no preapproval.** The corrected wayfinding is materially improved, but player-height readability remains below the 90 threshold in two supplied views. This is a walkthrough-only review; it does not accept the paused full build.

I directly inspected all eight supplied images in `production/evidence/walkthrough`: `plant.png`, `refinery.png`, `gate.png`, `reactor.png`, `waste.png`, `clean.png`, `delivery.png` and `service.png`. I also read `wayfinding-walk01.json` at revision `full04`. No live Blender session was opened, no scene or source was edited, no GPU work was run and no agents were spawned. The images are direct perspective captures with UI chrome; the readability scores below are pixel judgments of the apparent eye-height views, not proof of a runtime player camera, controller or field of view.

## Scores

| Category | Score /100 | Basis |
|---|---:|---|
| Sign size and hierarchy | 92 | The 1.65 × 1.10 m panels, common 0.245 m titles, 0.40 m codes and 0.105 m subtitles establish a strong code → destination → function hierarchy. Primary titles and codes remain readable at oblique approach distances; small mechanical labels remain appropriately secondary. |
| Sign shape / visual integration | 91 | The eight panels use a consistent industrial format with dark frames, pale faces, orange edge accents, visible fasteners and compatible route chevrons. The large panels are assertive in narrow views but remain coherent with the corridor construction. |
| Door compliance | 93 | The visible pair-leaf assemblies carry matching port identities and destination words: F01 refinery, F02 reactor, S01 plant, S02 clean and S03 waste. The open internal gate reads `FG01 / FREIGHT`; external doors remain visually closed. This is visual compliance only; motion, controller behavior and neighbor passage are unverified. |
| Destination semantics | 94 | The corrected labels consistently map F01 → REFINERY / FUEL ASSEMBLY, F02 → REACTOR / FUEL TRANSFER, S01 → PLANT / TURBINE-ELECTRICAL, S02 → CLEAN / MEDICAL-COMPLIANCE, S03 → WASTE / WASTE TRANSFER and FG01 → FREIGHT. Service and delivery cues reinforce the route without the former ambiguous `04` numbering. |
| Player-height readability | **88** | Six views are clear at the supplied perspective. `clean.png` clips the right side of the S02 destination panel, truncating the visible `MEDICAL / COMPLIANCE` line; `service.png` places the plant branch cue at the frame edge behind foreground equipment/structure, so the branch is less immediately readable from that approach. These are pixel-level presentation issues even though the geometry audit is clean. |
| Backing and construction quality | 92 | The panels read as physically mounted assemblies with substantial faces, edge frames, fasteners and supporting members. The corrected audit reports zero unbacked glyph samples and zero opaque forward obstructions across the 143-row set. Its sole remaining ray hit is the transparent first-aid lid, which is not an opaque sign obstruction. The audit does not prove oblique readability or load capacity. |

## Per-image findings

| Image | Score | Finding |
|---|---:|---|
| `plant.png` | 92 | S01 / PLANT door pair and branch panel are clear; S02 / CLEAN is also visibly resolved across the turn. The central structural post separates the two destinations without crossing their readable faces. |
| `refinery.png` | 93 | F01 / REFINERY is readable on the overhead door header, leaves and the oblique wall panel. FUEL ASSEMBLY supplies useful destination context. |
| `gate.png` | 92 | FG01 / FREIGHT is clear over the open gate, with the F02 / REACTOR destination cue visible beyond. The route direction and floor marking agree. |
| `reactor.png` | 93 | F02 / REACTOR and FUEL TRANSFER are legible on the header and both leaves. The framing gives the door a strong destination anchor. |
| `waste.png` | 93 | S03 / WASTE and WASTE TRANSFER are immediately readable, and the distant F02 reactor cue confirms route context. The large left panel remains inside the supplied view sufficiently for the identity to read. |
| `clean.png` | **87** | S02 / CLEAN is clear on the header and leaves, but the right wall panel is cropped at the image edge and its `MEDICAL / COMPLIANCE` subtitle is visibly truncated. This is the clearest remaining player-height readability defect. |
| `delivery.png` | 92 | F02 / REACTOR and FREIGHT APPROACH are clear on the oblique approach panel and door; the route line supports the destination read. |
| `service.png` | **88** | The overhead PLANT SERVICES sign, S02 / CLEAN panel and service equipment establish the junction. The plant branch cue at left is partially lost behind the foreground framing and image edge, so the first-glance branch read is weaker than the dedicated plant view. |

## Contract and count check

The corrected evidence uses the requested identity semantics while preserving the documented topology: five external assemblies (F01, F02, S01, S02, S03), one internal freight gate (FG01), and twelve leaves total. The corridor remains the irregular 22.40 × 24.00 m floor envelope. These counts describe authored assemblies and leaves; they do not establish six open exits or a connected neighboring facility.

The corrected wayfinding probe has 143 rows and reports no unbacked glyph samples and no opaque obstruction samples. That is a meaningful construction improvement over the prior baseline, but its own method says it does not establish viewing-distance legibility. The direct pixel issues in `clean.png` and `service.png` therefore remain valid review findings.

## Required follow-up before acceptance

- Supply a replacement clean approach view in which the entire S02 destination panel and subtitle are visible and readable from the same apparent eye-height distance.
- Supply a replacement service-junction view in which the S01 plant branch cue is readable on first approach without relying on the dedicated plant close view.
- Recheck that those views preserve the backing/support result and the F01/F02/S01/S02/S03/FG01 semantics.
- Keep broader engineering, runtime, neighboring-door, cold-render and paused full-build acceptance separate from this walkthrough review.

**Luna result:** corrected wayfinding is close and the numbering semantics are now coherent, but `clean.png` (87) and `service.png` (88) are below 90. Await replacement evidence; no preapproval.
