# Luna independent Fuel Corridor walkthrough and wayfinding review

**Status: HOLD / baseline rejected for correction. No final score or preapproval.**

Reviewed the shared build brief and Fuel Corridor brief, the local connection contracts and contents specification, the P07 interface, the frozen `full04` manifest and five available `full04` route pixels, plus `production/evidence/walkthrough/wayfinding-before.json`. No live Blender session was opened, no scene or source was edited, and no render was run. The walkthrough evidence is incomplete: the manifest records only C01–C05 of the required ten formal and six diagnostic views.

## Requirement interpretation

The documented layout is coherent for the assigned connector scope. `interface.json` defines five external port identities: F01 refinery, F02 reactor, S01 plant, S02 clean and S03 waste. The authored assembly list adds one internal freight gate. The consistent interpretation is therefore **5 external door assemblies + 1 internal gate = 6 assemblies**, each represented by two sliding leaves for **12 leaves**. Twelve leaves must not be described as twelve doors or twelve proven exits.

The plan and source use the proposed identifier families F01, F02, S01, S02, S03 and FG01 for the internal gate. The current visible baseline instead repeats `04`, `FC / 04`, `FC-04 / L` and `FC-04 / R` across route signs, bay markers, gate text and all five external door pairs. That value has no stated role and is visually presented as both a zone/route number and a door/equipment identity. The corrected walkthrough should use the documented codes consistently, with destination words retained. No reviewed brief requires a contiguous door sequence.

The floor cells span X −5.4 to 17.0 and Y 0 to 24: an irregular connected footprint with a **22.40 × 24.00 m bounding envelope**, not a filled rectangular room. The freight centerline is 38.20 m; the bypass is 23.40 m. Freight uses the two 3.00 m turn allowances and the 2.20 × 0.90 m conservative transport allowance. The service route is 2.40 m gross / 2.00 m dressed target, with a 3.00 m north leg. These are design and planning contracts; turning, stretcher motion, runtime door operation, global assembly and end-to-end travel remain unverified.

F01 and F02 presentation caps are section-owned assemblies. The neighboring refinery sill and reactor closure remain separate ownership layers; the reactor doors are documented closed. A visible cap or labeled port therefore does not prove an open neighboring route.

## Baseline readability findings

The evaluated wayfinding probe contains 143 glyph/arrow rows. Its method checks backing within 80 mm and front obstruction within 500 mm in the normal direction; it does not establish viewing-distance legibility. The baseline has **11 front-blocked rows / 680 samples** and **4 rows with unbacked samples / 43 samples**.

Primary route-label defects are concentrated at the plant branch, the cross-passage identity and the reactor delivery identity:

| Baseline group | Finding |
|---|---|
| Plant identity | `PLANT` has 32/182 unbacked and 32/182 blocked samples; `SERVICES` has 66/189 blocked samples; one chevron is fully unbacked and another has 4/6 unbacked samples. |
| Cross-passage identity | `FUEL ROUTE` has 45/197 blocked samples and `KEEP TURN CLEAR` has 14/183 blocked samples. |
| Reactor delivery identity | `REACTOR` has 42/184 blocked samples and `FREIGHT APPROACH` has 51/181 blocked samples. |
| Smaller labels | Service-air label has 24/184 blocked samples and the plant door title has 2/182 blocked samples. These remain placement checks, not a viewing-distance score. |
| Non-route occlusion | Spare-parts label is 197/197 blocked; first-aid label is 205/205 behind its clear lid. These do not substitute for the primary route defects and should not be counted as route unreadability without pixel confirmation. |

The five inspected pixels broadly establish entry, staging, a cross-route turn, the refinery endpoint and the waste/reactor approach. They also show the ambiguity in practice: large `04` markers coexist with `SERVICE`, `REACTOR`, `REFINERY` and `WASTE TRANSFER`, while the visible gate header reads `FUEL TRANSFER / 04`. The camera framing further crops part of a route sign in C02/C03, so corrected evidence needs full-frame checks for approach readability rather than relying on object inventory.

## Required corrected evidence checks

Before any acceptance decision, the replacement evidence should demonstrate:

- All primary destination and branch signs are fully contained by appropriately sized, physically supported backings, with no wall post, flange, web, rail or fixture crossing the readable face.
- F01, F02, S01, S02, S03 and FG01 appear in the correct route/door contexts, and `04` is removed or explicitly redefined so it cannot be mistaken for a port or gate identity.
- The full route can be followed in both directions from the formal cameras: refinery → freight staging → FG01 → east turn → reactor approach, with the bypass and all three reserved service branches distinguishable.
- The five external ports remain five reserved/section-owned connections, and F01/F02 caps are visibly and textually distinguished from neighboring closed doors.
- All ten formal and six diagnostic views are present in one corrected manifest. The gate-mechanism view must be inspectable; filenames, object names and manifest descriptions cannot substitute for pixels.
- Recheck text support and obstruction after the wall/post correction, then perform a fresh saved-file verification. This review does not infer navigation, engine collision, controller behavior, structural capacity or runtime opening from the current evidence.

**Luna decision on this baseline:** reject for correction and hold final scoring. Await the corrected walkthrough evidence before assigning a final visual/readability score or approval.
