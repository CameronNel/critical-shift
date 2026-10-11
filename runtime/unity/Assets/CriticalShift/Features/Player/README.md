# Local player interaction slice

Responsibility: first-person movement and physical projections of canonical player actions.
Two separate scene generators provide a graybox fixture and a derivative of the current
assembled map with spawn bindings. Neither edits the authored facility map.

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
unity -batchmode -nographics -projectPath "$PWD/runtime/unity" -runTests -testPlatform PlayMode -testFilter CriticalShift.Tests.Player.PlayerBindingTests -testResults "$PWD/runtime/out/player-playmode.xml" -logFile "$PWD/runtime/out/player-playmode.log"
```

Expect nine `PlayerBindingTests`, zero skips/failures. They cover physical pickup/drop,
equipment, seat and blocked exit, placement/take, movement/pause, crouch clearance, ten resets,
closing-door obstruction/reopening and an occupant inside a concave leaf's empty query bounds.
The six actual-map cases require the generated assembled map; preparation and the combined
15-case native run are documented in [SPAWN_ROOM.md](../../../../../validation/SPAWN_ROOM.md).
For a desktop fixture build, invoke `CriticalShift.Bootstrap.Player.Editor.PlayerRoomBuild.Build`
with `-csBuildPath` and `-buildTarget Linux64` or `Win64`. This method selects the fixture scene
explicitly, Built-in rendering, Mono, .NET Standard 2.1 and Disabled stripping.

Contract coverage: CMD/HOLD/WORKER/LIFE/SHIFT offline cases; physical assertions supplement
LIFE-01 and WORKER-01. This is not completion of PHYS ragdoll/cart/conveyor/network cases.
No old path or serialized identity is replaced. New scene scripts have stable metadata.
No networking, Steam, voice, persistence, accepted map import, measured
performance or human feel approval is claimed. See [the task evidence](../../../../../validation/PLAYER_SLICE.md).

## Spawn on the current assembled map

See [spawn preparation and evidence](../../../../../validation/SPAWN_ROOM.md). Run
`python runtime/tools/prepare_spawn.py`, then **Critical Shift > Spawn > Create assembled map scene**.
This separate generator consumes the pinned assembly builder, scoped FBX exports, exact source
door poses/markers and the existing rig. All six placed rooms are included; runtime interactions
are assigned only in spawn. The other rooms retain geometry and prototype static collision.

`SpawnRoomBindings` owns local door/scanner/briefing presentation, while `WorkerAnimation`
projects custody/posture onto the original skeleton and clips. `MovingDoor` checks intermediate
leaf poses against workers/rigidbodies and reopens on blocked closing. Its disabled query bounds
are separate from actual leaf mesh colliders, so the curved pod does not become a solid box.
Multiplayer door state, airlock pressure, physical suit damage and scanner certification are
outside this local slice.

Station suits use `PlayerOperations`' bounded, lease-bound preparation intention on the existing
shift clock. Stand in front of an open locker, face it, and press E with free hands to start
15 seconds of preparation. Movement/turning are held while the existing `SUIT_UP` clip follows
the preparation clock. The worker stays unsuited and the hanging suit stays visible until
the final pose; the equipment commit then shows the worn outfit and hides the hanging suit
together. E/Q cancels. E on that station (or U while in reach) returns it there. Closing the
locker, losing the standing pose/reach/claim, impact, disconnect or reset cancels preparation.
Pause freezes the deadline and pose while host lease renewal continues. No second inventory
or timer owner is introduced. Scene generation and all 15 native physical tests pass in this
container; visual/human review remains separate.
