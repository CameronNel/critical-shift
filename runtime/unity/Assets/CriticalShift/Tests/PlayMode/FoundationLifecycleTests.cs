using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using CriticalShift.Application;
using CriticalShift.Bootstrap;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Tests.PlayMode
{
    public sealed class FoundationLifecycleTests
    {
        private GameObject fixture;
        private readonly List<string> messages = new List<string>();

        [SetUp] public void CaptureLogs()
        {
            messages.Clear();
            UnityApplication.logMessageReceived += OnLog;
        }

        [UnityTearDown] public IEnumerator CleanUp()
        {
            try
            {
                if (fixture != null)
                {
                    var bootstrap = fixture.GetComponent<FoundationBootstrap>();
                    if (bootstrap != null && bootstrap.Phase != ProcessPhase.Stopped)
                    {
                        ExpectStopped(bootstrap.HasErrors);
                        bootstrap.StopProcess();
                    }
                    Object.Destroy(fixture);
                }
                yield return null;
                LogAssert.NoUnexpectedReceived();
            }
            finally
            {
                fixture = null;
                UnityApplication.logMessageReceived -= OnLog;
            }
        }

        private void OnLog(string message, string stackTrace, LogType type) => messages.Add(message);

        private static void ExpectReady() => LogAssert.Expect(LogType.Log, new Regex(
            "^CS_FOUNDATION_READY unity=" + Regex.Escape(UnityApplication.unityVersion) +
            " build=" + Regex.Escape(UnityApplication.buildGUID) + "$"));

        private static void ExpectStopped(bool errors, bool zeroFrames = false) => LogAssert.Expect(LogType.Log, new Regex(
            "^CS_FOUNDATION_STOPPED frames=" + (zeroFrames ? "0" : "(?:0|[1-9][0-9]*)") +
            " errors=" + (errors ? "1" : "0") + "$"));

        private void AssertStoppedWithoutReadiness(FoundationBootstrap bootstrap, bool failedStartup)
        {
            Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Stopped));
            Assert.That(bootstrap.HasErrors, Is.EqualTo(failedStartup));
            Assert.That(messages.Any(m => m.StartsWith("CS_FOUNDATION_READY ")), Is.False);
            Assert.That(messages.Count(m => m.StartsWith("CS_FOUNDATION_STOPPED ")), Is.EqualTo(1));
            Assert.That(messages, Does.Contain("CS_FOUNDATION_STOPPED frames=0 errors=" + (failedStartup ? "1" : "0")));
            LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator StopBeforeStartDoesNotBecomeReady()
        {
            fixture = new GameObject("Stop before Start fixture");
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            ExpectStopped(false, zeroFrames: true);
            bootstrap.StopProcess();
            bootstrap.StopProcess();
            yield return null;
            AssertStoppedWithoutReadiness(bootstrap, false);
        }

        [UnityTest] public IEnumerator StopBeforeAwakeDoesNotBecomeReady()
        {
            fixture = new GameObject("Stop before Awake fixture");
            fixture.SetActive(false);
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            ExpectStopped(false, zeroFrames: true);
            bootstrap.StopProcess();
            fixture.SetActive(true);
            yield return null;
            AssertStoppedWithoutReadiness(bootstrap, false);
        }

        [UnityTest] public IEnumerator DisabledCameraPreventsReadiness()
        {
            fixture = new GameObject("Disabled camera fixture");
            fixture.SetActive(false);
            fixture.AddComponent<Camera>().enabled = false;
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            LogAssert.Expect(LogType.Error, "Foundation requires its enabled local Camera.");
            ExpectStopped(true, zeroFrames: true);
            fixture.SetActive(true);
            yield return null;
            AssertStoppedWithoutReadiness(bootstrap, true);
        }

        [UnityTest] public IEnumerator CameraDisabledBeforeStartPreventsReadiness()
        {
            fixture = new GameObject("Camera disabled before Start fixture");
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            fixture.GetComponent<Camera>().enabled = false;
            LogAssert.Expect(LogType.Error, "Foundation requires its enabled local Camera.");
            ExpectStopped(true, zeroFrames: true);
            yield return null;
            AssertStoppedWithoutReadiness(bootstrap, true);
        }

        [UnityTest] public IEnumerator StartupErrorPreventsReadiness()
        {
            fixture = new GameObject("Startup error fixture");
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            LogAssert.Expect(LogType.Error, "Injected foundation startup error.");
            ExpectStopped(true, zeroFrames: true);
            Debug.LogError("Injected foundation startup error.");
            yield return null;
            AssertStoppedWithoutReadiness(bootstrap, true);
        }

        [UnityTest] public IEnumerator StoppedBootstrapDoesNotObserveLaterErrors()
        {
            fixture = new GameObject("Stopped log subscriber fixture");
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            ExpectStopped(false, zeroFrames: true);
            bootstrap.StopProcess();
            LogAssert.Expect(LogType.Error, "Unrelated error after foundation stop.");
            Debug.LogError("Unrelated error after foundation stop.");
            yield return null;
            AssertStoppedWithoutReadiness(bootstrap, false);
        }

        [UnityTest] public IEnumerator RunningErrorsAreRetainedThroughShutdown()
        {
            fixture = new GameObject("Running error fixture");
            ExpectReady();
            var bootstrap = fixture.AddComponent<FoundationBootstrap>();
            yield return null;
            Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Ready));
            Assert.That(bootstrap.HasErrors, Is.False);
            LogAssert.Expect(LogType.Error, "Injected running foundation error.");
            Debug.LogError("Injected running foundation error.");
            Assert.That(bootstrap.HasErrors, Is.True);
            ExpectStopped(true);
            bootstrap.StopProcess();
            Object.Destroy(fixture);
            yield return null;
            Assert.That(messages.Count(m => m.StartsWith("CS_FOUNDATION_STOPPED ")), Is.EqualTo(1));
            Assert.That(messages.Single(m => m.StartsWith("CS_FOUNDATION_STOPPED ")), Does.EndWith(" errors=1"));
            LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator SceneStartsAndStopsCleanly()
        {
            ExpectReady();
            yield return SceneManager.LoadSceneAsync("Foundation", LoadSceneMode.Single);
            yield return null;
            var roots = SceneManager.GetActiveScene().GetRootGameObjects();
            var bootstrap = roots.SelectMany(r => r.GetComponentsInChildren<FoundationBootstrap>()).Single();
            Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Ready));
            Assert.That(bootstrap.GetComponent<Camera>().enabled, Is.True);
            ExpectStopped(false);
            bootstrap.StopProcess();
            bootstrap.StopProcess();
            Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Stopped));
            LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator ReloadGetsAFreshProcess()
        {
            for (int i = 0; i < 3; i++)
            {
                ExpectReady();
                yield return SceneManager.LoadSceneAsync("Foundation", LoadSceneMode.Single);
                yield return null;
                var bootstrap = SceneManager.GetActiveScene().GetRootGameObjects()
                    .SelectMany(r => r.GetComponentsInChildren<FoundationBootstrap>()).Single();
                Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Ready));
                ExpectStopped(false);
                bootstrap.StopProcess();
                Assert.That(bootstrap.Phase, Is.EqualTo(ProcessPhase.Stopped));
            }
            LogAssert.NoUnexpectedReceived();
        }
    }
}
