# Decisions, Risks and Source Register

**Revision 2.0 | 8 September 2026 | Documentation proposal for independent review**

This is the decision and uncertainty register for the engineering plan, not a claim that any runtime gate has passed. A/S/H/V references point to documents in this directory. It records decisions here rather than scattering competing mini-ADRs across the repository.

## 1. Established constraints from the inspected repository

Baseline inspected: `8235e7b10ee5cb7ba11d1a90dc6c4677991e20f6`.

| Constraint | Source | Interpretation for this plan |
| --- | --- | --- |
| One to four cooperative players; host owns shared outcomes and clients send intent | GAME_SPEC introduction and section 28 | No silent client ownership of money, material outcomes, health or machines |
| Initial no mid-shift joining and no host migration | GAME_SPEC 28.7 and 37.2 | Between-shift lobby boundary; host loss ends shared play rather than automatic migration |
| Unity 6000.4.3f1, C#, Built-in pipeline, Unity 3D physics recorded | ENGINE_DECISION | Preserve the recorded selection; verify the exact installed/buildable toolchain in Gate 0 |
| Previous Unity implementation removed on 4 September 2026 | README and ENGINE_DECISION current-repository note | Historical prototype claims are not present-day runtime evidence |
| Network physics before expanded content | ROADMAP Gates 0-2; ENGINE_DECISION required spike | Small reproducible fixture and 20-minute multiplayer gate first |
| One task/branch, no direct main edits, no agent self-merge | GAME_SPEC 32.6 | Documentation and code changes go through independently reviewed PRs |
| Gullet depth progression, three independent sectors and persistent 22-piece collapse sets | sections/mine/AGENT_READ_FIRST.md | Separate excavation from obstruction; preserve existing IDs and uncleared rubble |
| Source art and runtime have separate responsibilities | GAME_SPEC 33; section build protocol; Gullet handoff | Do not delete authoring source/evidence as unused runtime content |

The master spec contains older candidate-stack and visual wording. Follow its stated visual override and the recorded engine decision; do not silently switch to an old URP candidate description. A mine-lift reference elsewhere in generic facility vision does not override the approved Gullet no-lift decision. Record a genuine unresolved gameplay contradiction rather than guessing.

## 2. Proposed architecture decisions

These are **proposed** decisions in this PR. Inherited product constraints above remain established; the particular engineering design below awaits independent acceptance. No approver or approval date is fabricated.

### ADR-CA-001: Modular game with explicit reference allowlist

**Decision proposed:** Core is small; feature Domains own rules; Application contains named cross-feature workflows; Unity/presentation/infrastructure are adapters; bootstrap owns construction. A02 is the reference allowlist. Use explicit assembly boundaries when real modules exist, not one assembly per imagined feature.

**Why:** the earlier linear diagram was directionally ambiguous and a shared Gameplay bucket overlapped with Inventory/Player/Facility ownership. The revised model makes writers and coordination distinct.

**Rejected alternatives:** one global GameManager; unrestricted feature-to-feature references; a framework/DI/event-bus layer for every class; dozens of empty interface assemblies. **Trade-off:** some cross-feature work is centralized in Application and needs cohesion review. Split by named use case, not by adding another generic manager. **Reopen when:** a demonstrated boundary requires a peer-domain contract or measurable build/maintenance problem justifies an assembly split. Evidence: ARCH-01 through ARCH-04 and feature ownership review.

### ADR-CA-002: Host commands, explicit state dimensions and bounded transactions

**Decision proposed:** host validated intentions; scoped command identity/replay window; generation-specific custody claims; separate depth/rubble and health/posture/suit dimensions; main-thread prepare/commit for logical multi-owner changes; physical completion tracked separately.

**Why:** duplicate callbacks, stale releases and overlapping writers are plausible failure paths for this game's physical production chain. A collapsed mine must remember opened depth, and a dragged worker can also be contaminated and suited.

**Rejected alternatives:** trusting client-declared outcomes; giant mutually exclusive enums; transferring resources through unrelated event subscribers; assuming Unity physics is lockstep deterministic. **Trade-off:** explicit IDs, receipts and conflict feedback add state that must be bounded and reset. This is not a durable transaction engine or exactly-once network guarantee. **Reopen when:** the selected SDK or measured interaction feel requires a different transport/prediction strategy while preserving host authority and the same invariants. Evidence: CMD/HOLD/TX/WORKER/MINE cases.

### ADR-CA-003: Reference-aware deletion with explicit compatibility

**Decision proposed:** candidate discovery followed by classification, migration, safe deletion and post-removal validation. Serialized/dynamic consumers and supported save migrations are first-class dependencies. Authoring/evidence files have different retention consumers from the Player build.

**Why:** zero text-search matches is not sufficient to delete Unity content or callbacks. **Rejected alternatives:** automatic deletion from grep output; retaining every abandoned version indefinitely; treating build stripping as repository cleanup. **Trade-off:** more deliberate review for serialized changes, offset by bounded migration expiry and a compact deletion ledger. **Reopen when:** proven tooling can replace a particular manual check without narrowing dependency coverage. Evidence: ASSET and DEAD cases.

### ADR-CA-004: Evidence-backed, stage-appropriate acceptance

**Decision proposed:** scope-aware checks, negative fixtures, discovery/result validation, independent review, explicit blocked states and production-gate sequencing. Numeric validation fixtures are ratified before measurement. Manual feel/art review remains distinct from technical checks.

**Why:** paper policies, zero-test greens and stale historical proof do not protect future work. **Rejected alternatives:** trusting exit code alone; author self-certification; imposing a full-game pipeline before a minimal project exists; loosening thresholds after failure without review. **Trade-off:** a missing runner or reviewer can honestly block a gate. **Reopen when:** actual evidence shows a check is ineffective, redundant or disproportionately costly; preserve coverage of its risk before removing it. Evidence: CI-01/02, V00 and work-package/gate records.

## 3. Open decisions and deadlines

Owners below are accountable roles; individual implementation/review assignments are **unassigned** until a work package is authorized. Cameron approves scope/stack decisions; the appointed implementation lead prepares evidence and an independent reviewer assesses it. No package is selected by mentioning it in a source reference.

| ID | Open decision | Due before | Required resolution / what can proceed meanwhile |
| --- | --- | --- | --- |
| D-01 | Exact available Unity editor, compiler/API compatibility, packages/Test Framework, analyzers, backend/stripping, runner/license and `runtime/unity/` root | WP-01/Gate 0 | Reproducible import/test/Player proof and recorded versions. Preserve recorded engine choice or explicitly reopen it. Planning may proceed; installed capability is unverified. |
| D-02 | Networking candidate authorization and final framework/transport selection | Candidate adapter trial, then Gate 1 integration | At most two named scoped trials with identical criteria, one retained production path and recorded limitations. Pure rules/fixture planning may proceed. |
| D-03 | Minimum input and UI/feedback approach; how local and remote intent enters the same API | First playable fixture | Recorded package/API choice, controller/feedback boundary and no SDK leaks. No full menu framework needed. |
| D-04 | Checkpoint boundary, save format/backend, supported versions and migration/pose policy | Any persistent user data is shipped | Choose scoped checkpoint rules and fixtures; prove preservation on failure. In-memory restart is not blocked by deferred saves. |
| D-05 | Steam and proximity-voice integration and package/data handling | Roadmap Gate 5 proofs | Actual compatibility/connectivity/voice evidence and maintenance review. Keep local game logic independent. |
| D-06 | A genuinely new collapse after full clearance: generation/respawn/reward policy | Implementing repeat-collapse behaviour | Resolve against mine source/scenery and get gameplay approval. Existing uncleared-rubble persistence and monotonic depth are already required. |
| D-07 | Minimum supported PC/hardware, resolution and distributed-peer performance budget | Target-performance acceptance, no later than vertical-slice performance claims | Named machines/settings/workloads and measured baselines. Do not equate supplied workstation with minimum spec. |
| D-08 | Shared two-person carry eligibility, actor loss and recovery contract | Enabling two-person carrying | Explicit state/lease policy and tests. First exclusive-carry spike does not need speculative shared-carry implementation. |
| D-09 | Initial numerical fixtures: receipt/queue sizes, lease timing, network profiles, convergence tolerances and resource budgets | First affected acceptance run | Ratify starting proposals in STATE_AND_CONTRACTS and VALIDATION_PLAN, or record alternatives with rationale before testing. Report measurements separately from targets. |

A later-stage open decision does not block unrelated earlier work. It does block a feature that would quietly commit that choice. Defer unused implementation rather than adding placeholder services.

## 4. Risk register

Impact describes consequence if the risk occurs. Likelihood is not quantified: no current runtime evidence exists in this revision from which to derive probabilities.

| Risk | Impact and concrete failure | Mitigation and detection | Gate/owner |
| --- | --- | --- | --- |
| R-01 Networked physics | High: contention, ragdoll or dragging leaves a permanent divergent/locked state | Host claims; N0/N1/N2; HOLD/PHYS tests; reopen stack on failure | Gate 1 / networking-physics implementer plus independent reviewer |
| R-02 Duplicate outcomes | High: retry mints fuel, charges energy twice or releases a new holder | Scoped receipt/lease identities; TX/CMD/HOLD tests and audit trace | Every shared-state gate / affected feature owner |
| R-03 Serialization breakage | High: renamed script/field loses prefab state or callbacks | GUID-preserving migration, affected-root inventory, ASSET tests and Player build | Any serialized change / import-feature owner |
| R-04 Central coordinator growth | Medium-high: Application/Core becomes the new global manager | Narrow workflow cards; no peer internals; ARCH review and change-coupling triggers | Every architecture PR / reviewer |
| R-05 Lifecycle leakage | High: stale callbacks modify next shift or listeners accumulate | Epochs, cancellation, explicit teardown and LIFE/SHIFT tests | Gate 1 and complete shift / session owner |
| R-06 Incorrect cleanup | High: naive unused scan deletes runtime-loaded assets or valuable authoring source | Four dependency classes, candidate classification and DEAD controls | Refactors/imports / author plus reviewer |
| R-07 False evidence | High: zero tests, stale build or unavailable runner is called successful | Discovery/result validation, negative controls, exact commit/environment | Gate 0 onward / tooling owner |
| R-08 Scope growth before proof | High: expanded facility built on unstable carrying or weak causal loop | Stage gates, smallest fixture, rejected trial deletion | All gates / product owner |
| R-09 Performance assumption | Medium-high: local/Blender result is sold as supported runtime FPS | Named hardware/build/workload, percentile/counter evidence, D-07/D-09 | Performance claims / runtime lead |
| R-10 Inconsistent authorities | Medium-high: historical prototype, old renderer text or generic lift overrides current decisions | Baseline/source register; contextual engine note; scoped conflict resolution | Any planning/implementation change / reviewer |
| R-11 Overengineering | Medium-high: abstractions and process outgrow the small game | No empty feature shells; targeted PR checks; responsibility-based review | Gate 0 and every expansion / implementer-reviewer |
| R-12 Save corruption | High: migration/replacement overwrites only good copy | Detached validation, previous-good preservation, SAVE fault cases | Before persistent release / persistence owner |

## 5. Reviewer challenge pack

An independent reviewer should attempt to break the plan, not endorse its terminology. Trace these cases to a writer, a contract, a failure outcome and a test:

1. A rejects insertion for a real gameplay reason; can A still send the next command? Is the rejection a terminal receipt rather than a permanent sequence gap?
2. Two players claim a crate; the loser retries; the winner disconnects during physical attachment. Which lease and joint are removed?
3. A machine finishes while a duplicate callback arrives and a view throws an exception. Can material or power be counted twice?
4. A deep mine collapses, one piece is cleared and a smaller blast arrives. Which depth and rubble values survive, and which IDs are displayed?
5. A worker is suited, contaminated and unconscious while being dragged. Which subsystem controls health, custody and physical motion without contradictory writers?
6. A serialized field/type moves, or a callback has no C# callers. What evidence prevents accidental deletion or silent value loss?
7. A task completes after scene teardown and a new shift starts. What prevents its callback from finding a different object and modifying it?
8. CI discovers no tests or a required runner is unavailable. Can the proposal still be reported as a passed runtime gate? It must not.
9. A developer needs one lever. What prevents this plan from forcing an inventory framework, twenty assemblies or a new event bus first?

Review readiness is not production readiness. Open D decisions, unimplemented gates and unmeasured performance remain explicitly outstanding even after a reviewer accepts the document structure.

## 6. Source register

### Repository authorities inspected

- [GAME_SPEC.md](../GAME_SPEC.md): particularly sections 2.7, 4.3, 28-33 and 35-38. Supplies scope, authority, physical-state requirements, agent policy and test intent.
- [ENGINE_DECISION.md](../ENGINE_DECISION.md): recorded stack, required spike and repository-reset caveat. Historical supporting evidence is not revalidated by this proposal.
- [ROADMAP.md](../ROADMAP.md): gate order and human acceptance; engineering packages are subordinate to it.
- [Root README](../../README.md) and [AGENTS.md](../../AGENTS.md): current repository purpose and agent entry points.
- [Gullet handoff](../../sections/mine/AGENT_READ_FIRST.md): independent progressive sectors, 22-piece collapse sets, authoring/runtime separation and unresolved Unity/art acceptance.
- Original architecture/index/health/checklist documents at the inspected baseline: replaced, not retained as parallel active guidance.

### Primary technical references consulted on 8 September 2026

These support narrow Unity mechanisms, not the proposed architecture as a whole. The Unity 6.0 and Test Framework 1.4 documentation below is reference material; it is **not** verification of compatibility with the recorded 6000.4.3f1 target. D-01 requires validating the actual pinned editor/package behaviour and updating references where needed. No external implementation code is copied into this proposal.

| ID | Source | Specific point used |
| --- | --- | --- |
| U1 | [Unity: Referencing assemblies](https://docs.unity3d.com/6000.0/Documentation/Manual/assembly-definitions-referencing.html) | Reference direction, prohibited cycles, automatic/plugin references and GUID reference behaviour |
| U2 | [Unity: Assembly Definition Inspector](https://docs.unity3d.com/6000.0/Documentation/Manual/class-AssemblyDefinitionImporter.html) | No Engine References and the distinct scope of assembly properties |
| U3 | [Unity: Domain reloading](https://docs.unity3d.com/6000.0/Documentation/Manual/domain-reloading.html) | Retained static state/subscriptions when reload is disabled; lifecycle reset obligations |
| U4 | [Unity: Preserving code using annotations](https://docs.unity3d.com/6000.0/Documentation/Manual/managed-code-stripping-preserving.html) | Dynamic/reflection references can need preservation; static stripping is not a complete usage oracle |
| U5 | [Unity: Asset metadata](https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html) | Metadata/GUID identity must travel with moved assets |
| U6 | [Unity: AssetDatabase.GetDependencies](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AssetDatabase.GetDependencies.html) | Reports referenced assets, not a proof of all runtime consumers or build necessity |
| U7 | [Unity: FormerlySerializedAs](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Serialization.FormerlySerializedAsAttribute.html) | Preserving serialized field values during a field rename |
| U8 | [Unity Test Framework: command-line tests](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html) | Test selection and result output need explicit invocation/result handling |

Numeric tolerances, window sizes, complexity triggers, ownership splits and delivery boundaries are proposed project engineering choices. They are not standards, vendor guarantees, measured results or independent approvals.
