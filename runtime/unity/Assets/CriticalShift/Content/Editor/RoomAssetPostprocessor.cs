using System.IO;
using UnityEditor;

namespace CriticalShift.Content.Editor
{
    /// <summary>Import settings for baked room content under Assets/CriticalShift/Content/Rooms, applied on every (re)import so they cannot drift.
    /// Texture roles come from the bake's file names (_BaseMap, _MetallicGlossMap, _BumpMap, _EmissionMap). Values: URP_SETTINGS.md.</summary>
    internal sealed class RoomAssetPostprocessor : AssetPostprocessor
    {
        static bool IsRoomAsset(string path) => path.StartsWith(BakedRoomImporter.RoomsFolder + "/", System.StringComparison.Ordinal);

        void OnPreprocessTexture()
        {
            if (!IsRoomAsset(assetPath)) return;
            var ti = (TextureImporter)assetImporter;
            string name = Path.GetFileNameWithoutExtension(assetPath);
            bool normal = name.EndsWith("_BumpMap"), data = name.EndsWith("_MetallicGlossMap");
            ti.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            ti.sRGBTexture = !(normal || data);                       // metallic (R) and smoothness (A) are data, not colour
            bool baseMap = name.EndsWith("_BaseMap");                 // carries alpha for transparent materials (1 elsewhere)
            ti.alphaSource = data || baseMap ? TextureImporterAlphaSource.FromInput : TextureImporterAlphaSource.None;
            ti.alphaIsTransparency = false;
            ti.mipmapEnabled = true;
            ti.streamingMipmaps = true;
            ti.maxTextureSize = 4096;
            ti.textureCompression = TextureImporterCompression.CompressedHQ;
            var standalone = ti.GetPlatformTextureSettings("Standalone");
            standalone.overridden = true;
            standalone.maxTextureSize = 4096;
            standalone.format = normal ? TextureImporterFormat.BC5 : TextureImporterFormat.BC7;
            ti.SetPlatformTextureSettings(standalone);
        }

        void OnPreprocessModel()
        {
            if (!IsRoomAsset(assetPath)) return;
            var mi = (ModelImporter)assetImporter;
            mi.globalScale = 1f;
            mi.useFileScale = true;
            mi.bakeAxisConversion = true;
            mi.isReadable = false;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.generateSecondaryUV = true;                            // UVBake is uv0 and is not a lightmap layout
            mi.importNormals = ModelImporterNormals.Import;
            mi.importTangents = ModelImporterTangents.CalculateMikk;
            mi.importCameras = false;
            mi.importLights = false;                                  // lights come from lights.json
            mi.importAnimation = false;
            mi.animationType = ModelImporterAnimationType.None;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            mi.materialLocation = ModelImporterMaterialLocation.InPrefab;   // BakedRoomImporter remaps each one to its URP Lit material
        }
    }
}
