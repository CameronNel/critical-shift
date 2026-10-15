# Condenser A2 — machinery finish, current R5c

The owner's direction is “less teal and cream, more machine color.” The condenser
now has deep machine-blue enamel, oxide-red waterboxes/pumps, graphite hotwell and
framing, gray service pipework, distinct bare metals, quiet mineral walls and a
darker coated floor. Yellow identifies access and controls. Neutral practical
light creates equipment highlights and readable shadows. This supersedes the
old ivory-panel preference; other constraints and review thresholds remain.

Built directly from frozen reviewed R34 `module.blend`, never A1 materials or
lighting. Blender5.2.2 LTS. Branch `codex/condenser-finish-a2`, started from
main70d93dd6 and fast-forwarded to82c29117 after cafeteria PR106 merged. Editable
[module_aaa_A2.blend](module_aaa_A2.blend) matches immutable
`checkpoints-A2/A2-R5c.blend`, SHA256
`5c1277da8d68c89abacaf851fbd8a70467032afaa86ff8fafe2f5e7951a73388`.
Actual build measurements/assignments: [finish-A2-build.json](finish-A2-build.json).
Authority: [REWORK_BRIEF.md](REWORK_BRIEF.md).

Paint has fine orange peel and controlled roughness; dark oiled iron, cast metal,
brass, brushed steel, rubber and glass remain separate families. Six original
numeric maps are packed. Explicit world-normal weighted planar samples use
world-metre coordinates,0.12–0.24m repeats and mineral tone within±5.5%. Floor
polish is confined to walk lanes through `A2 floor metres` UVs. Curved triplanar
blend transitions are disclosed, not claimed as distortion-free UVs. There is
no A1 camouflage/grime layer or inherited A1 mood pass.

Independent warm diagnosis found coarse pipe cross-sections and a rotated-face
texture-axis mismatch. Both are repaired in new images:14 existing service
curves retain all centreline points, endpoints, radii, names and transforms,
with32-sided profiles on the two large CW headers and16 on the remainder. The
projection uses matching coordinate/normal frames; flange/cap checker fields
now show squares. All15 material-board captions are visible on their front faces.
See [R5 diagnostic](critics-A2/DIAGNOSTIC_R5.md) and
[R5b diagnostic](critics-A2/DIAGNOSTIC_R5b.md); these are not final acceptance. The independent critic also opened every fresh
R5c main image and the new owner/comparison views, finding no new major finish
defect: [R5c warm-main diagnostic](critics-A2/DIAGNOSTIC_R5c.md).

The finish also includes24 shallow formwork tie sockets, manufactured gallery
lamp frames/lenses/clamps and a1mm north-wall erection joint. R5c has
**349,678 native evaluated triangles**, including text, and **395,482 in the
assembled map**. Only634 tiny washer/shank meshes receive the tighter budget
reserve; bolt heads and the eight audited chest stacks are excluded. All original
non-light object matrices remain unchanged. Frozen R34/A1/accepted inputs,
contracts and other rooms remain untouched. The sole combined-script edit is
the authorized condenser A1→A2 source tuple.

## Actual checks and evidence

- All six original saved-room audits PASS:
  [CPU summary](evidence-A2/R5c/room-audits/R5c/cpu-validation-summary.json).
  Bore/inlet, doorway/routes, supports, joints, fastener seating, gallery and
  cameras are covered by the original tools. Native geometry checks do not
  certify the different assembled gallery headroom.
- Build and all11 original map tools exit0; every specified numeric gate PASS:
  [exact pass values](evidence-A2/map-R5c/pass-values.json),
  [commands/exit codes](evidence-A2/map-R5c/commands.json).
  Normal17/18 (only inherited cart route), proxies10/10, meltdown20/20,
  closed13/13; condenser2 exits/no single-door cut-off; doors45/0flags;
  no new condenser floor or overlap pair;395482tri; scoped FBX202/re-importPASS.
- Lighting29/30, only inherited `spine_mid`. All four required views meet the
  stronger15% near-black/5% clipping limits. Interior median0.577,
  near-black0.1%, clipped2.2%. All30 actual lighting frames are retained.
- Current exact owner view: `renders-A2/owner-map-R5c/` (1920×1080,32samples,
  eye1.6/3.9/−4.4, target6/10.3/−4.8,16mm). Complete and opened at full resolution; A1 comparison beside it.
- Fresh full warmR5c22+7, stabilityR6c22+7, cold-R6c22+7 and four material
  diagnostics are queued/running. Their current actual commands/status are in
  [the sequential receipt](evidence-A2/palette-revision-R5c/commands.json).
  No incomplete pack or unrun comparison is a pass.
- Final independent ten-category scores: **pending**. No self-acceptance or merge.
  [Current review inputs](critics-A2/REVIEW_INPUTS_R5c.md).

The collector uses the section's original render/audit/comparison tools in
isolated temporary copies. Documented cloud adaptations are CPU5threads,
Linux nice10, CPU OIDN and the required four AAA cameras. No numeric threshold
or camera guard is relaxed. Actual argv, working directories, exit codes,
durations, native/renderer/camera/PNG hashes and producer PIDs are retained.
The current queue entrypoint is `run_A2_palette_evidence.py --blender <5.2.2>
--round R5c --stability R6c`; `--resume` retains only verified completed work
against the identical native. Historical R3/R4 helpers are not the current queue.

## Failed and superseded work

R3e technical checks and complete R3/R4/cold images passed; the owner rejected
the pale art as flat. R5's complete22+7 warm images, owner view, numeric room/map
checks and four diagnostics completed, but its stability/cold queue was stopped
for the independently identified corrections. Its earlier preview-append
priority-guard failure is retained; a fresh full pack subsequently exited0.
R5b repaired profiles/mapping but failed the actual map budget at406070;
remaining map/full/stability/cold stages were not run. R5c recovers that budget
through the small fastener reserve. R2b/R3a–c calibration failures are retained.
Focused R5b preview camera-name and diagnostic-import failures are retained with
their corrected fresh attempts. No old pixels are relabelled as a new cycle.
See [WORK_LOG.md](evidence-A2/WORK_LOG.md) and per-revision command receipts.

## Binding limits — no waiver or engine acceptance

The R34 gallery walking surface is about z3.94. The prescribed map ceiling
underside is z5.695, leaving about1.755m assembled standing clearance. The native
2m audit uses the original roof and does not certify that condition. Preserving
architecture/equipment transforms and roof/U04 mating conflicts with a universal
visible z5.6 cap. The source report explicitly retains260 inherited upper
structure exceptions, while lights/new finish fixtures are capped. An optional
clarification remains unanswered; silence and disclosure are **not a waiver**.

Overhead CW isolators and the isolate hook retain their R34 locations. The brief
makes their repair optional; rubric hard gate8 still requires accessible controls.
These unresolved conflicts prevent unconditional strict acceptance. Full final
scoring must record them, regardless of art improvement or technical map passes.

**Not run/certified:** Unity material conversion or engine import/movement,
runtime performance/FPS, human playtest, full removal swept volume, turbine U02
work, reciprocal cooling remotes or full facility loop. The FBX round trip covers
colliders/anchors through Blender only. No new neighbor openings or source edits.
One task branch, one draft PR, no self merge.
