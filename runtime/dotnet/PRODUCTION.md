# Offline production: batches, machines and safe transfers

**OFFLINE-004 | 8 September 2026 | Implementation without Unity**

User-authorized scope: a substantial useful offline batch. Based on PR #42 at `82aae83fa0e9daa471eb31d59a51fb44f34faff4`, after the interaction, world/time and worker slices. See PR #43 for exact tested commits, executed counts and review status. Tests described here are requirements and executable fixtures, not a substitute for their run artifacts. No production milestone or merge approval is implied.

## The concrete loop

Register an ore container and two recipe-driven machines during world setup. An authorized worker grabs the container, inserts it in the crusher, starts a cycle, waits through explicit clock updates, ejects the result, carries it to a second processor and retrieves fictional fuel. Moisture can block safe startup; overriding that interlock accelerates the selected fixture but produces a delayed jam. Isolate power, repair, restore power and explicitly resume to recover.

The example uses 100 abstract input units -> 80 crushed units plus 20 waste -> 60 fuel units plus another 20 waste. These are configurable test values, not approved balance, real mass yields or nuclear process instructions. Contamination, moisture and bypass history remain inspectable across transformations. No actual reactor, fuel chemistry or real equipment operation is modeled.

## Owners and dependency boundaries

| Owner | Authoritative facts | Non-responsibilities |
| --- | --- | --- |
| Existing Interaction domain | Holder/lease, machine slot occupancy, container custody/revision | Quantities, recipes, machine work |
| Materials domain | Current batch quantities/properties, parent/origin/cause identities, reserved conversions, completed/cancelled receipts and waste totals | Holder or machine operating state |
| Production domain | Immutable machine mode, work, power availability, cycle identity and jam state | Material or custody mutation |
| Application ProductionOperations | Validated cross-owner transactions, integration and detached views | Physics, UI, network transport, an alternate world clock |
| WorldSession | Shared world epoch, readiness, command guard, clock and teardown | Recipe algorithms or duplicated inventory |

The Materials and Production domains reference only base libraries, not one another or Unity. Application is their coordination point. ProductionOperations is exposed as `world.Production` for setup and queries; no public direct machine mutation bypasses the existing interaction admission path. Its two partial files are one type for complexity review. WorldSession remains above the earlier approximate 400-line trigger when its partial files are counted together; the added production work stays outside its facade except construction, ticking and cleanup. Independent review must assess that trade-off; file splitting is not a waiver.

## Setup and public command contract

After constructing WorldSession, register authenticated connections as before. Use `world.Production.RegisterMachine` with an immutable MachineRecipe, and `RegisterBatch` with explicit container/batch/origin/cause identities. RegisterBatch also registers its custody entity; do not register the same container twice. Machine IDs and object IDs cannot collide. Start closes registration. Default machine/cycle capacities are 16/1024, with explicit limits up to 128/4096. They are bounded offline fixtures, not performance guarantees.

Send `InteractionKind.Production` with a typed ProductionRequest through `WorldSession.ExecuteInteraction`. It shares the SAME per-connection sequence and receipts as Grab/Release/Renew. The trusted connection determines actor identity; the existing access policy and worker condition determine whether the actor may operate the target. The eventual policy must validate real machine access; this module is not a transport/authentication or role-permission implementation.

Actions are Insert, Eject, Start, SetPower, Repair, Resume and CancelCycle. Every action supplies the expected machine revision. Insert additionally supplies the held container, current object revision, batch revision and lease generation. Start checks current batch revision; Eject checks current object revision. Unused payload fields must have their canonical defaults. Invalid payloads do not consume the sequence; admitted gameplay rejections do, preserving the next-command path. Matching retained retries return historical receipts without another logical commit. Changed payloads and old evicted commands cannot run again. Only HasNewCommit may initiate a new adapter effect.

## Custody and transaction guarantees within this slice

Each machine has one logical processing slot. The existing claim store atomically transfers Held -> Slotted and Slotted -> World after validating the current lease/revision and empty/eligible destination. A slotted container cannot be grabbed or generically retired. A worker becoming incapacitated or disconnecting does not eject material already owned by a machine. The losing actor in a full-port conflict retains their own input unchanged.

There is one reusable container with a new batch identity after conversion, not an unbounded supply of freshly spawned physical fuel objects. The one-slot convention tests transaction semantics; final inlet/output sockets, trays, conveyors and separate physical outputs require a deliberate later binding/migration design. It does not override the master specification's richer physical machine interfaces.

Startup validates mode, power, material type, capacity, moisture, nonzero rounded output and history capacity before mutation. MaterialLedger prepares a conversion and reserves its output identity/history capacity before the matching machine cycle is installed. No user callback, await, renderer or physics code runs between the logical owner updates. Completion consumes the reserved input version once and creates the declared output plus waste. Repeated completion returns the retained receipt; it cannot mint another batch. Memory failure or an unexpected integrity exception is not a supported partial-success recovery: WorldSession faults/clears the affected world and propagates diagnostics.

There is no distributed transaction or crash-durable promise. The terminal summary and conversion receipts are in-memory data, not saves. Cycle identity/history remains bounded. If the history budget fills, a new cycle is rejected BEFORE reserving input rather than silently losing replay protection or failing after work completes.

## Time, failure and cleanup

Processing uses the world's explicitly supplied shift-time coordinate. World pause stops work. Power loss preserves completed work and moves a running cycle to PowerPaused; restored power alone does not restart it. Jam detection clamps work at the authored threshold even if a clock sample overshoots. Repair requires power off, disarms that cycle's wet-input jam and leaves it paused. Resume needs power and a resumable mode. An active/jammed machine cannot eject its input.

CancelCycle requires isolated power. The initial cancellation policy preserves the complete original input and records a cancelled cycle; no partial product or invented material loss is emitted. Completion transforms the batch atomically in logical state. OutputReady blocks another cycle until explicit ejection, preventing accidental repeated processing of output under the same identity.

**Deadline decision:** required production is advanced up to the capped shift deadline before timeout cleanup. A cycle completed exactly at that deadline counts once. A cycle needing more time is cancelled by teardown, with its input included in terminal active-unit accounting. Advisory WorldTimerQueue signals retain their discard-on-end policy and do not drive production. The integration tests distinguish 999/1000/1001 ms around a 1000 ms recipe. Explicit Finish/Stop acts at the last sampled time; the host must sample time before deciding to end.

Stop, timeout, fault and restart clear live machines, material maps, reservations and custody. A detached terminal ProductionSummary retains issued/active/waste quantities and completion/cancellation totals. It is not a second mutable inventory. The fresh successor starts empty and requires explicit setup; scenario fixtures may deliberately re-register their initial ore. Reading an old summary cannot restore its entities.

Actual physical insertion/ejection readiness is NOT implemented. The eventual Unity adapter must coordinate pending bindings, collision, placement and failure recovery before treating logical acceptance as a working machine. Tests here do not prove an inlet collider, material shader, conveyor or character controller works.

## Review fixes carried forward from PR #42

Impact observations now require explicit hazard and cause IDs. Sequence admission is scoped per `(world, worker, hazard)` with up to 32 retained sources per worker. Duplicate severity/delay/cause returns Duplicate, changed cause is a payload mismatch, and independent hazard streams do not conflict. Exhausted source capacity rejects a new source; it never evicts protection and then replays old damage. The latest worker view and bounded trace keep source/cause/severity separately from the object released by an impact. Producers must retain their original identity and source-local sequence; they cannot rotate IDs to force a new observation.

Scenario reports use create-new file semantics. Existing output paths are rejected without truncation, including Windows case aliases, hardlinks, symlinks and symlinked parents. Choose a new report filename or explicitly remove your obsolete report before invoking the tool. No overwrite flag is added. The verification harness exercises real filesystem aliases in temporary directories and checks source hashes after each failed attempt.

Both repairs are in this dependent PR, not a claim that PR #42's original head was retroactively fixed. Its test-only old-arity convenience adapters supply explicit synthetic hazard IDs; there is no permissive source-free impact overload in runtime code.

## Run and review

From `runtime/dotnet`:

```sh
python tools/verify.py
```

For one production scenario, use a report path that does not already exist:

```sh
dotnet run --project tools/CriticalShift.Scenarios --configuration Release -- --scenario scenarios/production-chain.json --report artifacts/manual-production-new.json --repeat 2
```

The four production fixtures cover the chain with power interruption, wet-input bypass/jam recovery, cancellation and exact-deadline completion. The three existing worker fixtures still run. ProductionWorldTests and ProductionStressTests cover cross-owner and two-actor behavior; ProductionRuleTests include 100 fixed seeds x 200 independent machine-oracle actions. A separate throughput test completes 100 transformations across 50 input containers with a seven-receipt command window, checking accounting after every operation and rejection of an evicted old request.

The existing verifier checks exact test/scenario discovery, compiled assembly references, immutable public projections, forbidden peer/tool dependencies, expected false-green controls, scenario failures and report safety. No new test/runtime package is introduced. Exact Linux/Windows results and source hashes belong in PR #43 and its artifacts. These are offline logical tests, not performance measurements, networked peer tests or proof of every possible dead path's absence.

No Unity project, physics substitute, networking/Steam/voice dependency, reactor/power-grid simulation, save schema, art/Blender asset or repository protection change is included. Later Unity integration must consume the same canonical source or migrate it once, not fork a competing implementation. Roadmap Gates 0 and 1 remain necessary before playable proof-of-fun acceptance; an offline chain is not a passing human fun or visual-integration gate.
