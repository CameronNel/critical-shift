using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    internal sealed partial class PhysicalWorldBindings
    {
        private sealed class MedicalPatientBinding
        {
            internal readonly Func<ObjectClaimView, Guid, Transform, Collider, bool, bool> Prepare;
            internal readonly Action<ObjectClaimView, Guid> Reconcile;
            internal readonly Action Cancel, Clear;
            internal MedicalPatientBinding(Func<ObjectClaimView, Guid, Transform, Collider, bool, bool> prepare,
                Action<ObjectClaimView, Guid> reconcile, Action cancel, Action clear)
            {
                Prepare = prepare ?? throw new ArgumentNullException(nameof(prepare));
                Reconcile = reconcile ?? throw new ArgumentNullException(nameof(reconcile));
                Cancel = cancel ?? throw new ArgumentNullException(nameof(cancel)); Clear = clear ?? throw new ArgumentNullException(nameof(clear));
            }
        }
        private sealed class MedicalSlot
        {
            internal readonly Guid Id;
            internal readonly Transform Bed, Discharge, Console;
            internal readonly Collider BedSupport, Floor;
            private readonly Vector3 bedPosition, dischargePosition, consolePosition;
            private readonly Quaternion bedRotation, dischargeRotation, consoleRotation;
            internal MedicalSlot(Guid id, Transform bed, Collider bedSupport, Transform discharge, Collider floor, Transform console)
            {
                Id = id; Bed = bed; BedSupport = bedSupport; Discharge = discharge; Floor = floor; Console = console;
                if (!LiveFrame(bed) || !LiveFrame(discharge) || !LiveFrame(console) || !StaticBox(bedSupport) || !StaticBox(floor))
                    throw new ArgumentException("Bind explicit static medical pose, console and box-support references.");
                bedPosition = bed.position; bedRotation = bed.rotation; dischargePosition = discharge.position; dischargeRotation = discharge.rotation;
                consolePosition = console.position; consoleRotation = console.rotation;
            }
            internal void RequireAvailable()
            {
                if (!LiveFrame(Bed) || !LiveFrame(Discharge) || !LiveFrame(Console) || !StaticBox(BedSupport) || !StaticBox(Floor) ||
                    (Bed.position - bedPosition).sqrMagnitude > 0.0000001f || (Discharge.position - dischargePosition).sqrMagnitude > 0.0000001f ||
                    (Console.position - consolePosition).sqrMagnitude > 0.0000001f ||
                    Mathf.Abs(Quaternion.Dot(Bed.rotation, bedRotation)) < 0.999999f ||
                    Mathf.Abs(Quaternion.Dot(Discharge.rotation, dischargeRotation)) < 0.999999f ||
                    Mathf.Abs(Quaternion.Dot(Console.rotation, consoleRotation)) < 0.999999f)
                    throw new InvalidOperationException("The medical station lost its explicit static placement or console binding.");
            }
            private static bool LiveFrame(Transform value) => value != null && value.gameObject.activeInHierarchy &&
                value.GetComponentInParent<Rigidbody>() == null && value.GetComponentInParent<ArticulationBody>() == null && Finite(value.position) &&
                (value.lossyScale - Vector3.one).sqrMagnitude <= 0.0001f && Finite(value.rotation);
            private static bool StaticBox(Collider support) => support is BoxCollider && support.enabled && !support.isTrigger &&
                support.gameObject.activeInHierarchy && support.GetComponentInParent<Rigidbody>() == null &&
                support.GetComponentInParent<ArticulationBody>() == null && support.includeLayers.value == 0 && support.excludeLayers.value == 0;
            private static bool Finite(Vector3 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) && !float.IsNaN(value.z) &&
                !float.IsInfinity(value.x) && !float.IsInfinity(value.y) && !float.IsInfinity(value.z);
            private static bool Finite(Quaternion value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) && !float.IsNaN(value.z) && !float.IsNaN(value.w) &&
                !float.IsInfinity(value.x) && !float.IsInfinity(value.y) && !float.IsInfinity(value.z) && !float.IsInfinity(value.w) &&
                Mathf.Abs(value.x * value.x + value.y * value.y + value.z * value.z + value.w * value.w - 1) <= 0.001f;
        }
        private readonly Dictionary<Guid, MedicalPatientBinding> medicalPatients = new Dictionary<Guid, MedicalPatientBinding>();
        private MedicalSlot medicalSlot;

        internal void BindMedicalSlot(Guid station, Transform bed, Collider bedSupport, Transform discharge, Collider floor, Transform console)
        {
            if (medicalSlot != null || world.Medical.View?.Id != station || slots.ContainsKey(station))
                throw new InvalidOperationException("Bind the registered medical station once without overlapping an equipment slot.");
            medicalSlot = new MedicalSlot(station, bed, bedSupport, discharge, floor, console);
        }

        internal void BindMedicalWorker(Guid body, Func<ObjectClaimView, Guid, Transform, Collider, bool, bool> prepare,
            Action<ObjectClaimView, Guid> reconcile, Action cancel, Action clear)
        {
            if (!workers.ContainsKey(body) || medicalPatients.ContainsKey(body))
                throw new InvalidOperationException("Bind medical callbacks once after the exact worker-body adapter.");
            medicalPatients.Add(body, new MedicalPatientBinding(prepare, reconcile, cancel, clear));
        }

        internal bool PrepareMedicalMove(Guid station, MedicalAction action, Guid body, out Guid stagedBody)
        {
            stagedBody = Guid.Empty;
            if (medicalSlot == null || medicalSlot.Id != station)
                throw new InvalidOperationException("The medical command has no explicit physical station binding.");
            medicalSlot.RequireAvailable();
            var medical = world.Medical.View;
            if (medical?.Id != station) throw new InvalidOperationException("The bound medical station disappeared.");
            bool entering = action == MedicalAction.Insert;
            if (!entering) body = medical.BodyId;
            if (body == Guid.Empty || world.GetWorkerForBody(body) == null) return false;
            if (!medicalPatients.TryGetValue(body, out var binding))
                throw new InvalidOperationException("The registered patient lost its required physical medical adapter.");
            var claim = world.GetObject(body);
            if (!binding.Prepare(claim, station, entering ? medicalSlot.Bed : medicalSlot.Discharge,
                entering ? medicalSlot.BedSupport : medicalSlot.Floor, entering)) return false;
            stagedBody = body; return true;
        }

        internal void RequireMedicalStation(Guid station)
        {
            if (medicalSlot == null || medicalSlot.Id != station || world.Medical.View?.Id != station)
                throw new InvalidOperationException("Medical work lost its explicit station binding.");
            medicalSlot.RequireAvailable();
            var medical = world.Medical.View;
            if (medical.BodyId == Guid.Empty) return;
            var current = world.GetObject(medical.BodyId);
            if (current == null || current.IsRetired || current.SlotId != station)
                throw new InvalidOperationException("The current medical patient lost its registered body custody.");
            ReconcileMedicalWorker(medical.BodyId, current, station);
        }

        internal void CancelMedicalStage(Guid body)
        { if (medicalPatients.TryGetValue(body, out var binding)) binding.Cancel(); }

        private void ReconcileMedicalWorker(Guid body, ObjectClaimView claim, Guid station)
        {
            if (!medicalPatients.TryGetValue(body, out var binding))
            {
                if (claim.SlotId.HasValue) throw new InvalidOperationException("Slotted worker has no medical placement callbacks.");
                return;
            }
            if (claim.SlotId.HasValue)
            {
                if (medicalSlot == null || medicalSlot.Id != station)
                    throw new InvalidOperationException("Occupied medical slot lost its required binding.");
                medicalSlot.RequireAvailable();
            }
            binding.Reconcile(claim, station);
        }

        private void ClearMedicalWorker(Guid body)
        {
            if (!medicalPatients.TryGetValue(body, out var binding)) return;
            binding.Clear(); medicalPatients.Remove(body);
        }

        private void ClearMedicalBindings()
        {
            foreach (var binding in medicalPatients.Values) binding.Clear();
            medicalPatients.Clear(); medicalSlot = null;
        }
    }
}
