# Finite backup power and black start

An optional timed backup supply can restore the existing reserve when a stopped
reactor has insufficient startup power. This is a fictional stored-charge
prototype. It does not model real equipment, physical fuel inventory or plant
engineering. [Task evidence](../validation/EMERGENCY_BLACK_START.md) records what
actually ran.

## Setup and commands

Register the reactor and then its optional supply before Start:

```csharp
world.Reactor.Register(reactorId, new ReactorDefinition(definitionId, initialReserve: 0));
world.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(
    durationMilliseconds: 5000, reserveUnits: 12, charges: 2));
// After the world starts, the already-authenticated connection uses its ordinary port.
var start = commands.OperateReactor(reactorId, ReactorAction.StartBackup);
var cancel = commands.OperateReactor(reactorId, ReactorAction.CancelBackup);
```

The existing Reactor target, current reactor revision, spatial access policy,
worker availability and per-connection receipt stream apply. No client chooses
an output amount or time. A source-less reactor returns BackupUnavailable.
Definitions bound duration to 1–60,000 ms, output to 1–1,000,000,000 abstract
reserve units and stock to 1–32 charges. Output must fit reactor reserve capacity.
The sandbox authors the default two-charge supply and exposes temporary panel
buttons through the existing host route; those native controls are not executed
by the offline evidence.

## Cycle and accounting rules

Start needs an unused charge and enough **current** headroom for its full output.
It consumes one charge and begins the authored delay once. Starting an active
cycle is NoChange. A matching retained retry returns the original detached
receipt; it never restarts work, consumes stock or credits energy again. Other
fresh consumers and completions invalidate stale reactor revisions.

The cycle remains autonomous after its initiating operator disconnects. Any
currently authorized upright worker at that reactor may explicitly cancel it.
Cancellation keeps the charge consumed and produces no power. Charges have no
refill or material-container interface in this bounded slice.

Completion uses canonical `PowerAccount.Credit(output, 0)`. It generates reserve,
never grid delivery, so it cannot directly satisfy a contract. Other generation
may fill the reserve after Start; excess then becomes canonical Spilled. The
source view's Produced/Stored/Spilled values attribute that output and do not
constitute another spendable balance. Core and medical costs spend the same
reserve, with the unchanged conservation identity:

`Initial + Generated = Available + Spent + Delivered + Spilled`.

## Time, teardown and diagnostics

The world splits required owner settlement at backup due times and contract
boundaries. At an exact shared coordinate, core generation precedes backup
completion. This fixes which source fills reserve space and makes attribution
independent of clock partitioning. Pause freezes the process clock. Completion
exactly at the capped deadline counts before terminal publication; a later due
cycle is cancelled by teardown, keeping its charge cost. Arithmetic and revision
preparation precede installs; unexpected integrity failure faults the world.

`ReactorView.EmergencyPower` is the current detached source projection.
`Reactor.EmergencyPowerSummary` and `Debrief.EmergencyPower` retain terminal
stock/outcomes without live mutation rights. Backup event CycleId/CauseId identify
that backup cycle, independently of a concurrent fuel cycle in ReactorView.
InputBatchId is empty for backup events. Typed trace, retained incident timeline
and the shared formatter preserve this identity and ignore historical retries.
Restart needs explicit fresh registration and rejects the previous epoch.

No Unity import, physical controls, Player, physics or multiplayer pass is implied.
The source composes the existing seven-domain graph without new packages or
framework selections. Numeric values remain authored fixtures pending playtest.
