# Timed protective suit fitting, 19 October 2026

Bounded implementation branch `codex/timed-suit-fitting-20261019`, based on
`5814b7e32d8b28a766746ab6e8e27f1093bb5ac8` (draft PR #122, Windows/Ubuntu CI
passed). Primary author: Codex. Independent read-only ultra design/review:
`audit_worker_recovery`. The continuing owner request authorizes useful game
systems without questions. This is implementation, not a planning-only task.

Purpose: let an authenticated worker gain protection through a timed preparation
procedure, following GAME_SPEC 6.1–6.4. A bounded authored station defines a
15–30-second shift-time fitting duration; WorkerState owns a separate immutable
pending attempt and the canonical suit condition. Application composes existing
custody/access/receipt/lifetime behavior. No physical inventory, removal,
continuous movement/stamina penalty, new domain, package or framework is selected.
This slice supplies a preparation-time cost, not the entire suit procedure.

Start derives its worker from the connection, requires Alert/Upright, empty
hands, current worker revision and current station access. One worker may occupy
a station; occupancy derives from the bounded roster. Definitions register during
Setup, up to eight. None/Compromised retain their original protection until an
exact owner completion sets Intact. Already Intact starts no work. Clients supply
no desired suit, duration, target worker or asserted completion.

Busy work blocks movement/grabbing/equipment and another fitting. Exact own-attempt
Cancel remains usable while busy, paused or out of reach; unconditional release
remains safe. Contact eligibility stays Alert/Upright independently of work
availability, so fitting cannot confer immunity to hazards. Completion changes
suit only and preserves contamination, injury attribution, pose and recovery.
Safe contamination revisions preserve the attempt. Impact, trusted suit changes,
station/access loss and disconnect interrupt; cancellation discards progress.

All active Start/Cancel/Complete changes use the ordinary worker revision.
Teardown counts pending work as terminal cancellations and retires the worker
owner without invoking a checked gameplay Cancel during failure cleanup. The
historical closing roster may describe an attempt still pending at the cutoff,
just as it may describe a recovery deadline after the shift; no live attempt or
protection survives teardown. Restart has a fresh epoch and no pending work.

Required polling settles each exact due boundary before terminal publication.
Pause freezes time. Current trusted station availability is polled under the
WorldSession reentrancy guard; unavailable access interrupts. These are sampled
observations, not proof of continuous physical presence. Access is sampled once
at the current projected poll coordinate before historical boundaries. A lost
current sample interrupts there even when completion was overdue; unrelated
backup/contract boundaries cannot backdate it. Native composition must
bind an explicit station/interaction point before exposing its existing temporary
GUI action. Unity import, contact behavior, physical presence, GUI, Player and
multiplayer remain NotRun.

Expected scope: Workers domain attempt/condition, narrow Application typed
intent/workflow/owner settlement/diagnostics, existing native eligibility and
station/GUI composition, focused tests and public-port scenario/model coverage,
affected S01/S02/S03/S07/S08 plus WORKER/CAUSE/LIFE validation mappings. Existing
condition owner, possession and impact receipt streams remain canonical; no
serialized identity is removed. Duration/fixture values remain D-09 prototypes.

Planned checks: exact due/protection, concurrency/busy authority, stale/duplicate/
malformed intentions, pause/cancel/access loss, contamination/injury preservation,
impact/condition interruption, disconnect, deadline and fail-closed cleanup,
source/native eligibility review and full verifier. Planned checks are not passes.

## Independent review and intermediate checks

Read-only ultra reviewers `audit_worker_recovery`, `audit_gameplay_integration`
and `audit_endurance_models` reviewed authority/lifetime, native consumers and
the independent oracle. Root authored every change. Review repairs include the
current-time access attribution, generic worker-revision fields, actual impact
hazard/cause on standalone interruption records, physical gravity/contact
eligibility while busy, and explicit diagnostic labelling for the existing
direct conveyor-reset control. No remaining blocker was found in these scopes.

The model reviewer found a fault-cleanup rethrow if a cancellation-counter
overflow was followed by checked terminal addition. Root removed checked
gameplay mutation from cleanup and uses an explicitly flagged saturated terminal
count when needed. A reflection-injected overflow regression verifies all
workers, connections, targets, timers and process owners are retired. This is
an arithmetic integrity boundary, not a claim that gameplay can naturally reach
that count.

All 40 focused cases passed. The new public-port timed-suit-protection scenario
passed twice, each with 17 steps and 68 assertions. Static checks passed 192
metadata GUIDs, 21 asmdefs and 121 production C# files. Initial builds had zero
warnings/errors. Full verification is pending.

Mixed seed 20261035 passed 10,000 cases / 13,234,387 CheckedSteps in 36.53 s.
The dedicated fitting model uses independent input-driven time, PPE, load,
availability, occupancy, revisions and counters across longer 45–95-second
lifetimes. It forces exposure at due-1 and after exact completion, paused
cancellation, condition interruption and fresh epochs. An omitted modeled suit
upgrade failed the dedicated protection invariant. Subsequent review strengthened
Started event payload/commit/identity checks and forced restored work and both
None/Compromised original suits; the final verifier will execute those changes.
The short mixed production/reactor/clinical rounds additionally start a fitting
and interfere with it, while the longer dedicated model covers completion.

This is a separate, short logical verification candidate. No duration from the
older frozen endurance builds is attributed to this feature. Unity import,
Player, GUI, physical reach/gravity/contacts and multiplayer remain NotRun.

## Final full verification

Source `72a591c3c39214d7e0a69696982cd0a1f26f2545` passed the full verifier
from 2026-10-19T09:50:06.149728+00:00 to
2026-10-19T09:50:40.082502+00:00 UTC: **965 executed/passed, zero
failed/skipped; 22 scenarios each twice**. All 40 focused fitting cases ran.
The real intentional NUnit/scenario/invariant controls and omitted modeled
medical start, exposure, backup credit and suit protection were rejected. Seed
reproduction passed; report create-new checks preserved existing bytes. All 254
recorded source/input hashes match this source commit. All nine frozen gameplay
DLLs match the verifier's assembly closure. Independent ignored snapshot:
`runtime/out/timed-suit-verification-20261019`.

The strengthened final model passed seed 20261036: 10,000 mixed cases /
13,281,822 CheckedSteps in 32.02 s against that frozen closure. This includes
both original suit conditions, verified Started event payload/commit fields,
per-world identity uniqueness and busy-grab/restored-work checks. CheckedSteps
count model samples/selected operations, not distinct assertions or commits.
This short probe is not attributed any older long-duration endurance seconds.

Review found no remaining blocker in the examined authority/lifecycle, native
consumer and model scopes after root's fixes. Unity import/Player, native fitting,
physical reach/motion/contacts, GUI feel and multiplayer remain NotRun. This is a
reviewable prototype and does not advance roadmap acceptance.
