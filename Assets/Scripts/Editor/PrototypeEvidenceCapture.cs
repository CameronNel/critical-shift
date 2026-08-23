#if UNITY_EDITOR
using System.IO;
using CriticalShift.Prototype;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CriticalShift.Editor
{
    public static class PrototypeEvidenceCapture
    {
        public static void CaptureShoeboxCommandLine()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            new GameObject("Capture Director").AddComponent<PrototypeGameDirector>();
            var player = new GameObject("Capture Player");
            player.transform.position = new Vector3(-12f, .1f, -7f);
            player.AddComponent<CharacterController>();
            player.AddComponent<PrototypePlayerController>();
            foreach (var existing in Object.FindObjectsByType<Camera>(FindObjectsSortMode.None)) existing.enabled = false;

            var runtime = new GameObject("Capture Runtime").AddComponent<PrototypeShoeboxRuntime>();
            runtime.Build(Vector3.zero);

            var light = new GameObject("Capture Sun").AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            light.shadows = LightShadows.Soft;
            light.transform.rotation = Quaternion.Euler(52f, -38f, 0f);

            var camera = new GameObject("Evidence Camera").AddComponent<Camera>();
            camera.transform.position = new Vector3(0f, 18f, -20f);
            camera.transform.LookAt(new Vector3(0f, 0f, 0f));
            camera.fieldOfView = 54f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(.035f, .055f, .07f);

            var renderTexture = new RenderTexture(960, 540, 24);
            var previous = RenderTexture.active;
            camera.targetTexture = renderTexture;
            camera.Render();
            RenderTexture.active = renderTexture;
            var image = new Texture2D(960, 540, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, 960, 540), 0, 0);
            image.Apply();
            var path = Path.GetFullPath("Assets/Screenshots/radioactive_shoebox_overview.png");
            File.WriteAllBytes(path, image.EncodeToPNG());
            camera.targetTexture = null;
            RenderTexture.active = previous;
            Object.DestroyImmediate(image);
            Object.DestroyImmediate(renderTexture);
            AssetDatabase.ImportAsset("Assets/Screenshots/radioactive_shoebox_overview.png", ImportAssetOptions.ForceUpdate);
            AssetDatabase.SaveAssets();
            Debug.Log("[CriticalShift] Captured radioactive shoebox evidence to " + path);
        }

        public static void CaptureFacilityCommandLine()
        {
            EditorSceneManager.OpenScene("Assets/Scenes/FacilityGreybox.unity", OpenSceneMode.Single);
            QualitySettings.SetQualityLevel(0, true);
            QualitySettings.shadows = ShadowQuality.Disable;
            QualitySettings.antiAliasing = 0;
            QualitySettings.shadowDistance = 0f;

            if (PrototypeGameDirector.Instance == null)
                new GameObject("Facility Capture Director").AddComponent<PrototypeGameDirector>();
            if (Object.FindAnyObjectByType<PrototypePlayerController>() == null)
            {
                var player = new GameObject("Facility Capture Player");
                player.transform.position = new Vector3(-72f, .06f, -40.2f);
                player.AddComponent<CharacterController>();
                player.AddComponent<PrototypePlayerController>();
            }
            if (PrototypeFacilityRuntime.Instance == null)
                new GameObject("Facility Capture Runtime").AddComponent<PrototypeFacilityRuntime>().Build();

            foreach (var existing in Object.FindObjectsByType<Camera>()) existing.enabled = false;
            foreach (var existing in Object.FindObjectsByType<Light>()) existing.shadows = LightShadows.None;

            var light = new GameObject("Facility Capture Sun").AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = .75f;
            light.shadows = LightShadows.None;
            light.transform.rotation = Quaternion.Euler(48f, -32f, 0f);
            RenderSettings.ambientLight = new Color(.2f, .23f, .27f);

            var camera = new GameObject("Facility Evidence Camera").AddComponent<Camera>();
            camera.allowHDR = false;
            camera.allowMSAA = false;
            camera.useOcclusionCulling = false;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(.035f, .055f, .07f);
            camera.nearClipPlane = .1f;
            camera.farClipPlane = 400f;

            var overview = GameObject.Find("Overview_Camera")?.GetComponent<Camera>();
            if (overview != null)
                Capture(camera, "full_shift_overview.png", overview.transform.position,
                    overview.transform.position + overview.transform.forward * 100f, overview.fieldOfView);
            CaptureIsolatedModel(camera, "full_shift_gullet_model.png",
                "Assets/Models/GulletMine/GulletMine_StylizedLowPoly.fbx", new Vector3(1f, .35f, -.8f));
            CaptureIsolatedModel(camera, "full_shift_reactor_model.png",
                "Assets/Models/ReactorPool/ReactorPool_StylizedLowPoly.fbx", new Vector3(1f, .45f, -1f));
            AssetDatabase.SaveAssets();
            Debug.Log("[CriticalShift] Captured full authored shift evidence under Assets/Screenshots/full_shift_*.png");
        }

        static void Capture(Camera camera, string filename, Vector3 position, Vector3 target, float fieldOfView)
        {
            camera.transform.position = position;
            camera.transform.LookAt(target);
            camera.fieldOfView = fieldOfView;
            var renderTexture = new RenderTexture(960, 540, 24);
            var previous = RenderTexture.active;
            camera.targetTexture = renderTexture;
            camera.Render();
            RenderTexture.active = renderTexture;
            var image = new Texture2D(960, 540, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, 960, 540), 0, 0);
            image.Apply();
            string assetPath = "Assets/Screenshots/" + filename;
            File.WriteAllBytes(Path.GetFullPath(assetPath), image.EncodeToPNG());
            camera.targetTexture = null;
            RenderTexture.active = previous;
            Object.DestroyImmediate(image);
            Object.DestroyImmediate(renderTexture);
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);
        }

        static void CaptureIsolatedModel(Camera camera, string filename, string assetPath, Vector3 viewDirection)
        {
            var enabledRenderers = Object.FindObjectsByType<Renderer>();
            foreach (var renderer in enabledRenderers) renderer.enabled = false;
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
            if (prefab == null) { Debug.LogError("[CriticalShift] Missing capture model: " + assetPath); return; }
            var instance = Object.Instantiate(prefab);
            instance.name = "Evidence Model " + prefab.name;
            var renderers = instance.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) { Object.DestroyImmediate(instance); return; }
            var visible = new System.Collections.Generic.List<Renderer>();
            foreach (var renderer in renderers)
            {
                bool hide = renderer.name == "SafetyFloor" ||
                    (prefab.name.Contains("Reactor") &&
                     (renderer.name.Contains("WallPanel") || renderer.name.Contains("CeilingDeck")));
                renderer.enabled = !hide;
                if (!hide) visible.Add(renderer);
            }
            if (visible.Count == 0) { Object.DestroyImmediate(instance); return; }
            var bounds = visible[0].bounds;
            foreach (var renderer in visible) bounds.Encapsulate(renderer.bounds);
            float fieldOfView = 50f;
            float radius = Mathf.Max(1f, bounds.extents.magnitude);
            float distance = radius / Mathf.Tan(fieldOfView * .5f * Mathf.Deg2Rad) * 1.25f;
            Vector3 direction = viewDirection.normalized;
            Vector3 position = bounds.center + direction * distance;
            camera.farClipPlane = Mathf.Max(400f, distance + radius * 4f);
            Capture(camera, filename, position, bounds.center, fieldOfView);
            Object.DestroyImmediate(instance);
            foreach (var renderer in enabledRenderers) if (renderer != null) renderer.enabled = true;
        }
    }
}
#endif
