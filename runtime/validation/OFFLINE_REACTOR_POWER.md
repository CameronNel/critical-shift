# OFFLINE-005: source integration and reactor/power rules

Authorized by Cameron on 18 September 2026: reconcile existing offline gameplay with WP-01, rerun offline checks, add a bounded reactor/power rules slice with executable scenarios. Do not open Blender or Unity. Primary author: ChatGPT. Independent reviewer: not assigned; acceptance pending. No self-merge.

## Provenance and protected baseline

Main baseline: `a82c7d9b80456153a0c65ca4897044a7f62c7d1c`.
Foundation source: PR #46, `43a2e328802fa4b73de407cfeebb5a7058edf90a`.
Offline source: PR #43, `30129f7a44e8976b13a4fe3307e329420034e2ff`, exact imported runtime/dotnet tree `3fdd46aaa237b9e8bca3bb28d7a4836c27ae8f8f`.
Candidate: `feat/offline-reactor-power-20260918`.

The current full `sections/` tree remains `06a41745022bcaee48d7ca3291b19f5febfcb673`. MAP.json, MAP.md, launchers, Blender files and the existing authoring workflow are outside the change. No old branch's root/map state was substituted. The large total diff includes inherited PR #43/#46 implementation; it is not all new reactor code.

## Source and consumer migration

- Keep canonical gameplay Application and five inherited domains under runtime/dotnet; add independent Reactor and Power domains with Application as their coordinator.
- Rename the foundation assembly to CriticalShift.ProcessLifetime, retaining its GUID and canonical ProcessLifetime.cs/type namespace. Update its real references/checks.
- Compile the same process source and eight original lifecycle assertions in the normal offline NUnit suite. Remove only the superseded narrow tools/pure-tests harness, not its assertions or Unity source.
- New reactor commands share existing epoch/connection/sequence/access/receipt validation. Custody remains with Interaction, quantities with the existing Materials ledger, time with the existing Session timeline. ReactorOperations is not another GameManager or clock.
- Keep optional native foundation source and historical evidence, but remove the automatic Unity workflow on this candidate. A push must not download or launch either editor.

One temporary exact-baseline migration script was applied in an isolated runner and removed. Its first two publication attempts failed (workflow-expression interpolation, then Actions token workflow-write permissions), with no partial branch publication. The successful publisher changed runtime source only. Workflow cleanup was performed through the authorized connector; no one-time write workflow remains. Ongoing runtime CI is read-only and never commits or merges.

## Executed baseline and first integrated verification

Baseline imported-source run `35318902624` passed on Windows and Linux before reactor changes. It reran all 525 inherited NUnit cases and existing scenarios, plus foundation Python checks.

Integrated executable revision: `c296c93b5b1b060d836c48de093413476443f1c1`.
Run: `35321833882`.
Both archives were downloaded and CRC/SHA256-checked. Actual TRX rows, build logs, scenario reports and all 92 source hashes were inspected; both platforms' input hashes matched one another and the locally retrieved source.

| Actual check on that revision | Linux | Windows |
| --- | --- | --- |
| C# build | 0 warnings, 0 errors | 0 warnings, 0 errors |
| NUnit cases | 675 passed, 0 failed, 0 skipped | 675 passed, 0 failed, 0 skipped |
| Offline Python guards | 27 passed | 27 passed |
| Foundation Python guards | 40 passed | 40 passed |
| Versioned scenarios | 12, each run twice | 12, each run twice |
| Scenario steps / assertions | 336 / 814 | 336 / 814 |
| Native Unity, Blender, physics, connected transport | NotRun | NotRun |

The 675 cases comprise all 525 inherited cases, eight preserved foundation assertions now executed by the standard offline test runner, and 142 new reactor/power/integration cases. Test declarations were not used as evidence. The exact test and scenario manifests remain checked against discovered/executed outcomes; no inherited scenario or test count was reduced. The supplementary API compiler was not run for this task.

Artifacts for the integrated revision (30-day retention):
- Linux `10537347353`, SHA256 `49a5eefbe8591b688f36001ace426e0613575e55acd5b582f18650ad4ee71f49`.
- Windows `10537277824`, SHA256 `2166d07e8f01d6e8aab5cff4a3afed9a051d5cdd811e9328fce6377a64e70cfd`.
- Exact source archive `10537571856`, SHA256 reported by GitHub `e89946878676f2533f5e32362ddbf6f682a343d149f8946a028458503f333e93`.

Later packaging/documentation commits require their own workflow evidence. The final PR and handoff summary identify the final checked revision; do not silently apply these earlier results to changed executable code.

## Contract coverage and review boundaries

The task exercises partial offline A01-A09, S01-S05/S07-S08, H01-H07, CMD/TX/POWER-01/CAUSE/LIFE/SHIFT and ARCH/CI concerns. It is explicitly authorized offline prework, not a WP-01/WP-02 or Gate 0/1 acceptance. Physical binding, authentication, engine simulation, native import, UI, human playtesting, saves and performance remain unverified.

[REACTOR_AND_POWER.md](../dotnet/REACTOR_AND_POWER.md) specifies concrete numeric fixtures, finite fuel, power conservation, one shared command stream, single-reactor scope, latched recovery and event-time versus final-snapshot semantics. AuxiliaryPower is a logical competing-consumer fixture, not a reanimation implementation. Part-used fuel cannot be unloaded in this slice. Terminal cancellation/accounting is not persistent fuel-budget restoration.

The existing WorldSession complexity review trigger remains visible: the coordinator is already above the approximate threshold when all partials are counted. Reactor-specific mutation lives in ReactorOperations; additions to WorldSession are construction, guarded clock integration and teardown. A separate independent reviewer must assess the combined graph and retained historical assumptions. File splitting and passing tests are not waivers or proof of absence of all defects.

## Handoff acceptance

The review candidate must include actual final-revision test/scenario evidence, preserved asset-tree verification and a source/optional CLI package. Final source compilation and executable scenarios do not establish a playable Unity game. Main remains unchanged; reviewer and maintainer control any merge. Historical WP-01 licensing evidence is retained only as historical context, not a current obstacle to completing the authorized editor-free task.
