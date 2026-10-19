using System;
using System.Globalization;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class MachineReadoutTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        [Test] public void MachineReadoutUsesActualImmutableRecipeValuesAndDerivedAliases()
        {
            var f = new ProductionFixture(); var state = f.World.Production.GetMachine(f.Machine)!; var recipe = state.Recipe;
            var text = SandboxMachineReadout.Recipe(state);
            Assert.That(text, Does.Contain("ore → crushed ore").And.Contain("1000 units").And.Contain("Normal 1s").And.Contain("bypass 0.5s").And.Contain("50%"));
            Assert.That(text, Does.Contain("jams after 0.2s")); Assert.That(state.RecipeId, Is.EqualTo(recipe.Id));
            Assert.That(state.IsDrying, Is.EqualTo(recipe.IsDrying)); Assert.That(state.DryingTargetMoisture, Is.Null);
            f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(1000); f.World.Stop();
            Assert.That(state.Mode, Is.EqualTo(ProductionMode.Idle)); Assert.That(state.Recipe, Is.SameAs(recipe));
            Assert.That(SandboxMachineReadout.Recipe(state), Is.EqualTo(text));
        }

        [TestCase(false)] [TestCase(true)]
        public void CurrentBypassFactComesFromTheCycleEvenWhenBothDurationsAreEqual(bool bypass)
        {
            var world = new WorldSession(new WorldSessionConfiguration(42, 10000), new TestAccess()); world.RegisterConnection(Id(20), Id(10));
            world.Production.RegisterMachine(Id(40), new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 1000, 100, 100));
            world.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), MaterialKind.Ore, 10);
            var port = new LocalCommandPort(world, Id(20)); world.Start(); port.Grab(Id(30)); port.OperateMachine(Id(40), ProductionAction.Insert, Id(30));
            var start = port.OperateMachine(Id(40), ProductionAction.Start, bypass: bypass); var historical = start.Production!.Machine!;
            Assert.That(historical.DurationMilliseconds, Is.EqualTo(1000)); Assert.That(historical.BypassedInspection, Is.EqualTo(bypass));
            world.AdvanceTo(1000); Assert.That(world.Production.GetMachine(Id(40))!.BypassedInspection, Is.EqualTo(bypass));
            Assert.That(world.Production.GetMachine(Id(40))!.Mode, Is.EqualTo(ProductionMode.OutputReady));
            port.OperateMachine(Id(40), ProductionAction.Eject); Assert.That(world.Production.GetMachine(Id(40))!.BypassedInspection, Is.False);
            Assert.That(historical.BypassedInspection, Is.EqualTo(bypass)); world.Stop();
        }

        [Test] public void InheritedSuspectInputDoesNotRelabelTheCurrentNormalCycle()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start, bypass: true); f.World.AdvanceTo(500);
            Assert.That(f.World.Production.GetBatch(f.Box)!.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            f.Act(ProductionAction.Eject); f.Grab(); f.Act(ProductionAction.Insert, f.Press); f.Act(ProductionAction.Start, f.Press);
            var normal = f.World.Production.GetMachine(f.Press)!; Assert.That(normal.BypassedInspection, Is.False);
            Assert.That(normal.Recipe.Input, Is.EqualTo(MaterialKind.CrushedOre)); f.World.AdvanceTo(1500);
            Assert.That(f.World.Production.GetMachine(f.Press)!.BypassedInspection, Is.False);
            Assert.That(f.World.Production.GetBatch(f.Box)!.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
        }

        [Test] public void CancelClearsCurrentBypassWhileRetainingItsHistoricalCycleFact()
        {
            var f = new ProductionFixture(); f.Load(); var start = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!;
            f.Act(ProductionAction.SetPower, power: false); f.Act(ProductionAction.CancelCycle);
            Assert.That(f.World.Production.GetMachine(f.Machine)!.BypassedInspection, Is.False);
            Assert.That(f.World.Production.GetConversion(start.CycleId)!.BypassedInspection, Is.True); Assert.That(start.BypassedInspection, Is.True);
        }

        [TestCase(false)] [TestCase(true)]
        public void JamHintRequiresIsolationOnlyWhilePowerIsActuallyOn(bool powered)
        {
            var f = new ProductionFixture(moisture: 900); f.Load(); f.Act(ProductionAction.Start, bypass: true); f.World.AdvanceTo(200);
            if (!powered) f.Act(ProductionAction.SetPower, power: false);
            var hint = SandboxMachineReadout.Controls(f.World.Production.GetMachine(f.Machine)!);
            if (powered)
            {
                Assert.That(hint, Does.Contain("F isolate power"));
                Assert.That(f.Act(ProductionAction.Repair).Production!.Status, Is.EqualTo(ProductionStatus.PowerMustBeOff));
            }
            else
            {
                Assert.That(hint, Does.Contain("R repair jam").And.Not.Contain("F isolate power"));
                Assert.That(f.Act(ProductionAction.Repair).HasNewCommit, Is.True);
            }
        }

        [TestCase(false)] [TestCase(true)]
        public void PausedCycleHintReflectsRestoredPowerBeforeExplicitResume(bool powered)
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(100); f.Act(ProductionAction.SetPower, power: false);
            if (powered) f.Act(ProductionAction.SetPower, power: true);
            var state = f.World.Production.GetMachine(f.Machine)!; Assert.That(state.Mode, Is.EqualTo(ProductionMode.PowerPaused));
            var hint = SandboxMachineReadout.Controls(state);
            if (powered) Assert.That(hint, Does.StartWith("R resume cycle").And.Not.Contain("F restore power"));
            else Assert.That(hint, Does.Contain("F restore power"));
            var resumed = f.Act(ProductionAction.Resume); Assert.That(resumed.Production!.Status, Is.EqualTo(powered ? ProductionStatus.Applied : ProductionStatus.NoPower));
        }

        [TestCase(false)] [TestCase(true)]
        public void OutputHintKeepsEjectionAvailableWithEitherPowerState(bool powered)
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(1000);
            if (!powered) f.Act(ProductionAction.SetPower, power: false);
            string hint = SandboxMachineReadout.Controls(f.World.Production.GetMachine(f.Machine)!);
            Assert.That(hint, Does.Contain("E eject output").And.Contain(powered ? "F isolates power" : "F restores power"));
            Assert.That(f.Act(ProductionAction.Eject).HasNewCommit, Is.True);
        }

        [TestCase(false, false)] [TestCase(false, true)] [TestCase(true, false)] [TestCase(true, true)]
        public void IdleHintDoesNotOfferStartBeforeItsInputAndPowerAreReady(bool loaded, bool powered)
        {
            var f = new ProductionFixture(); if (loaded) f.Load(); if (!powered) f.Act(ProductionAction.SetPower, power: false);
            var hint = SandboxMachineReadout.Controls(f.World.Production.GetMachine(f.Machine)!);
            if (!loaded) Assert.That(hint, Does.Contain("E insert").And.Not.Contain("R start"));
            else if (!powered) Assert.That(hint, Does.Contain("F restore power").And.Not.Contain("R start"));
            else Assert.That(hint, Does.Contain("R start normal cycle").And.Contain("B bypass inspection"));
        }

        [Test] public void WetInputAndPowerInterlockRejectionsExplainTheSafeNextAction()
        {
            var f = new ProductionFixture(moisture: 900); f.Load(); long revision = f.World.View.Revision;
            var wet = f.Act(ProductionAction.Start).Production!;
            Assert.That(SandboxMachineReadout.Result(wet, ProductionAction.Start), Does.Contain("Use the dryer").And.Contain("wet bypass jams"));
            Assert.That(f.World.View.Revision, Is.EqualTo(revision));
            f.Act(ProductionAction.Start, bypass: true); f.World.AdvanceTo(200);
            var unsafeRepair = f.Act(ProductionAction.Repair).Production!;
            Assert.That(SandboxMachineReadout.Result(unsafeRepair, ProductionAction.Repair), Does.StartWith("Isolate power"));
            f.Act(ProductionAction.SetPower, power: false); f.Act(ProductionAction.Repair);
            var noPower = f.Act(ProductionAction.Resume).Production!;
            Assert.That(SandboxMachineReadout.Result(noPower, ProductionAction.Resume), Does.StartWith("Restore machine power"));
        }

        [Test] public void DryingReadoutOffersOnlyItsAuthoredSafeProcedure()
        {
            var f = new ProductionFixture(start: false); f.World.Production.RegisterMachine(Id(90), MachineRecipe.Drying(Id(91), MaterialKind.Ore, 8000, 128, 100)); f.World.Start();
            var state = f.World.Production.GetMachine(Id(90))!; string text = SandboxMachineReadout.Recipe(state);
            Assert.That(text, Does.Contain("Safe drying: 8s").And.Contain("128 units").And.Contain("10%").And.Contain("No inspection bypass"));
            Assert.That(text, Does.Not.Contain("bypass 8s")); Assert.That(state.DryingTargetMoisture, Is.EqualTo(100));
            f.Grab(); f.Act(ProductionAction.Insert, Id(90)); Assert.That(SandboxMachineReadout.Controls(f.World.Production.GetMachine(Id(90))!), Does.Contain("R start safe drying").And.Not.Contain("B bypass"));
        }

        [Test] public void HistoricalStartedReadoutKeepsItsOriginalDurationAndBypassAfterCompletion()
        {
            var f = new ProductionFixture(); f.Load(); var start = f.Act(ProductionAction.Start, bypass: true).Production!;
            string text = SandboxMachineReadout.Result(start, ProductionAction.Start); f.World.AdvanceTo(500);
            Assert.That(text, Does.Contain("0.5s").And.Contain("Inspection bypass"));
            Assert.That(SandboxMachineReadout.Result(start, ProductionAction.Start), Is.EqualTo(text));
            Assert.That(start.Machine!.Mode, Is.EqualTo(ProductionMode.Processing)); Assert.That(f.World.Production.GetMachine(f.Machine)!.Mode, Is.EqualTo(ProductionMode.OutputReady));
        }

        [TestCase("fr-FR")] [TestCase("en-US")]
        public void MachineTimingReadoutKeepsAuthoredFractionalSecondsAcrossLocales(string locale)
        {
            var previous = CultureInfo.CurrentCulture;
            try { CultureInfo.CurrentCulture = new CultureInfo(locale); Assert.That(SandboxMachineReadout.Seconds(1500), Is.EqualTo("1.5s")); }
            finally { CultureInfo.CurrentCulture = previous; }
        }
    }
}
