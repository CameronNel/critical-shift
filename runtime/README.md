# Critical Shift runtime

**Current development, 18 October 2026:** `codex/unity-gameplay-sandbox` adds local-host gameplay over the canonical sources: physical crate handling, cart/conveyor motion, worker knockdown/drag/recovery, process feedback and combined-map doors. The required Unity **6000.4.3f1 / 39d1a88d4dd1**, URP **17.4.0**, is in use. Source `6554abef` passed **132/132 native gameplay cases**, a strict Windows build, headless cleanup, an actual rendered PNG and the physical deny/carry/drop exercise. Separate foundation validation passed **12 EditMode + 9 PlayMode** cases, build and Player. The pure suite passed **723** assertions; supplementary API checks passed all **21 assemblies**. Native runs disclose a verified preinitialized SDK cache rather than a cold package extraction. Earlier failures, the diagnostic-policy change and open acceptance work remain in the [active checkpoint](validation/GAMEPLAY_SANDBOX.md). The current collision derivative's 37 doors, 152 proxies and 13 anchors were measured within 0.285 mm; its fresh URP preparation also passed. This does not establish human feel, supported FPS, full facility traversal/art, multiplayer or independent acceptance. The [compact evidence index](validation/results/gameplay-2026-10-18.json) and [actual game-camera frame](validation/results/gameplay-2026-10-18.png) are reviewable in this branch. Draft [PR #111](https://github.com/CameronNel/critical-shift/pull/111) is stacked on Claude's bake/importer branch and is unmerged.

The local workstation delivery is `runtime/out/CriticalShift-Gameplay-Win64-20261018.zip` (about 70 MB). Its 308 Player files were compared byte-for-byte after archive verification, and a fresh extraction passed startup/cleanup. Extract the whole folder and run `CriticalShiftSandbox.exe`; Unity is not needed to launch the Player. [Controls and scope](unity/Assets/CriticalShift/Sandbox/README.md).

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

The Unity integration trial references these same sources through the local first-party package `com.criticalshift.gameplay` at `dotnet/src`. Eight engine-free asmdefs mirror the .NET project references; no gameplay source or DLL is copied into `Assets`. Source-project build output belongs in ignored `dotnet/artifacts/compiled`, outside the package. Do not introduce a second mutable holder, material ledger, clock or power balance. The optional scenario executable remains separate. Native package import has run; physical scene acceptance remains unverified. The actual editor bundles Test Framework 1.6.0 and NUnit 2.0.5, now reflected by the declared pins. See the [sandbox development checkpoint](validation/GAMEPLAY_SANDBOX.md).

## Contracts and useful entrypoints

- [Offline build, interaction and ownership](dotnet/README.md)
- [World/session and clocks](dotnet/WORLD_AND_TIME.md)
- [Worker recovery and scenarios](dotnet/WORKERS_AND_SCENARIOS.md)
- [Production, accounting and cancellation](dotnet/PRODUCTION.md)
- [Reactor, reserve power and fuel-cycle contracts](dotnet/REACTOR_AND_POWER.md)
- [Current Unity task, preservation and evidence](validation/GAMEPLAY_SANDBOX.md)
- [Offline reactor provenance and evidence](validation/OFFLINE_REACTOR_POWER.md)
- [Canonical architecture](../design/code-architecture/README.md)

PR #43 and PR #46 remain provenance for their contributions; their earlier heads do not establish results on the current revision. The old offline branch's map state was not transplanted. Current runtime work reads only the four declared combined-map collision/anchor inputs from `sections/`; the authored scenes, bake outputs and protected importer remain outside its edit scope.

## Native foundation remains separately unverified

The required Unity target remains **6000.4.3f1, revision 39d1a88d4dd1**, with the pinned Mono desktop profile in [toolchain.json](toolchain.json). The bounded implementation of Cameron's 15 October URP selection now declares URP/Core/ShaderGraph/config 17.4.0 and their measured dependency lock. Native-created pipeline/global settings and Linear Player/Graphics/Quality settings are included. Foundation and sandbox build acceptance still require their own complete runs. See [the engine decision](../design/ENGINE_DECISION.md).

The original WP-01 work is documented in [WP01.md](validation/WP01.md) and its historical [execution-summary.json](validation/execution-summary.json). Those results belong to their recorded revisions. Source and installed-file identity checks do not establish native execution on this branch.

No editor was opened for the historical OFFLINE-005 task. The current continuation has native rendering and foundation preparation evidence, but complete foundation tests/build/Player remain pending. `Critical Shift > Foundation > Prepare project` and its separate native runner remain available:

```powershell
python runtime/tools/run_foundation.py --unity "C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe" --target Win64
```

That runner needs Python 3.12+, an already activated matching Editor and matching build support. It uses a disposable copy, requires its own native test/build/readiness evidence and does not import the map. No activation or credentials belong in this repository. The automatic native Unity workflow is absent on this candidate; pushing code cannot accidentally run it.

For the separate sandbox inventory:

```powershell
python runtime/tools/run_sandbox.py --unity "C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe" --target Win64
```

That runner preserves source hashes and native logs/results in a disposable workspace under ignored `runtime/out/`. It requires exact test discovery and the pinned editor identity. `--build-player` separately requests a URP-gated build; adding `--run-player` requests the same new build's headless startup/teardown smoke. Neither flag establishes rendered playability, human feel, multiplayer convergence or supported performance. Consult the checkpoint for the latest actual execution status.

For the separate combined-map collision derivative:

```powershell
python runtime/tools/run_combined_map.py --unity 'C:\Program Files\Unity\Hub\Editor\6000.4.3f1\Editor\Unity.exe' --target Win64
```

It imports the scoped FBX, validates actual proxy bounds and door/room anchors to 1 cm and saves a generated scene in its disposable workspace. Native measurements showed that this collision export needs a 180-degree root rotation to match the existing baked-art placement frame. Room floors/art and ladder traversal are separate work; the diagnostic spawn uses the existing spine floor.

## Scope boundary

The current deliverable is a local-host integration trial undergoing native validation. Gate 0/1, physical feel, renderer integration and independent review remain pending. Its physics and presentation sources do not choose transport, Steam, voice, a production input/UI framework, persistence or a save schema. The combined-map derivative imports collision proxies and anchors; it does not import room art or establish map acceptance. Read the fixture values and their limits before treating them as game balance.
