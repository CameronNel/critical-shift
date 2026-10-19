#nullable enable
using System;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    public enum SuitFittingAction { Start, Cancel }
    public enum SuitFittingStatus { Applied, NoChange, UnknownStation, RevisionConflict, InvalidWorker, HandsOccupied, StationOccupied, StaleAttempt, InvalidTime }
    public enum SuitFittingEvent { Started, Completed, Cancelled, Interrupted }
    public sealed class SuitFittingDefinition
    {
        public SuitFittingDefinition(long durationMilliseconds = 20000) { Rules = new SuitFittingRules(durationMilliseconds); }
        internal SuitFittingRules Rules { get; }
        public long DurationMilliseconds => Rules.DurationMilliseconds;
    }
    public sealed class SuitFittingRequest
    {
        public const int CurrentVersion = 1;
        public SuitFittingRequest(SuitFittingAction action, long workerRevision = 0, Guid attempt = default, int version = CurrentVersion)
        { Action = action; WorkerRevision = workerRevision; AttemptId = attempt; Version = version; }
        public SuitFittingAction Action { get; }
        public long WorkerRevision { get; }
        public Guid AttemptId { get; }
        public int Version { get; }
        internal bool IsWellFormed => Version == CurrentVersion &&
            (Action == SuitFittingAction.Start ? WorkerRevision >= 0 && AttemptId == Guid.Empty :
             Action == SuitFittingAction.Cancel && WorkerRevision == 0 && AttemptId != Guid.Empty);
        internal bool Same(SuitFittingRequest other) => Action == other.Action && WorkerRevision == other.WorkerRevision &&
            AttemptId == other.AttemptId && Version == other.Version;
    }
    public sealed class SuitFittingAttemptView
    {
        internal SuitFittingAttemptView(SuitFittingAttempt attempt)
        { Id = attempt.Id; StationId = attempt.StationId; StartedAtMilliseconds = attempt.StartedAtMilliseconds;
          DueAtMilliseconds = attempt.DueAtMilliseconds; OriginalSuit = (WorkerSuit)(int)attempt.OriginalSuit; }
        public Guid Id { get; }
        public Guid StationId { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public WorkerSuit OriginalSuit { get; }
    }
    public sealed class SuitFittingChange
    {
        internal SuitFittingChange(SuitFittingEvent kind, WorkerView worker, SuitFittingAttemptView attempt, long at)
        { Kind = kind; Worker = worker; Attempt = attempt; ShiftMilliseconds = at; PreviousWorkerRevision = checked(worker.Revision - 1); }
        public SuitFittingEvent Kind { get; }
        public WorkerView Worker { get; }
        public SuitFittingAttemptView Attempt { get; }
        public long ShiftMilliseconds { get; }
        public long PreviousWorkerRevision { get; }
    }
    public sealed class SuitFittingReply
    {
        internal SuitFittingReply(SuitFittingStatus status, WorkerView? worker, SuitFittingChange? change)
        { Status = status; Worker = worker; Change = change; }
        public SuitFittingStatus Status { get; }
        public WorkerView? Worker { get; }
        public SuitFittingChange? Change { get; }
    }
    public sealed class SuitFittingSummary
    {
        internal SuitFittingSummary(long started, long completed, long cancelled, long interrupted, int pending, bool countersSaturated = false)
        { Started = started; Completed = completed; Cancelled = cancelled; Interrupted = interrupted; Pending = pending; CountersSaturated = countersSaturated; }
        public long Started { get; }
        public long Completed { get; }
        public long Cancelled { get; }
        public long Interrupted { get; }
        public int Pending { get; }
        public bool CountersSaturated { get; }
    }
}
