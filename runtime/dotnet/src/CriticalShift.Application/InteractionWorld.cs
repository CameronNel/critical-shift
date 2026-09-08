using System;
using System.Collections.Generic;
using CriticalShift.Features.Interaction.Domain;

namespace CriticalShift.Application
{
    /// <summary>
    /// Host-side interaction workflow for one world epoch. Single-threaded, no callbacks mid-commit.
    /// Connections must already be authenticated by the caller. This is not a networking service.
    /// </summary>
    public sealed class InteractionWorld
    {
        private readonly ExclusiveClaimStore _claims;
        private readonly IInteractionAccessPolicy _access;
        private readonly Dictionary<Guid, Connection> _connections = new Dictionary<Guid, Connection>();
        private readonly int _maxConnections;
        private readonly int _receiptCapacity;
        private bool _started;
        private bool _stopped;
        private bool _faulted;
        private bool _executing;

        public InteractionWorld(Guid epoch, IInteractionAccessPolicy access, int maxEntities = 128,
            int maxConnections = 4, int receiptCapacity = 256, long leaseMilliseconds = 3000)
        {
            if (epoch == Guid.Empty) throw new ArgumentException("World epoch must not be empty.", nameof(epoch));
            if (maxConnections < 1 || maxConnections > 4) throw new ArgumentOutOfRangeException(nameof(maxConnections));
            if (receiptCapacity < 1 || receiptCapacity > 4096) throw new ArgumentOutOfRangeException(nameof(receiptCapacity));
            Epoch = epoch;
            _access = access ?? throw new ArgumentNullException(nameof(access));
            _claims = new ExclusiveClaimStore(maxEntities, leaseMilliseconds);
            _maxConnections = maxConnections;
            _receiptCapacity = receiptCapacity;
        }

        public Guid Epoch { get; }
        public bool IsStopped => _stopped;
        public bool IsFaulted => _faulted;
        public int RegisteredCount => _claims.RegisteredCount;
        public int ActiveClaimCount => _claims.ActiveClaimCount;

        public void RegisterObject(Guid entityId) { RequireSetup(); _claims.Register(entityId); }

        public void RegisterConnection(Guid connectionId, Guid actorId)
        {
            RequireSetup();
            if (connectionId == Guid.Empty || actorId == Guid.Empty)
                throw new ArgumentException("Connection and actor identities must not be empty.");
            if (_connections.ContainsKey(connectionId)) throw new InvalidOperationException("Duplicate connection identity.");
            foreach (var connection in _connections.Values)
                if (connection.ActorId == actorId) throw new InvalidOperationException("An actor may have only one connection.");
            if (_connections.Count >= _maxConnections) throw new InvalidOperationException("Connection capacity reached.");
            _connections.Add(connectionId, new Connection(actorId, _receiptCapacity));
        }

        public void Start()
        {
            RequireSetup();
            bool hasConnectedActor = false;
            foreach (var connection in _connections.Values)
                if (connection.Connected) { hasConnectedActor = true; break; }
            if (!hasConnectedActor) throw new InvalidOperationException("A connected actor is required before starting.");
            _started = true;
        }

        public ObjectClaimView? GetObject(Guid entityId) => Project(_claims.Get(entityId));
        public int RetainedReceiptCount(Guid connectionId) =>
            _connections.TryGetValue(connectionId, out var c) ? c.Receipts.Count : 0;
        public long LastSequence(Guid connectionId) =>
            _connections.TryGetValue(connectionId, out var c) ? c.Receipts.LastSequence : 0;

        public InteractionReply Execute(Guid connectionId, InteractionCommand command)
        {
            if (command == null) throw new ArgumentNullException(nameof(command));
            RequireIdle();
            var readiness = Readiness(command.Epoch);
            if (readiness != null) return readiness;
            if (!_connections.TryGetValue(connectionId, out var connection) || !connection.Connected)
                return new InteractionReply(InteractionStatus.UnknownConnection, false);
            if (!command.IsWellFormed) return new InteractionReply(InteractionStatus.InvalidPayload, false);
            var replay = connection.Receipts.Check(command);
            if (replay != null) return replay;

            _executing = true;
            try
            {
                var reply = Apply(connection.ActorId, command);
                // Gameplay rejections are terminal too, so the next sequence is never wedged.
                connection.Receipts.Record(command, reply);
                return reply;
            }
            catch
            {
                // Never retry a possibly partially committed operation after an unexpected failure.
                _faulted = true;
                throw;
            }
            finally { _executing = false; }
        }

        public IReadOnlyList<ObjectClaimView> AdvanceTo(long monotonicMilliseconds)
        {
            RequireRunning();
            var changes = _claims.AdvanceTo(monotonicMilliseconds);
            var views = new List<ObjectClaimView>(changes.Count);
            foreach (var change in changes) views.Add(Project(change)!);
            return views.AsReadOnly();
        }

        public ObjectClaimView? Disconnect(Guid connectionId)
        {
            RequireIdle();
            if (_stopped || !_connections.TryGetValue(connectionId, out var connection) || !connection.Connected) return null;
            connection.Connected = false;
            connection.Receipts.Clear();
            return Project(_claims.ReleaseActor(connection.ActorId));
        }

        /// <summary>Trusted binding callback. An old generation may not release a newer claim.</summary>
        public InteractionReply ReportAttachmentFailure(Guid epoch, Guid entityId, long leaseGeneration)
        {
            RequireIdle();
            var readiness = Readiness(epoch);
            if (readiness != null) return readiness;
            var state = _claims.Get(entityId);
            if (state == null) return new InteractionReply(InteractionStatus.UnknownEntity, false);
            if (!state.HolderId.HasValue) return new InteractionReply(InteractionStatus.StaleLease, false, Project(state));
            return Map(_claims.TryRelease(entityId, state.HolderId.Value, leaseGeneration), false);
        }

        public InteractionReply RetireObject(Guid epoch, Guid entityId)
        {
            RequireIdle();
            var readiness = Readiness(epoch);
            return readiness ?? Map(_claims.Retire(entityId), false);
        }

        public void Stop()
        {
            RequireIdle();
            _stopped = true;
            _claims.Stop();
            _connections.Clear();
        }

        private InteractionReply Apply(Guid actorId, InteractionCommand command)
        {
            // Releasing must remain possible when an object moves out of reach.
            if (command.Kind != InteractionKind.Release)
            {
                var access = _access.Evaluate(actorId, command.EntityId, command.Kind);
                switch (access)
                {
                    case AccessDecision.OutOfReach: return new InteractionReply(InteractionStatus.OutOfReach, true);
                    case AccessDecision.ActorUnavailable: return new InteractionReply(InteractionStatus.ActorUnavailable, true);
                    case AccessDecision.TargetUnavailable: return new InteractionReply(InteractionStatus.TargetUnavailable, true);
                    case AccessDecision.Allowed: break;
                    default: throw new InvalidOperationException("Invalid host access-policy result.");
                }
            }
            switch (command.Kind)
            {
                case InteractionKind.Grab: return Map(_claims.TryGrab(command.EntityId, actorId, command.ExpectedRevision), true);
                case InteractionKind.Release: return Map(_claims.TryRelease(command.EntityId, actorId, command.LeaseGeneration), true);
                case InteractionKind.Renew: return Map(_claims.TryRenew(command.EntityId, actorId, command.LeaseGeneration), true);
                default: throw new InvalidOperationException("An unvalidated interaction reached the domain.");
            }
        }

        private InteractionReply Map(ClaimResult result, bool terminal)
        {
            InteractionStatus status;
            switch (result.Error)
            {
                case ClaimError.None: status = result.Changed ? InteractionStatus.Applied : InteractionStatus.NoChange; break;
                case ClaimError.UnknownEntity: status = InteractionStatus.UnknownEntity; break;
                case ClaimError.EntityRetired: status = InteractionStatus.EntityRetired; break;
                case ClaimError.AlreadyClaimed: status = InteractionStatus.AlreadyClaimed; break;
                case ClaimError.ActorAlreadyHolding: status = InteractionStatus.ActorAlreadyHolding; break;
                case ClaimError.NotHolder: status = InteractionStatus.NotHolder; break;
                case ClaimError.StaleLease: status = InteractionStatus.StaleLease; break;
                case ClaimError.RevisionConflict: status = InteractionStatus.RevisionConflict; break;
                case ClaimError.StoreStopped: status = InteractionStatus.WorldStopped; break;
                default: throw new InvalidOperationException("Unmapped claim result.");
            }
            return new InteractionReply(status, terminal, Project(result.Snapshot));
        }

        private ObjectClaimView? Project(ClaimSnapshot? state) => state == null ? null :
            new ObjectClaimView(Epoch, state.EntityId, state.HolderId, state.Revision,
                state.LeaseGeneration, state.ExpiresAtMilliseconds, state.IsRetired);

        private InteractionReply? Readiness(Guid epoch)
        {
            if (_stopped) return new InteractionReply(InteractionStatus.WorldStopped, false);
            if (_faulted) return new InteractionReply(InteractionStatus.WorldFaulted, false);
            if (!_started) return new InteractionReply(InteractionStatus.NotReady, false);
            return epoch == Epoch ? null : new InteractionReply(InteractionStatus.WrongEpoch, false);
        }

        private void RequireIdle()
        {
            if (_executing) throw new InvalidOperationException("Interaction workflows may not be re-entered.");
        }
        private void RequireSetup()
        {
            RequireIdle();
            if (_started || _stopped || _faulted) throw new InvalidOperationException("Registration is limited to world setup.");
        }
        private void RequireRunning()
        {
            RequireIdle();
            if (!_started || _stopped || _faulted) throw new InvalidOperationException("The interaction world is not running.");
        }

        private sealed class Connection
        {
            internal Connection(Guid actorId, int capacity) { ActorId = actorId; Receipts = new CommandReceipts(capacity); }
            internal Guid ActorId { get; }
            internal CommandReceipts Receipts { get; }
            internal bool Connected { get; set; } = true;
        }
    }
}
