# Timed isolated jam clearing, 19 October 2026

Branch `codex/timed-jam-clearing-20261019`, based on
`6b4587ba` (draft operational-readout PR). Primary author: Codex.
Independent read-only ultra design/boundary review: `audit_shift_boundaries`.
The continuing owner request authorizes useful game implementation.

Purpose: make recovery from an authored machine jam consume shift time, within
the existing MachineState/Production workflow. Recipe authors an optional
bounded repair duration; zero retains the older instant fixture behavior.
Canonical crusher/processor opt into 6/8-second isolated clearing. This is an
autonomous machine-owned clearing stage once started, not a new worker-held
repair procedure, tool inventory, package or electrical allocation system.

Repair requires Jammed with power isolated. Positive duration enters Repairing,
preserving original conversion/cycle/input reservation and frozen processing
work. Repair work advances on the canonical shift clock; pause freezes it.
Completion leaves power isolated and state PowerPaused. Restoring power and
explicit Resume remain required. Power restoration during clearing rejects;
repeat Repair returns NoChange without restarting progress. Existing isolated
CancelCycle cancels the whole cycle, discards repair progress and preserves input.
Operator impact/disconnect does not cancel already-started autonomous clearing.

RepairStarted/RepairCompleted facts retain original cycle/material attribution.
Completion occurrence uses repair-work delta, not frozen processing work.
Large polls cannot turn leftover repair time into production work. Required
production settlement already precedes terminal publication; no new global timer
or cross-owner deadline is needed. Bounded accumulated work avoids an absolute
due-time overflow. Definitions/modes append compatibly; no serialized identity
or owner is removed. D-09 authored durations remain prototype balance.

Expected files: existing Production domain/state and Application recipe/view/
workflow, canonical setup/scenario authoring, readout/native feedback consumers,
focused tests/scenario/model and S01/S03/S05/S08, TX/CAUSE/LIFE mappings.
Planned checks: isolation, no early resume/eject, progress/retries/cancel,
pause/deadline/large-versus-partitioned settlement, original input/lineage/history,
operator loss, overflow fail-closed cleanup and required owner ordering.
Native import, GUI, keys, physical behavior and multiplayer remain NotRun.

## Intermediate validation and independent review

All 19 focused cases passed with zero failures/skips. The new versioned
timed-jam-clearing scenario passed twice: 20 steps and 85 assertions per run.
Its pause interval advances host time without consuming clearing time; exact
completion leaves power isolated and no conversion output, followed by explicit
power restoration/resume and conserved 8 output + 2 waste from 10 input units.
Builds had zero warnings/errors.

Independent read-only ultra boundary and native-consumer reviews found no
actionable defect. Root authored all changes. Reviewers did not execute tests
or native code. The appended mode is handled in contextual input, feedback,
readout and trace consumers; repair does not count as a completed conversion.

TimedRepairSoak derives power, mode, separate work, revisions, exact events,
pause/terminal state and conserved material from authored inputs and requested
operations before invoking Application. It binds only the opaque fresh cycle ID
after validating the initial start. Each case forces a complete clearing with
midpoint pause/rejections, then random power/resume/cancel/replay operations.
The mixed multi-owner worlds also author positive repair durations. A deliberate
omission of only the modeled clearing-completion transition failed case seed55
at the specific isolation-ledger mode invariant, rather than an unconditional
failure. A 10,000-case randomized run with seed20261038 passed 13,847,608
checked steps in 32.028 seconds. Checked steps count modeled observations and
selected operations, not distinct assertions. Full verifier/final source evidence
remains pending; older preserved long probes do not cover this revision.

The first full verifier at source968648ca passed 1,022 tests and 23 scenarios
each twice. A third ultra model review identified two bounded coverage gaps,
then root strengthened the checks before final verification: event payloads now
validate machine and material projections, and each mixed lifetime forces an
isolated jam clearing to start while medical treatment, reactor generation and
backup work are active. Returned typed changes, not the bounded trace, prove
repair completion at its due coordinate. This avoids depending on retained
diagnostic history when trace capacity is deliberately one record. The deliberate
mode-transition omission still fails its named invariant after strengthening.
