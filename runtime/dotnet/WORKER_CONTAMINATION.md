# Discrete worker contamination contacts

This prototype uses the existing Workers-owned 0–100 contamination meter. It does
not implement radiation dose, biological shutdown, exposure stages, material
contamination conversion or accepted game balance. The later fitting slice is
documented in [TIMED_SUIT_FITTING.md](TIMED_SUIT_FITTING.md).

## Authored sources and host authority

During Setup register up to 32 immutable sources. Each source has Exposure or
Decontamination kind, a discrete load of 1–100 units and a 1–60,000 ms shift-clock
cooldown (default 500 ms). No new assembly edge or state owner is introduced.

```csharp
world.RegisterWorkerContaminationSource(spillId,
    new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 20));
world.RegisterWorkerContaminationSource(washId,
    new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, 30));
// After world start and current host-clock sampling, an explicitly bound host
// observation adapter supplies source, target, sequence, cause and sampled time.
var reply = world.ObserveWorkerContamination(world.Epoch, workerId, spillId,
    observationSequence, causeId, world.View.ElapsedMilliseconds);
```

This is a trusted host observation port like worker impacts, not a client command
or a player's claim to have washed. Future native adapters must observe their
explicitly bound source/worker and current world clock. Sources are authored at
setup; callers cannot choose the load or kind in an observation. The existing
`SetWorkerEnvironment` remains trusted absolute condition control for fixtures
and diagnostics. It writes the same meter, not a parallel exposure balance.

## Protection and contact arithmetic

| Suit | Fraction of a new exposure load retained |
| --- | --- |
| None | 100% |
| Compromised | 50%, rounded upward to a whole unit |
| Intact | 25%, rounded upward to a whole unit |

These are fictional fixture parameters. Small discrete loads retain a minimum
one unit; they are not integrated rates. The meter clamps to 0–100. Cleaning
subtracts its authored load regardless of suit, clamps at 0, and does not repair
suits, heal consciousness, stand a worker, change injury/recovery identity or
release held/slotted custody. `EffectiveUnits` is the post-protection contact
load before meter clamping; actual meter change is `After - Before`.

## Identity, timing and cooldown

Sequence and cooldown belong to each `(worker, source)` pair; two workers at the
same source do not share them. Impact observation sequencing remains separate.
There is one retained receipt/high-water mark per source, bounded to 32 per worker.
Definitions and receipts retire with their owning world/worker.

- A new contact must use the next source sequence and exactly the current
  authoritative shift coordinate. Past/future samples, invalid payloads, unknown
  sources, gaps and old sequences have no effect and do not consume a new receipt.
- A matching retained retry compares original cause/sample/definition before
  current time, suit or contamination. It returns Duplicate with the original
  detached contact data and current Worker view, and never repeats an effect.
  A changed retained payload is PayloadMismatch; older identities are TooOld.
- An admitted sample during cooldown returns CoolingDown and consumes its source
  sequence, preserving the original eligibility deadline. Frequent callbacks
  cannot slide that deadline or increase contamination during the cooldown.
- An eligible contact at an already clean/saturated meter returns NoChange and
  consumes its receipt/cooldown. Applied alone changes condition revision and
  sets `WorkerReply.Changed`. NoChange/CoolingDown only advance protocol history.
- Wrong epoch, pause and terminal/disconnected ownership reject before admission.
  Pause freezes the process clock; it does not accumulate exposure to catch up.

Only the trusted observation stream uses these outcomes. Authenticated player
intentions keep the existing separate critical-command receipt contract.

## Medical and causal integration

An accepted contamination condition change, including trusted absolute environment
control, immediately interrupts a treating patient whose value exceeds the
station's limit. The returned `WorkerReply.MedicalChange` exposes that required
owner transition. Washing before another poll cannot erase the unsafe excursion.
Interruption retains costs, body custody, cycle identity and original injury
cause; a new valid start is a separately paid cycle. Safe changes do not interrupt.
Advancing to the treatment due coordinate completes it before a later contact,
so late exposure cannot retroactively cancel a completed cycle.

Exposure has its own source/cause and does not overwrite worker injury attribution.
Changed contact events carry raw/effective load, before/after meter and occurrence
time in the typed trace and bounded retained incident timeline. Immediate medical
records use the station identity; their trigger cause/source can identify the
contact while `MedicalChange.InjuryCauseId` retains the treated injury. Readouts
project those events and ignore historical retries.

## Trusted local feed and sampled fixture areas

`WorkerContaminationFeed` composes one trusted producer per registered
worker/source pair during Setup. The engine adapter calls ObserveIfDue only
after observing current presence. The feed uses the last accepted sequence and
the canonical contact's NextEligibleAtMilliseconds as a scheduling hint. It
accepts Applied, NoChange and CoolingDown receipts, retains sequence/cooldown
across outside gaps and pause, and samples once after a delayed frame. It never
integrates missed contacts. Missing workers and inactive worlds emit nothing;
unexpected stream rejection latches failure for the host to stop visibly.

The temporary Unity fixture binds actual pelvis Rigidbody points to two
unit-scale oriented boxes in deterministic source order. No availability,
consciousness, posture or custody gate grants immunity. Pumping settles due work
before the new current contact; an exposure sampled at suit completion uses the
new protection. Source 720 authors raw12 exposure each1000ms, source721 washes
25 each1000ms. Markings at (0,1.5,-4.5) and (5,1.5,-4.5), half extents
(1.25,1.5,1.25), are non-colliding and separated. The compact readout exposes
canonical suit/load and current sampled area even with the main panel hidden.

This is sampled pelvis presence, not continuous exposure or full-body contact.
Current candidate evidence: [fixture zones](../validation/FIXTURE_CONTAMINATION_ZONES.md).

## Evidence boundary

[Task evidence](../validation/WORKER_CONTAMINATION.md) records actual tests,
scenario/model execution and independent source review for the original contact
slice. Later feed/fixture evidence is separate. Native import, GUI, physical
sampling and multiplayer remain NotRun; source checks are not those results.
