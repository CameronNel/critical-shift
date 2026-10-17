using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Content.Editor
{
    /// <summary>Imports rooms baked by sections/facility-assembly/unity/bake_room.py into this project as URP Lit content:
    /// textures with the right import settings, one URP Lit material per materials.json entry, the FBX with those materials remapped,
    /// the room's lights from lights.json, and a prefab per room. Imported files are generated content (Assets/CriticalShift/Content/Rooms,
    /// git-ignored); the room sources and bakes stay in sections/. Menu: Critical Shift > Rooms. Batch mode:
    /// -executeMethod CriticalShift.Content.Editor.BakedRoomImporter.ImportAllBatch [-bakedRooms &lt;folder&gt;]</summary>
    public static class BakedRoomImporter
    {
        public const string RoomsFolder = "Assets/CriticalShift/Content/Rooms";
        const string RenderingFolder = "Assets/CriticalShift/Content/Rendering";
        const string UrpLit = "Universal Render Pipeline/Lit";
        const string UrpAssetType = "UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset, Unity.RenderPipelines.Universal.Runtime";
        const string UrpRendererType = "UnityEngine.Rendering.Universal.UniversalRendererData, Unity.RenderPipelines.Universal.Runtime";
        const string UrpRendererBaseType = "UnityEngine.Rendering.Universal.ScriptableRendererData, Unity.RenderPipelines.Universal.Runtime";
        static readonly string[] CopiedFiles = { "materials.json", "lights.json", "bake_report.json" };

        /// <summary>The bake output folder in this repository: runtime/unity/Assets -> repository root -> sections/facility-assembly/unity.</summary>
        public static string DefaultBakedRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "..", "sections", "facility-assembly", "unity"));

        [MenuItem("Critical Shift/Rooms/Set Up URP")]
        public static void SetUpUrpMenu() => SetUpUrp(out _);

        [MenuItem("Critical Shift/Rooms/Import All Baked Rooms")]
        public static void ImportAllMenu()
        {
            if (!SetUpUrp(out string problem)) { Report("URP is not ready", problem); return; }
            var rooms = FindBakedRooms(DefaultBakedRoot);
            if (rooms.Count == 0) { Report("No baked rooms", "None found under " + DefaultBakedRoot + " (a room folder has materials.json, <room>.fbx and textures/)."); return; }
            Report("Imported rooms", ImportRooms(rooms));
        }

        [MenuItem("Critical Shift/Rooms/Import One Baked Room...")]
        public static void ImportOneMenu()
        {
            string folder = EditorUtility.OpenFolderPanel("Baked room folder (contains materials.json)", DefaultBakedRoot, "");
            if (string.IsNullOrEmpty(folder)) return;
            if (!SetUpUrp(out string problem)) { Report("URP is not ready", problem); return; }
            if (!IsBakedRoom(folder)) { Report("Not a baked room", folder + " needs materials.json, " + Path.GetFileName(folder) + ".fbx and textures/."); return; }
            Report("Imported room", ImportRooms(new List<string> { folder }));
        }

        public const string MapFolder = RoomsFolder + "/map";

        /// <summary>The map bake (bake_all.ps1 -Map) in this repository: sections/facility-assembly/unity/map.</summary>
        public static string DefaultBakedMap => Path.Combine(DefaultBakedRoot, "map");

        [MenuItem("Critical Shift/Rooms/Import Baked Map (all rooms in place)")]
        public static void ImportMapMenu()
        {
            if (!SetUpUrp(out string problem)) { Report("URP is not ready", problem); return; }
            Report("Imported map", ImportMap(DefaultBakedMap, out _));
        }

        /// <summary>Batch: -executeMethod CriticalShift.Content.Editor.BakedRoomImporter.ImportMapBatch [-bakedMap &lt;folder&gt;]</summary>
        public static void ImportMapBatch()
        {
            string[] args = Environment.GetCommandLineArgs();
            int k = Array.IndexOf(args, "-bakedMap");
            string root = k >= 0 && k + 1 < args.Length ? args[k + 1] : DefaultBakedMap;
            if (!SetUpUrp(out string problem)) { Debug.LogError(problem); EditorApplication.Exit(2); return; }
            string summary = ImportMap(root, out bool ok);
            Debug.Log(summary);
            EditorApplication.Exit(ok ? 0 : 1);
        }

        /// <summary>Imports every room baked from the combined map (unity/map/&lt;room&gt;) and builds one scene, Content/Rooms/map/CriticalShift_Map.unity,
        /// with each room prefab where map_placement.json (map_placement.py, read from combined_map.blend) puts it.</summary>
        static string ImportMap(string root, out bool ok)
        {
            ok = false;
            string placementFile = Path.Combine(root, "map_placement.json");
            if (!File.Exists(placementFile)) return "No map_placement.json in " + root + ". Pull the repository, or run map_placement.py on the combined map.";
            var placement = (Dictionary<string, object>)((Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(placementFile)))["rooms"];
            var rooms = FindBakedRooms(root);
            if (rooms.Count == 0) return "No map bakes under " + root + ". Bake them with bake_all.ps1 -Map.";
            string summary = ImportRooms(rooms, MapFolder);
            ok = !summary.Contains("FAILED");

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var mapRoot = new GameObject("CriticalShift_Map");
            var placed = new List<string>();
            var unplaced = new List<string>();
            foreach (string source in rooms)
            {
                string room = Path.GetFileName(source.TrimEnd('/', '\\'));
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(MapFolder + "/" + room + "/" + room + ".prefab");
                if (prefab == null || !placement.TryGetValue(room, out object p)) { unplaced.Add(room); continue; }
                var entry = (Dictionary<string, object>)p;
                var loc = (List<object>)entry["location"];
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, mapRoot.transform);
                go.transform.localPosition = BlenderToUnity.Point((double)loc[0], (double)loc[1], (double)loc[2]);
                go.transform.localRotation = BlenderToUnity.MapYaw(Num(entry, "rotation_z_deg", 0.0));
                placed.Add(room);
            }
            var missing = placement.Keys.Where(r => !placed.Contains(r)).ToList();
            string scenePath = MapFolder + "/CriticalShift_Map.unity";
            EditorSceneManager.SaveScene(scene, scenePath);
            summary += "\nScene " + scenePath + ": " + placed.Count + " pieces placed";
            if (missing.Count > 0) summary += "; not baked: " + string.Join(", ", missing);
            if (unplaced.Count > 0) { summary += "; NOT PLACED (no prefab or no placement): " + string.Join(", ", unplaced); ok = false; }
            return summary;
        }

        /// <summary>Batch entry point. Exits non-zero when URP is missing, no room is found or any room fails.</summary>
        public static void ImportAllBatch()
        {
            string[] args = Environment.GetCommandLineArgs();
            int k = Array.IndexOf(args, "-bakedRooms");
            string root = k >= 0 && k + 1 < args.Length ? args[k + 1] : DefaultBakedRoot;
            if (!SetUpUrp(out string problem)) { Debug.LogError(problem); EditorApplication.Exit(2); return; }
            var rooms = FindBakedRooms(root);
            if (rooms.Count == 0) { Debug.LogError("No baked rooms under " + root); EditorApplication.Exit(3); return; }
            string summary = ImportRooms(rooms);
            Debug.Log(summary);
            EditorApplication.Exit(summary.Contains("FAILED") ? 1 : 0);
        }

        // ---------------------------------------------------------------------------------------------------------------------------
        // URP: the project must have the package (installed by the owner in Package Manager) and a pipeline asset in use.

        /// <summary>Checks URP is installed, creates and assigns a pipeline asset if none is in use, and switches the project to Linear colour.</summary>
        public static bool SetUpUrp(out string problem)
        {
            problem = null;
            if (Shader.Find(UrpLit) == null || Type.GetType(UrpAssetType) == null)
            {
                problem = "Universal RP is not installed. Window > Package Manager > Unity Registry > Universal RP > Install, then run this again.";
                return false;
            }
            if (PlayerSettings.colorSpace != ColorSpace.Linear)
            {
                PlayerSettings.colorSpace = ColorSpace.Linear;
                Debug.Log("[Rooms] Player colour space set to Linear (URP and the baked maps expect it).");
            }
            var assetType = Type.GetType(UrpAssetType);
            if (GraphicsSettings.defaultRenderPipeline != null && assetType.IsInstanceOfType(GraphicsSettings.defaultRenderPipeline)) return true;
            try
            {
                Directory.CreateDirectory(RenderingFolder);
                AssetDatabase.Refresh();
                string assetPath = RenderingFolder + "/CriticalShift_URP.asset", rendererPath = RenderingFolder + "/CriticalShift_URP_Renderer.asset";
                var pipeline = AssetDatabase.LoadAssetAtPath<RenderPipelineAsset>(assetPath);
                if (pipeline == null)
                {
                    var renderer = ScriptableObject.CreateInstance(Type.GetType(UrpRendererType, true));
                    AssetDatabase.CreateAsset(renderer, rendererPath);
                    MethodInfo create = assetType.GetMethod("Create", BindingFlags.Public | BindingFlags.Static, null, new[] { Type.GetType(UrpRendererBaseType, true) }, null);
                    pipeline = (RenderPipelineAsset)create.Invoke(null, new object[] { renderer });
                    AssetDatabase.CreateAsset(pipeline, assetPath);
                    AssetDatabase.SaveAssets();
                }
                GraphicsSettings.defaultRenderPipeline = pipeline;
                for (int level = 0; level < QualitySettings.names.Length; level++)
                {
                    QualitySettings.SetQualityLevel(level, false);
                    if (QualitySettings.renderPipeline != null && !assetType.IsInstanceOfType(QualitySettings.renderPipeline)) QualitySettings.renderPipeline = null;
                }
                Debug.Log("[Rooms] URP pipeline asset created and assigned: " + assetPath + ". Tune it per sections/facility-assembly/unity/URP_SETTINGS.md.");
                return true;
            }
            catch (Exception e)
            {
                problem = "URP is installed but its pipeline asset could not be created automatically (" + e.GetBaseException().Message + "). " +
                          "Create one: Assets > Create > Rendering > URP Asset (with Universal Renderer), then Edit > Project Settings > Graphics > " +
                          "Default Render Pipeline = that asset. Then run this again.";
                return false;
            }
        }

        // ---------------------------------------------------------------------------------------------------------------------------
        // Rooms

        public static bool IsBakedRoom(string folder)
        {
            string room = Path.GetFileName(folder.TrimEnd('/', '\\'));
            return File.Exists(Path.Combine(folder, "materials.json")) && File.Exists(Path.Combine(folder, room + ".fbx")) && Directory.Exists(Path.Combine(folder, "textures"));
        }

        public static List<string> FindBakedRooms(string root) =>
            Directory.Exists(root) ? Directory.GetDirectories(root).Where(IsBakedRoom).OrderBy(d => d, StringComparer.Ordinal).ToList() : new List<string>();

        static string ImportRooms(List<string> sources, string destRoot = RoomsFolder)
        {
            var lines = new StringBuilder();
            foreach (string source in sources)
            {
                string room = Path.GetFileName(source.TrimEnd('/', '\\'));
                try
                {
                    EditorUtility.DisplayProgressBar("Importing baked rooms", room, (float)sources.IndexOf(source) / sources.Count);
                    lines.AppendLine(ImportRoom(source, destRoot));
                }
                catch (Exception e)
                {
                    Debug.LogException(e);
                    lines.AppendLine(room + ": FAILED: " + e.GetBaseException().Message);
                }
            }
            EditorUtility.ClearProgressBar();
            AssetDatabase.SaveAssets();
            return lines.ToString().TrimEnd();
        }

        static string ImportRoom(string source, string destRoot)
        {
            string room = Path.GetFileName(source.TrimEnd('/', '\\'));
            string dest = destRoot + "/" + room;
            int copied = CopyRoom(source, dest);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);   // textures and FBX import here, with RoomAssetPostprocessor's settings

            var manifest = (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(Path.Combine(dest, "materials.json")));
            var entries = (Dictionary<string, object>)manifest["materials"];
            var materials = new Dictionary<string, Material>();
            foreach (var pair in entries) materials[pair.Key] = BuildMaterial(dest, pair.Key, (Dictionary<string, object>)pair.Value);

            string fbx = dest + "/" + room + ".fbx";
            int remapped = RemapMaterials(fbx, materials, out List<string> unmatched);
            int lights = 0;
            string prefab = BuildPrefab(room, fbx, Path.Combine(dest, "lights.json"), dest, ref lights);
            string line = string.Format("{0}: {1} files copied, {2} materials ({3} remapped in the FBX), {4} lights, prefab {5}",
                                        room, copied, materials.Count, remapped, lights, prefab);
            if (unmatched.Count > 0) line += "; FBX materials with no manifest entry: " + string.Join(", ", unmatched);
            return line;
        }

        /// <summary>Copies what Unity needs (FBX, textures, manifests) and skips the bake's working files; unchanged files are not copied again.</summary>
        static int CopyRoom(string source, string dest)
        {
            var files = new List<string> { Path.Combine(source, Path.GetFileName(source.TrimEnd('/', '\\')) + ".fbx") };
            files.AddRange(CopiedFiles.Select(f => Path.Combine(source, f)).Where(File.Exists));
            files.AddRange(Directory.GetFiles(Path.Combine(source, "textures"), "*.png"));
            int copied = 0;
            Directory.CreateDirectory(Path.Combine(dest, "textures"));
            foreach (string file in files)
            {
                string rel = file.Substring(source.TrimEnd('/', '\\').Length + 1);
                string target = Path.Combine(dest, rel);
                var a = new FileInfo(file);
                var b = new FileInfo(target);
                if (b.Exists && b.Length == a.Length && b.LastWriteTimeUtc >= a.LastWriteTimeUtc) continue;
                File.Copy(file, target, true);
                copied++;
            }
            return copied;
        }

        // ---------------------------------------------------------------------------------------------------------------------------
        // Materials (URP Lit). Keywords are set here because no material inspector runs on script-made materials.

        static Material BuildMaterial(string dest, string name, Dictionary<string, object> e)
        {
            Directory.CreateDirectory(dest + "/Materials");
            string path = dest + "/Materials/" + SafeName(name) + ".mat";
            var shader = Shader.Find(UrpLit);
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            bool isNew = mat == null;
            if (isNew) mat = new Material(shader);
            mat.shader = shader;
            mat.name = SafeName(name);
            mat.shaderKeywords = new string[0];
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", 0.5f);
            mat.SetFloat("_SmoothnessTextureChannel", 0f);   // smoothness from the metallic map's alpha
            mat.SetFloat("_BumpScale", 1f);
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;

            if (e.ContainsKey("_BaseMap"))
            {
                mat.SetTexture("_BaseMap", Texture(dest, e, "_BaseMap"));
                mat.SetTexture("_MetallicGlossMap", Texture(dest, e, "_MetallicGlossMap"));
                mat.EnableKeyword("_METALLICSPECGLOSSMAP");
                mat.SetFloat("_Smoothness", 1f);               // URP multiplies the map's alpha by this
                mat.SetTexture("_BumpMap", Texture(dest, e, "_BumpMap"));
                mat.EnableKeyword("_NORMALMAP");
                if (e.ContainsKey("_EmissionMap"))
                {
                    mat.SetTexture("_EmissionMap", Texture(dest, e, "_EmissionMap"));
                    float k = Num(e, "_EmissionColor_intensity", 1.0);
                    mat.SetColor("_EmissionColor", BlenderToUnity.LinearColor(k, k, k));
                    mat.EnableKeyword("_EMISSION");
                    mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                }
            }
            else
            {
                var c = (List<object>)e["_BaseColor"];
                bool transparent = e.TryGetValue("_Surface", out object surface) && (string)surface == "Transparent";
                double alpha = transparent ? (e.ContainsKey("_Alpha") ? Num(e, "_Alpha", 0.25) : 0.25) : 1.0;
                mat.SetColor("_BaseColor", BlenderToUnity.LinearColor((double)c[0], (double)c[1], (double)c[2], alpha));
                mat.SetFloat("_Metallic", Num(e, "_Metallic", 0.0));
                mat.SetFloat("_Smoothness", Num(e, "_Smoothness", 0.5));
                if (e.TryGetValue("_EmissionColor", out object em) && Num(e, "_EmissionColor_intensity", 0.0) > 0)
                {
                    var ec = (List<object>)em;
                    double k = Num(e, "_EmissionColor_intensity", 0.0);
                    mat.SetColor("_EmissionColor", BlenderToUnity.LinearColor((double)ec[0] * k, (double)ec[1] * k, (double)ec[2] * k));
                    mat.EnableKeyword("_EMISSION");
                    mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                }
                if (transparent) MakeTransparent(mat);
            }
            if (!mat.IsKeywordEnabled("_SURFACE_TYPE_TRANSPARENT")) MakeOpaque(mat);
            if (isNew) AssetDatabase.CreateAsset(mat, path); else EditorUtility.SetDirty(mat);
            return mat;
        }

        static void MakeOpaque(Material mat)
        {
            mat.SetFloat("_Surface", 0f);
            mat.SetFloat("_SrcBlend", (float)BlendMode.One);
            mat.SetFloat("_DstBlend", (float)BlendMode.Zero);
            mat.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
            mat.SetFloat("_DstBlendAlpha", (float)BlendMode.Zero);
            mat.SetFloat("_ZWrite", 1f);
            mat.SetOverrideTag("RenderType", "Opaque");
            mat.renderQueue = -1;
            mat.SetShaderPassEnabled("DepthOnly", true);
            mat.SetShaderPassEnabled("ShadowCaster", true);
        }

        static void MakeTransparent(Material mat)
        {
            mat.SetFloat("_Surface", 1f);
            mat.SetFloat("_Blend", 0f);
            mat.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            mat.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            mat.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
            mat.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
            mat.SetFloat("_ZWrite", 0f);
            mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            mat.SetOverrideTag("RenderType", "Transparent");
            mat.renderQueue = (int)RenderQueue.Transparent;
            mat.SetShaderPassEnabled("DepthOnly", false);
            mat.SetShaderPassEnabled("ShadowCaster", false);
        }

        static Texture2D Texture(string dest, Dictionary<string, object> e, string key)
        {
            string path = dest + "/" + ((string)e[key]).Replace('\\', '/');
            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (tex == null) throw new FileNotFoundException("Texture listed in materials.json is missing", path);
            return tex;
        }

        static float Num(Dictionary<string, object> e, string key, double fallback) =>
            (float)(e.TryGetValue(key, out object v) && v is double d ? d : fallback);

        /// <summary>The bake's file-name rule (bake_room.py fname): each of &lt; &gt; : " / \ | ? * and whitespace becomes '_'.</summary>
        public static string SafeName(string name)
        {
            var sb = new StringBuilder(name.Length);
            foreach (char ch in name) sb.Append("<>:\"/\\|?*".IndexOf(ch) >= 0 || char.IsWhiteSpace(ch) ? '_' : ch);
            return sb.ToString();
        }

        /// <summary>The bake exports each material as "U_" + its source name. Remaps those FBX materials to the URP materials and reimports.</summary>
        static int RemapMaterials(string fbx, Dictionary<string, Material> materials, out List<string> unmatched)
        {
            unmatched = new List<string>();
            var importer = (ModelImporter)AssetImporter.GetAtPath(fbx);
            if (importer == null) throw new InvalidOperationException("FBX did not import: " + fbx);
            var byNormalised = materials.ToDictionary(p => Normalise(p.Key), p => p.Value);
            var embedded = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<Material>().Select(m => m.name).Distinct().ToList();
            foreach (var existing in importer.GetExternalObjectMap().Keys.Where(k => k.type == typeof(Material)).Select(k => k.name)) if (!embedded.Contains(existing)) embedded.Add(existing);
            int remapped = 0;
            foreach (string source in embedded)
            {
                string key = source.StartsWith("U_", StringComparison.Ordinal) ? source.Substring(2) : source;
                if (!materials.TryGetValue(key, out Material mat) && !byNormalised.TryGetValue(Normalise(key), out mat)) { unmatched.Add(source); continue; }
                importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), source), mat);
                remapped++;
            }
            importer.SaveAndReimport();
            return remapped;
        }

        static string Normalise(string s) => new string(s.Where(char.IsLetterOrDigit).Select(char.ToLowerInvariant).ToArray());

        // ---------------------------------------------------------------------------------------------------------------------------
        // Prefab: the room model (static for GI and occlusion) plus its lights, at the room's own module origin.

        const StaticEditorFlags RoomStatic = StaticEditorFlags.ContributeGI | StaticEditorFlags.OccluderStatic | StaticEditorFlags.OccludeeStatic |
                                             StaticEditorFlags.ReflectionProbeStatic;   // no BatchingStatic: the GPU Resident Drawer replaces it (URP_SETTINGS.md)

        static string BuildPrefab(string room, string fbx, string lightsJson, string dest, ref int lightCount)
        {
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            var root = new GameObject(room);
            try
            {
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, root.transform);
                foreach (Transform t in instance.GetComponentsInChildren<Transform>(true)) GameObjectUtility.SetStaticEditorFlags(t.gameObject, RoomStatic);
                if (File.Exists(lightsJson))
                {
                    var lightsRoot = new GameObject("Lights");
                    lightsRoot.transform.SetParent(root.transform, false);
                    var data = (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(lightsJson));
                    foreach (var o in (List<object>)data["lights"]) { AddLight(lightsRoot.transform, (Dictionary<string, object>)o); lightCount++; }
                }
                string path = dest + "/" + room + ".prefab";
                PrefabUtility.SaveAsPrefabAsset(root, path, out bool ok);
                if (!ok) throw new InvalidOperationException("Prefab could not be saved: " + path);
                return path;
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        static void AddLight(Transform parent, Dictionary<string, object> l)
        {
            var go = new GameObject((string)l["name"]);
            go.transform.SetParent(parent, false);
            var p = (List<object>)l["location"];
            var r = (List<object>)l["rotation_euler_deg"];
            var c = (List<object>)l["color"];
            go.transform.localPosition = BlenderToUnity.Point((double)p[0], (double)p[1], (double)p[2]);
            go.transform.localRotation = BlenderToUnity.LightRotation((double)r[0], (double)r[1], (double)r[2]);
            var light = go.AddComponent<Light>();
            light.color = BlenderToUnity.LinearColor((double)c[0], (double)c[1], (double)c[2]);
            light.shadows = l.TryGetValue("shadow", out object s) && s is bool b && b ? LightShadows.Soft : LightShadows.None;
            double watts = Num(l, "energy_blender", 0.0);
            switch ((string)l["type"])
            {
                case "AREA":
                    var size = (List<object>)l["size"];
                    double sx = (double)size[0], sy = size.Count > 1 ? (double)size[1] : sx;
                    string shape = l.TryGetValue("shape", out object sh) ? (string)sh : "SQUARE";
                    bool disc = shape == "DISK" || shape == "ELLIPSE";
                    if (shape == "SQUARE" || shape == "DISK") sy = sx;
                    double area = disc ? Math.PI * sx * sy / 4.0 : sx * sy;
                    light.type = disc ? LightType.Disc : LightType.Rectangle;
                    light.areaSize = disc ? new Vector2((float)(sx / 2.0), (float)(sx / 2.0)) : new Vector2((float)sx, (float)sy);
                    light.intensity = BlenderToUnity.AreaIntensity(watts, area);
                    light.lightmapBakeType = LightmapBakeType.Baked;   // URP has no realtime area lights
                    break;
                case "SPOT":
                    light.type = LightType.Spot;
                    float angle = Num(l, "spot_angle_deg", 45.0);
                    light.spotAngle = angle;
                    light.innerSpotAngle = angle * (1f - Num(l, "spot_blend", 0.15));
                    light.intensity = BlenderToUnity.PointIntensity(watts);
                    light.range = BlenderToUnity.Range(light.intensity);
                    light.lightmapBakeType = LightmapBakeType.Mixed;
                    break;
                case "SUN":
                    light.type = LightType.Directional;
                    light.intensity = BlenderToUnity.SunIntensity(watts);
                    light.lightmapBakeType = LightmapBakeType.Mixed;
                    break;
                default:
                    light.type = LightType.Point;
                    light.intensity = BlenderToUnity.PointIntensity(watts);
                    light.range = BlenderToUnity.Range(light.intensity);
                    light.lightmapBakeType = LightmapBakeType.Mixed;
                    break;
            }
        }

        static void Report(string title, string body)
        {
            Debug.Log("[Rooms] " + title + "\n" + body);
            if (!Application.isBatchMode) EditorUtility.DisplayDialog(title, body.Length > 1500 ? body.Substring(0, 1500) + "\n... (full text in the Console)" : body, "OK");
        }
    }
}
