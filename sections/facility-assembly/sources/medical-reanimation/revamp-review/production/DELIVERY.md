# Reanimation room source and evidence

Branch: `codex/reanimation-room-revamp-20260930`.

Open `module_overhaul_R2.blend` in Blender 5.2.2 LTS or newer and choose `REANIMATION_EDIT_LOCAL`. The other scene, `Critical Shift | Mountain Watershed`, is a read-only linked assembled-map reference. Preserve the source ZIP folder hierarchy so all 25 linked libraries resolve. Local room materials and the clinical poster are packed. The loose `.blend` contains the editable room, but the source ZIP also supplies its map dependencies.

The original medical module, approved spawn module, map file and room interface are protected. This is an isolated art branch; the assembled map continues to use its existing medical module until separate owner promotion. No merge was performed.

OCRU is the reanimation station for incapacitated or biologically offline workers (GAME_SPEC 4.5, 5.3–5.4). The opposite cot is for recovery. This art task does not implement runtime revival or engine integration.

The labelled final gallery includes four full-footprint corner cutaways, four walls, ten asset heroes, three player-height views, two detail views and one under-bed inspection. New evidence is 1067 × 600, Cycles 24 samples with denoising. Only the hidden-bag inspection adds a temporary, labelled 2 W fill; normal renders use the saved one-red, one-warm and two-directional light arrangement. Cutaways and labels are render-only and never saved into the source.

Build and verify from the room directory:

```sh
blender -b --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python overhaul_room.py -- --stage full
blender -b --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python verify_overhaul.py
blender -b --factory-startup --disable-autoexec --threads 5 --python-exit-code 1 --python render_overhaul.py -- --out cycle-16
blender -b --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python verify_overhaul.py -- --cold --dependencies
blender -b --factory-startup --disable-autoexec --threads 5 --python-exit-code 1 --python render_overhaul.py -- --cold --out cycle-17
python3 compare_overhaul_renders.py --hot cycle-16 --cold cycle-17
python3 package_overhaul.py --cycle cycle-17 --portable-map
blender -b --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python verify_delivery.py -- --root /path/to/extracted/source --report /path/to/portable-check.json
```

The bundled label font includes its licence; render-only labels fall back to the system font or Blender Bfont if necessary. Python comparison needs Pillow and NumPy. Baseline R1, original source modules, approved spawn input, poster and scripts are included in the source archive. Build snapshots are historical evidence; run the `.py` files in the room root.

Current skill-guided revision passes the independent process gates at source `39007192eef36f87c5299933e3a2a4f3462791871144c349a580ba2d9d322487`. Final cycle 16 scores 91.1/100; cycle 17 scores 91.7/100. Each category exceeds its exact minimum; all camera gates pass and no critical defects remain. Full hot/cold objective checks, exact 24-view decoded RGB/camera stability and actual extracted source-archive dependencies pass. Process PASS establishes art/source readiness for owner review. Owner art approval, main promotion and runtime integration remain separate. The review archive retains all useful renders, reference/concept images, diagnostics and recorded failures.

The exact final source ZIP is cold-verified again after packaging. Its external `reanimation-portable-final-check.json` and delivery manifest identify archive checksums, branch commit and remote availability. The source package includes the stage extracted-archive proof for the identical native source and dependencies.

The source and evidence are committed on the task branch; its remote delivery result is recorded in the external manifest. The Git bundle carries history and LFS pointers; native/source and evidence ZIPs carry actual files.
