# Runtime code: start here

The current engine-independent C# source, tests and verification tools live in [dotnet/](dotnet/README.md). No Unity project is created or needed to run these checks.

- [Interaction and offline build overview](dotnet/README.md)
- [World/session, shift clock and timers](dotnet/WORLD_AND_TIME.md)
- [Worker recovery, possession cleanup and executable scenarios](dotnet/WORKERS_AND_SCENARIOS.md)
- [Production chain and material accounting](dotnet/PRODUCTION.md)
- [Canonical architecture and code-health rules](../design/code-architecture/README.md)

These libraries are intended for later engine integration as one canonical implementation, not a second game engine. Unity import, physical behaviour and connected multiplayer still need separate validation.
