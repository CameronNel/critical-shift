# Grounded Spawn rebuild evidence

This rebuild starts from `origin/main` **8603063**, following the art-direction reset in **7b99369**. A final fetch confirmed main remains at 8603063. It lives on `codex/spawn-reference-rebuild` in an isolated worktree; prior local work and rejected blends were preserved, and no existing blend was loaded as modeling input.

## Source and provenance

- `../blender/spawnroom.blend`: authoritative editable room.
- `../blender/spawnroom_style_slice.blend`: editable small kit scene.
- `checkpoints/approved-style-slice.blend`: the original 8.5/10 slice checkpoint, saved before expansion.
- `../blender/README.md`: reproducible commands, source organization and engine handoff.
- `../assets/portraits/SOURCES.md`: original image generation provenance.
- `REFERENCE_REVIEW.md`: all 28 numbered plates and extracted rules reviewed before modeling.

All meshes and material graphs are authored locally. Two fictional institutional portraits were generated with OpenAI's built-in image tool, then mapped to matte paper and packed. No online models, downloaded texture sets, HDRIs, commercial-game assets or third-party art were incorporated. There are therefore no external asset URLs or attribution licenses to list. Blender's bundled font is used.

## Review trail

- `renders/review/slice-grey/`: primary form rejection and correction baseline.
- `renders/review/slice-01/` through `slice-03/`: three material/construction slice iterations.
- `critics/slice-review.md`: slice scores and defects.
- `renders/review/room-baseline/`: first three-camera room test.
- `renders/review/room-01/` onward: eleven-camera full correction cycles, retained including failures.
- `critics/full-room-review.md`: same-camera findings, explicit camera exceptions and builder scores.
- Each full cycle retains camera transforms and contact JSON; later cycles also retain objective measurements.

The reviews are builder self-assessments. They do not imply independent critic or user approval. Render success and object counts do not determine visual scores.

## Objective evidence and limits

The current source has four PPE stations, four briefing seats, one central integrity machine, one modest exit radiation instrument and four spawn locations. The source audit measures 1.203 m side aisles, 1.295 m behind the machine and 3.296 m in the gathering hall. The outer briefing routes are 1.247 m behind the seats and 1.437 m north of them. All 36 furniture feet are checked from actual mesh bounds. The expanded contact audit checks 59 registered props and their exact supports.

Six machine preview states use words and mechanical changes as well as lights. Audio/interaction positions are engine handoff markers. Runtime gameplay, networking, collisions, rigging, LODs, sound playback and optimized exports are not implemented by this Blender art delivery.

Final status: PASS. Weighted rubric 91.5/100; visual mean 8.7/10, builder self-review. The original slice mean is 8.45/10 (8.5 rounded); final kit regression is 8.55/10. All eleven saved-source cold-start images are pixel-identical to room-06. See TASK_STATE.md, RUBRIC.md, stability_comparison.json and cold_start_comparison.json. The final gallery and audit reports are in renders/final/; CONTACT_SHEET.png summarizes the eleven mandatory views. Five STATE images and two DETAIL images supplement them. All formal review and failure evidence remains in renders/review/.
