using CriticalShift.Application;
using CriticalShift.Features.Player.Unity;
using System;
using System.IO;
using System.Linq;
using UnityEngine;

namespace CriticalShift.Bootstrap.Player
{
    // Explicit authored composition. Gameplay ticking belongs to LocalShiftHost, not this bootstrap.
    public sealed class PlayerRoomBootstrap : MonoBehaviour
    {
        [SerializeField] private LocalShiftHost host;
        [SerializeField] private FirstPersonWorker[] workers;
        [SerializeField] private InteractionTarget[] targets;
        [SerializeField, Range(30, 3600)] private int shiftSeconds = 1200;
        [SerializeField] private string mapCommit, mapBindingsSha256;
        [SerializeField] private string[] mapRoomKeys;
        [SerializeField] private int[] mapCollisionTriangles;
        private bool _initialized;
        private bool _smoke;
        private int _smokeFrames;
        public void Configure(LocalShiftHost session, FirstPersonWorker[] players, InteractionTarget[] interactables)
        { host = session; workers = (FirstPersonWorker[])players.Clone(); targets = (InteractionTarget[])interactables.Clone(); }
        public void ConfigureMapIdentity(string commit, string bindingsSha256, string[] roomKeys, int[] collisionTriangles)
        {
            if (string.IsNullOrEmpty(commit) || commit.Length != 40 || string.IsNullOrEmpty(bindingsSha256) || bindingsSha256.Length != 64 ||
                roomKeys == null || collisionTriangles == null || roomKeys.Length != collisionTriangles.Length ||
                roomKeys.Length == 0 || roomKeys.Any(string.IsNullOrEmpty) || roomKeys.Distinct().Count() != roomKeys.Length ||
                collisionTriangles.Any(count => count <= 0))
                throw new InvalidOperationException("Invalid assembled map identity.");
            mapCommit = commit; mapBindingsSha256 = bindingsSha256;
            mapRoomKeys = (string[])roomKeys.Clone(); mapCollisionTriangles = (int[])collisionTriangles.Clone();
        }
        public void Initialize()
        {
            if (_initialized) return;
            if (host == null || workers == null || targets == null) throw new System.InvalidOperationException("Missing player room composition.");
            host.Configure(workers, targets, () => new WorldSession(new WorldSessionConfiguration(1,
                shiftSeconds * 1000L, true, maxObjects: 64, maxConnections: 4), host, playerActions: host), shiftSeconds);
            _initialized = true;
        }
        private void Start()
        {
            Initialize(); if (host.View == null) host.Begin();
            _smoke = System.Array.Exists(System.Environment.GetCommandLineArgs(), argument => argument == "--cs-player-smoke");
        }
        private void Update()
        {
            if (!_smoke) return;
            if (host.View?.Phase != WorldPhase.Running)
            { Debug.LogError("CS_PLAYER_ROOM_SMOKE_FAILED: " + host.Feedback); UnityEngine.Application.Quit(1); _smoke = false; return; }
            if (++_smokeFrames < 120) return;
            host.Shutdown();
            var stopped = host.View;
            if (stopped == null || stopped.Phase != WorldPhase.Stopped || stopped.ActiveClaimCount != 0 ||
                stopped.ConnectedPlayerCount != 0 || stopped.PendingTimerCount != 0 || stopped.RegisteredObjectCount != 0)
            { Debug.LogError("CS_PLAYER_ROOM_SMOKE_FAILED: stopped world retained active resources"); UnityEngine.Application.Quit(1); }
            else
            {
                try { ObserveMapSmoke(); }
                catch (Exception error)
                { Debug.LogError("CS_PLAYER_ROOM_SMOKE_FAILED: " + error); UnityEngine.Application.Quit(1); _smoke = false; return; }
                Debug.Log("CS_PLAYER_ROOM_SMOKE_OK: started, ran 120 frames and shut down the prepared room"); UnityEngine.Application.Quit(0);
            }
            _smoke = false;
        }

        [Serializable] private sealed class RoomSmokeRecord
        { public string key; public int triangles; public Vector3 boundsCenter, boundsExtents; }
        [Serializable] private sealed class MapSmokeRecord
        {
            public string mapCommit, mapBindingsSha256, graphicsDevice, limits;
            public int frames;
            public RoomSmokeRecord[] rooms;
        }
        private void ObserveMapSmoke()
        {
            var args = Environment.GetCommandLineArgs(); int reportIndex = Array.IndexOf(args, "--cs-map-smoke-report");
            if (reportIndex < 0) return;
            string Argument(string flag)
            {
                int index = Array.IndexOf(args, flag);
                if (index < 0 || index + 1 >= args.Length) throw new InvalidOperationException("Missing " + flag);
                return args[index + 1];
            }
            if (mapCommit != Argument("--cs-expected-map-commit") || mapBindingsSha256 != Argument("--cs-expected-map-bindings-sha256") ||
                mapRoomKeys == null || mapCollisionTriangles == null || mapRoomKeys.Length != mapCollisionTriangles.Length ||
                mapRoomKeys.Length == 0 || mapRoomKeys.Distinct().Count() != mapRoomKeys.Length)
                throw new InvalidOperationException("Player map identity differs from the reviewed delivery.");
            var rooms = UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsInactive.Include)
                .Where(node => node.name.StartsWith("ROOM_", StringComparison.Ordinal)).ToArray();
            if (rooms.Length != mapRoomKeys.Length || !rooms.Select(room => room.name).OrderBy(name => name)
                .SequenceEqual(mapRoomKeys.Select(key => "ROOM_" + key).OrderBy(name => name)))
                throw new InvalidOperationException("Player room inventory differs from the reviewed delivery.");
            bool Finite(Vector3 v) => float.IsFinite(v.x) && float.IsFinite(v.y) && float.IsFinite(v.z);
            var records = mapRoomKeys.Select((key, index) =>
            {
                var room = rooms.Single(node => node.name == "ROOM_" + key);
                var collision = room.Find("Static collision — " + key);
                if (collision == null) throw new InvalidOperationException("Missing room collision: " + key);
                var shape = collision.GetComponentsInChildren<MeshCollider>(true).Single();
                if (!shape.enabled || !shape.gameObject.activeInHierarchy || shape.sharedMesh == null)
                    throw new InvalidOperationException("Inactive room collision: " + key);
                var mesh = shape.sharedMesh; ulong indices = 0;
                for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
                {
                    if (mesh.GetTopology(submesh) != MeshTopology.Triangles) throw new InvalidOperationException("Nontriangle collision: " + key);
                    indices += mesh.GetIndexCount(submesh);
                }
                var bounds = mesh.bounds;
                if (indices != (ulong)mapCollisionTriangles[index] * 3 || !Finite(bounds.center) || !Finite(bounds.extents) || bounds.extents.sqrMagnitude <= 0)
                    throw new InvalidOperationException("Room collision differs from the reviewed delivery: " + key);
                return new RoomSmokeRecord { key = key, triangles = (int)(indices / 3), boundsCenter = bounds.center, boundsExtents = bounds.extents };
            }).ToArray();
            File.WriteAllText(Path.GetFullPath(Argument("--cs-map-smoke-report")), JsonUtility.ToJson(new MapSmokeRecord
            {
                mapCommit = mapCommit, mapBindingsSha256 = mapBindingsSha256, frames = _smokeFrames, rooms = records,
                graphicsDevice = SystemInfo.graphicsDeviceName,
                limits = "Loaded room/collision inventory and startup/shutdown only; continuous navigation and target-hardware performance are not assessed."
            }, true));
            Debug.Log("CS_PLAYER_MAP_INVENTORY_OK; commit=" + mapCommit + "; rooms=" + records.Length);
        }
    }
}
