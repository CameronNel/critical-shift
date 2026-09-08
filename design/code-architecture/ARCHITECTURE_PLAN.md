# Architecture Plan

**Revision 2.0 | Planning proposal | No implementation**  
Read with [state contracts](STATE_AND_CONTRACTS.md), [validation](VALIDATION_PLAN.md) and [decisions](DECISIONS_AND_RISKS.md). Proposed decisions ADR-CA-001 and ADR-CA-002 govern this document.

## A01. Shape: a modular game, not a framework

Use a modular monolith: one Unity application with bounded feature modules. The purpose of a module is a coherent responsibility, not a folder quota. Do not introduce microservices, a custom dependency-injection framework, a universal event bus, event sourcing, generic repositories, an interface for every class or a replacement physics engine.

Pure C# rules should run without a Unity scene. This does not mean the entire game is deterministic or engine-independent. Rigidbody motion, collision contacts, animation and rendering remain Unity concerns. Rule tests receive explicit time, inputs and any required random stream; physics acceptance tests use invariant/tolerance checks, not promises of bit-identical networked physics.

There is no general `Gameplay` bucket containing a second inventory, player state or facility model. Shared concepts have a named owner. Extract a reusable abstraction only after a real boundary or a second concrete consumer justifies it. Names such as Manager are not intrinsically prohibited; a class with unrelated responsibilities is.

## A02. Exact dependency direction

**In this document `A -> B` means A may reference B.** It does not mean execution order or an event travelling from B to A.

```text
Bootstrap -> instantiated adapters and Application
Adapters  -> Application / their explicitly allowed contracts
Application -> instantiated feature Domains
Feature.Domain -> Core
Core -> approved .NET base libraries only
```

The following is a maximum allowlist, not a requirement to add all references. An unlisted project dependency is denied until a reviewed decision changes this table. All names have the `CriticalShift.` prefix.

| Assembly role | May reference | Must not reference |
| --- | --- | --- |
| Core | Approved base libraries | UnityEngine, UnityEditor, feature code, SDKs, disk/network services |
| Features.<F>.Domain | Core | Other feature Domain implementations, Application, Unity, presentation, SDKs |
| Application | Core; Domains actually used by named workflows | UnityEngine/UnityEditor, adapter assemblies, SDKs, rendering, filesystem implementation |
| Unity.Shared, only if needed | Core; UnityEngine | Application workflows, feature rules, networking SDK, mutable global services |
| Features.<F>.Unity | Its own Domain; Application; Core; Unity.Shared if present; UnityEngine | Another feature's Unity implementation, networking/Steam/voice SDKs, UnityEditor |
| FacilityPhysics.Unity | Application; Core; Unity.Shared if present; UnityEngine | Feature internals, inventory rules, SDKs; it is limited to shared physical adapters such as cart/conveyor in the first spike |
| Presentation | Application command/query views; Core; Unity.Shared if present; approved UI/input presentation dependencies | Domain instances and mutators, networking authority, save implementation, UnityEditor |
| Infrastructure.Networking | Application command/snapshot contracts; Core; Unity.Shared if needed; selected networking SDK and Unity dependencies | Feature Domain internals, authoritative production/health rules, presentation implementation |
| Infrastructure.Persistence | Application snapshot/migration ports; Core; approved serialization/storage dependencies | Live Domain instances, UI, networking SDK, scene searching |
| Bootstrap | Explicitly instantiated runtime modules and adapters | Test assemblies, UnityEditor, gameplay-rule ownership |
| <F>.Editor | Required runtime contracts; UnityEditor and importer APIs | Inclusion in a Player build |
| Test assemblies | Their declared subjects and fixtures | Being referenced by production assemblies or included as production content |

Application exposes purpose-specific immutable views and command ports. It does not give presentation, storage or transport a mutable Domain instance. A serialization-specific DTO is a representation, not another state owner. Do not promote Domain internals to public merely to satisfy a mapper.

A feature Domain needs no peer reference in the initial model. Cross-feature orchestration belongs in an Application workflow. If a future domain relationship genuinely warrants a direct reference, record its direction, contract ownership and cycle analysis first. Moving everything into Core to evade the rule is not acceptable.

## A03. Assembly enforcement is necessary but incomplete

Use assembly definitions at actual boundaries. Pure Core, Domain and Application assemblies must omit engine references. Configure explicit project references and control precompiled-plugin references. Unity's Auto Referenced setting concerns predefined-assembly references; it does not by itself isolate arbitrary feature assemblies or remove code from the build. Override References concerns precompiled DLL references; do not confuse it with the project-assembly allowlist. See technical sources U1 and U2 in the [source register](DECISIONS_AND_RISKS.md).

No first-party runtime source may silently fall into a predefined catch-all assembly such as Assembly-CSharp. Editor and test code need explicit inclusion/exclusion rules. Inspect the resolved editor and Player graphs, including implicit plugin references, build symbols and transitive engine/package leakage. An asmdef filename alone proves none of this.

Assembly boundaries reject forbidden references and cycles. They cannot prove that two different classes model the same business fact, that a workflow is cohesive, or that an event graph makes sense. Those require the owner catalogue, architecture tests and review. Negative test fixtures must demonstrate that the future checks detect deliberate violations; the future checker must not validate only its own static allowlist.

## A04. Future source layout and initial size

Proposed engine-project root: `runtime/unity/`. Confirm this in Gate 0; do not create it during this planning revision. Keep `Assets`, `Packages` and `ProjectSettings` together there rather than mixed with Blender sources or design documents.

```text
runtime/unity/
  Assets/CriticalShift/
    Core/
    Application/                 named workflows, neutral command/query ports
    Features/<feature>/
      Domain/
      Unity/
      Editor/                   only when needed
      Tests/                    explicit test assemblies
    FacilityPhysics/
    Presentation/
    Infrastructure/Networking/
    Infrastructure/Persistence/
    Bootstrap/
    Content/                    deliberate runtime imports; provenance retained
    Tests/Architecture/
    Tests/Integration/
  Packages/
  ProjectSettings/
```

This is a placement plan, not an instruction to create empty folders or assemblies. The first physics spike needs only the rules for interaction claims and worker physical-state transitions, their Unity adapters, small Application workflows, physical cart/conveyor adapters, bootstrap and tests. Add the selected transport adapter only after its time-boxed evaluation is authorized. Core and Unity.Shared stay minimal; omit Unity.Shared until there is genuinely shared adapter code. A crate does not require a full economy or RPG inventory system.

Introduce Mining, Materials, Production and Reactor domains only at their relevant delivery steps. Do not produce a skeleton for every planned feature or an assembly per script. The dependency table controls boundaries when a module exists; the owner catalogue records future responsibility without demanding implementation today.

## A05. Feature and workflow contracts

Every implemented feature gets a short local README recording: responsibility and non-responsibilities; mutation owner and lifetime; public inputs/outputs; allowed dependencies; active implementation paths; authored configuration; failure/recovery; test IDs; and any migration/exception. This is a feature card, not a second architecture manual.

Domain APIs express operations, not unrestricted setters. A machine cannot be put into Processing just because a caller toggles a field. It validates its own preconditions and emits a result. Cross-feature actions such as inserting a batch, reanimating a worker or applying a mine consequence are named Application workflows. One workflow handles one use case; Application must not become a renamed GameManager.

Use synchronous method calls for local request/response. Use typed, scoped notifications for committed facts. No global string-topic bus, hidden subscription chains or reflection-based handler discovery as the default architecture. Each event contract records producer, intended consumers, lifetime and whether delivery is required or cosmetic. Consumers do not synchronously re-enter an owner mid-commit.

An input or network adapter requests an operation. A host workflow decides it. A projection reports the committed revision. An animation, lamp or HUD does not infer a new authoritative state from its current appearance.

## A06. Composition and lifetime

Explicit composition creates dependencies, validates required references and then activates the system. Scene names, hierarchy paths, scene-wide Find calls and ambient service locators are not the normal wiring mechanism. Inspector references and deliberate local GetComponent-style binding are acceptable where ownership is clear. A composition-owned ID registry is explicit infrastructure, not a mutable static registry available to any code.

| Lifetime | Owner | Start boundary | End boundary |
| --- | --- | --- | --- |
| Application process | Bootstrap | Start application and load configuration | Application exit |
| Connection | Networking adapter | Authenticated lobby connection | Disconnect/connection replacement |
| Gameplay world/session epoch | Session coordinator | New shift or restored world generation | Shift teardown, restart, host loss |
| Section views/physics bindings | Section binder | Validated scene loaded for current world | Section unload or world teardown |
| Feature aggregate/entity | Named feature owner | Explicit registration/spawn | Explicit removal or world teardown |
| Presentation subscription | View/controller that subscribed | Bind/enable after composition | Unbind/disable/destruction |

Bootstrap performs construction, not gameplay updates. Session coordination owns start/stop, not every machine's state. Unity callbacks collect local references and delegate; gameplay readiness does not depend on incidental Awake/Start order.

Startup sequence: validate package/configuration compatibility; establish host/client role; create a fresh world epoch; construct host owners or client replicas; bind stable IDs; validate references and colliders; subscribe consumers; signal Ready; enable input and simulation. Missing required IDs, duplicate bindings or unknown definitions prevent Ready with an actionable report. Optional decoration can degrade without fabricating gameplay readiness.

Teardown sequence: stop accepting new commands; mark the world stopping; settle or cancel pending operations; release claims and controlled attachments; cancel timers/tasks; unsubscribe; remove section bindings; dispose world-owned objects; advance the epoch before another world accepts input. Teardown must be idempotent. The next run must not reuse stale subscriptions, receipts or scene references.

Async work is permitted only with a defined owner, cancellation and error path. Authoritative mutation occurs on the designated simulation thread. A background result returns with its world epoch and is discarded if that world no longer exists. Never retain a MonoBehaviour, Rigidbody or mutable aggregate inside a background save/network operation.

Domain/scene reload defaults remain enabled until the lifecycle tests pass with the proposed alternative settings. Unity documents that disabled domain reload retains static fields and event subscriptions unless explicitly reset; see U3. A narrowly scoped engine startup hook is not a license for mutable static gameplay state.

## A07. Data, identity and simulation boundaries

Separate immutable authored definitions, mutable host-owned state, client/read projections and versioned save snapshots. ScriptableObjects may supply authored definitions. Copy/validate values for runtime use; do not mutate shared asset files as the session database.

Use stable logical IDs. Display labels and scene object names are not identity. Unity asset GUIDs identify assets, network object IDs identify transport instances, and logical entity IDs identify gameplay objects. Record the mapping; do not assume they are interchangeable. World epochs prevent delayed operations targeting newly created objects with coincidentally similar IDs.

The host advances game-time rules using a controlled simulation clock. Command receipt, leases and disconnect timeouts use a monotonic host clock appropriate to their unscaled lifecycle. Wall-clock changes or a client's timestamp must not control outcomes. Pause policy and simulation timestep are explicit configuration decisions, not inferred from frame rate.

State models can be deterministic under fixed inputs without Unity physics being deterministic across peers. Physics produces observations on the host; domain/application rules interpret validated observations. Clients smooth visuals. Do not maintain an independent client economy/reactor simulation that can contradict the host.

## A08. Authoring-to-runtime boundary

Blender is the visual source, not a second live multiplayer simulation. Section Python preview controls and historical renders are authoring/validation artifacts; they are not dead runtime code merely because Unity does not reference them.

Each imported section must eventually have an explicit binding manifest: source revision; export/import settings; scale, axes and origin; logical section/entity IDs; mesh/prefab mappings; collider and trigger roles; spawn/interaction points; state variants; material conversion; licensing/provenance; and the runtime owner consuming each binding. Runtime imports belong in the engine project; original sources and art evidence remain in their section package.

For the Gullet, preserve the approved shallow descent, absence of a mine lift, independent sectors and persistent rubble identifiers. Runtime state selects the correct authored variant; hiding a render mesh alone does not prove collision, navigation or network agreement. The material-review handoff explicitly leaves Unity integration and final art acceptance outstanding. A runtime prototype cannot upgrade that status by assumption.

## A09. Change boundaries and exceptions

Any change to dependency direction, mutation ownership, serialization identity or an infrastructure package requires a decision entry before implementation. The reviewer checks the affected graph, state contract, migration and evidence. The exception procedure is in CODE_HEALTH_PLAN.md. Do not weaken a rule in the same patch that violates it without exposing that change prominently.

Practical review questions: can this feature be tested without loading unrelated scenes; can a fresh reviewer identify its writer; can its external effects be traced; can it be removed without breaking an unrelated feature; and is every abstraction serving a present use case? A diagram is insufficient unless these answers remain clear.
