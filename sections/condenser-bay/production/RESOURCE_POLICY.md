# User resource policy — 2026-09-12

The user stopped Astra after GPU renders reduced their game to approximately 20 fps, then authorized continuing without consuming all GPU power.

Active implementation: **CPU-only Cycles rendering, two Blender threads, affinity restricted to two logical processors, Windows IDLE priority, CPU OpenImageDenoise**. Run `blender/resource_guard.py` before opening/building a scene. All current wrappers enforce this. Run only one Blender job at a time. Do not use EEVEE, GPU Cycles, GPU denoising, global GPU power changes, or the old archived GPU wrappers unless the user changes this constraint.

The first 768×432, 16-sample test took 49.19 seconds of rendering. The process was verified at IDLE priority with affinity mask 0xc000; its manifest records CYCLES / CPU / two threads / GPU denoising false. Lower sample counts or lower resolution are not GPU usage limits and are not substitutes for this policy.

R27 historical EEVEE warm pack is retained; cold-R27 was interrupted and remains incomplete. `CPU-probe-R27` is a separate preview, not an acceptance pack. R28+ saved artifacts and review manifests explicitly record the new engine. Scores must be based on fresh complete warm/cold CPU evidence; no EEVEE score is silently carried forward. The shared GPU gate is not acquired for CPU jobs, and gpu.lock must not be deleted.

Single-worker mutex rejection was verified with a second lightweight Python guard invocation while Blender ran. The guard fails before a saved scene is opened in current wrappers. No second render process was launched.

User confirmed their game frame rate is back to normal with this CPU-only limit. Retain two logical processors, IDLE priority, one worker and no GPU rendering.

## Superseding user authorization — GPU speed restored
The user explicitly said: 'You may use gpu again. Configure that it run as fast as possible'. Current default is Cycles HIP on AMD Radeon RX 9070 XT, hardware ray tracing enabled, GPU denoising enabled, persistent scene data, normal process priority and all 16 logical processors. Use the shared gpu_gate.py owner astra-condenser-bay; one GPU worker and separate cold reopen. Prior CPU caps remain documented as history and available via ASTRA_RENDER_MODE=CPU for direct CPU-only work; current review wrappers select GPU. Do not change global game/driver settings or delete gpu.lock. Device capability probe: validation/gpu-device-probe.json.
