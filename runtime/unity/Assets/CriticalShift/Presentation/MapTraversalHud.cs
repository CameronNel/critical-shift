using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Temporary local traversal controls, using the fixture's existing IMGUI input approach.</summary>
    public sealed class MapTraversalHud : MonoBehaviour
    {
        private Action<Vector2> movement, look;
        private Action jump, interact, recover, evacuate, restart;
        private Func<string> status;
        private readonly HashSet<KeyCode> held = new HashSet<KeyCode>();
        private GUIStyle wrapped;
        public void Initialize(Action<Vector2> move, Action<Vector2> turn, Action hop, Action door, Action recovery,
            Action evacuationExercise, Action reset, Func<string> readStatus)
        {
            if (status != null || move == null || turn == null || hop == null || door == null || recovery == null ||
                evacuationExercise == null || reset == null || readStatus == null) throw new ArgumentException("Bind every traversal control explicitly.");
            movement = move; look = turn; jump = hop; interact = door; recover = recovery; evacuate = evacuationExercise;
            restart = reset; status = readStatus;
        }
        private void Update()
        {
            if (status == null) return;
            movement(new Vector2((held.Contains(KeyCode.D) ? 1 : 0) - (held.Contains(KeyCode.A) ? 1 : 0),
                (held.Contains(KeyCode.W) ? 1 : 0) - (held.Contains(KeyCode.S) ? 1 : 0)));
        }
        private void OnGUI()
        {
            if (status == null) return;
            var input = Event.current;
            if (input.type == EventType.MouseDrag && input.button == 1) { look(new Vector2(input.delta.x, -input.delta.y)); input.Use(); }
            bool key = input.keyCode == KeyCode.W || input.keyCode == KeyCode.A || input.keyCode == KeyCode.S || input.keyCode == KeyCode.D ||
                input.keyCode == KeyCode.E || input.keyCode == KeyCode.H || input.keyCode == KeyCode.Space;
            if (key && input.type == EventType.KeyUp) { held.Remove(input.keyCode); input.Use(); }
            if (key && input.type == EventType.KeyDown)
            {
                if (held.Add(input.keyCode))
                {
                    if (input.keyCode == KeyCode.E) interact();
                    if (input.keyCode == KeyCode.H) recover();
                    if (input.keyCode == KeyCode.Space) jump();
                }
                input.Use();
            }
            if (wrapped == null) wrapped = new GUIStyle(GUI.skin.label) { wordWrap = true };
            GUILayout.BeginArea(new Rect(12, 12, 370, Mathf.Min(390, Screen.height - 24)), GUI.skin.box);
            GUILayout.Label("COMBINED MAP | PROVISIONAL COLLISION TRAVERSAL");
            GUILayout.Label("WASD walk · Space hop · right-drag look · E door · H recover", wrapped);
            GUILayout.Label(status(), wrapped);
            if (GUILayout.Button("Exercise evacuation door states")) evacuate();
            if (GUILayout.Button("Restart traversal")) restart();
            GUILayout.Label("Connector proxies only. Room floors/art are separate imports. The condenser ladder is not traversable yet.", wrapped);
            GUILayout.EndArea();
            GUI.Label(new Rect(Screen.width / 2f - 5, Screen.height / 2f - 10, 20, 20), "+");
        }
        private void ClearInput() { held.Clear(); movement?.Invoke(Vector2.zero); }
        private void OnApplicationFocus(bool focus) { if (!focus) ClearInput(); }
        private void OnDisable() => ClearInput();
        private void OnDestroy()
        { ClearInput(); movement = null; look = null; jump = null; interact = null; recover = null; evacuate = null; restart = null; status = null; }
    }
}
