# Conservative Blender snapshot cleanup, 14 September 2026

## Scope and result

Removed exactly five superseded output-only `.blend` snapshots from the cleanup branch, totaling **1,028,261,512 bytes** (1.028 GB / 0.958 GiB) of hydrated working-file payload. The earlier image cleanup removed 1,603,515,639 bytes, for a combined **2,631,777,151 bytes** (2.632 GB / 2.451 GiB). This is a current-checkout reduction, not a reduction in remote Git LFS storage quota.

The authoritative map remains the editable R17 scene and R17 inspection scene named in `MAP.json`. Neither was saved or changed. All map modules, linked exterior libraries, posters, textures, source artwork, current review evidence and replay inputs were retained. There are 111 tracked Blender files after this stage.

## Exact removals

| File in sections/facility-assembly/blender | Hydrated bytes | Reason |
| --- | ---: | --- |
| facility_master_A08_access.blend | 163364998 | Superseded master output; relevant walkthrough input retained |
| facility_master_A11_map_finish.blend | 170436320 | Superseded master output; relevant walkthrough input retained |
| facility_master_A12_complete.blend | 171384190 | Superseded master output; relevant walkthrough input retained |
| facility_master_A13_roof_services.blend | 171903416 | Superseded master output; relevant walkthrough input retained |
| facility_material_preview_A14.blend | 351172588 | Superseded generated preview output; A14 authoring source and current R17 preview retained |

Only these exact output filenames were added to the local Blender directory's `.gitignore`. There is no blanket `.blend` ignore and no rule suppressing new revisions.

## Why the broader deletion proposal was narrowed

The earlier proposal to discard all 24 non-canonical files was too broad. Source inspection found real rebuild dependencies:

- `correct_spawn_daylight_R17.py` opens `facility_spawn_concept02_R16.blend`.
- `upgrade_spawn_realtime_R16.py` opens the R15 authoring scene.
- `build_spawn_concept02.py` opens the A14 authoring baseline.
- Other historical walkthroughs, proxies and the whole-map floor are consumed by assembly/replay scripts.
- R15's preview still has a launcher and a default audit consumer.

Those files remain. No rebuild scripts were rewritten or redirected. The five removed files' literal executable references were inspected as output writes, not source reads. Dynamic `facility_{kind}_A07_horizontal_network.blend` input selection was also inspected, and both A07 inputs remain. No current launcher or active map/source registry referenced the five removals.

## Checks actually performed

Source audit run: https://github.com/CameronNel/critical-shift/actions/runs/34888100378

Native validation run: https://github.com/CameronNel/critical-shift/actions/runs/34888430517

The validation ran against commit `42e29618621d1234ba98a077963273df81dbdbbb` in a disposable GitHub Actions checkout with read-only repository permissions. It could not publish changes. The workflow source at that commit is the reproducible record of this bounded audit, not a general unused-file detector.

1. Verified the exact five candidate LFS object hashes and hashed all 671 pre-existing executable/source-workflow files against the separately inspected source audit.
2. Hydrated only protected map inputs, checked their LFS SHA256 hashes, and recorded every retained tracked file's physical byte hash.
3. Opened both canonical R17 scenes in separate Blender 5.2.1 processes, with scripts disabled and no rendering or saving.
4. Required the fresh native inventories to match the earlier durable R17 audit exactly. Checked that neither any native dependency path nor the library/image reports named a deletion candidate. Both scenes resolved 24 libraries with no missing libraries and retained 105 packed image payloads each.
5. Removed exactly the five allowlisted files in the disposable checkout.
6. Opened both R17 scenes again in fresh Blender processes. Full before/after JSON inventories were byte-identical, including scene hashes, object counts, geometry digests, dependency paths and packed-image hashes. Every one of the 2,375 retained tracked files in that runner comparison was byte-identical. The staged diff contained exactly five deletions and no other change.
7. Downloaded the resulting audit artifact and separately recomputed the before/after report hashes and deletion byte totals before publishing the matching deletions to the existing task branch.

The editable map retained 55,016 objects; the inspection map retained 55,390. No Unity, interactive navigation, embedded-script execution, FPS test or rendered comparison was performed. This is dependency and byte-integrity evidence, not a new art or gameplay acceptance.

The full native records match the existing durable `maintenance/image-cleanup-20260914/DEPENDENCIES_AFTER.json`; this cleanup's summary records their fresh individual checksums rather than duplicating those large reports. The complete new records and logs are in artifact `snapshot-native-verification` (ID 10365952130), with a 14-day retention period. `SUMMARY.json` retains the candidate Git blobs/LFS OIDs, sizes, scene checksums and result data permanently in the branch.

## Recovery and publication

The pre-deletion commit is `42e29618621d1234ba98a077963273df81dbdbbb`; the same five snapshots are also present in baseline main commit `a82c7d9b80456153a0c65ca4897044a7f62c7d1c`. Recover an individual snapshot from one of these commits and hydrate its exact Git LFS path, checking the object hash in `SUMMARY.json`. No historical commits, LFS objects or remote assets were purged.

Historical reports can still link to these intentionally pruned output snapshots. Those are archival references, not missing current-map dependencies. The corresponding build inputs and scripts were deliberately retained.

The one-off workflow was retired after successful validation, so no ongoing deletion automation is installed. The only final changes in this stage are five snapshot removals, exact-filename ignore rules and these audit documents. Changes are part of PR #44 on `chore/prune-generated-images-20260914`; independent review and merge into main are pending.
