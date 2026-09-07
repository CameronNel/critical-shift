# Waste Storage

**Paused by user; incomplete.** Start with [CONTINUE.md](CONTINUE.md). The reviewed checkpoint is `blender/waste-storage-checkpoint-r03.blend`; current build source contains unbuilt r04 edits. Style expansion remains gated.

Original Blender environment package for Critical Shift. The section uses a local metric frame: main entry threshold (0,0,0), +Y inward, +Z up. [Architecture](scenery/ARCHITECTURE.md), [floorplan](scenery/floorplan.svg), [interfaces](interface.json) and [connection handoff](scenery/CONNECTIONS.md) define the module. Read [TASK_STATE](production/TASK_STATE.md) for actual acceptance; the existence of this README does not imply completion.

The visual source starts factory empty. No geometry is imported from existing sections or asset services. Source ownership is confined to this section. Approved generated references guide rendering/material quality; their geometry is not reused.

## Build and review

Windows prerequisites: Blender 5.2, bundled Python with Pillow and NumPy, and the shared facility GPU gate. `production/run.ps1` locates the section relative to itself, creates a private ignored `.runtime` directory and explicitly starts Blender with factory settings. It does not use any live Blender session.

From the repository root:

```powershell
& sections/waste-storage/production/run.ps1 -Action build -Stage full -Revision full-r01
& sections/waste-storage/production/run.ps1 -Action validate -Revision full-r01
& sections/waste-storage/production/run.ps1 -Action render -Revision full-r01
```

The `render` action always invokes `C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py --owner waste-storage` before Blender. GPU queue timeout is not authority to stop another worker. `-Blend` and `-Output` select explicit checkpoint and evidence paths. `-Cameras` may select a comma-separated subset for development; full review requires all ten.

Blender source: `blender/build_scene.py`. Final authoritative file: `blender/waste-storage.blend` when TASK_STATE records finalization. Ten cameras and assembly support metadata are exported in `blender/scene_manifest.json`. The validator independently examines evaluated triangles, target contact, route volumes, dimensions, camera transforms, mesh/material consistency and dependencies. Its reports clearly state checks that are outside their scope.

Fixed review defaults: Cycles, 1280 × 800, 64 samples, denoising, seed 4217. The renderer preserves camera transforms, writes untouched PNGs and hashes each image in a batch manifest. QA contact sheets are labeled derivative thumbnails; original frames are the pixel evidence.

```powershell
# Run with the bundled Python executable:
python sections/waste-storage/production/evidence.py sheet <batch-directory>
python sections/waste-storage/production/evidence.py compare <before-batch> <after-batch> --output <comparison.json>
```

## Acceptance evidence

The independent Astra Ultra reviewer writes `production/critics/`. Every relevant category must be ≥90; four complete full-room review cycles and stable final two cycles are mandatory. Actual scores, remaining defects and cold-start results live in TASK_STATE and RUBRIC. Reports never award visual quality for source complexity or claimed effort.

`production/checkpoints/` holds curated source snapshots; temporary Blender backups and runtime caches are excluded. A final cold-start audit must reopen/rebuild using a fresh process, rerun objective validation, render all ten cameras and compare against the prior accepted state.

The [gameplay handoff](scenery/GAMEPLAY_HANDOFF.md) lists simulation, networking, collision/navigation and incident work for engine integration. Blender source completion does not assert that those runtime systems have been implemented.
