using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Domain;
using CriticalShift.Features.Session.Domain;
using CriticalShift.Features.Workers.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ModelAndBoundaryTests
    {
        public static IEnumerable<int> Seeds => Enumerable.Range(1, 100);

        [TestCaseSource(nameof(Seeds)), Category("HOLD-MODEL")]
        public void ModelSequencesPreserveExclusiveCustody(int seed)
        {
            // Independent array model: no production snapshots or mutation helpers implement the oracle.
            var store = new ExclusiveClaimStore(8, 3000);
            var holders = Enumerable.Repeat(-1, 8).ToArray();
            var revisions = new long[8]; var generations = new long[8];
            var deadlines = new long[8]; var retired = new bool[8];
            for (int i = 0; i < 8; i++) store.Register(Fixture.Id(100 + i));
            uint random = (uint)seed; long now = 0;
            for (int step = 0; step < 200; step++)
            {
                random ^= random << 13; random ^= random >> 17; random ^= random << 5;
                int entity = (int)(random % 8), actor = (int)((random >> 4) % 4);
                int op = (int)((random >> 8) % (step >= 170 ? 6 : 5));
                var id = Fixture.Id(100 + entity); var who = Fixture.Id(10 + actor);
                long token = (random & 0x4000) == 0 ? generations[entity] : generations[entity] + 7;
                long expectedRevision = (random & 0x8000) == 0 ? revisions[entity] : revisions[entity] + 1;
                ClaimError expected = ClaimError.None;
                ClaimResult? result = null;
                switch (op)
                {
                    case 0:
                        expected = retired[entity] ? ClaimError.EntityRetired :
                            revisions[entity] != expectedRevision ? ClaimError.RevisionConflict :
                            holders[entity] != -1 ? ClaimError.AlreadyClaimed :
                            holders.Contains(actor) ? ClaimError.ActorAlreadyHolding : ClaimError.None;
                        result = store.TryGrab(id, who, expectedRevision);
                        if (expected == ClaimError.None)
                        { holders[entity] = actor; revisions[entity]++; generations[entity]++; deadlines[entity] = now + 3000; }
                        break;
                    case 1:
                    case 2:
                        expected = retired[entity] ? ClaimError.EntityRetired :
                            holders[entity] == -1 || token <= 0 || token != generations[entity] ? ClaimError.StaleLease :
                            holders[entity] != actor ? ClaimError.NotHolder : ClaimError.None;
                        result = op == 1 ? store.TryRelease(id, who, token) : store.TryRenew(id, who, token);
                        if (expected == ClaimError.None)
                        {
                            if (op == 1) { holders[entity] = -1; deadlines[entity] = 0; revisions[entity]++; }
                            else if (deadlines[entity] != now + 3000) { deadlines[entity] = now + 3000; revisions[entity]++; }
                        }
                        break;
                    case 3:
                        now += (random >> 16) % 4001;
                        for (int i = 0; i < 8; i++)
                            if (holders[i] != -1 && deadlines[i] <= now)
                            { holders[i] = -1; deadlines[i] = 0; revisions[i]++; }
                        store.AdvanceTo(now);
                        break;
                    case 4:
                        for (int i = 0; i < 8; i++)
                            if (holders[i] == actor) { holders[i] = -1; deadlines[i] = 0; revisions[i]++; }
                        store.ReleaseActor(who);
                        break;
                    case 5:
                        expected = retired[entity] ? ClaimError.EntityRetired : ClaimError.None;
                        result = store.Retire(id);
                        if (expected == ClaimError.None)
                        { retired[entity] = true; holders[entity] = -1; deadlines[entity] = 0; revisions[entity]++; }
                        break;
                }
                string trace = $"seed={seed}, step={step}, operation={op}, entity={entity}, actor={actor}";
                if (result != null) Assert.That(result.Error, Is.EqualTo(expected), trace);
                var observedHolders = new HashSet<Guid>();
                for (int i = 0; i < 8; i++)
                {
                    var view = store.Get(Fixture.Id(100 + i))!;
                    Guid? holder = holders[i] == -1 ? (Guid?)null : Fixture.Id(10 + holders[i]);
                    Assert.That(view.HolderId, Is.EqualTo(holder), trace);
                    Assert.That(view.Revision, Is.EqualTo(revisions[i]), trace);
                    Assert.That(view.LeaseGeneration, Is.EqualTo(generations[i]), trace);
                    Assert.That(view.ExpiresAtMilliseconds, Is.EqualTo(deadlines[i]), trace);
                    Assert.That(view.IsRetired, Is.EqualTo(retired[i]), trace);
                    if (view.HolderId.HasValue) Assert.That(observedHolders.Add(view.HolderId.Value), Is.True, trace);
                }
                Assert.That(store.ActiveClaimCount, Is.EqualTo(observedHolders.Count), trace);
                Assert.That(store.RegisteredCount, Is.EqualTo(8), trace);
            }
            store.Stop(); Assert.That(store.ActiveClaimCount, Is.Zero); Assert.That(store.RegisteredCount, Is.Zero);
        }

        [Test, Category("CMD-03")]
        public void TenThousandRejectionsKeepReceiptStorageBounded()
        {
            var f = new Fixture(receipts: 7);
            for (int i = 1; i <= 10000; i++)
            {
                var reply = f.World.Execute(f.C1, f.Grab(i, box: Fixture.Id(999)));
                Assert.That(reply.Status, Is.EqualTo(InteractionStatus.UnknownEntity));
                Assert.That(reply.IsTerminal, Is.True);
                Assert.That(f.World.RetainedReceiptCount(f.C1), Is.LessThanOrEqualTo(7));
            }
            Assert.That(f.World.LastSequence(f.C1), Is.EqualTo(10000));
            Assert.That(f.World.Execute(f.C1, f.Grab(1, box: Fixture.Id(999))).Status, Is.EqualTo(InteractionStatus.TooOld));
            Assert.That(f.World.Execute(f.C1, f.Grab(10001)).Accepted, Is.True);
        }

        [Test, Category("ARCH-01")]
        public void CompiledAssembliesStayWithinReferenceAllowlist()
        {
            var domain = typeof(ExclusiveClaimStore).Assembly;
            var session = typeof(SessionTimeline).Assembly;
            var workers = typeof(WorkerState).Assembly;
            var application = typeof(InteractionWorld).Assembly;
            Assert.That(domain.GetReferencedAssemblies().Select(x => x.Name), Is.SubsetOf(new[] { "netstandard" }));
            Assert.That(session.GetReferencedAssemblies().Select(x => x.Name), Is.SubsetOf(new[] { "netstandard" }));
            Assert.That(workers.GetReferencedAssemblies().Select(x => x.Name), Is.SubsetOf(new[] { "netstandard" }));
            Assert.That(application.GetReferencedAssemblies().Select(x => x.Name),
                Is.SubsetOf(new[] { "netstandard", "CriticalShift.Features.Interaction.Domain", "CriticalShift.Features.Session.Domain", "CriticalShift.Features.Workers.Domain" }));
        }

        private static bool ContainsDomain(Type type) =>
            type.Assembly == typeof(ExclusiveClaimStore).Assembly || type.Assembly == typeof(SessionTimeline).Assembly || type.Assembly == typeof(WorkerState).Assembly ||
            (type.HasElementType && ContainsDomain(type.GetElementType()!)) ||
            (type.IsGenericType && type.GetGenericArguments().Any(ContainsDomain));

        [Test, Category("ARCH-04")]
        public void ApplicationPublicApiDoesNotExposeDomainOwners()
        {
            foreach (var type in typeof(InteractionWorld).Assembly.GetExportedTypes())
            {
                foreach (var method in type.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
                {
                    Assert.That(ContainsDomain(method.ReturnType), Is.False, method.Name);
                    foreach (var parameter in method.GetParameters())
                        Assert.That(ContainsDomain(parameter.ParameterType), Is.False, method.Name);
                }
                foreach (var constructor in type.GetConstructors())
                    foreach (var parameter in constructor.GetParameters())
                        Assert.That(ContainsDomain(parameter.ParameterType), Is.False, type.Name);
            }
        }

        [Test, Category("ARCH-04")]
        public void RuntimeHasNoAuthoredMutableStaticFields()
        {
            foreach (var assembly in new[] { typeof(InteractionWorld).Assembly, typeof(ExclusiveClaimStore).Assembly, typeof(SessionTimeline).Assembly, typeof(WorkerState).Assembly })
                foreach (var type in assembly.GetTypes())
                {
                    if (type.IsDefined(typeof(CompilerGeneratedAttribute), false)) continue;
                    foreach (var field in type.GetFields(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic))
                        Assert.That(field.IsLiteral || field.IsInitOnly, Is.True, type.FullName + "." + field.Name);
                }
        }

        [Test]
        public void SnapshotPublicPropertiesCannotBeSet()
        {
            foreach (var type in new[] { typeof(ClaimSnapshot), typeof(ObjectClaimView), typeof(InteractionReply), typeof(InteractionCommand),
                typeof(WorldSessionConfiguration), typeof(WorldSessionView), typeof(WorldTimerHandle), typeof(WorldTimerSignal),
                typeof(WorldTimerScheduleReply), typeof(WorldAdvanceResult), typeof(TimerEntry), typeof(WorkerSnapshot), typeof(WorkerView), typeof(WorkerReply),
                typeof(SessionTraceRecord), typeof(SessionTraceView) })
                foreach (var property in type.GetProperties()) Assert.That(property.SetMethod, Is.Null, type.Name + "." + property.Name);
        }
    }
}
