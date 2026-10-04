# Independent bounded code/package review — R50

Read-only review of the R50 source/material inventory/validation, canonical build/render/replay tools, package instructions and requested change scope. I read the prior R49 code review and R47 guard-check report. I did not rerun those R47 checks; their PASS results are historical evidence only.

## Findings

### Medium — cold comparison rejects revision names accepted by the builder and renderers

`blender/build_overhaul.py:7` accepts names matching `R\d+[a-z]?`; `blender/render_overhaul.py:15` and `blender/render_detail.py:14` accept the same revision family. `blender/compare_coldstart.py:12`, however, requires every character after `R` to be a digit. Thus a supported full revision such as `R50a` can build and render but its cold state/pixel comparison exits at the assertion before reading evidence. This is a reproducible static grammar mismatch; the current numeric R50 comparison is unaffected. Make the comparison revision validation match the canonical supported full-revision grammar, while retaining basename/path rejection.

### Medium — normal archive guard misses orphaned revision snapshots

`blender/build_overhaul.py:11` rejects reuse only when the checkpoint `.blend` or `history/<REV>_build.py` exists. Lines 14–18 include `history/<REV>_full_room.py` and `<REV>_build.json` among planned outputs, but only check whether they are symlinks or resolve to the immutable source. If an interrupted/partial prior build left `history/R50_full_room.py` without the checkpoint or build snapshot, a normal R50 build passes the collision guard and later `write_bytes` can overwrite that historical module. The same hole applies to a lone checkpoint build report. Reject any pre-existing revision-owned archive/checkpoint output (apart from intentional stable candidate aliases), or require explicit recovery for partial archives. The R47 guard report does not show this orphan-file case, and I did not rerun its tests.

### Low — clean-checkout cold comparison dependency is undocumented

`blender/compare_coldstart.py:8` imports Pillow (`PIL.Image`, `ImageChops`, and `ImageStat`) and is run with ordinary Python after Blender renders. The README documents Blender, `git lfs pull`, and environment variables, but does not state/install the Pillow dependency or give the comparison command. A fresh checkout with Blender available but no Pillow cannot complete the documented reproducibility workflow. Add an explicit prerequisite/install step or a pinned comparison requirements file and command.

## R50 evidence and scope

The seven R50 additions in `blender/full_room.py:1137–1149` enlarge the existing single-layer `projected_coating_loss` calls; they do not add a second primer outline. The shared helper ray-projects tessellated vertices onto the evaluated curved shell and records a support anchor. `production/validation_R50.json` is source-matched to `267bcf58ca796d9a09503088207cd3820419476b5301b388ecb64029095e8264`, passes with 589,943 evaluated triangles, 335 new and 57 inherited supports, zero disabled material links and zero issues; all 26 projected-wear face checks pass. `production/material_contract_R50.json` has the same source hash, 290 visible materials, no image-texture consumers and no UV shader consumers. These inventories support source/dependency claims only; they are not visual acceptance.

The changed path set is limited to `AGENTS.md`, Waste Storage overhaul files, and the two candidate aliases `module_overhaul_R1.blend` and `module_overhaul_slice_R0.blend`. The Waste Storage row is the only `AGENTS.md` change. Root `.gitattributes` covers facility-assembly `.blend`/`.png` bodies; the package `.gitattributes` covers generated validation/material/fingerprint/build JSON, and `git check-attr` resolves those rules for the R50 files. No external image-texture or linked-library dependency is reported by the R50 material inventory.

This bounded review does not certify R50 full render pixels, cold replay, runtime integration, or art acceptance. No blanket claim is made that historical rejection checks were rerun.

## Canonical remediation follow-up

The three findings above have been addressed in the current canonical workflow and checked with `production/workflow_guard_checks_R50.json`:

- `build_overhaul.py:11–18` now rejects any existing revision-owned checkpoint/build report/history builder/history full-room artifact. Candidate aliases remain intentionally separate. The recorded isolated checks preserve orphan `.blend`, `_build.json`, `_build.py`, and `_full_room.py` sentinels; reject a linked candidate alias and a path revision; and confirm the original source unchanged.
- `compare_coldstart.py:12` now accepts the canonical numeric or lowercase-letter-suffixed full revision grammar while continuing to reject traversal. Its recorded positive control executes the actual comparator with complete R49 23-view evidence renamed `R49a` and passes authoring plus pixels.
- `README.md:9` and `production/HANDOFF.md` now state the Pillow requirement and provide the comparison command plus exact selected-revision replay sequence.

These checks exercised the updated canonical scripts in isolated fixtures. They did not rewrite or rerun the frozen R50 archived builder; its exact replay remains preserved. The fixes resolve the identified reusable-workflow findings for new canonical revisions, with R50 itself still subject to its separate complete paired visual and cold evidence gates.
