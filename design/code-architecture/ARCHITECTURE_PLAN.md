# Runtime Architecture Plan

**Status:** Planning only.

This document defines the intended shape of the future Critical Shift Unity/C# implementation. It is deliberately stricter than a normal prototype structure because the project is expected to grow across many physical systems, multiplayer interactions and facility sections.

## 1. Primary rule

**Game rules should live in plain C# wherever practical. Unity should execute, connect, simulate and present those rules rather than becoming the only place they exist.**

A reactor rule, refinery rule, mine-state transition or inventory operation should not require a loaded scene merely to determine whether the operation is valid.

Unity-specific code is still appropriate for:

- `MonoBehaviour` lifecycle;
- scene and prefab bindings;
- Rigidbody/Collider interaction;
- animation;
- audio/VFX;
- camera and input adapters;
- Unity serialization;
- rendering/UI presentation;
- package-specific networking adapters.

## 2. Planned dependency direction

The exact assembly names may be refined when the Unity skeleton is created, but the intended dependency direction is:

```text
CriticalShift.Core
        ↓
CriticalShift.Gameplay
        ↓
CriticalShift.Features.*
        ↓
CriticalShift.Unity
      ↙      ↘
CriticalShift.UI   CriticalShift.Networking
```

The important rule is direction, not the decorative diagram.

### CriticalShift.Core

Pure C# shared primitives and contracts with no `UnityEngine` dependency.

Examples:

- stable IDs/value objects;
- time abstractions where needed;
- result/error types;
- common state-machine primitives where genuinely shared;
- serialization-neutral data contracts;
- narrowly scoped interfaces.

Core must not become a miscellaneous helper bucket.

### CriticalShift.Gameplay

Authoritative game rules that span more than one feature or provide shared gameplay concepts.

Examples:

- interaction contracts;
- item/inventory rules;
- damage/health state concepts;
- facility progression contracts;
- save-state schemas and migration concepts;
- authoritative game-event contracts.

Prefer no `UnityEngine` dependency here.

### CriticalShift.Features.*

Feature-oriented modules that own a coherent gameplay area.

Likely initial feature families include:

- `Mining`;
- `Cart`;
- `Refinery`;
- `Reactor`;
- `PowerGrid`;
- `Inventory`;
- `Interaction`;
- `Player`;
- `Facility`.

A feature owns its rules, state and public contracts. Internal details should remain internal. A feature may depend on Core/Gameplay public contracts but should not reach into another feature's private implementation.

### CriticalShift.Unity

Unity-facing adapters and composition.

Examples:

- `MonoBehaviour` wrappers;
- Rigidbody adapters;
- trigger/collision translation;
- scene composition roots;
- prefab bindings;
- Unity serialization adapters;
- ScriptableObject-backed configuration where appropriate.

The Unity layer should not become a second copy of the game rules.

### CriticalShift.UI

Presentation only. UI reads public state and sends explicit commands/intent. It must not contain authoritative gameplay decisions.

### CriticalShift.Networking

Package-specific replication/transport adapters after the networking framework is selected.

Authoritative gameplay rules must not be implemented only inside networking callbacks. Network code should translate between replicated messages/state and gameplay commands/state.

Until a networking decision exists, game systems should depend on narrow networking-neutral contracts rather than a speculative package API.

## 3. Feature-oriented repository structure

Do not build a generic directory such as:

```text
Scripts/
  Managers/
  Controllers/
  Helpers/
  Utils/
  Misc/
```

The intended structure is closer to:

```text
Assets/CriticalShift/
  Core/
  Gameplay/
  Features/
    Mining/
      Domain/
      Unity/
      Tests/
    Cart/
      Domain/
      Unity/
      Tests/
    Refinery/
      Domain/
      Unity/
      Tests/
    Reactor/
      Domain/
      Unity/
      Tests/
  Presentation/
    UI/
  Infrastructure/
    Networking/
    Persistence/
  Tests/
    Architecture/
    Integration/
```

This is a planning shape, not permission to create empty folders before they are needed. Structure should grow with real implementation.

## 4. Assembly boundaries

Unity Assembly Definition files (`.asmdef`) should enforce the major dependency boundaries once implementation begins.

Planned rules:

- Core must not reference UnityEngine.
- Gameplay/domain assemblies must not reference UI.
- UI may consume public gameplay contracts but gameplay may not depend on UI.
- networking adapters may consume gameplay contracts but gameplay rules may not depend directly on the selected transport/package;
- feature internals should not become public merely to bypass an assembly boundary;
- circular assembly references are prohibited;
- editor-only code must remain in editor-only assemblies.

Architecture tests should reinforce rules that `.asmdef` files cannot conveniently express.

## 5. Composition instead of service hunting

Dependencies should be wired explicitly at clear composition points.

Avoid architectural reliance on:

- `GameObject.Find()`;
- `FindObjectOfType()`/scene-wide lookup as service location;
- mutable static singletons;
- hidden global registries;
- string-based scene object discovery.

Unity inspector references are acceptable for local scene/prefab composition when ownership is obvious. Larger systems should have explicit composition/bootstrap ownership rather than dozens of objects independently searching for each other.

## 6. No universal GameManager

There must not be one global class responsible for player state, saving, progression, audio, UI, facility machines, networking and scene changes.

Small coordinating objects are acceptable when they have one explicit responsibility. "Manager" is not banned as a word; undefined ownership is the problem.

Any class whose responsibility can only be described as "coordinates everything" should be redesigned.

## 7. State ownership

Each important state must have one authoritative owner.

Examples:

- a mine sector owns its excavation/collapse state;
- an inventory owns its item quantities/slots;
- a reactor state model owns reactor operating state;
- a cart physics body owns its simulated physical state while gameplay systems consume exposed state/events;
- the network replicates authoritative state rather than inventing a parallel competing model.

Presentation may cache derived display data, but it must not become a second source of truth.

## 8. Commands, queries and events

Use explicit operations rather than arbitrary cross-feature mutation.

Conceptually:

```text
Command: TryOpenBlastGate
Command: ApplyMiningEvent
Command: StartRefineryBatch
Query:   CanStartReactor
Event:   MineSectorStateChanged
Event:   BatchCompleted
```

Not every method needs ceremonial CQRS infrastructure. The goal is clarity about who may change state and who merely observes it.

Events should not become a global untyped event bus where dependency relationships disappear. Prefer typed, scoped events with known ownership.

## 9. Data and configuration

Separate authored configuration from mutable runtime state.

Use stable IDs instead of scene names or display strings for authoritative references.

ScriptableObjects may be used for authored configuration/catalogue data where they fit Unity's workflow, but runtime game state should not be accidentally stored in mutable shared assets.

Magic strings and unexplained numeric constants in gameplay logic should be replaced with named configuration or value objects where doing so improves clarity.

## 10. Interfaces and abstraction policy

Create abstractions at real boundaries, not pre-emptively around every class.

Good reasons for an interface include:

- Unity vs plain-C# boundary;
- persistence boundary;
- network/package boundary;
- time/randomness where deterministic testing needs control;
- interchangeable device/service implementations;
- a public feature contract with intentionally hidden internals.

Do not create `IFoo` plus a single `FooService` for every trivial class merely to look architectural. Excess abstraction is another form of spaghetti, only wearing a tie.

## 11. Expected class scope

Prefer small, cohesive classes with explicit ownership.

Warning signs requiring review:

- a class knows about several unrelated features;
- a class frequently changes for unrelated reasons;
- public fields exist only because wiring was inconvenient;
- methods repeatedly reach through several object layers;
- boolean combinations create hidden state machines;
- a file becomes difficult to understand without reading half the repository;
- a class grows because "it was already there" rather than because the responsibility belongs there.

There is no arbitrary universal line-count ban, but unusually large classes require justification and usually indicate missing boundaries.

## 12. Feature change rule

When implementing a feature, the preferred sequence is:

1. identify the state owner;
2. define public contracts/commands;
3. implement testable game rules;
4. add Unity adapters only where Unity behavior is required;
5. integrate through explicit composition;
6. add automated tests at the appropriate level;
7. remove superseded implementation immediately;
8. verify no new dependency inversion/cycle was introduced.

## 13. Planned architecture validation

When the Unity project is created, add automated checks for at least:

- forbidden assembly references;
- Core/domain references to UnityEngine;
- gameplay references to UI/presentation;
- package-specific networking references outside networking infrastructure;
- duplicate authoritative state services where detectable;
- unexpected dependency cycles.

The architecture should therefore fail loudly when a future agent attempts a shortcut that violates a deliberate boundary.
