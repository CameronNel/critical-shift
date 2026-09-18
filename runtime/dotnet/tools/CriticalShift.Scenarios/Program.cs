using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    /// <summary>Tool-only scripted host. All state changes use the production Application API.</summary>
    internal static class Program
    {
        private static int Main(string[] args)
        {
            string? scenario = null, reportPath = null; int repeats = 1;
            try
            {
                for (int i = 0; i < args.Length; i++)
                {
                    if (i + 1 >= args.Length) throw new ArgumentException("Each option needs a value.");
                    string value = args[++i];
                    switch (args[i - 1])
                    {
                        case "--scenario": scenario = value; break;
                        case "--report": reportPath = value; break;
                        case "--repeat": repeats = int.Parse(value, System.Globalization.CultureInfo.InvariantCulture); break;
                        default: throw new ArgumentException("Unknown command-line option.");
                    }
                }
                if (scenario == null || reportPath == null || repeats < 1 || repeats > 50)
                    throw new ArgumentException("Use --scenario FILE --report FILE [--repeat 1..50].");
                if (Path.GetFullPath(scenario) == Path.GetFullPath(reportPath))
                    throw new ArgumentException("The report must not overwrite the scenario.");
                var info = new FileInfo(scenario);
                if (!info.Exists || info.Length > 262144) throw new ArgumentException("Scenario missing or larger than 256 KiB.");
                using var json = JsonDocument.Parse(File.ReadAllText(scenario), new JsonDocumentOptions { MaxDepth = 16 });
                var fixture = new Scenario(json.RootElement);
                var result = fixture.Run(repeats);
                var options = new JsonSerializerOptions { WriteIndented = true };
                options.Converters.Add(new JsonStringEnumConverter());
                string output = JsonSerializer.Serialize(result, options);
                string? parent = Path.GetDirectoryName(Path.GetFullPath(reportPath));
                if (parent != null) Directory.CreateDirectory(parent);
                // Atomic create-new refuses any existing file, including case aliases, symlinks and hardlinks.
                // Report generation never truncates or replaces a user file.
                using (var file = new FileStream(reportPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(file)) writer.Write(output + Environment.NewLine);
                Console.WriteLine($"{result.Status}: {result.Name}; {result.CompletedSteps} completed steps; {result.Assertions} assertions.");
                if (result.Error != null) Console.Error.WriteLine(result.Error);
                Console.WriteLine("Offline logical scenarios only. Reach and recovery clearance use synthetic test policies.");
                return result.Status == "Passed" ? 0 : 1;
            }
            catch (Exception error) when (error is ArgumentException || error is FormatException ||
                error is OverflowException || error is UnauthorizedAccessException || error is KeyNotFoundException || error is IOException || error is JsonException || error is InvalidOperationException)
            {
                // Configuration failures cannot become a successful empty run. Do not print private paths.
                Console.Error.WriteLine("Scenario configuration failed: " + error.GetType().Name);
                return 2;
            }
        }
    }

    internal sealed class Scenario
    {
        private readonly JsonElement _spec;
        private readonly ScriptedPolicies _policy = new ScriptedPolicies();
        private WorldSession _world = null!;
        private Guid _previousEpoch;
        private int _assertions, _completed, _step, _run;
        private string _operation = "setup";
        private readonly string _name;

        internal Scenario(JsonElement spec)
        {
            _spec = spec;
            _name = Text(spec, "name");
            if (_name.Length > 80 || !spec.TryGetProperty("steps", out var steps) ||
                steps.ValueKind != JsonValueKind.Array || steps.GetArrayLength() < 1 || steps.GetArrayLength() > 512)
                throw new ArgumentException("A named scenario needs 1..512 steps.");
        }

        internal ScenarioReport Run(int repeats)
        {
            try
            {
                for (_run = 1; _run <= repeats; _run++)
                {
                    _policy.Clearance = RecoveryClearance.Unavailable;
                    _world = new WorldSession(new WorldSessionConfiguration(checked((int)Number(_spec, "seed", 42)),
                        Number(_spec, "duration", 20000), Flag(_spec, "pause", false)), _policy, _policy,
                        traceCapacity: checked((int)Number(_spec, "traceCapacity", 32)));
                    _previousEpoch = Guid.Empty; Bind(_world); _step = 0;
                    foreach (var step in _spec.GetProperty("steps").EnumerateArray())
                    {
                        _step++; _operation = Text(step, "op");
                        string actual = Execute(step);
                        Expect(actual, Text(step, "expect"), "operation status");
                        if (step.TryGetProperty("assert", out var assertions)) AssertState(assertions);
                        else if (_operation == "assert") throw new InvalidOperationException("Assert operation has no assertions.");
                        _completed++;
                    }
                    // Capture a deliberate Stop in diagnostics as well; a scenario cannot leak live state between repetitions.
                    _world.Stop();
                    Expect(_world.WorkerCount, 0, "teardown workers");
                    Expect(_world.View.ActiveClaimCount, 0, "teardown claims");
                }
                return Report("Passed", repeats, null);
            }
            catch (Exception e)
            {
                string error = $"Run {_run}, step {_step}, operation {_operation}: {e.GetType().Name}: {e.Message}";
                // Assertions and domain errors here contain identifiers and typed outcomes, not account data.
                _world?.Stop();
                return Report("Failed", Math.Max(0, _run - 1), error);
            }
        }

        private ScenarioReport Report(string status, int completedRuns, string? error) =>
            new ScenarioReport(_name, status, completedRuns, _completed, _assertions, _step,
                error, _world?.View, _world?.Trace, _world?.Production.Summary);

        private string Execute(JsonElement s)
        {
            int actor = checked((int)Number(s, "actor", 1));
            if (actor < 1 || actor > 4) throw new ArgumentException("Scenario actor must be 1..4.");
            Guid who = Id(actor), epoch = Epoch(s);
            switch (_operation)
            {
                case "advance": return _world.AdvanceTo(Number(s, "time")).World.Phase.ToString();
                case "pause": return _world.Pause(epoch).ToString();
                case "resume": return _world.Resume(epoch).ToString();
                case "impact": return _world.ApplyWorkerImpact(epoch, who, Number(s, "seq"),
                    Choice<WorkerImpact>(s, "severity"), Number(s, "delay"), Id(checked((int)Number(s, "hazard"))), Id(checked((int)Number(s, "cause")))).Status.ToString();
                case "aid": return _world.StabilizeWorker(epoch, who, Number(s, "revision"), Number(s, "delay")).Status.ToString();
                case "environment": return _world.SetWorkerEnvironment(epoch, who, Number(s, "revision"),
                    Choice<WorkerSuit>(s, "suit"), checked((int)Number(s, "contamination"))).Status.ToString();
                case "beginRecovery": return _world.BeginWorkerRecovery(epoch, who, Number(s, "episode"),
                    Number(s, "revision")).Status.ToString();
                case "completeRecovery":
                    _policy.Clearance = Choice<RecoveryClearance>(s, "clearance");
                    return _world.CompleteWorkerRecovery(epoch, who, Number(s, "attempt")).Status.ToString();
                case "cancelRecovery": return _world.CancelWorkerRecovery(epoch, who, Number(s, "attempt")).Status.ToString();
                case "grab":
                case "release":
                    return _world.ExecuteInteraction(Id(100 + actor), new InteractionCommand(epoch,
                        Number(s, "seq"), _operation == "grab" ? InteractionKind.Grab : InteractionKind.Release,
                        Id(checked((int)Number(s, "entity", 500))), Number(s, "revision", 0), Number(s, "lease", 0))).Status.ToString();
                case "production": return ProductionScenarioSteps.Execute(s, _world, epoch, Id(100 + actor));
                case "disconnect":
                    int count = _world.View.ConnectedPlayerCount;
                    _world.Disconnect(epoch, Id(100 + actor));
                    return count == _world.View.ConnectedPlayerCount ? "NoChange" : "Disconnected";
                case "restart":
                    _previousEpoch = _world.Epoch;
                    _world = _world.Restart(_policy, _policy); Bind(_world);
                    return _world.View.Phase.ToString();
                case "assert": return "Checked";
                default: throw new ArgumentException("Unknown scenario operation: " + _operation);
            }
        }

        private void AssertState(JsonElement assertions)
        {
            if (assertions.ValueKind != JsonValueKind.Object || !assertions.EnumerateObject().Any())
                throw new ArgumentException("An assertion object cannot be empty.");
            var worker = _world.GetWorker(Id(checked((int)Number(assertions, "actor", 1))));
            foreach (var a in assertions.EnumerateObject())
            {
                switch (a.Name)
                {
                    case "actor": break;
                    case "phase": Expect(_world.View.Phase.ToString(), a.Value.GetString(), a.Name); break;
                    case "outcome": Expect(_world.View.Outcome.ToString(), a.Value.GetString(), a.Name); break;
                    case "elapsed": Expect(_world.View.ElapsedMilliseconds, a.Value.GetInt64(), a.Name); break;
                    case "workers": Expect(_world.WorkerCount, a.Value.GetInt32(), a.Name); break;
                    case "connections": Expect(_world.View.ConnectedPlayerCount, a.Value.GetInt32(), a.Name); break;
                    case "claims": Expect(_world.View.ActiveClaimCount, a.Value.GetInt32(), a.Name); break;
                    case "timers": Expect(_world.View.PendingTimerCount, a.Value.GetInt32(), a.Name); break;
                    case "pose": Expect(worker?.Pose.ToString(), a.Value.GetString(), a.Name); break;
                    case "awareness": Expect(worker?.Awareness.ToString(), a.Value.GetString(), a.Name); break;
                    case "suit": Expect(worker?.Suit.ToString(), a.Value.GetString(), a.Name); break;
                    case "contamination": Expect(worker?.Contamination, (int?)a.Value.GetInt32(), a.Name); break;
                    case "episode": Expect(worker?.RecoveryEpisode, (long?)a.Value.GetInt64(), a.Name); break;
                    case "attempt": Expect(worker?.RecoveryAttempt, (long?)a.Value.GetInt64(), a.Name); break;
                    case "revision": Expect(worker?.Revision, (long?)a.Value.GetInt64(), a.Name); break;
                    case "readyAt": Expect(worker?.RecoveryNotBeforeMilliseconds, (long?)a.Value.GetInt64(), a.Name); break;
                    case "workerPresent": Expect(worker != null, a.Value.GetBoolean(), a.Name); break;
                    case "traceDropped": Expect(_world.Trace.DroppedRecords > 0, a.Value.GetBoolean(), a.Name); break;
                    default:
                        if (!ProductionScenarioSteps.TryRead(a, assertions, _world, out var actual, out var expected))
                            throw new ArgumentException("Unknown assertion: " + a.Name);
                        if (a.Name != "machine" && a.Name != "batch") Expect(actual, expected, a.Name);
                        break;
                }
            }
            if (assertions.EnumerateObject().All(x => x.Name == "actor" || x.Name == "machine" || x.Name == "batch"))
                throw new ArgumentException("An actor selector alone is not an assertion.");
        }

        private void Expect<T>(T actual, T expected, string label)
        {
            _assertions++;
            if (!EqualityComparer<T>.Default.Equals(actual, expected))
                throw new InvalidOperationException($"{label}: expected {expected}, observed {actual}.");
        }
        private Guid Epoch(JsonElement step)
        {
            if (!step.TryGetProperty("epoch", out var value)) return _world.Epoch;
            if (value.GetString() != "previous" || _previousEpoch == Guid.Empty)
                throw new ArgumentException("Only an established previous epoch can be requested.");
            return _previousEpoch;
        }
        private void Bind(WorldSession world)
        {
            for (int i = 1; i <= 4; i++) world.RegisterConnection(Id(100 + i), Id(i));
            world.RegisterObject(Id(500)); ProductionScenarioSteps.Bind(_spec, world); world.Start();
        }
        // Synthetic observations live only in this tool, never in runtime/Application/Domain.
        private sealed class ScriptedPolicies : IInteractionAccessPolicy, IWorkerRecoveryPolicy
        {
            internal RecoveryClearance Clearance { get; set; } = RecoveryClearance.Unavailable;
            public AccessDecision Evaluate(Guid actorId, Guid entityId, InteractionKind kind) => AccessDecision.Allowed;
            public RecoveryClearance Evaluate(Guid epoch, Guid workerId, long attempt) => Clearance;
        }
    }

    internal sealed class ScenarioReport
    {
        internal ScenarioReport(string name, string status, int runs, int steps, int assertions, int lastStep,
            string? error, WorldSessionView? world, SessionTraceView? trace, ProductionSummary? production)
        { Name = name; Status = status; CompletedRuns = runs; CompletedSteps = steps; Assertions = assertions;
          LastStep = lastStep; Error = error; FinalWorld = world; Trace = trace; Production = production; }
        public string Scope => "Offline logical execution; synthetic access/clearance; no physics or network";
        public string Name { get; }
        public string Status { get; }
        public int CompletedRuns { get; }
        public int CompletedSteps { get; }
        public int Assertions { get; }
        public int LastStep { get; }
        public string? Error { get; }
        public WorldSessionView? FinalWorld { get; }
        public SessionTraceView? Trace { get; }
        public ProductionSummary? Production { get; }
    }
}
