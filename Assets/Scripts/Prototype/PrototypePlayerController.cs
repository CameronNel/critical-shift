using UnityEngine;

namespace CriticalShift.Prototype
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class PrototypePlayerController : MonoBehaviour
    {
        public float moveSpeed = 5f;
        public float sprintSpeed = 8f;
        public float lookSpeed = 2f;
        public float interactRange = 3f;
        CharacterController controller; Camera view; float pitch; Vector3 velocity;
        PrototypeInteractable focusedTarget;
        PrototypePhysicsInteractor physicsInteractor;
        PrototypeWorkerBody workerBody;
        bool wearingSuit;
        public string FocusPrompt { get; private set; }
        public bool WearingSuit => wearingSuit;
        public PrototypeWorkerBody.BodyState BodyState => workerBody != null ? workerBody.State : PrototypeWorkerBody.BodyState.Normal;

        public void SetSuitState(bool suitOn) { wearingSuit = suitOn; }

        void Awake()
        {
            controller = GetComponent<CharacterController>();
            view = GetComponentInChildren<Camera>();
            if (view == null)
            {
                var go = new GameObject("View");
                go.transform.SetParent(transform);
                go.transform.localPosition = new Vector3(0f, 1.6f, 0f);
                go.tag = "MainCamera";
                view = go.AddComponent<Camera>();
                go.AddComponent<AudioListener>();
            }
            BuildViewHands();
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
            physicsInteractor = GetComponent<PrototypePhysicsInteractor>();
            if (physicsInteractor == null) physicsInteractor = gameObject.AddComponent<PrototypePhysicsInteractor>();
            workerBody = GetComponent<PrototypeWorkerBody>();
            if (workerBody == null) workerBody = gameObject.AddComponent<PrototypeWorkerBody>();
        }

        void BuildViewHands()
        {
            if (view == null || view.transform.Find("View Hands") != null) return;
            var root = new GameObject("View Hands").transform;
            root.SetParent(view.transform);
            root.localPosition = Vector3.zero;
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            var material = shader != null ? new Material(shader) { color = new Color(.18f, .42f, .46f) } : null;
            for (int i = 0; i < 2; i++)
            {
                var hand = GameObject.CreatePrimitive(PrimitiveType.Cube);
                hand.name = i == 0 ? "Left Glove" : "Right Glove";
                hand.transform.SetParent(root);
                hand.transform.localPosition = new Vector3(i == 0 ? -.23f : .23f, -.24f, .62f);
                hand.transform.localRotation = Quaternion.Euler(18f, i == 0 ? -8f : 8f, 0f);
                hand.transform.localScale = new Vector3(.13f, .13f, .34f);
                var handCollider = hand.GetComponent<Collider>();
                if (Application.isPlaying) Destroy(handCollider); else DestroyImmediate(handCollider);
                if (material != null) hand.GetComponent<Renderer>().sharedMaterial = material;
            }
        }

        void Update()
        {
            Look();
            Move();
            FindFocus();
            if (Input.GetKeyDown(KeyCode.R) && PrototypeGameDirector.Instance != null && PrototypeGameDirector.Instance.IsTerminal) PrototypeGameDirector.Instance.ResetShift();
            if (Input.GetKeyDown(KeyCode.E)) Interact(false);
            if (Input.GetKeyDown(KeyCode.F)) Interact(true);
        }

        void Look()
        {
            if (Input.GetKeyDown(KeyCode.Escape)) { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
            if (Cursor.lockState != CursorLockMode.Locked && Input.GetMouseButtonDown(0)) { Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false; }
            if (Cursor.lockState != CursorLockMode.Locked) return;
            transform.Rotate(0f, Input.GetAxis("Mouse X") * lookSpeed, 0f);
            pitch = Mathf.Clamp(pitch - Input.GetAxis("Mouse Y") * lookSpeed, -80f, 80f);
            float knockdownTilt = workerBody != null && workerBody.State == PrototypeWorkerBody.BodyState.KnockedDown ? 62f : 0f;
            view.transform.localEulerAngles = new Vector3(pitch, 0f, knockdownTilt);
        }

        void Move()
        {
            if (workerBody != null && (workerBody.State == PrototypeWorkerBody.BodyState.KnockedDown ||
                workerBody.State == PrototypeWorkerBody.BodyState.Incapacitated ||
                workerBody.State == PrototypeWorkerBody.BodyState.Reanimating ||
                workerBody.State == PrototypeWorkerBody.BodyState.BeingDragged))
                return;
            Vector3 input = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical"));
            input = Vector3.ClampMagnitude(input, 1f);
            float speed = Input.GetKey(KeyCode.LeftShift) ? sprintSpeed : moveSpeed;
            if (!wearingSuit) speed *= 1.15f;
            bool crouching = Input.GetKey(KeyCode.LeftControl);
            controller.height = crouching ? 1.15f : 1.8f;
            controller.center = new Vector3(0f, controller.height * 0.5f, 0f);
            view.transform.localPosition = new Vector3(0f, crouching ? 1.0f : 1.6f, 0f);
            controller.Move(transform.TransformDirection(input) * speed * Time.deltaTime);
            if (controller.isGrounded && velocity.y < 0f) velocity.y = -2f;
            if (controller.isGrounded && Input.GetKeyDown(KeyCode.Space)) velocity.y = 5f;
            velocity.y += Physics.gravity.y * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }

        void FindFocus()
        {
            FocusPrompt = null;
            focusedTarget = null;
            if (view != null && Physics.Raycast(view.transform.position, view.transform.forward, out var hit, interactRange))
            {
                var target = hit.collider.GetComponentInParent<PrototypeInteractable>();
                if (target != null)
                {
                    focusedTarget = target;
                    FocusPrompt = target.SupportsShortcut
                        ? $"[E] {target.Prompt}   [F] {target.AlternatePrompt}"
                        : $"[E] {target.Prompt}";
                }
            }
        }

        void Interact(bool forceShortcut)
        {
            if (workerBody != null && workerBody.State != PrototypeWorkerBody.BodyState.Normal && workerBody.State != PrototypeWorkerBody.BodyState.Recovering) return;
            if (focusedTarget != null)
                focusedTarget.Interact(forceShortcut && focusedTarget.SupportsShortcut);
        }

        void OnDisable() { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
    }
}
