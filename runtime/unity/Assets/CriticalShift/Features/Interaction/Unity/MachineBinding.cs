using System;
using CriticalShift.Application;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    public enum MachineBindingKind { Production, Reactor }
    [DisallowMultipleComponent]
    public sealed class MachineBinding : SceneTarget
    {
        [SerializeField] private MachineBindingKind kind;
        [SerializeField] private ProductionAction productionAction = ProductionAction.Start;
        [SerializeField] private ReactorAction reactorAction = ReactorAction.Start;
        [SerializeField] private MachineBinding machine;
        [SerializeField] private Transform slot;
        [SerializeField] private MaterialKind input = MaterialKind.Ore, output = MaterialKind.CrushedOre;
        [SerializeField] private int units = 1000, durationMilliseconds = 5000;
        [SerializeField] private bool poweredValue = true, bypassInspection;
        public MachineBindingKind Kind => kind;
        public MachineBinding Machine => machine != null ? machine : this;
        public Transform Slot => Machine.slot;
        public ProductionAction ProductionAction => productionAction;
        public ReactorAction ReactorAction => reactorAction;
        public bool PoweredValue => poweredValue;
        public bool BypassInspection => bypassInspection;
        public MachineRecipe Recipe => new MachineRecipe(Id, input, output, durationMilliseconds,
            Math.Max(2, durationMilliseconds / 2), Math.Max(1, durationMilliseconds / 4), units);
        public ReactorDefinition Definition => new ReactorDefinition(Id);
        public override bool Supports(SceneOperation value) => value == Operation;
        public override bool Apply(WorkerScenePort worker, SceneOperation value, long generation) => Supports(value);
        public override void ClearBinding() { }
    }
}
