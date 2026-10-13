using System;
using System.Collections.Generic;
using System.Linq;
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
            var cookie=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if(cookie!=null && !Valid(cookie,source)){AssetDatabase.DeleteAsset(path);cookie=null;}
            if(cookie==null)
            {
                cookie=new Texture2D(128,128,TextureFormat.RGBAHalf,false,true)
                    {name="Mine context physical spot",filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Clamp};
                for(int y=0;y<128;y++) for(int x=0;x<128;x++) cookie.SetPixel(x,y,Pixel(source,x,y));
                cookie.Apply(false,false);AssetDatabase.CreateAsset(cookie,path);
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
            if(cookie.width!=128 || cookie.height!=128 || cookie.format!=TextureFormat.RGBAHalf ||
                cookie.mipmapCount!=1 || !cookie.isReadable || cookie.isDataSRGB ||
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

        internal static IDisposable ScopeBake(Transform room,ExportLight[] sources)=>new BakeScope(room,sources);

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
