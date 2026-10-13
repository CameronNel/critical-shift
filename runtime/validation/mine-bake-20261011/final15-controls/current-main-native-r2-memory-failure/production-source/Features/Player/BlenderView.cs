using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    // Display-only transform exported using the source Blender colour configuration.
    [RequireComponent(typeof(Camera))]
    [ExecuteAlways]
    public sealed class BlenderView : MonoBehaviour
    {
        [SerializeField] private Material displayTransform;
        [SerializeField] private Material outsideTransform;
        [SerializeField] private Bounds localDisplayBounds;
        [SerializeField] private Color outsideBackgroundColor;
        private Color savedBackgroundColor;
        public void Configure(Material material) => displayTransform = material;
        public void ConfigureOutside(Bounds bounds, Material material,Color background)
        { localDisplayBounds=bounds;outsideTransform=material;outsideBackgroundColor=background; }
        private void OnPreRender()
        {
            var camera=GetComponent<Camera>();savedBackgroundColor=camera.backgroundColor;
            if(outsideTransform!=null && !localDisplayBounds.Contains(transform.position)) camera.backgroundColor=outsideBackgroundColor;
        }
        private void OnPostRender() => GetComponent<Camera>().backgroundColor=savedBackgroundColor;
        private void OnRenderImage(RenderTexture source, RenderTexture destination)
        {
            var material=outsideTransform!=null && !localDisplayBounds.Contains(transform.position) ? outsideTransform : displayTransform;
            if (material == null) Graphics.Blit(source, destination);
            else Graphics.Blit(source, destination, material);
        }
    }
}
