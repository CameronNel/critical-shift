# F13 preflight attempt journal

This journal records two superseded attempts whose files were deleted during cleanup. Their exact source and raw output files are no longer recoverable. This is a provenance record, not reconstructed evidence. The successful bounded surface probe remains in `f13-luna-preflight/`.

## Initial in-memory repair probe

The temporary `contact_probe.py` opened the frozen `module_overhaul_R1.blend` read-only, then invoked `repair_sixth_review()` in memory. It subsequently failed while looking up the physical notice as a standalone object. The frozen f12 native had already consolidated it into `CD | Joined Checkin Counter Hatch / ivory`, so `S.objects['CD | Worker reassurance glass notice']` raised `KeyError`; that failure invalidated this probe’s post-repair measurements. No scene save was requested. The probe caught the exception and wrote `contact_measurements.json`, which recorded the failure. I later deleted both files; neither should be treated as evidence.

Command used:

```sh
/workspace/tools/blender-5.2.2-linux-x64/blender --background --disable-autoexec --threads 1 --python-exit-code 1 --python critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/probes/f13-luna-preflight/contact_probe.py -- critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/probes/f13-luna-preflight/contact_measurements.json
```

## Interrupted copied-builder attempt

I created a temporary copy named `disposable_overhaul_dock.py`, patched its native output path to `f13-luna-preflight/disposable-f13.blend`, and patched both build-state writes to `f13-luna-preflight/disposable-build-state.json`. I started it with `--stage full --revision f13_luna_preflight`, then stopped it at the primary author’s instruction before it reached a save. The captured `build.log` showed it opening canonical `module.blend` and emitting a `Material.use_nodes` deprecation warning; it contained no save-completion line. Ctrl-C did not stop the child process, so I sent SIGTERM to Blender PID 61969 and its shell PID 61965. The Blender process then exited. No disposable native or disposable build-state output existed. The copied script and partial log were subsequently deleted; their exact files are not recoverable. This attempt did not produce an f13 candidate and is not evidence.

Command used:

```sh
/workspace/tools/blender-5.2.2-linux-x64/blender --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/probes/f13-luna-preflight/disposable_overhaul_dock.py -- --stage full --revision f13_luna_preflight
```

The shell redirected stdout/stderr to the deleted `f13-luna-preflight/build.log` and tailed it after process completion.

## Canonical-file evidence

At final inspection, the frozen native still hashed to `73b85e9a84b577d2059a07371abd366666536800eb45c9e56a7d7788a21b77a3`. `revamp/production/build-state.json` hashed to `7fcae227cc7fb9bb620753a2b75a44cdb32ffd08379341cdac6bbe8b7aaaf7da` and was absent from `git status --short`. The copied builder’s only native and state output destinations were redirected to the preflight directory; neither output was created. No Blender process from either attempt remained. The successful independent surface probe also confirmed the frozen native hash before and after its read-only process.
