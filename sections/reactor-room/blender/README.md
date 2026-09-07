# Reactor Blender source

`build_scene.py` authors the complete P02 reactor hall from an empty factory scene. The editable output is `reactor_scene.blend`. No earlier 3D assets are opened, appended or imported during a normal build. Procedural surface maps are generated from the source and packed into the scene.

The hall is metric, X east / Y north / Z up. The centered pool, two independent drive banks, east-wall-centered control room at +10 m and compact four-flight stair follow `../architecture/output/reactor_compact_stair_architectural_set.pdf`. Approved A02/B01 images set the material and rendering direction; their superseded stair layout is not used.

Use Blender 5.2 LTS. The recorded machine uses Cycles HIP on an AMD RX 9070 XT. `build-scene.ps1` is a convenience launcher where PowerShell script execution is already allowed. No execution-policy change is required; the direct command is:

```powershell
$env:BLENDER_USER_RESOURCES = 'C:/path/to/reactor-room/production/private-blender-profile'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --disable-autoexec --threads 6 --python-exit-code 1 --python 'C:/path/to/reactor-room/blender/build_scene.py' -- --revision art-09a --render all --samples 80 --width 1440
```

Use `--render none` for geometry and validation only, a comma-separated list of camera names for a targeted preview, or `--render diagnostics` for the plan, control-interior and pool-depth diagnostics. Each revision writes its exact authoring source and a measured validation manifest. Ten camera subjects are documented in `../production/CAMERAS.md`.

To verify a saved scene, replace `--factory-startup` with the absolute `.blend` path and append `--cold-start` after the script arguments. Use a new revision/output label for reproduction so accepted images remain unchanged. A successful reopen is distinct from reproducing all ten images.

During parallel local facility work, wrap GPU Blender commands with `C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py --owner reactor --` using the bundled Python runtime. It serializes this run's GPU jobs and releases its lock on process exit. CPU geometry audits may run independently.

Authoritative completion status and independent reports are in `../production/TASK_STATE.md` and `../production/critics/`. A renderable file or passing dimension checks do not constitute art acceptance or engine integration.
