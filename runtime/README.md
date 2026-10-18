# Critical Shift runtime

**Current development, 18 October 2026:** `codex/unity-gameplay-sandbox` adds an isolated local-host Unity fixture over the canonical gameplay sources. It includes physical crate handling, cart/conveyor adapters, worker knockdown/drag/recovery and bounded process presentation. Cameron has ended gaming and explicitly authorized Unity/testing. Execution is beginning; current results and limits belong in the [active development checkpoint](validation/GAMEPLAY_SANDBOX.md). Combined-map gameplay is authorized separately from the changing baked-art importer; preserve Claude's PR #110 paths. See [sandbox controls and evidence boundary](unity/Assets/CriticalShift/Sandbox/README.md).

Historical source provenance: OFFLINE-005 (18 September 2026) reconciled consolidated offline gameplay from PR #43 (`30129f7a44e8976b13a4fe3307e329420034e2ff`) with WP-01 foundation source from PR #46 (`43a2e328802fa4b73de407cfeebb5a7058edf90a`), then added bounded fictional reactor/power rules. Its original candidate branch was `feat/offline-reactor-power-20260918`. Current work still requires independent review and maintainer merge.

## Start without either editor

After execution is authorized, from the repository root:

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
| `unity/Assets/CriticalShift/Features/Interaction/Unity/` | Local host clock, command admission, explicit physical claim/slot bindings and spatial observations |
| `unity/Assets/CriticalShift/Features/Workers/Unity/` | Local walking, one ragdoll handoff, drag/crawl forces and staged recovery clearance |
| `unity/Assets/CriticalShift/FacilityPhysics/` | Bounded cart/conveyor forces, load observations, motion visuals and physics diagnostics |
| `unity/Assets/CriticalShift/Presentation/` | Read-only process/material/worker feedback and temporary IMGUI controls |
| `unity/Assets/CriticalShift/Sandbox/` | Scratch fixture composition, scoped scene generator, declared native cases and controls |
| `tools/` | Source/evidence checks and separate optional foundation/sandbox native runners |

The foundation assembly was renamed from `CriticalShift.Application` to `CriticalShift.ProcessLifetime`, preserving its metadata GUID and C# type namespace. The gameplay assembly keeps `CriticalShift.Application`. Foundation references and checks were updated. The offline suite compiles both together and exercises multiple real gameplay sessions inside one process lifetime.

The former narrow `tools/pure-tests/` harness was removed after its eight original assertions were linked into the normal offline NUnit suite. Their canonical source still also belongs to the original Unity EditMode test assembly. A passing offline run of that source is not a native Unity Test Runner pass.

The Unity integration trial references these same sources through the local first-party package `com.criticalshift.gameplay` at `dotnet/src`. Eight engine-free asmdefs mirror the .NET project references; no gameplay source or DLL is copied into `Assets`. Source-project build output belongs in ignored `dotnet/artifacts/compiled`, outside the package. Do not introduce a second mutable holder, material ledger, clock or power balance. The optional scenario executable remains separate. Native package import and physical scene acceptance remain unverified; see the [sandbox development checkpoint](validation/GAMEPLAY_SANDBOX.md).

## Contracts and useful entrypoints

- [Offline build, interaction and ownership](dotnet/README.md)
- [World/session and clocks](dotnet/WORLD_AND_TIME.md)
- [Worker recovery and scenarios](dotnet/WORKERS_AND_SCENARIOS.md)
- [Production, accounting and cancellation](dotnet/PRODUCTION.md)
- [Reactor, reserve power and fuel-cycle contracts](dotnet/REACTOR_AND_POWER.md)
- [Current Unity task, preservation and evidence](validation/GAMEPLAY_SANDBOX.md)
- [Offline reactor provenance and evidence](validation/OFFLINE_REACTOR_POWER.md)
- [Canonical architecture](../design/code-architecture/README.md)

PR #43 and PR #46 remain provenance for their contributions; their earlier heads do not establish results on the current revision. The old offline branch's map state was not transplanted. Current runtime work leaves the independently changing `sections/` content outside its edit and import scope.

## Native foundation remains separately unverified

The required Unity target remains **6000.4.3f1, revision 39d1a88d4dd1**, with the pinned Mono desktop profile in [toolchain.json](toolchain.json). Cameron selected URP on 15 October; the project still has its older Built-in configuration, and no URP package/version has been installed by this pass. The sandbox's import/physics fixture can use that existing configuration, while its optional Player build explicitly requires URP. See [the engine decision](../design/ENGINE_DECISION.md).

The original WP-01 work is documented in [WP01.md](validation/WP01.md) and its historical [execution-summary.json](validation/execution-summary.json). Those results belong to their recorded revisions. Source and installed-file identity checks do not establish native execution on this branch.

No editor was opened for OFFLINE-005. Startup scene creation, complete ProjectSettings serialization, package import, engine tests and Player execution remain NotRun here. The source preparation command is still `Critical Shift > Foundation > Prepare project` in a future activated editor, and the native runner remains available for a separately authorized task:

```powershell
python runtime/tools/run_foundation.py --unity "C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe" --target Win64
```

That runner needs Python 3.12+, an already activated matching Editor and matching build support. It uses a disposable copy, requires its own native test/build/readiness evidence and does not import the map. No activation or credentials belong in this repository. The automatic native Unity workflow is absent on this candidate; pushing code cannot accidentally run it.

For the separate sandbox inventory, the future authorized command is:

```powershell
python runtime/tools/run_sandbox.py --unity "C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe" --target Win64
```

That runner preserves source hashes and native logs/results in a disposable workspace under ignored `runtime/out/`. It requires exact test discovery and the pinned editor identity. `--build-player` separately requests a URP-gated build; adding `--run-player` requests the same new build's headless startup/teardown smoke. Neither flag establishes rendered playability, human feel, multiplayer convergence or supported performance. All current sandbox execution remains NotRun.

## Scope boundary

The current deliverable is a source-only local-host integration trial. Gate 0/1, native compatibility, physical feel, renderer integration and independent review remain pending. Its physics and presentation sources do not choose transport, Steam, voice, a production input/UI framework, persistence or a save schema. It imports no map, terrain or authored art. Read the fixture values and their limits before treating them as game balance.
