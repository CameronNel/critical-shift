# Offline runtime: interaction, world, workers, production and reactor/power

**Start here for executable C# gameplay rules.** Planning remains in [design/code-architecture/](../../design/code-architecture/README.md). Current source integration and provenance are in [runtime/README.md](../README.md). This directory contains engine-independent libraries and executable tests, not a Unity project or physical simulation.

## Active modules and ownership

| Source | Responsibility | Allowed project references |
| --- | --- | --- |
| `src/CriticalShift.Features.Interaction.Domain/` | Exclusive object claims, versions, leases, slots and retirement | None |
| `src/CriticalShift.Features.Session.Domain/` | Shift lifecycle, separate host/shift clocks and one-shot timers | None |
| `src/CriticalShift.Features.Workers.Domain/` | Worker conditions, guarded recovery and deadlines | None |
| `src/CriticalShift.Features.Materials.Domain/` | Quantities, batch ancestry and conversion accounting | None |
| `src/CriticalShift.Features.Production.Domain/` | Recipe-cycle state, work, power and jam transitions | None |
| `src/CriticalShift.Features.Reactor.Domain/` | Fictional finite fuel work, cooling, instability and trip state | None |
| `src/CriticalShift.Features.Power.Domain/` | Reserve, generation, spending, delivery and spill accounting | None |
| `src/CriticalShift.Application/` | Command admission/receipts, WorldSession composition and cross-owner workflows | The seven domains above |
| `src/CriticalShift.ProcessLifetime/` | Builds the one canonical foundation process-lifetime source by an exact file link | None |
| `tests/CriticalShift.Offline.Tests/` | Contract, lifecycle, model and compiled-boundary tests; eight linked original foundation assertions | Declared runtime subjects only |
| `tools/` | Scoped dependency/result checks, verifier and scenario executable | Not runtime code |

Domains do not reference peer domains or engine APIs. Application coordinates the existing owners instead of duplicating custody, time, quantities or power. There is no new Core assembly, event bus, DI framework or transport abstraction. The pure process library is distinct from gameplay Application; the source-integration guide records its retained metadata identity and future Unity boundary.

## Run without either editor

Prerequisites: stable .NET 8 SDK, Python 3.10+ and network access for initial test-package restore. No Unity, Blender, GPU, editor license or local game installation is needed.

```sh
cd runtime/dotnet
python tools/verify.py
```

The current `Editor-free runtime verification` workflow runs this on Windows and Linux with read-only repository permissions. It also runs the foundation's static/Python checks, packages the actual scenario executable and retains exact source inputs. It performs no game deployment, editor launch, automatic commit or merge. It does not change repository protection settings.

Verification checks project/source boundaries, negative Python fixtures, C# compilation, the exact expected NUnit manifest, actual TRX rows, and a separate deliberately failing NUnit control. Missing/empty results, incorrect discovery, failure/skip rows, inconsistent totals and a false-green negative control fail validation. Every scenario is executed twice and checked against its expected steps/assertions. Reports refuse existing paths, including filesystem aliases. Logs, results, source hashes and exact SDK/OS are in ignored `artifacts/`; declarations alone are not passing evidence.

Runtime libraries target .NET Standard 2.1 / C# 8.0, with no third-party runtime package dependencies. .NET 8 is the offline compiler/test host, not a replacement game engine. The existing stable 8.0 roll-forward policy records the exact SDK used in every run. Test-only packages remain Microsoft.NET.Test.Sdk 17.11.1, NUnit 3.14.0 and NUnit3TestAdapter 4.6.0. No new runtime package is selected by OFFLINE-005.

## Feature contracts and scenarios

[WORLD_AND_TIME.md](WORLD_AND_TIME.md) covers clocks, pause, timers, teardown and restart. [WORKERS_AND_SCENARIOS.md](WORKERS_AND_SCENARIOS.md) covers worker condition/recovery, possession cleanup and synthetic clearance. [PRODUCTION.md](PRODUCTION.md) retains production custody, accounting, cancellation and its prior review repairs. [REACTOR_AND_POWER.md](REACTOR_AND_POWER.md) extends the existing production chain through one finite fuel cycle and reserve account, including its explicit fixture limits.

Use fresh report names for manual scenarios:

```sh
dotnet run --project tools/CriticalShift.Scenarios --configuration Release -- --scenario scenarios/reactor-full-production-chain.json --report artifacts/manual-reactor-new.json --repeat 2
```

The 12 current scenarios include all eight inherited inputs plus four reactor/power inputs. See the manifests and actual task/PR evidence for exact counts and results. The optional successful workflow package can run the same first-party scenario executable with a .NET 8 runtime; it is not a Unity Player or graphical game.

## Interaction calling contract

A trusted composition point creates InteractionWorld or the enclosing WorldSession, registers stable entities and already-authenticated connection-to-actor mappings, then starts it. There is no permissive production access policy. Never accept setup registration or binding-failure callbacks directly from untrusted network payloads.

All operations belong to one host simulation thread. Advance the monotonic host clock explicitly before a tick's commands. Shift time pauses independently. Input authentication, rate limits and real reach/line-of-sight checks remain adapter responsibilities.

Commands start at sequence 1 per connection. Grab uses the object revision; Release/Renew require the exact lease generation. Production and Reactor requests share that same stream and add their target revisions and bounded typed payloads. Admitted well-formed gameplay rejections also finalize their sequences. A matching retained retry returns its historical receipt without another mutation. Changed payloads, gaps, wrong epochs and too-old evicted requests do not execute. Receipt storage is bounded; its high-water mark survives eviction.

**Accepted does not mean a new physical effect.** Only HasNewCommit identifies a new logical change. A replayed accepted receipt can describe an object already released; compare current epoch/revision and never reattach from historical state. Physical binding must later acknowledge/fail the exact epoch/entity/lease with its own tested adapter.

Release remains possible when reach changes. Unexpected access-policy or integrity errors fault the workflow rather than silently continuing. Stop is idempotent and clears owned state. Retired entity IDs cannot be registered again within the world. Setup roster capacity counts live connections while keeping a separate bounded history of retired identities; in-world joining/reconnect remains unsupported.

## Authorization, integration and evidence scope

OFFLINE-001 through OFFLINE-004 supplied interaction, world/time, workers and production in consolidated PR #43. OFFLINE-005 imports that exact candidate into the WP-01 source branch, resolves its assembly collision, and adds this bounded reactor/power slice at Cameron's explicit request without either editor. Original branches/PRs are provenance, not separate active implementations to copy or independently merge over this candidate.

Native Unity import, AOT/stripping, PlayMode, physical simulation and Player compatibility remain unverified. No roadmap gate or complete WP-01/WP-02 is declared passed. A seed in world configuration does not establish deterministic physics. The fixture is not full reactor/meltdown, power-distribution or demand-contract implementation.

Not implemented here: physical controllers/carrying/loading, world geometry, network authentication/transport, input/UI, Steam, voice, persistence or checkpoint schemas. Current Blender sources, textures, licensed materials and art evidence are outside runtime cleanup and unchanged.

Offline domain/application evidence partially addresses CMD, HOLD, LIFE, SHIFT, TX, POWER, CAUSE, ARCH and CI concerns. It does not replace their native/multiplayer acceptance scopes, measure supported FPS, or prove that every defect/dead path is absent. The final task/PR identifies the exact executed commit and independent-review status.
