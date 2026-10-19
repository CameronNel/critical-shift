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
plus a clinical model with independently predicted admission, costs and outcomes.
It then runs three randomized epochs with fresh bindings. Each epoch starts
actual reactor, machine and paid medical work together, then mixes custody
contention, production, power controls, replay, impacts, aid/environment, medical
commands, standing clearance, pause, doors, evacuation, disconnect and timers.
Checks run after randomized steps and at teardown.

The mixed medical ledger uses new commits and explicit owner-change results;
it never reconstructs required state from the bounded diagnostic trace. It
matches events to requested actions and body identities, checks legal station
transitions, tracks distinct started/closed cycles and captured injury causes,
and predicts due time from authored duration. Completion must preserve the
pre-poll patient's suit/contamination. A due/invalid cycle cannot silently omit
its required completion/interruption. Disconnected fixture bodies must be
retired with their workers. Independent spending sums the authored reactor
action costs and medical starts; stock use and terminal cancellation must agree.
These checks complement the separate clinical admission model.

Invariants cover material/power conservation, reserve bounds, current/future and
settled demand windows, replay without new commits/spend, old-epoch rejection,
one held object per actor, holder/slot exclusivity, available holders, configured
trace bounds, retained journal bounds, chronological incident detail, frozen
debrief and complete owner teardown. Before every mixed owner poll, stored
standing deadlines predict the returned worker expiries, including at terminal
cutoff; overdue recoveries cannot survive in the final roster. `CheckedSteps` includes randomized loop
steps (some selected operations are inapplicable) and independent-model clock
samples; it is not a count of committed actions.

The regular verifier runs12 cases, a single-seed reproduction, an intentionally
failed invariant, a deliberately omitted paid-medical-start ledger control and
an existing-report refusal. Seed reproduction checks that the case executes
successfully again; it does not compare a normalized full trace/state digest.
A long run is useful
logical compositional evidence, not Unity/physics, multiplayer, performance,
human feel, full medical/meltdown or saved-game acceptance. The report's assembly
hashes identify the code actually exercised; later source changes need their own
verification. No real-time waiting is used to pad the logical simulation loop.
