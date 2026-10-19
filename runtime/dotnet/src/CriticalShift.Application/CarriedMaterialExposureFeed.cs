#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public sealed class CarriedMaterialExposureSource
    {
        public CarriedMaterialExposureSource(Guid container, Guid source, int threshold, string label)
        {
            if (container == Guid.Empty || source == Guid.Empty || container == source || threshold < 0 || threshold >= 1000 ||
                string.IsNullOrWhiteSpace(label) || label.Length > 64) throw new ArgumentException("Bind distinct material/source identities, a bounded threshold and label.");
            ContainerId = container; SourceId = source; Threshold = threshold; Label = label;
        }
        public Guid ContainerId { get; }
        public Guid SourceId { get; }
        public int Threshold { get; }
        public string Label { get; }
    }

    /// <summary>One world-scoped trusted producer over explicit current custody. Owns scheduling, never condition or material.</summary>
    public sealed class CarriedMaterialExposureFeed
    {
        private WorldSession? world;
        private Guid[]? workers;
        private CarriedMaterialExposureSource[]? sources;
        private WorkerContaminationFeed?[,]? feeds;
        public Guid Epoch { get; }
        public bool Failed { get; private set; }
        public int BoundFeedCount
        {
            get { int count = 0; if (feeds != null) foreach (var feed in feeds) if (feed != null) count++; return count; }
        }

        public CarriedMaterialExposureFeed(WorldSession session, IReadOnlyList<Guid> workerIds, IReadOnlyList<CarriedMaterialExposureSource> bindings)
        {
            if (session == null || session.View.Phase != WorldPhase.Setup || workerIds == null || workerIds.Count < 1 || workerIds.Count > 4 ||
                bindings == null || bindings.Count < 1 || bindings.Count > 8) throw new ArgumentException("Compose bounded material exposure before world startup.");
            var actors = new Guid[workerIds.Count]; var definitions = new CarriedMaterialExposureSource[bindings.Count];
            var uniqueWorkers = new HashSet<Guid>(); var uniqueContainers = new HashSet<Guid>(); var uniqueSources = new HashSet<Guid>();
            for (int i = 0; i < actors.Length; i++)
            {
                Guid actor = workerIds[i];
                if (actor == Guid.Empty || !uniqueWorkers.Add(actor) || session.GetWorker(actor) == null)
                    throw new ArgumentException("Material exposure needs distinct registered workers.");
                actors[i] = actor;
            }
            for (int i = 0; i < definitions.Length; i++)
            {
                var definition = bindings[i];
                if (definition == null || !uniqueContainers.Add(definition.ContainerId) || !uniqueSources.Add(definition.SourceId) ||
                    session.GetObject(definition.ContainerId) == null || session.Production.GetBatch(definition.ContainerId) == null ||
                    !session.IsWorkerExposureSource(definition.SourceId))
                    throw new ArgumentException("Material exposure needs distinct material containers and registered Exposure sources.");
                definitions[i] = definition;
            }
            Array.Sort(actors); Array.Sort(definitions, (a, b) => a.ContainerId.CompareTo(b.ContainerId));
            var prepared = new WorkerContaminationFeed?[actors.Length, definitions.Length];
            for (int w = 0; w < actors.Length; w++)
                for (int s = 0; s < definitions.Length; s++) prepared[w, s] = new WorkerContaminationFeed(session, actors[w], definitions[s].SourceId);
            Epoch = session.Epoch; world = session; workers = actors; sources = definitions; feeds = prepared;
        }

        /// <summary>Call once after host-clock settlement. Each due feed observes only the current holder and material.</summary>
        public IReadOnlyList<WorkerReply> Sample()
        {
            if (world == null || Failed) return Array.Empty<WorkerReply>();
            if (world.View.Phase == WorldPhase.Setup) return Array.Empty<WorkerReply>();
            if (world.View.Phase != WorldPhase.Running && world.View.Phase != WorldPhase.Paused) { Clear(); return Array.Empty<WorkerReply>(); }
            if (world.View.Phase == WorldPhase.Paused) return Array.Empty<WorkerReply>();
            try
            {
                if (world.Epoch != Epoch) throw new InvalidOperationException("Material exposure cannot move to another world epoch.");
                for (int w = 0; w < workers!.Length; w++)
                    if (world.GetWorker(workers[w]) == null)
                        for (int s = 0; s < sources!.Length; s++) feeds![w, s] = null;
                var replies = new List<WorkerReply>();
                for (int s = 0; s < sources!.Length; s++)
                {
                    var definition = sources[s]; var claim = world.GetObject(definition.ContainerId);
                    if (claim == null) throw new InvalidOperationException("A live material exposure source lost its claim registration.");
                    if (claim.IsRetired) continue;
                    var batch = world.Production.GetBatch(definition.ContainerId);
                    if (claim.Epoch != Epoch || batch == null || batch.Epoch != Epoch || batch.ContainerId != definition.ContainerId)
                        throw new InvalidOperationException("A live material exposure source lost its exact current batch binding.");
                    if (!claim.HolderId.HasValue || claim.SlotId.HasValue || batch.Contamination <= definition.Threshold) continue;
                    Guid holder = claim.HolderId.Value;
                    if (world.GetWorker(holder) == null) throw new InvalidOperationException("Dirty carried material has no live worker owner.");
                    int w = Array.IndexOf(workers!, holder);
                    if (w < 0) throw new InvalidOperationException("A live dirty-material holder is absent from the sealed exposure bindings.");
                    var feed = feeds![w, s] ?? throw new InvalidOperationException("A live material holder lost its trusted exposure producer.");
                    var reply = feed.ObserveIfDue(batch);
                    if (reply != null) replies.Add(reply);
                }
                return replies.AsReadOnly();
            }
            catch { Failed = true; Clear(); throw; }
        }

        /// <summary>Current guidance only; this method never samples or advances any feed.</summary>
        public string Describe(Guid actor)
        {
            if (world == null || Failed || world.GetWorker(actor) == null) return "No active carried-material exposure";
            var labels = new List<string>();
            foreach (var definition in sources!)
            {
                var claim = world.GetObject(definition.ContainerId); var batch = world.Production.GetBatch(definition.ContainerId);
                if (claim != null && !claim.IsRetired && claim.HolderId == actor && !claim.SlotId.HasValue && batch != null && batch.Contamination > definition.Threshold)
                    labels.Add(definition.Label);
            }
            return labels.Count == 0 ? "No dirty cargo currently held" : "Dirty cargo: " + string.Join(", ", labels) + ". PPE reduces exposure; wash the cargo and use the wash area.";
        }
        public void Clear()
        {
            if (feeds != null) Array.Clear(feeds, 0, feeds.Length);
            world = null; workers = null; sources = null; feeds = null;
        }
    }
}
