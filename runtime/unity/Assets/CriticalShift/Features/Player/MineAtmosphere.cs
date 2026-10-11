using System;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    [Serializable] public sealed class MineFogVolume
    {
        public Vector3 minimum,maximum,grid;
        public Color color;
        public Texture2D density,lighting;
    }

    // Source density stays in Blender. Unity supplies baked illumination and depth.
    [RequireComponent(typeof(Camera))]
    [ExecuteAlways]
    public sealed class MineAtmosphere : MonoBehaviour
    {
        [SerializeField] private Material profile;
        [SerializeField] private MineFogVolume[] volumes;
        private Material instance;
        private void OnEnable() => GetComponent<Camera>().depthTextureMode|=DepthTextureMode.Depth;
        public void Configure(Material material,MineFogVolume[] source)
        {
            if(material==null || source==null || source.Length>2) throw new ArgumentException("Invalid mine atmosphere delivery.");
            profile=material;volumes=source;GetComponent<Camera>().depthTextureMode|=DepthTextureMode.Depth;
        }
        private void OnRenderImage(RenderTexture source,RenderTexture destination)
        {
            if(profile==null || volumes==null || volumes.Length==0) { Graphics.Blit(source,destination);return; }
            if(instance==null) instance=new Material(profile) {hideFlags=HideFlags.HideAndDontSave};
            var camera=GetComponent<Camera>();camera.depthTextureMode|=DepthTextureMode.Depth;
            instance.SetMatrix("_InvProjection",GL.GetGPUProjectionMatrix(camera.projectionMatrix,true).inverse);
            instance.SetMatrix("_MineCameraToWorld",camera.cameraToWorldMatrix);
            instance.SetVector("_Origin",camera.transform.position);instance.SetInt("_VolumeCount",volumes.Length);
            for(int i=0;i<volumes.Length;i++)
            {
                var volume=volumes[i];instance.SetVector("_Minimum"+i,volume.minimum);instance.SetVector("_Maximum"+i,volume.maximum);
                instance.SetVector("_Grid"+i,volume.grid);instance.SetColor("_Scatter"+i,volume.color);
                instance.SetTexture("_Density"+i,volume.density);instance.SetTexture("_Lighting"+i,volume.lighting);
            }
            Graphics.Blit(source,destination,instance);
        }
        private void OnDisable()
        {
            if(instance!=null)
            {
                if(UnityEngine.Application.isPlaying) Destroy(instance);
                else DestroyImmediate(instance);
            }
            instance=null;
        }
    }
}
