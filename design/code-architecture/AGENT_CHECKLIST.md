# Runtime-Code Agent Checklist

**Mandatory for agents creating, changing or refactoring Critical Shift Unity/C# runtime code.**

Read [README.md](README.md), [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) and [CODE_HEALTH_PLAN.md](CODE_HEALTH_PLAN.md) before implementation work.

## Before changing code

- Identify the feature/module that owns the responsibility.
- Identify the single authoritative owner of any state being changed.
- Search for an existing implementation before creating a new one.
- Confirm the intended assembly/dependency direction.
- Keep unselected packages/frameworks behind neutral contracts.
- Decide which behavior can remain plain C# and which genuinely needs Unity.

## While changing code

- Do not introduce a global catch-all manager.
- Do not use scene-wide lookup/service-location as architecture.
- Do not introduce mutable global static state without a documented exceptional reason.
- Do not duplicate authoritative gameplay state in UI/networking/Unity adapters.
- Keep feature internals private to the feature where practical.
- Keep Unity adapters thin when the rule itself does not depend on Unity.
- Add tests at the lowest appropriate layer.
- Avoid generic `Utils`, `Helpers`, `Misc` or similar dumping grounds.
- Do not add speculative abstractions/packages for hypothetical future needs.

## Before considering the change complete

- Compile cleanly.
- Run relevant analysis and architecture checks.
- Run relevant unit/EditMode/integration/PlayMode tests.
- Search for the implementation being replaced.
- Delete superseded code and safe-to-remove obsolete assets/configuration.
- Remove stale TODOs, flags, imports, fields and documentation created obsolete by the change.
- Confirm there is still one obvious active implementation.
- Confirm no forbidden dependency or circular reference was introduced.
- Update architecture/engine decision documentation if the technical architecture changed.

## Stop conditions

Do not silently proceed if the change requires:

- selecting a networking framework;
- selecting Steam/voice/input/UI infrastructure not yet decided;
- violating an assembly boundary;
- creating a second authoritative state model;
- retaining old and new implementations indefinitely;
- introducing a major new global service/framework.

Instead, record the technical decision or migration plan first.

## Final self-review question

A fresh agent opening the repository six months later should be able to answer **which code owns this feature, where its state lives, what it depends on, and which implementation is current** without archaeology.
