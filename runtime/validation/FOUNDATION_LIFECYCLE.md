# Foundation startup and shutdown repair

**18 October 2026 — source work; native acceptance pending.**

Authorized scope: lightweight coding while Cameron plays. Do not launch Unity,
compile, run tests, import assets or start other heavy work until Cameron says
testing may resume. Primary author: Codex; independent reviewer unassigned.

- Base: `27feed80e71638c7dc29f5a44564de6fa1a65a94`.
- Branch: `codex/unity-foundation-lifecycle`.
- Purpose: prevent the existing foundation bootstrap from reporting Ready after
  failed camera validation, a captured startup error or an explicit stop before
  Unity calls Start. Keep error observations scoped to the running process.
- Owner/lifetime: the existing `ProcessLifetime` remains the only process-phase
  writer. `FoundationBootstrap` owns its Unity log subscription and releases it
  when the process stops. This is not a gameplay-session owner.
- Dependencies: existing ProcessLifetime and UnityEngine only; no package,
  assembly, serialized identity or infrastructure decision changes.
- Changed paths: bootstrap, existing PlayMode fixture, expected native test
  inventory, WP01's current inventory link and this task record. No replacement
  implementation or deletion.
- Contracts: A06, H01/H04/H07 and V00/V01; narrow foundation lifecycle coverage
  related to LIFE-01. Full gameplay lifecycle acceptance remains separate.

## Version and renderer authority

Read GAME_SPEC sections 34.2 and 44.4 alongside ENGINE_DECISION. The spec describes
a candidate stack and requires an explicit version; ENGINE_DECISION selects
**Unity 6000.4.3f1**, revision **39d1a88d4dd1**, matching both
`runtime/toolchain.json` and `runtime/unity/ProjectSettings/ProjectVersion.txt`.
The installed 6000.6.2f1 is not the selected editor. When authorized, native checks
must use `C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe`.
Reading that executable's ProductVersion metadata without launching it returned
`6000.4.3f1_39d1a88d4dd1`, matching the required version and revision exactly.

The owner selected URP on 15 October. The current foundation still contains its
older Built-in checks and no URP package. This repair changes neither renderer
nor package pins; the URP migration remains separate, unvalidated work.

## Acceptance and validation status

Seven new PlayMode cases are implemented, **NotRun**:

1. Stop between Awake and Start: no Ready marker or attempted restart.
2. Stop on an inactive object before Awake: activation cannot revive it.
3. Disabled required camera on activation: one error, stopped state, no Ready.
4. Camera disabled between Awake and Start: same failure before readiness.
5. Error captured between Awake and Start: stopped state and no Ready marker.
6. Error after explicit stop: no retained log subscriber changes the old process.
7. Error while Ready: its error status survives stop; destruction emits no second
   stopped marker.

The bootstrap's read-only `HasErrors` property exposes its existing error flag
for these lifecycle assertions. It is not another state owner. A startup error
uses the same failure shutdown path as invalid camera setup. Errors after Ready
remain recorded for shutdown/smoke failure reporting, as before.

Existing clean startup/reload tests remain in the expected inventory. Repeated
stop and destruction must remain harmless. Failed startup in the smoke Player
must exit with the existing error code 20 rather than wait for the smoke timeout.

Validation performed here is source/diff inspection, `git diff --check` (no
whitespace errors), and reading the installed executable's version metadata.
The declared native inventory is now 12 EditMode and 9 PlayMode cases; these are
expected counts, not discovery or execution results. Compilation, all test
suites, native import, Player build/execution, smoke failure exit and performance
are **NotRun** at the owner's request. No native test discovery or pass counts
are claimed. Once testing is allowed, use the existing disposable foundation
runner described in WP01.md with the pinned editor and Windows target; native
package/license availability still needs checking.

Map/layout, scenes, authored content, importer, package configuration, gameplay
rules and the pure process implementation are deliberately unchanged. Acceptance
and independent review remain pending; this branch is not merged and no roadmap
gate is advanced.
