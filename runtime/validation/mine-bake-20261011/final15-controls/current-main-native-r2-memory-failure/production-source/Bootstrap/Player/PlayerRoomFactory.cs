using System;
using CriticalShift.Application;
using CriticalShift.Features.Player.Unity;
using UnityEngine;

namespace CriticalShift.Bootstrap.Player
{
    /// <summary>Disposable graybox fixture, also used by physical binding tests. No map asset dependency.</summary>
    public static class PlayerRoomFactory
    {
        public static LocalShiftHost Create()
        {
            var root = new GameObject("Critical Shift — Player Test Room");
            Box(root.transform, "Floor", new Vector3(0, -0.25f, 0), new Vector3(16, 0.5f, 16));
            Box(root.transform, "Back wall", new Vector3(0, 2, 7.5f), new Vector3(16, 4, 0.5f));
            Box(root.transform, "Front wall", new Vector3(0, 2, -7.5f), new Vector3(16, 4, 0.5f));
            Box(root.transform, "Left wall", new Vector3(-7.5f, 2, 0), new Vector3(0.5f, 4, 16));
            Box(root.transform, "Right wall", new Vector3(7.5f, 2, 0), new Vector3(0.5f, 4, 16));
            var crate = Item(root.transform, "Carry crate", new Vector3(-1, 0.3f, 1.8f), PlayerTargetKind.Carryable, 2);
            var suit = Item(root.transform, "Protective equipment", new Vector3(1, 0.3f, 1.8f), PlayerTargetKind.ProtectiveEquipment, 3);
            var chairObject = Box(root.transform, "Chair", new Vector3(-2, 0.25f, 3), new Vector3(0.8f, 0.5f, 0.8f));
            Box(chairObject.transform, "Chair back", new Vector3(-2, 0.9f, 3.35f), new Vector3(0.8f, 1, 0.1f));
            var seat = Anchor(chairObject.transform, "Seat pose", new Vector3(-2, 0.55f, 3));
            var exit = Anchor(chairObject.transform, "Clear standing exit", new Vector3(-2, 0.06f, 1.8f));
            var chair = chairObject.AddComponent<InteractionTarget>();
            chair.Configure(Id(4), PlayerTargetKind.Seat, "sit on chair", chairObject.GetComponent<Collider>(), anchor: seat, exitPose: exit);
            var tableObject = Box(root.transform, "Placement table", new Vector3(0, 0.5f, 4), new Vector3(2, 0.8f, 1));
            var placement = tableObject.AddComponent<InteractionTarget>();
            placement.Configure(Id(5), PlayerTargetKind.Placement, "place/take item", tableObject.GetComponent<Collider>(),
                anchor: Anchor(tableObject.transform, "Item placement", new Vector3(0, 1.5f, 4)), slot: Id(15));
            var playerObject = new GameObject("Local worker"); playerObject.transform.SetParent(root.transform, false);
            playerObject.transform.position = new Vector3(0, 0.06f, -1);
            var capsule = playerObject.AddComponent<CharacterController>();
            capsule.height = 1.8f; capsule.radius = 0.3f; capsule.center = Vector3.up * 0.9f;
            var cameraObject = new GameObject("First person camera"); cameraObject.transform.SetParent(playerObject.transform, false);
            cameraObject.transform.localPosition = Vector3.up * 1.6f;
            var camera = cameraObject.AddComponent<Camera>(); camera.nearClipPlane = 0.05f; camera.farClipPlane = 60; camera.fieldOfView = 75;
            var carry = Anchor(cameraObject.transform, "Carry anchor", cameraObject.transform.position + Vector3.forward * 1.1f);
            var gear = Anchor(playerObject.transform, "Equipment anchor", playerObject.transform.position + Vector3.up * 0.8f);
            var worker = playerObject.AddComponent<FirstPersonWorker>(); worker.Configure(Id(1), Id(11), camera, carry, gear);
            var lightObject = new GameObject("Room light"); lightObject.transform.SetParent(root.transform, false);
            lightObject.transform.rotation = Quaternion.Euler(50, -30, 0);
            var light = lightObject.AddComponent<Light>(); light.type = LightType.Directional; light.intensity = 1.2f;
            var host = root.AddComponent<LocalShiftHost>();
            var bootstrap = root.AddComponent<PlayerRoomBootstrap>();
            bootstrap.Configure(host, new[] { worker }, new[] { crate, suit, chair, placement }); bootstrap.Initialize();
            return host;
        }
        private static InteractionTarget Item(Transform root, string name, Vector3 position, PlayerTargetKind kind, int id)
        {
            var obj = Box(root, name, position, Vector3.one * 0.4f);
            var body = obj.AddComponent<Rigidbody>(); body.mass = 3; body.interpolation = RigidbodyInterpolation.Interpolate;
            var target = obj.AddComponent<InteractionTarget>(); target.Configure(Id(id), kind, name, obj.GetComponent<Collider>(), body);
            return target;
        }
        private static GameObject Box(Transform parent, string name, Vector3 position, Vector3 scale)
        {
            var obj = GameObject.CreatePrimitive(PrimitiveType.Cube); obj.name = name;
            obj.transform.SetParent(parent, true); obj.transform.position = position;
            obj.transform.localScale = new Vector3(scale.x / parent.lossyScale.x, scale.y / parent.lossyScale.y, scale.z / parent.lossyScale.z);
            return obj;
        }
        private static Transform Anchor(Transform parent, string name, Vector3 position)
        {
            var obj = new GameObject(name); obj.transform.SetParent(parent, true); obj.transform.position = position;
            // Normalize anchor scale: parent primitives have nonuniform scale.
            obj.transform.localScale = new Vector3(1 / parent.lossyScale.x, 1 / parent.lossyScale.y, 1 / parent.lossyScale.z);
            return obj.transform;
        }
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
    }
}
