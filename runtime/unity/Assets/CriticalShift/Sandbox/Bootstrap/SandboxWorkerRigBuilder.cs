using System;
using CriticalShift.Features.Workers.Unity;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Sandbox
{
    /// <summary>Debug humanoid geometry and joint bindings, isolated from every authored character/map asset.</summary>
    internal static class SandboxWorkerRigBuilder
    {
        internal static WorkerBodyRig Build(Guid epoch, Guid actor, CharacterController controller,
            Transform eyes, SandboxPrimitives shapes)
        {
            var rigRoot = SandboxPrimitives.Empty("Worker physical rig", controller.transform, Vector3.zero);
            var bodies = new Rigidbody[11]; var colliders = new Collider[11];
            bodies[0] = Segment(0, "Pelvis", new Vector3(0, 0.86f, 0), 0.20f, 0.4f, 12, shapes.Dark);
            bodies[1] = Segment(1, "Torso", new Vector3(0, 1.23f, 0), 0.19f, 0.55f, 18, shapes.Yellow);
            bodies[2] = Segment(2, "Head", new Vector3(0, 1.65f, 0), 0.15f, 0.3f, 4, shapes.Steel);
            bodies[3] = Segment(3, "Left upper arm", new Vector3(-0.34f, 1.25f, 0), 0.085f, 0.4f, 3, shapes.Yellow);
            bodies[4] = Segment(4, "Left forearm", new Vector3(-0.37f, 0.9f, 0), 0.075f, 0.35f, 2, shapes.Dark);
            bodies[5] = Segment(5, "Right upper arm", new Vector3(0.34f, 1.25f, 0), 0.085f, 0.4f, 3, shapes.Yellow);
            bodies[6] = Segment(6, "Right forearm", new Vector3(0.37f, 0.9f, 0), 0.075f, 0.35f, 2, shapes.Dark);
            bodies[7] = Segment(7, "Left thigh", new Vector3(-0.14f, 0.57f, 0), 0.115f, 0.45f, 7, shapes.Steel);
            bodies[8] = Segment(8, "Left shin", new Vector3(-0.14f, 0.24f, 0), 0.095f, 0.45f, 5, shapes.Dark);
            bodies[9] = Segment(9, "Right thigh", new Vector3(0.14f, 0.57f, 0), 0.115f, 0.45f, 7, shapes.Steel);
            bodies[10] = Segment(10, "Right shin", new Vector3(0.14f, 0.24f, 0), 0.095f, 0.45f, 5, shapes.Dark);
            Connect(1, 0, new Vector3(0, 1.02f, 0)); Connect(2, 1, new Vector3(0, 1.48f, 0));
            Connect(3, 1, new Vector3(-0.28f, 1.43f, 0)); Connect(4, 3, new Vector3(-0.36f, 1.07f, 0));
            Connect(5, 1, new Vector3(0.28f, 1.43f, 0)); Connect(6, 5, new Vector3(0.36f, 1.07f, 0));
            Connect(7, 0, new Vector3(-0.14f, 0.77f, 0)); Connect(8, 7, new Vector3(-0.14f, 0.43f, 0));
            Connect(9, 0, new Vector3(0.14f, 0.77f, 0)); Connect(10, 9, new Vector3(0.14f, 0.43f, 0));
            bodies[2].GetComponentInChildren<Renderer>().shadowCastingMode = ShadowCastingMode.ShadowsOnly;
            var rig = rigRoot.AddComponent<WorkerBodyRig>();
            rig.Initialize(epoch, actor, controller, eyes, bodies[0], bodies[2].transform, bodies, colliders);
            return rig;

            Rigidbody Segment(int index, string name, Vector3 center, float radius, float height, float mass, Material material)
            {
                var item = SandboxPrimitives.Empty(name, rigRoot.transform, center);
                var collider = item.AddComponent<CapsuleCollider>(); collider.radius = radius; collider.height = height; collider.enabled = false;
                var body = item.AddComponent<Rigidbody>(); body.mass = mass; body.isKinematic = true; body.useGravity = false;
                body.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
                body.maxAngularVelocity = 8;
                colliders[index] = collider;
                SandboxPrimitives.Shape(PrimitiveType.Capsule, name + " visual", item.transform, Vector3.zero,
                    new Vector3(radius * 2, height * 0.5f, radius * 2), material, false);
                return body;
            }

            void Connect(int child, int parent, Vector3 localAnchor)
            {
                Vector3 anchor = controller.transform.TransformPoint(localAnchor);
                var joint = bodies[child].gameObject.AddComponent<CharacterJoint>(); joint.connectedBody = bodies[parent];
                joint.autoConfigureConnectedAnchor = false;
                joint.anchor = bodies[child].transform.InverseTransformPoint(anchor);
                joint.connectedAnchor = bodies[parent].transform.InverseTransformPoint(anchor);
                joint.axis = Vector3.up; joint.swingAxis = Vector3.right;
                joint.lowTwistLimit = new SoftJointLimit { limit = -25 };
                joint.highTwistLimit = new SoftJointLimit { limit = 25 };
                joint.swing1Limit = new SoftJointLimit { limit = 40 };
                joint.swing2Limit = new SoftJointLimit { limit = 40 };
                joint.enableCollision = false;
            }
        }
    }
}
