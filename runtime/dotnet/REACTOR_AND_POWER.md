# OFFLINE-005: fictional reactor and reserve-power rules

**Editor-free implementation, 18 September 2026.** This bounded slice connects the existing production chain to one abstract reactor and one reserve account per world. It does not model nuclear engineering, fuel chemistry, heat transfer, radiation or real equipment procedures. Numeric values are explicit test fixtures, not approved game balance.

## What is now executable

Ore is processed by the existing recipe machines into Fuel. The same registered container is carried into the reactor's canonical interaction slot. Startup requires cooling and sufficient reserve. Explicit shift-clock samples consume a finite operating-time budget, deliver grid units and recharge reserve up to its capacity. Lost cooling or suspect fuel raises an abstract instability counter, emits attributed warnings and trips the core. Cooling restoration never automatically restarts it. Fully used fuel becomes SpentFuel through the same material ledger and retains its origin and cause.

Four new scenarios extend the eight inherited scenarios without replacing them:

| Scenario | Exercises |
| --- | --- |
| `reactor-full-production-chain.json` | Actual ore/crusher/processor outputs entering the core; startup replay, finite output, spent-fuel rejection and clean restart |
| `reactor-cooling-recovery.json` | Cooling loss, exact warning/trip boundaries, once-only emergency spending, explicit reset/restart and final ejection attribution |
| `reactor-reserve-contention.json` | Two authenticated fixture actors competing for the same reserve, stale revisions, retries and pause admission |
| `reactor-deadline.json` | Generation capped at the shift deadline, completion before teardown and rejection of prior-world commands |

Run `python tools/verify.py` from `runtime/dotnet`. For a manual run, choose a new report filename:

```sh
dotnet run --project tools/CriticalShift.Scenarios --configuration Release -- --scenario scenarios/reactor-full-production-chain.json --report artifacts/manual-reactor-new.json --repeat 2
```

The JSON report contains actual assertion outcomes, final world/production/power summaries and a bounded trace. Existing files, including aliased scenario inputs, are never overwritten. A restart creates a fresh world and trace; the runner's final snapshot is the last world, not an archive of every previous world. Earlier steps remain verified by scenario assertions and executable tests.

## Owners, dependencies and public command path

`ReactorCore` owns immutable operating mode, loaded duration, accumulated work, cooling and abstract instability. `PowerAccount` owns immutable reserve and accounting totals. Both domains reference base libraries only; neither references the other or an engine.

Application `ReactorOperations` coordinates core/power state, calls the existing Interaction owner for custody and the existing ProductionOperations/MaterialLedger for fuel conversion. It has no independent world clock, quantity store or receipt stream. One public setup method registers the reactor through the existing world setup guard; later mutation is internal and reachable through `WorldSession.ExecuteInteraction` only. The existing application boundary checks also cover the new domain owners and detached views.

Register before `WorldSession.Start`:

```csharp
world.Reactor.Register(reactorId, new ReactorDefinition(definitionId));
```

A command uses `InteractionKind.Reactor`, the reactor logical ID, current world epoch, the existing per-connection sequence, and a `ReactorRequest`. The request includes the expected reactor revision. Insert additionally needs the held container ID, current object/batch revisions and exact lease generation. Eject needs the current slotted object's revision. Cooling is supplied only for SetCooling; all irrelevant fields must remain at their canonical defaults.

The trusted host observation policy validates actor access. There is no permissive production default. Scenario/test policies are explicitly synthetic. Do not treat these tests as spatial reach, authentication or real multiplayer validation.

A well-formed admitted gameplay rejection finalizes its sequence. A matching retained retry returns its historical receipt without another change; a changed retry, sequence gap, too-old request or wrong epoch cannot execute. Only `HasNewCommit` authorizes a new logical effect. Replayed ReactorChange metadata remains inspectable, but the trace's committed ReactorEvent is absent. Clients never supply their own reserve cost or generated energy.

## Operating rules and interlocks

Modes are Empty, Loaded, Running, Shutdown, Tripped and Exhausted. Insert accepts only an actual Fuel batch within configured capacity and transfers Held to Slotted through the canonical custody owner. A failed insertion leaves the actor's object and all material quantities unchanged.

Startup or restart requires Loaded/Shutdown, cooling enabled, remaining operating budget and instability below the warning threshold. It spends the definition's fixed startup cost. A request to Start an already Running core is NoChange and does not spend again. The first successful start reserves one conversion/cycle identity before installing the running core and new reserve value. A restart after shutdown keeps that original cycle and accumulated work.

Shutdown pauses work. Trip is latched. Restoring cooling only enables cooldown; ResetTrip requires the configured safe threshold and leaves the core Shutdown. A separate Start request is required and spends its startup cost. EmergencyCooling enables cooling and reduces instability by the fixture's relief amount, spending its fixed reserve cost only when a change can occur. It neither resets a trip nor restarts the core.

The bounded AuxiliaryPower action is a reserve-consumer fixture to exercise contention with startup/emergency cooling. It is not an implemented reanimation machine, refinery power circuit or general-purpose client-specified withdrawal API.

## Finite fuel and material accounting

Fuel capacity is expressed as an abstract operating-time budget. Generation is calculated from completed quanta of cumulative work, not per-call rounding, so subdividing a clock advance cannot mint energy or discard fractional progress.

Fuel is exclusively slotted while processing. On exhaustion, one reserved conversion changes the ledger's Fuel batch to a new SpentFuel batch with the same nominal quantity and retained lineage. This is bookkeeping of fictional batch units; it does not assert real mass-energy equivalence. Other production conversions retain their existing output/waste accounting.

The example fixture is 100 ore units -> 80 crushed units + 20 waste -> 60 fuel units + 20 waste -> 60 spent-fuel units. Those 60 fuel units provide 6000 operating milliseconds: 60 quanta produce 300 abstract power units, comprising 60 reserve credits and 240 grid delivery. With initial reserve 10 and startup cost 3, the example ends with reserve 67 when there is no additional spending or overflow.

Unused Loaded fuel may be ejected before first startup. Once a cycle starts, partly used fuel cannot be ejected in this slice: unloading and reinserting must not reset its work budget. Fully Exhausted fuel can be ejected only after instability is at or below the safe reset threshold. SpentFuel cannot be inserted as fresh fuel. Safe mid-cycle unloading, physical casks, conveyors and refuelling equipment require a later explicit design/binding change.

Fuel cycles share the existing bounded material-conversion history. Exhausted history rejects the next startup before reserving material or debiting power. A repeated completion cannot produce another output batch. On world teardown, unfinished conversions follow the existing cancellation/aggregate-accounting policy and live state is discarded. No mid-cycle checkpoint or fuel-budget restoration is implemented; fresh-world setup is explicit, not an implicit refund into the old world.

## Power accounting and contention

The PowerAccount identity is:

`Initial + Generated = Available + Spent + Delivered + Spilled`

Available never becomes negative or exceeds capacity. Excess reserve credit is recorded as Spilled, never silently lost or reclassified as delivered. Insufficient reserve rejects the action without changing core state, material reservation or power. The application serializes validated requests on the host simulation thread; competing consumers cannot each spend from a copied balance. Checked arithmetic is evaluated before installing accepted states. This is in-memory atomic workflow logic, not a distributed or crash-durable transaction.

## Time and causal evidence

The existing world supplies capped shift time. Pause stops reactor work, instability progression and output while the host clock can continue existing lease handling. Exact repeated samples have no new effect. Backwards time is rejected. Required work is advanced to the deadline before terminal cleanup, so completion exactly at the deadline counts once and later time does not count.

Unsafe-running time raises instability. CoolingLost takes precedence over SuspectFuel while cooling is absent. Safe running and cooled shutdown reduce it. A trip or exhaustion can occur inside a large clock step; work/output is capped at that event. Exhaustion wins an exact exhaustion/trip tie. A latched trip can cool during the remainder of a large step without implicitly resetting itself.

Warnings/trips carry exact occurrence times and cause identities. Suspect-fuel consequences retain the initiating batch/cause and production bypass history. A cooling-loss command creates its own cause reused by its warning/trip. Ejection keeps original input/cycle attribution independently of the resulting empty view. ReactorChange.State is the detached final state of the sampled command/advance, not a reconstruction of every intermediate event-time state. Generated is a batch of newly completed output quanta for that advance. Consumers must not confuse its final snapshot with a historical gauge at WarningAt.

Stop, timeout or unexpected fault freeze detached power totals, clear live core/claims/material reservations and reject stale requests. Restart receives a new epoch and no reactor configuration until setup registers it. No event observer can alter quantities or spend power.

## Reviewable default fixture

One reactor; reserve capacity 100; initial reserve 10; startup cost 3; emergency-cooling cost 4; auxiliary cost 6. Maximum fuel 10000 nominal units; each unit grants 100 operating milliseconds. Every completed 100-millisecond quantum credits reserve 1 and grid 4. Warning at 400 unsafe milliseconds; trip at 800; reset/ejection safe at 100; emergency relief 400. Contamination above 500 or inherited inspection-bypass history marks fuel suspect. These defaults are configurable and bounded by validated definitions.

Not implemented: a full reactor/meltdown model, demand contracts or quota completion, turbine/distribution topology, real emergency-energy sources, reanimation power consumption, physical fuel loading, UI/audio, saves, transport, native compatibility or proof of fun. These limits keep OFFLINE-005 bounded rather than silently claiming the entire GAME_SPEC reactor department is complete.
