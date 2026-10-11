using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Player.Editor
{
    [Serializable] public sealed class SurfaceTexture { public string file, sha256, colorSpace; public int size; }
    [Serializable] public sealed class SurfaceMaps { public SurfaceTexture albedo, normal, emission, metallicSmoothness; }
    [Serializable] public sealed class SurfaceDefinition { public string key, source; public int atlas; public float dielectricSpecular=0.04f; public float alpha, transmission, surfaceOpacity, metallic, smoothness, emissionStrength; public bool transparent, baseConstant, normalConstant, metallicConstant, roughnessConstant, emissionConstant; public SurfaceTexture directEmission; public float[] baseColor, emissionColor; }
    [Serializable] public sealed class SurfacePackage
    {
        public string room, uv; public bool lightingIncludedInAlbedo; public int meshes;
        public SurfaceMaps maps; public SurfaceDefinition[] definitions;
        public SurfaceMaps[] atlases;
        public SurfaceTexture displayLut;
        public SurfaceTexture letteringMesh;
        public SurfaceTexture wallMesh;
    }

    internal static class SpawnSurfaceBuild
    {
        internal static void SplitEmbeddedEmitter(Transform node, Vector3[] pointLights, SurfacePackage package)
        {
            var renderer=node.GetComponent<MeshRenderer>();var filter=node.GetComponent<MeshFilter>();
            if(renderer==null || filter==null || !renderer.enabled || !pointLights.Any(renderer.bounds.Contains)) return;
            var definitions=package.definitions.ToDictionary(d=>d.key,StringComparer.Ordinal);
            var slots=renderer.sharedMaterials.Select(m=>definitions.TryGetValue(m.name,out var d) && d.emissionConstant && d.emissionStrength>0).ToArray();
            if(!slots.Any(lit=>lit)) return;
            // Blender samples an extended point emitter outside its tiny visible bulb. A built-in
            // point bake starts at its centre; keep that bulb from occluding its own light.
            var opaque=UnityEngine.Object.Instantiate(filter.sharedMesh);
            var emitter=UnityEngine.Object.Instantiate(filter.sharedMesh);
            for(int slot=0;slot<slots.Length;slot++)
            {
                if(slots[slot]) opaque.SetTriangles(Array.Empty<int>(),slot);
                else emitter.SetTriangles(Array.Empty<int>(),slot);
            }
            string prefix=SpawnMapBuild.Folder+"Surfaces/"+node.name;
            AssetDatabase.DeleteAsset(prefix+"-fixture.asset");AssetDatabase.CreateAsset(opaque,prefix+"-fixture.asset");
            AssetDatabase.DeleteAsset(prefix+"-emitter.asset");AssetDatabase.CreateAsset(emitter,prefix+"-emitter.asset");
            filter.sharedMesh=opaque;
            var child=new GameObject("Embedded emitter surface");child.transform.SetParent(node,false);
            child.AddComponent<MeshFilter>().sharedMesh=emitter;
            var surface=child.AddComponent<MeshRenderer>();surface.sharedMaterials=renderer.sharedMaterials;
            surface.shadowCastingMode=ShadowCastingMode.Off;surface.receiveShadows=false;
            GameObjectUtility.SetStaticEditorFlags(child,StaticEditorFlags.ContributeGI|StaticEditorFlags.ReflectionProbeStatic);
        }

        internal static Dictionary<string, Material> Materials(SurfacePackage package)
        {
            if (package == null || package.room != "spawn-room" || package.lightingIncludedInAlbedo || package.uv != "CS_DeliveryUV")
                throw new InvalidOperationException("Spawn requires explicit unlit source material maps.");
            string folder = SpawnMapBuild.Folder + "Surfaces/";
            var atlases=new List<(Texture2D albedo,Texture2D normal,Texture2D metallic,Texture2D emission)>();
            foreach (var maps in package.atlases)
                atlases.Add((Texture(maps.albedo,false),Texture(maps.normal,true),Texture(maps.metallicSmoothness,false),Texture(maps.emission,false)));
            var result = new Dictionary<string, Material>();
            foreach (var definition in package.definitions)
            {
                var (albedo,normal,metallic,emission)=atlases[definition.atlas];
                string path = folder + definition.key + ".mat";
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material == null) { material = new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(material, path); }
                material.shader=Shader.Find(definition.transparent ? "CriticalShift/BlenderGlass" : "CriticalShift/BlenderSurface");
                if(material.shader==null) throw new InvalidOperationException("Missing source surface shader.");
                material.doubleSidedGI=!definition.transparent;
                material.color = new Color(1, 1, 1, definition.transparent ? definition.surfaceOpacity : 1);
                material.SetTexture("_MainTex", albedo); material.SetTexture("_BumpMap", normal); material.SetFloat("_BumpScale", 1);
                material.SetTexture("_MetallicGlossMap", metallic); material.SetFloat("_GlossMapScale", 1);
                material.SetFloat("_Metallic",definition.metallic);material.SetFloat("_Glossiness",definition.smoothness);
                if(!definition.transparent) material.SetFloat("_DielectricSpecular",definition.dielectricSpecular);
                material.SetFloat("_MetallicFromMap",definition.metallicConstant?0:1);
                material.SetFloat("_SmoothnessFromMap",definition.roughnessConstant?0:1);
                material.SetTexture("_EmissionMap", emission); material.SetColor("_EmissionColor", Color.white);
                material.EnableKeyword("_NORMALMAP"); material.EnableKeyword("_METALLICGLOSSMAP"); material.EnableKeyword("_EMISSION");
                material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                // Uniform shader inputs do not depend on atlas coverage, which can be subpixel for lettering.
                if (definition.baseConstant)
                    material.SetTexture("_MainTex", ConstantTexture(folder+definition.key+"-base.asset",definition.baseColor,1));
                if (definition.normalConstant)
                { material.SetTexture("_BumpMap",null); material.DisableKeyword("_NORMALMAP"); }
                if (definition.metallicConstant && definition.roughnessConstant)
                {
                    material.SetTexture("_MetallicGlossMap",null); material.DisableKeyword("_METALLICGLOSSMAP");
                    material.SetFloat("_Metallic",definition.metallic); material.SetFloat("_Glossiness",definition.smoothness);
                }
                if (definition.emissionConstant)
                {
                    bool lit=definition.emissionStrength>0 && definition.emissionColor!=null &&
                        (definition.emissionColor[0]>0 || definition.emissionColor[1]>0 || definition.emissionColor[2]>0);
                    material.SetTexture("_EmissionMap",lit ? ConstantTexture(folder+definition.key+"-emission.asset",definition.emissionColor,definition.emissionStrength) : null);
                    material.SetColor("_EmissionColor",lit ? Color.white : Color.black);
                    if (lit) material.EnableKeyword("_EMISSION"); else material.DisableKeyword("_EMISSION");
                    material.globalIlluminationFlags=lit ? MaterialGlobalIlluminationFlags.BakedEmissive : MaterialGlobalIlluminationFlags.EmissiveIsBlack;
                }
                if (definition.directEmission!=null && !string.IsNullOrEmpty(definition.directEmission.file))
                {
                    if (definition.baseColor==null || definition.baseColor.Length!=4) throw new InvalidOperationException("Missing source screen colour: "+definition.source);
                    material.SetTexture("_BumpMap",null);material.SetTexture("_MetallicGlossMap",null);
                    material.DisableKeyword("_NORMALMAP");material.DisableKeyword("_METALLICGLOSSMAP");
                    if (!definition.baseConstant) material.SetColor("_Color",new Color(definition.baseColor[0],definition.baseColor[1],definition.baseColor[2],definition.baseColor[3]));
                    material.SetFloat("_Metallic",definition.metallic);material.SetFloat("_Glossiness",definition.smoothness);
                    material.SetTexture("_EmissionMap",Texture(definition.directEmission,false));material.SetColor("_EmissionColor",Color.white*definition.emissionStrength);
                }
                material.SetFloat("_Mode", definition.transparent ? 2 : 0);
                material.SetOverrideTag("RenderType", definition.transparent ? "Transparent" : "Opaque");
                material.SetInt("_SrcBlend", (int)(definition.transparent ? BlendMode.SrcAlpha : BlendMode.One));
                material.SetInt("_DstBlend", (int)(definition.transparent ? BlendMode.OneMinusSrcAlpha : BlendMode.Zero));
                material.SetInt("_ZWrite", definition.transparent ? 0 : 1);
                material.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                if (definition.transparent) material.EnableKeyword("_ALPHABLEND_ON");
                else material.DisableKeyword("_ALPHABLEND_ON");
                material.renderQueue = definition.transparent ? (int)RenderQueue.Transparent : -1;
                EditorUtility.SetDirty(material); result.Add(definition.key, material);
            }
            AssetDatabase.SaveAssets(); return result;
        }

        internal static Material View(SurfacePackage package)
        {
            var lut = Texture(package.displayLut, false);
            string path = SpawnMapBuild.Folder + "Surfaces/BlenderView.mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null) { material = new Material(Shader.Find("Hidden/CriticalShift/BlenderView")); AssetDatabase.CreateAsset(material,path); }
            material.SetTexture("_ViewLut",lut); EditorUtility.SetDirty(material); return material;
        }

        private static Texture2D ConstantTexture(string path,float[] colour,float strength)
        {
            if (colour==null || colour.Length!=4) throw new InvalidOperationException("Missing uniform source colour: "+path);
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture==null)
            {
                texture=new Texture2D(1,1,TextureFormat.RGBAHalf,false,true) {name=Path.GetFileNameWithoutExtension(path),filterMode=FilterMode.Point,wrapMode=TextureWrapMode.Clamp};
                AssetDatabase.CreateAsset(texture,path);
            }
            texture.SetPixel(0,0,new Color(colour[0]*strength,colour[1]*strength,colour[2]*strength,colour[3]));
            texture.Apply(false,false); EditorUtility.SetDirty(texture); return texture;
        }

        private static Texture2D Texture(SurfaceTexture source, bool normal)
        {
            if (source == null) throw new InvalidOperationException("Missing material texture.");
            SpawnMapBuild.CheckHash(source.file, source.sha256);
            string path = SpawnMapBuild.Folder + source.file;
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) throw new InvalidOperationException("Missing generated texture: " + path);
            importer.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            // Unity auto-detects wide colour strips as cubemaps. These are explicit 2D shader inputs.
            importer.textureShape = TextureImporterShape.Texture2D;
            importer.sRGBTexture = source.colorSpace == "sRGB";
            importer.maxTextureSize = source.size; importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.mipmapEnabled = !source.file.Contains("display-lut") && !source.file.Contains("source-emission"); importer.wrapMode = TextureWrapMode.Clamp;
            importer.isReadable = false;
            importer.filterMode = source.file.Contains("display-lut") ? FilterMode.Bilinear : FilterMode.Trilinear;
            importer.SaveAndReimport();
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture==null) throw new InvalidOperationException("Texture importer produced no Texture2D asset: "+path);
            if (source.file.Contains("display-lut") && (texture.width!=4096 || texture.height!=64))
                throw new InvalidOperationException("The Blender display lookup must retain its 4096x64 layout.");
            return texture;
        }
    }
}
