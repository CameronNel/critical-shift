using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Simple host-local hold model: one player owns the held rigidbody until release.
    public sealed class PrototypePhysicsInteractor : MonoBehaviour
    {
        public float reach = 3f;
        public KeyCode grabKey = KeyCode.G;
        PrototypeCarryable held; PrototypeWorkerBody draggedWorker; Camera view; float distance; bool previousKinematic, previousWorkerKinematic;
        public PrototypeCarryable Held => held;
        void Awake() => view = GetComponentInChildren<Camera>();
        void Update()
        {
            if (Input.GetKeyDown(grabKey) || Input.GetMouseButtonDown(1)) { if (held == null && draggedWorker == null) { if (!TryGrab()) TryDragWorker(); } else Release(false); }
            if (held != null && Input.GetMouseButtonDown(0)) Release(true);
        }
        void FixedUpdate()
        {
            if (view == null) return;
            var point = view.transform.position + view.transform.forward * Mathf.Clamp(distance, 0.8f, held != null ? held.maxHoldDistance : 1.5f);
            if (held != null) { var body = held.Body; body.MovePosition(Vector3.Lerp(body.position, point, 0.45f)); body.angularVelocity *= 0.75f; }
            if (draggedWorker != null && draggedWorker.PhysicsBody != null)
                draggedWorker.PhysicsBody.MovePosition(Vector3.Lerp(draggedWorker.PhysicsBody.position, point, 0.35f));
        }
        public bool TryGrab()
        {
            if (held != null || view == null || !Physics.Raycast(view.transform.position, view.transform.forward, out var hit, reach)) return false;
            var item = hit.collider.GetComponentInParent<PrototypeCarryable>();
            if (item == null || item.IsHeld || item.Body == null) return false;
            held = item; distance = Mathf.Clamp(Vector3.Distance(view.transform.position, item.transform.position), 0.8f, item.maxHoldDistance);
            previousKinematic = item.Body.isKinematic; item.Body.isKinematic = true; item.IsHeld = true; return true;
        }
        public void Release(bool throwObject)
        {
            if (draggedWorker != null) { draggedWorker.EndDrag(); if (draggedWorker.PhysicsBody != null) draggedWorker.PhysicsBody.isKinematic = previousWorkerKinematic; draggedWorker = null; return; }
            if (held == null) return;
            var item = held; held = null; item.IsHeld = false; item.Body.isKinematic = previousKinematic;
            if (throwObject && view != null) item.Body.AddForce(view.transform.forward * item.throwImpulse, ForceMode.VelocityChange);
        }
        public void ReleaseIfHolding(PrototypeCarryable item)
        {
            if (item != null && held == item) Release(false);
        }
        bool TryDragWorker()
        {
            if (view == null || !Physics.Raycast(view.transform.position, view.transform.forward, out var hit, reach)) return false;
            var worker = hit.collider.GetComponentInParent<PrototypeWorkerBody>();
            if (worker == null || !worker.BeginDrag()) return false;
            draggedWorker = worker;
            if (worker.PhysicsBody != null) { previousWorkerKinematic = worker.PhysicsBody.isKinematic; worker.PhysicsBody.isKinematic = true; }
            return true;
        }
        public bool TryDrag(PrototypeWorkerBody worker)
        {
            if (held != null || draggedWorker != null || worker == null || !worker.BeginDrag()) return false;
            draggedWorker = worker;
            distance = 1.5f;
            if (worker.PhysicsBody != null)
            {
                previousWorkerKinematic = worker.PhysicsBody.isKinematic;
                worker.PhysicsBody.isKinematic = true;
            }
            return true;
        }

        void OnDisable() { Release(false); }
    }
}
