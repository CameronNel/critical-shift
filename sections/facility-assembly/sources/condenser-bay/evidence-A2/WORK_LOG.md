# A2 work log — ongoing

Task authority: `REWORK_BRIEF.md`, read in full from current main before any work.
Branch: `codex/condenser-finish-a2`, from main `70d93dd6`.
Blender: 5.2.2 LTS, `/workspace/scratch/blender52/blender-5.2.2-linux-x64/blender`.

## Baseline

- Hydrated 88 selected source/texture files individually. No broad sparse checkout.
- Original R34 inventory: 2,724 objects, 641,598 evaluated triangles, AgX Medium
  High Contrast, exposure -0.1, world strength 0.2. Native dependency scan has no
  external images or libraries; Bfont is built in.
- Built the unchanged A1 compact map to
  `/workspace/scratch/condenser-A2-baseline/combined_A1.blend`. Build log confirms
  D01 opened 29, pump-feed curve points 8, west escape cut 4, roof slab lowered,
  ground opening 1. No zero condenser count.
- Rendered and inspected `renders-A2/baseline-map/OWNER_A1.png`, 1920×1080,
  32 samples, eye (1.6,3.9,-4.4), target (6,10.3,-4.8), lens 16 mm. Used the
  unchanged `combined/render_views.py`, mine hidden, original map color setup.
  A1 render took about nine minutes; its orange patterned walls and supports are
  plainly visible. Baseline scripts/reports copied outside the repo for comparison.

## R1

- Built directly from `module.blend`: 386,490 triangles, source bytes unchanged.
  Native checkpoint `checkpoints-A2/A2-R1.blend`, receipt and builder snapshot.
- All six byte-identical saved-scene audits PASS via isolated temporary copies;
  reports are under `A2-R1/room-audits/`. No R34 evidence or architecture file was
  overwritten. Separate cold inventory also measures 386,490 triangles.
- Three 960×540, 16-sample previews inspected (AAA01, C02, C10): distinct metal
  and paint; wall camouflage gone; lighting too even. No independent scores.
- Full 22-view 1920×1080, 32-sample batch completed (68m20s). Contact sheet,
  hero and material close view inspected. Initial surface pass remains too even;
  this is diagnostic evidence, not independent acceptance.
- Initial CLI `--cycle` collided with Cycles add-on argument abbreviation. Raw
  failed log retained. The builder now uses `--finish-pass`.

## R2 and R2b checkpoints

- R2 adds actual 8 mm-deep, 24 mm-diameter formwork sockets (12 each on east and
  west walls; all y≤7.2, away from the escape-door band). Factory wear stays on
  handled parts. Floor coating polish is confined to the measured lanes.
- R34 light rig tuned by zone: stronger machinery/task keys and lower general
  fill. Gallery light names retained. New open-channel fixture meshes work with
  the map's existing -0.12 m LIGHT-only patch and are clamped to the inherited
  suspension posts. Both assemblies have registered 1 mm target contact anchors.
- The published A1 map performance report counts 422,140 condenser triangles,
  although the native A1/source count is 386,490. Additional reserve is obtained
  only from tiny washer/shank meshes; the eight audited chest stacks are excluded.
- R2: 358,666 triangles; all six room audits PASS.
- R2b: 351,482 triangles; all six room audits PASS; zero changed non-light
  object matrices. Caps all light positions below 5.55 m. Trims six existing
  exterior overhangs to the roof footprint while retaining inner planes, D01 stub,
  original transforms and all port markers. Evidence labels are immutable.

## Height interpretation

The brief asks to retain R34 layout, the 2 m gallery audit and the roof/U04 mate,
and also caps all visible geometry at z5.6. The original gallery deck is z3.9;
its audit probes to z5.98. The map's prescribed roof underside is z5.695. Those
structural requirements cannot literally coexist with a universal z5.6 cap.
An optional clarification was sent. The working interpretation retains the
structural roof/U04 mating geometry and applies the lower cap to fixtures and
new finish details. This interpretation must remain disclosed; silence is not
an owner approval or an art acceptance.

## R2 planning snapshot (superseded by subsequent entries)

- Finish and inspect R1 full set; iterate full camera cycles and cold comparisons.
- Supplemental seven-view sets, neutral/checker material evidence and full-size
  detail crops. Current supplemental controller reuses the original scripts.
- Promote the refined checkpoint to `module_aaa_A2.blend`; change only the
  authorized condenser source line in `build_compact_map.py`.
- Final map check chain after corrections (one map Blender process at a time),
  owner A2 view and exact A1/A2 comparison.
- Independent ten-category review after the checks; final records, root condenser
  row, COMPACT_MAP/ASSEMBLY_REPORT additions and production TASK_STATE note.
- Commit/push and exactly one draft PR. Do not merge this task.

Frozen original source, A1, accepted snapshots, contracts, other rooms, front end
and combined-map scripts remain unchanged. No Unity engine or FPS run is claimed.

## R2b assembled diagnostic gate — FAIL

Original map tools all ran sequentially; exact commands in map-R2b/commands.json.
Normal walk 17/18 (existing cart route failure), colliders 10/10, meltdown 20/20,
normal and collider closed doors 13/13. Evacuation: two condenser routes and no
single-door cutoff. Doors: 45, zero flagged. Scoped export: 202 objects, re-import
PASS. Map performance: 387,990 condenser triangles. Overlap pair/height comparison:
no new condenser pair. This is not an all-clear report of inherited contacts.

Two actual failures remain recorded in map-R2b/pass-values.json: a new 4-sample
NorthWall/turbine floor pair, and interior clipping 18.5%. All other required
condenser lighting views pass; inherited spine_mid remains hot. There are 25
views in the actual main script, not 30. No failed gate was relabelled a pass.

## R3 / R3a correction

R3: a 1 mm erection joint at the existing north-wall top eliminates the new
coplanar floor-pair report; no original object transforms move. All six room
audits PASS. R3a also lowers the ivory reflectance and selected machine/general
wash levels to address assembled highlight clipping. Fixture/task contrast and
walk-lane readability are retained. Refined mineral tone is a packed 0.24 m map,
limited to ±5.5% value. Empty ceiling material slots filled with mineral concrete.

R3a all six saved-room audits PASS; quick original floor audit now matches the
baseline 40 pair keys exactly. Required four-view lighting rerun is in progress.
Neither R3 nor R3a has independent art scores yet. Final full-map run is pending.

## R3 calibration results and frozen R3d

Original four-view lighting reruns: R3a interior clipping 12.4%; R3b 6.8%;
R3c 5.3%. Those stages FAIL and retain their actual images/logs. R3d lowers
only selected frontal/practical keys again; all four required views now pass.
Inside median0.732, near-black0.001, clipped0.049; D01 clipped0.031, escape
tunnel0.000, stair bottom0.018. Stronger brief near-black15% bar also passes.

Final native R3d SHA256 `aca38967ff20cc38ce3493497165b277f94ea5cca350a47a45d27c9e056d10b1`.
All six original room audits PASS; 351,482 native evaluated triangles. Builder
default now reproduces R3d from R34. New packed mineral-tone map remains within
±5.5% at a 0.24m repeat. Master, receipt and immutable checkpoint saved.
Source-constraint report is scoped: footprint/light caps/name/matrix checks pass,
but explicitly lists inherited structural height exceptions. No universal-height
or assembled-gallery headroom pass is claimed. Optional reach work not done.

Complete final original-tool map queue started in map-R3d. Build log is copied
from the actual immediately preceding R3d build, not presented as an extra build.
Full camera cycles, supplemental/cold evidence and independent scores still pending.

## R3d complete map gates — PASS (scoped)

All11 queued original tools completed, plus the immediately prior actual map build.
Pass-value audit: normal17/18/cart only, colliders10/10, meltdown20/20, closed13/13
(normal and proxy modes); evacuation2 routes/no single cut; doors45/0; floor40
keys exactly baseline, no new condenser overlap pair; map387,990tri; export202
objects/re-importPASS. Lighting24/25, only inheritedspine_mid; allfour condenser
views meet stronger15% black and5% clipping bars. Full details map-R3d/pass-values.json.
This does NOT erase the recorded structural-height/gallery-headroom exception.

## R3e pre-render construction correction

Code inspection identified inward mesh-face winding in the four newly made lamp
frame/diffuser meshes. Measured signed volumes were negative at R3d and positive
at R3e; all four have zero open boundary edges. No object transforms, materials,
lighting or triangle counts changed. Evidence: fixture-normal-correction.json.
R3e SHA256 f95b2ec895ea12619ca9d4bcc37b6901c924e754b472b692a2e0f49c6e97dd2c.
Allsix saved-room auditsPASS. Immutable checkpoint promoted byte-for-byte to
module_aaa_A2.blend; receipt records promotion. Master is now R3e. New final map
build and complete map gate rerun pending. No final art acceptance yet.

## R3e final numeric map gates — PASS (scoped)

Final exact original-tool chain completed. The environment restart interrupted
lighting after 21 frames; its interrupted raw log is retained. Resume verified
unchanged native/map hashes, skipped only recorded exit-zero commands and reran
all 25 lighting views in a fresh process. All 11 commands have recorded exit0.
Pass-value audit PASS: normal17/18 (cart only), colliders10/10, meltdown20/20,
closed13/13; condenser2 routes/no single cut; doors45/0; floor40 keys match
baseline/no new condenser intrusion; map387990tri; export202/re-importPASS;
lighting24/25 with only inheritedspine_mid, requiredfour satisfy15%black/5%clip.
Source structural height/gallery-headroom exception remains disclosed. Owner
full-size A2 view and subsequent room evidence queue are running. No independent
art scores or Unity runtime claim.

## Evidence recovery after second environment/tool refresh

The attached R2 producer was terminated after20 of22 full-size frames. Its exit
is unknown, not PASS. Original frames/manifests/logs and collector source before
resume support are preserved in restarts/R2. The original section renderer
already supports appending missing cameras with strict same-native/backend/settings
checks. A2 collectors now expose explicit resume, verify original PNG hashes and
render only missing cameras; per-image producer PIDs remain genuine. Final R3,
R4 and cold sets will use the same updated collector version. Actual Linux
priority is recorded as NICE10 (the original generic CPU IDLE label remains only
in archived raw partial/history evidence). One detached sequential worker
continues the queue, monitored through raw logs and its recorded PID; no source
geometry/material/light or numeric tolerance changes. No independent scores yet.

R2 full22 complete at1920x1080/16samples; all22 actual frames individually
inspected by builder. Twenty from the interrupted producer, two new resumed
frames; original PNG hashes/PIDs retained. This is diagnostic R2b, whose map
gates FAIL; no independent acceptance or cold pass is claimed for R2. Final
R3 batch starts against the frozen f95b2e... native.


## Owner palette correction — 2026-10-15 (R5)

R3/R4 and cold-R4 full22+7 sets actually completed. All four original numeric
comparisons PASS; exact results remain in final-comparisons/commands.json. This
is reproducibility evidence, not art approval. The owner rejects this finish
as flat/uninspiring, with too much teal/cream, and requests machinery colors.
No independent art scores or PR were issued for it.

R5 is rebuilt from frozen R34 using the same permitted geometry steps. Deep
machine-blue shell/chest, oxide-red waterboxes/pumps, graphite hotwell/framing,
neutral-gray service pipes, quieter neutral mineral walls/floor, exposed metal
fasteners and restrained yellow access/controls. Light spectra are neutralized
while energy/positions retain the calibrated R34-derived rig. CD-01 screenprint
is light for contrast against blue. Owner palette direction supersedes the old
ivory-panel preference; all other rubric gates are unchanged. Geometry remains
351482tri, original non-light matrix changes[]; previous master R3e is retained
as immutable checkpoint. New receipt lists all material assignments.

Preview batch R5 starts with C02_HERO/AAA02_PUMPS/AAA03_OPERATOR at1920x1080,
16spp. New room/map/full/stability/cold checks and independent review are pending;
R3e passes are not offered as R5 passes.

R5 three-frame preview completed and all three actual full-size images inspected.
Proceed with full evidence. Allsix saved-room auditsPASS against1f63a0c...;
source footprint/light/name/matrix checksPASS with the same260 inherited upper
extents explicitly disclosed. New map build now runs. No independent scores.

Main advanced to82c29117 during R5 map checks (cafeteria PR106). Stopped the old-base
worker; partial logs retained as map-R5-main70d93dd6-interrupted, no final pass.
Fast-forwarded the same task branch, preserving all PR106 changes. Generated
map/export/report stash conflicts resolved to new main inputs, then rebuild.
Only condenser source tuple differs in combined scripts. New-main committed
validation baseline retained; fresh map queue includes30lighting views.

R5 updated-main full numeric map gatePASS. Exact11tools completed plusbuild.
Main82c29117 retained cafeteria revamp.30lighting renders/29stockreadable, only
inheritedspine_mid; requiredfour strongerlimitsPASS, insideclip.023/median.579/
black.001. Walk17/18/cartonly, proxies10/10, meltdown20/20, closed13/13;door45/0;
condenser2routes/nosinglecut;floor40samekeys;nonewcondenseroverlap;387990tri;
export202/reimportPASS. Actualcommandsandrawlogsmap-R5. Exactowner16mmlens
mapviewnowrendering. Fullnewcamera/stability/cold/independentscoresstillpending.

R5 full-pack append failed before rendering (exit1): original renderer guard
expects its generic CPU priority IDLE but completed preview metadata correctly
records Linux NICE10. Native/map remain unchanged. No guard or threshold bypass.
Preserved three preview PNGs/manifests intact as R5-preview, with their genuine
producer PID. Full R5 will be rendered anew in one process, not relabelled.
The failed invocation/log remains in palette-revision-R5/commands.json and its
archived R5 log; explicit retry records the repair and keeps the nonzero attempt.

R5 fresh complete22-camera batch finished with actualexit0. All22 actualfullsize
PNGs inspected by builder; per-image native/hash/PID records retained. No relabelled
preview frames. Supplements running; firstfour opened. Independent Codex critic
begins diagnostic warm-pixel inspection, explicitly with no scores/acceptance
until complete cold evidence. Stable/cold queue will hold after diagnostics for
any consequential corrections; no old R34 scores inherited.

2026-10-15 R5 independent warm diagnostic: all22+7 plus owner and four material diagnostics actually inspected by independent Codex critic. Machine palette materially stronger; no numeric scores/cold acceptance. Critic identified coarse CW pipe profiles and rotated-face texture-axis mismatch. R5 stability/cold queue deliberately stopped before those stages; retained actual warm/diagnostic successes and append failure. R5b rebuilt from frozen R34 with 14 round pipe profiles and explicit world-frame triplanar repeats, 360522 native triangles, original nonlight matrices unchanged. New checkpoint promoted byte-identically; preview/new checks pending. No waiver for assembled gallery headroom or overhead reach.

R5b focused previews: S02 completed exit0 and inspected; C02/W03 completed and inspected before style-preview producer exit1 on mistyped third camera AAA01_COOLING. Actual logs/exit retained. Correct AAA01_WIDE_NE queued in separate new preview label; canonical full camera pack remains fresh and unchanged. No render/priority guard bypass.

R5b material diagnostic first attempt exit1 after neutral board: Blender CLI does not add the script directory to sys.path, so shared projection-helper import failed. Native was untouched; partial board and raw failure preserved under material-diagnostics-R5b-import-failed. Added explicit local module path in diagnostic only; fresh diagnostic retry queued. Captions now visible on all15 front faces in actual neutral board.

Corrected R5b canonical material diagnostics completed exit0; all4 actual images opened by builder and independent critic. Rotated cap/flange checker fields now show squares; triplanar transitions disclosed. All15 captions visible. Fresh six original saved-room audits PASS and scoped constraints PASS with inherited upper-height exception; combined map rebuild/checks running.

R5b map build exit0 and all named patch counts positive, but original perf_report measured406070 triangles; queue stopped FAIL_BUDGET before other map tools, owner, or full warm/stability/cold. No threshold changed. Read-only saved-source probe shows634 tiny washer/shank meshes retain55352 triangles at0.60decimate. New R5c lowers the pre-profile reserve target343000 (same selected tiny meshes; eight audited steam-chest stacks/head geometry remain intact), retaining all14 improved round pipe profiles and all world-frame material fixes. R5b remains immutable failed-budget evidence.

R5c actual map performance395482, below400000; all named patch counts positive. Native349678. Normal visual-mesh walk17/18 with only baseline cart failure, closed doors13/13. Remaining original map chain and fresh full renders still running. Metadata follow-up identified gallery_fixtures.bounds in builder receipt comes from cached pre-update bound_box, while saved evaluated source check confirms all new fixture/lens geometry below5.6. Constraint helper now records evaluated fixture bounds (numeric policy unchanged); rerun it once AFTER current sequential worker exits, retain command/exit/native hash and amend only derived receipt bounds with the measured proof, preserving cached values under explicit label. Do not launch a concurrent Blender while the map worker runs. Actual R5c builder archived under palette-revision-R5c/builder-R5c.py.

R5c all11 original map commands exit0 and exact pass-value audit PASS. Actual395482tri,17/18normal (baselinecart),10/10proxies,20/20meltdown,13/13closed,45doors0flags,2condenserexits/no singlecut,40floorpairs unchanged/no newcondenseroverlap,202FBXroundtripPASS,lighting29/30 only inheritedspine_mid. Fourrequiredstronglimits pass; interior median.577/black.001/clip.022. Exact owner32sample view now rendering; full warm/stability/cold queued, not yet passes.

Evidence-layout repair: cooling-isolator lossless crop now uses actual supplemental S02 (full width below banner), which contains both complete wheels/gauges, instead of ceiling-focused C06 whose frame cuts valve bodies. No source, renderer, camera or numeric comparison changes; original pixels and crop provenance retained.

Current R5c full22main completed exit0 in2639.55s, all22 actually opened by builder and independent critic. DIAGNOSTIC_R5c.md records no new major finish defect and no obvious fastener seating regression from.48 reserve. Existing minute notes and binding headroom/reach conflicts retained. Supplements/material/stability/cold remain incomplete; no scores or acceptance.

R5c warm supplements7/7 completed exit0; builder actually opened every current22+7 full-size image. Rebuilt original-pixel review crops (pack_A2_review.py R5c --owner --owner-label owner-map-R5c exit0); independent critic inspecting all7 supplements/crops. Current material4, R6c and cold-R6c still pending, no final scores or acceptance.
