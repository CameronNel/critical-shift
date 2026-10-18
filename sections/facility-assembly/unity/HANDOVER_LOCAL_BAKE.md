# Handover: the final map bake for Unity URP on the owner's PC

**What this is:** the prompt for the agent on the owner's Windows PC (Gemini). Written 2026-10-18 after an independent review of every bake script, the fixes, and a full rehearsal of all 13 map pieces in the cloud (CPU, 256 px; results in `README.md`, *Review and fixes, 2026-10-18*). Paste everything below the line.

**Why a new run:** every bake made before 2026-10-18 is wrong in ways the review found (lost emission strips and screens, opaque decals and frosted glass, clipped lamps, failures that looked like passes) and the first 8 map rooms also held the whole map. None of those outputs are kept; the pipeline that bakes now stops by itself on any of those faults.

---

You are on the owner's Windows PC:
- Ryzen 7 5800X, 32 GB RAM;
- AMD Radeon RX 9070 XT, 16 GB;
- Blender 5.2.2 LTS, portable, at `C:\Blender\blender-5.2.2-windows-x64\blender.exe`.

**Goal:** bake the Critical Shift map for Unity URP with Blender, on the GPU, once. Nothing else.

**Hard rules. Breaking any of them means stop.**

1. **Device: GPU only.** Always pass `-Device GPU`. Never pass `-Device CPU`, never set `CS_BLENDER_DEVICE`, never edit a script to change the device. If the GPU is not found, stop and report. Do not fall back.
2. **No git writes** except the `git fetch` and `git switch --detach` in step 1. No `add`, `commit`, `push`, `reset`, `clean`, `stash`, `rebase`, `merge`; do not delete branches. Do not edit any tracked file. Bake outputs stay local and uncommitted (they are git-ignored).
3. **No broad LFS downloads.** Never run a plain `git lfs pull` or `git lfs fetch --all`. Fetch only what step 3 lists.
4. **Install nothing.** Do not change Windows settings, power plans or drivers; ask the owner.
5. **Any error not covered below:** stop, then report the exact command, the last 60 lines of output or of the room's log, and what you think caused it. Do not change scripts, settings or atlas sizes, and do not resume, until the owner says so.

## Step 0: Where things are

Work in the owner's existing clone, the folder you used for the earlier bakes (the one holding `sections/facility-assembly/unity/bake_all.ps1`). Make sure no Blender is running:

```powershell
Get-Process blender -ErrorAction SilentlyContinue | Select-Object Id, Path
```

If one is listed, stop and ask the owner before closing it (an earlier bake may still be running). The blender-mcp processes are not Blender; leave them.

## Step 1: Update to the reviewed scripts

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"           # keep this set in this shell for every git command below
git fetch origin ccr-b12a99c0-hbdwp2
git switch --detach origin/ccr-b12a99c0-hbdwp2
git log -1 --oneline                      # must be COMMIT_PLACEHOLDER or newer
git status --porcelain                    # must print nothing
```

- If the owner says PR #110 has been merged, use `main` instead: `git fetch origin main` and `git switch --detach origin/main`.
- If the switch fails, or `git status --porcelain` prints anything, stop and show it. Do not stash, reset or clean.

Check these files exist: `sections/facility-assembly/unity/bake_all.ps1`, `bake_room.ps1`, `bake_room.py`, `bake_check.py`, `check_device.py`, and `sections/facility-assembly/blender_device.py`.

## Step 2: Move every older bake out of the way (keep it; do not delete)

```powershell
$old = "..\map-bake-before-2026-10-18"
New-Item -ItemType Directory -Force $old | Out-Null
Get-ChildItem sections/facility-assembly/unity/map -Directory -ErrorAction SilentlyContinue | Move-Item -Destination $old
Get-ChildItem sections/facility-assembly/unity/map                 # must list only map_placement.json
```

If `Move-Item` reports that a folder already exists in `$old`, use `..\map-bake-before-2026-10-18b` instead and run it again. If the last command lists anything but `map_placement.json`, stop and report. The owner deletes the old folders later.

## Step 3: Fetch the files the bake reads, from LFS

The map file, the room files it links, and **the turbine's 23 texture PNGs** (they are separate files, not packed in its .blend; without them the turbine would bake magenta and the run now stops in prep):

```powershell
$files = @(
  "sections/facility-assembly/combined/combined_map.blend",
  "sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend",
  "sections/facility-assembly/sources/waste-storage/module_aaa_A1.blend",
  "sections/facility-assembly/sources/turbine-room/rebuild/turbine_room_v2_geo.blend",
  "sections/facility-assembly/sources/turbine-room/rebuild/*.png",
  "sections/facility-assembly/sources/fuel-corridor/module_short_S1.blend",
  "sections/facility-assembly/sources/electrical-room/overhaul/checkpoints/full-R11.blend",
  "sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend",
  "sections/facility-assembly/sources/medical-reanimation/module_overhaul_R2.blend",
  "sections/facility-assembly/sources/refinery/module_overhaul_R1.blend",
  "sections/facility-assembly/sources/front-end-area/front_end_area_cafeteria_revamp.blend",
  "sections/facility-assembly/sources/spawn-room/module.blend",
  "sections/facility-assembly/sources/spawn-room/hero_suit.blend",
  "sections/reactor-room/blender/reactorroom.blend",
  "sections/facility-assembly/sources/mine-r39/module_r39_aaa.blend",
  "sections/facility-assembly/sources/condenser-bay/module_aaa_A1.blend",
  "sections/facility-assembly/exteriors/refinery/exterior-R01.blend",
  "sections/facility-assembly/exteriors/medical-reanimation/exterior-R04.blend",
  "sections/facility-assembly/exteriors/spawn-room/exterior-R05.blend"
)
foreach ($f in $files) { git lfs pull --include="$f" --exclude=""; if ($LASTEXITCODE -ne 0) { throw "lfs pull failed: $f" } }
Get-ChildItem ($files | ForEach-Object { $_ -replace '/', '\' }) | Where-Object { $_.Length -lt 100KB } | Select-Object FullName, Length
```

The last command must print **nothing**: every file is larger than 100 KB (an LFS pointer is about 130 bytes). If any file is listed after a second pull, stop and report; it may be the LFS quota. Also count the turbine textures:

```powershell
(Get-ChildItem sections/facility-assembly/sources/turbine-room/rebuild/*.png).Count     # must be 23
```

## Step 4: GPU check (renders nothing)

```powershell
& "C:\Blender\blender-5.2.2-windows-x64\blender.exe" -b --factory-startup --python-exit-code 1 --python sections/facility-assembly/unity/check_device.py -- --device GPU
```

The output must contain `BLENDER VERSION 5.2.2 LTS` and `BLENDER DEVICE GPU (owner choice): HIP [...]`. If it says no GPU backend was found, stop and report (likely an out-of-date Adrenalin driver). Do not try CPU.

## Step 5: GPU smoke test (about 15 minutes)

One small room through every stage at rehearsal quality, on the GPU, into a separate folder. It proves the GPU path (HIP, float images, the new mask and check stages) before the long run:

```powershell
& powershell -NoProfile -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_all.ps1 -Device GPU -Map -Quality rehearsal -Only cooling-plant `
    -Blender "C:\Blender\blender-5.2.2-windows-x64\blender.exe" -OutRoot sections/facility-assembly/unity/_smoke -LogDir sections/facility-assembly/unity/_smoke/logs
```

It must end with `==== all 1 rooms done`, and `sections/facility-assembly/unity/_smoke/logs/map-cooling-plant.log` must contain `BLENDER DEVICE GPU (owner choice): HIP` and `CHECK cooling-plant OK`. Report the minutes per stage (the lines after each `== cooling-plant : <stage>`). If it fails, stop and report; do not start step 6.

## Step 6: The bake (several hours; run once)

Start it in its own window, so it is not tied to your command timeout:

```powershell
Start-Process powershell -WorkingDirectory (Get-Location) -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','sections/facility-assembly/unity/bake_all.ps1','-Device','GPU','-Map','-Blender','C:\Blender\blender-5.2.2-windows-x64\blender.exe'
```

**What it does:** 13 pieces, one after another, smallest first: cooling-plant, waste-storage, turbine-room, fuel-corridor, electrical-room, compliance-dock, medical-reanimation, refinery, front-end-area, spawn-room, reactor-room, mine, then map-connections. The condenser bay is left out on purpose (its finish is being reworked).

**Each piece runs these stages:** prep, base, rough, normal, metal, emit, mask, finish, check, compare.
- **prep** (unwrap, CPU-bound) is the longest stage; in the cloud rehearsal it took TIMING_PLACEHOLDER.
- **check** stops the run if the piece's output is wrong (anything outside the room in the bake, missing or invalid maps, lights, or an FBX that does not re-import with the same meshes and triangles).
- Logs: `sections/facility-assembly/unity/_logs/map-<piece>.log`. Outputs: `sections/facility-assembly/unity/map/<piece>/`.

Watch the first piece until its `base` stage has started and confirm the log shows `BLENDER DEVICE GPU (owner choice): HIP`. Then tell the owner it is running. These lines are expected and not errors: `Cannot find lib '...facility_environment.blend'`, `Unrecognized file format`, `lib.override.resync | ERROR Linked id ...`.

**If it stops:** `bake_all.ps1` names the piece and its log, and prints the exact command to resume (it keeps `-Map`). **Do not resume yourself.** Report the piece, the stage, the last 60 lines of its log, and the resume command, and wait for the owner. In particular:
- out of GPU memory (`System is out of GPU memory`, `hipErrorOutOfMemory`) or a driver timeout: report; do not lower settings;
- `CHECK FAIL ...` lines: report them all;
- `images have no pixels`: an LFS file is still a pointer; report the file names.

## Step 7: Report back to the owner

1. `git log -1 --oneline`, the first line of `blender.exe --version`, and the GPU line from step 4.
2. Which pieces finished and which did not; for each finished piece, the minutes per stage from its log and the `ok` line of `map/<piece>/bake_check.json`.
3. The total size of `sections/facility-assembly/unity/map/`.
4. The comparison images: `map/<piece>/compare/source/*.png` and `compare/baked/*.png`. Name any pair that looks clearly different (black, pink, missing parts).
5. `git status --porcelain` must print nothing (the outputs are git-ignored). **Do not commit them.**

**Known limits** (not for you to fix; tell the owner if asked):
- The turbine's blue rim glow (view-dependent shading) cannot be baked; it needs a small custom Unity shader later.
- Glass in the source renders casts dark shadows (Cycles does not trace light through glass by default); the baked side and Unity do not.
- Nothing has been imported into Unity yet: that is *Critical Shift > Rooms > Import Baked Map* in the Unity project, after this run.
