using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Temporary fixture controls over command/query ports. No feature owner or physics implementation is referenced.</summary>
    public sealed class SandboxHud : MonoBehaviour
    {
        public event Action<Guid> GrabRequested, ReleaseRequested;
        public event Action<Guid, ProductionAction, Guid, bool, bool> MachineRequested;
        public event Action<Guid, ReactorAction, Guid, bool> ReactorRequested;
        public event Action ReplayRequested, PauseRequested, ResetRequested, BeltResetRequested;
        public event Action TransferFocusedRequested, DropHeldRequested, StartFocusedRequested, ToggleFocusedPowerRequested;
        public event Action BypassFocusedRequested;
        public event Action ShutdownFocusedRequested, EmergencyCoolingFocusedRequested;
        public event Action<bool> WorkerHoistRequested;
        public event Action RecoveryRequested, DiagnosticKnockdownRequested;
        public event Action PatientRecoveryRequested, PatientKnockdownRequested;
        public event Action<Vector2> MovementRequested, LookRequested, CarryRotationRequested;
        public event Action JumpRequested;
        public event Action ThrowRequested;
        public event Action<float> CarryDistanceRequested;
        public event Action<float, float, bool> CartDriveRequested;
        private readonly HashSet<KeyCode> held = new HashSet<KeyCode>();
        private LocalCommandPort commands;
        private Guid[] containers, machines;
        private Guid actor, reactor, patient;
        private Func<string> actionStatus, physicsStatus;
        private Func<Guid, string> traceName;
        private int selectedContainer, selectedMachine;
        private bool bypass, active, visible = true;
        private Vector2 scroll;
        private GUIStyle wrapped;
        private SandboxTraceFeed traceFeed;
        private ShiftDebriefView shownDebrief;
        private IReadOnlyList<SandboxTraceFeed.Entry> debriefRows;
        private double nextTraceRefresh;

        public void Initialize(LocalCommandPort port, Guid localActor, Guid[] containerIds, Guid[] machineIds,
            Guid reactorId, Guid patientActorId, Func<string> readAction, Func<string> readPhysics, Func<Guid, string> readTraceName)
        {
            if (commands != null || port == null || containerIds == null || containerIds.Length == 0 ||
                machineIds == null || machineIds.Length == 0 || localActor == Guid.Empty || reactorId == Guid.Empty ||
                patientActorId == Guid.Empty || patientActorId == localActor)
                throw new ArgumentException("Provide one local command port and explicit fixture selections.");
            commands = port; actor = localActor; reactor = reactorId; patient = patientActorId;
            containers = (Guid[])containerIds.Clone(); machines = (Guid[])machineIds.Clone();
            actionStatus = readAction ?? throw new ArgumentNullException(nameof(readAction));
            physicsStatus = readPhysics ?? throw new ArgumentNullException(nameof(readPhysics));
            traceName = readTraceName ?? throw new ArgumentNullException(nameof(readTraceName));
            traceFeed = new SandboxTraceFeed(port);
        }

        public void Activate()
        {
            if (commands == null || GrabRequested == null || ReleaseRequested == null || MachineRequested == null ||
                ReactorRequested == null || ReplayRequested == null || PauseRequested == null || ResetRequested == null ||
                BeltResetRequested == null || MovementRequested == null || LookRequested == null || CartDriveRequested == null ||
                TransferFocusedRequested == null || DropHeldRequested == null || StartFocusedRequested == null || ToggleFocusedPowerRequested == null ||
                RecoveryRequested == null || DiagnosticKnockdownRequested == null || PatientRecoveryRequested == null || PatientKnockdownRequested == null ||
                BypassFocusedRequested == null || WorkerHoistRequested == null || ShutdownFocusedRequested == null ||
                EmergencyCoolingFocusedRequested == null || JumpRequested == null || CarryRotationRequested == null || ThrowRequested == null || CarryDistanceRequested == null)
                throw new InvalidOperationException("Fixture controls require all explicit command and input bindings.");
            active = true;
        }

        private void Update()
        {
            if (!active) return;
            if (Time.realtimeSinceStartupAsDouble >= nextTraceRefresh)
            { nextTraceRefresh = Time.realtimeSinceStartupAsDouble + 0.25; traceFeed.Refresh(); }
            MovementRequested?.Invoke(new Vector2(Axis(KeyCode.D, KeyCode.A), Axis(KeyCode.W, KeyCode.S)));
            WorkerHoistRequested?.Invoke(held.Contains(KeyCode.LeftShift) || held.Contains(KeyCode.RightShift));
            bool arrows = held.Contains(KeyCode.UpArrow) || held.Contains(KeyCode.DownArrow) || held.Contains(KeyCode.LeftArrow) || held.Contains(KeyCode.RightArrow);
            CartDriveRequested?.Invoke(arrows ? Axis(KeyCode.UpArrow, KeyCode.DownArrow) : Axis(KeyCode.W, KeyCode.S),
                arrows ? Axis(KeyCode.RightArrow, KeyCode.LeftArrow) : Axis(KeyCode.D, KeyCode.A), held.Contains(KeyCode.Space));
        }

        private float Axis(KeyCode positive, KeyCode negative) => (held.Contains(positive) ? 1 : 0) - (held.Contains(negative) ? 1 : 0);

        private void HandleInput(Event input)
        {
            if (input.type == EventType.MouseDrag && input.button == 1)
            { LookRequested?.Invoke(new Vector2(input.delta.x, -input.delta.y)); input.Use(); }
            if (input.type == EventType.MouseDrag && input.button == 2)
            { CarryRotationRequested?.Invoke(new Vector2(input.delta.x, -input.delta.y)); input.Use(); }
            if (input.type == EventType.ScrollWheel && (!visible ||
                !new Rect(12, 12, 350, Mathf.Max(300, Screen.height - 24)).Contains(input.mousePosition)))
            { CarryDistanceRequested?.Invoke(input.delta.y); input.Use(); }
            if (input.type != EventType.KeyDown && input.type != EventType.KeyUp) return;
            if (input.keyCode == KeyCode.Tab)
            {
                if (input.type == EventType.KeyUp) held.Remove(KeyCode.Tab);
                else if (held.Add(KeyCode.Tab)) visible = !visible;
                input.Use(); return;
            }
            if (input.keyCode == KeyCode.E || input.keyCode == KeyCode.G || input.keyCode == KeyCode.R || input.keyCode == KeyCode.F ||
                input.keyCode == KeyCode.H || input.keyCode == KeyCode.B || input.keyCode == KeyCode.X || input.keyCode == KeyCode.C || input.keyCode == KeyCode.T)
            {
                if (input.type == EventType.KeyUp) held.Remove(input.keyCode);
                else if (held.Add(input.keyCode))
                {
                    if (input.keyCode == KeyCode.E) TransferFocusedRequested?.Invoke();
                    else if (input.keyCode == KeyCode.G) DropHeldRequested?.Invoke();
                    else if (input.keyCode == KeyCode.R) StartFocusedRequested?.Invoke();
                    else if (input.keyCode == KeyCode.F) ToggleFocusedPowerRequested?.Invoke();
                    else if (input.keyCode == KeyCode.B) BypassFocusedRequested?.Invoke();
                    else if (input.keyCode == KeyCode.X) ShutdownFocusedRequested?.Invoke();
                    else if (input.keyCode == KeyCode.C) EmergencyCoolingFocusedRequested?.Invoke();
                    else if (input.keyCode == KeyCode.T) ThrowRequested?.Invoke();
                    else RecoveryRequested?.Invoke();
                }
                input.Use(); return;
            }
            if (input.keyCode != KeyCode.W && input.keyCode != KeyCode.A && input.keyCode != KeyCode.S && input.keyCode != KeyCode.D &&
                input.keyCode != KeyCode.UpArrow && input.keyCode != KeyCode.DownArrow && input.keyCode != KeyCode.LeftArrow &&
                input.keyCode != KeyCode.RightArrow && input.keyCode != KeyCode.Space && input.keyCode != KeyCode.LeftShift && input.keyCode != KeyCode.RightShift) return;
            if (input.type == EventType.KeyDown)
            {
                bool first = held.Add(input.keyCode);
                if (first && input.keyCode == KeyCode.Space) JumpRequested?.Invoke();
            }
            else held.Remove(input.keyCode);
            input.Use();
        }

        private void OnGUI()
        {
            if (!active || commands == null) return;
            if (wrapped == null) wrapped = new GUIStyle(GUI.skin.label) { wordWrap = true };
            HandleInput(Event.current);
            GUI.Label(new Rect(Screen.width * 0.5f - 6, Screen.height * 0.5f - 10, 20, 20), "+");
            if (!visible)
            {
                GUI.Label(new Rect(12, 12, Screen.width - 24, 40), "WASD move | Space hop/brake | right-drag look | middle-drag turn | wheel reach | T throw | Tab panel", wrapped);
                GUI.Label(new Rect(12, 56, Screen.width - 24, 40), "E transfer | G drop | F power/cooling | R start/repair/resume/reset | B bypass | X shutdown | C emergency cooling | H recover", wrapped);
                GUI.Label(new Rect(12, 100, Screen.width - 24, 70), actionStatus(), wrapped);
                var contract = commands.Contract;
                if (contract != null)
                {
                    var wave = contract.Current;
                    string objective = wave == null || commands.Debrief != null ? contract.Title + " · " + contract.Outcome :
                        wave.Label + " · " + wave.DeliveredEnergyUnits + "/" + wave.RequiredEnergyUnits + " energy this window";
                    GUI.Label(new Rect(12, 174, Screen.width - 24, 70), objective, wrapped);
                }
                return;
            }
            bool previousEnabled = GUI.enabled;
            GUILayout.BeginArea(new Rect(12, 12, 350, Mathf.Max(300, Screen.height - 24)), GUI.skin.box);
            scroll = GUILayout.BeginScrollView(scroll);
            try
            {
                var world = commands.World;
                GUILayout.Label("CRITICAL SHIFT | LOCAL GAMEPLAY FIXTURE");
                GUILayout.Label("WASD walk · Space hop · right-drag look · middle-drag turns crate · wheel adjusts reach · T throws crate · Tab hides panel", wrapped);
                GUILayout.Label("E takes cart handle · WASD/arrows drive · Space brakes");
                GUILayout.Label("Shift " + TimeSpan.FromMilliseconds(world.RemainingMilliseconds).ToString(@"mm\:ss") + " | " + world.Phase +
                    (world.Outcome == WorldOutcome.None ? "" : " · " + world.Outcome), wrapped);
                DrawContract();
                if (commands.Debrief != null)
                {
                    DrawDebrief(commands.Debrief);
                    if (GUILayout.Button("Start another shift")) ResetRequested?.Invoke();
                    DrawDebriefTimeline(commands.Debrief);
                    return;
                }
                GUILayout.Label("Held objects: " + world.ActiveClaimCount + " | " + actionStatus(), wrapped);
                var worker = commands.GetWorker(actor);
                if (worker != null) GUILayout.Label("Worker " + worker.Awareness + " / " + worker.Pose);
                GUILayout.Space(8);
                GUI.enabled = previousEnabled && (world.Phase == WorldPhase.Running || world.Phase == WorldPhase.Paused);
                DrawContainer();
                GUI.enabled = previousEnabled && world.Phase == WorldPhase.Running && worker?.CanInteract == true;
                DrawMachine();
                DrawReactor();
                GUI.enabled = previousEnabled;
                GUILayout.Space(8);
                GUILayout.Label(physicsStatus(), wrapped);
                DrawAccounting();
                GUI.enabled = previousEnabled && world.Phase == WorldPhase.Running && worker?.Pose == WorkerPose.Down;
                if (GUILayout.Button("Attempt worker recovery (H)")) RecoveryRequested?.Invoke();
                GUI.enabled = previousEnabled && world.Phase == WorldPhase.Running;
                if (GUILayout.Button("Fixture only: simulate knockdown")) DiagnosticKnockdownRequested?.Invoke();
                var patientView = commands.GetWorker(patient);
                if (patientView != null) GUILayout.Label("Fixture patient: " + patientView.Awareness + " / " + patientView.Pose);
                if (GUILayout.Button("Fixture patient: knock down")) PatientKnockdownRequested?.Invoke();
                if (GUILayout.Button("Fixture patient: attempt recovery")) PatientRecoveryRequested?.Invoke();
                GUI.enabled = previousEnabled && (world.Phase == WorldPhase.Running || world.Phase == WorldPhase.Paused);
                if (GUILayout.Button("Clear conveyor blockage latch")) BeltResetRequested?.Invoke();
                if (GUILayout.Button(world.Phase == WorldPhase.Paused ? "Resume process clock" : "Pause process clock")) PauseRequested?.Invoke();
                GUI.enabled = previousEnabled && (world.Phase == WorldPhase.Running || world.Phase == WorldPhase.Paused) && commands.CanReplayLast;
                if (GUILayout.Button("Retry last action")) ReplayRequested?.Invoke();
                GUI.enabled = previousEnabled;
                if (GUILayout.Button("Restart isolated fixture")) ResetRequested?.Invoke();
                GUILayout.Label("Single local host. No networking or map loaded.");
                DrawTrace();
            }
            finally
            {
                GUI.enabled = previousEnabled;
                GUILayout.EndScrollView(); GUILayout.EndArea();
            }
        }

        private void DrawContainer()
        {
            GUILayout.Label("MATERIAL CONTAINER " + (selectedContainer + 1) + " / " + containers.Length);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Previous crate")) selectedContainer = (selectedContainer + containers.Length - 1) % containers.Length;
            if (GUILayout.Button("Next crate")) selectedContainer = (selectedContainer + 1) % containers.Length;
            GUILayout.EndHorizontal();
            Guid id = containers[selectedContainer];
            var batch = commands.GetBatch(id); var custody = commands.GetObject(id);
            GUILayout.Label(batch == null ? "Unavailable" : batch.Kind + " · " + batch.Units + " units · moisture " + batch.Moisture);
            GUILayout.Label(custody?.HolderId == actor ? "You are holding this crate" : custody?.SlotId != null ? "Loaded into equipment" : "In the world");
            GUILayout.BeginHorizontal();
            bool mayRelease = GUI.enabled;
            GUI.enabled = mayRelease && commands.World.Phase == WorldPhase.Running && commands.GetWorker(actor)?.CanInteract == true;
            if (GUILayout.Button("Grab selected")) GrabRequested?.Invoke(id);
            GUI.enabled = mayRelease && custody?.HolderId == actor;
            if (GUILayout.Button("Release selected")) ReleaseRequested?.Invoke(id);
            GUILayout.EndHorizontal();
            GUI.enabled = mayRelease;
        }

        private void DrawContract()
        {
            var contract = commands.Contract;
            if (contract == null) return;
            GUILayout.Label(contract.Title, wrapped);
            var current = contract.Current;
            if (current != null && (contract.Phase == WorldPhase.Running || contract.Phase == WorldPhase.Paused || contract.Phase == WorldPhase.Setup))
            {
                long remaining = Math.Max(0, current.EndMilliseconds - contract.ElapsedMilliseconds);
                GUILayout.Label(current.Label + " · " + current.DeliveredEnergyUnits + "/" + current.RequiredEnergyUnits +
                    " energy · " + Clock(remaining) + " left", wrapped);
                if (current.RequiredEnergyUnits == 0) GUILayout.Label("Prepare ore, fuel and cooling before the grid request begins.", wrapped);
                GUILayout.Label("Each window counts its own energy. Surplus cannot pay a later request.", wrapped);
                var upcoming = contract.Upcoming;
                if (upcoming != null) GUILayout.Label("Next: " + upcoming.Label + " in " +
                    Clock(Math.Max(0, upcoming.StartMilliseconds - contract.ElapsedMilliseconds)) + " · " +
                    upcoming.RequiredEnergyUnits + " energy in that window", wrapped);
            }
            else GUILayout.Label("Contract " + contract.Outcome + " · delivered " + contract.DeliveredEnergyUnits + " energy", wrapped);
            foreach (var wave in contract.Waves)
                if (wave.Settled) GUILayout.Label((wave.Met ? "Met: " : "Missed: ") + wave.Label + " · " +
                    wave.DeliveredEnergyUnits + "/" + wave.RequiredEnergyUnits + " energy", wrapped);
        }

        private static string Clock(long milliseconds)
        {
            long seconds = milliseconds / 1000;
            return (seconds / 60).ToString("D2") + ":" + (seconds % 60).ToString("D2");
        }

        private void DrawDebrief(ShiftDebriefView debrief)
        {
            GUILayout.Space(8); GUILayout.Label("SHIFT DEBRIEF · " + debrief.World.Outcome);
            if (debrief.Power != null)
            {
                var power = debrief.Power;
                GUILayout.Label("Grid supplied " + power.Delivered + " energy · reserve remaining " + power.Available, wrapped);
                GUILayout.Label("Reserve spent " + power.Spent + " · energy spilled " + power.Spilled, wrapped);
            }
            var material = debrief.Production;
            GUILayout.Label("Material " + material.ActiveUnits + " units · waste " + material.WasteUnits +
                " · conversions " + material.CompletedCycles + " · cancelled " + material.CancelledCycles, wrapped);
            var incidents = debrief.Incidents;
            if (debrief.Medical.UsedCartridges > 0)
                GUILayout.Label("Powered stabilization · completed " + debrief.Medical.CompletedCycles +
                    " · cartridges used " + debrief.Medical.UsedCartridges + " · cancelled " + debrief.Medical.CancelledCycles +
                    " · interrupted " + debrief.Medical.InterruptedCycles, wrapped);
            GUILayout.Label("Worker impacts " + incidents.WorkerImpacts + " · incapacitating impacts " + incidents.Incapacitations +
                " · successful standing recoveries " + incidents.StandingRecoveries, wrapped);
            GUILayout.Label("Machine jams " + incidents.MachineJams + " · completed bypass conversions " + incidents.BypassedConversions, wrapped);
            GUILayout.Label("Reactor warnings " + incidents.ReactorWarnings + " · trips " + incidents.ReactorTrips +
                " · emergency cooling uses " + incidents.EmergencyCoolingUses, wrapped);
            if (incidents.Saturated) GUILayout.Label("Incident totals reached the recording limit.", wrapped);
            if (debrief.DroppedIncidents > 0) GUILayout.Label(debrief.DroppedIncidents + " older incident details are no longer retained; totals cover the shift.", wrapped);
            GUILayout.Label("WORKERS AT SHIFT END");
            foreach (var worker in debrief.WorkersAtEnd)
                GUILayout.Label(WorkerName(worker.Id) + " · " + worker.Awareness + " / " + worker.Pose +
                    " · suit " + worker.Suit + " · contamination " + worker.Contamination, wrapped);
        }

        private string WorkerName(Guid id)
        {
            string name = traceName(id);
            return !string.IsNullOrEmpty(name) ? name : id == actor ? "You" : id == patient ? "Test worker" : "Worker";
        }

        private void DrawDebriefTimeline(ShiftDebriefView debrief)
        {
            GUILayout.Space(8); GUILayout.Label("SHIFT INCIDENT TIMELINE");
            if (!ReferenceEquals(debrief, shownDebrief))
            { debriefRows = SandboxTraceFeed.DebriefEntries(debrief); shownDebrief = debrief; }
            foreach (var row in debriefRows) DrawTraceRow(row);
        }

        private void DrawMachine()
        {
            GUILayout.Space(8); GUILayout.Label("PRODUCTION MACHINE " + (selectedMachine + 1));
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Previous machine")) selectedMachine = (selectedMachine + machines.Length - 1) % machines.Length;
            if (GUILayout.Button("Next machine")) selectedMachine = (selectedMachine + 1) % machines.Length;
            GUILayout.EndHorizontal();
            Guid id = machines[selectedMachine]; var state = commands.GetMachine(id);
            if (state == null) { GUILayout.Label("Machine unavailable"); return; }
            GUILayout.Label(state.Mode + " | " + (state.Powered ? "power on" : "power off") + " | " + state.WorkMilliseconds + " / " + state.DurationMilliseconds + " ms");
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Insert selected")) MachineRequested?.Invoke(id, ProductionAction.Insert, containers[selectedContainer], false, false);
            if (GUILayout.Button("Eject")) MachineRequested?.Invoke(id, ProductionAction.Eject, Guid.Empty, false, false);
            GUILayout.EndHorizontal();
            bypass = GUILayout.Toggle(bypass, "Bypass inspection");
            GUILayout.Label("Bypass is faster; wet material can jam and the output retains suspect-fuel history.", wrapped);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Start cycle")) MachineRequested?.Invoke(id, ProductionAction.Start, Guid.Empty, bypass, false);
            if (GUILayout.Button(state.Powered ? "Power off" : "Power on")) MachineRequested?.Invoke(id, ProductionAction.SetPower, Guid.Empty, false, !state.Powered);
            GUILayout.EndHorizontal();
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Repair jam")) MachineRequested?.Invoke(id, ProductionAction.Repair, Guid.Empty, false, false);
            if (GUILayout.Button("Resume")) MachineRequested?.Invoke(id, ProductionAction.Resume, Guid.Empty, false, false);
            if (GUILayout.Button("Cancel cycle")) MachineRequested?.Invoke(id, ProductionAction.CancelCycle, Guid.Empty, false, false);
            GUILayout.EndHorizontal();
        }

        private void DrawReactor()
        {
            GUILayout.Space(8); var state = commands.Reactor;
            GUILayout.Label("REACTOR | " + (state == null ? "unavailable" : state.Mode.ToString()));
            if (state == null) return;
            GUILayout.Label("Reserve " + state.Power.Available + " | grid delivered " + state.Power.Delivered +
                " | instability " + state.InstabilityMilliseconds + " ms", wrapped);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Load selected fuel")) ReactorRequested?.Invoke(reactor, ReactorAction.Insert, containers[selectedContainer], false);
            if (GUILayout.Button("Eject fuel")) ReactorRequested?.Invoke(reactor, ReactorAction.Eject, Guid.Empty, false);
            GUILayout.EndHorizontal();
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Start reactor")) ReactorRequested?.Invoke(reactor, ReactorAction.Start, Guid.Empty, false);
            if (GUILayout.Button("Shut down")) ReactorRequested?.Invoke(reactor, ReactorAction.Shutdown, Guid.Empty, false);
            GUILayout.EndHorizontal();
            if (GUILayout.Button(state.Cooling ? "Close cooling valve" : "Open cooling valve"))
                ReactorRequested?.Invoke(reactor, ReactorAction.SetCooling, Guid.Empty, !state.Cooling);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Emergency cooling")) ReactorRequested?.Invoke(reactor, ReactorAction.EmergencyCooling, Guid.Empty, false);
            if (GUILayout.Button("Reset trip")) ReactorRequested?.Invoke(reactor, ReactorAction.ResetTrip, Guid.Empty, false);
            GUILayout.EndHorizontal();
        }

        private void ClearInput()
        {
            held.Clear(); MovementRequested?.Invoke(Vector2.zero); CartDriveRequested?.Invoke(0, 0, true); WorkerHoistRequested?.Invoke(false);
        }

        private void DrawAccounting()
        {
            var totals = commands.ProductionSummary;
            GUILayout.Space(8); GUILayout.Label("MATERIAL & POWER ACCOUNTING");
            GUILayout.Label("Material units · issued " + totals.IssuedUnits + " · active " + totals.ActiveUnits + " · waste " + totals.WasteUnits, wrapped);
            GUILayout.Label("Cycles · completed " + totals.CompletedCycles + " · cancelled " + totals.CancelledCycles + " · pending " + totals.PendingCycles, wrapped);
            var power = commands.Power;
            if (power != null)
            {
                GUILayout.Label("Power units · initial " + power.Initial + " · generated " + power.Generated, wrapped);
                GUILayout.Label("Power units · grid " + power.Delivered + " · reserve " + power.Available + " · spent " + power.Spent +
                    " · spilled " + power.Spilled, wrapped);
            }
        }

        private void DrawTrace()
        {
            GUILayout.Space(8); GUILayout.Label("RECENT FIXTURE EVENTS");
            if (traceFeed.GapDetected)
                GUILayout.Label("Diagnostic history is incomplete · source evicted " + traceFeed.SourceDroppedRecords + " records", wrapped);
            if (traceFeed.SequenceExhausted)
                GUILayout.Label("Diagnostic sequence exhausted · new trace records are unavailable", wrapped);
            for (int i = traceFeed.Entries.Count - 1; i >= 0; i--)
            {
                DrawTraceRow(traceFeed.Entries[i]);
            }
        }
        private void DrawTraceRow(SandboxTraceFeed.Entry row)
        {
            string cause = row.CauseId == Guid.Empty ? "" : " · cause " + row.CauseId.ToString("N").Substring(0, 8);
            string subject = traceName(row.EntityId);
            if (string.IsNullOrEmpty(subject) && row.ActorId != Guid.Empty) subject = WorkerName(row.ActorId);
            string hazard = row.HazardId == Guid.Empty ? "" : traceName(row.HazardId);
            GUILayout.Label(Clock(row.ShiftMilliseconds) + " · " + (string.IsNullOrEmpty(subject) ? "" : subject + ": ") + row.Description +
                (string.IsNullOrEmpty(hazard) ? "" : " · source " + hazard) + cause, wrapped);
        }
        private void OnApplicationFocus(bool focused) { if (!focused) ClearInput(); }
        private void OnDisable() { active = false; ClearInput(); }
        private void OnDestroy()
        {
            ClearInput(); GrabRequested = null; ReleaseRequested = null; MachineRequested = null; ReactorRequested = null;
            ReplayRequested = null; PauseRequested = null; ResetRequested = null; BeltResetRequested = null;
            TransferFocusedRequested = null; DropHeldRequested = null; StartFocusedRequested = null; ToggleFocusedPowerRequested = null;
            BypassFocusedRequested = null; ShutdownFocusedRequested = null; EmergencyCoolingFocusedRequested = null;
            WorkerHoistRequested = null;
            RecoveryRequested = null; DiagnosticKnockdownRequested = null;
            PatientRecoveryRequested = null; PatientKnockdownRequested = null;
            MovementRequested = null; LookRequested = null; CarryRotationRequested = null; CartDriveRequested = null; JumpRequested = null; ThrowRequested = null;
            CarryDistanceRequested = null;
            traceName = null;
        }
    }
}
