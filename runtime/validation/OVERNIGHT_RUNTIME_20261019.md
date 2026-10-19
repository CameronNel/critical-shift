# Critical Shift overnight runtime handoff, 19 October 2026

PR #111 is repaired and merged at `98ef79d4cb1e0acaa6d5131245f9b5ed1fbe7509`.
Continued game development is in the bounded draft stack below. Root authored
all changes; independent ultra agents reviewed ownership, timing, medical,
physical integration, models, retained evidence and main compatibility.
Review findings were implemented and checked by the same author. The work extends
the isolated local gameplay fixture; current native execution remains unverified.

## Resulting gameplay

- A twelve-minute shift has preparation, three demand windows, warnings,
  shortfall feedback and a retained causal debrief. Authored initial stock can
  satisfy the full contract through the safe route.
- Medical rescue has exclusive body custody, whole-rig chamber placement,
  powered timed stabilization, finite cartridges, patient discharge and a
  separate standing recovery. Current access and injury deadlines remain
  authoritative; a chambered alert patient can request its own egress.
- Workers receive bounded contamination from authored exposure/wash zones and
  currently held dirty cargo. Current PPE reduces exposure; cooldowns survive
  drops, handovers, conversions and washing. Fitting and removal take shift time,
  keep prior gear until completion and interrupt on access/state loss. Worn suits
  apply the authored walking cost while retaining existing carry/air/cart rules.
- Ore washing lowers contamination and produces wet ore; drying conditions it
  before the existing crusher/processor/fuel route. Both preserve quantity,
  cause, parent lineage and inherited inspection flags. Jam clearing is timed,
  keeps process work frozen and requires isolated power.
- New production cycles debit the single shared reserve once. Finite black-start
  backup can recover depleted reserve. Core output can be routed to grid,
  reserve or the balanced split; completed quanta, demand endpoints and spill
  remain conserved. Cooled shutdown fuel can explicitly be discarded as spent
  material to load fresh fuel, forfeiting all remaining time without power generation or
  refund. Current readouts explain interlocks, costs and the next useful action.
- Deadline settlement, stale/replayed intentions, cleanup and retained fault
  evidence were repaired. Committed owner facts survive a later settlement
  failure; lease expiry prepares a complete batch before release. No second
  inventory, energy or worker-state writer was introduced.

These are authored prototype rules, not accepted production balance. The changes
add no transport, Steam, voice, save system, map/room art or new framework.

## Review and merge map

All continuation PRs are drafts pending independent maintainer review/merge.
The repository's [AGENTS.md](../../AGENTS.md) and
[GAME_SPEC32.6](../../design/GAME_SPEC.md) require one author/task branch and no
agent self-merge. The owner's explicit merge instruction was applied to PR #111;
it does not silently waive the rule for this later stack. No confirmation was
requested while the owner slept.

| PR / current head | Change | Tests / scenarios | Base |
|---|---|---:|---|
| [#113](https://github.com/CameronNel/critical-shift/pull/113) `567a8fc6` | Shift demand and causal debrief | 767/15 | main |
| [#114](https://github.com/CameronNel/critical-shift/pull/114) `2f247020` | Powered medical stabilization | 812/18 | #113 |
| [#115](https://github.com/CameronNel/critical-shift/pull/115) `523f4274` | Full-contract sandbox stock route | 818/18 | #114 |
| [#116](https://github.com/CameronNel/critical-shift/pull/116) `c79ce7a8` | Exact worker deadline settlement | 824/18 | #115 |
| [#117](https://github.com/CameronNel/critical-shift/pull/117) `4848041a` | Independent medical endurance model | 824/18 | #116 |
| [#118](https://github.com/CameronNel/critical-shift/pull/118) `aa1bffa5` | Compact objective feedback | 831/18 | #117 |
| [#119](https://github.com/CameronNel/critical-shift/pull/119) `483b577a` | Medical egress admission | 839/18 | #118 |
| [#120](https://github.com/CameronNel/critical-shift/pull/120) `50df95cf` | Worker contamination and PPE | 878/19 | #119 |
| [#121](https://github.com/CameronNel/critical-shift/pull/121) `94f991dd` | Finite emergency black start | 906/20 | #120 |
| [#122](https://github.com/CameronNel/critical-shift/pull/122) `5814b7e3` | Safe ore drying | 925/21 | #121 |
| [#123](https://github.com/CameronNel/critical-shift/pull/123) `6a43dfdf` | Timed suit fitting | 965/22 | #122 |
| [#124](https://github.com/CameronNel/critical-shift/pull/124) `cf2508bf` | Physical contamination/wash zones | 983/22 | #123 |
| [#125](https://github.com/CameronNel/critical-shift/pull/125) `6b4587ba` | Operational machine guidance | 1003/22 | #124 |
| [#127](https://github.com/CameronNel/critical-shift/pull/127) `d8e59d79` | Timed isolated jam clearing | 1022/23 | #125 |
| [#128](https://github.com/CameronNel/critical-shift/pull/128) `b819189d` | Shared production reserve costs | 1046/24 | #127 |
| [#130](https://github.com/CameronNel/critical-shift/pull/130) `3f0be906` | Physical medical rescue adapter | 1062/24 | #128 |
| [#131](https://github.com/CameronNel/critical-shift/pull/131) `2f7f7933` | Suit walking tradeoff | 1068/24 | #130 |
| [#132](https://github.com/CameronNel/critical-shift/pull/132) `7fe6af1d` | Ore washing and safe dirty route | 1096/25 | #131 |
| [#133](https://github.com/CameronNel/critical-shift/pull/133) `6b343cce` | Current dirty-cargo exposure | 1121/25 | #132 |
| [#134](https://github.com/CameronNel/critical-shift/pull/134) `d6584d01` | Core output routing | 1154/26 | #133 |
| [#135](https://github.com/CameronNel/critical-shift/pull/135) `25ed108c` | Timed suit removal | 1183/27 | #134 |
| [#136](https://github.com/CameronNel/critical-shift/pull/136) `7fa3ad90` | Safe partial fuel discard | 1208/28 | #135 |
| [#137](https://github.com/CameronNel/critical-shift/pull/137) `a26b976b` | Fault evidence and atomic lease expiry | 1219/28 | #136 |

Merge in dependency order; each PR's base is the preceding runtime branch.
External PRs #112, #126 and #129 are not this work. Read-only comparison of live main
`c7e69f0a` and runtime tip `7fa3ad90` found no overlapping changed paths from
`98ef79d4`, no package/asmdef/settings/serialized-scene conflicts, and 214 unique
runtime GUIDs in the virtual combined tree. This was source inspection, not a
native merged build. Keep main's map/sky additions. Later fault changes touch runtime and the architecture validation plan; they
do not add a map overlap. Root also constructed a clean virtual merge at tree
`d9a4c9f6651cfcf626fb101c93ac7d6d1dd48fc8` and exported its scoped runtime:
static checks passed 214 GUIDs/21 asmdefs/135 C# files. This is still source only;
[the checkpoint](evidence/merged-source-20261019.json) records exact inputs.

## Exact final source checks

Final tested source `5d2c39733659ee0fa5a05a05a71ad3c5bc8366c7`: **1,219 executed/passed,
zero failed/skipped;28 versioned scenarios each twice**. The verifier built the
actual C# 8/netstandard2.1 libraries and .NET 8 runner, reconciled exact discovery,
checked report safety and rejected the deliberately failing NUnit/scenario
checks, all 13 logical controls, and attempted report overwrite. Seed 55 was
re-executed successfully; this is deterministic seed reproduction, not a claim
of byte-identical trace output. All 285 recorded inputs match the
specified git tree. Nine gameplay DLL hashes match its frozen closure.

The final frozen seed 20261066 passed 10,000 mixed cases and 15,604,834 selected
operations/model checks in 40.1065863 seconds. It exercised the final normal gameplay
composition separately from the injected fault cases and from duration accounting.

The last fault fix has 11 focused cases. Eight owner-prefix regressions fail on
pre-fix `7fa3ad90` and pass after the fix; two additional lease atomicity cases
also fail before the fix. The post-journal failure case guards against duplicate
publication. Baseline tests omit only the newly added typed-production property
assertion, because the property did not exist before the fix. These are injected
failure witnesses, not claims that normal players can exhaust 64-bit revisions.

Python runtime tooling: 182 passed. Static source metadata/declared boundaries
passed (204 GUIDs/21 asmdefs/133 Unity/package C# files at the latest checkpoint).
Supplementary parsing checked 79 Unity-side files under C# 8 with zero syntax
errors. Neither check resolves Unity references or establishes native behavior.
Frozen results, scenarios, TRX and controls are retained in the evidence files.
All 23 PR inventory counts and the current-head Windows/Ubuntu successes were
reconciled at 14:01 UTC; the exact [PR checkpoint](evidence/pr-checkpoint-20261019.json)
and [inventory/ancestry audit](evidence/pr-inventory-20261019.json) retain revisions.

## Eight-hour accounting

The continuation began at 21:23:22 UTC on 18 October 2026. A failed/interrupted overnight probe
and the idle gap before resumed work at 05:36 UTC on 19 October are excluded. Useful
implementation, review and verification continued through this handoff. For
conservative completed probe accounting, only sequential 45-second children with
observed process exit code 0 and validated final `Passed` reports are counted.

**28,800.954 completed logical-probe seconds**, across 640
accepted chunks and 10 preserved build closures, exceed 28,800 seconds.
The probes completed 11,404,886 mixed cases and 11,914,594,716 selected
operations/model checks. These are aggregate probe cases/checks, not distinct
assertions, unique seeds, commits or successful player actions. Selected checks
include inapplicable operations and state observations.

| Source closure | Accepted chunks | Seconds (rounded) | Mixed cases |
|---|---:|---:|---:|
| `0f386de5` | 34 | 1,530.026 | 991,120 |
| `2f247020` | 43 | 1,935.049 | 1,202,756 |
| `4848041a` | 158 | 7,110.189 | 3,315,186 |
| `32ed08ce` | 93 | 4,185.107 | 1,765,721 |
| `5e6847da` | 42 | 1,890.055 | 644,001 |
| `278c38d2` | 48 | 2,160.125 | 683,107 |
| `4841a03e` | 65 | 2,925.106 | 904,218 |
| `b4d74ef3` | 54 | 2,430.101 | 699,742 |
| `0d827463` | 46 | 2,070.076 | 544,087 |
| `91df0439` | 57 | 2,565.120 | 654,948 |

The index retains the reported subsecond values and full nine-DLL hashes.

This is not one eight-hour process, one unchanged build, native playtesting or a
measurement of continuous authoring time. Each series belongs only to its
recorded source and nine-DLL closure; earlier hours do not validate later edits.
The latest 1,219-test revision is recorded separately from the duration series.
The first interrupted 600.001-second report and unacknowledged final children in the
first two supervised series are excluded entirely. No failed control contributes
time. Accepted UTC probe intervals were independently checked for overlap.

See the [duration index](evidence/overnight-logical-20261019.json) and
[compressed raw records](evidence/overnight-logical-20261019.jsonl.gz), including
source hashes, closure hashes, raw reports, accepted exits, PR/native checkpoints
and the final supervisor result. The separate final execution archive includes
raw TRX, 13 logical control reports, exact scenarios, the frozen 10,000-case report and
pre-fix fault-regression results. Archive hashes and scope are in
[evidence notes](evidence/README.md).

## Native readiness and next useful work

Pinned Unity 6000.4.3f1 was unavailable locally; its official Linux download probe
returned proxy 403. The configured Desktop Commander machine remained Offline
at the final check. No login, activation bypass or replacement editor was used.
Current native catalogue: **179 authored cases, all current execution NotRun**.
No current Unity import, PlayMode, physics, rendered controls, Player,
performance, multiplayer, feel or art acceptance is claimed. The historical
132-test native pass belongs only to `6554abef`, not this continuation.

On an activated pinned editor host, run the existing runner from repository root:

```sh
python runtime/tools/run_sandbox.py --unity /absolute/path/to/Unity --target Linux64 --build-player --run-player
```

Use Win64 on the corresponding host. The separate foundation runner covers its
own assembly selection and should also be run for a full native project check.
Preserve the fresh evidence directory and
its exact source/profile identity; a new run must pass inventory reconciliation.
Then inspect the rendered fixture controls, whole-body chamber clearance and
free discharge, suit fitting/removal/mobility, zone/cargo exposure, washer/dryer
sockets, route switches and spent-fuel physical release. Run the full authored
shift route and failure recovery with actual physics. Performance and multiplayer
remain separate gates. See the [fixture guide](../unity/Assets/CriticalShift/Sandbox/README.md)
and per-feature validation notes; do not infer native readiness from offline CI.

The exact workflow packaging script also produced a clean local bundle from
the verified frozen binaries. Fresh extraction passed the safe dirty-ore and
fuel-discard scenarios twice, mixed seed 55, and unchanged-byte report-overwrite
rejection. All 41 members and 285 input hashes were checked. The CI artifact
download itself was blocked by storage 403; this local result does not claim
the downloaded CI bundle ran. See [package evidence](evidence/packaged-runner-20261019.json).

For editor-free reproduction:

```sh
python runtime/tools/check_source.py
python -m unittest discover -s runtime/tools/tests
python runtime/dotnet/tools/verify.py
```

Use a stable .NET 8 SDK allowed by `runtime/dotnet/global.json`; this local
execution used8.0.423. Verification outputs are ignored derivatives; source and
inventories remain versioned. No roadmap
acceptance gate advanced and no claim of 100% perfection is made.
