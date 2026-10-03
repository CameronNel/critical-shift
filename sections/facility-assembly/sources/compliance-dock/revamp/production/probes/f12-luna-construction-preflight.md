# f12 Luna construction preflight

**Status: one confirmed construction blocker found.** This is a read-only technical diagnosis, not a visual review, acceptance score, or 99/100 determination.

I read the frozen f12 construction sources against the byte-exact f11 native (`cf5b4c12…57d035`) and measured the saved failed f12 native only inside a disposable Blender 5.2.2 process. I did not save any scene. The four frozen source hashes are recorded in the paired JSON report.

The cargo ribs have a real piecewise-shear defect. The rib cross-section has Z offsets `-0.66`, `+0.61`, and `+0.66` m around a 1.45 m centre. Its long side edge runs from about Z=0.79 to 2.06 m, crossing the intended shoulder break at Z=1.98 m without an authored vertex there. The repair moves only existing vertices using a clamped shift, so Blender linearly interpolates a false inward/outward shear through the lower vertical wall. Direct BVH rays at Y=6.8 m show the east rib buried 19.6 mm into the shield at Z=1.98 m, aligned within 0.025 mm at Z=2.01 m, then exposed by 13.2 mm at Z=2.03 m. The west side mirrors this result. The upper captive screw follows the intended formula, so its position does not prove continuous rib contact. Add a real profile edge at the break (or split lower and drafted upper sections), then remeasure all eight ribs and their upper screws against the corrected body.

The new queue sheets leave a small support gap above the preceding forms. The repositioned fourth form ends at Z=1.065 m. The first new 0.45 mm sheet is centred at Z=1.0655 m, so its lower face is at Z=1.065275 m: a 0.275 mm gap. The later new sheets touch because their pitch equals their thickness. Starting the first queue sheet at a 1.065 m lower face (centre Z=1.065225 m) closes the gap. The current interface guard does not check this paper contact or the title and top-page clearance.

The f11 state used 381,032 evaluated triangles, leaving 68,968 against the 450,000 planning limit. It already used all 1,150 material submeshes and all 36 local families. The f12 recipe appears to reuse those material families and consolidate same-parent cosmetic meshes, so the budget is not proven to fail; final saved-native counters must be checked because neither exact ceiling has slack.

The current corrected code has specific geometry guards for G1 cassettes/fixings, cargo cover rebate floors, and the new P2/D1/D2 jamb-foot witnesses. The f11 native confirms the D1 jamb feet span Z=0 to 2.2 m. The trolley tarp in f11 has both `CD_Physical_1m` and `CD_Fabric_Cut_1m`; the current textile pass charts the new small cloth meshes before material use. I found no further definite defect in those recipes from this preflight. However, the fifth-review guard does not cover the cargo lifting-eye/collar seats, G1 pedestal load transfer, or the manuscript sheet’s support on the counter; measure those interfaces on the rebuilt native.

This review did not inspect final f12 pixels, assign scores, or validate runtime behavior. The corrected canonical retry exited before saving, so this document cannot establish full-scene acceptance. Blender reader processes have exited and the saved f11 native remains byte-exact.

Raw probe evidence is in `production/probes/f12-luna-preflight/`.
