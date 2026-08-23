using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Runtime-only bootstrap binds the prototype loop to the authored facility while
    /// retaining a tiny fallback arena for isolated script/test scenes.
    public sealed class PrototypeBootstrap : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Create()
        {
            if (FindAnyObjectByType<PrototypeBootstrap>() == null)
                new GameObject("PrototypeRuntime").AddComponent<PrototypeBootstrap>();
        }

        void Awake()
        {
            if (FindAnyObjectByType<PrototypeGameDirector>() == null)
                new GameObject("ShiftDirector").AddComponent<PrototypeGameDirector>();
            if (FindAnyObjectByType<PrototypeHUD>() == null)
                new GameObject("PrototypeHUD").AddComponent<PrototypeHUD>();

            DisableAuthoringCameras();
            bool hasAuthoredFacility = GameObject.Find("[MACHINE] BRIEFING BOARD") != null;
            BuildPlayer(hasAuthoredFacility ? FindSpawnPosition() : new Vector3(0f, 0.05f, 0f),
                hasAuthoredFacility ? 10.5f : 0f);

            if (hasAuthoredFacility) BindAuthoredFacility();
            else BuildFallbackArena();

            if (FindAnyObjectByType<Light>() == null)
            {
                var light = new GameObject("PrototypeLight").AddComponent<Light>();
                light.type = LightType.Directional;
                light.intensity = 0.9f;
            }
        }

        static void DisableAuthoringCameras()
        {
            foreach (var camera in FindObjectsByType<Camera>()) camera.enabled = false;
            foreach (var listener in FindObjectsByType<AudioListener>()) listener.enabled = false;
        }

        static Vector3 FindSpawnPosition()
        {
            // The facility's authored shift-entrance marker sits inside a sealed
            // transition volume. Begin on the briefing dais instead so the first
            // frame is readable and the player can immediately reach the board.
            var board = GameObject.Find("[MACHINE] BRIEFING BOARD");
            if (board != null)
                return new Vector3(board.transform.position.x - 1.5f, 0.06f,
                    board.transform.position.z - 8.16f);

            var spawn = GameObject.Find("[SPAWN] Shift entrance");
            return spawn != null ? spawn.transform.position + Vector3.up * 0.05f : new Vector3(-74.4f, 0.05f, -43.8f);
        }

        static void BuildPlayer(Vector3 position, float yaw)
        {
            var go = new GameObject("PrototypePlayer");
            go.transform.position = position;
            go.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            var character = go.AddComponent<CharacterController>();
            character.height = 1.8f;
            character.radius = 0.35f;
            character.center = new Vector3(0f, 0.9f, 0f);
            character.stepOffset = 0.3f;
            go.AddComponent<PrototypePlayerController>();
        }

        static void BindAuthoredFacility()
        {
            BindStation("[MACHINE] BRIEFING BOARD", PrototypeStation.Briefing, "open the shift briefing");
            BindStation("[MACHINE] ORE LOADER", PrototypeStation.Mine, "load an ore batch");
            BindStation("[MACHINE] PROCESSOR", PrototypeStation.Refinery, "refine one safe fuel batch");
            BindStation("[MACHINE] CONTROL POSITION", PrototypeStation.Reactor, "start the reactor");
            BindStation("[MACHINE] EMERGENCY SHUTDOWN", PrototypeStation.EmergencyCooling, "inject emergency cooling");
        }

        static void BindStation(string objectName, PrototypeStation station, string prompt)
        {
            var go = GameObject.Find(objectName);
            if (go == null)
            {
                Debug.LogWarning($"[PrototypeBootstrap] Authored station not found: {objectName}");
                return;
            }

            var target = go.GetComponent<PrototypeInteractable>();
            if (target == null) target = go.AddComponent<PrototypeInteractable>();
            target.station = station;
            target.prompt = prompt;
        }

        static void BuildFallbackArena()
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "PrototypeFloor";
            floor.transform.position = new Vector3(7.5f, -0.5f, 4f);
            floor.transform.localScale = new Vector3(26f, 1f, 12f);
            BuildFallbackStation("Briefing Console", PrototypeStation.Briefing, new Vector3(0f, 1f, 4f), Color.yellow, "open the shift briefing");
            BuildFallbackStation("Mine Console", PrototypeStation.Mine, new Vector3(5f, 1f, 4f), Color.green, "load an ore batch");
            BuildFallbackStation("Refinery Console", PrototypeStation.Refinery, new Vector3(10f, 1f, 4f), Color.cyan, "refine one safe fuel batch");
            BuildFallbackStation("Reactor Console", PrototypeStation.Reactor, new Vector3(15f, 1f, 4f), Color.red, "start the reactor");
            BuildFallbackStation("Emergency Cooling", PrototypeStation.EmergencyCooling, new Vector3(18f, 1f, 1f), new Color(1f, 0.4f, 0.1f), "inject emergency cooling");
        }

        static void BuildFallbackStation(string name, PrototypeStation station, Vector3 position, Color color, string prompt)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.position = position;
            go.transform.localScale = new Vector3(1.4f, 1.6f, 0.8f);
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            if (shader != null)
            {
                var material = new Material(shader) { color = color };
                go.GetComponent<Renderer>().sharedMaterial = material;
            }
            var target = go.AddComponent<PrototypeInteractable>();
            target.station = station;
            target.prompt = prompt;
        }
    }
}
