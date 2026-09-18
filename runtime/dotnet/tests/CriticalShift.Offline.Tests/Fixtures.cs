using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    internal sealed class TestAccess : IInteractionAccessPolicy
    {
        internal AccessDecision Decision { get; set; } = AccessDecision.Allowed;
        internal int Calls { get; private set; }
        internal Guid LastActor { get; private set; }
        internal Action? Callback { get; set; }
        public AccessDecision Evaluate(Guid actorId, Guid entityId, InteractionKind kind)
        {
            Calls++;
            LastActor = actorId;
            Callback?.Invoke();
            return Decision;
        }
    }

    internal sealed class Fixture
    {
        internal static Guid Id(int n) => new Guid(n, 0, 0, new byte[8]);
        internal readonly Guid Epoch;
        internal readonly Guid A = Id(10), B = Id(11), C1 = Id(20), C2 = Id(21);
        internal readonly Guid Box = Id(30), Other = Id(31);
        internal readonly TestAccess Access = new TestAccess();
        internal readonly InteractionWorld World;

        internal Fixture(int receipts = 256, int epoch = 1)
        {
            Epoch = Id(epoch);
            World = new InteractionWorld(Epoch, Access, receiptCapacity: receipts);
            World.RegisterConnection(C1, A);
            World.RegisterConnection(C2, B);
            World.RegisterObject(Box);
            World.RegisterObject(Other);
            World.Start();
        }
        internal InteractionCommand Grab(long seq, long revision = 0, Guid? box = null) =>
            new InteractionCommand(Epoch, seq, InteractionKind.Grab, box ?? Box, revision);
        internal InteractionCommand Release(long seq, long generation = 1) =>
            new InteractionCommand(Epoch, seq, InteractionKind.Release, Box, leaseGeneration: generation);
        internal InteractionCommand Renew(long seq, long generation = 1) =>
            new InteractionCommand(Epoch, seq, InteractionKind.Renew, Box, leaseGeneration: generation);
        internal void Holder(Guid? actor) => Assert.That(World.GetObject(Box)!.HolderId, Is.EqualTo(actor));
    }
}
