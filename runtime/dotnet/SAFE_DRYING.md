# Safe material drying

The optional drying recipe gives wet ore a safe path into the existing production
chain. Moisture remains canonical material state; no DriedOre kind or extra
quantity owner is introduced. This is a fictional conditioning fixture, not a
real industrial process. [Task evidence](../validation/SAFE_ORE_CONDITIONING.md)
records actual checks and the unexecuted native scope.

```csharp
world.Production.RegisterMachine(dryerId,
    MachineRecipe.Drying(recipeId, MaterialKind.Ore,
        durationMilliseconds: 8000, maximumUnits: 128, targetMoisture: 100));
// After setup/start, the current authenticated port uses ordinary machine commands.
commands.Grab(containerId);
commands.OperateMachine(dryerId, ProductionAction.Insert, containerId);
commands.OperateMachine(dryerId, ProductionAction.Start);
```

The explicit factory fixes input/output to the same kind, yield to 1000 and safe
moisture tolerance to 1000. Target moisture must be 0–999; all ordinary recipe
identity/duration/capacity bounds apply. Ordinary conversion construction keeps
its different-kind restriction. Start requires input above the target and rejects
inspection bypass. AlreadyConditioned and BypassUnavailable are ordinary terminal
gameplay rejections, before history reservation or process mutation.

A completed cycle creates one normal child batch in the same container. Quantity,
contamination, origin, cause and inherited flags remain unchanged; only moisture,
batch identity/parent and material revision change. Drying cannot remove suspect
inspection history, so its later reactor consequences still apply. It produces
zero waste and does not repair a worker suit, wash a worker or clean material
contamination. Those are separate canonical facts.

The existing machine process owns timing, power pause/resume, cancellation and
terminal settlement. No advisory callback or second clock is introduced.
Cancellation keeps the exact wet input, completion at the deadline counts once,
and matching command retries remain historical. MachineView exposes immutable
IsDrying/DryingTargetMoisture facts for readouts and hides no new authority.

Scenario definitions opt in with `"drying": true`, using input, duration, capacity
and optional outputMoisture (default 100). Output, bypassDuration, jamAfter, yield
and tolerance fields are rejected for this mode because the factory fixes them.
Existing ordinary definitions retain their prior format.

Canonical sandbox setup authors one 8-second ore dryer, ID 402/recipe 452. Its
logical wet crate route preserves 12 units through drying, then produces 11 fuel
units through the existing crusher/processor. Those provide 55 seconds of fuel
work and 440 grid units under the sandbox fixture parameters. This is a feasible
public-port route, not accepted physical balance or an entire contract solution.
The temporary native fixture places the dryer separately at (-8.5, 0, 9), reusing
existing machine/loading controls; GUI and physical execution remain NotRun.
