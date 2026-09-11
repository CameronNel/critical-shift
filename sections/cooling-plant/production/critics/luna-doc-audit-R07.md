# Luna delivery-document audit — before R08 review

Date: 2026-09-11
Scope: `sections/cooling-plant/` only
Mode: read-only audit; no non-critic documentation was edited

The following discrepancies are concrete stale-state or wording hazards. Historical review files may retain their historical scores when clearly labelled; active handoff documents should describe the current R08-in-progress state.

## Active documents needing refresh

1. **`scenery/cooling-plant.md:7`** still says only the pump/workshop style slice is built and full-room functions are unproven. R06 already has a complete full-room build and R06 objective/walkthrough PASS; R08 is the current build under review.

2. **`production/ACTIVE_STATUS.md:7`** says R05 palette-reference approval is pending. Luna approved R05 (94/92/92/91/93) and R06/R07 concept guidance. The sentence should retain the rejected teal/photoreal history while stating the current concept set is approved direction.

3. **`production/ACTIVE_STATUS.md:13`** still says “Luna R06 review pending” and “R07 rebuilding only” while the Luna R06 review is recorded and R08 is now building. Update the current revision/status after R08 evidence exists.

4. **`production/CAMERAS.md:3`** still says only C07/C08/C10 have slice evidence and full-room evidence is pending. All ten fixed and eight eye-height R06 views were rendered and independently reviewed; W08 replacement/R08 evidence is the remaining current review state.

5. **`production/TASK_STATE.md:3`** still names R06 as current and says final Luna approval is pending. It should point to the R08 render/review state once the batch is available, while retaining R06 as historical evidence.

6. **`sections/cooling-plant/README.md:3,12`** still identifies R06 as current and links only the R06 review batch. Update to the current R08 evidence location after R08 renders; keep the accurate statement that final acceptance/push and whole-map/runtime integration remain pending.

7. **`CONTINUE.md:7,9`** still instructs the next operator to finish R06 and obtain the R06 Luna review. R06 review is complete; the continuation should reference R08 and the planned wider W08 result. Its explicit “no fixed cosmetic-cycle count” and “neighbours remain unassembled” language is current and should be preserved.

8. **`production/CORRECTION_HISTORY.md:11`** describes the “current R05 walk report” after the R06 route correction. The report actually consumed for the latest PASS is R06 walkthrough evidence; rename the reference or explicitly mark R05 as historical.

9. **`interface.json:317,590`** contains stale S03 acceptance wording: the workbench source alignment still says the S03 trim is required and the KC-BENCH note says final standing-space/door acceptance is pending. R06 objective and route reports pass these checks; preserve the contract but update these as-built/status notes to point to the current PASS, pending only future rebuild/hash/cold evidence where applicable.

## Stale palette and rubric language

10. **`art/REFERENCE_REVIEW.md:3`** calls “restrained teal machinery” part of the current calibration and attributes the review to an Astra reviewer. Teal is now explicitly rejected by the user for Cooling Plant. This line should be labelled historical reactor-reference observation and state that current implementation uses ivory/charcoal/oxide-orange/yellow.

11. **`production/critics/luna-calibration.md:20,22,47,48`** still presents teal machinery as an active material/reference standard and says teal primitive language is a future hazard. The current acceptance standard should use the no-teal palette; retain historical teal warnings only as rejected-history context. Its S03 five-failure blockers and “no full-room score exists” language are historical and should be clearly marked as such if the file remains active.

12. **`production/RUBRIC.md:3–20`** is still the old S01/S02 slice rubric with unscored scale/technical categories, stale teal/color references in its historical framing, and a fixed “minimum four full review/correction cycles.” The current handoff uses eight integration categories and the user explicitly removed a fixed cosmetic-cycle count. Replace the active rubric with current Luna integration scores/criteria or label the entire table historical.

13. **`production/CHECKLIST.md:5,8–10`** still treats style-slice approval, detailed equipment and route authoring as incomplete and requires four full cycles. Those items have current R06 visual/technical evidence or are superseded by full-room-first work. Keep genuinely pending items (R08 review, cold-start render comparison, stable evidence, commit/push) and remove the fixed-cycle wording.

## Four-cycle wording requiring an explicit decision

The current R06 technical report and JSON (`production/technical/R06-validation.md:14` and `R06-validation.json:9`) still say final completion requires “four full review cycles.” This is inconsistent with the resumed user instruction recorded in ACTIVE_STATUS/CONTINUE: no fixed cosmetic-cycle count. If the project still requires a protocol-level number of complete evidence cycles, document that as a separate non-cosmetic technical requirement; otherwise update the R06 current report wording. Historical R01/R02/R04/S02/S03 reports may retain their recorded old acceptance policy if clearly historical.

## Whole-map and approval wording audit

No active file was found to claim whole-map or runtime approval incorrectly. `README.md`, `architecture/README.md`, `architecture/CONNECTIONS.md`, `interface.json`, `production/ACTIVE_STATUS.md`, `CONTINUE.md` and `production/technical/R06-validation.*` correctly retain neighbour-unassembled, reactor-door, remote-endpoint, cold-start and runtime limitations. Preserve this language when refreshing R08. The neutral boundary visible in C03/W08 is an intentional unassembled neighbour boundary and must not be rewritten as a missing corridor.
