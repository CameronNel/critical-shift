# Fixed-camera builder review

These are builder self-reviews, not independent critics or user acceptance. No delegated agent was used. Original failed images remain in `renders/review/` so the corrections can be checked.

## Initial composition — room-baseline

Three test cameras, before formal full review. FAIL. The first open door hid the locker composition; the briefing rows aligned into two silhouettes; the values washed together. Corrected the door opening, staggered chairs, reduced practical output, and darkened navigation plates. The waiting bench was recessed to preserve the gathering corridor. Plates 00–03, 08, 11, 13, 24.

## Full cycle 1 — room-01

All eleven cameras rendered and individually reviewed. FAIL, despite 40/40 registered assembly contacts passing.

Three worst visible problems:
1. Hall navigation depended on signs; adjacent room functions were invisible. Add internal observation glazing. Plates 00, 01, 17.
2. Door sheets had false horizontal seams and open leaves intersected shared walls. Rebuild a continuous aperture sheet and give hinges the necessary setback. Plates 08, 20.
3. Chamber glazing obscured its controller, while reverse views exposed unfinished shared-wall backs and an overlapping recess ceiling. Move controller forward, use clear safety glass, and correct architecture. Plates 06, 09, 10, 22.

Additional audit findings: F sat at the chamber envelope and cropped out the material context; Walk B aimed into the machine instead of along the circulation edge; D was too narrow to judge the reverse route. Their invalid baseline renders are retained. F was moved to open floor, Walk B keeps its position and looks along the aisle, D keeps its transform and widens from 23 to 16 mm. These exceptions are explicit; all other transforms remain unchanged. All eleven cameras are frozen from room-02 onward.

Visual scores (scale, shape, materials, light, colour, story, density, signs, PPE, game read): 8.5, 7.5, 7, 8, 8, 6.5, 8.5, 9, 7.5, 7. Average **7.75/10**. Weighted rubric **78/100**. Blocking issues include support appearance and incomplete route evidence. No completion claim.

## Full cycle 2 — room-02

All eleven views reviewed. FAIL. Objective validation correctly rejects the 1.133 m north machine clearance. The coverage check also misclassified two architectural wall assemblies as benches; corrected its asset filter rather than adding false dressing tags.

Three worst problems: projecting chamber leaves narrow the aisle; open room leaf overlaps the observation window; shared wall backs and locker ceiling have unfinished areas. Changed the chamber to inward hinged leaves, rebuilt the room door, finished inner wall surfaces and sealed the ceiling. Individual boot support catches a 14.5 mm shelf gap that the bay-root anchors did not catch. Added purposeful bay variation and the locker clipboard. Plates 03–06, 09, 13, 15, 23. Weighted rubric **82/100**; visual average **8.0/10**. Clearance and contact appearance block acceptance.

## Full cycle 3 — room-03

All eleven views reviewed. 54 registered contacts PASS; objective layout PASS. Both side aisles 1.203 m, rear clearance 1.295 m; hall 3.296 m. All chairs, sideboard and bench feet meet the floor. Inner walls, machine rear access and clear glass read consistently in reverse views.

Three remaining weaknesses: the hinged personnel leaf covers the observation pane; the nearer suit silhouette clips behind the doorway in camera C; the visor still reads as a flat thick insert. Next pass uses a real wall pocket and tracked door, places the near bays deeper, and curves/thins the visor. Navigation gains two pictograms within the existing sign family. Chamber states gain separate words, door positions and emission changes. Plates 00, 03–06, 08, 10, 12, 22, 24. Weighted rubric **86/100**, visual average **8.2/10**. Not accepted.

## Full cycle 4 — room-04

All eleven views reviewed. 54 contact checks PASS. Pocket door, clearer glass, thinner curved visor and pictograms are improvements. The source has six readable machine states, but the objective report falsely expanded the machine envelope using inactive font bounds. The validator now measures active physical mesh/curve surfaces and checks the state words separately; no clearance threshold was lowered.

Three remaining refinements: the pocket leaf still needs its last 100 mm of travel for the entry composition; the near bays need another 300 mm of depth to reveal the full silhouette past the jamb; the floor and centre light keep the locker foreground too pale. Correct these, add a modest return-air grille, and add small handle-contact wear. The practical fixture positions and all cameras remain fixed; centre locker output is reduced by 45% as an explicit lighting correction. Plates 03, 05, 09–11, 15, 20, 23. Weighted rubric **88/100**, visual average **8.35/10**. Not accepted; final stability/cold-start still required.

## Full cycle 5 — room-05

All eleven views rendered and individually reviewed. **59/59 contacts and 28/28 objective checks PASS**. Two stations on each side are discernible from C; the central machine is open and its control is physically mounted. Four seats and the display remain readable from E, with their fronts and foot contacts exposed in Walk C. The reverse hall retains its portrait/bench cluster and clear route. The floor is less reflective, the locker centre is quieter, and material context F distinguishes fabric, rubber, painted sheet, plaster and glazing. Six state readouts/door poses pass source checks.

No new visual veto identified in this pass. The three previously worst issues—door travel, clipped near station, pale foreground—are improved from the same cameras. Remaining finish work is a flush pocket pull inside its cavity, then a fresh identical-settings stability build and saved-source cold start. No layout/material/light change is planned for the stability pass.

Builder visual scores: scale 9, shape 8.5, materials 8.5, lighting 8.5, colour 9, storytelling 8.5, density 9, signage 9, PPE 8.5, commercial game read 8.5. Average **8.7/10**. Weighted art/layout subtotal **81.5/90** (18/20 layout, 18/20 art, 14/15 hero, 13.5/15 materials, 9/10 lighting, 9/10 dressing). Technical completion points remain provisional until cold start. These are builder judgments, not external acceptance.

## Full cycle 6 — room-06 stability rebuild

A fresh factory-scene build completed with 59/59 support and 28/28 objective checks passing. All eleven camera manifests match room-05 exactly. Ten decoded PNGs are pixel-identical; Spawn differs by only 0.0000245 of an 8-bit value on average after the pocket pull became flush. The full contact sheet was reviewed against room-05's individually inspected images. No material, lighting or composition regression is visible; visual scores remain **8.7/10**. The final two cycles are materially stable.

The only source finish was recessing the sliding door pull into its wall pocket clearance. No new room geometry, material or lighting changes were introduced. A source inventory was added for the engine handoff. Cold start now reopens the saved blend and independently checks the outer briefing aisles as well as the existing geometry/state tests.

## Cold-start final verification

The room-06 Blender process exited. A separate Blender 5.2.0 LTS process opened the saved spawnroom.blend without rebuilding it, reran the source and contact audits, and rendered all eleven mandatory cameras. The process finished with COLD_START_PASS and exit code 0. All eleven decoded PNGs are exactly pixel-identical to room-06; camera manifests also match. See cold_start_comparison.json.

All 59 contacts and 29 objective checks pass, including the newly measured 1.247 m route behind briefing seats and 1.437 m north route. Two supplemental human-use views and five non-idle chamber states were individually inspected: mounted crew portrait, clipboard/bench contact, fabric/rubber separation, readable state words, closed/open seal doors and appropriate indicator lights are visible. These supplemental views do not replace mandatory cameras or change the saved source. No new veto was found.

Final weighted score: 91.5/100, including 10/10 reproducibility; full visual category mean 8.7/10. Earlier 8.75 arithmetic was corrected from the unchanged category scores, not through a rescoring. Review remains builder self-assessment. Engine interaction, sound playback, collision, rigging, LODs and export optimization remain handoff work.
