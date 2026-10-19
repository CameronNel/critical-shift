#nullable enable
using System;
using CriticalShift.Application;

namespace CriticalShift.Sandbox
{
    /// <summary>Canonical logical stock, recipes and objectives for the local sandbox. No physical bindings.</summary>
    internal static class SandboxGameplaySetup
    {
        internal const int ContainerCount = 8;
        internal const long ShiftDurationMilliseconds = 12 * 60 * 1000;
        internal static Guid CrusherId => Id(400);
        internal static Guid ProcessorId => Id(401);
        internal static Guid DryerId => Id(402);
        internal static Guid WasherId => Id(403);
        internal static Guid SuitStationId => Id(710);
        internal static Guid ExposureSourceId => Id(720);
        internal static Guid WashSourceId => Id(721);
        internal static Guid MedicalStationId => Id(730);
        internal static Guid ReactorId => Id(500);
        internal static Guid ContainerId(int index)
        {
            if (index < 0 || index >= ContainerCount) throw new ArgumentOutOfRangeException(nameof(index));
            return Id(100 + index);
        }
        internal static WorldSessionConfiguration Configuration() =>
            new WorldSessionConfiguration(7, ShiftDurationMilliseconds, true, maxObjects: 32);

        // Trusted, one-shot composition. A failed setup is disposed by its caller rather than retried partially.
        internal static void Register(WorldSession world)
        {
            if (world == null) throw new ArgumentNullException(nameof(world));
            if (world.View.Phase != WorldPhase.Setup || world.Configuration.ShiftDurationMilliseconds != ShiftDurationMilliseconds)
                throw new InvalidOperationException("The sandbox requires fresh setup with its authored shift duration.");
            for (int i = 0; i < ContainerCount; i++)
                world.Production.RegisterBatch(ContainerId(i), Id(200 + i), Id(300), Id(310 + i),
                    i == 6 ? MaterialKind.Fuel : MaterialKind.Ore, i == 0 ? 36 : 12,
                    moisture: i == 7 ? 850 : 100, contamination: i == 5 ? 800 : 0);
            world.Production.RegisterMachine(CrusherId, new MachineRecipe(Id(450), MaterialKind.Ore, MaterialKind.CrushedOre,
                6000, 3000, 1500, 128, yieldPermille: 950, repairDurationMilliseconds: 6000, reserveCost: 1));
            world.Production.RegisterMachine(ProcessorId, new MachineRecipe(Id(451), MaterialKind.CrushedOre, MaterialKind.Fuel,
                9000, 4500, 1500, 128, repairDurationMilliseconds: 8000, reserveCost: 2));
            world.Production.RegisterMachine(DryerId, MachineRecipe.Drying(Id(452), MaterialKind.Ore, 8000, 128, 100, reserveCost: 1));
            world.Production.RegisterMachine(WasherId, MachineRecipe.Washing(Id(453), MaterialKind.Ore, 10000, 128, 100, reserveCost: 1));
            world.Reactor.Register(ReactorId, new ReactorDefinition(Id(501), millisecondsPerFuelUnit: 5000,
                powerQuantumMilliseconds: 500, warningMilliseconds: 6000, tripMilliseconds: 12000,
                resetMilliseconds: 1000, emergencyReliefMilliseconds: 5000));
            world.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition());
            world.SuitFitting.Register(SuitStationId, new SuitFittingDefinition());
            world.Medical.Register(MedicalStationId, new MedicalDefinition());
            world.RegisterWorkerContaminationSource(ExposureSourceId, new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 12, 1000));
            world.RegisterWorkerContaminationSource(WashSourceId, new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, 25, 1000));
            world.Contracts.Register(new ShiftContractDefinition(Id(800), "Restore the city supply",
                new GridDemandWave(Id(801), "Prepare fuel and cooling", 2 * 60 * 1000, 0),
                new GridDemandWave(Id(802), "Morning supply", 6 * 60 * 1000, 800, 30 * 1000),
                new GridDemandWave(Id(803), "Industrial demand", 9 * 60 * 1000, 850, 45 * 1000),
                new GridDemandWave(Id(804), "Peak grid request", ShiftDurationMilliseconds, 1100, 60 * 1000)));
        }
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
    }
}
