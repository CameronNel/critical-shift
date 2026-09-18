using System;
using System.Collections.Generic;
using CriticalShift.Features.Materials.Domain;
using CriticalShift.Features.Production.Domain;

namespace CriticalShift.Application
{
    public sealed partial class ProductionOperations
    {
        internal IReadOnlyList<ProductionChange> AdvanceTo(long shiftMilliseconds)
        {
            var changes = new List<ProductionChange>();
            var ids = new List<Guid>(_machines.Keys); ids.Sort();
            foreach (var id in ids)
            {
                var next = _machines[id].AdvanceTo(shiftMilliseconds, out var signal);
                if (signal == MachineSignal.Completed)
                {
                    var receipt = _materials.Finish(next.CycleId, false);
                    if (receipt.Status != ConversionStatus.Completed) throw new InvalidOperationException("Cancelled cycle attempted completion.");
                    _completed++; _machines[id] = next;
                    changes.Add(Conversion(receipt, next));
                }
                else
                {
                    _machines[id] = next;
                    if (signal == MachineSignal.Jammed)
                    {
                        var plan = _materials.GetPending(next.CycleId);
                        var container = _interaction.SlotOccupant(id);
                        if (plan == null || container != plan.Input.ContainerId ||
                            !ReferenceEquals(_materials.Get(plan.Input.ContainerId), plan.Input))
                            throw new InvalidOperationException("Active process lost its reserved input or custody.");
                        changes.Add(new ProductionChange(ProductionEvent.Jammed, Project(next), Project(plan.Input)!, null, 0,
                            plan.CycleId, plan.RecipeId, plan.BypassedInspection));
                    }
                }
            }
            return changes.AsReadOnly();
        }
        internal void Clear()
        {
            if (_final != null) return;
            // Preserve a detached terminal accounting summary, never a live second inventory.
            _final = new ProductionSummary(_materials.IssuedUnits, _materials.ActiveUnits, _materials.WasteUnits,
                _completed, _cancelled + _materials.PendingCount, 0);
            _machines.Clear(); _recipes.Clear(); _materials.Clear();
        }
        private ProductionChange Conversion(ConversionReceipt r, MachineState state) =>
            new ProductionChange(r.Status == ConversionStatus.Completed ? ProductionEvent.Completed : ProductionEvent.Cancelled,
                // Keep the resulting machine view and the original cycle identity separate.
                Project(state), Project(r.Plan.Input)!,
                r.Status == ConversionStatus.Completed ? Project(r.Plan.Output) : null,
                r.Status == ConversionStatus.Completed ? r.Plan.WasteUnits : 0,
                r.Plan.CycleId, r.Plan.RecipeId, r.Plan.BypassedInspection);
        private ConversionView Project(ConversionReceipt r) => new ConversionView(r.Plan.CycleId,
            r.Plan.MachineId, r.Plan.RecipeId, r.Status == ConversionStatus.Cancelled,
            Project(r.Plan.Input)!, r.Status == ConversionStatus.Completed ? Project(r.Plan.Output) : null,
            r.Status == ConversionStatus.Completed ? r.Plan.WasteUnits : 0, r.Plan.BypassedInspection);
        private MaterialView? Project(BatchSnapshot? b) => b == null ? null : new MaterialView(_world.Epoch,
            b.ContainerId, b.BatchId, b.ParentId, b.OriginId, b.CauseId, (MaterialKind)(int)b.Kind,
            b.Units, b.Moisture, b.Contamination, b.Revision, (MaterialFlags)(int)b.Flags);
        private MachineView Project(MachineState s) => new MachineView(_world.Epoch,
            s.Id, _recipes[s.Id].Id, s.Revision, (ProductionMode)(int)s.Mode, s.Powered, s.CycleId,
            _interaction.SlotOccupant(s.Id), s.DurationMilliseconds, s.WorkMilliseconds);
        private InteractionReply Reply(ProductionStatus status, MachineState? machine,
            ObjectClaimView? custody = null, InteractionStatus? custodyError = null, ProductionChange? change = null)
        {
            var view = machine == null ? null : Project(machine);
            var batch = custody != null ? GetBatch(custody.EntityId) :
                view?.ContainerId is Guid container ? GetBatch(container) : null;
            var outcome = status == ProductionStatus.Applied ? InteractionStatus.Applied :
                status == ProductionStatus.NoChange ? InteractionStatus.NoChange : custodyError ?? InteractionStatus.ProductionRejected;
            return new InteractionReply(outcome, true, custody, production: new ProductionReply(status, view, batch, change));
        }
    }
}
