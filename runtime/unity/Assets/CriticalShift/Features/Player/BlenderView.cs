using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    // Display-only transform exported using the source Blender colour configuration.
    [RequireComponent(typeof(Camera))]
    [ExecuteAlways]
    public sealed class BlenderView : MonoBehaviour
    {
        [SerializeField] private Material displayTransform;
        public void Configure(Material material) => displayTransform = material;
        private void OnRenderImage(RenderTexture source, RenderTexture destination)
        {
            if (displayTransform == null) Graphics.Blit(source, destination);
            else Graphics.Blit(source, destination, displayTransform);
        }
    }
}
