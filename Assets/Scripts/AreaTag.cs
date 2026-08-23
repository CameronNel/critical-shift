using UnityEngine;

namespace CriticalShift
{
    [DisallowMultipleComponent]
    public class AreaTag : MonoBehaviour
    {
        public string areaId;
        public string department;
        public bool isHazardZone;
        public string audioProfile;
        public string notes;
    }
}
