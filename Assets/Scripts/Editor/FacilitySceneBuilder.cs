using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace CriticalShift.Editor
{
    public static class FacilitySceneBuilder
    {
        private const string JsonPath = "Assets/Data/facility.json";
        private const string ScenePath = "Assets/Scenes/FacilityGreybox.unity";
        private const string MaterialsFolder = "Assets/Materials/Greybox";

        private static Dictionary<string, Material> s_materials = new Dictionary<string, Material>();
        private static Shader s_defaultShader;

        [MenuItem("Critical Shift/Build Facility Greybox Scene", priority = 10)]
        public static void BuildFacilityScene()
        {
            try
            {
                EditorUtility.DisplayProgressBar("Building Facility", "Loading facility data...", 0.05f);

                string fullJsonPath = Path.Combine(Directory.GetCurrentDirectory(), JsonPath);
                if (!File.Exists(fullJsonPath))
                {
                    Debug.LogError($"[FacilitySceneBuilder] facility.json not found at {fullJsonPath}");
                    return;
                }

                string jsonText = File.ReadAllText(fullJsonPath);
                FacilityData data = JsonUtility.FromJson<FacilityData>(jsonText);

                if (data == null || data.entities == null || data.entities.Length == 0)
                {
                    // Fallback to custom JSON parsing if Unity's JsonUtility has polymorphic limitations
                    data = ParseFacilityData(jsonText);
                }

                EnsureFolders();
                InitMaterials(data.zones);

                // Create new empty scene
                Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

                GameObject rootEnvironment = new GameObject("--- ENVIRONMENT & LIGHTING ---");
                SetupLightingAndCameras(rootEnvironment);

                GameObject rootFacility = new GameObject("--- FACILITY_ZONES ---");
                GameObject rootStations = new GameObject("--- STATIONS & INTERACTABLES ---");
                GameObject rootRoutes = new GameObject("--- ROUTES & TRACKS ---");
                GameObject rootSpawns = new GameObject("--- SPAWN POINTS & MARKERS ---");

                Dictionary<string, Transform> zoneParents = new Dictionary<string, Transform>();
                foreach (var zone in data.zones)
                {
                    GameObject zoneObj = new GameObject($"Zone_{zone.name.ToUpper()}");
                    zoneObj.transform.SetParent(rootFacility.transform);
                    zoneParents[zone.id] = zoneObj.transform;

                    // Zone Header / Marker
                    CreateZoneMarker(zone, zoneObj.transform);
                }

                int total = data.entities.Length;
                for (int i = 0; i < total; i++)
                {
                    var entity = data.entities[i];
                    float progress = 0.1f + 0.8f * ((float)i / total);
                    EditorUtility.DisplayProgressBar("Building Facility", $"Building {entity.id} ({i + 1}/{total})", progress);

                    Transform parent = zoneParents.ContainsKey(entity.zone) ? zoneParents[entity.zone] : rootFacility.transform;

                    BuildEntity(entity, parent, rootStations.transform, rootRoutes.transform, rootSpawns.transform);
                }

                // Routes are authored alongside the greybox data and are the primary
                // wayfinding language for the first playable shift. Keep them as thin,
                // emissive guide rails: readable from the overview camera, inexpensive,
                // and never blocking player movement.
                RouteData[] routes = data.routes != null && data.routes.Length > 0 && data.routes[0] != null && data.routes[0].path != null && data.routes[0].path.Length > 1
                    ? data.routes
                    : ParseRoutes(jsonText);
                BuildRoutes(routes, rootRoutes.transform);

                // Save scene
                EditorSceneManager.SaveScene(scene, ScenePath);
                Debug.Log($"<color=#4CAF50>[FacilitySceneBuilder] Successfully built facility scene at {ScenePath} with {total} entities across {data.zones.Length} zones!</color>");
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
        }

        private static void EnsureFolders()
        {
            if (!AssetDatabase.IsValidFolder("Assets/Scenes")) AssetDatabase.CreateFolder("Assets", "Scenes");
            if (!AssetDatabase.IsValidFolder("Assets/Materials")) AssetDatabase.CreateFolder("Assets", "Materials");
            if (!AssetDatabase.IsValidFolder(MaterialsFolder)) AssetDatabase.CreateFolder("Assets/Materials", "Greybox");
        }

        private static Shader GetShader()
        {
            if (s_defaultShader != null) return s_defaultShader;
            s_defaultShader = Shader.Find("Universal Render Pipeline/Lit");
            if (s_defaultShader == null) s_defaultShader = Shader.Find("Standard");
            if (s_defaultShader == null) s_defaultShader = Shader.Find("Diffuse");
            return s_defaultShader;
        }

        private static void InitMaterials(ZoneData[] zones)
        {
            s_materials.Clear();
            Shader shader = GetShader();

            CreateMaterial("Mat_Floor_Concrete", new Color(0.35f, 0.36f, 0.38f), 0.7f);
            CreateMaterial("Mat_Floor_Grade", new Color(0.26f, 0.28f, 0.26f), 0.8f);
            CreateMaterial("Mat_Wall_Industrial", new Color(0.48f, 0.50f, 0.52f), 0.6f);
            CreateMaterial("Mat_Metal_Catwalk", new Color(0.28f, 0.30f, 0.33f), 0.4f);
            CreateMaterial("Mat_Metal_Machine", new Color(0.22f, 0.24f, 0.26f), 0.3f);
            CreateMaterial("Mat_Hazard_Stripe", new Color(0.95f, 0.75f, 0.10f), 0.5f);
            CreateMaterial("Mat_Emissive_Control", new Color(0.1f, 0.8f, 0.9f), 0.2f, true, new Color(0.1f, 0.8f, 0.9f) * 2f);
            CreateMaterial("Mat_Emissive_Alarm", new Color(0.95f, 0.2f, 0.1f), 0.2f, true, new Color(0.95f, 0.2f, 0.1f) * 3f);
            CreateMaterial("Mat_Rock_Cavern", new Color(0.24f, 0.21f, 0.18f), 0.9f);
            CreateMaterial("Mat_Cart_Track", new Color(0.15f, 0.15f, 0.16f), 0.2f);
            CreateMaterial("Mat_Coolant_Liquid", new Color(0.1f, 0.55f, 0.65f, 0.85f), 0.1f, true, new Color(0.05f, 0.3f, 0.4f));
            CreateMaterial("Mat_Route_Guide", new Color(0.22f, 0.82f, 0.58f), 0.35f, true, new Color(0.22f, 0.82f, 0.58f) * 1.5f);

            if (zones != null)
            {
                foreach (var z in zones)
                {
                    if (ColorUtility.TryParseHtmlString(z.color, out Color c))
                    {
                        CreateMaterial($"Mat_Zone_{z.id}", c, 0.6f);
                    }
                }
            }
        }

        private static Material CreateMaterial(string name, Color color, float roughness, bool emissive = false, Color? emissiveColor = null)
        {
            string path = $"{MaterialsFolder}/{name}.mat";
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(GetShader());
                mat.color = color;
                if (mat.HasProperty("_Roughness")) mat.SetFloat("_Roughness", roughness);
                if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", 1f - roughness);
                if (mat.HasProperty("_Glossiness")) mat.SetFloat("_Glossiness", 1f - roughness);

                if (emissive && emissiveColor.HasValue)
                {
                    mat.EnableKeyword("_EMISSION");
                    if (mat.HasProperty("_EmissionColor")) mat.SetColor("_EmissionColor", emissiveColor.Value);
                }

                AssetDatabase.CreateAsset(mat, path);
            }
            s_materials[name] = mat;
            return mat;
        }

        private static Material GetMaterial(string name, string fallbackZone = null)
        {
            if (s_materials.TryGetValue(name, out Material mat)) return mat;
            if (!string.IsNullOrEmpty(fallbackZone) && s_materials.TryGetValue($"Mat_Zone_{fallbackZone}", out Material zoneMat)) return zoneMat;
            if (s_materials.TryGetValue("Mat_Wall_Industrial", out Material defMat)) return defMat;
            return null;
        }

        private static void SetupLightingAndCameras(GameObject parent)
        {
            // Prototype quality defaults: stable frame time on the target low/mid
            // fidelity hardware. The scene intentionally does not require ray tracing,
            // post-processing, HDR, or high shadow distances to read well.
            QualitySettings.vSyncCount = 0;
            QualitySettings.antiAliasing = 0;
            QualitySettings.shadowDistance = 55f;
            QualitySettings.shadowResolution = ShadowResolution.Low;
            QualitySettings.realtimeReflectionProbes = false;
            QualitySettings.pixelLightCount = 3;

            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;

            // Sea of Thieves-inspired look carried entirely by lighting:
            // saturated golden key, teal ambient gradient, painterly haze,
            // and punchy emissive accents. No geometry detail required.
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.13f, 0.25f, 0.30f);
            RenderSettings.ambientEquatorColor = new Color(0.11f, 0.16f, 0.19f);
            RenderSettings.ambientGroundColor = new Color(0.10f, 0.07f, 0.05f);
            RenderSettings.ambientIntensity = 0.48f;

            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.18f, 0.30f, 0.34f);
            RenderSettings.fogStartDistance = 60f;
            RenderSettings.fogEndDistance = 520f;

            // Procedural sky - deep saturated blue gradient like a Sea of Thieves noon
            Material sky = AssetDatabase.LoadAssetAtPath<Material>($"{MaterialsFolder}/Mat_SoT_Sky.mat");
            if (sky == null)
            {
                Material src = AssetDatabase.GetBuiltinExtraResource<Material>("Default-Skybox.mat");
                if (src != null)
                {
                    sky = new Material(src);
                    AssetDatabase.CreateAsset(sky, $"{MaterialsFolder}/Mat_SoT_Sky.mat");
                }
            }
            if (sky != null)
            {
                if (sky.HasProperty("_AtmosphereThickness")) sky.SetFloat("_AtmosphereThickness", 0.62f);
                if (sky.HasProperty("_Exposure")) sky.SetFloat("_Exposure", 0.78f);
                if (sky.HasProperty("_SunSize")) sky.SetFloat("_SunSize", 0.045f);
                if (sky.HasProperty("_SkyTint")) sky.SetColor("_SkyTint", new Color(0.60f, 0.80f, 0.95f));
                if (sky.HasProperty("_GroundColor")) sky.SetColor("_GroundColor", new Color(0.48f, 0.54f, 0.60f));
                RenderSettings.skybox = sky;
            }

            // Main Directional Sun - warm, golden, saturated
            GameObject sun = new GameObject("Directional Light");
            sun.transform.SetParent(parent.transform);
            Light sunLight = sun.AddComponent<Light>();
            sunLight.type = LightType.Directional;
            sunLight.color = new Color(1f, 0.74f, 0.42f);
            sunLight.intensity = 0.78f;
            sunLight.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(40f, -34f, 0f);

            // Teal skylight fill from the opposite hemisphere for warm/cool contrast
            GameObject fill = new GameObject("Ambient Fill Light");
            fill.transform.SetParent(parent.transform);
            Light fillLight = fill.AddComponent<Light>();
            fillLight.type = LightType.Directional;
            fillLight.color = new Color(0.26f, 0.60f, 0.68f);
            fillLight.intensity = 0.18f;
            fillLight.shadows = LightShadows.None;
            fill.transform.rotation = Quaternion.Euler(-45f, 138f, 0f);

            // Overview Camera - auto-aimed at the whole site
            GameObject camObj = new GameObject("Overview_Camera");
            camObj.transform.SetParent(parent.transform);
            camObj.tag = "MainCamera";
            Camera cam = camObj.AddComponent<Camera>();
            camObj.AddComponent<AudioListener>();
            cam.fieldOfView = 50f;
            cam.farClipPlane = 900f;
            Vector3 siteCenter = new Vector3(-22f, 0f, -25f);
            camObj.transform.position = new Vector3(95f, 90f, 105f);
            camObj.transform.rotation = Quaternion.LookRotation(siteCenter - camObj.transform.position, Vector3.up);

            // Reactor Perch Camera
            GameObject perchCam = new GameObject("Reactor_Perch_Camera");
            perchCam.transform.SetParent(parent.transform);
            Camera pCam = perchCam.AddComponent<Camera>();
            pCam.enabled = false;
            pCam.fieldOfView = 60f;
            perchCam.transform.position = new Vector3(0f, 12f, -18f);
            perchCam.transform.rotation = Quaternion.Euler(25f, 0f, 0f);
        }

        private static void CreateZoneMarker(ZoneData zone, Transform parent)
        {
            GameObject marker = new GameObject($"[Zone_Sign_{zone.id}]");
            marker.transform.SetParent(parent);
            if (zone.signAt != null && zone.signAt.Length == 3)
            {
                marker.transform.position = new Vector3(zone.signAt[0], zone.signAt[1], zone.signAt[2]);
            }
        }

        private static void BuildEntity(EntityData e, Transform zoneParent, Transform stationsParent, Transform routesParent, Transform spawnsParent)
        {
            if (e.hidden) return;

            switch (e.type)
            {
                case "floor":
                    BuildFloor(e, zoneParent);
                    break;
                case "wall":
                    BuildWall(e, zoneParent);
                    break;
                case "platform":
                    BuildPlatform(e, zoneParent);
                    break;
                case "stair":
                    BuildStair(e, zoneParent);
                    break;
                case "ramp":
                    BuildRamp(e, zoneParent);
                    break;
                case "catwalk":
                    BuildCatwalk(e, zoneParent);
                    break;
                case "machine":
                    BuildMachine(e, stationsParent);
                    break;
                case "prop":
                    BuildProp(e, zoneParent);
                    break;
                case "doorway":
                    BuildDoorway(e, zoneParent);
                    break;
                case "conveyor":
                    BuildConveyor(e, routesParent);
                    break;
                case "track":
                    BuildTrack(e, routesParent);
                    break;
                case "pipe":
                    BuildPipe(e, routesParent);
                    break;
                case "cavern":
                case "tunnel":
                    BuildCavernOrTunnel(e, zoneParent);
                    break;
                case "light":
                    BuildLight(e, zoneParent);
                    break;
                case "spawn":
                    BuildSpawn(e, spawnsParent);
                    break;
                case "marker":
                    BuildMarker(e, stationsParent);
                    break;
                case "mannequin":
                    BuildMannequin(e, zoneParent);
                    break;
                default:
                    break;
            }
        }

        private static void BuildFloor(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3 || e.size == null || e.size.Length < 2) return;

            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = e.id;
            go.transform.SetParent(parent);

            float thickness = e.thickness > 0 ? e.thickness : (HasTag(e, "grade") ? 0.6f : 0.3f);
            float width = e.size[0];
            float length = e.size[1];

            // In Three.js greybox, position is center of walkable TOP surface
            Vector3 center = new Vector3(e.position[0], e.position[1] - thickness * 0.5f, e.position[2]);
            go.transform.position = center;
            go.transform.localScale = new Vector3(width, thickness, length);

            if (e.rotationY != 0)
            {
                go.transform.rotation = Quaternion.Euler(0f, e.rotationY, 0f);
            }

            Material mat = HasTag(e, "grade") ? GetMaterial("Mat_Floor_Grade") : GetMaterial("Mat_Floor_Concrete", e.zone);
            go.GetComponent<Renderer>().sharedMaterial = mat;
            go.isStatic = true;
        }

        private static void BuildWall(EntityData e, Transform parent)
        {
            if (e.from == null || e.from.Length < 2 || e.to == null || e.to.Length < 2) return;

            Vector2 from = new Vector2(e.from[0], e.from[1]);
            Vector2 to = new Vector2(e.to[0], e.to[1]);
            Vector2 diff = to - from;
            float totalLength = diff.magnitude;
            if (totalLength < 0.01f) return;

            Vector2 dir = diff.normalized;
            float angle = Mathf.Atan2(dir.x, dir.y) * Mathf.Rad2Deg; // angle in degrees

            float height = e.height > 0 ? e.height : 4f;
            float thickness = e.thickness > 0 ? e.thickness : 0.3f;
            float baseY = e.baseY;

            Material mat = GetMaterial("Mat_Wall_Industrial", e.zone);

            GameObject wallRoot = new GameObject(e.id);
            wallRoot.transform.SetParent(parent);
            wallRoot.isStatic = true;

            if (e.openings == null || e.openings.Length == 0)
            {
                // Solid unbroken wall
                Vector2 mid2D = (from + to) * 0.5f;
                GameObject segment = GameObject.CreatePrimitive(PrimitiveType.Cube);
                segment.name = "Segment_Solid";
                segment.transform.SetParent(wallRoot.transform);
                segment.transform.position = new Vector3(mid2D.x, baseY + height * 0.5f, mid2D.y);
                segment.transform.rotation = Quaternion.Euler(0f, angle + 90f, 0f);
                segment.transform.localScale = new Vector3(totalLength, height, thickness);
                segment.GetComponent<Renderer>().sharedMaterial = mat;
                segment.isStatic = true;
            }
            else
            {
                // Build wall segments with real framed openings (cutouts, lintels, sills)
                var sortedOpenings = new List<WallOpeningData>(e.openings);
                sortedOpenings.Sort((a, b) => a.at.CompareTo(b.at));

                float currentPos = 0f;
                int segIndex = 0;

                foreach (var op in sortedOpenings)
                {
                    float opStart = Mathf.Max(0f, op.at - op.width * 0.5f);
                    float opEnd = Mathf.Min(totalLength, op.at + op.width * 0.5f);

                    // Wall segment before opening
                    if (opStart > currentPos + 0.05f)
                    {
                        float segLen = opStart - currentPos;
                        float segMid = currentPos + segLen * 0.5f;
                        Vector2 segPos2D = from + dir * segMid;

                        GameObject seg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                        seg.name = $"Seg_{segIndex++}";
                        seg.transform.SetParent(wallRoot.transform);
                        seg.transform.position = new Vector3(segPos2D.x, baseY + height * 0.5f, segPos2D.y);
                        seg.transform.rotation = Quaternion.Euler(0f, angle + 90f, 0f);
                        seg.transform.localScale = new Vector3(segLen, height, thickness);
                        seg.GetComponent<Renderer>().sharedMaterial = mat;
                        seg.isStatic = true;
                    }

                    // Sill below opening (if bottom > 0)
                    float opBottom = op.bottom > 0 ? op.bottom : 0f;
                    float opTop = op.top > 0 ? op.top : height;
                    float opMidX = (opStart + opEnd) * 0.5f;
                    float opWidth = opEnd - opStart;
                    Vector2 opMid2D = from + dir * opMidX;

                    if (opBottom > 0.05f)
                    {
                        GameObject sill = GameObject.CreatePrimitive(PrimitiveType.Cube);
                        sill.name = $"Sill_{segIndex++}";
                        sill.transform.SetParent(wallRoot.transform);
                        sill.transform.position = new Vector3(opMid2D.x, baseY + opBottom * 0.5f, opMid2D.y);
                        sill.transform.rotation = Quaternion.Euler(0f, angle + 90f, 0f);
                        sill.transform.localScale = new Vector3(opWidth, opBottom, thickness);
                        sill.GetComponent<Renderer>().sharedMaterial = mat;
                        sill.isStatic = true;
                    }

                    // Lintel above opening (if top < height)
                    if (opTop < height - 0.05f)
                    {
                        float lintelH = height - opTop;
                        GameObject lintel = GameObject.CreatePrimitive(PrimitiveType.Cube);
                        lintel.name = $"Lintel_{segIndex++}";
                        lintel.transform.SetParent(wallRoot.transform);
                        lintel.transform.position = new Vector3(opMid2D.x, baseY + opTop + lintelH * 0.5f, opMid2D.y);
                        lintel.transform.rotation = Quaternion.Euler(0f, angle + 90f, 0f);
                        lintel.transform.localScale = new Vector3(opWidth, lintelH, thickness);
                        lintel.GetComponent<Renderer>().sharedMaterial = mat;
                        lintel.isStatic = true;
                    }

                    currentPos = opEnd;
                }

                // Final trailing segment
                if (currentPos < totalLength - 0.05f)
                {
                    float segLen = totalLength - currentPos;
                    float segMid = currentPos + segLen * 0.5f;
                    Vector2 segPos2D = from + dir * segMid;

                    GameObject seg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    seg.name = $"Seg_{segIndex++}";
                    seg.transform.SetParent(wallRoot.transform);
                    seg.transform.position = new Vector3(segPos2D.x, baseY + height * 0.5f, segPos2D.y);
                    seg.transform.rotation = Quaternion.Euler(0f, angle + 90f, 0f);
                    seg.transform.localScale = new Vector3(segLen, height, thickness);
                    seg.GetComponent<Renderer>().sharedMaterial = mat;
                    seg.isStatic = true;
                }
            }
        }

        private static void BuildPlatform(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3 || e.size == null || e.size.Length < 2) return;

            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = e.id;
            go.transform.SetParent(parent);

            float thickness = e.thickness > 0 ? e.thickness : 0.35f;
            Vector3 center = new Vector3(e.position[0], e.position[1] - thickness * 0.5f, e.position[2]);
            go.transform.position = center;
            go.transform.localScale = new Vector3(e.size[0], thickness, e.size[1]);

            if (e.rotationY != 0) go.transform.rotation = Quaternion.Euler(0f, e.rotationY, 0f);

            go.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Metal_Catwalk");
            go.isStatic = true;
        }

        private static void BuildStair(EntityData e, Transform parent)
        {
            if (e.from == null || e.from.Length < 3 || e.to == null || e.to.Length < 3) return;

            Vector3 start = new Vector3(e.from[0], e.from[1], e.from[2]);
            Vector3 end = new Vector3(e.to[0], e.to[1], e.to[2]);
            Vector3 delta = end - start;
            float horizontalDist = new Vector2(delta.x, delta.z).magnitude;
            if (horizontalDist < 0.05f) return;

            float width = e.width > 0 ? e.width : 2f;
            int stepCount = e.stepCount > 0 ? e.stepCount : Mathf.Max(3, Mathf.RoundToInt(Mathf.Abs(delta.y) / 0.22f));

            GameObject stairRoot = new GameObject(e.id);
            stairRoot.transform.SetParent(parent);
            stairRoot.isStatic = true;

            Material mat = GetMaterial("Mat_Metal_Catwalk");

            for (int i = 0; i < stepCount; i++)
            {
                float t0 = (float)i / stepCount;
                float t1 = (float)(i + 1) / stepCount;

                Vector3 p0 = Vector3.Lerp(start, end, t0);
                Vector3 p1 = Vector3.Lerp(start, end, t1);
                Vector3 stepCenter = (p0 + p1) * 0.5f;

                float stepHeight = Mathf.Abs(delta.y) / stepCount;
                float stepLength = horizontalDist / stepCount;

                GameObject step = GameObject.CreatePrimitive(PrimitiveType.Cube);
                step.name = $"Step_{i}";
                step.transform.SetParent(stairRoot.transform);
                step.transform.position = new Vector3(stepCenter.x, p1.y - stepHeight * 0.5f, stepCenter.z);

                Vector3 forward = new Vector3(delta.x, 0f, delta.z).normalized;
                step.transform.rotation = Quaternion.LookRotation(forward);
                step.transform.localScale = new Vector3(width, stepHeight, stepLength * 1.15f);
                step.GetComponent<Renderer>().sharedMaterial = mat;
                step.isStatic = true;
            }

            // Smooth slope box collider for seamless player walking
            GameObject colliderObj = new GameObject("Ramp_Collider");
            colliderObj.transform.SetParent(stairRoot.transform);
            Vector3 mid = (start + end) * 0.5f;
            colliderObj.transform.position = mid;
            Vector3 dir = (end - start).normalized;
            colliderObj.transform.rotation = Quaternion.LookRotation(dir, Vector3.up);
            BoxCollider col = colliderObj.AddComponent<BoxCollider>();
            col.size = new Vector3(width, 0.4f, (end - start).magnitude);
        }

        private static void BuildRamp(EntityData e, Transform parent)
        {
            if (e.from == null || e.from.Length < 3 || e.to == null || e.to.Length < 3) return;

            Vector3 start = new Vector3(e.from[0], e.from[1], e.from[2]);
            Vector3 end = new Vector3(e.to[0], e.to[1], e.to[2]);
            Vector3 diff = end - start;
            float len = diff.magnitude;
            if (len < 0.05f) return;

            GameObject ramp = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ramp.name = e.id;
            ramp.transform.SetParent(parent);

            float width = e.width > 0 ? e.width : 2f;
            float thickness = e.thickness > 0 ? e.thickness : 0.3f;

            ramp.transform.position = (start + end) * 0.5f - Vector3.up * (thickness * 0.5f);
            ramp.transform.rotation = Quaternion.LookRotation(diff, Vector3.up);
            ramp.transform.localScale = new Vector3(width, thickness, len);

            ramp.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Metal_Catwalk");
            ramp.isStatic = true;
        }

        private static void BuildCatwalk(EntityData e, Transform parent)
        {
            if (e.path == null || e.path.Length < 2) return;

            GameObject catwalkRoot = new GameObject(e.id);
            catwalkRoot.transform.SetParent(parent);
            catwalkRoot.isStatic = true;

            float width = e.width > 0 ? e.width : 1.8f;
            Material mat = GetMaterial("Mat_Metal_Catwalk");

            for (int i = 0; i < e.path.Length - 1; i++)
            {
                if (e.path[i].Length < 3 || e.path[i + 1].Length < 3) continue;
                Vector3 p0 = new Vector3(e.path[i][0], e.path[i][1], e.path[i][2]);
                Vector3 p1 = new Vector3(e.path[i + 1][0], e.path[i + 1][1], e.path[i + 1][2]);
                Vector3 seg = p1 - p0;
                float segLen = seg.magnitude;
                if (segLen < 0.05f) continue;

                GameObject segment = GameObject.CreatePrimitive(PrimitiveType.Cube);
                segment.name = $"Catwalk_Seg_{i}";
                segment.transform.SetParent(catwalkRoot.transform);
                segment.transform.position = (p0 + p1) * 0.5f - Vector3.up * 0.1f;
                segment.transform.rotation = Quaternion.LookRotation(seg, Vector3.up);
                segment.transform.localScale = new Vector3(width, 0.2f, segLen);
                segment.GetComponent<Renderer>().sharedMaterial = mat;
                segment.isStatic = true;
            }
        }

        private static void BuildMachine(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3 || e.size == null || e.size.Length < 3) return;

            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = $"[MACHINE] {e.label ?? e.id}";
            go.transform.SetParent(parent);

            Vector3 size = new Vector3(e.size[0], e.size[1], e.size[2]);
            Vector3 center = new Vector3(e.position[0], e.position[1] + size.y * 0.5f, e.position[2]);
            go.transform.position = center;
            go.transform.localScale = size;

            if (e.rotationY != 0) go.transform.rotation = Quaternion.Euler(0f, e.rotationY, 0f);

            go.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Metal_Machine");
            go.isStatic = true;
        }

        private static void BuildProp(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3 || e.size == null || e.size.Length < 3) return;

            PrimitiveType primType = (e.shape == "cylinder") ? PrimitiveType.Cylinder : PrimitiveType.Cube;
            GameObject go = GameObject.CreatePrimitive(primType);
            go.name = e.id;
            go.transform.SetParent(parent);

            Vector3 size = new Vector3(e.size[0], e.size[1], e.size[2]);
            Vector3 center = new Vector3(e.position[0], e.position[1] + size.y * 0.5f, e.position[2]);
            go.transform.position = center;
            go.transform.localScale = size;

            if (e.rotationY != 0) go.transform.rotation = Quaternion.Euler(0f, e.rotationY, 0f);

            Material mat = e.zone == "mine" ? GetMaterial("Mat_Rock_Cavern") : GetMaterial("Mat_Metal_Machine");
            go.GetComponent<Renderer>().sharedMaterial = mat;
            go.isStatic = true;
        }

        private static void BuildDoorway(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3) return;

            GameObject door = new GameObject(e.id);
            door.transform.SetParent(parent);
            door.transform.position = new Vector3(e.position[0], e.position[1], e.position[2]);
            if (e.rotationY != 0) door.transform.rotation = Quaternion.Euler(0f, e.rotationY, 0f);

            // Door frame posts
            float w = e.width > 0 ? e.width : 2f;
            float h = e.height > 0 ? e.height : 2.8f;

            GameObject postL = GameObject.CreatePrimitive(PrimitiveType.Cube);
            postL.name = "Post_L";
            postL.transform.SetParent(door.transform);
            postL.transform.localPosition = new Vector3(-w * 0.5f, h * 0.5f, 0f);
            postL.transform.localScale = new Vector3(0.25f, h, 0.35f);
            postL.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Hazard_Stripe");

            GameObject postR = GameObject.CreatePrimitive(PrimitiveType.Cube);
            postR.name = "Post_R";
            postR.transform.SetParent(door.transform);
            postR.transform.localPosition = new Vector3(w * 0.5f, h * 0.5f, 0f);
            postR.transform.localScale = new Vector3(0.25f, h, 0.35f);
            postR.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Hazard_Stripe");

            GameObject header = GameObject.CreatePrimitive(PrimitiveType.Cube);
            header.name = "Header";
            header.transform.SetParent(door.transform);
            header.transform.localPosition = new Vector3(0f, h + 0.15f, 0f);
            header.transform.localScale = new Vector3(w + 0.5f, 0.3f, 0.4f);
            header.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Hazard_Stripe");
        }

        private static void BuildConveyor(EntityData e, Transform parent)
        {
            if (e.path == null || e.path.Length < 2) return;

            GameObject convRoot = new GameObject(e.id);
            convRoot.transform.SetParent(parent);
            float width = e.width > 0 ? e.width : 1.4f;

            Material beltMat = GetMaterial("Mat_Hazard_Stripe");

            for (int i = 0; i < e.path.Length - 1; i++)
            {
                if (e.path[i].Length < 3 || e.path[i + 1].Length < 3) continue;
                Vector3 p0 = new Vector3(e.path[i][0], e.path[i][1], e.path[i][2]);
                Vector3 p1 = new Vector3(e.path[i + 1][0], e.path[i + 1][1], e.path[i + 1][2]);
                Vector3 seg = p1 - p0;
                float segLen = seg.magnitude;
                if (segLen < 0.05f) continue;

                GameObject belt = GameObject.CreatePrimitive(PrimitiveType.Cube);
                belt.name = $"Belt_Seg_{i}";
                belt.transform.SetParent(convRoot.transform);
                belt.transform.position = (p0 + p1) * 0.5f;
                belt.transform.rotation = Quaternion.LookRotation(seg, Vector3.up);
                belt.transform.localScale = new Vector3(width, 0.25f, segLen);
                belt.GetComponent<Renderer>().sharedMaterial = beltMat;
                belt.isStatic = true;
            }
        }

        private static void BuildTrack(EntityData e, Transform parent)
        {
            if (e.path == null || e.path.Length < 2) return;

            GameObject trackRoot = new GameObject(e.id);
            trackRoot.transform.SetParent(parent);
            Material trackMat = GetMaterial("Mat_Cart_Track");

            for (int i = 0; i < e.path.Length - 1; i++)
            {
                if (e.path[i].Length < 3 || e.path[i + 1].Length < 3) continue;
                Vector3 p0 = new Vector3(e.path[i][0], e.path[i][1], e.path[i][2]);
                Vector3 p1 = new Vector3(e.path[i + 1][0], e.path[i + 1][1], e.path[i + 1][2]);
                Vector3 seg = p1 - p0;
                float segLen = seg.magnitude;
                if (segLen < 0.05f) continue;

                GameObject rail = GameObject.CreatePrimitive(PrimitiveType.Cube);
                rail.name = $"Rail_Seg_{i}";
                rail.transform.SetParent(trackRoot.transform);
                rail.transform.position = (p0 + p1) * 0.5f + Vector3.up * 0.05f;
                rail.transform.rotation = Quaternion.LookRotation(seg, Vector3.up);
                rail.transform.localScale = new Vector3(1.2f, 0.1f, segLen);
                rail.GetComponent<Renderer>().sharedMaterial = trackMat;
                rail.isStatic = true;
            }
        }

        private static void BuildPipe(EntityData e, Transform parent)
        {
            if (e.path == null || e.path.Length < 2) return;

            GameObject pipeRoot = new GameObject(e.id);
            pipeRoot.transform.SetParent(parent);
            float radius = e.radius > 0 ? e.radius : 0.25f;
            Material mat = GetMaterial("Mat_Metal_Machine");

            for (int i = 0; i < e.path.Length - 1; i++)
            {
                if (e.path[i].Length < 3 || e.path[i + 1].Length < 3) continue;
                Vector3 p0 = new Vector3(e.path[i][0], e.path[i][1], e.path[i][2]);
                Vector3 p1 = new Vector3(e.path[i + 1][0], e.path[i + 1][1], e.path[i + 1][2]);
                Vector3 seg = p1 - p0;
                float segLen = seg.magnitude;
                if (segLen < 0.05f) continue;

                GameObject cyl = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                cyl.name = $"Pipe_Seg_{i}";
                cyl.transform.SetParent(pipeRoot.transform);
                cyl.transform.position = (p0 + p1) * 0.5f;
                cyl.transform.rotation = Quaternion.FromToRotation(Vector3.up, seg.normalized);
                cyl.transform.localScale = new Vector3(radius * 2f, segLen * 0.5f, radius * 2f);
                cyl.GetComponent<Renderer>().sharedMaterial = mat;
                cyl.isStatic = true;
            }
        }

        private static void BuildCavernOrTunnel(EntityData e, Transform parent)
        {
            if (e.position != null && e.position.Length == 3 && e.size != null && e.size.Length == 3)
            {
                GameObject cav = GameObject.CreatePrimitive(PrimitiveType.Cube);
                cav.name = e.id;
                cav.transform.SetParent(parent);
                cav.transform.position = new Vector3(e.position[0], e.position[1] + e.size[1] * 0.5f, e.position[2]);
                cav.transform.localScale = new Vector3(e.size[0], e.size[1], e.size[2]);
                cav.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Rock_Cavern");
                cav.isStatic = true;
            }
            else if (e.path != null && e.path.Length >= 2)
            {
                GameObject tunRoot = new GameObject(e.id);
                tunRoot.transform.SetParent(parent);
                float w = e.width > 0 ? e.width : 3.2f;
                float h = e.height > 0 ? e.height : 2.8f;
                Material mat = GetMaterial("Mat_Rock_Cavern");

                for (int i = 0; i < e.path.Length - 1; i++)
                {
                    if (e.path[i].Length < 3 || e.path[i + 1].Length < 3) continue;
                    Vector3 p0 = new Vector3(e.path[i][0], e.path[i][1], e.path[i][2]);
                    Vector3 p1 = new Vector3(e.path[i + 1][0], e.path[i + 1][1], e.path[i + 1][2]);
                    Vector3 seg = p1 - p0;
                    float len = seg.magnitude;
                    if (len < 0.05f) continue;

                    GameObject tunSeg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    tunSeg.name = $"Tunnel_Seg_{i}";
                    tunSeg.transform.SetParent(tunRoot.transform);
                    tunSeg.transform.position = (p0 + p1) * 0.5f + Vector3.up * (h * 0.5f);
                    tunSeg.transform.rotation = Quaternion.LookRotation(seg, Vector3.up);
                    tunSeg.transform.localScale = new Vector3(w, h, len);
                    tunSeg.GetComponent<Renderer>().sharedMaterial = mat;
                    tunSeg.isStatic = true;
                }
            }
        }

        private static void BuildLight(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3) return;

            GameObject lightObj = new GameObject(e.id);
            lightObj.transform.SetParent(parent);
            lightObj.transform.position = new Vector3(e.position[0], e.position[1], e.position[2]);

            Light l = lightObj.AddComponent<Light>();
            l.type = LightType.Point;
            l.range = Mathf.Min(e.range > 0 ? e.range : 12f, 12f);
            float authoredIntensity = e.intensity > 0 ? e.intensity : 3.2f;
            // The JSON mixes legacy hand-authored values with physically based
            // light-unit values. Normalize both into the Built-in renderer's useful
            // prototype range so overlapping practicals do not bleach the facility.
            l.intensity = Mathf.Clamp(authoredIntensity > 10f
                ? authoredIntensity * 0.015f
                : authoredIntensity * 0.28f, 0.35f, 2.2f);
            l.shadows = LightShadows.None;
            l.renderMode = LightRenderMode.ForceVertex;

            if (!string.IsNullOrEmpty(e.color) && ColorUtility.TryParseHtmlString(e.color, out Color c))
            {
                l.color = c;
            }
            else
            {
                // Warm amber industrial practical, Sea of Thieves warmth
                l.color = new Color(1f, 0.83f, 0.58f);
            }
        }

        private static void BuildSpawn(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3) return;

            GameObject spawnObj = new GameObject($"[SPAWN] {e.label ?? e.id}");
            spawnObj.transform.SetParent(parent);
            spawnObj.transform.position = new Vector3(e.position[0], e.position[1], e.position[2]);

            GameObject pad = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pad.name = "Spawn_Pad";
            pad.transform.SetParent(spawnObj.transform);
            pad.transform.localPosition = new Vector3(0f, 0.05f, 0f);
            pad.transform.localScale = new Vector3(1.6f, 0.05f, 1.6f);
            pad.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Emissive_Control");
            // Spawn pads are visual authoring aids, never gameplay obstacles.
            Collider padCollider = pad.GetComponent<Collider>();
            if (padCollider != null) UnityEngine.Object.DestroyImmediate(padCollider);
        }

        private static void BuildRoutes(RouteData[] routes, Transform parent)
        {
            if (routes == null) return;

            foreach (var route in routes)
            {
                if (route == null || route.path == null || route.path.Length < 2) continue;

                var routeObject = new GameObject($"[ROUTE_{route.kind?.ToUpperInvariant() ?? "GUIDE"}] {route.name}");
                routeObject.transform.SetParent(parent);
                var line = routeObject.AddComponent<LineRenderer>();
                line.useWorldSpace = true;
                line.positionCount = route.path.Length;
                line.startWidth = route.kind == "primary" ? 0.16f : 0.10f;
                line.endWidth = line.startWidth;
                line.numCapVertices = 2;
                line.numCornerVertices = 2;
                line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                line.receiveShadows = false;

                var routeMaterial = GetMaterial("Mat_Route_Guide");
                line.sharedMaterial = routeMaterial;
                Color routeColor = Color.white;
                if (!string.IsNullOrEmpty(route.color)) ColorUtility.TryParseHtmlString(route.color, out routeColor);
                line.startColor = routeColor;
                line.endColor = routeColor;

                for (int i = 0; i < route.path.Length; i++)
                {
                    var point = route.path[i];
                    line.SetPosition(i, point != null && point.Length >= 3
                        ? new Vector3(point[0], point[1] + 0.08f, point[2])
                        : Vector3.zero);
                }
            }
        }

        private static RouteData[] ParseRoutes(string json)
        {
            // Unity's JsonUtility does not deserialize nested float[][] arrays. The
            // facility file intentionally stays tool-friendly JSON, so use a narrow
            // fallback parser for only the route records rather than adding a package.
            var routesStart = json.IndexOf("\"routes\"", StringComparison.Ordinal);
            if (routesStart < 0) return Array.Empty<RouteData>();
            string routeText = json.Substring(routesStart);
            var result = new List<RouteData>();
            var objects = Regex.Matches(routeText, @"\{\s*""id""\s*:\s*""([^""]+)"".*?""name""\s*:\s*""([^""]*)"".*?""kind""\s*:\s*""([^""]*)"".*?""color""\s*:\s*""([^""]*)"".*?""path""\s*:\s*\[((?:\s*\[[^\]]+\]\s*,?)+)\]\s*\},?", RegexOptions.Singleline);
            foreach (Match obj in objects)
            {
                var points = new List<float[]>();
                var pointMatches = Regex.Matches(obj.Groups[5].Value, @"\[\s*(-?[0-9.eE+]+)\s*,\s*(-?[0-9.eE+]+)\s*,\s*(-?[0-9.eE+]+)\s*\]");
                foreach (Match point in pointMatches)
                {
                    if (float.TryParse(point.Groups[1].Value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float x) &&
                        float.TryParse(point.Groups[2].Value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float y) &&
                        float.TryParse(point.Groups[3].Value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float z))
                        points.Add(new[] { x, y, z });
                }
                if (points.Count >= 2)
                    result.Add(new RouteData { id = obj.Groups[1].Value, name = obj.Groups[2].Value, kind = obj.Groups[3].Value, color = obj.Groups[4].Value, path = points.ToArray() });
            }
            return result.ToArray();
        }

        private static void BuildMarker(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3) return;

            GameObject marker = new GameObject($"[MARKER_{e.kind?.ToUpper() ?? "INFO"}] {e.label ?? e.id}");
            marker.transform.SetParent(parent);
            marker.transform.position = new Vector3(e.position[0], e.position[1] + 1f, e.position[2]);

            GameObject icon = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            icon.name = "Marker_Sphere";
            icon.transform.SetParent(marker.transform);
            icon.transform.localPosition = Vector3.zero;
            icon.transform.localScale = new Vector3(0.4f, 0.4f, 0.4f);

            Material mat = (e.kind == "hazard") ? GetMaterial("Mat_Emissive_Alarm") : GetMaterial("Mat_Emissive_Control");
            icon.GetComponent<Renderer>().sharedMaterial = mat;

            // Remove sphere collider so players don't bump into interaction marker gizmos
            Collider col = icon.GetComponent<Collider>();
            if (col != null) UnityEngine.Object.DestroyImmediate(col);
        }

        private static void BuildMannequin(EntityData e, Transform parent)
        {
            if (e.position == null || e.position.Length < 3) return;

            GameObject man = new GameObject(e.id);
            man.transform.SetParent(parent);
            man.transform.position = new Vector3(e.position[0], e.position[1], e.position[2]);
            if (e.rotationY != 0) man.transform.rotation = Quaternion.Euler(0f, e.rotationY, 0f);

            // 1.75m stylized human silhouette blockout
            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            body.name = "Body";
            body.transform.SetParent(man.transform);
            body.transform.localPosition = new Vector3(0f, 0.875f, 0f);
            body.transform.localScale = new Vector3(0.5f, 0.875f, 0.35f);
            body.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Zone_arrival");

            GameObject head = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            head.name = "Helmet";
            head.transform.SetParent(man.transform);
            head.transform.localPosition = new Vector3(0f, 1.6f, 0f);
            head.transform.localScale = new Vector3(0.35f, 0.38f, 0.38f);
            head.GetComponent<Renderer>().sharedMaterial = GetMaterial("Mat_Hazard_Stripe");
        }

        private static bool HasTag(EntityData e, string tag)
        {
            if (e.tags == null) return false;
            foreach (var t in e.tags) if (t == tag) return true;
            return false;
        }

        #region Custom JSON Parser Fallback
        private static FacilityData ParseFacilityData(string json)
        {
            // Simple parsing wrapper if required
            return JsonUtility.FromJson<FacilityData>(json);
        }
        #endregion
    }

    [Serializable]
    public class FacilityData
    {
        public string format;
        public int version;
        public string name;
        public string description;
        public ZoneData[] zones;
        public EntityData[] entities;
        public RouteData[] routes;
    }

    [Serializable]
    public class ZoneData
    {
        public string id;
        public string name;
        public string color;
        public float[] signAt;
        public string levels;
        public string summary;
    }

    [Serializable]
    public class EntityData
    {
        public string id;
        public string type;
        public string zone;
        public string label;
        public string notes;
        public string[] tags;
        public string color;
        public bool collision;
        public bool hidden;

        public float[] position;
        public float[] size;
        public float thickness;
        public float rotationY;

        public float[] from;
        public float[] to;
        public float height;
        public float baseY;
        public WallOpeningData[] openings;

        public float[][] path;
        public float width;
        public int stepCount;
        public float radius;
        public string shape;

        public string kind;
        public float intensity;
        public float range;
    }

    [Serializable]
    public class WallOpeningData
    {
        public float at;
        public float width;
        public float bottom;
        public float top;
    }

    [Serializable]
    public class RouteData
    {
        public string id;
        public string name;
        public string kind;
        public string color;
        public string notes;
        public float[][] path;
    }
}
