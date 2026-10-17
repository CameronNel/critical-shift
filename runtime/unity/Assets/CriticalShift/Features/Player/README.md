# Local player interaction slice

Responsibility: first-person movement and physical projections of canonical player actions in
an isolated graybox room. This does not assemble or change the authored facility map.

`PlayerRoomBootstrap` explicitly constructs application sessions. `LocalShiftHost` owns the
local session lifetime, monotonic clock pump, connection/target registry and physical policy;
`FirstPersonWorker` owns CharacterController motion and input. `InteractionTarget` projects
custody into Rigidbody/collider/transform bindings. None owns an independent inventory,
seat holder, suit condition, or shift clock. `PlayerOperations` coordinates the existing
Interaction and Workers owners through authenticated, revisioned commands and leases.

Dependencies: `CriticalShift.Features.Player.Unity` -> Application + UnityEngine;
`CriticalShift.Player.Bootstrap` -> that feature + Application + UnityEngine;
`CriticalShift.Player.Editor` -> those runtime subjects + UnityEditor;
`CriticalShift.Player.Tests.PlayMode` -> runtime subjects + NUnit/Test Runner.
Application -> existing Interaction/Workers domains. No domain peer edge is added.

## Prepare and play

From the repository root, with .NET 8 and the repository's activated Unity **6000.4.3f1**:

```sh
python runtime/tools/prepare_player.py
unity -projectPath "$PWD/runtime/unity"
```

The preparation script builds and imports eight canonical DLLs with explicit plugin metadata.
Rerun it whenever canonical C# changes. DLLs, import manifests and the generated scene are
ignored build output. Their implementation is not copied into Unity source. The script is
cross-platform; replace the `unity` alias with the installed pinned editor executable as needed.

In the editor choose **Critical Shift > Player Room > Create test scene**, then press Play.
Use the legacy **Input Manager (Old)** keyboard/mouse setting. Mouse axes use Unity's default
`Mouse X` and `Mouse Y` entries. The scene has a worker, crate, protective item, chair, table,
floor and walls; it is independent of Blender exports. The foundation scene catalogue remains
unchanged. The generated scene persists explicit bootstrap/worker/target references.

| Controls | Action |
| --- | --- |
| WASD / mouse | Move / look |
| Space / Left Ctrl / Left Shift | Short jump / crouch / sprint |
| E | Pick up, sit/stand, place a held item on the table, or take its occupant |
| Q / R / U | Drop / wear held protective equipment / remove worn equipment |
| Escape / F5 | Pause or resume / restart with a fresh world epoch |

Seats require empty hands. Worn equipment frees the hand and slows movement. The fixture uses
immediate equipment attachment, not the full suiting procedure or radiation protection.
Carry and seat claims renew each second; claims expire after three seconds without renewal.
A blocked drop/placement/exit rejects the action without changing custody. Crouching cannot
expand under a low ceiling. Paused sessions still pump host time and renew leases; losing
focus pauses input. Termination/reset/disable restore physical bindings, cursor and time scale.
Unexpected missing bindings or unavailable recovery poses stop the session visibly.

Authored binding limits: 1–4 explicit workers, exactly one reading local keyboard/mouse,
1–64 targets, distinct nonempty IDs, dedicated equipment/placement slot IDs. Portable objects
need one collider and a Rigidbody on the target root, with bounding radius <=0.6m. Seats need
seat and exit transforms; placement targets need an attachment transform. Wire these roles
explicitly when the map has exported Unity assets and colliders; section names alone do not
create runtime bindings.

## Checks

```sh
cd runtime/dotnet
python tools/verify.py
```

Supplementary pinned API compilation from the repository root:

```sh
python runtime/tools/check_player_api.py --editor-root /path/to/unity-6000.4.3f1 --out runtime/out/player-api
python runtime/tools/check_source.py
```

Native PlayMode tests, after activation/import (omit `-quit` when running tests):

```sh
unity -batchmode -nographics -projectPath "$PWD/runtime/unity" -runTests -testPlatform PlayMode -testFilter CriticalShift.Tests.Player -testResults "$PWD/runtime/out/player-playmode.xml" -logFile "$PWD/runtime/out/player-playmode.log"
```

Expect seven `PlayerBindingTests`, zero skips/failures. They cover physical pickup/drop,
equipment, seat and blocked exit, placement/take, movement/pause, crouch clearance and ten resets.
For a desktop fixture build, invoke `CriticalShift.Bootstrap.Player.Editor.PlayerRoomBuild.Build`
with `-csBuildPath` and `-buildTarget Linux64` or `Win64`. This method selects the fixture scene
explicitly, Built-in rendering, Mono, .NET Standard 2.1 and Disabled stripping.

Contract coverage: CMD/HOLD/WORKER/LIFE/SHIFT offline cases; physical assertions supplement
LIFE-01 and WORKER-01. This is not completion of PHYS ragdoll/cart/conveyor/network cases.
No old path or serialized identity is replaced. New scene scripts have stable metadata.
No networking, Steam, voice, persistence, character animation, accepted map import, measured
performance or human feel approval is claimed. See [the task evidence](../../../../../validation/PLAYER_SLICE.md).
