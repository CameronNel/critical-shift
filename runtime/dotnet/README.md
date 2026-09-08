# Offline runtime: interaction, world, workers and time

**Start here for real C# code.** Planning remains in [design/code-architecture/](../../design/code-architecture/README.md). This directory contains engine-independent runtime libraries and executable tests, not a Unity project.

## Active modules and ownership

| Source | Responsibility | Allowed project references |
| --- | --- | --- |
| `src/CriticalShift.Features.Interaction.Domain/` | Exclusive object claims, versions, lease generations, expiry and retirement | None |
| `src/CriticalShift.Features.Session.Domain/` | Shift lifecycle, separate host/shift clocks and bounded one-shot timers | None |
| `src/CriticalShift.Features.Workers.Domain/` | Independent worker conditions, guarded recovery and completion deadlines | None |
| `src/CriticalShift.Application/` | Interaction command admission/receipts and WorldSession composition; detached public views | The domains above |
| `tests/CriticalShift.Offline.Tests/` | Contract, lifecycle, seeded model and compiled-boundary checks | Declared runtime subjects only |
| `tools/` | Scoped dependency/result validation and build/test entrypoint | Not runtime code |

The Session domain does not reference the Interaction domain. WorldSession privately composes the existing interaction owner; it does not duplicate custody, expose live domain objects or create a generic GameManager. There is no Core assembly, event bus, DI framework or repository abstraction without a present consumer.

## Run without Unity

Prerequisites: stable .NET 8 SDK, Python 3.10+ and network access for initial test-package restore. No Unity editor, GPU, Unity license or local game installation is needed.

```sh
cd runtime/dotnet
python tools/verify.py
```

The existing GitHub workflow `Offline interaction contracts` runs this same verification on Linux and Windows, now including session/time tests. It has read-only repository permissions and no game deployment step. No repository protection setting is changed.

Verification checks project/source boundaries, negative Python fixtures, C# compilation, the exact expected NUnit test manifest, real TRX results, and a separate intentionally failing NUnit control. Missing/empty results, incorrect discovery, failure/skip rows, inconsistent totals and a false-green negative control fail validation. `artifacts/` contains actual logs, result files, source hashes and environment; test declarations alone are not passing evidence. Follow the current PR for run status.

Runtime libraries target **.NET Standard 2.1 / C# 8.0**, with no third-party runtime package dependencies. .NET 8 is the offline compiler/test host, not the eventual engine runtime. The SDK follows the existing stable 8.0 roll-forward policy and exact versions are recorded. Test-only packages remain Microsoft.NET.Test.Sdk 17.11.1, NUnit 3.14.0 and NUnit3TestAdapter 4.6.0. This work adds no new package selection.

## Workers and executable scenarios

See [WORKERS_AND_SCENARIOS.md](WORKERS_AND_SCENARIOS.md) for current worker APIs, recovery clearance, possession cleanup, bounded diagnostics and scenario commands. The same verifier now runs the three versioned offline scenarios and deliberate failure controls. They use production rules with explicitly synthetic access/clearance observations, not Unity or network simulation.

## Interaction calling contract

A trusted composition point creates an InteractionWorld (or the enclosing WorldSession), registers stable entities and already-authenticated connection-to-actor mappings, then starts it. There is no permissive production access policy; a caller must provide host-observed access decisions. TestAccess exists only in tests. Never accept registration or binding-failure callbacks directly from untrusted network payloads.

All operations belong to one host simulation thread. Advance the monotonic unscaled host clock explicitly before processing a tick's commands. Claims do not expire through hidden threads. Input authentication, time sampling, rate limits and real reach/line-of-sight checks remain adapter responsibilities, not features implemented here.

Commands start at sequence 1 per connection. Grab uses the expected object revision; Release/Renew require the exact lease generation. Both accepted and well-formed gameplay-rejected next commands finalize their sequence. A matching retry returns its historical receipt without rerunning mutation. Changed payload, forward gap, wrong epoch and too-old evicted commands do not execute. Receipt storage is bounded; the high-water mark survives eviction.

**Accepted does not mean a new physical effect.** Only HasNewCommit identifies a new logical change. A replayed accepted receipt may describe an object already released. Compare current epoch/revision and never reattach from historical state. Physical binding must later acknowledge/fail the exact epoch/entity/lease with a separately tested adapter.

Release remains possible when access/reach changes. Unexpected access-policy or integrity errors fault the workflow rather than silently continuing. Stop is idempotent and clears owned state. Retired entity IDs cannot be registered again within the world.

Setup roster changes now count only live connections toward player capacity. Disconnected connection identities remain invalid, but retained identity history has a separate bounded budget (default 256, max 4096). Rejoining setup needs a fresh connection identity. In-world joining/reconnect remains unsupported. This fixes the setup-capacity review finding on PR #40.

## World and timer calling contract

See [WORLD_AND_TIME.md](WORLD_AND_TIME.md) for phase transitions, timeout policy, explicit ticking, pause, cancellation, snapshot revisions, teardown and restart. These are logical session services, not terrain, rooms, scene loading, weather or a playable character controller.

## Authorization, integration and gate status

OFFLINE-001 introduced interaction prework; OFFLINE-002 extends it with world/session/time; OFFLINE-003 adds worker conditions/recovery, possession cleanup and executable scenarios at Cameron's explicit request while Unity is unavailable. OFFLINE-002 is stacked on the implementation from PR #40, not a copied replacement. The scoped offline-prework exception in DELIVERY_PLAN remains applicable; no Roadmap Gate 0/1 or complete WP-01/02/03 is declared passed.

Later Unity integration must consume these libraries/the same source or move them atomically. Do not copy them into competing Unity implementations. The exact editor import, C# profile, AOT/stripping, PlayMode, physical simulation and Player compatibility have not been validated. World configuration seed metadata does not imply deterministic physics or a generated world.

Not implemented: Unity projects/assets/controllers, network transport/authentication, physical carrying, runtime geometry, inventory/materials/machines/reactor/mining, persistence, UI/input, Steam or voice. Existing Blender sources, textures, licensing/provenance and art evidence are unchanged. No serialized Unity migration is performed.

Evidence scope: offline domain/application tests are partial evidence for CMD, HOLD, LIFE, SHIFT, ARCH and CI cases in the plan, not their complete Unity/multiplayer gate acceptance. Model-action totals are operations exercised inside seeded tests, not thousands of separate test methods or a code-coverage percentage. Static checks and review cannot prove absence of every dead path or design mistake.
