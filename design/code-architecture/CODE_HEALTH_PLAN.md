# Code Health, Dead-Code and Review Plan

**Status:** Planning only.

This document defines how the future Critical Shift implementation should prevent dead code, duplicate systems and architectural decay from accumulating.

## 1. Definition of done includes deletion

A feature or refactor is not complete merely because the new path works.

If a change replaces an existing implementation, the same change should normally:

1. migrate callers/tests/data;
2. remove the superseded implementation;
3. remove now-unused interfaces/adapters/configuration;
4. remove obsolete assets/prefabs/scenes when safe;
5. update documentation;
6. search the repository for stale references and old names.

Do not keep old code "just in case" in the active tree. Git history already exists for that purpose.

## 2. Prohibited repository habits

The implementation should reject these patterns unless a documented, time-bounded exception exists:

- commented-out legacy implementations;
- `Old`, `New`, `New2`, `Final`, `Final2`, `UseThisOne` parallel implementations;
- orphaned scripts no longer referenced by code, scenes or prefabs;
- duplicate authoritative state models;
- unused serialized fields kept to avoid thinking about migration;
- TODO/FIXME comments without a tracked reason/owner or explicit local explanation;
- broad warning suppression without justification;
- empty abstractions created only for anticipated future use;
- generic `Utils`, `Helpers` or `Misc` dumping grounds;
- hidden static mutable state;
- permanent feature flags for abandoned paths;
- copied logic where one authoritative rule should exist.

## 3. Planned automated gate

Once the Unity project exists, every merge to the implementation branch/main should aim to pass this sequence:

```text
Restore/package validation
        ↓
C# compilation
        ↓
Formatting/style validation
        ↓
Static analysis / Roslyn analyzers
        ↓
Architecture tests
        ↓
EditMode/unit tests
        ↓
Integration tests
        ↓
Relevant PlayMode tests
        ↓
Build validation
```

For multiplayer work, the later gate should extend to deterministic local multi-client smoke tests and runtime error capture as required by `design/ENGINE_DECISION.md`.

## 4. Warning policy

The target is a near-zero warning baseline.

New warnings must not be treated as harmless background noise. A warning may be suppressed only when:

- the warning is understood;
- the code is intentionally correct;
- the suppression is as narrow as possible;
- the reason is documented beside the suppression or in the relevant project configuration.

A repository with hundreds of ignored warnings loses the ability to use warnings as signal.

## 5. Static analysis plan

Select analyzers during Unity-project setup that can reliably run in the chosen Unity/C# environment. The exact package set is intentionally not selected in this planning pass.

The analyzer configuration should target at least:

- unused private members where detectable;
- unreachable code;
- suspicious null handling;
- accidental allocations/per-frame patterns where tooling supports it;
- inconsistent naming and visibility;
- redundant code;
- misuse of async/task patterns if introduced;
- unsafe exception swallowing;
- overly broad suppressions;
- common correctness bugs.

Analyzer severity should be introduced deliberately so the team/agents do not simply disable a useful rule because a first pass produces noise.

## 6. Test layers

### Unit/domain tests

Fast tests for pure C# rules.

Examples:

- mine progression is monotonic;
- collapse rubble persists until removed;
- refinery batch preconditions;
- reactor startup interlocks;
- inventory constraints;
- save-state migrations.

These should not require a scene when Unity behavior is irrelevant.

### Integration tests

Test the collaboration between a small number of real systems/adapters.

Examples:

- pulling a lever sends an intended command and changes the correct machine state;
- completing a refinery batch updates inventory/progression correctly;
- save/load reconstructs feature states without duplicated ownership.

### PlayMode tests

Use Unity runtime/physics only when the behavior actually depends on Unity.

Examples:

- rigidbody cart collision behavior;
- trigger and collider interaction;
- ragdoll transitions;
- scene/prefab wiring;
- physical lever behavior;
- later multiplayer runtime flows.

Do not replace all meaningful tests with slow PlayMode tests simply because the project is a game.

## 7. Architecture tests

The Unity skeleton should include tests/checks that make major dependency rules executable.

At minimum, verify:

- Core/domain assemblies do not reference `UnityEngine`;
- gameplay does not reference UI/presentation;
- feature internals are not referenced across feature boundaries without an allowed public contract;
- networking package namespaces do not leak into authoritative gameplay assemblies;
- editor assemblies do not leak into runtime assemblies;
- forbidden dependency cycles do not exist.

These tests are expected to evolve with the real assembly graph.

## 8. Pull request / change review questions

Every non-trivial implementation change should answer, explicitly or by obvious evidence:

1. What responsibility is being added or changed?
2. Which module/feature owns it?
3. What new dependency is introduced?
4. Is there already code that performs this responsibility?
5. What existing code becomes obsolete?
6. What was deleted as a result?
7. Which tests prove the intended behavior?
8. Does the change create a second source of truth?
9. Does it increase coupling to Unity or a third-party package unnecessarily?
10. Can a future agent identify the active implementation without guessing?

Large changes spanning unrelated features should be split unless an atomic migration genuinely requires them to move together.

## 9. Dead-code sweep after replacement work

For every substantial replacement/refactor, perform a targeted sweep:

```text
Search old type names
Search old namespaces
Search serialized references
Search old ScriptableObject/prefab/scene usage
Search old feature flags
Search TODO/FIXME created by the migration
Run compile + tests
Delete obsolete files/assets
Run compile + tests again
```

Where Unity serialization makes deletion risky, the migration must document the reference transition and validate the affected scenes/prefabs before deleting the old asset.

## 10. Asset dead-code policy

Code hygiene includes Unity assets.

The implementation should periodically detect/review:

- unused prefabs;
- duplicate materials/config assets;
- obsolete ScriptableObjects;
- abandoned scenes;
- duplicate imported meshes/textures;
- editor/test fixtures that leaked into production content.

Do not automatically delete a Unity asset solely because a naive text search finds no reference; serialized/addressable/runtime-loaded references require engine-aware validation.

## 11. Milestone cleanup gates

Perform an explicit code-health review at least at:

- technical prototype/spike completion;
- vertical slice;
- alpha;
- beta/release-candidate preparation.

Each review should inspect:

- dependency graph;
- oversized/low-cohesion classes;
- duplicate systems;
- dead code/assets;
- abandoned interfaces;
- stale feature flags;
- warning/suppression count;
- test gaps;
- package leakage into domain code;
- TODO/FIXME inventory;
- save/data migration debt;
- runtime allocation/performance hotspots where relevant.

Major feature expansion should not continue through serious known architectural debt merely because the current build still launches.

## 12. Refactor discipline

Refactors should preserve behavior and improve structure in controlled steps.

Preferred pattern:

1. establish/strengthen tests around current behavior;
2. make the structural change;
3. migrate callers;
4. delete the obsolete path;
5. run full relevant validation;
6. keep the repository buildable at the merge boundary.

Avoid months-long parallel rewrites unless a written migration plan proves they are necessary.

## 13. Complexity budget

Do not add an abstraction, manager, event layer, service locator, framework or package merely because it might be useful later.

Every new architectural mechanism must solve a present, named problem and have a clear owner.

This applies equally to under-engineering and over-engineering. A hundred interfaces nobody needs are still spaghetti; they are simply alphabetized spaghetti.

## 14. Documentation upkeep

When architecture materially changes:

- update this section;
- update `design/ENGINE_DECISION.md` when the technical stack changes;
- record framework/package decisions rather than silently introducing them;
- keep the architecture diagram and feature ownership current enough that a fresh agent can understand the intended dependency direction before editing code.

The repository must not depend on oral history or one agent remembering why a strange subsystem exists.
