using CriticalShift.Prototype;
using NUnit.Framework;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeShiftRulesTests
    {
        [Test]
        public void FuelQuotaRequiresTwoBatches()
        {
            Assert.IsFalse(PrototypeShiftRules.HasFuelQuota(1));
            Assert.IsTrue(PrototypeShiftRules.HasFuelQuota(2));
        }

        [Test]
        public void UnsafeFuelCreatesRecoverableCriticalEvent()
        {
            Assert.IsTrue(PrototypeShiftRules.IsMeltdown(PrototypeShiftRules.ReactorHeatFor(2, true)));
        }

        [Test]
        public void SafeFuelStaysBelowCriticalHeat()
        {
            Assert.IsFalse(PrototypeShiftRules.IsMeltdown(PrototypeShiftRules.ReactorHeatFor(2, false)));
        }

        [Test]
        public void CoolingRecoveryReturnsToReadableSafeHeat()
        {
            Assert.Less(PrototypeShiftRules.RecoveredHeat, 100f);
        }
    }
}
