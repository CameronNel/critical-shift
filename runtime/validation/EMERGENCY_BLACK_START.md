# Finite emergency power / black start, 19 October 2026

Bounded implementation branch `codex/emergency-black-start-20261019`, based on
`50df95cf` (draft PR #120). Primary author: Codex. Independent read-only ultra
reviewer: `audit_shift_boundaries`; further model review follows implementation.
The owner authorized useful game systems and fixes without questions.

Purpose: recover a stopped, fueled reactor when its canonical reserve has fallen
below startup cost, as described by GAME_SPEC 7.3, 12.4 and 20.6. One optional
finite authored backup supply lives in the existing Power domain, composed by
ReactorOperations. Existing authenticated Reactor commands operate it at the
reactor target with current reactor revision, shared receipt/access/pause rules.
There is no client-supplied energy amount, second reserve, generic credit port,
new domain/assembly edge, package, transport, UI or persistence framework.

Starting consumes one authored stored charge exactly once and begins a timed
cycle. Cancellation keeps that charge consumed; disconnect leaves committed
work autonomous. A completed cycle credits reserve through PowerAccount and
cannot deliver contract/grid energy. Current headroom must fit the output before
starting; later reserve generation may still spill and is accounted by the sole
Power owner. All completion arithmetic/revisions are prepared before installs.

Split required process settlement at each backup due time as well as contract
boundaries. At a shared coordinate, reactor generation precedes backup completion.
This makes source storage/spill attribution independent of clock partitioning.
Pause freezes work; due-at-deadline completes once before terminal publication;
later due work is cancelled by teardown without refunds. Summary/causal events
remain detached in debrief; restart receives a fresh optional setup and epoch.

Expected paths: Power domain state, Application reactor contracts/partial owner,
world cutoff calculation, typed event/readout/debrief, canonical sandbox setup
and existing temporary GUI buttons, focused tests and versioned
public-port scenario/model evidence. Relevant S01/S02/S03/S05/S08 and POWER-01,
LIFE-02, CMD-02/03, TIME-01. No replaced mutation owner or serialized identity is
removed. Numeric values and stored charges are fictional prototype fixtures,
not physical generator fuel inventory, radiation or accepted balance.

Planned acceptance: zero-reserve black start, finite charges, shared medical/core
spending, retries/rejections, stale revisions/epoch/access, pause, cancel/operator
loss, exact deadline, split-vs-leap source attribution and causal retention.
Unity/native controls/physics/GUI/Player/multiplayer remain NotRun.

## Intermediate executed evidence

The first candidate built with zero warnings/errors and 21 focused tests passed.
The expanded 28-case suite passed with denied/stale/malformed admission, due-time
overflow, source/core/medical spending in both consumer orders and a forced
reactor-revision overflow at the deadline. That failure test confirms no energy
or successful terminal outcome is published before fail-closed cleanup.

The new public-port black-start scenario passed twice: 16 steps and 67 assertions
per run. A first independent event-clock composite run passed 100 cases, checking
backup/core source chronology and stock/outcomes rather than reading diagnostics.
Full verification and final model/source review are pending.

Independent review identified an accidental unused randomized backup registration
inside the paired supply comparison fixture; it was removed so both comparison
worlds retain identical authored inputs. Review also caught the normalized trace
omitting reactor cycle identity. The primary author corrected generic cycle/cause
projection, with focused assertions against the typed backup payload.

The first 10,000-case seed 20261031 probe passed 11,290,865 CheckedSteps in 26.48 s
before those review fixes. The omitted-backup-credit control failed at its intended
independent source-chronology invariant. A later candidate run will supersede the
pre-fix model result; neither is native proof.

The post-fix 28 targeted cases passed again. A post-fix 10,000-case seed 20261032
probe passed 11,287,984 CheckedSteps in 26.10 s. The oracle was then strengthened
to check returned BackupCompleted occurrence time and committed cycle identity
against its independent schedule, plus fresh start/cancel attribution. The final
verifier and later candidate probe will cover that additional check.

## Final full verification and review

Source commit `acd63c72fea362f04584674776cb5a46c992b066` passed the complete verifier from
2026-10-19T09:08:57.105778+00:00 to 2026-10-19T09:09:31.388809+00:00 UTC: **906 executed/passed, zero
failed/skipped, 20 scenarios each twice**. This includes the strengthened backup
identity/time oracle. Intentional NUnit/scenario/invariant failures, missing
medical-start/exposure/backup-credit controls and report overwrite attempts were
rejected; seed reproduction passed. Source inputs (238) match the recorded
commit, and all nine frozen gameplay DLLs match the verifier's closure hashes.
The independent freeze is ignored `runtime/out/emergency-power-verification-20261019`;
it has no long-duration endurance attribution.

Static source checks passed 188 metadata GUIDs, 21 asmdefs and 117 production C#
files. Final independent ultra boundary and model reviews found no blocking
findings after root's fixes. Reviewers did not edit or run builds/native checks.
Unity import, temporary GUI controls, Player, physical feel and multiplayer are
NotRun. Source review and offline results do not advance native/roadmap acceptance.
