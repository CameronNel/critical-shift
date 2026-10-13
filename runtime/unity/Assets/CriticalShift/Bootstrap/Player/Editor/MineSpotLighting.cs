using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using GiMapping=UnityEngine.Experimental.GlobalIllumination.Lightmapping;
using GiFalloff=UnityEngine.Experimental.GlobalIllumination.FalloffType;

namespace CriticalShift.Player.Editor
{
    // Same measured radiant-power convention as source points. The alpha cookie
    // preserves Cycles' cosine smoothstep cone; RGB identifies physical falloff.
    // A point cookie cannot exactly integrate the source sphere at its cone edge.
    internal static class MineSpotLighting
    {
        internal static void Configure(Light light,ExportLight source)
        {
            ValidateSource(source);
            if(light.cookie!=null) throw new InvalidOperationException("Context spot already has a cookie: "+source.name);
            light.transform.localRotation=Rotation(source);
            light.type=LightType.Spot;light.spotAngle=source.spotSize*Mathf.Rad2Deg;
            light.innerSpotAngle=light.spotAngle;light.intensity=source.power/(4*Mathf.PI*Mathf.PI);
            light.shapeRadius=source.radius;
            string Bits(float f)=>BitConverter.ToInt32(BitConverter.GetBytes(f),0).ToString("x8");
            string path=SpawnMapBuild.Folder+"Surfaces/MineSpot-"+Bits(source.radius)+"-"+Bits(source.spotSize)+"-"+Bits(source.spotBlend)+".asset";
            var existing=AssetDatabase.LoadMainAssetAtPath(path);
            if((existing!=null && !(existing is Texture2D)) || (existing==null && File.Exists(path)))
                throw new InvalidOperationException("Incompatible generated spot asset; regenerate the delivery before creating lights: "+path);
            var cookie=existing as Texture2D;
            if(cookie!=null && !Valid(cookie,source))
            {
                // Deleting a bound cookie and recreating its path before the
                // first camera render produces legacy attenuation and loses the
                // smooth cone in the pinned editor. Preserve texture identity.
                if(!Compatible(cookie))
                    throw new InvalidOperationException("Incompatible generated spot cookie; regenerate the delivery before creating lights: "+path);
                Populate(cookie,source);EditorUtility.SetDirty(cookie);
            }
            if(cookie==null)
            {
                cookie=new Texture2D(128,128,TextureFormat.RGBAHalf,false,true)
                    {name="Mine context physical spot",filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Clamp};
                Populate(cookie,source);AssetDatabase.CreateAsset(cookie,path);
            }
            light.cookie=cookie;
        }

        internal static void ValidateSource(ExportLight source)
        {
            if(source==null || string.IsNullOrEmpty(source.name) || source.type!="SPOT" || !source.normalized || !source.softFalloff ||
                !float.IsFinite(source.power) || source.power<0 || !float.IsFinite(source.radius) || source.radius<=0 ||
                !float.IsFinite(source.spotSize) || source.spotSize<=0 || source.spotSize>179*Mathf.Deg2Rad ||
                !float.IsFinite(source.spotBlend) || source.spotBlend<=0 || source.spotBlend>1 ||
                source.position==null || source.position.Length!=3 || source.position.Any(p=>!float.IsFinite(p)) ||
                source.color==null || source.color.Length!=3 || source.color.Any(c=>!float.IsFinite(c)||c<0) ||
                source.rotation==null || source.rotation.Length!=4 || source.rotation.Any(q=>!float.IsFinite(q)) ||
                source.rotation.Sum(q=>q*q)<.99f || source.rotation.Sum(q=>q*q)>1.01f)
                throw new InvalidOperationException("Unsupported source-physical context spot: "+source?.name);
        }

        private static Quaternion Rotation(ExportLight source)
        {
            var q=source.rotation;var rotation=new Quaternion(q[1],q[2],q[3],q[0]);
            var forward=rotation*Vector3.back;var up=rotation*Vector3.up;
            return Quaternion.LookRotation(new Vector3(forward.x,forward.z,forward.y),new Vector3(up.x,up.z,up.y));
        }

        private static Color Pixel(ExportLight source,int x,int y)
        {
            float tangent=Mathf.Tan(source.spotSize*.5f),outer=Mathf.Cos(source.spotSize*.5f);
            float u=((x+.5f)/128*2-1)*tangent,v=((y+.5f)/128*2-1)*tangent;
            float cosine=1/Mathf.Sqrt(1+u*u+v*v),f=Mathf.Clamp01((cosine-outer)/((1-outer)*source.spotBlend));
            return new Color(.9375f,.03125f,source.radius,f*f*(3-2*f));
        }

        private static bool Valid(Texture2D cookie,ExportLight source)
        {
            if(!Compatible(cookie) ||
                cookie.filterMode!=FilterMode.Bilinear || cookie.wrapMode!=TextureWrapMode.Clamp) return false;
            for(int y=0;y<128;y++) for(int x=0;x<128;x++)
            {
                var actual=cookie.GetPixel(x,y);var expected=Pixel(source,x,y);
                if(!float.IsFinite(actual.r)||!float.IsFinite(actual.g)||!float.IsFinite(actual.b)||!float.IsFinite(actual.a)||
                    Mathf.Abs(actual.r-expected.r)>.0001f || Mathf.Abs(actual.g-expected.g)>.0001f ||
                    Mathf.Abs(actual.b-expected.b)>Mathf.Max(.000001f,source.radius*.0006f) ||
                    Mathf.Abs(actual.a-expected.a)>.0005f) return false;
            }
            return true;
        }

        private static bool Compatible(Texture2D cookie)=>cookie.width==128 && cookie.height==128 &&
            cookie.format==TextureFormat.RGBAHalf && cookie.mipmapCount==1 && cookie.isReadable && !cookie.isDataSRGB;

        private static void Populate(Texture2D cookie,ExportLight source)
        {
            cookie.filterMode=FilterMode.Bilinear;cookie.wrapMode=TextureWrapMode.Clamp;
            for(int y=0;y<128;y++) for(int x=0;x<128;x++) cookie.SetPixel(x,y,Pixel(source,x,y));
            cookie.Apply(false,false);
        }

        internal static IDisposable ScopeBake(Transform room,ExportLight[] sources)=>new BakeScope(room,sources);

        [Serializable] private sealed class SpotBakeRecord
        {
            public string name, type, configuredMode, bakedMode, shadows, cookiePath, cookieGuid;
            public bool isBaked, cookieMatchesSource;
            public float intensity, range, spotAngle, innerSpotAngle, radius;
            public Vector3 position;
            public Quaternion rotation;
            public Color color;
        }

        [Serializable] private sealed class SpotBakeInventory
        {
            public string unityVersion, preparedSceneSha256;
            public int lightmaps;
            public SpotBakeRecord[] spots;
        }

        // Observe the saved scene after reopening it for a capture. Record actual
        // bake output separately from the requested mode; do not repair lights here.
        internal static void RecordBakeOutput(Transform room,ExportLight[] sources)
        {
            if(sources==null || sources.Length!=6 || sources.Select(s=>s.name).Distinct().Count()!=6)
                throw new InvalidOperationException("Missing the six authored context spotlights.");
            var lights=room.GetComponentsInChildren<Light>(true);
            var records=sources.Select(source=>
            {
                ValidateSource(source);
                var light=lights.Single(l=>l.name==source.name);
                var output=light.bakingOutput;
                var cookie=light.cookie as Texture2D;
                string path=cookie==null ? "" : AssetDatabase.GetAssetPath(cookie);
                return new SpotBakeRecord
                {
                    name=source.name,type=light.type.ToString(),configuredMode=light.lightmapBakeType.ToString(),
                    bakedMode=output.lightmapBakeType.ToString(),isBaked=output.isBaked,
                    shadows=light.shadows.ToString(),intensity=light.intensity,range=light.range,
                    spotAngle=light.spotAngle,innerSpotAngle=light.innerSpotAngle,radius=light.shapeRadius,
                    position=light.transform.localPosition,rotation=light.transform.localRotation,color=light.color,
                    cookiePath=path,cookieGuid=string.IsNullOrEmpty(path) ? "" : AssetDatabase.AssetPathToGUID(path),
                    cookieMatchesSource=cookie!=null && Valid(cookie,source)
                };
            }).ToArray();
            if(records.Any(r=>r.type!="Spot" || !r.cookieMatchesSource || string.IsNullOrEmpty(r.cookiePath) ||
                r.cookieGuid.Length!=32 || !File.Exists(r.cookiePath) ||
                !float.IsFinite(r.intensity) || r.intensity<0 || !float.IsFinite(r.range) || r.range<=0 ||
                !float.IsFinite(r.spotAngle) || !float.IsFinite(r.innerSpotAngle) || !float.IsFinite(r.radius) || r.radius<=0 ||
                !float.IsFinite(r.position.x) || !float.IsFinite(r.position.y) || !float.IsFinite(r.position.z) ||
                !float.IsFinite(r.rotation.x) || !float.IsFinite(r.rotation.y) || !float.IsFinite(r.rotation.z) || !float.IsFinite(r.rotation.w) ||
                !float.IsFinite(r.color.r) || !float.IsFinite(r.color.g) || !float.IsFinite(r.color.b) || !float.IsFinite(r.color.a)))
                throw new InvalidOperationException("Persisted context spotlight inventory is invalid.");
            using var hash=SHA256.Create();
            File.WriteAllText(SpawnMapBuild.Folder+"mine-spot-bake-output.json",JsonUtility.ToJson(new SpotBakeInventory
            {
                unityVersion=UnityEngine.Application.unityVersion,lightmaps=LightmapSettings.lightmaps.Length,spots=records,
                preparedSceneSha256=BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes(SpawnMapBuild.Folder+"prepared-scene.json")))
                    .Replace("-","").ToLowerInvariant()
            },true));
            Debug.Log("CS_MINE_ACTUAL_SPOT_BAKE_OUTPUT; spots="+records.Length);
        }

        private sealed class BakeScope : IDisposable
        {
            private readonly GiMapping.RequestLightsDelegate previous;
            private bool disposed;
            internal BakeScope(Transform room,ExportLight[] sources)
            {
                if(sources==null || sources.Length==0 || sources.Select(s=>s.name).Distinct().Count()!=sources.Length)
                    throw new InvalidOperationException("Missing or duplicate authored context spots.");
                var all=room.GetComponentsInChildren<Light>(true);var ids=new HashSet<EntityId>();
                foreach(var source in sources)
                {
                    ValidateSource(source);
                    var light=all.Single(l=>l.name==source.name);
                    var position=light.transform.localPosition;var rotation=light.transform.localRotation;var color=light.color;
                    if(light.type!=LightType.Spot || !(light.cookie is Texture2D cookie) || !Valid(cookie,source) ||
                        !float.IsFinite(position.x)||!float.IsFinite(position.y)||!float.IsFinite(position.z)||
                        !float.IsFinite(rotation.x)||!float.IsFinite(rotation.y)||!float.IsFinite(rotation.z)||!float.IsFinite(rotation.w)||
                        !float.IsFinite(color.r)||!float.IsFinite(color.g)||!float.IsFinite(color.b)||!float.IsFinite(color.a)||
                        !float.IsFinite(light.intensity) || !float.IsFinite(light.range) || light.range<=0 ||
                        !float.IsFinite(light.spotAngle) || !float.IsFinite(light.innerSpotAngle) || !float.IsFinite(light.shapeRadius) ||
                        Mathf.Abs(light.intensity-source.power/(4*Mathf.PI*Mathf.PI))>.0001f ||
                        Mathf.Abs(light.spotAngle-source.spotSize*Mathf.Rad2Deg)>.0001f ||
                        Mathf.Abs(light.innerSpotAngle-light.spotAngle)>.0001f || Mathf.Abs(light.shapeRadius-source.radius)>.00001f ||
                        light.shadows!=LightShadows.Soft || Quaternion.Angle(light.transform.localRotation,Rotation(source))>.01f ||
                        Vector3.Distance(light.transform.localPosition,new Vector3(source.position[0],source.position[2],source.position[1]))>.0001f ||
                        Vector4.Distance(light.color,new Color(source.color[0],source.color[1],source.color[2]).gamma)>.0001f)
                        throw new InvalidOperationException("Context spot does not match its source: "+source.name);
                    ids.Add(light.GetEntityId());
                }
                previous=GiMapping.GetDelegate();
                GiMapping.SetDelegate((requests,output)=>
                {
                    previous(requests,output);
                    for(int i=0;i<requests.Length;i++) if(ids.Contains(requests[i].GetEntityId()))
                    {var data=output[i];data.falloff=GiFalloff.InverseSquaredNoRangeAttenuation;output[i]=data;}
                });
            }
            public void Dispose()
            {
                if(disposed)return;
                GiMapping.SetDelegate(previous);disposed=true;
            }
        }
    }
}
