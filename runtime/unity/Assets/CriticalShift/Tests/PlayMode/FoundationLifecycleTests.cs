using System.Collections;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Bootstrap;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace CriticalShift.Tests.PlayMode
{
    public sealed class FoundationLifecycleTests
    {
        [UnityTest] public IEnumerator SceneStartsAndStopsCleanly()
        {
            yield return SceneManager.LoadSceneAsync("Foundation", LoadSceneMode.Single);
            yield return null;
            var roots = SceneManager.GetActiveScene().GetRootGameObjects();
            var bootstrap = roots.SelectMany(r => r.GetComponentsInChildren<FoundationBootstrap>()).Single();
            Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Ready));
            Assert.That(bootstrap.GetComponent<Camera>().enabled, Is.True);
            bootstrap.StopProcess();
            bootstrap.StopProcess();
            Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Stopped));
            LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator ReloadGetsAFreshProcess()
        {
            for (int i = 0; i < 3; i++)
            {
                yield return SceneManager.LoadSceneAsync("Foundation", LoadSceneMode.Single);
                yield return null;
                var bootstrap = SceneManager.GetActiveScene().GetRootGameObjects()
                    .SelectMany(r => r.GetComponentsInChildren<FoundationBootstrap>()).Single();
                Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Ready));
                bootstrap.StopProcess();
                Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Stopped));
            }
            LogAssert.NoUnexpectedReceived();
        }
    }
}
