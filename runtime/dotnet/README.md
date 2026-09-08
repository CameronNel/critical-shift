# Offline interaction implementation

**Task:** OFFLINE-001, 8 September 2026. **Baseline:** `57f15bcb5e879976f6af5465bb1f8bf7116702df`. **Scope:** engine-independent C# implementation and tests, explicitly requested while Cameron cannot use Unity. Independent review and merge are pending. Check the current PR/workflow artifacts for execution results; file existence is not test evidence.

## Responsibility and non-goals

This slice owns exclusive logical object claims and their ordered host command workflow. It prevents duplicate claim changes, stale releases and retained world state. It deliberately does not implement Unity, physical attachment, worker movement/health, materials, machines, mining, saves, input/UI, Steam, voice or a networking transport.

The access-policy interface is the real host observation boundary. There is no permissive production default. TestAccess lives only in the test project. A successful offline test is not proof of authentication, spatial reach validation, connected multiplayer or working physical carrying.

## Local decision: bounded offline prework

The user authorized useful coding without starting Unity. This is a scoped sequencing/source-placement exception to the future `runtime/unity/` layout, not completion of WP-01/WP-02 or Roadmap Gate 0. Those still need the engine/agent tooling, engine ignore rules, actual Unity import/test/Player and CI smoke evidence, plus a bounded agent scene change and inspected errors specified in the roadmap. No production gate advances here.

The two real libraries target **.NET Standard 2.1 with C# 8.0** and have no third-party package dependencies. The .NET 8 SDK is only the offline compiler/test host, not a replacement Unity runtime. The current SDK policy permits stable 8.0 feature/patch roll-forward; every execution records its exact version. Exact Unity compiler, importer, AOT/stripping and Player compatibility remain unverified. The later integration must consume this single source/library or move it atomically; do not maintain copied implementations.

Test-only dependencies are explicitly pinned: Microsoft.NET.Test.Sdk 17.11.1, NUnit 3.14.0 and NUnit3TestAdapter 4.6.0. They are not runtime dependencies or selections for Unity, networking or UI. Python standard-library checks provide graph/result validation without a new production framework. Review this bounded tooling choice with the PR; no unrequested packages are installed on Cameron's computer.

The domain has one exclusive held object per actor in this first slice. This is not an implemented inventory or a final shared-carry design. Registration is setup-only; mid-session join/reconnect and dynamic spawning are not enabled. Default offline fixtures are four connection identities, 128 registered entities, 256 receipts per connection and a 3,000 ms lease. These are testable local configuration, not ratified networking/feel targets for the final game. D-02/D-03/D-08/D-09 remain open for their future scopes.

## Source and dependency map

| Location | Owner / allowed dependency |
| --- | --- |
| `src/CriticalShift.Features.Interaction.Domain/` | ExclusiveClaimStore owns custody, revisions, lease generations and expiry. Base libraries only. |
| `src/CriticalShift.Application/` | InteractionWorld owns this workflow's connection mapping, command admission and bounded receipts. References Interaction.Domain, never Unity/transport. |
| `tests/CriticalShift.Offline.Tests/` | NUnit examples, seeded independent model, public/compiled-boundary checks and an isolated failing control. Never referenced by production libraries. |
| `tools/` | Scoped project/reference validation, result verification and reproducible test entrypoint. Not runtime code. |

No Core assembly is created just to hold unused interfaces. There is no event bus, dependency-injection container, generic transaction framework, filesystem service or duplicated mutable RunState.

## Calling contract

A trusted composition point constructs one InteractionWorld with a **fresh nonempty epoch** and an IInteractionAccessPolicy. It registers stable entity IDs and already-authenticated connection-to-actor mappings, then calls Start. Do not accept registration calls or binding-failure callbacks directly from untrusted network payloads.

Call every operation on the same host simulation thread. This module does not synchronize arbitrary parallel callers. AdvanceTo receives monotonically increasing **unscaled host milliseconds** before processing a tick's commands. Never use client time. Expiration is processed explicitly, not by a hidden timer; process the returned detached changed-state views when an adapter eventually exists.

Commands start at sequence 1 per connection. Use the current entity revision for Grab and the exact granted lease generation for Release/Renew. Accepted and gameplay-rejected next commands both advance the stream. A matching retry returns its historical receipt; changed payload, forward gap and too-old evicted requests do not execute. Retained receipts are bounded and the high-water mark survives eviction.

**Do not drive physical effects from Accepted alone.** Only HasNewCommit indicates a new state change; a replay can report an old accepted state after the object has already been released. Read current projections, compare epoch/revision, and never reattach from a historical receipt. This module reports logical custody only. An adapter must later report actual physical failure for the exact epoch/entity/lease generation and implement its own tested binding lifecycle.

Release does not require a reach check: an object moving out of reach must not trap the holder. Grab and Renew call the supplied host policy. Unexpected policy/integrity exceptions fault the workflow and are rethrown; further commands fail closed until teardown. Routine invalid gameplay requests return typed rejections instead of throwing. No catch-and-ignore recovery is used.

Disconnect clears the actor's current logical claim and connection receipts. Stop is idempotent and clears world-owned claims/registrations/receipts. Recreate the next world with a new epoch; do not reuse a stopped instance or old epoch. Retired IDs cannot be re-registered within the same world, preventing an old lease from targeting a newly created entity with reused identity.

## Run without Unity

Prerequisites: stable .NET 8 SDK, Python 3.10+ and network access for the initial test-package restore. No Unity license, editor, GPU or local game installation is required by this test harness.

```sh
cd runtime/dotnet
python tools/verify.py
```

The command checks the actual project graph, runs Python negative controls, compiles the two libraries and test project, executes the positive NUnit suite, verifies expected test discovery/counters, then compiles and runs a deliberately failing NUnit test in a separate configuration. A missing/malformed/empty result, skip, unexpected test set, compiler warning/error or false-green negative control fails verification. Logs, TRX results, exact SDK/OS and per-file hashes are written under ignored `artifacts/`.

The GitHub workflow `Offline interaction contracts` runs the same command on Linux and Windows with read-only repository permissions and no Unity use. It does not deploy a game or change branch protection. Evidence status must come from actual job results, not this workflow declaration.

## Test scope and limitations

The positive manifest currently expects 146 NUnit cases across 39 named methods, including 100 seeds x 200 actions in a separate array-based claim model. Additional cases exercise 10,000 rejected commands, receipt eviction, conflict/retry handling, access denial, exact expiry, stale attachment callbacks, overflow, teardown and cross-epoch protection. Thirteen Python guard tests exercise clean/forbidden references and false result files. The deliberately failing NUnit control is separate, not counted as a positive test.

These provide **partial offline evidence** for CMD-01/02/03/04, HOLD-01/02/03, LIFE-01/02, SHIFT-01, ARCH-01/04 and CI-01/02. They do not fulfill those IDs' entire Unity/multiplayer acceptance scopes. The source tripwire is conservative and the compiled-reference check covers these libraries only; neither proves absence of every form of spaghetti, reflection-based dependency or dead code.

No existing runtime implementation was found at the inspected baseline, so there is no replaced-source deletion. Source art, generated Blender code, materials and review evidence are untouched. There are no serialized Unity identity migrations in this change.

Future engine integration, trusted input/network adapters, clock/lifecycle hooks, rate limits, peer authentication, view delivery and physical readiness still require their own implementation and evidence. Broader game features remain in the existing roadmap, not as unused stubs here.

## Technical references

- [.NET Standard API sharing](https://learn.microsoft.com/en-us/dotnet/standard/net-standard)
- [Unity 6 .NET profile support](https://docs.unity.cn/6000.0/Documentation/Manual/dotnet-profile-support.html)

These references inform the conservative library target. They do not certify the recorded Unity editor's compatibility with these unimported files.
