# Electrical Room

Original editable Blender source and metric architecture for Critical Shift's turbine-to-distribution section. **Paused incomplete at the user's wind-down request.** Current acceptance status is in `production/TASK_STATE.md`; exact resumption instructions are in `CONTINUE.md`. Only the validation slice is built. The full-room design and final ten-camera package remain unfinished.

The entry threshold is (0,0,0), +Y into the hall, +Z up. See `architecture/floorplan.svg`, `architecture/architecture.md`, and `interface.json`. Neighbor placement is explicitly unbound. The section does not implement engine gameplay, navigation or multiplayer logic.

## Reproduction tools

The Windows workstation uses Blender5.2 and a private section-local `.blender-user` directory. All GPU renders must use the shared `C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py`. `blender/run.ps1` wraps the factory-empty source build and gated rendering. `blender/validate_scene.py` independently measures the saved evaluated geometry. `blender/compare_renders.py` compares camera settings and actual decoded PNG pixels.

Current validation slice example, from the repository directory:

```powershell
& './sections/electrical-room/blender/run.ps1' -Mode slice -Revision S05 -Samples 24 -Width 1200 -Height 750
```

Factory build without rendering:

```powershell
$env:BLENDER_USER_RESOURCES=Join-Path (Get-Location) 'sections/electrical-room/.blender-user'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python-exit-code 2 --python './sections/electrical-room/blender/build_room.py' -- --stage slice --revision S05
```

Blender source is factory-empty and requires no imported geometry or external image/font files. Archived source bytes and exact camera/settings manifests are retained per meaningful revision. All surfaces, props, labels, materials and room construction are authored by the section scripts. Python/Pillow is needed only for the external PNG comparison tool; Blender builds and renders have no Python-package installation dependency.

`production/technical-notes.md` explains what the objective validator proves and what it cannot prove. Independent reviews remain the visual authority; source counts and technical passes do not establish art acceptance.
