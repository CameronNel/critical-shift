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
    }
}
#endif
