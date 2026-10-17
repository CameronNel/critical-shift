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
        private void Start() { Initialize(); if (host.View == null) host.Begin(); }
    }
}
