#if UNITY_EDITOR
using System.Collections;
using System.IO;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Features.Player.Unity;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace CriticalShift.Tests.Player
{
    // Requires the real exported map, saved by SpawnMapBuild.Create. No graybox substitutions.
    public sealed class SpawnMapBindingTests
    {
        private Scene _scene;
        private LocalShiftHost _host;
        private FirstPersonWorker _worker;
        private Animator _animator;
        private Transform[] _nodes;
        private InteractionTarget[] _targets;
        [System.Serializable] private sealed class MapInventory { public RoomInventory[] rooms; }
        [System.Serializable] private sealed class RoomInventory { public string key; public int collisionTriangles; }

        [UnitySetUp] public IEnumerator SetUp()
        {
            _scene = EditorSceneManager.LoadSceneInPlayMode("Assets/CriticalShift/Generated/Spawn/AssembledMap.unity",
                new LoadSceneParameters(LoadSceneMode.Additive));
            yield return null;
            _host = _scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren<LocalShiftHost>()).Single();
            _worker = _host.GetComponentInChildren<FirstPersonWorker>();
            _animator = _worker.GetComponentInChildren<Animator>();
            _nodes = _host.GetComponentsInChildren<Transform>(true);
            _targets = _host.GetComponentsInChildren<InteractionTarget>();
            Assert.That(_host.View, Is.Not.Null);
            if (_host.View.Phase == WorldPhase.Paused) _host.TogglePause();
            Assert.That(_host.View.Phase, Is.EqualTo(WorldPhase.Running), _host.Feedback);
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            if (_host != null) _host.Shutdown();
            if (_scene.IsValid() && _scene.isLoaded) yield return SceneManager.UnloadSceneAsync(_scene);
            Physics.SyncTransforms();
        }
        private Transform Node(string name) => _nodes.Single(node => node.name == name);
        private void Approach(Vector3 position, Vector3 aim)
        {
            var capsule = _worker.GetComponent<CharacterController>(); capsule.enabled = false;
            _worker.transform.SetPositionAndRotation(position, Quaternion.identity); capsule.enabled = true;
            Physics.SyncTransforms();
            for (int i = 0; i < 8; i++) _worker.Step(default, 0.05f);
            _worker.Eye.transform.LookAt(aim); Physics.SyncTransforms();
        }
        private void ApproachStation(InteractionTarget station)
        {
            var room = Node("ROOM_spawn-room");
            var centre = station.Shape.bounds.center;
            var side = room.InverseTransformPoint(centre).z > 4 ? -1 : 1;
            var position = centre + Vector3.forward * (side * 0.9f); position.y = room.position.y + 0.06f;
            Approach(position, centre);
            Assert.That(_worker.Grounded, Is.True, station.name);
            Assert.That(_host.InReach(_worker, station.Shape), Is.True, station.name);
        }
        private IEnumerator Until(System.Func<bool> condition, float seconds, string reason)
        {
            var deadline = Time.realtimeSinceStartupAsDouble + seconds;
            while (!condition() && Time.realtimeSinceStartupAsDouble < deadline) yield return null;
            Assert.That(condition(), Is.True, reason + ": " + _host.Feedback);
        }
        private string RayTo(Vector3 point)
        {
            var origin = _worker.Eye.transform.position;
            return _host.Ray(_worker, point - origin, 4, out var hit) ?
                hit.collider.name + " at " + hit.point.ToString("F4") + " triangle " + hit.triangleIndex : "no hit";
        }
        private string ThresholdRays()
        {
            return string.Join("; ", new[] { 0.08f, 0.3f, 0.6f }.Select(height =>
            {
                var start = _worker.transform.position + Vector3.up * height;
                var hits = Physics.RaycastAll(start, Vector3.forward, 2, ~0, QueryTriggerInteraction.Ignore)
                    .Where(hit => !hit.collider.transform.IsChildOf(_worker.transform)).OrderBy(hit => hit.distance).ToArray();
                return "height " + height + ": " + (hits.Length == 0 ? "clear" : hits[0].collider.name + " at " +
                    hits[0].point.ToString("F4") + " triangle " + hits[0].triangleIndex);
            }));
        }

        [Test] public void ImportedMapStartsWithCompleteCollisionAndAnimatedRig()
        {
            Assert.That(_nodes.Count(node => node.name.StartsWith("ROOM_")), Is.EqualTo(6));
            var collisions = _nodes.Where(node => node.name.StartsWith("Static collision — "))
                .SelectMany(node => node.GetComponentsInChildren<MeshCollider>()).ToArray();
            Assert.That(collisions.Length, Is.EqualTo(6));
            var exported = JsonUtility.FromJson<MapInventory>(File.ReadAllText("Assets/CriticalShift/Generated/Spawn/map-bindings.json"));
            foreach (var room in exported.rooms)
            {
                var shape = Node("Static collision — " + room.key).GetComponentInChildren<MeshCollider>();
                Assert.That(shape.sharedMesh.triangles.Length / 3, Is.EqualTo(room.collisionTriangles), room.key);
                if (room.collisionTriangles > 2000000)
                    Assert.That(shape.cookingOptions.HasFlag(MeshColliderCookingOptions.UseFastMidphase), Is.False,
                        room.key + " exceeds the safe fast-midphase mesh size");
            }
            Assert.That(_animator.avatar.isValid, Is.True);
            Assert.That(_animator.applyRootMotion, Is.False);
            Assert.That(_animator.runtimeAnimatorController.animationClips.Select(clip => clip.name).Distinct().Count(), Is.EqualTo(52));
            foreach (var state in new[] { "IDLE", "WALK_F", "SUIT_UP", "SPAWN_SIT_DOWN", "SPAWN_SEATED_IDLE", "SPAWN_STAND_UP" })
                Assert.That(_animator.HasState(0, Animator.StringToHash(state)), Is.True, state);
            Assert.That(_worker.CanStandAt(_worker.transform.position), Is.True);
        }

        [UnityTest] public IEnumerator AllBenchSeatsAnimateAndHaveUsableStandingExits()
        {
            foreach (var seat in _targets.Where(target => target.Kind == PlayerTargetKind.Seat))
            {
                Approach(seat.Exit.position, seat.Shape.bounds.center);
                Assert.That(_host.InReach(_worker, seat.Shape), Is.True, seat.name + "; ray=" + RayTo(seat.Shape.bounds.center) +
                    "; eye=" + _worker.Eye.transform.position.ToString("F4") + "; target=" + seat.Shape.bounds.center.ToString("F4"));
                var bones = _worker.GetComponentsInChildren<SkinnedMeshRenderer>(true).SelectMany(mesh => mesh.bones).Distinct().ToArray();
                var before = bones.Select(bone => bone.localRotation).ToArray();
                _host.Act(_worker, PlayerAction.Sit, seat);
                Assert.That(_host.Worker(_worker.Id).Pose, Is.EqualTo(WorkerPose.Seated), _host.Feedback);
                Assert.That(_worker.GetComponent<CharacterController>().enabled, Is.False);
                yield return Until(() => _animator.GetCurrentAnimatorStateInfo(0).IsName("SPAWN_SEATED_IDLE"), 2, "Seated idle did not play");
                Assert.That(bones.Where((bone, i) => Quaternion.Angle(before[i], bone.localRotation) > 10).Any(), Is.True,
                    "The imported rig bones did not move into the seated pose.");
                _host.Act(_worker, PlayerAction.Stand, seat);
                Assert.That(_host.Worker(_worker.Id).Pose, Is.EqualTo(WorkerPose.Upright), _host.Feedback);
                Assert.That(_worker.GetComponent<CharacterController>().enabled, Is.True);
                Assert.That(_worker.CanStandAt(_worker.transform.position), Is.True, seat.name);
                yield return Until(() => _animator.GetCurrentAnimatorStateInfo(0).IsName("SPAWN_STAND_UP"), 1, "Stand-up did not play");
                yield return Until(() => !_animator.GetCurrentAnimatorStateInfo(0).IsName("SPAWN_STAND_UP"), 2, "Stand-up did not finish");
            }
        }

        [UnityTest] public IEnumerator LockerPreparationPausesCompletesAndReturnsTheAuthoredSuit()
        {
            var stations = _targets.Where(target => target.Station).OrderBy(target => target.name).ToArray();
            foreach (var station in stations)
            {
                ApproachStation(station); _host.Act(_worker, PlayerAction.PrepareEquipment, station);
                Assert.That(_host.Preparation(_worker.Id), Is.Not.Null, station.name + ": " + _host.Feedback);
                Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.None));
                Assert.That(_host.TryUse(_worker), Is.True);
                Assert.That(_host.Preparation(_worker.Id), Is.Null);
                Assert.That(_host.Held(_worker.Id), Is.Null);
            }
            var chosen = stations[0]; ApproachStation(chosen);
            _host.Act(_worker, PlayerAction.PrepareEquipment, chosen);
            Assert.That(_host.Preparation(_worker.Id), Is.Not.Null);
            var origin = _worker.transform.position;
            _worker.Step(new PlayerInputFrame(Vector2.up, Vector2.zero, false, false, false), 0.05f);
            Assert.That(_worker.transform.position, Is.EqualTo(origin));
            yield return Until(() => _animator.GetCurrentAnimatorStateInfo(0).IsName("SUIT_UP"), 1,
                "Suit-up animation did not play; clip duration=" + _animator.runtimeAnimatorController.animationClips.Single(c => c.name == "SUIT_UP").length +
                "; state=" + _animator.GetCurrentAnimatorStateInfo(0).shortNameHash + "; next=" + _animator.GetNextAnimatorStateInfo(0).shortNameHash +
                "; speed=" + _animator.speed);
            _host.TogglePause(); var elapsed = _host.View.ElapsedMilliseconds;
            yield return new WaitForSecondsRealtime(0.3f);
            Assert.That(_host.View.ElapsedMilliseconds, Is.EqualTo(elapsed));
            Assert.That(_animator.speed, Is.Zero);
            Assert.That(_host.Equipment(_worker.Id), Is.Null);
            _host.TogglePause();
            yield return Until(() => _host.Equipment(_worker.Id) != null, 17, "Preparation did not equip the suit");
            Assert.That(_host.Equipment(_worker.Id).EntityId, Is.EqualTo(chosen.Id));
            Assert.That(_host.Preparation(_worker.Id), Is.Null);
            Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(Node("CS_spawn-room_PPE_01_suit").gameObject.activeSelf, Is.False);
            _host.Act(_worker, PlayerAction.Unequip, chosen);
            Assert.That(_host.Equipment(_worker.Id), Is.Null, _host.Feedback);
            Assert.That(Node("CS_spawn-room_PPE_01_suit").gameObject.activeSelf, Is.True);
        }

        [UnityTest] public IEnumerator AirlockControlOpensTheDoorAndAllowsWalkingIntoTheCafeteria()
        {
            var room = Node("ROOM_spawn-room"); var control = Node("Airlock control -1").GetComponent<Collider>();
            var point = control.bounds.center - Vector3.forward; point.y = room.position.y + 0.06f;
            Approach(point, control.bounds.center);
            Assert.That(_host.TryUse(_worker), Is.True, "Airlock control could not be aimed at");
            var door = Node("Airlock").GetComponent<MovingDoor>();
            yield return Until(() => door.Open, 4, "Airlock did not open");
            var start = room.position + new Vector3(0, 0.06f, 8.2f); Approach(start, start + Vector3.forward);
            for (int i = 0; i < 80; i++) _worker.Step(new PlayerInputFrame(Vector2.up, Vector2.zero, false, false, false), 0.05f);
            Assert.That(_worker.transform.position.z, Is.GreaterThan(Node("ROOM_front-end-area").position.z + 0.3f),
                "The authored spawn/cafeteria connection is not traversable by the player capsule; ray=" +
                RayTo(_worker.Eye.transform.position + Vector3.forward * 3) + "; feet=" + _worker.transform.position.ToString("F4") + "; " + ThresholdRays());
            Assert.That(_worker.Grounded, Is.True);
        }

        [UnityTest] public IEnumerator IntegrityChamberSealsTestsAndReleasesAnUnsuitedWorker()
        {
            var position = Node("Integrity test position").position;
            var button = Node("Integrity test button").GetComponent<Collider>();
            Approach(position, button.bounds.center);
            Assert.That(_host.TryUse(_worker), Is.True, "The authored chamber button is not reachable from inside");
            Assert.That(_host.Busy(_worker.Id), Is.True, _host.Feedback);
            var door = Node("Integrity chamber").GetComponent<MovingDoor>();
            yield return Until(() => door.Closed, 4, "The actual curved chamber leaves did not seal");
            yield return Until(() => !_host.Busy(_worker.Id), 5, "The timed integrity test did not finish");
            Assert.That(Node("CS_spawn-room_POD_state_FAIL").gameObject.activeSelf, Is.True);
            Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.None));
            yield return Until(() => door.Open, 4, "The chamber did not release the worker");
        }
    }
}
#endif
