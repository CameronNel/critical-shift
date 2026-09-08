# Runtime and Architecture Agent Checklist

**Revision 2.0 | Planning only | Entry and handoff requirements**

Start at [README.md](README.md). A first implementation agent reads all linked plans once. A returning agent rereads this checklist, the affected A/S/H contracts and validation cases, the current decision/gate record and the relevant section handoff. Do not rely on previous-chat memory as the source of repository state.

## Before work

- Confirm the requested scope. Planning-only means documentation only: no Unity skeleton, runtime/test code, packages, workflows, scenes/assets or repository-setting changes.
- Read current repository/branch state and search for the existing implementation, contracts and consumers before proposing another system. Note the inspected base commit.
- Use one bounded task branch and one primary author. Do not directly edit main or merge your own work; GAME_SPEC 32.6 governs review.
- Identify the responsibility, sole mutation owner, lifetime, explicit dependencies and relevant rule/test IDs. Distinguish host state, Unity physics state, client projections and authoring data.
- Resolve only decisions needed by this task. Do not silently select a networking, UI/input, persistence, Steam or voice package. A candidate evaluation needs explicit scope before installation.
- Establish acceptance, expected changed paths and deletion/serialization implications. Unavailable runner/hardware/reviewer is a declared blocker for that acceptance, not a reason to invent success.

## Task record

Use a short issue, PR body or feature task note; do not create three copies. These fields must be answerable:

| Field | Required content |
| --- | --- |
| Purpose and non-goals | One bounded user-visible or technical responsibility |
| Baseline and scope | Base SHA, branch, intended files and planning/implementation classification |
| Ownership | Feature/aggregate writer, lifetime, command/query boundary |
| Dependencies | Allowed graph edges added/changed; SDK/configuration decisions |
| Contracts and evidence | A/S/H rule IDs and V test IDs; fixtures; observable acceptance |
| Migration/removal | Replaced path, reference roots, identity/schema changes, deletion ledger or explicit none |
| Risks/decisions | Relevant D/R IDs; needed approvals; unsupported assumptions |
| Review | Primary author; independent reviewer when assigned; no fabricated approvals |

## During implementation, when separately authorized

Keep domain operations separate from engine/transport/presentation. Do not return live mutable owners to UI or network code. Bind dependencies explicitly; avoid global service hunting. Keep commands, leases, epochs, transactions and lifecycle cleanup aligned with the state contracts. Limit abstractions to present consumers. Migrate and remove replaced paths rather than retaining two active authorities.

Preserve serialized and logical identities intentionally. Review dynamic consumers before deletion. Do not delete authoring sources, licensed originals or validation history because they are absent from a Player dependency graph. Fix generated source and regenerate rather than hand-patching only the output.

Unexpected authority, integrity or lifecycle failure is visible and blocks the affected gate. Do not catch and ignore it, retry a resource mutation under a fresh identity, broadly suppress diagnostics or weaken a test to obtain a pass.

## Before handoff

- Inspect the complete diff against the declared base. Remove unrelated changes and ensure the actual touched paths match the authorized scope.
- Verify dependency/owner changes, input-validation and duplicate/stale-command paths; inspect teardown and cancellation as well as startup.
- Execute the relevant checks on the latest revision when tooling exists. Report exact discovered/executed/failed/skipped counts and artifacts. Zero tests or absent results cannot pass.
- Finish the deletion/migration ledger and validate after removal. Explain intentional old names, compatibility fixtures and unresolved candidates.
- Update the affected owner map, decision and test mapping together. Keep the root entry links valid; do not add a competing hidden guide.
- Submit a reviewable PR with evidence and limitations. Do not claim independent review, successful Unity execution, measured FPS or enforced branch protection unless verified.

## Required final handoff format

State: **changed; deliberately not changed; validated; not run/blocked; decisions still open; review/merge status**. Include the commit/PR reference and only real evidence. Planned test names belong under Planned, not Passed. An author's self-review is useful but does not satisfy independent approval.

For this planning revision, documentation consistency/scope checks are applicable. Runtime, compiler, PlayMode, multiplayer, physics, performance and save tests remain unimplemented/unrun by this revision. Do not create them merely to make the handoff sound more complete.

## Stop and escalate the affected scope when

An action would bypass host authority; create a second writer; cross an unapproved dependency; silently install a framework; risk irreversible serialized/save loss; require unsupported joins/migration; retain a replacement indefinitely; or claim readiness without the necessary evidence. Record the exact conflict and the smallest decision or test needed. Continue only unrelated already-authorized work, not a larger speculative rewrite.
