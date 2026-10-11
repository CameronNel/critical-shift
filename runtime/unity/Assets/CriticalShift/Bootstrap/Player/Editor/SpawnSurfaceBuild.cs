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
    [Serializable] public sealed class SuitOcclusionVertex { public float[] position; public float front, back; }
    [Serializable] public sealed class SuitOcclusionMesh { public string node; public SuitOcclusionVertex[] vertices; }
    [Serializable] public sealed class SuitOcclusion { public bool lightingIncluded; public SuitOcclusionMesh[] meshes; }
    [Serializable] public sealed class SurfaceDefinition { public string key, source; public int atlas; public float dielectricSpecular=0.04f; public float alpha, transmission, surfaceOpacity, metallic, smoothness, emissionStrength, reflectionIOR; public bool transparent, thinSurface, alphaMapped, baseConstant, normalConstant, metallicConstant, roughnessConstant, emissionConstant; public SurfaceTexture directEmission, directAlbedo; public float[] baseColor, emissionColor, reflectionColor; }
    [Serializable] public sealed class SurfacePackage
    {
        public string room, uv; public bool lightingIncludedInAlbedo; public int meshes;
        public SurfaceMaps maps; public SurfaceDefinition[] definitions;
        public SurfaceMaps[] atlases;
        public SurfaceTexture displayLut;
        public SurfaceTexture letteringMesh;
        public SurfaceTexture wallMesh;
        public SurfaceTexture suitOcclusion;
        public AssemblyLighting assemblyLighting;
    }
    [Serializable] public sealed class AssemblyLighting
    {
        public float[] world_color, sun_color, sun_rot_deg;
        public float world_strength, sun_energy;
    }

    internal static class SpawnSurfaceBuild
    {
        internal static void BindSuitOcclusion(Dictionary<string,Transform> nodes,Transform room,SurfacePackage package)
        {
            if(package.suitOcclusion==null) throw new InvalidOperationException("Regenerate hanging suit geometry occlusion.");
            SpawnMapBuild.CheckHash(package.suitOcclusion.file,package.suitOcclusion.sha256);
            var source=JsonUtility.FromJson<SuitOcclusion>(File.ReadAllText(SpawnMapBuild.Folder+package.suitOcclusion.file));
            if(source.lightingIncluded || source.meshes.Length!=4) throw new InvalidOperationException("Unexpected hanging suit occlusion inventory.");
            Vector3Int Key(Vector3 p)=>new Vector3Int(Mathf.RoundToInt(p.x*10000),Mathf.RoundToInt(p.y*10000),Mathf.RoundToInt(p.z*10000));
            foreach(var record in source.meshes)
            {
                var node=nodes[record.node];var filter=node.GetComponent<MeshFilter>();var renderer=node.GetComponent<MeshRenderer>();
                var lookup=record.vertices.GroupBy(v=>Key(new Vector3(v.position[0],v.position[2],v.position[1])))
                    .ToDictionary(g=>g.Key,g=>new Color(g.Average(v=>v.front),g.Average(v=>v.back),1,1));
                var mesh=UnityEngine.Object.Instantiate(filter.sharedMesh);
                mesh.colors=mesh.vertices.Select(v=>
                {
                    var p=Key(room.InverseTransformPoint(node.TransformPoint(v)));
                    if(lookup.TryGetValue(p,out var colour)) return colour;
                    // FBX float rounding can land on the adjacent quantization cell.
                    for(int x=-1;x<=1;x++) for(int y=-1;y<=1;y++) for(int z=-1;z<=1;z++)
                        if(lookup.TryGetValue(p+new Vector3Int(x,y,z),out colour)) return colour;
                    throw new InvalidOperationException("Source hood vertex is missing: "+record.node+" "+p);
                }).ToArray();
                string prefix=SpawnMapBuild.Folder+"Surfaces/"+record.node+"-occlusion";
                AssetDatabase.DeleteAsset(prefix+".asset");AssetDatabase.CreateAsset(mesh,prefix+".asset");filter.sharedMesh=mesh;
                renderer.sharedMaterials=renderer.sharedMaterials.Select((material,index)=>
                {
                    var copy=new Material(material);copy.shader=Shader.Find("CriticalShift/BlenderHood");copy.SetFloat("_VertexOcclusion",1);
                    string path=prefix+"-"+index+".mat";AssetDatabase.DeleteAsset(path);AssetDatabase.CreateAsset(copy,path);return copy;
                }).ToArray();
            }
        }
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
            string fileName=new string(node.name.Select(c=>"<>:\"/\\|?*".IndexOf(c)>=0 ? '_' : c).ToArray());
            string prefix=SpawnMapBuild.Folder+"Surfaces/"+fileName;
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
            if (package == null || (package.room != "spawn-room" && package.room != "mine") || package.lightingIncludedInAlbedo || package.uv != "CS_DeliveryUV")
                throw new InvalidOperationException("Room requires explicit unlit source material maps.");
            string folder = SpawnMapBuild.Folder + "Surfaces/";
            var atlases=new List<(Texture2D albedo,Texture2D normal,Texture2D metallic,Texture2D emission)>();
            for(int index=0;index<package.atlases.Length;index++)
            {
                var maps=package.atlases[index];var definitions=package.definitions.Where(d=>d.atlas==index).ToArray();
                bool mine=package.room=="mine";
                atlases.Add((mine && definitions.All(d=>d.baseConstant) ? null : Texture(maps.albedo,false),
                    mine && definitions.All(d=>d.normalConstant) ? null : Texture(maps.normal,true),
                    mine && definitions.All(d=>d.metallicConstant && d.roughnessConstant) ? null : Texture(maps.metallicSmoothness,false),
                    mine && definitions.All(d=>d.emissionConstant) ? null : Texture(maps.emission,false)));
            }
            var result = new Dictionary<string, Material>();
            foreach (var definition in package.definitions)
            {
                var (albedo,normal,metallic,emission)=atlases[definition.atlas];
                string path = folder + definition.key + ".mat";
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material == null) { material = new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(material, path); }
                material.shader=Shader.Find(definition.thinSurface ? "CriticalShift/BlenderThinVisor" : definition.alphaMapped ? "CriticalShift/BlenderDecal" : definition.transparent ? "CriticalShift/BlenderGlass" : "CriticalShift/BlenderSurface");
                if(material.shader==null) throw new InvalidOperationException("Missing source surface shader.");
                if(definition.thinSurface)
                {
                    material.SetTexture("_ReflectionMap",metallic);material.SetFloat("_ReflectionIOR",definition.reflectionIOR);
                    var c=definition.reflectionColor;material.SetColor("_ReflectionColor",new Color(c[0],c[1],c[2],c[3]));
                    material.SetFloat("_Glossiness",definition.smoothness);material.renderQueue=(int)RenderQueue.Transparent;
                    material.doubleSidedGI=false;material.globalIlluminationFlags=MaterialGlobalIlluminationFlags.EmissiveIsBlack;
                    EditorUtility.SetDirty(material);result.Add(definition.key,material);continue;
                }
                material.doubleSidedGI=!definition.transparent;
                material.color = new Color(1, 1, 1, definition.transparent ? definition.surfaceOpacity : 1);
                material.SetTexture("_MainTex", albedo); material.SetTexture("_BumpMap", normal); material.SetFloat("_BumpScale", 1);
                material.SetTexture("_MetallicGlossMap", metallic); material.SetFloat("_GlossMapScale", 1);
                material.SetFloat("_Metallic",definition.metallic);material.SetFloat("_Glossiness",definition.smoothness);
                if(!definition.transparent || definition.alphaMapped) material.SetFloat("_DielectricSpecular",definition.dielectricSpecular);
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
                if(definition.directAlbedo!=null && !string.IsNullOrEmpty(definition.directAlbedo.file))
                    material.SetTexture("_MainTex",Texture(definition.directAlbedo,false));
                material.SetFloat("_Mode", definition.transparent ? 2 : 0);
                material.SetOverrideTag("RenderType", definition.transparent ? "Transparent" : "Opaque");
                material.SetInt("_SrcBlend", (int)(definition.transparent ? BlendMode.SrcAlpha : BlendMode.One));
                material.SetInt("_DstBlend", (int)(definition.transparent ? BlendMode.OneMinusSrcAlpha : BlendMode.Zero));
                material.SetInt("_ZWrite", definition.transparent ? 0 : 1);
                material.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                if (definition.transparent) material.EnableKeyword("_ALPHABLEND_ON");
                else material.DisableKeyword("_ALPHABLEND_ON");
                // Decals lie under the outer clear visor; retain their source UVs/alpha.
                material.renderQueue = definition.alphaMapped ? (int)RenderQueue.Transparent-10 : definition.transparent ? (int)RenderQueue.Transparent : -1;
                EditorUtility.SetDirty(material); result.Add(definition.key, material);
            }
            AssetDatabase.SaveAssets(); return result;
        }

        internal static Material View(SurfacePackage package)
        {
            var lut = Texture(package.displayLut, false);
            string path = SpawnMapBuild.Folder + "Surfaces/" + (package.room=="spawn-room" ? "BlenderView" : "MineBlenderView") + ".mat";
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
            if(source.file.StartsWith("Surfaces/mine-",StringComparison.Ordinal) &&
                !source.file.Contains("display-lut") && !source.file.EndsWith(".exr",StringComparison.Ordinal))
            {
                var platform=importer.GetPlatformTextureSettings("Standalone");platform.overridden=true;platform.format=normal ? TextureImporterFormat.BC5 : TextureImporterFormat.BC7;
                platform.maxTextureSize=source.size;platform.textureCompression=TextureImporterCompression.CompressedHQ;platform.compressionQuality=100;
                importer.SetPlatformTextureSettings(platform);
            }
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
