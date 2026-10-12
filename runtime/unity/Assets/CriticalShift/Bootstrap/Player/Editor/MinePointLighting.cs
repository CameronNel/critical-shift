using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using GiMapping=UnityEngine.Experimental.GlobalIllumination.Lightmapping;
using GiFalloff=UnityEngine.Experimental.GlobalIllumination.FalloffType;

namespace CriticalShift.Player.Editor
{
    // Cycles point power is total radiant flux. The built-in diffuse BRDF omits
    // /pi, so its inverse-square intensity is power/(4*pi*pi). Independent native
    // far-field baked and Forward Lambert controls establish this conversion.
    // The native bake's finite-radius mismatch remains explicitly unresolved.
    internal static class MinePointLighting
    {
        internal static void Configure(Light light,ExportLight source)
        {
            if(source.type!="POINT" || light.type!=LightType.Point || light.cookie!=null ||
                !float.IsFinite(source.power) || source.power<0 || !float.IsFinite(source.radius) || source.radius<0)
                throw new InvalidOperationException("Unsupported source-physical mine point: "+source.name);
            light.intensity=source.power/(4*Mathf.PI*Mathf.PI);
            float radius=Mathf.Max(source.radius,.001f);
            string path=SpawnMapBuild.Folder+"Surfaces/MinePointRadius-"+
                BitConverter.ToInt32(BitConverter.GetBytes(radius),0).ToString("x8")+".asset";
            var cookie=AssetDatabase.LoadAssetAtPath<Cubemap>(path);
            if(cookie!=null && !ValidCookie(cookie,radius))
            {
                // Generated assets are disposable. Rebuild a stale marker before
                // saving the current scene rather than silently using stock falloff.
                AssetDatabase.DeleteAsset(path);cookie=null;
            }
            if(cookie==null)
            {
                cookie=new Cubemap(1,TextureFormat.RGBAHalf,false) {name="Mine physical point identity",filterMode=FilterMode.Point,wrapMode=TextureWrapMode.Clamp};
                foreach(var face in new[] {CubemapFace.PositiveX,CubemapFace.NegativeX,CubemapFace.PositiveY,CubemapFace.NegativeY,CubemapFace.PositiveZ,CubemapFace.NegativeZ})
                    cookie.SetPixels(new[] {new Color(.9375f,.03125f,radius,1)},face);
                cookie.Apply(false,false);AssetDatabase.CreateAsset(cookie,path);
            }
            light.cookie=cookie;
        }

        private static bool ValidCookie(Cubemap cookie,float radius)
        {
            if(cookie.width!=1 || cookie.height!=1 || cookie.format!=TextureFormat.RGBAHalf ||
                cookie.mipmapCount!=1 || !cookie.isReadable || cookie.filterMode!=FilterMode.Point ||
                cookie.wrapMode!=TextureWrapMode.Clamp) return false;
            foreach(var face in new[] {CubemapFace.PositiveX,CubemapFace.NegativeX,CubemapFace.PositiveY,CubemapFace.NegativeY,CubemapFace.PositiveZ,CubemapFace.NegativeZ})
            {
                var pixel=cookie.GetPixel(face,0,0);
                // Source radius is quantized to half in the identity texture.
                if(!float.IsFinite(pixel.r) || !float.IsFinite(pixel.g) || !float.IsFinite(pixel.b) || !float.IsFinite(pixel.a) ||
                    Mathf.Abs(pixel.r-.9375f)>.0001f || Mathf.Abs(pixel.g-.03125f)>.0001f ||
                    Mathf.Abs(pixel.b-radius)>Mathf.Max(.000001f,radius*.0006f) || Mathf.Abs(pixel.a-1)>.0001f) return false;
            }
            return true;
        }

        internal static IDisposable ScopeBake(Transform mine)=>new BakeScope(mine);

        private sealed class BakeScope : IDisposable
        {
            private readonly GiMapping.RequestLightsDelegate previous;
            private readonly Dictionary<Light,float> runtimeIntensities;
            private bool disposed;
            internal BakeScope(Transform mine)
            {
                previous=GiMapping.GetDelegate();
                runtimeIntensities=mine.GetComponentsInChildren<Light>().Where(l=>l.type==LightType.Point)
                    .ToDictionary(l=>l,l=>l.intensity);
                var ids=new HashSet<EntityId>(runtimeIntensities.Keys.Select(l=>l.GetEntityId()));
                // Diagnostic baseline only. The pinned Progressive CPU Soft
                // inverse-square control receives shapeRadius but still differs
                // from Cycles near the emitter. Preserve existing legacy GI until
                // a source-radiance transfer passes independent visual review.
                foreach(var pair in runtimeIntensities) pair.Key.intensity=pair.Value*(4*Mathf.PI*Mathf.PI)/100;
                GiMapping.SetDelegate((requests,output)=>
                {
                    previous(requests,output);
                    for(int index=0;index<requests.Length;index++)
                        if(ids.Contains(requests[index].GetEntityId()))
                        {
                            var data=output[index];data.falloff=GiFalloff.Legacy;output[index]=data;
                        }
                });
            }
            public void Dispose()
            {
                if(disposed) return;
                GiMapping.SetDelegate(previous);disposed=true;
                foreach(var pair in runtimeIntensities) if(pair.Key!=null) pair.Key.intensity=pair.Value;
            }
        }
    }
}
