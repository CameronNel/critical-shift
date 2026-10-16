# Handover: bake every room for Unity URP on the owner's PC

**What this is:** a prompt for the agent on the owner's Windows PC. It was written 2026-10-16 for branch `ccr-b12a99c0-hbdwp2` (PR #108, not merged). Paste everything below the line.

---

You are on the owner's Windows PC:
- Ryzen 7 5800X, 32 GB RAM;
- AMD Radeon RX 9070 XT, 16 GB.

**Goal:** bake the Critical Shift rooms into Unity URP texture sets with Blender, on the GPU. Nothing else.

**Hard rules. Breaking any of them means stop.**

1. **Device: GPU only.** The owner chose GPU.
   - Always pass `-Device GPU`.
   - Never pass `-Device CPU`, never set `CS_BLENDER_DEVICE=CPU`, and never edit a script to change the device.
   - If the GPU is not found, stop and report. Do not fall back.
2. **No git writes.**
   - Do not run `git add`, `commit`, `push`, `reset`, `clean`, `stash`, `rebase` or `merge`, and do not delete branches.
   - Do not edit any tracked file. The bake outputs stay local and uncommitted, because the GitHub LFS quota is small.
3. **No broad LFS downloads.** Never run a plain `git lfs pull` or `git lfs fetch --all`. Fetch only the files listed in step 4.
4. **Do not install anything except what step 2 names.** Do not change Windows settings, power plans or drivers yourself; ask the owner.
5. **Any error not covered below:** stop, then report the exact command, its last 40 lines of output, and what you think caused it. Do not improvise fixes to the scripts.

## Step 1: Repository

Run every command in PowerShell. If the owner has a clone, `cd` to it. Otherwise clone without downloading LFS files:

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone https://github.com/CameronNel/critical-shift.git
cd critical-shift
```

Then, in either case:

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"          # keep this set in this shell for every git command below
git status --porcelain                   # must print nothing (see below)
git fetch origin ccr-b12a99c0-hbdwp2
git switch ccr-b12a99c0-hbdwp2           # creates a local tracking branch if there is none
git pull --ff-only origin ccr-b12a99c0-hbdwp2
git log -1 --oneline
```

**`git status` must print nothing.** If it prints anything, stop and show the owner; do not stash or discard.

**If the `ff-only` pull fails,** stop and report.

**If PR #108 has been merged** (the owner will say so), use `main` instead of `ccr-b12a99c0-hbdwp2` in the commands above.

**Check these files exist:**
- `sections/facility-assembly/unity/bake_all.ps1`
- `sections/facility-assembly/unity/bake_room.ps1`
- `sections/facility-assembly/unity/bake_room.py`
- `sections/facility-assembly/unity/check_device.py`
- `sections/facility-assembly/blender_device.py`

## Step 2: Tools and versions

Check each item, and only install what is missing or wrong.

### Git for Windows 2.40 or newer, with Git LFS

```powershell
git --version
git lfs version
```

If `git lfs` is missing, ask the owner to install Git for Windows from https://git-scm.com/download/win; it includes LFS. Then run `git lfs install` once.

### Blender 5.2.2 LTS, exactly

The room files were saved by 5.2, and the scripts were tested on 5.2.2.
- Do not use 4.x or 5.0 / 5.1.
- Do not use Steam or Microsoft Store builds: they update on their own.
- Do not upgrade past 5.2.2 during the run.

Check:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --version
```

The first line must be `Blender 5.2.2 LTS`.

**If it is missing or a different version,** the installer is https://download.blender.org/release/Blender5.2/blender-5.2.2-windows-x64.msi. Its SHA-256 is:

`8dac2751ebe8e3867327eec52f1ef9b344c0a27499bb6221a301b4b35f2828d1`

Check it with `Get-FileHash <file> -Algorithm SHA256` before running it. The MSI installs to `C:\Program Files\Blender Foundation\Blender 5.2\`, which is the scripts' default path.

**If another 5.2 version is already installed there,** ask the owner before replacing it. The portable alternative leaves an existing install alone:
- Download https://download.blender.org/release/Blender5.2/blender-5.2.2-windows-x64.zip, whose SHA-256 is `3849d17a682cba006075aaa3f3597ecb5c9c30ec31035b2e092c53e40679b535`.
- Extract it to `C:\Blender\blender-5.2.2-windows-x64\`.
- Add `-Blender "C:\Blender\blender-5.2.2-windows-x64\blender.exe"` to every bake command below.

### AMD graphics driver

Blender's HIP backend needs the current **AMD Software: Adrenalin Edition** driver; the HIP runtime comes with it, so no ROCm or HIP SDK is needed.
- The owner updates it from AMD Software, under Home and then Check for Updates.
- Do not install drivers yourself. If it is out of date, ask the owner.

### Disk space

Keep at least 25 GB free on the repository's drive:

```powershell
Get-PSDrive -PSProvider FileSystem
```

### Sleep

Ask the owner to keep the PC awake for the whole run, which may take several hours. Do not change the power settings yourself.

## Step 3: GPU check (renders nothing)

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python sections/facility-assembly/unity/check_device.py -- --device GPU
```

The output must contain both of these lines:

```
BLENDER VERSION 5.2.2 LTS
BLENDER DEVICE GPU (owner choice): HIP [...the GPU name...]
```

**If it says `BLENDER DEVICE GPU was asked for, but Blender found no GPU backend`, stop.** Report it and tell the owner the likely causes: the Adrenalin driver is out of date, or the wrong GPU is selected. Do not try CPU.

## Step 4: Fetch the room files from LFS (about 255 MB)

Run exactly this; each `--include` names one file:

```powershell
$files = @(
  "sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend",
  "sections/facility-assembly/sources/waste-storage/module_aaa_A1.blend",
  "sections/facility-assembly/sources/turbine-room/rebuild/turbine_room_v2_geo.blend",
  "sections/facility-assembly/sources/fuel-corridor/module_short_S1.blend",
  "sections/facility-assembly/sources/electrical-room/overhaul/checkpoints/full-R11.blend",
  "sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend",
  "sections/facility-assembly/sources/medical-reanimation/module_overhaul_R2.blend",
  "sections/facility-assembly/sources/refinery/module_overhaul_R1.blend",
  "sections/facility-assembly/sources/front-end-area/front_end_area_cafeteria_revamp.blend",
  "sections/facility-assembly/sources/spawn-room/module.blend",
  "sections/facility-assembly/sources/spawn-room/hero_suit.blend",
  "sections/reactor-room/blender/reactorroom.blend",
  "sections/facility-assembly/sources/mine-r39/module_r39_aaa.blend"
)
foreach ($f in $files) { git lfs pull --include="$f" --exclude=""; if ($LASTEXITCODE -ne 0) { throw "lfs pull failed: $f" } }
foreach ($f in $files) { "{0,12:n0}  {1}" -f (Get-Item $f).Length, $f }
```

**Every file must be larger than 1 MB.** A file of about 130 bytes is still an LFS pointer. If one stays a pointer after a second try, stop and report; it may be the LFS quota.

**Do not fetch `sections/facility-assembly/blender/facility_environment.blend`.** The medical and dock files mention it, but Blender only warns that it is missing, and the bake does not need it.

## Step 5: Bake

**Rooms:** twelve, smallest first.

| Order | Rooms |
|---|---|
| 1–6 | cooling-plant, waste-storage, turbine-room, fuel-corridor, electrical-room, compliance-dock |
| 7–12 | medical-reanimation, refinery, front-end-area, spawn-room, reactor-room, mine |

**The condenser bay is left out on purpose:** its finish is being reworked.

Start the run in its own window, so it is not tied to your command timeout:

```powershell
Start-Process powershell -WorkingDirectory (Get-Location) -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','sections/facility-assembly/unity/bake_all.ps1','-Device','GPU'
```

If you use the portable Blender, add `'-Blender','C:\Blender\blender-5.2.2-windows-x64\blender.exe'` to the list.

**Before the first bake, `bake_all.ps1` checks:**
- Blender is found;
- the GPU is found;
- every file from step 4 is present.

**Each room then runs these stages:** prep, base, rough, normal, metal, emit, finish, compare.
- The compare stage renders three cameras from the source and the baked file, at 64 samples.
- Each room's log is `sections/facility-assembly/unity/_logs/<room>.log`.
- Each room's output is `sections/facility-assembly/unity/<room>/`. It holds the `textures/` folder, `<room>.fbx`, `<room>_unity.blend`, `materials.json`, `lights.json`, `bake_report.json` and `compare/`.

**Watch the first room until its `base` stage has started:**

```powershell
Get-Content sections/facility-assembly/unity/_logs/cooling-plant.log -Wait -Tail 20
```

Confirm the log shows `BLENDER DEVICE GPU (owner choice): HIP`. After that you do not need to keep watching; tell the owner it is running. The medical and dock rooms print these lines, which are expected and not errors:
- `Cannot find lib '...facility_environment.blend'`;
- `Unrecognized file format`;
- `lib.override.resync | ERROR Linked id 'SCCritical Shift | Mountain Watershed' ...`.

Neither room needs that file. Only a non-zero exit, which `bake_all.ps1` reports, counts as a failure.

**If a room fails,** `bake_all.ps1` stops and names the room and its log. Read the last 60 lines of that log.

- **Out of GPU memory** (`System is out of GPU memory`, `hipErrorOutOfMemory`) or a driver timeout or crash: stop and report. Do not lower settings or switch devices yourself. The owner decides between rerunning that room with smaller atlases and other options.
- **`KeyError` naming a collection:** stop and report the exact name.

A missing comparison camera only prints `COMPARE missing camera <name>` and the run carries on; include it in the report.
- **Anything else:** stop and report.

**Resuming after the owner agrees on a fix:** run `bake_all.ps1` again, adding:
- `-Only <room> -From <stage that failed>` for the failed room;
- then `-Skip <rooms already done>` for the rest.

Comma-separate room names, with no spaces.

## Step 6: Report back to the owner

When all rooms are done, or the run stops, report:

1. **Versions and status:**
   - `git log -1 --oneline`;
   - `blender.exe --version` (first line);
   - the GPU line from step 3;
   - which rooms finished and which did not.
2. **For each finished room,** from `sections/facility-assembly/unity/<room>/bake_report.json`:
   - minutes per stage (from the room's log: each stage prints `== <room> : <stage>` and then its minutes);
   - objects;
   - triangles;
   - lights;
   - seconds.

   From `materials.json`, give each material's `size` (the atlas size).

   Also give the total size of the `textures/` folder and of the `.fbx`.
3. **Comparison images:** the paths of the images in `<room>/compare/source/` and `<room>/compare/baked/`, and any pair that looks clearly different (dark, black, pink or missing parts).
4. **For a failed room:** the room, the stage, and the last 60 lines of its log.
5. **Repository state:** confirm that `git status --porcelain` shows only the new bake outputs (untracked) and the rebaked `cooling-plant/` files, and nothing else. **Do not commit them.**

**Known limits**, not for you to fix; tell the owner if asked:
- These bakes come from the room files. They do not include the map-side changes: door cuts, the mine's triangle reduction, the turbine's exterior skin, the animated ore cart and the evacuation additions.
- The reactor's 16 roof-bay area lights sit outside its collections, so they are not in its `lights.json`.
- Nothing has been imported into Unity yet.
