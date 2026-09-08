using System;
using System.Collections.Generic;
using CriticalShift.Features.Session.Domain;

namespace CriticalShift.Application
{
    /// <summary>
    /// Trusted single-threaded composition of one shift, its timers and the existing interaction owner.
    /// This is logical world/session state, not a scene, physics simulation or network server.
    /// </summary>
    public sealed partial class WorldSession
    {
        private readonly SessionTimeline _timeline;
        private readonly WorldTimerQueue _timers;
        private readonly InteractionWorld _interaction;
        private readonly WorkerWorkflow _workers;
        private readonly SessionDiagnostics _diagnostics;
        private readonly long _recoveryCompletionWindowMilliseconds;
        private bool _executing;
        private bool _restartIssued;
        private long _revision;

        public WorldSession(WorldSessionConfiguration configuration, IInteractionAccessPolicy access,
            IWorkerRecoveryPolicy? recovery = null, int traceCapacity = 128,
            long recoveryCompletionWindowMilliseconds = 5000)
        {
            Configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            if (access == null) throw new ArgumentNullException(nameof(access));
            if (recoveryCompletionWindowMilliseconds < 1 || recoveryCompletionWindowMilliseconds > 60000)
                throw new ArgumentOutOfRangeException(nameof(recoveryCompletionWindowMilliseconds));
            _recoveryCompletionWindowMilliseconds = recoveryCompletionWindowMilliseconds;
            _diagnostics = new SessionDiagnostics(traceCapacity);
            // Epoch identity is deliberately distinct from reproducible gameplay seed/configuration.
            _timeline = new SessionTimeline(Guid.NewGuid(), configuration.Seed,
                configuration.ShiftDurationMilliseconds, configuration.AllowPause);
            _timers = new WorldTimerQueue(Epoch, configuration.TimerCapacity);
            _workers = new WorkerWorkflow(Epoch, configuration.MaxConnections, recovery, recoveryCompletionWindowMilliseconds);
            _interaction = new InteractionWorld(Epoch, new RunningAccess(_timeline, _workers, access),
                configuration.MaxObjects, configuration.MaxConnections,
                configuration.ReceiptCapacity, configuration.LeaseMilliseconds);
        }

        public Guid Epoch => _timeline.Epoch;
        public WorldSessionConfiguration Configuration { get; }
        public WorldSessionView View => new WorldSessionView(Epoch, _revision, _timeline.Seed,
            Map(_timeline.Phase), Map(_timeline.Outcome), _timeline.HostMilliseconds,
            _timeline.ElapsedMilliseconds, _timeline.RemainingMilliseconds, _timers.Count,
            _interaction.RegisteredCount, _interaction.ActiveClaimCount, _interaction.ConnectedCount);

        public void RegisterObject(Guid entityId)
        {
            RequireIdle(); long next = NextRevision();
            _interaction.RegisterObject(entityId); _revision = next;
        }
        public void RegisterConnection(Guid connectionId, Guid actorId)
        {
            RequireIdle(); long next = NextRevision();
            _workers.ValidateRegistration(actorId);
            _interaction.RegisterConnection(connectionId, actorId);
            _workers.Register(actorId); _revision = next;
        }
        public ObjectClaimView? GetObject(Guid entityId) => _interaction.GetObject(entityId);

        public void Start(long hostMilliseconds = 0)
        {
            RequireIdle();
            if (_timeline.Phase != TimelinePhase.Setup) throw new InvalidOperationException("World setup has finished.");
            if (hostMilliseconds < 0) throw new ArgumentOutOfRangeException(nameof(hostMilliseconds));
            if (_interaction.ConnectedCount == 0) throw new InvalidOperationException("A connected actor is required.");
            long next = NextRevision();
            try
            {
                _timeline.Start(hostMilliseconds);
                _timers.AdvanceTo(hostMilliseconds, 0);
                _interaction.Start();
                _interaction.AdvanceTo(hostMilliseconds);
                _revision = next;
                _diagnostics.Append(View, Epoch, SessionTraceKind.Started, changed: true);
            }
            catch { FailClosed(); throw; }
        }

        public WorldAdvanceResult AdvanceTo(long hostMilliseconds)
        {
            RequireIdle();
            if (hostMilliseconds < _timeline.HostMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(hostMilliseconds), "Host time cannot move backwards.");
            if (!_timeline.IsActive) return EmptyAdvance(false);
            long next = NextRevision();
            bool timeChanged = hostMilliseconds != _timeline.HostMilliseconds;
            try
            {
                if (_timeline.AdvanceTo(hostMilliseconds))
                {
                    // End wins over advisory notifications in this batch, including overdue signals.
                    // A terminal snapshot requires complete adapter teardown, not just released-claim handling.
                    StopOwnedResources(); _revision = next;
                    _diagnostics.Append(View, Epoch, SessionTraceKind.Ended, changed: true);
                    return EmptyAdvance(true);
                }
                var released = _interaction.AdvanceTo(hostMilliseconds);
                var workerChanges = _workers.ExpireRecovery(_timeline.ElapsedMilliseconds);
                var due = _timers.AdvanceTo(hostMilliseconds, _timeline.ElapsedMilliseconds);
                var signals = new List<WorldTimerSignal>(due.Count);
                foreach (var entry in due)
                    signals.Add(new WorldTimerSignal(new WorldTimerHandle(entry.Epoch, entry.Sequence),
                        entry.OwnerId, entry.Signal, entry.Clock == TimerClock.Host ?
                        WorldTimeBasis.RealTime : WorldTimeBasis.ShiftTime, entry.DueMilliseconds));
                if (timeChanged || released.Count != 0 || due.Count != 0 || workerChanges.Count != 0) _revision = next;
                foreach (var change in workerChanges)
                    _diagnostics.Append(View, Epoch, SessionTraceKind.RecoveryExpired, change.Worker!.Id,
                        input: change.Worker.RecoveryAttempt, changed: true, worker: change,
                        previousWorkerRevision: change.Worker.Revision - 1);
                if (timeChanged || released.Count != 0 || due.Count != 0)
                    _diagnostics.Append(View, Epoch, SessionTraceKind.Advanced, changed: true);
                return new WorldAdvanceResult(View, signals.AsReadOnly(), released, false, workerChanges);
            }
            catch { FailClosed(); throw; }
        }

        // Controls operate at the last processed host sample. The host must keep pumping real time
        // during pause, and sample before changing pause/resume state. No hidden clock or callback runs here.
        public WorldControlStatus Pause(Guid epoch)
        {
            RequireIdle();
            var rejection = Readiness(epoch);
            if (rejection.HasValue) return rejection.Value;
            if (!Configuration.AllowPause) return WorldControlStatus.PauseDisabled;
            long next = NextRevision();
            if (!_timeline.TryPause()) return WorldControlStatus.NoChange;
            _revision = next; return WorldControlStatus.Applied;
        }

        public WorldControlStatus Resume(Guid epoch)
        {
            RequireIdle();
            var rejection = Readiness(epoch);
            if (rejection.HasValue) return rejection.Value;
            long next = NextRevision();
            if (!_timeline.TryResume()) return WorldControlStatus.NoChange;
            _revision = next; return WorldControlStatus.Applied;
        }

        public WorldControlStatus Finish(Guid epoch, WorldEndReason reason)
        {
            RequireIdle();
            var rejection = Readiness(epoch);
            if (rejection.HasValue) return rejection.Value;
            var outcome = reason switch
            {
                WorldEndReason.Succeeded => TimelineOutcome.Succeeded,
                WorldEndReason.Failed => TimelineOutcome.Failed,
                WorldEndReason.Aborted => TimelineOutcome.Aborted,
                WorldEndReason.HostLost => TimelineOutcome.HostLost,
                _ => throw new ArgumentOutOfRangeException(nameof(reason))
            };
            long next = NextRevision();
            _timeline.TryFinish(outcome); StopOwnedResources(); _revision = next;
            _diagnostics.Append(View, epoch, SessionTraceKind.Ended, changed: true);
            return WorldControlStatus.Applied;
        }

        public WorldTimerScheduleReply Schedule(Guid epoch, Guid ownerId, string signal,
            long delayMilliseconds, WorldTimeBasis basis = WorldTimeBasis.ShiftTime)
        {
            RequireIdle();
            var rejection = Readiness(epoch);
            if (rejection.HasValue) return new WorldTimerScheduleReply(rejection.Value);
            var clock = basis switch
            {
                WorldTimeBasis.RealTime => TimerClock.Host,
                WorldTimeBasis.ShiftTime => TimerClock.Simulation,
                _ => throw new ArgumentOutOfRangeException(nameof(basis))
            };
            long next = NextRevision();
            if (!_timers.TrySchedule(ownerId, signal, clock, delayMilliseconds, out var entry))
                return new WorldTimerScheduleReply(WorldControlStatus.TimerCapacityReached);
            _revision = next;
            return new WorldTimerScheduleReply(WorldControlStatus.Applied, new WorldTimerHandle(Epoch, entry!.Sequence));
        }

        public WorldControlStatus CancelTimer(WorldTimerHandle handle)
        {
            if (handle == null) throw new ArgumentNullException(nameof(handle));
            RequireIdle();
            var rejection = Readiness(handle.Epoch);
            if (rejection.HasValue) return rejection.Value;
            long next = NextRevision();
            if (!_timers.Cancel(handle.Epoch, handle.Sequence)) return WorldControlStatus.NoChange;
            _revision = next; return WorldControlStatus.Applied;
        }

        public int CancelTimersForOwner(Guid epoch, Guid ownerId)
        {
            RequireIdle();
            if (Readiness(epoch).HasValue) return 0;
            long next = NextRevision();
            int count = _timers.CancelOwner(epoch, ownerId);
            if (count != 0) _revision = next;
            return count;
        }

        public InteractionReply ExecuteInteraction(Guid connectionId, InteractionCommand command)
        {
            if (command == null) throw new ArgumentNullException(nameof(command));
            RequireIdle();
            if (command.Epoch != Epoch) return new InteractionReply(InteractionStatus.WrongEpoch, false);
            if (_timeline.Phase == TimelinePhase.Faulted)
                return new InteractionReply(InteractionStatus.WorldFaulted, false);
            long next = NextRevision();
            _executing = true;
            try
            {
                var reply = _interaction.Execute(connectionId, command);
                if (reply.HasNewCommit) _revision = next;
                _diagnostics.Append(View, command.Epoch, SessionTraceKind.Interaction,
                    _interaction.ConnectedActor(connectionId) ?? Guid.Empty, command.EntityId,
                    command.Sequence, reply.HasNewCommit, interaction: reply);
                return reply;
            }
            catch { FailClosed(); throw; }
            finally { _executing = false; }
        }

        // Identity checks are required even on trusted adapter callbacks: IDs may recur in a new shift.
        // Timer-owner groups are explicit; the feature that owns a group cancels it when its lifetime ends.
        public ObjectClaimView? Disconnect(Guid epoch, Guid connectionId)
        {
            RequireIdle();
            if (epoch != Epoch) return null;
            long next = NextRevision(); int count = _interaction.ConnectedCount;
            var actor = _interaction.ConnectedActor(connectionId);
            try
            {
                var released = _interaction.Disconnect(connectionId);
                if (count != _interaction.ConnectedCount)
                {
                    if (actor.HasValue) { _workers.Remove(actor.Value); _timers.CancelOwner(epoch, actor.Value); }
                    _revision = next;
                    _diagnostics.Append(View, epoch, SessionTraceKind.Disconnected, actor ?? Guid.Empty,
                        released?.EntityId ?? Guid.Empty, changed: true);
                }
                return released;
            }
            catch { FailClosed(); throw; }
        }

        public InteractionReply ReportAttachmentFailure(Guid epoch, Guid entityId, long generation)
        {
            RequireIdle(); long next = NextRevision();
            try
            {
                var reply = _interaction.ReportAttachmentFailure(epoch, entityId, generation);
                if (reply.HasNewCommit) _revision = next;
                return reply;
            }
            catch { FailClosed(); throw; }
        }

        public InteractionReply RetireObject(Guid epoch, Guid entityId)
        {
            RequireIdle(); long next = NextRevision();
            try
            {
                var reply = _interaction.RetireObject(epoch, entityId);
                if (reply.HasNewCommit)
                {
                    _timers.CancelOwner(epoch, entityId); _revision = next;
                }
                return reply;
            }
            catch { FailClosed(); throw; }
        }

        public void Stop()
        {
            RequireIdle();
            if (_timeline.Phase == TimelinePhase.Stopped) return;
            long next = NextRevision();
            _timeline.Stop(); StopOwnedResources(); _revision = next;
            _diagnostics.Append(View, Epoch, SessionTraceKind.Stopped, changed: true);
        }

        /// <summary>
        /// Return one fresh setup-only successor. Explicit access-policy rebinding avoids silently
        /// reusing references to old world objects. The caller must bind its roster and entities again.
        /// </summary>
        public WorldSession Restart(IInteractionAccessPolicy nextWorldAccess, IWorkerRecoveryPolicy? nextRecovery = null)
        {
            RequireIdle();
            if (_restartIssued) throw new InvalidOperationException("A successor was already created from this world.");
            var next = new WorldSession(Configuration, nextWorldAccess, nextRecovery, _diagnostics.Capacity,
                _recoveryCompletionWindowMilliseconds);
            Stop(); _restartIssued = true;
            return next;
        }

        private WorldAdvanceResult EmptyAdvance(bool ended) => new WorldAdvanceResult(View,
            Array.Empty<WorldTimerSignal>(), Array.Empty<ObjectClaimView>(), ended);
        private long NextRevision() => checked(_revision + 1);
        private void StopOwnedResources() { _timers.Stop(); _interaction.Stop(); _workers.Clear(); }
        private void FailClosed()
        {
            _timeline.Fault(); StopOwnedResources();
            if (_revision < long.MaxValue) _revision++;
            _diagnostics.Append(View, Epoch, SessionTraceKind.Faulted, changed: true);
        }
        private void RequireIdle()
        {
            if (_executing) throw new InvalidOperationException("World operations may not be re-entered.");
        }

        private WorldControlStatus? Readiness(Guid epoch)
        {
            if (epoch != Epoch) return WorldControlStatus.WrongEpoch;
            return _timeline.Phase switch
            {
                TimelinePhase.Setup => WorldControlStatus.NotReady,
                TimelinePhase.Ended => WorldControlStatus.Ended,
                TimelinePhase.Stopped => WorldControlStatus.Stopped,
                TimelinePhase.Faulted => WorldControlStatus.Faulted,
                _ => (WorldControlStatus?)null
            };
        }

        private static WorldPhase Map(TimelinePhase phase) => phase switch
        {
            TimelinePhase.Setup => WorldPhase.Setup, TimelinePhase.Running => WorldPhase.Running,
            TimelinePhase.Paused => WorldPhase.Paused, TimelinePhase.Ended => WorldPhase.Ended,
            TimelinePhase.Stopped => WorldPhase.Stopped, TimelinePhase.Faulted => WorldPhase.Faulted,
            _ => throw new InvalidOperationException("Unmapped timeline phase.")
        };
        private static WorldOutcome Map(TimelineOutcome outcome) => outcome switch
        {
            TimelineOutcome.None => WorldOutcome.None, TimelineOutcome.Succeeded => WorldOutcome.Succeeded,
            TimelineOutcome.Failed => WorldOutcome.Failed, TimelineOutcome.TimedOut => WorldOutcome.TimedOut,
            TimelineOutcome.Aborted => WorldOutcome.Aborted, TimelineOutcome.HostLost => WorldOutcome.HostLost,
            TimelineOutcome.Faulted => WorldOutcome.Faulted,
            _ => throw new InvalidOperationException("Unmapped timeline outcome.")
        };

        private sealed class RunningAccess : IInteractionAccessPolicy
        {
            private readonly SessionTimeline _timeline;
            private readonly IInteractionAccessPolicy _inner;
            private readonly WorkerWorkflow _workers;
            internal RunningAccess(SessionTimeline timeline, WorkerWorkflow workers, IInteractionAccessPolicy inner)
            { _timeline = timeline; _workers = workers; _inner = inner; }
            public AccessDecision Evaluate(Guid actorId, Guid entityId, InteractionKind kind)
            {
                // Rejections use the existing receipt stream; pause cannot create a sequence gap.
                // Release and host-approved renewal remain possible while simulation is paused.
                return !_workers.CanInteract(actorId) ||
                    (kind == InteractionKind.Grab && _timeline.Phase != TimelinePhase.Running) ?
                    AccessDecision.ActorUnavailable : _inner.Evaluate(actorId, entityId, kind);
            }
        }
    }
}
