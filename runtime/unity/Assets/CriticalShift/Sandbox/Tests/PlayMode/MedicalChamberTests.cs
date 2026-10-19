using System;
using System.Collections;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Presentation;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    // Declared native coverage. These tests require the pinned editor; source/offline checks cannot execute them.
    public sealed class MedicalChamberTests
    {
        private GameObject root;
        private SandboxPrimitives shapes;
        private WorldSession world;
        private LocalWorldHost host;
        private LocalCommandPort operatorPort, patientPort;
        private LocalWorkerStateHost patientState;
        private WorkerBodyRig patientRig;
        private WorkerMedicalPlacement placement;
        private WorkerContaminationZones zones;
        private WorkerRecoveryRegistry recovery;
        private Transform bed, discharge;
        private Collider bedSupport, floor;
        private List<Exception> faults;
        private double clock;
        private int expectedFaults;
        private Guid focus;
        private static Guid Id(int n) => new Guid(n, 0, 0, new byte[8]);
        private Guid Station => Id(95);
        private Guid Patient => Id(3);
        private Guid Body => Id(650);
        private ObjectClaimView Claim => world.GetWorkerBodyClaim(Patient);

        [SetUp] public void SetUp()
        {
            root = new GameObject("Explicit native medical placement fixture"); root.transform.position = new Vector3(6500, 0, 6500);
            faults = new List<Exception>(); clock = 0; expectedFaults = 0; focus = Station;
        }

        private void Create(bool patientIsLocal = false, bool exposureAtBed = false)
        {
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); shapes = new SandboxPrimitives(shader);
            var access = new SpatialInteractionAccess(3.8f, (actor, target, body) => host != null && host.MayIgnoreForSight(actor, target, body));
            recovery = new WorkerRecoveryRegistry(); world = new WorldSession(new WorldSessionConfiguration(42, 20000, true), access, recovery);
            world.RegisterConnection(Id(2), Id(1)); world.RegisterConnection(Id(4), Patient);
            world.RegisterWorkerBody(Id(1), Id(651)); world.RegisterWorkerBody(Patient, Body);
            world.Reactor.Register(Id(90), new ReactorDefinition(Id(91))); world.Medical.Register(Station, new MedicalDefinition());
            if (exposureAtBed) world.RegisterWorkerContaminationSource(Id(720), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 60, 1000));
            operatorPort = new LocalCommandPort(world, Id(2)); patientPort = new LocalCommandPort(world, Id(4));
            host = root.AddComponent<LocalWorldHost>(); host.Initialize(world, patientIsLocal ? patientPort : operatorPort,
                patientIsLocal ? Patient : Id(1), () => clock, faults.Add);
            host.BindMedicalReadout(SandboxMedicalReadout.Controls, SandboxMedicalReadout.Result);
            host.BindFocus(() => focus, id => "Medical fixture target");
            floor = SandboxPrimitives.Box("Explicit static floor", root.transform, new Vector3(0, -0.15f, 0), new Vector3(20, 0.3f, 20), shapes.Floor).GetComponent<Collider>();
            var station = SandboxPrimitives.Empty("Medical station", root.transform, Vector3.zero);
            bedSupport = SandboxPrimitives.Box("Bed", station.transform, new Vector3(0, 0.55f, 0), new Vector3(1.5f, 0.3f, 2.5f), shapes.Steel).GetComponent<Collider>();
            bed = SandboxPrimitives.Empty("Bed pose", station.transform, new Vector3(0, 0.7f, 0)).transform;
            discharge = SandboxPrimitives.Empty("Discharge pose", station.transform, new Vector3(0, 0, -3)).transform;
            var console = SandboxPrimitives.Empty("Console point", station.transform, new Vector3(-1.6f, 1.1f, 0));
            SandboxPrimitives.Box("Console contact", station.transform, new Vector3(-1.6f, 0.7f, 0), new Vector3(0.35f, 1.4f, 0.35f), shapes.Dark);
            host.BindMedicalSlot(Station, bed, bedSupport, discharge, floor, console.transform); access.BindTarget(Station, station.transform, console.transform);
            BuildWorker(Id(1), Id(651), new Vector3(-1.6f, 0.1f, -1.6f), access, false);
            patientRig = BuildWorker(Patient, Body, new Vector3(0, 0.1f, -2.2f), access, true);
            if (exposureAtBed)
            {
                zones = root.AddComponent<WorkerContaminationZones>(); zones.Initialize(world, host.Pump, host.ReportExternalFailure);
                var area = SandboxPrimitives.Empty("Explicit bed exposure", root.transform, new Vector3(0, 1, 0));
                zones.BindArea(Id(720), area.transform, new Vector3(0.75f, 1, 1.25f), "Controlled bed exposure");
                zones.BindWorker(Patient, patientRig); zones.Seal();
            }
            recovery.Seal(); host.Activate(); patientState.Activate(); patientState.DiagnosticIncapacitate();
            if (zones != null) zones.Activate();
            Assert.That(world.GetWorker(Patient).Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            Physics.SyncTransforms();
        }

        private WorkerBodyRig BuildWorker(Guid actor, Guid body, Vector3 position, SpatialInteractionAccess access, bool isPatient)
        {
            var worker = SandboxPrimitives.Empty("Worker " + actor, root.transform, position);
            var controller = SandboxWorkerRigBuilder.AddController(worker);
            var eyes = SandboxPrimitives.Empty("Eyes", worker.transform, new Vector3(0, 1.55f, 0));
            var rig = SandboxWorkerRigBuilder.Build(world.Epoch, actor, controller, eyes.transform, shapes, false); rig.BindDragEntity(body);
            access.BindActor(actor, eyes.transform); access.BindTarget(body, worker.transform, rig.SuitGrip);
            var carry = SandboxPrimitives.Empty("Carry", eyes.transform, new Vector3(0, -0.15f, 1.75f)); host.BindCarryTarget(actor, carry.transform);
            var drag = SandboxPrimitives.Empty("Drag", worker.transform, new Vector3(0, 0.55f, 1.2f)); host.BindDragTarget(actor, drag.transform);
            host.BindWorkerBody(body, actor, rig.CopyBodySegments(), rig.PullBodyClaim, rig.ReleaseBodyClaim, () => rig.TotalPhysicalMass, rig.SetBodyHoist);
            var medical = new WorkerMedicalPlacement(); medical.Bind(rig);
            host.BindMedicalWorker(body, medical.Prepare, medical.Reconcile, medical.CancelStage, medical.Clear);
            var standing = new WorkerRecoveryPlacement(); standing.Bind(rig); recovery.Bind(world.Epoch, actor, standing);
            if (isPatient)
            {
                placement = medical; patientState = worker.AddComponent<LocalWorkerStateHost>();
                patientState.Initialize(world, actor, rig, standing, host.Pump, () => { }, host.ReportExternalFailure);
                patientState.BindHazard(Id(703), diagnostic: true);
            }
            return rig;
        }

        private void Load(bool operatorIsLocal = true)
        {
            if (operatorIsLocal)
            {
                host.Grab(Body); Assert.That(Claim.HolderId, Is.EqualTo(Id(1))); host.TransferFocused();
            }
            else
            {
                Assert.That(operatorPort.Grab(Body).HasNewCommit, Is.True);
                Assert.That(placement.Prepare(Claim, Station, bed, bedSupport, true), Is.True);
                Assert.That(operatorPort.OperateMedical(Station, MedicalAction.Insert, Body).HasNewCommit, Is.True);
                placement.Reconcile(Claim, Station);
            }
            Assert.That(Claim.SlotId, Is.EqualTo(Station)); Assert.That(patientRig.IsChambered, Is.True);
        }
        private GameObject Obstacle(Vector3 position, Vector3 size) => SandboxPrimitives.Box("Controlled clearance obstacle", root.transform,
            root.transform.InverseTransformPoint(position), size, shapes.Dark);
        private WaitForFixedUpdate Step() { clock += Time.fixedDeltaTime; return new WaitForFixedUpdate(); }

        [UnityTearDown] public IEnumerator TearDown()
        {
            if (zones != null) zones.Shutdown(); if (host != null) host.Shutdown(); if (patientState != null) patientState.Shutdown(); recovery?.Clear(); shapes?.Dispose();
            if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived(); Assert.That(faults.Count, Is.EqualTo(expectedFaults), string.Join("\n", faults));
        }

        [UnityTest] public IEnumerator MedicalInsertionUsesTheWholeJointConsistentRigAndExactCustody()
        {
            Create(); var before = Claim; var original = world.GetWorker(Patient); Load();
            Assert.That(Claim.Revision, Is.EqualTo(before.Revision + 2)); // grab + insertion
            Assert.That(Claim.LeaseGeneration, Is.EqualTo(1)); Assert.That(Claim.HolderId, Is.Null);
            Assert.That(world.GetWorker(Patient).LastCauseId, Is.EqualTo(original.LastCauseId));
            Assert.That(world.GetWorker(Patient).Suit, Is.EqualTo(original.Suit)); Assert.That(world.GetWorker(Patient).Contamination, Is.EqualTo(original.Contamination));
            foreach (var part in patientRig.CopyBodySegments())
            { Assert.That(part.isKinematic, Is.True); Assert.That(part.useGravity, Is.False); Assert.That(part.GetComponent<CapsuleCollider>().enabled, Is.False); }
            foreach (var joint in patientRig.GetComponentsInChildren<CharacterJoint>())
                Assert.That(Vector3.Distance(joint.transform.TransformPoint(joint.anchor), joint.connectedBody.transform.TransformPoint(joint.connectedAnchor)), Is.LessThan(0.01f));
            Assert.That(patientState.GetComponent<CharacterController>().enabled, Is.False);
            yield return null;
        }

        [UnityTest] public IEnumerator MedicalCompletionStaysChamberedUntilFreeDischargeAndSeparateRecovery()
        {
            Create(); Load(); host.StartFocused(); clock = 3; host.Pump();
            Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Ready)); Assert.That(world.GetWorker(Patient).Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(patientRig.IsChambered, Is.True); host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(Claim.SlotId, Is.Null); Assert.That(patientRig.IsChambered, Is.False); Assert.That(world.GetWorker(Patient).Pose, Is.EqualTo(WorkerPose.Down));
            foreach (var part in patientRig.CopyBodySegments()) { Assert.That(part.isKinematic, Is.False); Assert.That(part.linearVelocity, Is.EqualTo(Vector3.zero)); }
            for (int i = 0; i < 160 && world.GetWorker(Patient).Pose != WorkerPose.Upright; i++)
            { yield return Step(); if (i > 40 && i % 10 == 0) patientState.RequestRecovery(); }
            Assert.That(world.GetWorker(Patient).Pose, Is.EqualTo(WorkerPose.Upright), patientState.LastAction);
        }

        [UnityTest] public IEnumerator BlockedMedicalBedRejectsBeforeSequenceCustodyOrResources()
        {
            Create(); host.Grab(Body); var before = Claim; long sequence = operatorPort.LastTerminalSequence;
            Obstacle(bed.position + Vector3.up * 0.35f, new Vector3(1.5f, 0.6f, 2.5f)); Physics.SyncTransforms();
            host.OperateMedical(Station, MedicalAction.Insert, Body);
            Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); Assert.That(Claim.Revision, Is.EqualTo(before.Revision));
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1))); Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Empty));
            Assert.That(world.Reactor.PowerSummary.Spent, Is.Zero); yield return null;
        }

        [UnityTest] public IEnumerator BlockedMedicalDischargeKeepsTheCurrentPatientAndCanBeRetriedFresh()
        {
            Create(); Load(); var before = Claim; long sequence = operatorPort.LastTerminalSequence;
            var obstacle = Obstacle(discharge.position + Vector3.up * 0.35f, new Vector3(1.5f, 0.7f, 2.5f)); Physics.SyncTransforms();
            host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(Claim.Revision, Is.EqualTo(before.Revision)); Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); Assert.That(patientRig.IsChambered, Is.True);
            obstacle.GetComponent<Collider>().enabled = false; host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(Claim.SlotId, Is.Null); yield return null;
        }

        [UnityTest] public IEnumerator IgnoreRaycastPhysicalObstacleStillBlocksMedicalDischarge()
        {
            Create(); Load(); var obstacle = Obstacle(discharge.position + Vector3.up * 0.35f, new Vector3(1.5f, 0.7f, 2.5f)); obstacle.layer = 2;
            bool ignored = Physics.GetIgnoreLayerCollision(0, 2); Physics.IgnoreLayerCollision(0, 2, false);
            try { Physics.SyncTransforms(); long sequence = operatorPort.LastTerminalSequence; host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
                Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); Assert.That(Claim.SlotId, Is.EqualTo(Station)); }
            finally { Physics.IgnoreLayerCollision(0, 2, ignored); }
            yield return null;
        }

        [UnityTest] public IEnumerator SaturatedMedicalClearanceCannotConsumeTheNextCommand()
        {
            Create(); host.Grab(Body); long sequence = operatorPort.LastTerminalSequence;
            for (int i = 0; i < 40; i++) Obstacle(bed.position + Vector3.up * 0.3f, new Vector3(2, 1, 3));
            Physics.SyncTransforms(); host.OperateMedical(Station, MedicalAction.Insert, Body);
            Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Empty)); yield return null;
        }

        [UnityTest] public IEnumerator PausedMedicalWorkKeepsThePhysicalChamberAndFrozenCountdown()
        {
            Create(); Load(); host.OperateMedical(Station, MedicalAction.Start, Guid.Empty); host.ToggleClockPause(); long sequence = operatorPort.LastTerminalSequence;
            clock = 5; host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(world.View.ElapsedMilliseconds, Is.Zero); Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Treating));
            Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); Assert.That(patientRig.IsChambered, Is.True);
            host.ToggleClockPause(); clock = 8; host.Pump(); Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Ready)); yield return null;
        }

        [UnityTest] public IEnumerator ChamberedDiagnosticInjuryInterruptsWithoutForcingKinematicSegments()
        {
            Create(); Load(); host.OperateMedical(Station, MedicalAction.Start, Guid.Empty); patientState.DiagnosticKnockdown(); clock = 0.001; host.Pump();
            Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Interrupted)); Assert.That(patientRig.IsChambered, Is.True);
            Assert.That(world.Medical.Summary.UsedCartridges, Is.EqualTo(1)); Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(6)); yield return null;
        }

        [UnityTest] public IEnumerator LostOccupiedMedicalAnchorStopsOnceWithoutDischarging()
        {
            Create(); Load(); bed.localPosition += Vector3.right * 0.2f; expectedFaults = 1;
            host.OperateMedical(Station, MedicalAction.Start, Guid.Empty);
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(world.Reactor.PowerSummary.Spent, Is.Zero);
            foreach (var part in patientRig.CopyBodySegments()) Assert.That(part.isKinematic, Is.True); yield return null;
        }

        [UnityTest] public IEnumerator PatientDisconnectRetiresChamberWithoutNeedingAClearDischargePad()
        {
            Create(); Load(); host.OperateMedical(Station, MedicalAction.Start, Guid.Empty);
            Obstacle(discharge.position + Vector3.up * 0.3f, new Vector3(2, 1, 3)); world.Disconnect(world.Epoch, Id(4)); host.ReplayLast();
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Empty));
            Assert.That(world.GetObject(Body).IsRetired, Is.True); foreach (var part in patientRig.CopyBodySegments()) Assert.That(part.isKinematic, Is.True); yield return null;
        }

        [UnityTest] public IEnumerator HistoricalMedicalEjectionCannotTeleportTheReleasedBodyAgain()
        {
            Create(); Load(); host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            var parts = patientRig.CopyBodySegments();
            foreach (var part in parts) { part.position += Vector3.back * 0.3f; part.PublishTransform(); }
            Vector3 moved = parts[0].position; host.ReplayLast(); Assert.That(parts[0].position, Is.EqualTo(moved)); Assert.That(Claim.SlotId, Is.Null); yield return null;
        }

        [UnityTest] public IEnumerator ForeignRetiredClaimCannotFreezeTheCurrentChamberedPatient()
        {
            Create(); Load(); world.Disconnect(world.Epoch, Id(2)); var foreign = world.GetObject(Id(651));
            Assert.Throws<InvalidOperationException>(() => placement.Reconcile(foreign, Station)); Assert.That(patientRig.IsChambered, Is.True); yield return null;
        }

        [UnityTest] public IEnumerator WorkerRigRejectsASecondMedicalPlacementOwner()
        {
            Create(); Assert.Throws<InvalidOperationException>(() => new WorkerMedicalPlacement().Bind(patientRig));
            host.Shutdown(); Assert.Throws<InvalidOperationException>(() => placement.Bind(patientRig)); yield return null;
        }

        [UnityTest] public IEnumerator CorruptedHeldMedicalPoseCannotBeConcealedByDischargePreparation()
        {
            Create(); Load(); var part = patientRig.CopyBodySegments()[0]; part.position += Vector3.right * 0.1f; part.PublishTransform();
            long sequence = operatorPort.LastTerminalSequence;
            var error = Assert.Throws<InvalidOperationException>(() => placement.Prepare(Claim, Station, discharge, floor, false));
            Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); Assert.That(Claim.SlotId, Is.EqualTo(Station));
            expectedFaults = 1; host.ReportExternalFailure(error); yield return null;
        }

        [UnityTest] public IEnumerator DisplacedChamberAfterStagingCannotBeSilentlyRepairedAtExitCommit()
        {
            Create(); Load(); Assert.That(placement.Prepare(Claim, Station, discharge, floor, false), Is.True);
            bed.localPosition += Vector3.right * 0.1f; Assert.That(operatorPort.OperateMedical(Station, MedicalAction.Eject).HasNewCommit, Is.True);
            var error = Assert.Throws<InvalidOperationException>(() => placement.Reconcile(Claim, Station));
            Assert.That(patientRig.IsChambered, Is.True); expectedFaults = 1; host.ReportExternalFailure(error); yield return null;
        }

        [UnityTest] public IEnumerator OwnMedicalEgressWorksOnTheExactCompletionKeyPressWithoutFocus()
        {
            Create(patientIsLocal: true); Load(operatorIsLocal: false); Assert.That(operatorPort.OperateMedical(Station, MedicalAction.Start).HasNewCommit, Is.True);
            focus = Guid.Empty; clock = 3; host.TransferFocused();
            Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Empty)); Assert.That(Claim.SlotId, Is.Null);
            Assert.That(world.GetWorker(Patient).Awareness, Is.EqualTo(WorkerAwareness.Alert)); Assert.That(world.GetWorker(Patient).Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(patientPort.LastTerminalSequence, Is.EqualTo(1)); Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(6)); yield return null;
        }

        [UnityTest] public IEnumerator SameTimeExternalAidSettlesInterruptionBeforeOwnMedicalEgress()
        {
            Create(patientIsLocal: true); Load(operatorIsLocal: false); operatorPort.OperateMedical(Station, MedicalAction.Start);
            var patient = world.GetWorker(Patient); world.StabilizeWorker(world.Epoch, Patient, patient.Revision, 0);
            Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Treating)); focus = Guid.Empty; host.TransferFocused();
            Assert.That(Claim.SlotId, Is.Null); Assert.That(world.Medical.Summary.InterruptedCycles, Is.EqualTo(1)); Assert.That(world.View.ElapsedMilliseconds, Is.Zero); yield return null;
        }

        [UnityTest] public IEnumerator OwnMedicalEgressStillRequiresActualConsoleLineOfSight()
        {
            Create(patientIsLocal: true); Load(operatorIsLocal: false); operatorPort.OperateMedical(Station, MedicalAction.Start); clock = 3; host.Pump();
            Obstacle(root.transform.position + new Vector3(-0.8f, 1, 0.4f), new Vector3(0.3f, 1, 1)); Physics.SyncTransforms(); focus = Guid.Empty;
            var before = Claim; host.TransferFocused(); Assert.That(Claim.Revision, Is.EqualTo(before.Revision)); Assert.That(patientRig.IsChambered, Is.True);
            Assert.That(host.LastAction, Does.Contain("OutOfReach")); yield return null;
        }

        [UnityTest] public IEnumerator MedicalDeadlineFreezesTheBedBeforeAnyLateDischargeCommand()
        {
            Create(); Load(); host.OperateMedical(Station, MedicalAction.Start, Guid.Empty);
            var parts = patientRig.CopyBodySegments(); Vector3 bedPosition = parts[0].position;
            Obstacle(discharge.position + Vector3.up * 0.3f, new Vector3(2, 1, 3));
            long sequence = operatorPort.LastTerminalSequence; clock = 20; host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence));
            Assert.That(parts[0].position, Is.EqualTo(bedPosition));
            foreach (var part in parts) Assert.That(part.isKinematic, Is.True);
            Assert.That(host.BoundBodyCount, Is.Zero); yield return null;
        }

        [UnityTest] public IEnumerator SoleTreatedPatientCanEgressAfterTheOperatorDisconnects()
        {
            Create(patientIsLocal: true); Load(operatorIsLocal: false); operatorPort.OperateMedical(Station, MedicalAction.Start);
            world.Disconnect(world.Epoch, Id(2)); focus = Guid.Empty; clock = 3; host.TransferFocused();
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(Claim.SlotId, Is.Null);
            Assert.That(patientRig.IsChambered, Is.False); Assert.That(patientPort.LastTerminalSequence, Is.EqualTo(1));
            Assert.That(world.GetWorker(Patient).Pose, Is.EqualTo(WorkerPose.Down)); yield return null;
        }

        [UnityTest] public IEnumerator ActualChamberPelvisStillSamplesUnsafeExposureAndInterruptsOnce()
        {
            Create(exposureAtBed: true); Load(); host.OperateMedical(Station, MedicalAction.Start, Guid.Empty);
            var injury = world.GetWorker(Patient).LastCauseId; var before = Claim;
            zones.Sample(); zones.Sample();
            Assert.That(world.GetWorker(Patient).Contamination, Is.EqualTo(60)); Assert.That(world.GetWorker(Patient).LastCauseId, Is.EqualTo(injury));
            Assert.That(world.Medical.View.Phase, Is.EqualTo(MedicalPhase.Interrupted)); Assert.That(world.Medical.Summary.InterruptedCycles, Is.EqualTo(1));
            Assert.That(Claim.Revision, Is.EqualTo(before.Revision)); Assert.That(Claim.SlotId, Is.EqualTo(Station)); Assert.That(patientRig.IsChambered, Is.True);
            Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(6)); yield return null;
        }

        [UnityTest] public IEnumerator RejectedTreatingEjectionCancelsItsStageBeforeAFreshDischarge()
        {
            Create(); Load(); host.OperateMedical(Station, MedicalAction.Start, Guid.Empty);
            var before = Claim; long sequence = operatorPort.LastTerminalSequence;
            host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence + 1)); Assert.That(Claim.Revision, Is.EqualTo(before.Revision));
            Assert.That(patientRig.IsChambered, Is.True); Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(6));
            host.OperateMedical(Station, MedicalAction.Cancel, Guid.Empty); host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(Claim.SlotId, Is.Null); Assert.That(patientRig.IsChambered, Is.False); yield return null;
        }

        [UnityTest] public IEnumerator DischargeObstructionAfterStagingCannotPublishAnUnsafeDestination()
        {
            Create(); Load(); Assert.That(placement.Prepare(Claim, Station, discharge, floor, false), Is.True);
            var parts = patientRig.CopyBodySegments(); Vector3 original = parts[0].position;
            Obstacle(discharge.position + Vector3.up * 0.3f, new Vector3(2, 1, 3)); Physics.SyncTransforms();
            Assert.That(operatorPort.OperateMedical(Station, MedicalAction.Eject).HasNewCommit, Is.True);
            var error = Assert.Throws<InvalidOperationException>(() => placement.Reconcile(Claim, Station));
            Assert.That(parts[0].position, Is.EqualTo(original)); expectedFaults = 1; host.ReportExternalFailure(error); yield return null;
        }

        [UnityTest] public IEnumerator ExcludedFloorLayerCannotRemainACertifiedMedicalSupport()
        {
            Create(); Load(); var before = Claim; long sequence = operatorPort.LastTerminalSequence;
            floor.excludeLayers = 1 << patientRig.CopyBodySegments()[0].gameObject.layer; expectedFaults = 1;
            host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence));
            foreach (var part in patientRig.CopyBodySegments()) Assert.That(part.isKinematic, Is.True); yield return null;
        }

        [UnityTest] public IEnumerator PatientContactLayerOverrideStopsBeforeMedicalDischarge()
        {
            Create(); Load(); long sequence = operatorPort.LastTerminalSequence;
            foreach (var part in patientRig.CopyBodySegments()) part.GetComponent<CapsuleCollider>().excludeLayers = 1 << floor.gameObject.layer;
            expectedFaults = 1; host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); yield return null;
        }

        [UnityTest] public IEnumerator PatientBodyLayerOverrideStopsBeforeMedicalDischarge()
        {
            Create(); Load(); long sequence = operatorPort.LastTerminalSequence;
            foreach (var part in patientRig.CopyBodySegments()) part.excludeLayers = 1 << floor.gameObject.layer;
            expectedFaults = 1; host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); yield return null;
        }

        [UnityTest] public IEnumerator NativeArticulationCannotBecomeAStaticMedicalAnchor()
        {
            Create(); Load(); long sequence = operatorPort.LastTerminalSequence;
            discharge.gameObject.AddComponent<ArticulationBody>(); expectedFaults = 1;
            host.OperateMedical(Station, MedicalAction.Eject, Guid.Empty);
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(operatorPort.LastTerminalSequence, Is.EqualTo(sequence)); yield return null;
        }
    }
}
