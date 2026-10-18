using System;
using System.Collections;
using System.Collections.Generic;
using CriticalShift.FacilityPhysics;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class CombinedMapDoorTests
    {
        private GameObject root;
        private Guid epoch;
        private readonly List<CombinedMapDoorBindings> adapters = new List<CombinedMapDoorBindings>();
        private readonly List<Exception> failures = new List<Exception>();
        private readonly List<Mesh> ownedMeshes = new List<Mesh>();

        [SetUp] public void SetUp()
        {
            root = new GameObject("Combined map door regression fixture"); root.transform.position = Vector3.one * 1000;
            epoch = Guid.NewGuid(); adapters.Clear(); failures.Clear(); ownedMeshes.Clear();
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            foreach (var adapter in adapters) if (adapter != null) adapter.Shutdown();
            if (root != null) UnityEngine.Object.Destroy(root);
            foreach (var mesh in ownedMeshes) if (mesh != null) UnityEngine.Object.Destroy(mesh);
            yield return null; LogAssert.NoUnexpectedReceived();
            Assert.That(failures, Is.Empty, "Unexpected combined-map door binding failure.");
        }

        private Transform Child(string name, Transform owner)
        {
            var item = new GameObject(name).transform; item.SetParent(owner, false); return item;
        }
        private CombinedMapDoorBindings Adapter(Transform owner = null)
        {
            var adapter = (owner == null ? root : owner.gameObject).AddComponent<CombinedMapDoorBindings>();
            adapters.Add(adapter); return adapter;
        }
        private DoorCollisionBinding Door(string id, Vector3 plan, Vector2 outward, float width, float height,
            DoorCollisionState state = DoorCollisionState.Closed, long revision = 0, Transform owner = null, Guid? worldEpoch = null)
        {
            var anchor = Child("Explicit door anchor " + id, owner == null ? root.transform : owner);
            // A local test frame, not evidence of FBX conversion. Authored door local +X is its outward normal.
            anchor.localPosition = new Vector3(plan.x, plan.z, plan.y);
            anchor.localRotation = Quaternion.Euler(0, -Mathf.Atan2(outward.y, outward.x) * Mathf.Rad2Deg, 0);
            var blocker = Child("Explicit solid contact " + id, anchor).gameObject.AddComponent<BoxCollider>();
            blocker.transform.localPosition = Vector3.up * height * 0.5f; blocker.size = new Vector3(0.12f, height, width);
            float triggerHeight = Mathf.Min(height, 2.4f);
            var threshold = Child("Explicit threshold " + id, anchor).gameObject.AddComponent<BoxCollider>();
            threshold.transform.localPosition = Vector3.up * triggerHeight * 0.5f;
            threshold.size = new Vector3(0.6f, triggerHeight, width); threshold.isTrigger = true;
            return new DoorCollisionBinding(new DoorCollisionProjection(worldEpoch ?? epoch, id, revision, state), anchor, blocker, threshold);
        }
        private DoorCollisionBinding Turbine(long revision = 0) => Door("TURBINE_D02", new Vector3(0, 21.53f, 0), Vector2.up, 1.44f, 2.38f, revision: revision);
        private DoorCollisionBinding Dock(long revision = 0) => Door("DOCK_P2", new Vector3(27.95f, -40.39f, 0), Vector2.right, 4.6f, 3.5f, revision: revision);
        private DoorCollisionProjection Projection(DoorCollisionBinding binding, long revision, DoorCollisionState state, Guid? worldEpoch = null) =>
            new DoorCollisionProjection(worldEpoch ?? epoch, binding.InitialProjection.DoorId, revision, state);

        private void AssertCrossing(DoorCollisionBinding binding, bool blocked)
        {
            Physics.SyncTransforms(); Vector3 normal = binding.Anchor.right;
            Vector3 start = binding.Anchor.position - normal * 1.5f;
            bool hit = Physics.CapsuleCast(start + Vector3.up * 0.3f, start + Vector3.up * 1.5f, 0.3f,
                normal, out var contact, 3, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            Assert.That(hit, Is.EqualTo(blocked), binding.InitialProjection.DoorId);
            if (blocked) Assert.That(contact.collider, Is.EqualTo(binding.Blocker));
            Assert.That(binding.Threshold.enabled, Is.True); Assert.That(binding.Threshold.isTrigger, Is.True);
        }

        [Test] public void RealDoorRowsApplySuppliedCollisionStatesWithoutOpeningSealedDock()
        {
            // Dimensions and planes from combined/validation/doors.json, including its diagonal and narrow openings.
            var reactor = Door("REACTOR_SE", new Vector3(11, -29.7f, 0), new Vector2(0.7071f, -0.7071f), 5, 5);
            var turbine = Turbine(); var dock = Dock();
            var condenser = Door("CONDENSER_W_ESCAPE", new Vector3(-0.34f, 12.1f, -6), Vector2.left, 1, 2.28f);
            var escape = Door("ESCAPE_HOUSE_DOOR", new Vector3(-5.6f, 13.1f, 0), Vector2.up, 1.56f, 2.18f);
            var rows = new[] { reactor, turbine, dock, condenser, escape }; var adapter = Adapter();
            adapter.Initialize(epoch, rows, failures.Add); Assert.That(adapter.BoundDoorCount, Is.EqualTo(5));
            foreach (var binding in rows) AssertCrossing(binding, true);
            var emergency = new[] { reactor, turbine, condenser, escape };
            var projections = new DoorCollisionProjection[emergency.Length];
            for (int i = 0; i < emergency.Length; i++) projections[i] = Projection(emergency[i], 1, DoorCollisionState.Open);
            Assert.That(adapter.ApplyBatch(projections), Is.EqualTo(DoorCollisionApplyStatus.Applied));
            foreach (var binding in emergency) AssertCrossing(binding, false);
            AssertCrossing(dock, true);
            Assert.That(adapter.Apply(Projection(turbine, 2, DoorCollisionState.Locked)), Is.EqualTo(DoorCollisionApplyStatus.Applied));
            AssertCrossing(turbine, true);
            Assert.That(adapter.Apply(Projection(turbine, 3, DoorCollisionState.Closed)), Is.EqualTo(DoorCollisionApplyStatus.Applied));
            AssertCrossing(turbine, true); Assert.That(adapter.FaultLatched, Is.False);
        }

        [Test] public void ProjectionBatchesFenceEpochRevisionAndConflictingReplaysAtomically()
        {
            var turbine = Turbine(3); var dock = Dock(3); var adapter = Adapter();
            adapter.Initialize(epoch, new[] { turbine, dock }, failures.Add);
            Assert.That(adapter.Apply(turbine.InitialProjection), Is.EqualTo(DoorCollisionApplyStatus.NoChange));
            Assert.That(adapter.Apply(Projection(turbine, 100, DoorCollisionState.Open, Guid.NewGuid())), Is.EqualTo(DoorCollisionApplyStatus.WrongEpoch));
            Assert.That(adapter.Apply(Projection(turbine, 2, DoorCollisionState.Open)), Is.EqualTo(DoorCollisionApplyStatus.StaleRevision));
            Assert.That(adapter.Apply(Projection(turbine, 3, DoorCollisionState.Open)), Is.EqualTo(DoorCollisionApplyStatus.RevisionConflict));
            Assert.That(adapter.Apply(new DoorCollisionProjection(epoch, "UNKNOWN_DOOR", 4, DoorCollisionState.Open)), Is.EqualTo(DoorCollisionApplyStatus.UnknownDoor));
            var open = Projection(turbine, 4, DoorCollisionState.Open);
            Assert.That(adapter.ApplyBatch(new[] { open, Projection(dock, 4, DoorCollisionState.Open, Guid.NewGuid()) }), Is.EqualTo(DoorCollisionApplyStatus.WrongEpoch));
            Assert.That(adapter.ApplyBatch(new[] { open, Projection(dock, 2, DoorCollisionState.Open) }), Is.EqualTo(DoorCollisionApplyStatus.StaleRevision));
            Assert.Throws<ArgumentException>(() => adapter.ApplyBatch(new[] { open, open }));
            Assert.That(turbine.Blocker.enabled, Is.True); Assert.That(dock.Blocker.enabled, Is.True);
            var accepted = new[] { open, Projection(dock, 4, DoorCollisionState.Closed) };
            Assert.That(adapter.ApplyBatch(accepted), Is.EqualTo(DoorCollisionApplyStatus.Applied));
            Assert.That(adapter.ApplyBatch(accepted), Is.EqualTo(DoorCollisionApplyStatus.NoChange));
            Assert.That(adapter.ApplyBatch(new[] { Projection(turbine, 5, DoorCollisionState.Closed), Projection(dock, 4, DoorCollisionState.Open) }),
                Is.EqualTo(DoorCollisionApplyStatus.RevisionConflict));
            Assert.That(turbine.Blocker.enabled, Is.False); Assert.That(dock.Blocker.enabled, Is.True);
            Assert.That(adapter.Apply(Projection(turbine, 4, DoorCollisionState.Open)), Is.EqualTo(DoorCollisionApplyStatus.NoChange));
            Assert.That(adapter.FaultLatched, Is.False);
        }

        [Test] public void RejectedDoorSetupLeavesContactsUntouchedAndAllowsCorrectedBinding()
        {
            var turbine = Turbine(); var dock = Dock(); var adapter = Adapter();
            var open = new DoorCollisionBinding(Projection(turbine, 0, DoorCollisionState.Open), turbine.Anchor, turbine.Blocker, turbine.Threshold);
            turbine.Blocker.enabled = true; turbine.Threshold.enabled = false; dock.Threshold.isTrigger = false;
            Assert.Throws<InvalidOperationException>(() => adapter.Initialize(epoch, new[] { open, dock }, failures.Add));
            Assert.That(adapter.IsBound, Is.False); Assert.That(adapter.BoundDoorCount, Is.Zero);
            Assert.That(turbine.Blocker.enabled, Is.True); Assert.That(turbine.Threshold.enabled, Is.False);
            dock.Threshold.isTrigger = true;
            var duplicateId = new DoorCollisionBinding(open.InitialProjection, dock.Anchor, dock.Blocker, dock.Threshold);
            Assert.Throws<ArgumentException>(() => adapter.Initialize(epoch, new[] { open, duplicateId }, failures.Add));
            var sharedContact = new DoorCollisionBinding(dock.InitialProjection, dock.Anchor, turbine.Blocker, dock.Threshold);
            Assert.Throws<ArgumentException>(() => adapter.Initialize(epoch, new[] { open, sharedContact }, failures.Add));
            var foreignAnchor = new DoorCollisionBinding(dock.InitialProjection, root.transform, dock.Blocker, dock.Threshold);
            Assert.Throws<InvalidOperationException>(() => adapter.Initialize(epoch, new[] { open, foreignAnchor }, failures.Add));
            var wrongEpoch = new DoorCollisionBinding(Projection(dock, 0, DoorCollisionState.Closed, Guid.NewGuid()), dock.Anchor, dock.Blocker, dock.Threshold);
            Assert.Throws<ArgumentException>(() => adapter.Initialize(epoch, new[] { open, wrongEpoch }, failures.Add));
            Assert.Throws<ArgumentException>(() => adapter.Initialize(epoch, new DoorCollisionBinding[129], failures.Add));
            var dynamicAnchor = Child("Unexpected dynamic anchor", root.transform);
            var body = dynamicAnchor.gameObject.AddComponent<Rigidbody>(); body.useGravity = false; body.isKinematic = true;
            var moving = new DoorCollisionBinding(dock.InitialProjection, dynamicAnchor, dock.Blocker, dock.Threshold);
            Assert.Throws<InvalidOperationException>(() => adapter.Initialize(epoch, new[] { open, moving }, failures.Add));
            Assert.That(turbine.Blocker.enabled, Is.True); Assert.That(turbine.Threshold.enabled, Is.False);
            adapter.Initialize(epoch, new[] { open, dock }, failures.Add);
            Assert.That(adapter.IsBound, Is.True); Assert.That(turbine.Blocker.enabled, Is.False);
            Assert.That(turbine.Threshold.enabled, Is.True); Assert.That(dock.Blocker.enabled, Is.True);
        }

        [UnityTest] public IEnumerator LostDoorContactReportsOnceAndCannotAffectTheNextWorld()
        {
            var turbine = Turbine(); var dock = Dock(); var adapter = Adapter();
            adapter.Initialize(epoch, new[] { turbine, dock }, failures.Add);
            UnityEngine.Object.Destroy(turbine.Blocker.gameObject); yield return null;
            Assert.That(adapter.CanClose("TURBINE_D02"), Is.False);
            adapter.Sample(); Assert.That(failures.Count, Is.EqualTo(1));
            Assert.That(failures[0].Message, Does.Contain("TURBINE_D02")); failures.Clear();
            Assert.That(adapter.FaultLatched, Is.True); Assert.That(adapter.enabled, Is.False);
            Assert.That(adapter.BoundDoorCount, Is.Zero); Assert.That(adapter.Epoch, Is.EqualTo(Guid.Empty));
            Assert.That(turbine.Threshold.enabled, Is.False); Assert.That(dock.Blocker.enabled, Is.False); Assert.That(dock.Threshold.enabled, Is.False);
            adapter.Sample(); adapter.Shutdown(); adapter.Shutdown();
            Assert.That(adapter.Apply(Projection(dock, 10, DoorCollisionState.Open)), Is.EqualTo(DoorCollisionApplyStatus.Unavailable));
            var nextOwner = Child("Fresh world contacts", root.transform); var next = Adapter(nextOwner); Guid nextEpoch = Guid.NewGuid();
            var fresh = Door("DOCK_P2", new Vector3(27.95f, -40.39f, 0), Vector2.right, 4.6f, 3.5f, owner: nextOwner, worldEpoch: nextEpoch);
            next.Initialize(nextEpoch, new[] { fresh }, failures.Add);
            Assert.That(next.Apply(Projection(dock, 10, DoorCollisionState.Open)), Is.EqualTo(DoorCollisionApplyStatus.WrongEpoch));
            Assert.That(fresh.Blocker.enabled, Is.True); Assert.That(next.FaultLatched, Is.False);
            yield return new WaitForFixedUpdate(); yield return null;
            Assert.That(failures, Is.Empty); next.Shutdown(); next.Shutdown();
            Assert.That(next.BoundDoorCount, Is.Zero); Assert.That(fresh.Blocker.enabled, Is.False); Assert.That(fresh.Threshold.enabled, Is.False);
        }

        [Test] public void DoorClosurePreflightRejectsLiveOccupantsAndSaturationWithoutChangingContacts()
        {
            var turbine = Turbine();
            var open = new DoorCollisionBinding(Projection(turbine, 0, DoorCollisionState.Open), turbine.Anchor, turbine.Blocker, turbine.Threshold);
            var adapter = Adapter(); adapter.Initialize(epoch, new[] { open }, failures.Add);
            var surround = Child("Static door surround", root.transform).gameObject.AddComponent<BoxCollider>();
            surround.transform.position = turbine.Anchor.position + Vector3.up + turbine.Anchor.forward * 0.72f;
            surround.size = Vector3.one * 0.1f;
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.True);
            var walker = Child("Occupying walking capsule", root.transform).gameObject.AddComponent<CharacterController>();
            walker.enabled = false;
            walker.transform.position = turbine.Anchor.position + Vector3.up * 0.05f;
            walker.center = Vector3.up * 0.9f; walker.height = 1.8f; walker.radius = 0.3f;
            // Exercise the controller's own movement API, as LocalWorkerMotor does during its movement update,
            // instead of relying only on a transform sync immediately after controller creation and configuration.
            walker.enabled = true; walker.Move(Vector3.zero); Physics.SyncTransforms();
            Bounds doorway = turbine.Threshold.bounds;
            var observations = new Collider[64];
            int observed = Physics.OverlapBoxNonAlloc(doorway.center, doorway.extents, observations, Quaternion.identity,
                Physics.AllLayers, QueryTriggerInteraction.Ignore);
            bool observedWalker = false;
            var observationDetails = new System.Text.StringBuilder();
            for (int i = 0; i < observed; i++)
            {
                var contact = observations[i]; observedWalker |= contact == walker;
                observationDetails.Append(contact == null ? "null" : contact.name + ":" + contact.GetType().Name +
                    " enabled=" + contact.enabled + " trigger=" + contact.isTrigger).Append("; ");
            }
            string occupancyDetails = "Controller in native query=" + observedWalker + ", enabled=" + walker.enabled +
                ", trigger=" + walker.isTrigger + ", controller bounds=" + walker.bounds + ", threshold bounds=" + doorway +
                ", native contacts=" + observationDetails;
            Assert.That(walker.bounds.Intersects(doorway), Is.True, occupancyDetails);
            Assert.That(adapter.CanClose("TURBINE_D02"), Is.False, occupancyDetails);
            walker.enabled = false;
            var portable = Child("Occupying portable body", root.transform).gameObject.AddComponent<BoxCollider>();
            portable.transform.position = turbine.Anchor.position + Vector3.up; portable.size = Vector3.one * 0.4f;
            portable.gameObject.layer = 2; // Ignore Raycast is still a physical occupant, so closure observes all layers.
            var body = portable.gameObject.AddComponent<Rigidbody>(); body.useGravity = false;
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.False);
            body.isKinematic = true;
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.False);
            portable.enabled = false;
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.True);
            portable.isTrigger = true; portable.enabled = true;
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.True);
            surround.enabled = false;
            var crowded = new Collider[64];
            for (int i = 0; i < crowded.Length; i++)
            {
                var contact = Child("Closure query capacity contact " + i, root.transform).gameObject.AddComponent<BoxCollider>();
                contact.transform.position = turbine.Threshold.bounds.center; contact.size = Vector3.one * 0.01f;
                crowded[i] = contact;
            }
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.False, "A full query cannot certify an empty doorway.");
            foreach (var contact in crowded) contact.enabled = false;
            Physics.SyncTransforms(); Assert.That(adapter.CanClose("TURBINE_D02"), Is.True);
            Assert.That(adapter.CanClose("UNKNOWN_DOOR"), Is.False);
            Assert.That(adapter.Apply(open.InitialProjection), Is.EqualTo(DoorCollisionApplyStatus.NoChange));
            Assert.That(turbine.Blocker.enabled, Is.False); Assert.That(turbine.Threshold.enabled, Is.True);
            Assert.That(adapter.Epoch, Is.EqualTo(epoch)); Assert.That(adapter.BoundDoorCount, Is.EqualTo(1));
            Assert.That(body.isKinematic, Is.True); Assert.That(body.linearVelocity, Is.EqualTo(Vector3.zero));
            Assert.That(adapter.FaultLatched, Is.False);
        }

        [Test] public void WholeModelMotionPreservesDoorBindingsButChildPoseDriftStopsThem()
        {
            var turbine = Turbine(); var adapter = Adapter(); adapter.Initialize(epoch, new[] { turbine }, failures.Add);
            root.transform.position += new Vector3(101.25f, -3.5f, 77.75f); root.transform.rotation = Quaternion.Euler(0, 33, 0);
            Physics.SyncTransforms(); adapter.Sample();
            Assert.That(adapter.IsBound, Is.True); Assert.That(adapter.FaultLatched, Is.False);
            Assert.That(adapter.Apply(turbine.InitialProjection), Is.EqualTo(DoorCollisionApplyStatus.NoChange));
            Vector3 displaced = turbine.Blocker.transform.localPosition + Vector3.right * 0.25f;
            turbine.Blocker.transform.localPosition = displaced; adapter.Sample();
            Assert.That(failures.Count, Is.EqualTo(1)); Assert.That(failures[0].Message, Does.Contain("TURBINE_D02")); failures.Clear();
            Assert.That(adapter.FaultLatched, Is.True); Assert.That(adapter.BoundDoorCount, Is.Zero);
            Assert.That(turbine.Blocker.enabled, Is.False); Assert.That(turbine.Threshold.enabled, Is.False);
            Assert.That(turbine.Blocker.transform.localPosition, Is.EqualTo(displaced), "A failure must not repair scene geometry.");
            adapter.Sample(); Assert.That(failures, Is.Empty);
        }

        [Test] public void DoorShapeScaleAndAnchorDriftRejectFurtherProjectionDelivery()
        {
            var turbine = Turbine(); var adapter = Adapter(); var singular = Child("Singular empty anchor", root.transform);
            singular.localScale = new Vector3(1, 0, 1);
            var invalid = new DoorCollisionBinding(turbine.InitialProjection, singular, turbine.Blocker, turbine.Threshold);
            Assert.Throws<InvalidOperationException>(() => adapter.Initialize(epoch, new[] { invalid }, failures.Add));
            Assert.That(adapter.BoundDoorCount, Is.Zero); Assert.That(turbine.Blocker.enabled, Is.True); Assert.That(turbine.Threshold.enabled, Is.True);
            adapter.Initialize(epoch, new[] { turbine }, failures.Add);
            CheckDrift(binding => binding.Anchor.localPosition += Vector3.right * 0.25f, "Anchor drift");
            CheckDrift(binding => binding.Blocker.transform.localScale *= 0.5f, "Blocker scale drift");
            CheckDrift(binding => binding.Threshold.transform.localScale *= 0.5f, "Threshold scale drift");
            CheckDrift(binding => ((BoxCollider)binding.Blocker).center += Vector3.up * 0.2f, "Blocker shape drift");
            CheckDrift(binding => ((BoxCollider)binding.Threshold).size *= 0.5f, "Threshold shape drift");
            CheckDrift(binding =>
            {
                var contact = (MeshCollider)binding.Blocker;
                var replacement = UnityEngine.Object.Instantiate(contact.sharedMesh); ownedMeshes.Add(replacement);
                contact.sharedMesh = replacement;
            }, "Mesh identity drift", meshBlocker: true);

            void CheckDrift(Action<DoorCollisionBinding> change, string label, bool meshBlocker = false)
            {
                var owner = Child(label, root.transform); owner.localPosition = Vector3.right * (adapters.Count * 4);
                var row = Door("TURBINE_D02", new Vector3(0, 21.53f, 0), Vector2.up, 1.44f, 2.38f, DoorCollisionState.Open, owner: owner);
                if (meshBlocker)
                {
                    var source = GameObject.CreatePrimitive(PrimitiveType.Cube); source.transform.SetParent(root.transform, false); source.SetActive(false);
                    row.Blocker.enabled = false;
                    var contact = row.Blocker.gameObject.AddComponent<MeshCollider>(); contact.sharedMesh = source.GetComponent<MeshFilter>().sharedMesh;
                    row = new DoorCollisionBinding(row.InitialProjection, row.Anchor, contact, row.Threshold);
                }
                var instance = Adapter(owner); instance.Initialize(epoch, new[] { row }, failures.Add); change(row);
                Assert.That(instance.Apply(Projection(row, 1, DoorCollisionState.Closed)), Is.EqualTo(DoorCollisionApplyStatus.Unavailable), label);
                Assert.That(failures.Count, Is.EqualTo(1), label); Assert.That(failures[0].Message, Does.Contain("TURBINE_D02")); failures.Clear();
                Assert.That(instance.FaultLatched, Is.True); Assert.That(instance.BoundDoorCount, Is.Zero);
                Assert.That(row.Blocker.enabled, Is.False); Assert.That(row.Threshold.enabled, Is.False);
            }
        }
    }
}
