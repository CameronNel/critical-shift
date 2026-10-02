using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    // Authored registration only; live quantities/revisions stay in ProductionOperations.
    public sealed class MaterialBinding : MonoBehaviour
    {
        [SerializeField] private MaterialKind kind;
        [SerializeField] private int units = 100, moisture, contamination;
        public MaterialKind Kind => kind;
        public int Units => units;
        public int Moisture => moisture;
        public int Contamination => contamination;
    }
}
