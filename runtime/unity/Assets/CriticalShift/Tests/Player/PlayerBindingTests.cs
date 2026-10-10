using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Bootstrap.Player;
using CriticalShift.Features.Player.Unity;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Tests.Player
{
    // These are native PlayMode assertions. API compilation does not execute them.
    public sealed class PlayerBindingTests
    {
        private LocalShiftHost _host;
        private FirstPersonWorker _worker;
        private InteractionTarget[] _targets;
        [SetUp] public void SetUp()
        {
            _host = PlayerRoomFactory.Create(); _worker = _host.GetComponentInChildren<FirstPersonWorker>();
            _targets = _host.GetComponentsInChildren<InteractionTarget>(); _host.Begin();
            Assert.That(_host.View.Phase, Is.EqualTo(WorldPhase.Running));
        }
        [TearDown] public void TearDown()
        { if (_host != null) { _host.Shutdown(); UnityEngine.Object.DestroyImmediate(_host.gameObject); } Physics.SyncTransforms(); }
        private InteractionTarget Find(PlayerTargetKind kind) => _targets.Single(t => t.Kind == kind);
        private void Approach(InteractionTarget target, Vector3 position)
        {
            var capsule = _worker.GetComponent<CharacterController>(); capsule.enabled = false;
            _worker.transform.position = position; capsule.enabled = true;
            _worker.Eye.transform.LookAt(target.Shape.bounds.center); Physics.SyncTransforms();
        }
        [Test] public void PickupAndDropProjectCanonicalCustodyIntoPhysics()
        {
            var crate = Find(PlayerTargetKind.Carryable); Approach(crate, new Vector3(-1, 0.06f, 0.5f));
            _host.Act(_worker, PlayerAction.PickUp, crate);
            Assert.That(_host.Held(_worker.Id).EntityId, Is.EqualTo(crate.Id));
            Assert.That(crate.transform.parent, Is.EqualTo(_worker.CarryAnchor));
            Assert.That(crate.GetComponent<Rigidbody>().isKinematic, Is.True); Assert.That(crate.Shape.enabled, Is.False);
            _worker.Eye.transform.localRotation = Quaternion.identity;
            _host.Act(_worker, PlayerAction.Drop, crate);
            Assert.That(_host.Held(_worker.Id), Is.Null); Assert.That(crate.Shape.enabled, Is.True);
            Assert.That(crate.GetComponent<Rigidbody>().isKinematic, Is.False);
        }
        [Test] public void EquipmentAttachesToBodyAndReturnsToWorld()
        {
            var suit = Find(PlayerTargetKind.ProtectiveEquipment); Approach(suit, new Vector3(1, 0.06f, 0.5f));
            _host.Act(_worker, PlayerAction.PickUp, suit); _host.Act(_worker, PlayerAction.Equip, suit);
            Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(suit.transform.parent, Is.EqualTo(_worker.EquipmentAnchor)); Assert.That(_host.Held(_worker.Id), Is.Null);
            _worker.Eye.transform.localRotation = Quaternion.identity;
            _host.Act(_worker, PlayerAction.Unequip, suit);
            Assert.That(_host.Equipment(_worker.Id), Is.Null); Assert.That(suit.Shape.enabled, Is.True);
        }
        [Test] public void SeatDisablesMotionAndBlockedExitKeepsLease()
        {
            var chair = Find(PlayerTargetKind.Seat); Approach(chair, chair.Exit.position);
            _host.Act(_worker, PlayerAction.Sit, chair);
            Assert.That(_host.Worker(_worker.Id).Pose, Is.EqualTo(WorkerPose.Seated));
            Assert.That(_worker.GetComponent<CharacterController>().enabled, Is.False);
            var blocker = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                blocker.transform.position = chair.Exit.position + Vector3.up; Physics.SyncTransforms();
                _host.Act(_worker, PlayerAction.Stand, chair);
                Assert.That(_host.Worker(_worker.Id).Pose, Is.EqualTo(WorkerPose.Seated));
                Assert.That(_host.Held(_worker.Id).EntityId, Is.EqualTo(chair.Id));
            }
            finally { UnityEngine.Object.DestroyImmediate(blocker); Physics.SyncTransforms(); }
            _host.Act(_worker, PlayerAction.Stand, chair);
            Assert.That(_worker.GetComponent<CharacterController>().enabled, Is.True);
            Assert.That(_worker.transform.position, Is.EqualTo(chair.Exit.position));
        }
        [Test] public void PlacementAndTakeUseTheAuthoredAnchor()
        {
            var crate = Find(PlayerTargetKind.Carryable); var table = Find(PlayerTargetKind.Placement);
            Approach(crate, new Vector3(-1, 0.06f, 0.5f)); _host.Act(_worker, PlayerAction.PickUp, crate);
            Approach(table, new Vector3(0, 0.06f, 2)); _host.Act(_worker, PlayerAction.Place, table);
            Assert.That(_host.Placed(table.Id).EntityId, Is.EqualTo(crate.Id));
            Assert.That(crate.transform.parent, Is.EqualTo(table.Attachment));
            _host.Act(_worker, PlayerAction.Take, table);
            Assert.That(_host.Placed(table.Id), Is.Null); Assert.That(_host.Held(_worker.Id).EntityId, Is.EqualTo(crate.Id));
        }
        [Test] public void ControllerMovesAndPausePreventsMovement()
        {
            var start = _worker.transform.position; var input = new PlayerInputFrame(Vector2.up, Vector2.zero, false, false, false);
            for (int i = 0; i < 10; i++) _worker.Step(input, 0.05f);
            Assert.That(_worker.transform.position.z, Is.GreaterThan(start.z + 1));
            _host.TogglePause(); var paused = _worker.transform.position;
            _worker.Step(input, 0.05f); Assert.That(_worker.transform.position, Is.EqualTo(paused));
            Assert.That(Time.timeScale, Is.Zero); _host.TogglePause(); Assert.That(Time.timeScale, Is.EqualTo(1));
        }
        [Test] public void LowCeilingPreventsCrouchExpansion()
        {
            _worker.Step(new PlayerInputFrame(Vector2.zero, Vector2.zero, false, true, false), 0.05f);
            var ceiling = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                ceiling.transform.position = _worker.transform.position + Vector3.up * 1.6f; ceiling.transform.localScale = new Vector3(2, 0.2f, 2);
                Physics.SyncTransforms(); _worker.Step(default, 0.05f);
                Assert.That(_worker.GetComponent<CharacterController>().height, Is.EqualTo(1.15f).Within(0.001f));
            }
            finally { UnityEngine.Object.DestroyImmediate(ceiling); }
        }
        [Test] public void TenResetsReturnBindingsAndClaimsToTheirInitialState()
        {
            var crate = Find(PlayerTargetKind.Carryable); var original = crate.transform.position;
            for (int i = 0; i < 10; i++)
            {
                var oldEpoch = _host.View.Epoch; Approach(crate, new Vector3(-1, 0.06f, 0.5f));
                _host.Act(_worker, PlayerAction.PickUp, crate); Assert.That(_host.Held(_worker.Id), Is.Not.Null);
                _host.Begin(); Assert.That(_host.View.Epoch, Is.Not.EqualTo(oldEpoch));
                Assert.That(_host.View.ActiveClaimCount, Is.Zero); Assert.That(crate.transform.position, Is.EqualTo(original));
                Assert.That(crate.Shape.enabled, Is.True); Assert.That(crate.GetComponent<Rigidbody>().isKinematic, Is.False);
            }
        }
    }
}
