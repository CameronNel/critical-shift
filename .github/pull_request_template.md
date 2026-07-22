## What changed

<!-- Describe the bounded change. -->

## Why

<!-- Link the issue or state the accepted objective. -->

## Scope

- [ ] Only files required for this task changed
- [ ] No new package, framework, or architecture was introduced without approval
- [ ] `GAME_SPEC.md` was not changed unless explicitly requested

## Multiplayer authority

<!-- State who owns the new state and what clients are allowed to request. Write N/A only when genuinely unrelated. -->

## Validation

- [ ] Project opens/imports without errors
- [ ] Relevant automated tests pass
- [ ] Standalone scene or feature test passes
- [ ] Multiplayer test passes when applicable
- [ ] Disconnect/reset behaviour was tested when applicable
- [ ] Runtime warnings and errors were reviewed

### Commands and results

```text
Paste validation commands and concise results here.
```

## Player-facing evidence

<!-- Attach screenshots, a short recording, logs, or deterministic output. -->

## Risks and follow-up

<!-- Note assumptions, known limitations, deferred work, and anything the reviewer must verify manually. -->

## Reviewer checklist

- [ ] Causality remains understandable to players
- [ ] No unrelated abstraction or refactor was introduced
- [ ] State can reset cleanly between shifts
- [ ] The implementation is small enough to review confidently
