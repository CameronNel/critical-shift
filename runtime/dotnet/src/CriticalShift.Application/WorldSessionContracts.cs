using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public enum WorldPhase { Setup, Running, Paused, Ended, Stopped, Faulted }
    public enum WorldOutcome { None, Succeeded, Failed, TimedOut, Aborted, HostLost, Faulted }
    public enum WorldEndReason { Succeeded, Failed, Aborted, HostLost }
    public enum WorldTimeBasis { RealTime, ShiftTime }
    public enum WorldControlStatus
    {
        Applied, NoChange, WrongEpoch, NotReady, Ended, Stopped, Faulted,
        PauseDisabled, TimerCapacityReached
    }

    /// <summary>Immutable authored inputs, not mutable run state or a save-game format.</summary>
    public sealed class WorldSessionConfiguration
    {
        public WorldSessionConfiguration(int seed, long shiftDurationMilliseconds, bool allowPause = false,
            int timerCapacity = 128, int maxObjects = 128, int maxConnections = 4,
            int receiptCapacity = 256, long leaseMilliseconds = 3000)
        {
            if (shiftDurationMilliseconds <= 0) throw new ArgumentOutOfRangeException(nameof(shiftDurationMilliseconds));
            if (timerCapacity < 1 || timerCapacity > 4096) throw new ArgumentOutOfRangeException(nameof(timerCapacity));
            if (maxObjects < 1) throw new ArgumentOutOfRangeException(nameof(maxObjects));
            if (maxConnections < 1 || maxConnections > 4) throw new ArgumentOutOfRangeException(nameof(maxConnections));
            if (receiptCapacity < 1 || receiptCapacity > 4096) throw new ArgumentOutOfRangeException(nameof(receiptCapacity));
            if (leaseMilliseconds < 1) throw new ArgumentOutOfRangeException(nameof(leaseMilliseconds));
            Seed = seed;
            ShiftDurationMilliseconds = shiftDurationMilliseconds;
            AllowPause = allowPause;
            TimerCapacity = timerCapacity;
            MaxObjects = maxObjects;
            MaxConnections = maxConnections;
            ReceiptCapacity = receiptCapacity;
            LeaseMilliseconds = leaseMilliseconds;
        }

        public int Seed { get; }
        public long ShiftDurationMilliseconds { get; }
        public bool AllowPause { get; }
        public int TimerCapacity { get; }
        public int MaxObjects { get; }
        public int MaxConnections { get; }
        public int ReceiptCapacity { get; }
        public long LeaseMilliseconds { get; }
    }

    public sealed class WorldSessionView
    {
        internal WorldSessionView(Guid epoch, long revision, int seed, WorldPhase phase, WorldOutcome outcome,
            long hostMilliseconds, long elapsedMilliseconds, long remainingMilliseconds,
            int timerCount, int objectCount, int claimCount, int connectionCount)
        {
            Epoch = epoch; Revision = revision; Seed = seed; Phase = phase; Outcome = outcome;
            HostMilliseconds = hostMilliseconds; ElapsedMilliseconds = elapsedMilliseconds;
            RemainingMilliseconds = remainingMilliseconds; PendingTimerCount = timerCount;
            RegisteredObjectCount = objectCount; ActiveClaimCount = claimCount;
            ConnectedPlayerCount = connectionCount;
        }

        public Guid Epoch { get; }
        public long Revision { get; }
        public int Seed { get; }
        public WorldPhase Phase { get; }
        public WorldOutcome Outcome { get; }
        public long HostMilliseconds { get; }
        public long ElapsedMilliseconds { get; }
        public long RemainingMilliseconds { get; }
        public int PendingTimerCount { get; }
        public int RegisteredObjectCount { get; }
        public int ActiveClaimCount { get; }
        public int ConnectedPlayerCount { get; }
    }

    /// <summary>Both epoch and sequence are required; a sequence alone is not a timer identity.</summary>
    public sealed class WorldTimerHandle
    {
        internal WorldTimerHandle(Guid epoch, long sequence) { Epoch = epoch; Sequence = sequence; }
        public Guid Epoch { get; }
        public long Sequence { get; }
    }

    /// <summary>A dequeued signal, not an executable callback or permission to mutate a later world.</summary>
    public sealed class WorldTimerSignal
    {
        internal WorldTimerSignal(WorldTimerHandle handle, Guid ownerId, string signal,
            WorldTimeBasis basis, long dueMilliseconds)
        {
            Handle = handle; OwnerId = ownerId; Signal = signal;
            Basis = basis; DueMilliseconds = dueMilliseconds;
        }
        public WorldTimerHandle Handle { get; }
        public Guid OwnerId { get; }
        public string Signal { get; }
        public WorldTimeBasis Basis { get; }
        public long DueMilliseconds { get; }
    }

    public sealed class WorldTimerScheduleReply
    {
        internal WorldTimerScheduleReply(WorldControlStatus status, WorldTimerHandle? handle = null)
        { Status = status; Handle = handle; }
        public WorldControlStatus Status { get; }
        public WorldTimerHandle? Handle { get; }
    }

    public sealed class WorldAdvanceResult
    {
        internal WorldAdvanceResult(WorldSessionView world, IReadOnlyList<WorldTimerSignal> signals,
            IReadOnlyList<ObjectClaimView> releasedClaims, bool endedThisAdvance)
        {
            World = world; Signals = signals; ReleasedClaims = releasedClaims;
            EndedThisAdvance = endedThisAdvance;
        }
        public WorldSessionView World { get; }
        public IReadOnlyList<WorldTimerSignal> Signals { get; }
        public IReadOnlyList<ObjectClaimView> ReleasedClaims { get; }
        public bool EndedThisAdvance { get; }
    }
}
