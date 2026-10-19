#nullable enable
using System;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    internal sealed partial class WorkerWorkflow
    {
        internal WorkerReply BeginSuitFitting(Guid actor, long revision, Guid station, Guid attempt, SuitFittingRules rules, long now, WorkerSuit target = WorkerSuit.Intact) =>
            _workers.TryGetValue(actor, out var worker) ? Reply(worker.BeginSuitFitting(revision, station, attempt, rules, now, (SuitCondition)(int)target), worker) :
            new WorkerReply(WorkerStatus.UnknownWorker);
        internal WorkerReply CancelSuitFitting(Guid actor, Guid attempt) =>
            _workers.TryGetValue(actor, out var worker) ? Reply(worker.CancelSuitFitting(attempt), worker) : new WorkerReply(WorkerStatus.UnknownWorker);
        internal WorkerReply CompleteSuitFitting(Guid actor, Guid attempt, long now) =>
            _workers.TryGetValue(actor, out var worker) ? Reply(worker.CompleteSuitFitting(attempt, now), worker) : new WorkerReply(WorkerStatus.UnknownWorker);
    }
}
