#if NEGATIVE_TEST_CONTROL
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class FailureControl
    {
        [Test]
        public void IntentionalFailureControl()
        {
            Assert.Fail("Intentional negative control: this test must fail, never ship or run in the positive suite.");
        }
    }
}
#endif
