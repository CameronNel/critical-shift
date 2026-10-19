# Sampled exposure while handling dirty cargo, 19 October 2026

Branch `codex/dirty-cargo-exposure-20261019`, based on draft PR132 `7fe6af1d`.
Root is sole author; independent ultra tracks review composition, lifecycle,
material/custody admission and model evidence. User authorizes continued work.

An engine-free Application sampler binds at most8 explicit material containers
and4 current workers during Setup, with one existing WorkerContaminationFeed per
worker/source. A dirty held container samples its current live holder only when
current contamination exceeds its authored threshold. Feeds and cooldowns persist
across drops, regrabs, lease changes, conversion and cleaning. Delayed sampling
produces one current contact; it neither catches up doses nor renews custody.

Canonical sources740–747 use12 worker-load units/1000shift-ms and material
threshold500/1000. Existing PPE scales the worker load; material and worker meters
remain separate scales. Washing dirty800 ore to100 stops handling exposure.
Source bindings must be Exposure, never a washing source. Unexpected live missing
bindings or competing producers latch failure; terminal teardown clears owned
feeds. No new condition, quantity, power or custody writer is introduced.

The fixture uses one explicitly ordered polling owner: existing zone sampling
first, then carried exposure, after its host-clock pump. This defines clamping
when washing and handling coexist, and avoids the Bootstrap smoke-only early
return or unordered FixedUpdate components. Worker-zone shutdown owns feed cleanup.
Material context is retained on the existing bounded trace so later clean batches
cannot rewrite the original dirty input attribution. A read-only cue explains
current dirty handling; reading it never samples or mutates state.

S01/S02/S03/S07/S08, WORKER/HOLD/LIFE/CAUSE evidence covers current holder/threshold,
PPE/cooldown, lease expiry, pause, cleaning/conversion, replay, disconnect/epoch,
ordered washing, immutable attribution and failure cleanup. Native timing/GUI
remains Planned/NotRun until pinned Unity executes it. This is trusted logical
custody-based handling, not continuous contact/proximity or radiation simulation.

Focused evidence:25 new executed cases passed, covering strict threshold501,
all three PPE scales, saturation/no-change receipts, per-worker/source cooldowns,
drop/regrab/handover, sampled jumps, slotted cargo, dirty conversion, washing,
historical custody receipts, real earlier injury, caller binding mutation,
setup/pause/disconnect/terminal and competing-producer admission.182 existing
tooling cases passed; static checks passed203 metadata GUIDs/21 asmdefs/132 C#.

The separate cargo soak predicts current holders, host-time lease expiry,
process-time cooldowns, PPE, meter/revision and material properties from authored
inputs. Every seed forces handover, exact cooldown, no catch-up, pause expiry,
second source and a washed child before randomized interleavings. Only the
opaque washed batch identity is learned. It checks complete contact receipts,
one material-attributed trace per contact and no new client command. The omitted
first positive load fails its named independent invariant. Preliminary seed
20261054 passed10,000 mixed cases/14,809,431 selected operations/model checks in
37.8345768s; this is aggregate gameplay work, not14.8million distinct assertions.

Ultra reviewers found no remaining concrete authority/lifecycle blocker. Root
fixed the reviewed HUD attribution omission: a cargo row now names both worker
and container. Model review also corrected an invalid two-object grab in the
tool oracle and tightened exact trace publication counting. Three native source
cases cover wash-before-cargo order and read-only cues, pause/real-time lease
expiry, and once-only host stop/cleanup on a competing producer. Catalogue174;
these cases, rendered HUD and current physics remain NotRun. Remote Desktop
Commander was checked again12:39UTC and remained Offline. No fresh Unity,
Player, performance or multiplayer result is claimed. Final candidate verification
and draft review status follow below when available.

Final candidate `f7f01bffbd4e35eb9d3e0c0dceebdde23d647fa2` passed the full
verifier12:39:54–12:40:35UTC: **1121 executed/passed, zero failed/skipped;25
scenarios each twice**. All existing controls and the named omitted-cargo-load
control were rejected. All274 recorded inputs match that git tree; nine DLL
hashes match the frozen closure in ignored `out/dirty-cargo-verification-20261019`.
Final frozen seed20261055 passed10,000 cases/14,807,172 selected operations and
model checks in40.843693s. Native catalogue174 remains NotRun. This continuation
is a draft for independent maintainer review and merge; no acceptance gate is
advanced.
