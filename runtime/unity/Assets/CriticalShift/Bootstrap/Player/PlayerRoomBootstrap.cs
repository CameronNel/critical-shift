using CriticalShift.Application;
using CriticalShift.Features.Player.Unity;
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
        private bool _initialized;
        private bool _smoke;
        private int _smokeFrames;
        public void Configure(LocalShiftHost session, FirstPersonWorker[] players, InteractionTarget[] interactables)
        { host = session; workers = (FirstPersonWorker[])players.Clone(); targets = (InteractionTarget[])interactables.Clone(); }
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
            else { Debug.Log("CS_PLAYER_ROOM_SMOKE_OK: started, ran 120 frames and shut down the prepared room"); UnityEngine.Application.Quit(0); }
            _smoke = false;
        }
    }
}
