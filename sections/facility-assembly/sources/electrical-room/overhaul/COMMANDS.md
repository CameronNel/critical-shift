# Electrical authoring and verification commands

Run from the repository root. `run.sh` requires Blender5.2 LTS and selects the
checksum-verified workspace installation unless `BLENDER_EXECUTABLE` is supplied.
Blender carries Python3.13.13; standalone QA uses the installed Python3.11.16.
One Blender process at a time, Cycles CPU with four threads. Formal images use
1280×720,16 samples, fixed seed73 and the fourteen original camera matrices/lenses.
Supplemental detail images use24 samples and record their own camera matrices.
The current source has six supplemental views, including DG07_Probe_Junction.
R1 through R8 had five. DG06_Service_Contact belongs only
to the retained, rejected floor-contact preflights and is not final evidence.

```sh
bash sections/facility-assembly/sources/electrical-room/overhaul/run.sh build full /tmp/electrical-rebuild.blend
bash sections/facility-assembly/sources/electrical-room/overhaul/run.sh validate /tmp/electrical-rebuild.blend /tmp/electrical-rebuild-validation.json
bash sections/facility-assembly/sources/electrical-room/overhaul/run.sh capture /tmp/electrical-rebuild.blend /tmp/electrical-rebuild-renders 16
```

The baseline copy is required; do not run the builder against a previously
overhauled source. Rebuild to a new output path when preserving an approved file.
The builder asserts the source has no overhaul objects, saves only its explicit
output, and leaves cameras/interfaces intact. Capture and validation do not save.

Door-only correction is reproducible through `door_history.py`, called by the
full baseline builder. To preserve every other reviewed object byte-for-byte in
Blender geometry/assignment signatures, apply `repair_door_history.py` to
`checkpoints/full-R4.blend` with `--output NEW_CHECKPOINT --receipt REPORT`. The
validator explicitly records replacement of104 identified decorative door marks,
checks the214 other baseline items with the existing bounded door/wire exceptions,
and checks eight new registered contact assemblies. It does not silently claim
all318 original items are unchanged.

The final broad finish stage is `surface_finish.py`, also called by the baseline
builder. It declares five tactile material profiles, six existing practical
powers and four fixed individual door coating phases. Existing work-position
floor wear and material traffic response remain; the rejected new polygon-patch
layer is omitted. Final validation records59 support assemblies.

`retire_floor_polygons.py` reproduces the final R6e→R7 correction: pass
`full-R6e.blend` before `--python` and use `--output NEW_CHECKPOINT --receipt REPORT`.
It removes exactly six new patches, their single support root and unused material,
checking3033 other geometry/material/visibility/light signatures unchanged.
Neither the original room floor nor its existing wear is removed. The retained
height/exposure helper scripts are historical preflight evidence; they are not
called by the final builder and do not describe final accepted art.

The next finish stages, also called by the full baseline builder, are
`lead_finish.py`, `vision_finish.py` and `reserve_finish.py`. To reproduce their
bounded saved-source application, run `repair_lead_finish.py` against
`checkpoints/full-R7c.blend`, then `repair_reserve_finish.py` against its output,
each with explicit `--output NEW_CHECKPOINT --receipt REPORT`. The first stage
checks eight winding-to-saddle contacts, preserves both trolley cable endpoints
and changes only ten existing meshes plus one wired-glass definition. The second
stage preserves every existing object/material definition and adds nine service
strips with eighteen measured rack-jamb contacts. Fixtures reuse three registered
rack roots; the final source still has59 registered support assemblies.

Additional Blender scripts use the same executable and
`-noaudio --background --disable-autoexec --python-exit-code 1 --python SCRIPT --`:

Pass the saved `.blend` source before `--python` for `capture.py`;
integration/audit scripts open their own explicit inputs.

- `capture.py --out DIR --diagnostics --samples 24 --width 1280`
- `capture.py --out DIR --floor-proof --samples 24 --width 1280` adds one
  low oblique resolving view of the existing center-floor material. It never
  changes/saves the room and does not replace a formal or map camera.
- `integrate_candidate.py --module MODULE --output CANDIDATE`
- `audit_candidate.py --candidate CANDIDATE --module MODULE --out REPORT`
- `optical_proof.py --out DIR` opens the provided saved source and creates a
  temporary existing-fuse specimen behind one pane. It renders the same camera
  with and without that pane, asserts unchanged source bytes and never saves.
  This diagnostic establishes transmission; it adds no credited room dressing.
- `preserve_legacy.py --baseline BASELINE --requests AUDIT --output CHECKPOINT
  --receipt REPORT` retains exact original material IDs needed by the main map's
  baked cache and checks unchanged visible material assignments. The builder
  also preserves baseline material IDs before creating the new room.
- `verify_active_checkout.py --out REPORT` runs the repository's native/preview
  cold checker, saves a task receipt and restores the historical tracked receipt.
  It verifies frozen-source hashes and control registration, not missing linked
  datablock names; candidate audit handles that separate check.

The integration script opens the current MAP.json authoring scene, changes only
the electrical interior cache/link in an additive candidate and checks original
neighbor transforms and source-library hashes before saving. It refuses the
canonical-map and immutable-R17 output paths. The candidate is an assembled-map
render/link handoff; map-owner preview/focus-mode integration and runtime work are
not certified by those images.

Cold pixel comparison uses Python3.11 with `Pillow==11.3.0` in an isolated venv:

```sh
python3.11 -m venv /tmp/electrical-qa
/tmp/electrical-qa/bin/python -m pip install Pillow==11.3.0
/tmp/electrical-qa/bin/python sections/facility-assembly/sources/electrical-room/overhaul/scripts/compare_captures.py --previous sections/facility-assembly/sources/electrical-room/overhaul/renders/R9 --cold sections/facility-assembly/sources/electrical-room/overhaul/renders/R10 --out /tmp/electrical-cold-comparison.json
```

For the R3→R4 unused-material-ID transition, pass
`--legacy-compatibility-receipt overhaul/legacy-compatibility-R4.json` (with the
full repository-relative path). That mode checks the exact input/output hashes
and unchanged visible assignments from the receipt, records different source
bytes explicitly and compares pixels/settings/cameras. It is not a same-source
cold repeat. R4→R5 comparison omits that option and requires identical source hashes.
R5→R6 uses `--visual-repair-receipt` with `visual-corrections-R6.json`, which
binds the exact door and final surface-stage receipts, and
reports a declared visual iteration with measured differences, not a cold repeat.
R6→R7 uses `retired-floor-polygons-R7.json` through the same transition option,
declaring only the rejected new six-piece layer/root/material retirement. R7→R8
comparison omits transition options and requires identical source hashes. R8→R9
uses `visual-corrections-R9.json`, explicitly binding the cable/glass and additive
reserve-lighting stages, and is a visual iteration. Final accepted R9→R10 cold
repeat omits transition options and requires identical source hashes; all fourteen
decoded RGB images are identical. No
transition option credits visual improvement without review.

`compare_map_captures.py` separately verifies all five assembled-map images,
using `--previous DIR --cold DIR --previous-integration RECEIPT
--cold-integration RECEIPT --previous-audit AUDIT --cold-audit AUDIT --out REPORT`.
It requires identical electrical module and base-map hashes, unchanged neighboring
sources/transforms, passing bounded link audits and exact camera/settings parity.
It reports every decoded-pixel difference without assigning visual acceptance.
`--require-identical-pixels` adds a separate bit-exact criterion. The retained
strict R7/R8 preflight fails on six channel values differing by one8-bit step in
EI_W01 while its other four map views are identical; this result is not silently
rounded to zero or substituted for the critic's visual review.
The final R9/R10 assembled repeat records three identical images and two with
a few one-step channel differences; the fresh critic independently finds no
material visual regression. `R9-to-R10-map-pixel-comparison.json` records the exact
measured result. It is not claimed as bit-exact for all five images.
Separate candidate saves can have different bytes due
to relative source paths/save metadata; this is explicitly recorded and is not
presented as a same-candidate-byte cold test or runtime certification.

The raw `renders/**/inspection.json` scene surveys use Git LFS under the scoped
overhaul `.gitattributes`; readable manifests, validation, reviews and build code
remain ordinary text. Hydrate the task's assets before reproduction:

```sh
git lfs pull --include="sections/facility-assembly/sources/electrical-room/**,sections/facility-assembly/blender/facility_electrical_overhaul_candidate.blend"
```

Whole-map context also requires the minimal map dependency set documented in
MAP.md. Intermediate map-R2 through map-R7 and map-R9 files are local-only; the final map candidate is
the committed assembled artifact.

## Repeat the final source/map checks

Use a fresh output candidate beside the map, preserving the reviewed artifact.
These commands run sequentially; source validation/capture do not save the module.
The repository checker wrapper also restores the historical tracked receipt.

```sh
electrical_dir="sections/facility-assembly/sources/electrical-room/overhaul"
electrical_module="sections/facility-assembly/sources/electrical-room/module.blend"
electrical_blender="${BLENDER_EXECUTABLE:-/workspace/toolchains/blender-5.2.1-linux-x64/blender}"
electrical_candidate="sections/facility-assembly/blender/electrical_review_copy.blend"
bash "$electrical_dir/run.sh" validate "$electrical_module" /tmp/electrical-source-check.json
"$electrical_blender" -noaudio --background --disable-autoexec --python-exit-code 1 --python "$electrical_dir/scripts/verify_active_checkout.py" -- --out /tmp/electrical-map-check.json
"$electrical_blender" -noaudio --background --disable-autoexec --python-exit-code 1 --python "$electrical_dir/scripts/integrate_candidate.py" -- --module "$electrical_module" --output "$electrical_candidate"
"$electrical_blender" -noaudio --background --disable-autoexec --python-exit-code 1 --python "$electrical_dir/scripts/audit_candidate.py" -- --candidate "$electrical_candidate" --module "$electrical_module" --baseline-audit "$electrical_dir/candidate-audit-R3.json" --out /tmp/electrical-link-audit.json
"$electrical_blender" -noaudio --background --disable-autoexec "$electrical_candidate" --python-exit-code 1 --python "$electrical_dir/scripts/capture.py" -- --out /tmp/electrical-map-renders --views EI_C01_Entry,EI_C03_Reverse,EI_C04_Route,EI_W01_Turbine_Return,EI_W02_Waste_Approach --samples 16 --width 1280
```

Integration writes a new `integration-candidate.json` receipt in the overhaul
folder. Preserve the reviewed final receipt (`integration-R10.json`); a newly generated
copy is a reproduction receipt, not replacement final acceptance. Audit compares
current missing-ID identities to the recorded pre-promotion R3 snapshot, so it
cannot normalize a source-promotion regression into a new baseline.

## Retained failures and repairs

- First slice support validation failed. `slice-validation.json` retains the raw
  failures; target names/anchors were corrected before full-room expansion.
- Slice and full-room visual failures remain in `critics/SLICE.md`, `R1.md` and
  `R2.md`; preflight optical evidence has a distinct source and manifest.
- A temporary ceiling diagnostic initially indexed an unevaluated mesh with an
  evaluated ray face index, raising `IndexError`. It was corrected to record hit
  object/location; a no-surface ray established the bevelled shell seam gap.
- Installing Pillow directly into the uv-managed standalone interpreter failed
  with `externally-managed-environment`. The isolated Python3.11 venv succeeded.
- First legacy-ID preservation attempt asserted incorrectly because Blender
  mutates the assigned library-load list from names into datablocks. Passing a
  copy preserves the string list and exact-name assertion; the corrected run
  restored all11 IDs. No source was saved by the failed attempt.
- Height-only floor-contact preflight still produced identical pixels because
  insulating mats covered the contours. The next exposed preflight resolved
  placement but revealed faceted pasted patches. Both failed attempts remain;
  final R7 retires only this weak NEW layer and preserves existing floor history.
- The first R7 optical manifest recorded an identity camera matrix before graph
  evaluation. That run is retained as `optical-metadata-preflight-R7` and excluded
  from final acceptance. The corrected script updates before recording, checks
  the evaluated pose after both renders and generates a fresh final pair.
- The first R9 supplemental command batch completed its five detail images but
  used a mistyped x86_64 executable path in the queued final step. That command
  failed127 before optical capture. The optical script was run explicitly with
  the installed x64 executable; the failed batch is not claimed as successful.
- This cloud host hangs in PulseAudio shutdown, including with `-noaudio`.
  Successful saved-output scripts flush and terminate after writing/verifying
  outputs; validator exit status still reflects failures. This does not turn a
  failed command, unfinished render or rejected review into a pass.

Hash-bound manifests/validation and independent reviews are the acceptance
evidence. Process success or a build/mesh count alone is not visual acceptance.
