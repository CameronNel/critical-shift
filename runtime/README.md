# Critical Shift runtime: one source integration candidate

**OFFLINE-005, 18 September 2026.** This candidate reconciles the consolidated offline gameplay from PR #43 (`30129f7a44e8976b13a4fe3307e329420034e2ff`) with WP-01 foundation source from PR #46 (`43a2e328802fa4b73de407cfeebb5a7058edf90a`), then adds bounded fictional reactor/power rules. It is on `feat/offline-reactor-power-20260918`. Independent review and maintainer merge remain separate. Main and the authored map are not changed.

## Start without either editor

From the repository root:

```sh
cd runtime/dotnet
python tools/verify.py
```

Prerequisites: a stable .NET 8 SDK, Python 3.10+ and network access for the initial test-package restore. No Unity or Blender installation, activation, GPU or game installation is required. Source is in `dotnet/src/`, executable tests in `dotnet/tests/`, and versioned scenarios in `dotnet/scenarios/`.

The verification command compiles the actual C# libraries and scenario runner, checks exact expected test discovery, executes a deliberately failing test in a separate configuration, runs every scenario twice and checks non-destructive report output. It fails on missing evidence, skipped/failed tests, unexpected inventories and false-green negative controls. Results and exact source hashes are in ignored `dotnet/artifacts/`. The read-only `Editor-free runtime verification` workflow runs this on Windows and Linux. It neither launches nor downloads either editor.

Run a single scenario with a fresh output filename:

```sh
dotnet run --project tools/CriticalShift.Scenarios --configuration Release -- --scenario scenarios/reactor-cooling-recovery.json --report artifacts/manual-cooling-new.json --repeat 2
```

The successful workflow also packages `offline-scenario-runner.zip`: the actual first-party .NET command-line executable, its gameplay libraries and all scenario inputs. Extract it and use the command in its README with a .NET 8 runtime. This is not a graphical game or Unity Player. It does not include Unity, Blender, test-framework binaries or map assets.

## Current ownership and source layout

| Location | Purpose |
| --- | --- |
| `dotnet/src/CriticalShift.Application/` | Canonical gameplay command admission, world/session composition and cross-owner workflows |
| `dotnet/src/CriticalShift.Features.*.Domain/` | Seven independent rule domains: Interaction, Session, Workers, Materials, Production, Reactor and Power |
| `unity/Assets/CriticalShift/Application/ProcessLifetime.cs` | The single canonical local-process lifetime implementation, not the gameplay session owner |
| `dotnet/src/CriticalShift.ProcessLifetime/` | Build project that links that exact process source; it contains no copied implementation |
| `unity/Assets/CriticalShift/Bootstrap/` | WP-01 diagnostic bootstrap and optional native preparation/build code; not gameplay or map integration |
| `tools/` | Foundation static/evidence checks and optional native tooling |

The foundation assembly was renamed from `CriticalShift.Application` to `CriticalShift.ProcessLifetime`, preserving its metadata GUID and C# type namespace. The gameplay assembly keeps `CriticalShift.Application`. Foundation references and checks were updated. The offline suite compiles both together and exercises multiple real gameplay sessions inside one process lifetime.

The former narrow `tools/pure-tests/` harness was removed after its eight original assertions were linked into the normal offline NUnit suite. Their canonical source still also belongs to the original Unity EditMode test assembly. A passing offline run of that source is not a native Unity Test Runner pass.

The application and seven gameplay domain DLLs built by the offline projects provide one future integration route. Do not copy these source files into another implementation or introduce a second mutable holder, material ledger, clock or power balance. The optional scenario package does not install DLLs into Unity. Native importer configuration and scene adapters remain future work.

## Contracts and useful entrypoints

- [Offline build, interaction and ownership](dotnet/README.md)
- [World/session and clocks](dotnet/WORLD_AND_TIME.md)
- [Worker recovery and scenarios](dotnet/WORKERS_AND_SCENARIOS.md)
- [Production, accounting and cancellation](dotnet/PRODUCTION.md)
- [Reactor, reserve power and fuel-cycle contracts](dotnet/REACTOR_AND_POWER.md)
- [Current task, preservation and evidence](validation/OFFLINE_REACTOR_POWER.md)
- [Canonical architecture](../design/code-architecture/README.md)

PR #43 and PR #46 remain provenance for their contributions. Their earlier heads are not substitutes for this reconciled candidate. The old offline branch's root README and map state were not transplanted. The entire current `sections/` tree remains `06a41745022bcaee48d7ca3291b19f5febfcb673`.

## Native foundation remains separately unverified

The recorded Unity target remains 6000.4.3f1, revision 39d1a88d4dd1, Built-in rendering and Mono desktop support. The original source-only WP-01 work is documented in [WP01.md](validation/WP01.md) and its historical [execution-summary.json](validation/execution-summary.json). Those results belong to the revisions recorded there, not the renamed current foundation.

No editor was opened for OFFLINE-005. Startup scene creation, complete ProjectSettings serialization, package import, engine tests and Player execution remain NotRun here. The source preparation command is still `Critical Shift > Foundation > Prepare project` in a future activated editor, and the native runner remains available for a separately authorized task:

```powershell
python runtime/tools/run_foundation.py --unity "C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe" --target Win64
```

That runner needs Python 3.12+, an already activated matching Editor and matching build support. It uses a disposable copy, requires its own native test/build/readiness evidence and does not import the map. No activation or credentials belong in this repository. The automatic native Unity workflow is absent on this candidate; pushing code cannot accidentally run it.

## Scope boundary

This is useful, user-authorized editor-free source prework, not a Gate 0/1 pass, accepted Unity foundation, production-ready reactor, complete power station or human fun test. It adds no physical interactions, transport, Steam, voice, UI/input framework, persistence, save schema, terrain or art changes. Single-threaded host policy, physical bindings, native compatibility and independently reviewed integration remain necessary. Read the reactor guide's fixture limits before using its values as game balance.
