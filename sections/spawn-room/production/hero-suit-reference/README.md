# HZ-01 owner-reference suit

The yellow hazmat reference supplied by the owner on 2026-10-01 is the target for
this character revision. It overrides the older adult-proportion instructions
for this scoped suit. It does not change environment art direction or room acceptance.

Open `../../blender/crew_hazmat_reference.blend` for the wearable character and
studio cameras. `../../../facility-assembly/sources/spawn-room/hero_suit.blend`
is the empty `HERO_SUIT` library already linked by the four spawn lockers on
`claude/spawn-polish`. Both are built through `character_suit.build_hazmat`;
`style="legacy"` retains the earlier suit test. The new style preserves region
coverage and `equip()` and supports suit/glove/boot/pack/accent/visor colour options.

The visor, hood seams, warm yellow fabric, grey rim hardware, headlamp, side ports,
orange face, charcoal eyes, black flat webbing, silver buckles, zipper, red keepers,
HZ-01 sleeve identifier, elbow chevron, knee protection, leg warning and shaped
rubber boots are authored in `../../blender/hazmat_reference.py`. The unseen back
is an inferred continuation, not a second supplied reference. Fonts are bundled
with their license; labels are meshes and face textures are packed in the scenes.
The visor uses an intentionally non-refracting thin-surface shader so the face
remains readable. This is a stylized authoring shader, not Unity equivalence.

The later glove-cuff cleanup removes the loose radial rib strips from both
wrist collars. `final/glove_cuffs.png` shows the updated cuffs, cropped from the
actual final hero render. Both native sources include this cleanup.

## Rebuild and review

From the repository root, using Blender **5.2.1 LTS** and Pillow in its bundled
Python. Helper tools use Python 3.12+; mine CI separately uses Python 3.11.

```sh
blender -b --factory-startup -noaudio --disable-autoexec --threads 5 \
  --python-exit-code 1 --python sections/spawn-room/blender/render_suit_reference.py -- \
  --output sections/spawn-room/production/hero-suit-reference/final \
  --save sections/spawn-room/blender/crew_hazmat_reference.blend \
  --width 1086 --samples 48 --views hero front side back

blender -b --factory-startup -noaudio --disable-autoexec \
  --python-exit-code 1 --python sections/spawn-room/blender/build_hero_suit.py -- \
  sections/facility-assembly/sources/spawn-room/hero_suit.blend

blender -b --factory-startup -noaudio --disable-autoexec \
  --python-exit-code 1 --python sections/spawn-room/blender/lod_hero_suit.py -- \
  sections/facility-assembly/sources/spawn-room/hero_suit.blend

blender -b sections/spawn-room/blender/crew_hazmat_reference.blend -noaudio \
  --disable-autoexec --python-exit-code 1 \
  --python sections/spawn-room/blender/render_suit_reference.py -- \
  --loaded --output sections/spawn-room/production/hero-suit-reference/cold-start \
  --width 1086 --samples 48 --views hero

blender -b sections/facility-assembly/sources/spawn-room/module.blend -noaudio \
  --disable-autoexec --python-exit-code 1 \
  --python sections/spawn-room/blender/validate_suit_library.py -- \
  --output sections/spawn-room/production/hero-suit-reference --render
```

When rebuilding an existing library, the builder reads its top, boot-bottom and
pack-back attachment coordinates, then aligns the new collection to those exact
coordinates. This keeps the already placed suits on their docks without saving
the room or moving its instances. A new destination with no prior library uses
the wearable character's natural frame. The small placement transform is recorded
on the library root; measurements on the collection describe the resulting frame.

The cloud toolchain for this task is installed under `/workspace/toolchains`:
Blender 5.2.1 LTS, standalone Python 3.12.14 with the repo's art dependencies,
Python 3.11.16 for mine CI, and Blender's bundled Python 3.13.13 with Pillow.
In this executor Blender needs tool network access to exit its audio backend
cleanly; `PULSE_SERVER=unix:/tmp/codex-no-pulse` and `-noaudio` were used. No VPN,
environment policy, Unity packages or workflow configuration was changed.

## Evidence and limits

See `TASK_STATE.md`, `final/VALIDATION.json`, `LINKED_LOCKER_VALIDATION.json` and
the cold-start report. The reference match is assessed from rendered pixels, not
from object names or successful saves. Neither this source nor the room receives
owner art approval automatically. The model is hero authoring geometry, with
substantially more triangles than the earlier gameplay test. Rigging, current LOD
budgets, Unity import, draw calls and frame time require a separate delivery pass.

`module_optimised.blend` (self-contained) has been regenerated from the linked module with the locker LOD of this suit
(see "Locker LOD" below and `../optimise/README.md`): contacts, signatures and the six-camera comparison were re-run on
it. The frozen accepted sources, map caches and provenance are not changed.

## Git delivery workaround

The owner requested publication despite the executor's Git LFS authentication
failure. The two suit native files and the PNG evidence in this directory use
ordinary Git storage through three explicit `.gitattributes` rules. Each file is
under 5 MB. This allows a complete, directly usable review branch to be published
through the authenticated GitHub Git Data API. Other facility LFS rules continue
to apply. The draft PR targets `claude/spawn-polish`; it does not merge or promote
the asset. The earlier local commit history and LFS objects are also retained in
the task's verified portable backup.

The workaround covers only those files. `module_optimised.blend` (regenerated with
the locker LOD in the follow-up PR #69) stays in Git LFS and was uploaded normally
by that branch's executor: a fresh clone of the branch followed by
`git lfs pull --include=sections/facility-assembly/sources/spawn-room/module_optimised.blend`
retrieves the 33,575,117-byte file and its SHA-256 equals the pointer's OID
(`3abf6ae6...f717f`).

## Locker LOD

`hero_suit.blend` (the library the four lockers link) is now a reduced copy of the suit: `build_hero_suit.py` builds the
full-detail suit (114,094 triangles) and `lod_hero_suit.py` then decimates it object by object to 22,371 triangles
(solidify applied first, smooth shading and every material kept; the collection records `cs_lod = "locker"` and the counts
before and after). Rebuild order: `build_hero_suit.py`, then `lod_hero_suit.py` (both are in the command block under "Rebuild and review", before
the linked-room validation, which now fails unless the library is the locker LOD). `lod_hero_suit.py` refuses a library already marked
`cs_lod = "locker"` (exit code 1, file untouched), so a retry cannot decimate twice; to redo the stage, rerun `build_hero_suit.py` first. The full-detail suit stays in
`crew_hazmat_reference.blend`. At locker distance the reduced suit differs from the full one by edge detail only (mean
absolute pixel difference 0.005 on a 854x640 render from 2.3 m).


The linked-locker validation (`LINKED_LOCKER_VALIDATION.json`, `final/linked_lockers.png`) was re-run on the locker LOD library: dock gap and top alignment pass for all four instances and the record includes the LOD triangle counts.
