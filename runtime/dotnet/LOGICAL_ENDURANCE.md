# Logical gameplay endurance

The existing scenario executable also runs reproducible composite lifetimes:

```sh
dotnet run --project tools/CriticalShift.Scenarios -c Release -- --soak --cases 10000 --report artifacts/endurance-new.jsonl
dotnet run --project tools/CriticalShift.Scenarios -c Release -- --soak --seconds 3600 --seed 20261018 --report artifacts/hour-new.jsonl
dotnet run --project tools/CriticalShift.Scenarios -c Release -- --soak --case-seed 903414045 --report artifacts/reproduce-new.jsonl
```

Choose exactly one stopping mode. Reports use create-new JSON Lines; an existing
path is refused. A Running line or interrupted process is not success. Require
process exit0 and a final Passed record. Each failed record includes a case seed
that recreates the case independently of all prior seeds. Reports identify the
complete CriticalShift DLL closure by SHA256, including every Domain DLL.
The initial snapshot must be preserved when testing while development continues.

Each case includes two finite-fuel supply worlds (one large clock jump, one
random partition) compared against independent integer quantum/window arithmetic,
then three randomized epochs with fresh bindings. Each randomized epoch starts
actual reactor and machine work, then mixes custody contention, production,
power controls, replay, impacts, aid, standing clearance, pause, doors, evacuation,
disconnect and timers. Checks run after randomized steps and at teardown.

Invariants cover material/power conservation, reserve bounds, current/future and
settled demand windows, replay without new commits/spend, old-epoch rejection,
one held object per actor, holder/slot exclusivity, available holders, configured
trace bounds, retained journal bounds, chronological incident detail, frozen
debrief and complete owner teardown. `CheckedSteps` includes randomized loop
steps (some selected operations are inapplicable) and independent-model clock
samples; it is not a count of committed actions.

The regular verifier runs12 cases, a single-seed reproduction, an intentionally
failed invariant control and an existing-report refusal. A long run is useful
logical compositional evidence, not Unity/physics, multiplayer, performance,
human feel, full medical/meltdown or saved-game acceptance. The report's assembly
hashes identify the code actually exercised; later source changes need their own
verification. No real-time waiting is used to pad the logical simulation loop.
