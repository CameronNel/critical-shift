# Runtime code: start here

## One integration route

**PR #43 is the consolidated offline-runtime integration candidate against `main`.** It contains the complete interaction, world/time, worker/scenario and production work previously reviewed through #40, #41 and #42, plus the repairs listed below. Check the live PR for its exact tested head, execution evidence and merge status. The presence of this document does not mean the PR is merged or independently approved.

Use the current #43 head for review and any dependent work until integration. Do not independently merge or cherry-pick the older partial implementation PRs: their earlier heads do not contain all subsequent review fixes. Their original branches, commits and discussions are retained as history, not competing active implementations.

| Historical contribution | Preserved head | Included scope |
| --- | --- | --- |
| #40 | `1d43c02` | Interaction custody, command receipts and offline verification |
| #41 | `63f81a5` | World lifetime, shift/host clocks and timers; setup-roster repair |
| #42 | `82aae83` | Worker state/recovery, diagnostics and executable scenarios |
| #43 before consolidation | `1fafae1` | Material/machine processing; hazard attribution and report-path repairs |

No history is rewritten by consolidation. Closing an earlier PR as superseded is not claiming its original head was fixed or individually merged. Main integration remains a separate maintainer action under [AGENTS.md](../AGENTS.md).

## Source, contracts and verification

The single canonical C# implementation remains [dotnet/](dotnet/README.md), with distinct `src/`, `tests/`, `tools/` and `scenarios/`. No files are copied into a parallel implementation.

- [Source ownership and offline build](dotnet/README.md)
- [World/session, shift clocks and timers](dotnet/WORLD_AND_TIME.md)
- [Worker recovery, possession cleanup and scenarios](dotnet/WORKERS_AND_SCENARIOS.md)
- [Production chain, accounting and cancellation contracts](dotnet/PRODUCTION.md)
- [Canonical architecture and code-health rules](../design/code-architecture/README.md)

From `runtime/dotnet`, run `python tools/verify.py`. It builds the actual libraries/tool, validates the exact test and scenario inventories, runs deliberately failing controls, checks boundaries and tests non-destructive report output. PR #43 records results from both Linux and Windows; scenario counts and source declarations are not execution evidence.

## Review repair index

| Finding | Canonical repair | Evidence entrypoints |
| --- | --- | --- |
| #40: disconnected setup player consumes capacity | Live connections count toward player slots; old identities have a separate bounded history | `WorldSessionTests`: setup replacement and identity-history cases |
| #42: impacts lose hazard/cause identity | Explicit source/cause with source-scoped sequence admission and typed trace fields | `HazardAttributionTests` |
| #42: report path can overwrite an aliased scenario | Create-new-only report writes; existing input aliases and unrelated files are refused | `tools/check_report_safety.py` |
| #43: cancellation loses cycle/shortcut attribution | Retained conversion receipt produces a typed cancellation with explicit cycle/recipe and current-cycle bypass decision | `CancellationAttributionTests`; `production-cancel-attribution.json` |

The cancellation regression was first run against the old implementation: the existing 513 cases passed and the added cycle-identity assertion failed. The final fix adds 12 cancellation cases without weakening the existing suite. Cancellation metadata does not manufacture output or alter retained input/waste accounting; replayed requests cannot publish another committed cancellation event.

## Scope and remaining gates

This is a fix/consolidation pass, not new reactor, power, terrain, UI or network implementation. It adds no runtime package and performs no Unity installation/import/Player/physics test. There are still six runtime assemblies: five peer-independent domains and Application. The existing WorldSession complexity review trigger remains visible in the feature documents; this pass does not grow or refactor that coordinator.

All earlier engine, physical-binding, multiplayer, persistence and human-playtest gates remain outstanding. Original section art, Blender sources, licensed materials and evidence are outside runtime cleanup. Old branches and retained evidence are not dead runtime code and must not be deleted by an unused-source sweep.
