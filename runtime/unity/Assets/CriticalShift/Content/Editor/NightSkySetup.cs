using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CriticalShift.Content.Editor
{
    /// <summary>Import settings for the night sky's textures, and the menu that puts the sky into the open scene. See Content/Sky/README.md.</summary>
    public sealed class NightSkyTexturePostprocessor : AssetPostprocessor
    {
        internal const string Folder = "Assets/CriticalShift/Content/Sky/Textures/";

        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Folder, StringComparison.Ordinal)) return;
            var importer = (TextureImporter)assetImporter;
            string name = System.IO.Path.GetFileNameWithoutExtension(assetPath);
            importer.textureType = TextureImporterType.Default;
            importer.mipmapEnabled = true;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
            importer.alphaSource = TextureImporterAlphaSource.None;
            if (name == "NightSky_Stars" || name == "NightSky_MilkyWay")
            {
                // Equirectangular in, cubemap out: no seam and no pole pinch. Faces are a quarter of the width (2048 and 1024).
                importer.textureShape = TextureImporterShape.TextureCube;
                importer.generateCubemap = TextureImporterGenerateCubemap.Cylindrical;
                importer.sRGBTexture = true;
                importer.filterMode = FilterMode.Trilinear;
                importer.maxTextureSize = name == "NightSky_Stars" ? 8192 : 4096;
            }
            else
            {
                importer.textureShape = TextureImporterShape.Texture2D;
                importer.sRGBTexture = name != "NightSky_MoonNormal";   // the normals are data, read as linear
                importer.wrapModeU = TextureWrapMode.Repeat;
                importer.wrapModeV = TextureWrapMode.Clamp;
                importer.filterMode = FilterMode.Trilinear;
                importer.anisoLevel = 4;
                importer.maxTextureSize = 2048;
            }
        }
    }

    public static class NightSkySetup
    {
        const string MaterialPath = "Assets/CriticalShift/Content/Sky/NightSky.mat";
        const string ComponentType = "CriticalShift.Presentation.NightSky, CriticalShift.Presentation";

        [MenuItem("Critical Shift/Environment/Set Up Night Sky")]
        public static void SetUp()
        {
            var shader = Shader.Find("CriticalShift/NightSky");
            var component = Type.GetType(ComponentType);
            if (shader == null || component == null)
            {
                EditorUtility.DisplayDialog("Night sky", "The CriticalShift/NightSky shader or the NightSky component is missing or failed to compile. Check the Console.", "OK");
                return;
            }

            var material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "NightSky" };
                AssetDatabase.CreateAsset(material, MaterialPath);
            }
            material.shader = shader;
            Assign(material, "_StarCube", AssetDatabase.LoadAssetAtPath<Cubemap>(NightSkyTexturePostprocessor.Folder + "NightSky_Stars.png"));
            Assign(material, "_MilkyWayCube", AssetDatabase.LoadAssetAtPath<Cubemap>(NightSkyTexturePostprocessor.Folder + "NightSky_MilkyWay.png"));
            Assign(material, "_MoonColor", AssetDatabase.LoadAssetAtPath<Texture2D>(NightSkyTexturePostprocessor.Folder + "NightSky_MoonColor.png"));
            Assign(material, "_MoonNormal", AssetDatabase.LoadAssetAtPath<Texture2D>(NightSkyTexturePostprocessor.Folder + "NightSky_MoonNormal.png"));
            EditorUtility.SetDirty(material);
            AssetDatabase.SaveAssets();

            var existing = UnityEngine.Object.FindObjectsByType(component, FindObjectsInactive.Include);
            var sky = existing.Length > 0 ? (Component)existing[0] : null;
            if (sky == null)
            {
                var go = new GameObject("Night Sky");
                Undo.RegisterCreatedObjectUndo(go, "Set Up Night Sky");
                var light = go.AddComponent<Light>();
                light.type = LightType.Directional;
                light.shadows = LightShadows.Soft;
                light.shadowStrength = 0.85f;
                sky = go.AddComponent(component);
                var so = new SerializedObject(sky);
                so.FindProperty("moonLight").objectReferenceValue = light;
                so.ApplyModifiedPropertiesWithoutUndo();
            }
            var serialized = new SerializedObject(sky);
            serialized.FindProperty("skyMaterial").objectReferenceValue = material;
            serialized.ApplyModifiedProperties();
            RenderSettings.skybox = material;
            EditorSceneManager.MarkSceneDirty(sky.gameObject.scene);
            Selection.activeGameObject = sky.gameObject;
            Debug.Log("Night sky set up in " + sky.gameObject.scene.name + ": " + MaterialPath + " and the Night Sky object (moonlight). Save the scene to keep it.");
        }

        static void Assign(Material material, string property, Texture texture)
        {
            if (texture == null) Debug.LogError("Night sky: " + property + " texture not found under " + NightSkyTexturePostprocessor.Folder + " (git lfs pull?).");
            else material.SetTexture(property, texture);
        }
    }
}
