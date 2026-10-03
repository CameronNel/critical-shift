# Fixed-view defects for the owner-requested revision

Source baseline: cycle 7 / 8c353ae9f06b9bcf0aeb47c07a8db863fda2575f9c40d1d34f884d2eaa48096b. Cameras remain fixed at 1067 x 600.

| View / region | Visible defect | Correction target | Evidence |
|---|---|---|---|
| HERO_OCRU / frame and liners | Dark flat panels lose manufactured form; too much uniform terracotta | Folded ivory jambs, stepped formed fascia, recessed liner construction, directional material separation | Same-camera clay and lit comparison |
| DETAIL_OCRU / berth | Identical inflated pads and smooth pillow | Bound vinyl, shallow tension creases, stitched panel construction inside inherited envelope | Neutral light, UV checker and lit detail |
| DETAIL_SUPPLIES / bench | Square pristine packages, cylindrical unlabelled bottles and slab-like linen | Folded carton creases, shoulder/cap profiles, wrapped typography, relaxed fabric edges, handled worktop | Fixed detail plus neutral material render |
| ENTRY / walls and lighting | Coarse plaster and uniformly clean room | Quiet fine plaster, material-controlled localized handling/age, clearer red focal contrast | Fixed entry and corner views |
| HERO_RECOVERY / bed | Smooth generic soft goods | Constructed pillowcase, textile folds and contact retained | Same-camera neutral and lit comparison |

Read skills: blender-headless, headless execution, visual review; blender-uv-texturing, surfacing. Only static modeling and materials are in scope. Reuse the existing room builder, validator and renderer. Preserve original module, map, spawn and interface. No runtime or whole-map edits.

## Full-room cycle 8

Independent visual review: 76.9/90, 17/24 camera gates passed; technical: 7.8/10. Acceptance FAIL. Repair the existing directional fill, cover-fitted welts, remove superseded seam geometry, preserve maintenance-card thickness, and refine concealed bag slack. Cycle 9 is pending.

### Cycle 9 repair preflight

At source 42af739f, independent seam/UV preflight passes: 10,032 seam vertices, max gap 1.601 mm / penetration 0.774 mm; obsolete seams removed; no collapsed card/UV faces. Focused lighting remains incomplete: cart still blocked by Seal guide (measured ray hit at [-1.496, 2.800, 2.111]); reserve front unblocked but weak. Moved existing fill to [1.30, 2.00, 2.65], 220 W / 170 degrees; new paths reach cart mattress and reserve. Source preflight is not a full-cycle pass. Paper note now follows bag surface with a 6×6 grid.

### Focused light and reserve refinement

Light 9b resolves cart, reverse leaves and OCRU side interfaces, but reserve remains blocked and rear-zone clarity regresses. Light 9c raises/repositions existing fill to [1.30,3.00,3.30], 280 W / 170 degrees / blend 0.20: entry rear zone and cabinet improve; reserve still too dark. Original battery cases retain old Structural warm graphite material. Revised battery cases use ivory pressed skins with shallow 1.17 mm recess, original envelope and matching label placement; cabinet sides/caps use the approved blue family. Sticky note follows actual folded bag surface and is visible in inspection. Full source and review remain pending.

### Candidate source 55f8e320 — cycle 9 underway

Layout/bounds, 102 support groups / 111 anchors, all 10,032 tailored-seam vertices, normals and physical UVs pass. Same-camera reserve hero now exposes blue shelf/case depth, ivory pressed battery fronts, retaining straps/cradles and handles. Root opened all player-height views, four full-room corners, four wall views and both clinical details; prior dark door and OCRU interfaces improve, bed/bench hierarchy retained. Full render set and independent formal scoring remain incomplete.

## Full cycle 9

Independent visual81.1/90 + technical8.9/10 =90.0/100 PASS. All24 cameras and category minima pass; no critical blockers. Source55f8e320. Final stability remains pending. Material limits: simplified secondary sink/pads, low shadow separation, restrained physical wear. Technical repair targets for cycle10: clean unused default UVs/select explicit render UVs; add recovery/cotton sewn surfaces and both battery labels to permanent checker; correct normalized Generated versus physical UV wording. No art/layout change planned.

## Full cycle 13: intended component support

Source `4da6305d` clears the prior 28 hardware pieces, 130 directed attachment contracts and the hidden bag. The fresh independent critic still found two rolled tray rims 9.401917 mm above their intended pan without sidewalls. An overlapping clipboard is not the intended support. Eight display-surround fixing cylinders also miss their own side bezels by 5.099 mm. Cycle13 is FAIL, regardless of passing visual scores. The creator repair adds continuous pressed tray sidewalls, short returns and five directed tray contacts, and centers all monitor fixings on their matching side panels with rooted per-component contacts. Final candidates must render as fresh complete14HOT/15COLD sets and pass independent reviews before delivery.

## Retained architecture mounting pass after cycle14

The conservative full-room scan proved26 detached compound clusters in the original machinery/fixtures, rather than only new group anchors. Source7b18 was stopped and its23/24 PNGs are incomplete WIP. New bridges connect battery runners/bearings, glazed leaves, OCRU receiver/suit housings, plaques, captive fixing bosses, fixed reserve chassis channels and decon fixture to their intended hosts. Reserve slots now follow their fixed screws; seated telemetry retains its dimensions/matrix, and C01 plaque seating is a6mm small-art pose. Sourcea55 exposed ambiguous bevel-edge anchor normals and an unnecessary new label mount in the reserved lane. The corrected3918 source freezes only witnesses whose actual directional rays satisfy the unchanged gap/penetration/normal tolerances, and seats the existing label instead.166/175 registrations/anchors and181 part contacts now pass hot/cold. Independent exact architectural-contact preflight and full15/16 reviews remain pending. The renderer cancellation bug is also fixed: cancelled or missing600p frames cannot mark a batch complete.


## Cycle 15: intended load-bearing interfaces

The expanded audit found a complete seven-family batch in source `3918b4e…`: stock cases lacked shelf bearing; the OCRU title plaque lacked standoffs; the recovery slip hovered over the tailored cover; four fascia and two access fasteners lacked captive bearings; an orange latch and two independent wear marks lacked their intended substrate; gauge text and pivot lacked proper seating/spindle. Cycle 15 was cancelled at 19/24 real images and is unscored. The renderer correctly exited 1 and left the batch incomplete.

Corrected source `39007192eef36f87c5299933e3a2a4f3462791871144c349a580ba2d9d322487` supplies two closed pressed-U feet per stock case with explicit downward contacts, plaque returns, a pressed chart holder, captive mechanical bearings, latch returns, seated wear/printing and a gauge spindle. Original object dimensions and equipment layout remain unchanged. Hot/cold numerical checks pass; independent measured-repair preflight and full current reviews remain pending. No failed or interrupted source establishes final stability.


## Final full cycles 16 and 17

The seven-family bounded repair preflight passes. Fresh full cycle 16 independent review passes at 91.1/100; unchanged-source full cold cycle 17 passes at 91.7/100. All category minima and 24 camera gates pass, with zero critical findings. All 24 decoded RGB images and camera matrices match exactly between the final pair. Both technical critics confirm current contacts/UV/printing/winding/dependencies and retain explicit sampling/internal-part/mechanism limits. Actual extracted source ZIP verification resolves all 25 libraries internally and loads all 124 file images without saving the source. Final checker evidence includes inherited active UV consumers in a disposable existing-renderer copy; authoritative source and beauty recipe remain unchanged.

Owner approval, promotion and engine/runtime validation are separate. Historical failures and interrupted batches remain intact; no failed comparison result was converted to a pass.
