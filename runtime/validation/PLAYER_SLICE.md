# Local playable interaction slice

User-authorized implementation, 10 October 2026. Base: `bb6b4924849d38097ee629a6fa2c00dc1b56095f`.
Branch: `feat/player-interaction-slice-20261010`. Primary author: Codex. Independent review and maintainer merge are pending.

## Scope and decisions before implementation

Implement one isolated Unity fixture: start/reset/end a local shift, first-person movement,
aimed interaction feedback, exclusive carrying and placement, protective equipment attachment,
and sitting/standing. Reuse `WorldSession`, `InteractionWorld`, and `WorkerState` as the writers.
Seat occupancy is an existing exclusive claim; worn equipment occupies an existing custody slot.
Player workflows coordinate these facts without introducing a second inventory or worker owner.

D-03 working fixture decision: Unity's built-in legacy keyboard/mouse input module and IMGUI
feedback, behind the local player controller. Add only built-in physics/input modules. No new
networking, UI framework, Steam, voice, renderer, persistence, or transport package is selected.
This is a local host fixture; contending authenticated actors in rule tests are not network peers.
The user's authorization permits this source implementation while native prerequisites remain
blocked; it does not advance any roadmap gate or waive independent review.

D-09 fixture: retain the existing 256 receipts/connection, 3-second claims, 1-second maximum
renewal interval, and four-actor limit. A seat requires empty hands; carrying while seated and
two-person carrying are outside this slice. A protective item attaches immediately for testing;
the full 15–30-second suiting procedure, upgrades, radiation protection and character animation
remain separate gameplay work. Movement and suit/carry slowdown values are provisional feel
settings, not accepted balance or measured performance.

Unity consumes DLLs built from the canonical `runtime/dotnet` projects. Generated DLLs and
their metadata are ignored and reproducible; there is no copied implementation. A dedicated
player fixture/editor assembly and scene generator preserve the foundation fixture and authored
Blender/map files. No existing serialized source identities are replaced; new identities get
metadata. No deletion or migration is required.

## Contracts and acceptance

A02/A05/A06: explicit application/Unity/editor boundaries, bounded setup, and idempotent cleanup.
S01–S04/S07: one writer, authenticated commands, revisions/leases, replay-safe side effects,
seat and suit dimensions, cleanup on impact/expiry/disconnect/stop. H04/V00: paired metadata,
honest source/API compilation versus native evidence. CMD/HOLD/WORKER/LIFE/SHIFT tests apply.

Required checks: existing offline verifier and negative controls; added player contract tests;
Unity API compilation against the pinned editor; static metadata/ownership checks; implemented
native fixture checks for physical bindings and movement. Unity import, PlayMode, Player build,
human feel review, map integration, and multiplayer acceptance require their actual prerequisites.
Results are recorded after execution; no gate is declared passed by this task note.

## Execution evidence — 10 October 2026

Executed against the working tree based on the SHA above; the verifier's source fingerprints
identify tested canonical files (its `commit` field is the pre-commit baseline). The PR head
records the committed source. Generated logs and binary outputs remain in ignored workspace
artifacts; no native success or independent approval is inferred from them.

| Check | Result and actual scope |
| --- | --- |
| `cd runtime/dotnet && python tools/verify.py` | **Passed**: 708 discovered/executed/passed, 0 failed, 0 skipped, including 20 player tests. All 12 versioned scenarios passed twice with exact expected steps/assertions. Expected failing NUnit, mismatched/empty scenario and report-safety controls behaved correctly. SDK 8.0.425; netstandard2.1 / C# 8 canonical libraries. |
| `python runtime/tools/prepare_player.py` | **Passed**: 8 canonical Release DLLs generated with explicit importer metadata and source/destination fingerprints. Build: 0 warnings/errors. |
| `check_player_api.py --editor-root …/unity-6000.4.3f1 --out runtime/out/player-api-final-reviewed` | **Passed**: 4 assemblies, 8 authored C# files, warnings treated as errors against the actual pinned editor's engine/editor/Standard/NUnit DLLs. API compilation only. |
| `python runtime/tools/check_source.py` | **Passed**: 46 metadata GUIDs, 9 asmdefs and 14 C# assets, including ignored generated imports. No orphan/missing/duplicate metadata or unowned C# source. |
| Diff/linked documentation | **Passed**: `git diff --check`, local documentation links and author self-review. No authored map/Blender, foundation script/catalogue, workflows or credentials modified. |
| Native Unity player-scene preparation | **Blocked**: exact 6000.4.3f1 editor exited **198** before import: `No valid Unity Editor license found. Please activate your license.` |
| Native PlayMode | **Blocked / NotRun**: seven implemented physical binding/movement/reset tests compiled but did not execute. No native results XML exists. |
| Desktop Player, human feel, map binding, remote peers, performance | **NotRun**; native build requires activation, and other acceptance needs the corresponding authored assets, runtime/hardware and review. |

Canonical import source fingerprint: `fa19394ed173a131c716e130c5115acd0cd0a6115307f41cd0d3b343eece4ca0`.
Unity player source fingerprint: `4d3581f3cd1738830f994d41d1a12b9f975327821e0acbddcb08ae31862c9967`.

Logs/reports: `dotnet/artifacts/summary.json`, `dotnet/artifacts/player-verification-final.log`,
`out/player-import-final.log`, `out/player-api-final-reviewed/player-api.json`, `out/player-source.json`,
`out/player-native-probe.log`. Initial API attempt in `out/player-api/` failed due to namespace
resolution of `Application`; it was corrected to explicit `UnityEngine.Application`, and later
attempts passed. That initial failure remains retained, rather than described as an uninterrupted pass.

The changes form one atomic local player slice: command contracts, their sole-owner workflows,
Unity bindings/controls, a reproducible fixture, and verification. Splitting away a required binding
would leave the slice unusable. New scripts and IDs have no pre-existing serialized consumers;
the original foundation fixture remains available. D-01 native acceptance, D-02 transport,
D-03 production UI/remote input, D-09 measured tuning and all existing roadmap gates remain open.
Independent review and maintainer merge are **pending**; this task does not merge its own work.

## Native follow-up — 10 October 2026

Unity Personal was subsequently activated through official browser sign-in. The stacked spawn
task now executes all nine graybox physical cases plus six cases against the current assembled
map: 15 passed, zero failed/skipped/inconclusive, including locker stance and the outfit swap
only at animation completion. A Linux Player build and startup/shutdown check
also pass. See [SPAWN_ROOM.md](SPAWN_ROOM.md) and its compact evidence for current sources,
package corrections, exact commands and limitations. The earlier blocked results above remain
the historical evidence for this slice; human feel, remote peers, performance and independent
acceptance still require review.
