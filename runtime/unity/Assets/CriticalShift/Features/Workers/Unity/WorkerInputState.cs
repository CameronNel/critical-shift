namespace CriticalShift.Features.Workers.Unity
{
    public enum WorkerActionInput { Script, Interact, Radio, Primary }

    // Local presentation state only; key release never commits a gameplay operation.
    public sealed class WorkerInputState
    {
        public bool ApplicationFocused { get; private set; } = true;
        public bool Captured { get; private set; } = true;
        private WorkerActionInput hold;

        public void SetApplicationFocus(bool value)
        {
            ApplicationFocused = value;
            if (!value) { Captured = false; ClearHold(); }
        }

        // A click that captures the cursor is consumed, so it cannot also dig or use a tool.
        public bool UpdateCapture(bool escapePressed, bool resumePressed)
        {
            if (!ApplicationFocused) return false;
            bool previous = Captured;
            if (escapePressed && Captured) { Captured = false; ClearHold(); }
            else if (!Captured && (escapePressed || resumePressed)) Captured = true;
            return previous != Captured;
        }

        public void BindHold(WorkerActionInput input) { hold = input; }
        public void ClearHold() { hold = WorkerActionInput.Script; }
        public bool HoldReleased(bool interactDown, bool radioDown, bool primaryDown)
        {
            switch (hold)
            {
                case WorkerActionInput.Interact: return !interactDown;
                case WorkerActionInput.Radio: return !radioDown;
                case WorkerActionInput.Primary: return !primaryDown;
                default: return false; // Scripted loops end through explicit cancellation.
            }
        }
    }
}
