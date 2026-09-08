# Runtime source

The first bounded engine-independent implementation is in [dotnet/](dotnet/README.md): exclusive object claims, ordered command receipts, lifecycle cleanup and executable tests.

This is **not a Unity project or a playable game**. The global [architecture plan](../design/code-architecture/README.md) still governs all implementation. Unity tooling, physical attachments, rendering and multiplayer transport remain separate unpassed gates.

There is one canonical copy of each C# source file. Do not create a parallel Unity rewrite or copy the files into multiple source roots. The later Unity integration must deliberately consume the same library or perform one reviewed source migration.
