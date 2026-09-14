# Mine exterior camera-match task: actual status

## Completed

- Created an isolated task branch `art/mine-exterior-camera-match-20260914` from main commit `a82c7d9b80456153a0c65ca4897044a7f62c7d1c`.
- Opened the actual full-map R17 material-preview scene, not a standalone mine or reconstructed layout.
- Confirmed 55,390 objects, 24 linked libraries without missing libraries, and 105 image datablocks in the native survey.
- Rendered three native full-scene camera captures with Blender 5.2.1 / Cycles CPU: `MINE_APPROACH`, `MINE_OBLIQUE`, `MINE_CONTEXT`, all at 1280x720.
- Recorded transforms, lens, sensor, shifts, clipping, aspect, image hashes and original scene hash. The source scene was never saved and its SHA256 remained unchanged. This is an offline capture, not a claim about EEVEE fidelity, Unity, gameplay or FPS.
- Selected `MINE_CONTEXT` as the wide primary reference-source frame. Lower views remain as evidence of the opaque foreground structure. Cameras are to be reused exactly for future comparisons.

Native successful capture run: https://github.com/CameronNel/critical-shift/actions/runs/34891131895
Capture artifact: `actual-mine-camera-baseline-cpu`, ID 10367026638, SHA256 `0ab98b125dbfe9a19405881c2c9328a600ce4875dfded15147a7ed33037aa321`. It includes the original PNGs, camera manifest, native survey and logs. Artifact retention is seven days. The script and camera metadata are retained here to reproduce the captures after expiry.

## Failed reference-generation gate

Several ChatGPT image-generation attempts returned unrelated mine comparison boards instead of editing the supplied real screenshot. Their architecture and framing do not match the actual source. Some images contained fabricated 'Blender before/after', 'independent review', scores and 'PASS' labels. **Those labels are generated illustration text, not actual operations or review results. Every such board is rejected.** They are not repository assets, authorized reference targets, Blender evidence or accepted art.

Rejected generation IDs from this corrective attempt:
- `8751b16f-05d1-4545-8d89-3bd18e07f770`
- `c1cb3c92-1900-483d-aa1f-1f5b4a04c5c3`
- `ee0fca4b-6d60-4d74-8b5c-46da4842a165`
- `0c38ca49-af15-423d-a49e-950faf47acf6`

The earlier imaginary 'Gullet Mine' concepts are also excluded. No generated reference has passed same-camera validation. Do not quietly substitute a different entrance, architectural layout or viewing angle to proceed.

## Not completed

- Valid same-camera generated reference: NOT COMPLETED.
- Mine-exterior geometry/material edit: NOT STARTED.
- Build/render/repair iteration loop: NOT STARTED.
- Independent visual critic: NOT RUN; no separate reviewer available in the current tool session.
- Nine-category 92+ acceptance: NOT ACHIEVED. All candidate-art scores remain unassigned.
- Native after-edit regression check: not applicable because no Blender asset was edited.

The original map, module libraries, packed textures, posters and source assets are unchanged. Main has not been edited. The one-off capture workflow was retired after successful capture; no ongoing job remains. Capture reproduction can use the script from the repository with the selectively hydrated current preview and its linked dependencies. The runnable workflow is preserved historically at capture commit `f8e9f1ecfcd3faf9bc19669fb36e9dda331cbe71`.

## Required next gate

Produce a SINGLE aligned style paint-over of the real `MINE_CONTEXT.png`, preserving the actual canopy, panel wings, foreground approach structure, rock silhouette and neighbouring buildings. No comparison-board labels, fabricated scores or 'after' renders. Check its perspective and silhouette overlay against the original before using it as a target. Only then edit the authoring R17 on this task branch and render the fixed cameras for the strict nine-category review in `REVIEW_CONTRACT.md`.
