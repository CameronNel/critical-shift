# Cooling Plant Blender artifact

Open `cooling_plant.blend` in Blender 5.2. The saved R10 file contains the complete room, ten fixed cameras and eight supplementary cameras. Scene units are metres. Local entry is CP-P01 at (0,0,0), +Y inward, +Z up. The proposed reactor transform is documented in ../interface.json and is not applied.

The factory-empty build is reproducible from build_scene.py, kit.py and develop_room.py. Their concatenated byte hash is recorded in the scene and build manifest. Explicitly use the full stage; the older slice option remains only for historical reproduction.

From the repository root in PowerShell:

```powershell
& sections/cooling-plant/blender/run.ps1 -Action build -Stage full -Revision R10
& sections/cooling-plant/blender/run.ps1 -Action render -Revision R10 -Cameras all -Samples 48 -Width 1440
```

The build replaces this section's authored artifact, so preserve user changes/checkpoints before rebuilding. Render commands use the shared facility GPU gate and section-private user resources. The wrapper's gate/Python/Blender paths reflect this production workstation; adjust those installation paths when transferring to another machine. Never bypass the shared gate on this workstation.

`validate.py` and `walk_audit.py` inspect the saved file in fresh background processes. They do not certify game-engine physics. `inspect_open_scene.py` only prepares this exact file's own interactive viewport and never saves it. The live MCP lease was released after inspection.

All assigned materials are procedural; native Blender text requires no external font download. The MCP dependency audit incorrectly treats the built-in font sentinel as a literal path; its raw finding is retained. See ../production/FINAL_HANDOFF.md for scores, measured contracts, numerical cold-render differences and remaining assembly work.
