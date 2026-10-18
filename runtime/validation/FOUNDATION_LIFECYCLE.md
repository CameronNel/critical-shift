# Foundation startup and shutdown repair

**18 October 2026 â€” scoped native lifecycle validation Passed; independent
acceptance pending.** The completed foundation
[report](../out/wp01-2kda5zu2/report.json) records all nine declared PlayMode cases
passed, alongside 12 EditMode cases, preparation, build and Player. The active
continuation is the
[sandbox checkpoint](GAMEPLAY_SANDBOX.md#completed-sandbox-gameplay-checkpoint-2005-utc).

Original authorized scope was lightweight coding while Cameron played, with
Unity/compilers/tests/imports prohibited. The owner later explicitly allowed
Unity/testing; that earlier restriction is historical and did not apply to the
completed run. Primary author: Codex; independent reviewer unassigned.

- Base: `27feed80e71638c7dc29f5a44564de6fa1a65a94`.
- Original branch: `codex/unity-foundation-lifecycle`; current continuation is
  `codex/unity-gameplay-sandbox`, [draft PR #111](https://github.com/CameronNel/critical-shift/pull/111),
  not self-merged.
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

The owner selected URP on 15 October. The current native foundation uses URP
17.4.0 and native-created rendering assets/settings, with the exact pinned
editor's resolved Test Framework 1.6.0 / ext.nunit 2.0.5. The original lifecycle
repair did not select or install that migration; its subsequent validation uses
the current selected profile. Renderer/gameplay evidence remains separately
bounded in the linked sandbox checkpoint.

## Acceptance and validation status

The seven added lifecycle cases below are now **Passed**, within the completed
nine-case [PlayMode XML](../out/wp01-2kda5zu2/PlayMode.xml):

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

The initial source-only stage performed diff inspection, `git diff --check` and
non-launching executable-version inspection; its native checks were then NotRun.
The first licensed [wp01-7vt5fx24 report](../out/wp01-7vt5fx24/report.json) remains
Failed: preparation and 12 EditMode cases passed, all nine PlayMode cases failed
on normal lifecycle logs rejected by `LogAssert.NoUnexpectedReceived`, and
build/Player were NotRun. Commit `c37905f6` added exact expected Ready/Stopped
markers before their emissions, retaining all assertions and the unexpected-log
checks. Foundation bootstrap/test C# is unchanged between that repair and the
successful `6554abef` candidate.

The [completed report](../out/wp01-2kda5zu2/report.json), 20:05:26â€“20:10:52 UTC,
is **Passed** on `6554abef808879191629884048ee6d3df19e4463`: strict package
initialization and separate clean native preparation passed; all 12 EditMode and
9 PlayMode cases were discovered/executed and passed with zero
failed/skipped/inconclusive. Win64 build and the matching Player passed, GUID
`dc6868dac643456b987abce1084c8bb0`; the Player exited zero with 7,720 frames and
zero errors. This Player launch covered successful startup/teardown; its
failed-startup exit20 path was not separately launched. See [WP01.md](WP01.md#completed-native-foundation-evidence-18-october-2026)
for raw XML/log links and the exact evidence scope.

Source remained unchanged, and every selected manifest/lock/cached-descriptor
audit passed. The run used the explicitly recorded preinitialized SDK
Library/PackageCache seed only, not cold extraction; it reused no seed Assets,
Packages, ProjectSettings, other Library folders, ScriptAssemblies or first-party
compiled code. Compilation/preparation/tests/build/Player ran in the disposable
workspace. Earlier licensing and native test failures retain their status.

Map/layout, scenes, authored content, importer, package configuration, gameplay
rules and the pure process implementation were unchanged by this lifecycle
repair. Independent acceptance and review remain pending; the current draft PR
is not self-merged and no roadmap gate is advanced. These results establish only
the declared foundation lifecycle bounds, not human feel, art, performance, map
or full-game acceptance.
