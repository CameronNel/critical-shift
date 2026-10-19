using System;
using System.Linq;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Tool-only input ledger. Expected custody, dose and due times never come from owner replies.</summary>
    internal static class CarriedMaterialExposureSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }

        internal static int Exercise(Random random, bool omitContact)
        {
            int threshold = random.Next(100, 800), dirty = random.Next(threshold + 1, 1001), target = random.Next(threshold + 1);
            int[] raw = { random.Next(1, 41), random.Next(1, 41) };
            long[] cooldown = { random.Next(2, 501), random.Next(2, 501) };
            long lease = 5000, duration = random.Next(2, 501), host = 0, shift = 0;
            var world = new WorldSession(new WorldSessionConfiguration(42, 1000000, true, leaseMilliseconds: lease), new Access(), traceCapacity: 256);
            for (int i = 0; i < 2; i++)
            {
                world.RegisterConnection(Id(990 + i), Id(992 + i));
                world.Production.RegisterBatch(Id(994 + i), Id(996 + i), Id(998), Id(999), MaterialKind.Ore, 12, 100, dirty);
                world.RegisterWorkerContaminationSource(Id(1000 + i), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, raw[i], cooldown[i]));
            }
            world.Production.RegisterMachine(Id(1002), MachineRecipe.Washing(Id(1003), MaterialKind.Ore, duration, 1000, target));
            var ports = new[] { new LocalCommandPort(world, Id(990)), new LocalCommandPort(world, Id(991)) };
            var feed = new CarriedMaterialExposureFeed(world, new[] { Id(992), Id(993) }, new[] {
                new CarriedMaterialExposureSource(Id(994), Id(1000), threshold, "Cargo A"),
                new CarriedMaterialExposureSource(Id(995), Id(1001), threshold, "Cargo B") });
            int[] holder = { -1, -1 }, load = { 0, 0 }; long[] expiry = { 0, 0 }, revision = { 0, 0 };
            var suit = new WorkerSuit[2]; var next = new long[2, 2]; var sequence = new long[2, 2];
            var clean = new bool[2]; var slotted = new bool[2]; Guid[] batchId = { Id(996), Id(997) };
            bool paused = false, omitted = false; int steps = 0;
            world.Start();
            void Accepted(InteractionReply reply) => Require(reply.HasNewCommit, "Authored carried-material custody action was rejected.");
            void Check()
            {
                Require(world.View.ElapsedMilliseconds == shift && world.View.HostMilliseconds == host, "Carried-material clocks differ from independent pause ledger.");
                for (int w = 0; w < 2; w++)
                {
                    var worker = world.GetWorker(Id(992 + w))!;
                    Require(worker.Contamination == load[w], "Carried material load differs from independently scheduled custody exposure.");
                    Require(worker.Revision == revision[w] && worker.Suit == suit[w] && worker.CanInteract && worker.LastCauseId == Guid.Empty &&
                        worker.LastHazardId == Guid.Empty && worker.Pose == WorkerPose.Upright, "Carried contact changed independent PPE, revision or injury state.");
                }
                for (int c = 0; c < 2; c++)
                {
                    var claim = world.GetObject(Id(994 + c))!; var material = world.Production.GetBatch(Id(994 + c))!;
                    Require(claim.HolderId == (holder[c] < 0 ? (Guid?)null : Id(992 + holder[c])) &&
                        claim.SlotId == (slotted[c] ? (Guid?)Id(1002) : null), "Carried-material custody differs from independent holder/lease ledger.");
                    Require(material.BatchId == batchId[c] && material.Contamination == (clean[c] ? target : dirty) &&
                        material.Moisture == (clean[c] ? 1000 : 100) && material.Units == 12 && material.Kind == MaterialKind.Ore &&
                        material.Revision == (clean[c] ? 1 : 0) && material.Flags == MaterialFlags.None && material.OriginId == Id(998) && material.CauseId == Id(999),
                        "Carried contact changed independent material identity, properties or lineage.");
                }
                Require(world.Production.Summary.ReserveSpent == 0 && world.Production.Summary.ActiveUnits == 24 && world.Production.Summary.WasteUnits == 0,
                    "Carried contact changed material quantity or paid reserve."); steps++;
            }
            void Sample()
            {
                long[] command = { ports[0].LastTerminalSequence, ports[1].LastTerminalSequence };
                var actual = feed.Sample(); int count = 0;
                for (int c = 0; c < 2; c++)
                {
                    int w = holder[c];
                    if (paused || w < 0 || slotted[c] || clean[c] || shift < next[w, c]) continue;
                    int before = load[w], percent = suit[w] == WorkerSuit.Intact ? 25 : suit[w] == WorkerSuit.Compromised ? 50 : 100;
                    int effective = (raw[c] * percent + 99) / 100, after = Math.Min(100, before + effective);
                    sequence[w, c]++; next[w, c] = shift + cooldown[c];
                    var status = after == before ? WorkerStatus.NoChange : WorkerStatus.Applied;
                    Require(count < actual.Count, "Carried sampler omitted an independently due holder/source contact.");
                    var reply = actual[count++]; var contact = reply.ContaminationContact;
                    Require(reply.Worker?.Id == Id(992 + w) && reply.Status == status && reply.Changed == (after != before) &&
                        contact != null && contact.SourceId == Id(1000 + c) && contact.Sequence == sequence[w, c] &&
                        contact.SampleShiftMilliseconds == shift && contact.NextEligibleAtMilliseconds == next[w, c] && contact.RawUnits == raw[c] &&
                        contact.EffectiveUnits == effective && contact.Before == before && contact.After == after && contact.OriginalOutcome == status &&
                        contact.Kind == WorkerContaminationKind.Exposure && contact.CauseId != Guid.Empty,
                        "Carried contact differs from independent current-holder, PPE or cooldown schedule.");
                    var records = world.Trace.Records.Where(r => r.ContaminationContact?.CauseId == contact!.CauseId).ToArray();
                    Require(records.Length == 1, "Carried contact diagnostic publication was missing or duplicated.");
                    var row = records[0];
                    Require(row.ActorId == Id(992 + w) && row.EntityId == Id(994 + c) && row.BatchId == batchId[c] && row.MaterialCauseId == Id(999) &&
                        row.CarriedMaterial?.Contamination == dirty && row.CarriedMaterial.Units == 12,
                        "Carried contact lost its immutable dirty-material attribution.");
                    if (after != before) revision[w]++;
                    if (omitContact && !omitted) omitted = true; else load[w] = after;
                }
                Require(actual.Count == count && ports[0].LastTerminalSequence == command[0] && ports[1].LastTerminalSequence == command[1],
                    "Carried sampler added an unsolicited observation or client command."); Check();
            }
            void Advance(long delta)
            {
                host += delta; if (!paused) shift += delta;
                for (int c = 0; c < 2; c++) if (holder[c] >= 0 && host >= expiry[c]) holder[c] = -1;
                world.AdvanceTo(host); Check();
            }
            void Grab(int w, int c) { Accepted(ports[w].Grab(Id(994 + c))); holder[c] = w; expiry[c] = host + lease; Check(); }
            void Drop(int c) { Accepted(ports[holder[c]].Release(Id(994 + c))); holder[c] = -1; Check(); }
            void Pause()
            { if (paused) world.Resume(world.Epoch); else world.Pause(world.Epoch); paused = !paused; Check(); }
            void Suit(int w, WorkerSuit value)
            {
                var result = world.SetWorkerEnvironment(world.Epoch, Id(992 + w), revision[w], value, load[w]);
                Require(result.Status == (suit[w] == value ? WorkerStatus.Duplicate : WorkerStatus.Applied), "Carried PPE change unexpectedly rejected.");
                if (suit[w] != value) revision[w]++; suit[w] = value; Check();
            }
            Grab(0, 0); Sample(); Sample(); Drop(0); Grab(0, 0); Sample(); Drop(0); Grab(1, 0); Sample(); Drop(0); Grab(0, 0);
            Suit(0, WorkerSuit.Intact); Advance(cooldown[0]); Sample();
            Advance(cooldown[0] * 3); Sample(); Sample(); // Still leased: one current contact, no catch-up.
            Pause(); Advance(lease); Sample(); Pause(); Grab(0, 0); Sample();
            Drop(0); Grab(0, 1); Sample();
            for (int operation = 0; operation < 48; operation++)
            {
                int c = random.Next(2), w = random.Next(2), choice = random.Next(7);
                if (choice == 0) Advance(random.Next(0, 1001));
                else if (choice == 1) Pause();
                else if (choice == 2 && !paused)
                { if (holder[c] >= 0) Drop(c); else if (Array.IndexOf(holder, w) < 0) Grab(w, c); else Check(); }
                else if (choice == 3 && !paused) Suit(w, (WorkerSuit)random.Next(3));
                else if (choice == 4)
                {
                    long a = world.GetWorker(Id(992))!.Revision, b = world.GetWorker(Id(993))!.Revision;
                    feed.Describe(Id(992)); feed.Describe(Id(993));
                    Require(world.GetWorker(Id(992))!.Revision == a && world.GetWorker(Id(993))!.Revision == b, "Cargo guidance sampled exposure."); Check();
                }
                else Sample();
            }
            if (paused) Pause();
            for (int c = 0; c < 2; c++) if (holder[c] >= 0) Drop(c);
            Grab(0, 0); Accepted(ports[0].OperateMachine(Id(1002), ProductionAction.Insert, Id(994))); holder[0] = -1; slotted[0] = true; Sample();
            Accepted(ports[0].OperateMachine(Id(1002), ProductionAction.Start));
            host += duration; shift += duration; world.AdvanceTo(host); clean[0] = true;
            batchId[0] = world.Production.GetBatch(Id(994))!.BatchId; // Only the owner's opaque child identity is learned.
            Require(batchId[0] != Id(996) && world.Production.GetBatch(Id(994))!.ParentBatchId == Id(996), "Washing failed to replace the cargo batch with a child.");
            Check(); Sample(); Accepted(ports[0].OperateMachine(Id(1002), ProductionAction.Eject)); slotted[0] = false; Grab(0, 0);
            Advance(cooldown[0]); Sample();
            world.Stop(); Require(feed.Sample().Count == 0 && feed.BoundFeedCount == 0 && !feed.Failed, "Carried sampler retained terminal bindings.");
            return steps + 1;
        }
    }
}
