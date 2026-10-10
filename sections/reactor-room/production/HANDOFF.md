# Reviewed reactor hall — next agent

The starting scene is [../blender/reactorroom.blend](../blender/reactorroom.blend),
SHA-256 `28fc09a259369b685ca1f96ad78cfd19bc0992f4ae67b200cb2143d9272905e3`.
It contains packed images and built-in fonts, with no linked scene libraries.
Use Blender 5.2.2 LTS. Open this saved source to continue; the older R1 map module,
dated render folders and an entirely fresh pipeline build are different checkpoints.

## Get only this handoff

From a clean checkout:

```sh
git fetch origin refs/heads/codex/reactor-refinement-handoff-20261010:refs/remotes/origin/codex/reactor-refinement-handoff-20261010
git switch --track origin/codex/reactor-refinement-handoff-20261010
git lfs install --local
git lfs pull --include="sections/reactor-room/blender/reactorroom.blend,sections/reactor-room/production/renders/final/refinement-28fc/**"
python3 sections/reactor-room/production/overhaul-R1/scripts/verify_refinement_handoff.py
```

The branch starts at `bb6b4924849d38097ee629a6fa2c00dc1b56095f`, the current main
at handoff creation. Only reactor paths, their scoped LFS attributes and the reactor discovery row in `AGENTS.md` are changed.
Do not merge the old `codex/reactor-integrated-720p-20261007` branch: its earlier
history diverges from current map work. A main merge is unnecessary to inspect or
continue this branch; repository review and merge remain separate steps.

## Inspect the result

- [Ten original full-quality 1280×720 views](renders/final/refinement-28fc/gallery.html).
- [Independent final review](critics/refinement-28fc/LUNA_28FC_FINAL_REVIEW.md):
  all 140 task criteria accepted, overall 91, all nine areas 88–93.
- [Original dispositions](critics/refinement-28fc/LUNA_28FC_DISPOSITIONS.json) and
  [evidence map](critics/refinement-28fc/LUNA_28FC_ROLLING_140_EVIDENCE_MAP.md).
- [Portable file index](checkpoints/refinement-28fc/handoff.json), finite warm/cold
  checks, the 124 declared cold comparisons and frozen stage-integration hashes.

The view manifests and reports are byte-preserving copies. Their absolute paths
describe the original authoring workspace, not a required directory layout in a
new checkout. Current files are located by `handoff.json`. Direct proof 37 uses the
final scene; proof 82 remains explicitly historical source `870b`, retained for
the unchanged maintenance fixture. Referenced historical reports are included;
the complete historical image archive is not downloaded with this handoff.

## Continue safely

Keep generated experiments under `/tmp` or another scratch directory. Use
`overhaul-R1/scripts/` for the existing authoring and finite-check tooling. The
accepted saved scene is the baseline: recorded cold checks do not claim a fresh
whole-pipeline run produces identical scene bytes. No pipeline is run by checkout.

For a new full-quality render, from the repository root:

```sh
blender --background --disable-autoexec -noaudio sections/reactor-room/blender/reactorroom.blend \
  --python-exit-code 1 --python sections/reactor-room/production/overhaul-R1/scripts/render_detail_views.py \
  -- --output /tmp/reactor-review
```

Do not save renderer camera changes over the accepted source. The broad wet patch
crossing one arrow is a documented minor finish weakness, not an open task issue.
Finite geometry checks do not prove every collision or access route: the control
room aggregate passes while some individual front-access checks report BLOCKED.
No Unity performance, runtime export or combined-map integration was validated.
The task's 90/85 score bar does not advance another repository acceptance gate.

## Storage

Git contains one scene, ten main PNGs and two supporting PNGs, with all thirteen
binaries in LFS. Review metadata and authoring code are ordinary Git files.
Generated iteration folders, Blender backup files and duplicate ZIP packages are
ignored. During this session the complete archives were preserved outside the
repository at `/workspace/reactor-room-refinement-archive-20261010/`; that local
directory is not a remotely available dependency. Its verified original ZIP hash
is recorded in `handoff.json`. Request that archive only for historical pixel
re-review; continuing the delivered scene does not require it.
