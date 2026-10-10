using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    [Serializable]
    public sealed class SpawnControl
    {
        public Collider Shape;
        public MovingDoor Door;
        public string Label;
        public bool PpeWarning;
        public InteractionTarget Station;
    }

    // Scene-specific physical/presentation adapter. Equipment, leases and timers remain canonical.
    public sealed class SpawnRoomBindings : MonoBehaviour
    {
        [SerializeField] private FirstPersonWorker[] workers = Array.Empty<FirstPersonWorker>();
        [SerializeField] private InteractionTarget[] stations = Array.Empty<InteractionTarget>();
        [SerializeField] private SpawnControl[] controls = Array.Empty<SpawnControl>();
        [SerializeField] private MovingDoor scannerDoor;
        [SerializeField] private Collider scanButton;
        [SerializeField] private Transform scanPosition;
        [SerializeField] private GameObject[] scanIndicators = Array.Empty<GameObject>();
        [SerializeField] private Collider briefingScreen;
        private LocalShiftHost _host;
        private FirstPersonWorker _scanActor;
        private long _testDue = -1;
        private bool _releasing, _briefing;
        private string _scanResult = "Ready";
        private readonly List<MovingDoor> _doors = new List<MovingDoor>();
        public void Configure(FirstPersonWorker[] actors, InteractionTarget[] equipment, SpawnControl[] doors,
            MovingDoor podDoor, Collider button, Transform podPosition, GameObject[] indicators, Collider screen)
        {
            workers = (FirstPersonWorker[])actors.Clone(); stations = (InteractionTarget[])equipment.Clone();
            controls = (SpawnControl[])doors.Clone(); scannerDoor = podDoor; scanButton = button;
            scanPosition = podPosition; scanIndicators = (GameObject[])indicators.Clone(); briefingScreen = screen;
        }
        public void Begin(LocalShiftHost host)
        {
            _host = host;
            if (stations.Length != 4 || scannerDoor == null || scanButton == null || scanPosition == null || briefingScreen == null || scanIndicators.Length != 6)
                throw new InvalidOperationException("Incomplete spawn-room contract.");
            _doors.Clear();
            foreach (var control in controls)
            {
                if (control.Shape == null || control.Door == null) throw new InvalidOperationException("Missing spawn door control.");
                if (!_doors.Contains(control.Door)) { _doors.Add(control.Door); control.Door.Capture(); }
            }
            scannerDoor.Capture(); ResetBindings();
        }
        public bool Busy(Guid actor) => _scanActor != null && _scanActor.Id == actor;
        public bool StationOpen(InteractionTarget station)
        { foreach (var control in controls) if (control.Station == station) return control.Door.Open; return false; }
        public void Tick()
        {
            if (_host == null || _host.View?.Phase != WorldPhase.Running) return;
            foreach (var door in _doors)
            { door.Step(Time.unscaledDeltaTime); if (door.Blocked) _host.Notify("Door blocked. Clear its path."); }
            scannerDoor.Step(Time.unscaledDeltaTime);
            foreach (var worker in workers)
            {
                var preparation = _host.Preparation(worker.Id);
                if (preparation == null) continue;
                var target = _host.Target(preparation.TargetId);
                if (!StationOpen(target) || !_host.InReach(worker, target.Shape))
                { _host.Act(worker, PlayerAction.Drop, target); _host.Notify("Preparation cancelled; suit returned to its locker."); }
                else if (_host.View.ElapsedMilliseconds >= preparation.DueShiftMilliseconds)
                    _host.Act(worker, PlayerAction.Equip, target);
            }
            if (_releasing)
            { if (scannerDoor.Open) _releasing = false; return; }
            if (_scanActor == null) return;
            var actor = _host.Worker(_scanActor.Id);
            if (actor == null || !actor.CanInteract || actor.Pose != WorkerPose.Upright ||
                Vector3.Distance(_scanActor.transform.position, scanPosition.position) > 0.7f || scannerDoor.Blocked)
            { ReleaseScan("Scan cancelled. Keep the chamber clear."); return; }
            if (scannerDoor.Closed && _testDue < 0)
            { _testDue = _host.View.ElapsedMilliseconds + 3000; Indicator(2); _scanResult = "Testing"; }
            if (_testDue >= 0 && _host.View.ElapsedMilliseconds >= _testDue)
            {
                _scanResult = actor.Suit == WorkerSuit.None || actor.Suit == WorkerSuit.Compromised ? "Fail — suit missing or compromised" :
                    actor.Contamination > 0 ? "Inspect — contamination present" : "Pass — suit intact";
                Indicator(actor.Suit != WorkerSuit.Intact ? 5 : actor.Contamination > 0 ? 4 : 3);
                ReleaseScan(_scanResult);
            }
        }
        public bool TryUse(FirstPersonWorker worker)
        {
            if (_host == null || _host.View?.Phase != WorldPhase.Running) return false;
            var actor = _host.Worker(worker.Id);
            if (actor?.CanInteract != true || actor.Pose != WorkerPose.Upright) return false;
            var preparation = _host.Preparation(worker.Id);
            if (preparation != null)
            { _host.Act(worker, PlayerAction.Drop, _host.Target(preparation.TargetId)); return true; }
            if (Busy(worker.Id)) { ReleaseScan("Scan cancelled."); return true; }
            var shape = Aimed(worker);
            if (shape == scanButton)
            {
                if (_scanActor != null || _releasing || !scannerDoor.Open) { _host.Notify("The chamber is occupied or opening."); return true; }
                if (_host.Held(worker.Id) != null) { _host.Notify("Free your hands before the integrity test."); return true; }
                if (!worker.Grounded) { _host.Notify("Stand inside the chamber before starting the test."); return true; }
                if (Vector3.Distance(worker.transform.position, scanPosition.position) > 0.7f)
                { _host.Notify("Step inside the open chamber, then use its test button."); return true; }
                _scanActor = worker; _testDue = -1; _releasing = false; _scanResult = "Sealing";
                scannerDoor.SetOpen(false); Indicator(1); worker.GetComponent<WorkerAnimation>()?.Gesture("PRESS_BUTTON");
                _host.Notify("Integrity test started. E cancels and opens the chamber."); return true;
            }
            if (shape == briefingScreen)
            { _briefing = !_briefing; _host.Notify(_briefing ? "Briefing opened; E closes it." : "Briefing closed."); return true; }
            foreach (var control in controls)
                if (shape == control.Shape || control.Door.Matches(shape))
                {
                    control.Door.Toggle();
                    worker.GetComponent<WorkerAnimation>()?.Gesture("PRESS_BUTTON");
                    _host.Notify(control.PpeWarning && _host.Worker(worker.Id).Suit != WorkerSuit.Intact ?
                        "Warning: PPE is missing or compromised. You may still leave." : control.Label); return true;
                }
            var equipment = _host.Equipment(worker.Id);
            if (equipment != null)
                foreach (var station in stations)
                    if (station.Id == equipment.EntityId && shape == station.Shape)
                    { _host.Act(worker, PlayerAction.Unequip, station); return true; }
            return false;
        }
        public string Prompt(FirstPersonWorker worker)
        {
            if (_host == null) return "";
            var preparation = _host.Preparation(worker.Id);
            if (preparation != null) return $"Suit preparation: {Mathf.CeilToInt((preparation.DueShiftMilliseconds - _host.View.ElapsedMilliseconds) / 1000f)}s · E cancel";
            if (Busy(worker.Id)) return "Integrity: " + _scanResult + " · E cancel";
            var shape = Aimed(worker);
            if (shape == scanButton) return "E — integrity test";
            if (shape == briefingScreen) return "E — shift briefing";
            foreach (var control in controls) if (shape == control.Shape || control.Door.Matches(shape)) return "E — " + control.Label;
            foreach (var station in stations)
                if (shape == station.Shape) return _host.Equipment(worker.Id)?.EntityId == station.Id ? "E — return suit to this locker" : "E — prepare suit (15s)";
            return "";
        }
        private Collider Aimed(FirstPersonWorker worker) => Physics.Raycast(worker.Eye.transform.position,
            worker.Eye.transform.forward, out var hit, 3, ~0, QueryTriggerInteraction.Collide) ? hit.collider : null;
        private void ReleaseScan(string message)
        { scannerDoor.SetOpen(true); _scanActor = null; _testDue = -1; _releasing = true; _host.Notify(message); }
        private void Indicator(int index)
        { for (int i = 0; i < scanIndicators.Length; i++) if (scanIndicators[i] != null) scanIndicators[i].SetActive(i == index); }
        public void ResetBindings()
        {
            _scanActor = null; _testDue = -1; _releasing = false; _briefing = false; _scanResult = "Ready";
            foreach (var control in controls) if (control?.Door != null) control.Door.ResetDoor();
            if (scannerDoor != null) scannerDoor.ResetDoor(); Indicator(0);
        }
        private void OnGUI()
        {
            if (!_briefing || _host?.View?.Phase != WorldPhase.Running) return;
            GUI.Box(new Rect(Screen.width - 420, 20, 400, 230), "Shift briefing");
            GUI.Label(new Rect(Screen.width - 405, 55, 370, 180),
                "Prepare at a locker, then check your suit in the integrity chamber.\n\n" +
                "Use the airlock controls to reach the cafeteria and the yard.\n\n" +
                "E uses a highlighted object. Q cancels a suit preparation.\n\n" +
                "The current map includes spawn, cafeteria, mine, refinery, medical and fuel corridor.");
        }
    }
}
