# Staged Engineering Delivery Plan

**Revision 2.0, with OFFLINE-001 clarification | Planning document | A work package requires its own implementation evidence**

This plan supplements [ROADMAP.md](../ROADMAP.md); it does not replace its production gates or authorize future implementation. Work-package IDs are local planning references, not claims that GitHub issues have been created. Acceptance criteria are specified in [VALIDATION_PLAN.md](VALIDATION_PLAN.md).

## 1. Roles and decision authority

Cameron remains product/engine decision owner as recorded in the repository. For each authorized work package, appoint one primary implementing agent and one independent reviewer before work starts. A named individual is not assigned merely because their name appears in a conversation. An implementer cannot supply their own independent approval. A maintainer controls merge under the repository's no-self-merge policy.

The implementation owner produces the design change, bounded source change and evidence. The reviewer examines behaviour, dependencies, deletion/migration and unverified claims. Product decisions affecting scope or gameplay go to Cameron; technical departures use the decision register. If no independent reviewer is available, prepare the branch/PR and report that acceptance is pending rather than silently bypassing the rule.

## 2. Minimum sequence

| Package | Bounded deliverable when separately authorized | Entry condition | Exit evidence / blocker |
| --- | --- | --- | --- |
| WP-00 Planning baseline | This architecture/state/health/validation proposal | Existing design/spec reviewed | Docs-only scope, linked rules, explicit decisions and independent acceptance. Status: proposed; no runtime claim. |
| WP-01 Reproducible foundation | Minimal Unity project at agreed runtime root; pinned editor, package/compiler/backend profile; documented clean import/test/build invocation | WP-00 accepted; D-01 decided; Unity runner/license actually available | Clean checkout imports, discovers a real test, builds/starts/stops a minimal Player. Engine-specific ignore rules and external MCP are validated; an agent makes a bounded scene change, runs it and inspects errors. Block if any required capability cannot be reproduced. |
| WP-02 Boundary and evidence checks | Explicit asmdefs, diagnostics baseline, resolved-graph checks, test-discovery failure controls and initial content-root inventory | WP-01 working | ARCH-01/02/03, CI-01/02 and DEAD-02, plus an actual Unity CI smoke run on the stated revision. Deliberate violations fail; removal restores pass. Block gameplay expansion if safeguards only exist on paper. |
| WP-03 Small interaction/worker rules | Claim/lease/sequence rules, orthogonal worker state and session lifetime; playable basic character controller; one crate, feedback, cart/conveyor/lever fixture | Full Roadmap Gate 0 evidence; D-03 minimal input/feedback choice; D-09 initial fixtures ratified | CMD, HOLD and LIFE cases at the lowest suitable layer; single-host PHYS behaviour; ordinary movement, turning, stopping, slopes/steps, collision and recovery demonstrated with the actual controller. No Materials/Reactor/whole-facility framework generated. |
| WP-04 Networking evaluation | At most two approved candidate adapters evaluated on the same isolated fixture, then one selected adapter | D-02 authorizes named candidates and comparison criteria; WP-03 fixture | Explicit result/limitations on authority, contention, disconnect and physics; recorded package decision. Remove rejected candidate from active production paths before integration. |
| WP-05 Networked physics acceptance | Two-peer smoke followed by four-peer physics room, playable controller and lifecycle tests | WP-04 chosen adapter; same command path for host and clients | Required N0/N1/N2 and Gate 1 soak evidence, ordinary character movement on host and clients, clean restarts and independent feel review. Static worker bodies cannot satisfy controller acceptance. Block content expansion on unstable claims, movement, ragdolls or teardown. |
| WP-06 Radioactive Shoebox | One bounded ore-to-fuel-to-reactor chain, cooling/demand, one shortcut and one causal consequence | Roadmap Gate 1 actually passed | TX, CAUSE and POWER cases; roadmap Gate 2 human communication/fun evidence. No larger content catalogue compensates for a weak loop. |
| WP-07 Social pressure | One infiltrator, legitimate suspicious worker and compliance interaction, through existing command boundaries | Roadmap Gate 2 passed; scoped feature cards | NPC authority/evidence checks and Gate 3 human acceptance. Avoid privileged scripts bypassing custody/health rules. |
| WP-08 Complete shift | Existing systems integrated through briefing, escalation, recovery, terminal outcome, debrief and clean restart | Roadmap Gate 3 passed | SHIFT and full worker/reanimation/causality checks; a complete 20-35-minute round per roadmap Gate 4. |
| WP-09 Vertical-slice integration | Small mine and declared refinery/reactor content; three-shift operation; tutorial; Steam/voice proofs at their gate | Roadmap Gate 4 passed; D-05 and relevant mine/data decisions resolved | MINE contracts, section binding/runtime evidence, applicable checkpoint tests, external playtest acceptance for Gate 5. Art acceptance remains a separate requirement. |
| WP-10 Alpha/release hardening | Supported saves, menus/accessibility/controller scope, broader incidents and release automation according to roadmap | Previous production gates passed; D-04/D-07 resolved before affected delivery | Supported schema migrations, fault injection, full health review, target-hardware results and release evidence. No unsupported durability/FPS claims. |

WP-01 and WP-02 establish Roadmap Gate 0 only with **all** of its engine, external MCP, ignore-rule, local/CI validation and agent scene-change evidence. WP-03 through WP-05 establish Gate 1 only with a responsive playable controller as well as networked physical interactions. These clarifications address the two missing gate conditions raised in the independent review of PR #39. Later packages map directly to the existing roadmap. A package is not complete because its files exist; all relevant exit conditions require actual evidence. A later feature can be designed in advance without implementing it or declaring its gate passed.

### OFFLINE-001: expressly authorized non-Unity prework

On 8 September 2026, Cameron requested useful coding without starting Unity or using his Unity-capable PC. The bounded [offline interaction slice](../../runtime/dotnet/README.md) implements exclusive claims, ordered receipts, lifecycle rules and their .NET tests under `runtime/dotnet/`. Its local decision records the conservative API/language target, test-only tooling and single-source integration requirement.

This is permission for that isolated engine-independent work before Unity tooling is available, **not** permission to mark WP-01, WP-02, WP-03, Gate 0 or Gate 1 complete. Offline compilation and tests supply only the named rules' partial evidence. The exception does not authorize a fake physics engine, unselected transport, full game framework, silent runtime package choices or content expansion. Unity integration must later consume the same implementation or migrate it once, not create a competing copy. Code review remains required; the prior owner-authorized merge of planning PR #39 was not blanket permission for future self-merges.

## 3. Candidate spikes without permanent duplicate systems

The networking decision must be evidence-led, but a trial adapter is needed to gather that evidence. Resolve the apparent circularity explicitly: authorize a bounded candidate evaluation first; isolate it on a task branch/fixture; state what must be measured; choose only after the results; then retain one integration path. A candidate trial is not a silent production package selection.

Use the same control/custody/physics scenarios and environment for candidates. Compare supported editor/build compatibility, authority APIs, contention recovery, latency behaviour, multi-process diagnostics, cleanup, integration burden and package/license maintenance. A feature checklist alone does not outweigh a failed required invariant. Do not write a universal transport abstraction trying to support every package; keep only the ports required by the current game contract.

If required networked physics cannot meet the accepted gate, record the evidence and reopen the engine/networking decision as ENGINE_DECISION.md requires. Do not spend the failure budget on more rooms, art, custom networking frameworks or a hidden client-authority shortcut.

## 4. Work-package readiness and handoff

Before coding, the task record identifies feature responsibility, state owner, allowed dependency changes, relevant A/S/H rules and test IDs, expected touched paths, existing implementation search, deletion/migration needs, open decisions, and definition of done. For a planning task, the touched paths must remain documentation and runtime checks must be reported unrun.

A ready-for-review handoff includes the exact commit, comparison to base, executed checks and full result locations, unexecuted checks with reason, deliberate behaviour changes, obsolete-path removal, known risk and proposed next task. Do not paste a list of planned checks into the Passed section. Gate acceptance needs an independent reviewer and durable evidence on the accepted revision.

Material architecture changes update the decision register and the owner/dependency/validation rows in the same PR. Avoid huge unrelated refactors. When a change truly must be atomic, explain why splitting it would leave broken serialization, half a transaction or two active owners.

## 5. Scope and cost controls

- No empty assemblies or features solely to match the catalogue. Start with interaction, worker transitions and minimal session orchestration.
- No full save system before checkpoint/supported-schema decisions. In-memory reset must work much earlier.
- No Steam/voice dependency in pure gameplay. Their proofs belong at the roadmap gate, not in every local test.
- No mid-shift join, host migration, dedicated-server architecture or custom lockstep physics added by this plan.
- No environment expansion used as evidence that runtime risk is solved. The Gullet's Blender material review is not Unity acceptance.
- No blanket testing bureaucracy for every typo. Documentation scope gets document validation; runtime changes get the relevant suites and mandatory shared-state smoke.

These are sequencing constraints, not permanent rejection of later approved vision. Reopening scope requires a recorded product decision and corresponding contract/test updates.

## 6. Gate record and cleanup

The future gate record stores: roadmap/work-package ID; accepted revision; implemented checks; execution status/counts; artifacts; configuration; reviewer; unresolved decisions; approved exceptions; and cleanup findings. At each health milestone, publish the metrics in H09. Keep a concise durable summary and evidence locations, not duplicated megabytes of logs across documents.

A serious integrity/authority/reference issue blocks the affected subsystem's gate. A missing runner blocks validation rather than justifying invented results. Unrelated authorized planning/art tasks and the explicit offline prework above may proceed, but no stage gets marked passed by assumption. This document remains a plan; each implementation's actual status belongs in its task/PR evidence rather than being inferred from this table.
