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
        private Renderer[] _suitMeshes, _coveredMeshes;
        [System.Serializable] private sealed class MapInventory { public RoomInventory[] rooms; }
        [System.Serializable] private sealed class RoomInventory { public string key; public int collisionTriangles; }
        [System.Serializable] private sealed class RigInventory { public MeshInventory[] meshes; }
        [System.Serializable] private sealed class MeshInventory { public string name, region; public bool suit; }

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
            var rig = JsonUtility.FromJson<RigInventory>(File.ReadAllText("Assets/CriticalShift/Generated/Spawn/rig-bindings.json"));
            var renderers = _worker.GetComponentsInChildren<Renderer>(true);
            _suitMeshes = rig.meshes.Where(mesh => mesh.suit).Select(mesh => renderers.Single(r => r.name == mesh.name)).ToArray();
            _coveredMeshes = rig.meshes.Where(mesh => !mesh.suit && !string.IsNullOrEmpty(mesh.region))
                .Select(mesh => renderers.Single(r => r.name == mesh.name)).ToArray();
            Assert.That(_suitMeshes.Length, Is.GreaterThan(0)); Assert.That(_coveredMeshes.Length, Is.GreaterThan(0));
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
            var facing = aim - position; facing.y = 0;
            _worker.transform.SetPositionAndRotation(position, Quaternion.LookRotation(facing)); capsule.enabled = true;
            Physics.SyncTransforms();
            for (int i = 0; i < 8; i++) _worker.Step(default, 0.05f);
            _worker.Eye.transform.LookAt(aim); Physics.SyncTransforms();
        }
        private void ApproachStation(InteractionTarget station)
        {
            var centre = station.Shape.bounds.center;
            Assert.That(station.StationPose, Is.Not.Null, station.name);
            Assert.That(_worker.CanStandAt(station.StationPose.position), Is.True, station.name + " standing position is blocked");
            Approach(station.StationPose.position, centre);
            Assert.That(_worker.Grounded, Is.True, station.name);
            Assert.That(_host.AtStation(_worker, station), Is.True, station.name);
            Assert.That(_host.InReach(_worker, station.Shape), Is.True, station.name);
        }
        private void Outfit(bool worn)
        {
            Assert.That(_suitMeshes.All(mesh => mesh.enabled == worn), Is.True, "Worn suit visibility");
            Assert.That(_coveredMeshes.All(mesh => mesh.enabled != worn), Is.True, "Underlying clothes visibility");
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

        [Test] public void SuitsRetainSourceFabricClearVisorAndHoodCavity()
        {
            foreach(var renderer in _suitMeshes)
                Assert.That(renderer.sharedMaterials.All(m=>m.shader.name=="CriticalShift/BlenderSurface" || m.shader.name=="CriticalShift/BlenderThinVisor"),Is.True,renderer.name);
            var visor=_suitMeshes.Single(r=>r.name=="SUIT_VISOR").sharedMaterial;
            Assert.That(visor.shader.name,Is.EqualTo("CriticalShift/BlenderThinVisor"));
            Assert.That(visor.renderQueue,Is.EqualTo(3000));
            Assert.That(visor.GetFloat("_ReflectionIOR"),Is.EqualTo(1.45f).Within(0.0001f));
            Assert.That(visor.GetTexture("_ReflectionMap"),Is.Not.Null);
            var cloth=_suitMeshes.Single(r=>r.name=="SUIT_BODY").sharedMaterials.First(m=>m.name.Contains("worker-suit"));
            Assert.That(cloth.GetTexture("_BumpMap"),Is.Not.Null);
            Assert.That(cloth.GetTexture("_MetallicGlossMap"),Is.Not.Null);
            Assert.That(cloth.GetFloat("_DielectricSpecular"),Is.EqualTo(0.02f).Within(0.0001f));
            foreach(var name in new[] {"FACE_EYES","FACE_MOUTH"})
            {
                var material=Node(name).GetComponent<Renderer>().sharedMaterial;
                Assert.That(material.shader.name,Is.EqualTo("CriticalShift/BlenderDecal"));
                Assert.That(material.GetTexture("_MainTex"),Is.Not.Null);
                Assert.That(material.renderQueue,Is.EqualTo(2990),"Face decals must render behind the visor");
                Assert.That(material.GetFloat("_DielectricSpecular"),Is.EqualTo(0.012f).Within(0.0001f));
            }
            foreach(var hood in _nodes.Where(n=>n.name.StartsWith("CS_spawn-room_PPE_") && n.name.EndsWith("__SUIT_HOOD")))
            {
                var mesh=hood.GetComponent<MeshFilter>().sharedMesh;
                Assert.That(mesh.colors.Length,Is.EqualTo(mesh.vertexCount),hood.name);
                Assert.That(mesh.colors.Any(c=>c.g<0.4f),Is.True,"Hood interior needs geometry occlusion");
                Assert.That(mesh.colors.Any(c=>c.r>0.9f),Is.True,"Open hood surfaces must retain ambient light");
                Assert.That(hood.GetComponent<Renderer>().sharedMaterials.All(m=>m.shader.name=="CriticalShift/BlenderHood"),Is.True);
                Assert.That(hood.GetComponent<Renderer>().sharedMaterials.All(m=>m.GetFloat("_VertexOcclusion")==1),Is.True);
            }
        }

        [Test] public void PersistedReflectionsRetainRoughSurfaceFiltering()
        {
            var probes=_nodes.SelectMany(n=>n.GetComponents<ReflectionProbe>()).ToArray();
            Assert.That(probes.Length,Is.EqualTo(3));
            foreach(var probe in probes)
            {
                var cube=probe.customBakedTexture as Cubemap;
                Assert.That(cube,Is.Not.Null);
                Assert.That(cube.mipmapCount,Is.GreaterThanOrEqualTo(6));
                Assert.That(cube.filterMode,Is.EqualTo(FilterMode.Trilinear));
                Assert.That(cube.wrapMode,Is.EqualTo(TextureWrapMode.Clamp));
                var importer=(UnityEditor.TextureImporter)UnityEditor.AssetImporter.GetAtPath(UnityEditor.AssetDatabase.GetAssetPath(cube));
                var settings=new UnityEditor.TextureImporterSettings();importer.ReadTextureSettings(settings);
                Assert.That(importer.sRGBTexture,Is.False);
                Assert.That(settings.cubemapConvolution,Is.EqualTo(UnityEditor.TextureImporterCubemapConvolution.Specular));
            }
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

        [UnityTest] public IEnumerator LockerPreparationRequiresStandingInFrontAndCancelsIfDisplaced()
        {
            var stations = _targets.Where(target => target.Station).OrderBy(target => target.name).ToArray();
            for (int i = 0; i < stations.Length; i++)
            {
                var station = stations[i]; var hanging = Node("CS_spawn-room_PPE_" + (i + 1).ToString("00") + "_suit");
                ApproachStation(station);
                _worker.transform.Rotate(Vector3.up, 180); _worker.Eye.transform.LookAt(station.Shape.bounds.center);
                Physics.SyncTransforms();
                Assert.That(_host.InReach(_worker, station.Shape), Is.True);
                _host.Act(_worker, PlayerAction.PrepareEquipment, station);
                Assert.That(_host.Preparation(_worker.Id), Is.Null, "Facing away must reject preparation");
                Approach(station.StationPose.position - station.StationPose.forward * 0.75f, station.Shape.bounds.center);
                Assert.That(_host.InReach(_worker, station.Shape), Is.True);
                _host.Act(_worker, PlayerAction.PrepareEquipment, station);
                Assert.That(_host.Preparation(_worker.Id), Is.Null, "Reach alone must not allow suiting up away from the standing position");
                ApproachStation(station);
                _worker.Step(new PlayerInputFrame(Vector2.zero, Vector2.zero, false, true, false), 0.05f);
                Assert.That(_worker.Crouched, Is.True);
                _host.Act(_worker, PlayerAction.PrepareEquipment, station);
                Assert.That(_host.Preparation(_worker.Id), Is.Null, "Crouching must reject preparation");
                _worker.Step(default, 0.05f);
                ApproachStation(station); _host.Act(_worker, PlayerAction.PrepareEquipment, station);
                Assert.That(_host.Preparation(_worker.Id), Is.Not.Null, station.name + ": " + _host.Feedback);
                Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.None));
                Outfit(false); Assert.That(hanging.gameObject.activeSelf, Is.True);
                yield return null;
                Assert.That(_host.TryUse(_worker), Is.True);
                Assert.That(_host.Preparation(_worker.Id), Is.Null);
                Assert.That(_host.Held(_worker.Id), Is.Null);
                Outfit(false); Assert.That(hanging.gameObject.activeSelf, Is.True);
            }
            var chosen = stations[0]; ApproachStation(chosen);
            _host.Act(_worker, PlayerAction.PrepareEquipment, chosen);
            Assert.That(_host.Preparation(_worker.Id), Is.Not.Null);
            Approach(chosen.StationPose.position - chosen.StationPose.forward * 0.75f, chosen.Shape.bounds.center);
            yield return Until(() => _host.Preparation(_worker.Id) == null, 1, "Displacement did not cancel preparation");
            Assert.That(_host.Held(_worker.Id), Is.Null); Assert.That(_host.Equipment(_worker.Id), Is.Null);
            Outfit(false); Assert.That(Node("CS_spawn-room_PPE_01_suit").gameObject.activeSelf, Is.True);
        }

        [UnityTest] public IEnumerator LockerAnimationSwapsSuitOnlyAtCompletionAndPauses()
        {
            var chosen = _targets.Single(target => target.name == "Suit station 1"); ApproachStation(chosen);
            var hanging = Node("CS_spawn-room_PPE_01_suit");
            var bones = _worker.GetComponentsInChildren<SkinnedMeshRenderer>(true).SelectMany(mesh => mesh.bones).Distinct().ToArray();
            var before = bones.Select(bone => bone.localRotation).ToArray();
            _host.Act(_worker, PlayerAction.PrepareEquipment, chosen);
            Assert.That(_host.Preparation(_worker.Id), Is.Not.Null);
            var due = _host.Preparation(_worker.Id).DueShiftMilliseconds; var started = due - chosen.PreparationMilliseconds;
            Outfit(false); Assert.That(hanging.gameObject.activeSelf, Is.True);
            var origin = _worker.transform.position; var rotation = _worker.transform.rotation;
            _worker.Step(new PlayerInputFrame(Vector2.up, Vector2.one * 100, true, true, true), 0.05f);
            Assert.That(_worker.transform.position, Is.EqualTo(origin));
            Assert.That(_worker.transform.rotation, Is.EqualTo(rotation)); Assert.That(_worker.Crouched, Is.False);
            yield return Until(() => _animator.GetCurrentAnimatorStateInfo(0).IsName("SUIT_UP"), 1,
                "Suit-up animation did not play; clip duration=" + _animator.runtimeAnimatorController.animationClips.Single(c => c.name == "SUIT_UP").length +
                "; state=" + _animator.GetCurrentAnimatorStateInfo(0).shortNameHash + "; next=" + _animator.GetNextAnimatorStateInfo(0).shortNameHash +
                "; speed=" + _animator.speed);
            _host.TogglePause(); yield return null;
            var elapsed = _host.View.ElapsedMilliseconds; var pausedProgress = _animator.GetCurrentAnimatorStateInfo(0).normalizedTime;
            var pausedPose = bones.Select(bone => bone.localRotation).ToArray();
            yield return new WaitForSecondsRealtime(0.3f);
            Assert.That(_host.View.ElapsedMilliseconds, Is.EqualTo(elapsed));
            Assert.That(_animator.speed, Is.Zero);
            Assert.That(_host.Equipment(_worker.Id), Is.Null);
            Assert.That(_animator.GetCurrentAnimatorStateInfo(0).normalizedTime, Is.EqualTo(pausedProgress).Within(0.0001f));
            Assert.That(bones.Where((bone, i) => Quaternion.Angle(pausedPose[i], bone.localRotation) > 0.01f).Any(), Is.False);
            Outfit(false); Assert.That(hanging.gameObject.activeSelf, Is.True);
            _host.TogglePause();
            var deadline = Time.realtimeSinceStartupAsDouble + 17; bool middleObserved = false;
            while (_host.Equipment(_worker.Id) == null && Time.realtimeSinceStartupAsDouble < deadline)
            {
                Outfit(false); Assert.That(hanging.gameObject.activeSelf, Is.True, "The suit must stay in the locker throughout the animation");
                Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.None));
                float progress = (_host.View.ElapsedMilliseconds - started) / (float)chosen.PreparationMilliseconds;
                if (progress >= 0.45f && progress < 0.9f)
                {
                    Assert.That(_animator.GetCurrentAnimatorStateInfo(0).IsName("SUIT_UP"), Is.True);
                    Assert.That(_animator.GetCurrentAnimatorStateInfo(0).normalizedTime, Is.EqualTo(progress).Within(0.03f),
                        "Animation must follow the preparation clock rather than finish early");
                    if (!middleObserved)
                        Assert.That(bones.Where((bone, i) => Quaternion.Angle(before[i], bone.localRotation) > 10).Any(), Is.True);
                    middleObserved = true;
                }
                yield return null;
            }
            Assert.That(middleObserved, Is.True); Assert.That(_host.Equipment(_worker.Id), Is.Not.Null, _host.Feedback);
            Assert.That(_host.Equipment(_worker.Id).EntityId, Is.EqualTo(chosen.Id));
            Assert.That(_host.View.ElapsedMilliseconds, Is.GreaterThanOrEqualTo(due));
            Assert.That(_animator.GetCurrentAnimatorStateInfo(0).IsName("SUIT_UP"), Is.True);
            Assert.That(_animator.GetCurrentAnimatorStateInfo(0).normalizedTime, Is.GreaterThanOrEqualTo(0.99f));
            Outfit(true);
            Assert.That(_host.Preparation(_worker.Id), Is.Null);
            Assert.That(_host.Worker(_worker.Id).Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(Node("CS_spawn-room_PPE_01_suit").gameObject.activeSelf, Is.False);
            _host.Act(_worker, PlayerAction.Unequip, chosen);
            Assert.That(_host.Equipment(_worker.Id), Is.Null, _host.Feedback);
            Outfit(false);
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
