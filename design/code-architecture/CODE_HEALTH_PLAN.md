# Code Health and Safe Removal Plan

**Revision 2.0 | Planning proposal | Safeguards not installed by this document**  
Read with [architecture](ARCHITECTURE_PLAN.md), [validation](VALIDATION_PLAN.md) and [delivery](DELIVERY_PLAN.md). ADR-CA-003 defines the removal policy.

## H01. Definition of done includes removal

An implementation change is complete only when the intended path works, its ownership remains clear, obsolete consumers have migrated, and superseded active paths are removed or covered by an approved bounded migration. A successful compile alone does not establish any of those conditions.

No commented-out alternative implementations, unowned feature flags or indistinguishable Old/New/Final variants belong in active production source. Git history is the fallback for removed work. A deliberately supported legacy save reader is different: it has a named compatibility requirement, fixture, owner and retirement condition. Do not delete necessary compatibility code because its name contains Legacy.

Do not generate unused interfaces, empty feature shells or managers for hypothetical future consumers. Tests and authoring tools are intentional consumers; a type need not appear in gameplay to be legitimate. A public method with no first-party caller is a candidate for review, not automatic proof of dead code.

## H02. Four kinds of dependency must be reviewed

| Dependency kind | Examples | Required check |
| --- | --- | --- |
| Compile-time | Assemblies, namespaces, plugins, generated source | Resolved assembly graph and analyzer report, including platform symbols |
| Serialized/authored | Prefab script GUIDs, field values, UnityEvents, animation callbacks, ScriptableObjects | Unity-aware inspection of declared content roots and migration fixtures |
| Dynamic/runtime | Explicit spawn catalogue, resource paths, reflection, registration, bundle/addressable entries if adopted | Catalogue/registration audit and runtime exercise of those paths |
| Behavioural | Events, timers, ownership transfers, lifecycle callbacks | Contract and lifecycle tests plus reviewer tracing |

No single text search covers all four. Unity's dependency API describes asset references, not a proof of runtime reachability; stripping also requires special care around reflective use. See U4 and U6 in [technical sources](DECISIONS_AND_RISKS.md). Static analysis is useful evidence, not a complete dead-code oracle.

## H03. Reference-aware deletion protocol

For each significant replacement, the PR contains a compact deletion ledger. Required fields: candidate path/type or asset GUID; old responsibility; replacement or reason no replacement is needed; last known consumers; inspected roots/dynamic registrations; migration performed; validation IDs/results; reviewer decision. Several files in one coherent replacement may share a row.

The removal sequence is:

1. Establish current behaviour with a focused regression test or preserved supported-format fixture.
2. Identify the complete affected set: callers, serialized fields, prefab variants, scenes, events, generated registrations, runtime catalogues, tests, importer inputs and docs.
3. Migrate consumers to the one intended replacement. Preserve stable identities or provide a reviewed mapping.
4. Reimport/open affected assets and exercise dynamic paths. A successful IDE rename is not a serialized-content migration.
5. Delete the superseded source and its genuinely unused adapters/configuration/flags. Remove a deleted asset's metadata too; preserve metadata when moving the same asset.
6. Re-run graph, reference, compilation, test and representative Player checks after deletion, not only before it.
7. Search old names/IDs again; explain every intentional match such as compatibility fixtures or history documentation.
8. Record remaining candidates and their classification. No unexplained candidate becomes silently accepted legacy debt.

A scan produces **candidates**. Each is classified Active, Dynamic/Serialized, Test/Editor, Authoring/Evidence, SupportedCompatibility, Generated/Vendor, ProvenObsolete, or Unknown. Only ProvenObsolete is eligible for deletion. Unknown blocks deletion and requires an owner, investigation task and expiry; it does not justify deleting the file or claiming that the codebase is clean.

If old and new implementations must coexist during a staged migration, declare the active production path, explicit routing, owner, supported fixtures, remaining steps and removal deadline. Default expiry is the earlier of 14 calendar days and the next affected production gate. Independent review is required to extend it. Do not leave both paths simultaneously authoritative.

## H04. Unity serialization and identity

Preserve `.meta` files/GUIDs when relocating existing assets. A deleted/recreated metadata file changes identity and may break references. Field renames, type/namespace/assembly moves, prefab variants, UnityEvent method bindings and managed-reference types are different migration problems. Do not assume one rename attribute repairs all of them. Unity documents FormerlySerializedAs for field-value migration; verify the appropriate supported mechanism for other changes in the pinned editor. Sources U5 and U7 cover these distinctions.

A serialization-affecting PR must state the old/new identity or schema, inventory of affected content, migration mechanism, validation fixtures and rollback path. Commit the source and metadata together. Do not hand-edit large scene/prefab YAML as the default migration strategy; use validated editor tooling once available and inspect the resulting serialized diff.

After migration: open/reimport affected scenes and prefab variants; verify required component and object references; invoke affected authored callbacks; test a clean import; and run a representative Player build using the selected scripting backend/stripping settings. Migration attributes and explicit preservation annotations remain until their documented consumers/compatibility obligations are gone. No blanket preservation of entire assemblies merely to hide incomplete reachability analysis.

## H05. Runtime assets and authoring assets are separate scopes

The future runtime content-root inventory includes enabled build scenes, registered spawn prefabs, startup/configuration assets, deliberately loaded resource paths, any adopted bundle/addressable catalogues, and reflection/registration preservation rules. Editor/test fixture roots are tracked separately from shipped roots. Root declarations must name real consumers rather than mark the entire asset tree permanently live.

The asset inventory should detect missing script references, missing GUIDs, duplicate logical IDs, orphaned metadata, obsolete prefabs and unexpected included content. It must not delete source art, raw licensed material originals, deterministic generators, importer inputs or review evidence under `sections/` because a game build omits them. These already have authoring and provenance consumers. A runtime cleanup must not alter visual-production acceptance history.

Generated output is labelled with source, generation command/version and expected destination. Fix the source/generator, regenerate and validate; do not maintain an unrepeatable hand-patched output as the active implementation. Vendor/package code is excluded from first-party style cleanup but included in dependency, license, compatibility and security review.

## H06. Diagnostics and complexity budgets

Hard acceptance conditions after the relevant tooling gate: zero unapproved new first-party compiler/analyzer diagnostics; zero forbidden dependency edges; zero missing required serialized references; zero unexplained duplicate authoritative writers; zero expired exceptions in affected scope; and no known superseded active path left without a migration record. These are scoped findings backed by evidence, not a claim that every possible dead path has been mathematically discovered.

Track third-party diagnostics separately with package/version, diagnostic ID, baseline count, reason and owner. Do not make all vendor warnings fatal by default, or suppress all warnings to obtain a green build. Narrow suppressions require an inline or linked reason. The analyzer set and severity configuration must be proven compatible with the pinned Unity toolchain before it becomes required.

The following are **initial review triggers**, not automatic quality scores:

| Trigger | Review action |
| --- | --- |
| Authored type exceeds roughly 400 logical lines, method exceeds 60, or measured cyclomatic complexity exceeds 15 | Inspect cohesion and branching; split by responsibility only if it improves comprehension. Exclude generated/data-heavy files with a stated reason. |
| A feature adapter gains a peer-feature dependency or an Application workflow touches unrelated use cases | Check the allowlist and ownership before accepting it; prohibited edges are hard failures, not waived by size. |
| New interface, event channel, global lifetime or third-party package | Identify the present consumer/problem and its removal cost. |
| Material growth in warnings, suppressions, allocations, load time or dependency fan-out | Explain the delta against the same fixture/baseline; an unexplained regression blocks the affected gate. |
| A PR exceeds roughly 500 authored source lines or crosses several unrelated features | Split by testable responsibility, or explain why an atomic migration is safer. Documentation, generated artifacts and deletion volume are not measured as ordinary source complexity. |

Do not optimize for small files, high coverage or low class counts at the expense of readable responsibility. A hundred trivial interfaces are not healthier than a small cohesive implementation. Coverage shows executed paths, not assertion quality or production reachability.

## H07. Continuous integration and review responsibilities

[VALIDATION_PLAN.md](VALIDATION_PLAN.md) is the single check/evidence specification. Do not maintain a second conflicting pipeline checklist here.

Every non-trivial PR states its scope, owner, affected rule/contract IDs, dependency changes, tests, deletion/migration impact and known limitations. Code changes do not include unrelated cleanup. Architecture/package/serialization decisions are explicit review items. A planned PR template is described in AGENT_CHECKLIST.md; this revision does not install a GitHub template or workflow.

Following GAME_SPEC section 32.6: use one task branch and one primary author; do not directly edit main; do not self-merge. Independent review may be human or a genuinely separate reviewer acting under project policy, but an author's second self-check is not independent acceptance. Cameron or a designated maintainer controls merge and product scope. Do not claim Tibo reviewed anything unless an actual review exists.

Future branch rules must make required checks and independent review real, with administrative bypasses documented. Their existence must be inspected, not inferred from this policy. If permissions or Unity licensing prevent validation, the result is Blocked/NotRun, not Passed. A maintainer must not mark runtime readiness based solely on a docs-only green check.

## H08. Exceptions and technical debt

An exception record contains ID, exact rule/scope, reason, alternatives considered, present risk, owner, independent approver, creation/expiry dates or gate, compensating test and removal condition. Store it with the affected feature decision/task and link it in the PR. Do not use a global catch-all exception list with no consumers.

A justified analyzer false positive may be suppressed narrowly. A real authority bypass, corrupting save migration, broken required reference, reproducible integrity failure or missing mandatory evidence is not an ordinary style waiver. Stop the affected gate and correct or redesign it. Missing performance hardware means target performance remains unverified; it does not make that test pass.

Avoid permanent debt scaffolding. A TODO/FIXME must identify a tracked local decision/work item or issue and removal condition. A legitimate deferred product feature stays in the roadmap, not as unused stub code in the runtime. Never pre-fill evidence, owners or approval dates for people who have not accepted them.

## H09. Cleanup cadence and evidence

Perform targeted removal/reference review with each replacement PR. Run the full owned-code/content-root health review at physics Gate 1, proof-of-fun Gate 2, vertical slice Gate 5, Alpha Gate 6 and release readiness. Review the touched graph between those gates rather than stopping every small change for a whole-project rewrite.

The gate health record reports forbidden edges; first-party/third-party diagnostics; suppressions and deltas; classified/unresolved removal candidates; known superseded paths; missing/broken required references; expired exceptions; test discovery/pass/fail/not-run counts; hot-path measurements; package/version changes; and supported migration fixtures. Include commit SHA, environment and reviewer. No current runtime baseline is asserted in this planning revision.

A blocking finding stops expansion of the affected subsystem. It does not require unrelated art or approved documentation work to stop. Close the specific integrity gap and rerun its evidence; do not turn cleanup into an indefinite full-game rewrite.
