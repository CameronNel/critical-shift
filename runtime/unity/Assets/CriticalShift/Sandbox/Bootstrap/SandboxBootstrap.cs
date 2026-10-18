using System;
using CriticalShift.Application;
using UnityEngine;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Sandbox
{
    /// <summary>Composition and fixture lifetime only; game rules and physical updates live in their owners.</summary>
    [DisallowMultipleComponent]
    public sealed class SandboxBootstrap : MonoBehaviour
    {
        [SerializeField] private Shader fixtureShader;
        [SerializeField] private Material fixtureLitTemplate, fixtureEmissionTemplate;
        [SerializeField] private SandboxPlayerCapture playerCapture;
        private SandboxFixture fixture;
        private Func<double> fixtureClock;
        private Action<Exception> fixtureDiagnostics;
        private bool resetRequested, stopping, started;
        private bool smoke, smokeErrors, smokeStopping, smokeFinished;
        private int smokeFrames, smokeCleanupFrames;
        private double smokeStartedAt;
        private Guid smokeEpoch;

        private void Awake()
        {
            smoke = !UnityApplication.isEditor && Array.IndexOf(Environment.GetCommandLineArgs(), "--cs-sandbox-smoke") >= 0;
            if (!smoke) return;
            UnityApplication.logMessageReceived += ObserveSmokeLog;
            UnityApplication.runInBackground = true;
            if (!Debug.isDebugBuild)
            {
                smokeErrors = true; Debug.LogError("Sandbox smoke requires the explicit development Player build.");
                smokeFinished = true; enabled = false; UnityApplication.Quit(20);
            }
        }

        private void Start() { started = true; stopping = false; StartFixture(); }
        private void OnEnable()
        {
            if (!started || fixture != null) return;
            stopping = false; StartFixture();
        }

        private void StartFixture()
        {
            try
            {
                if (fixtureShader == null) throw new InvalidOperationException("Generate the sandbox scene to bind its renderer shader explicitly.");
                fixture = new SandboxFixture(transform, fixtureShader, () => resetRequested = true, fixtureClock, fixtureDiagnostics,
                    fixtureLitTemplate, fixtureEmissionTemplate);
                Debug.Log("CS_SANDBOX_READY local_host=true map_loaded=false epoch=" + fixture.Epoch);
                if (smoke)
                {
                    int meshes = fixture.PreparePlayerSmoke(); smokeEpoch = fixture.Epoch; smokeStartedAt = Time.realtimeSinceStartupAsDouble;
                    Debug.Log($"CS_SANDBOX_PLAYER_READY unity={UnityApplication.unityVersion} build={UnityApplication.buildGUID} epoch={smokeEpoch:N} bindings={fixture.PhysicalBindingCount} bodies={fixture.PhysicsObservationCount} meshes={meshes}");
                }
            }
            catch (Exception exception)
            {
                try { StopFixture(); }
                catch (Exception cleanup) { Debug.LogException(cleanup, this); }
                Debug.LogException(exception, this); enabled = false;
                if (smoke) UnityApplication.Quit(20);
            }
        }

        public Shader FixtureShader => fixtureShader;
        public Material FixtureLitTemplate => fixtureLitTemplate;
        public Material FixtureEmissionTemplate => fixtureEmissionTemplate;
        public SandboxPlayerCapture PlayerCapture => playerCapture;
        public WorldSessionView World => fixture == null ? null : fixture.Snapshot;
        public WorldSessionView LastStoppedWorld { get; private set; }
        public int LastStoppedPhysicalBindings { get; private set; }
        public int LastStoppedPhysicsObservations { get; private set; }
        public int PhysicalBindingCount => fixture == null ? 0 : fixture.PhysicalBindingCount;
        public void BindFixtureShader(Shader shader)
        {
            if (fixture != null || shader == null) throw new InvalidOperationException("Bind the shader before fixture activation.");
            fixtureShader = shader;
        }

        public void BindFixtureMaterials(Material litTemplate, Material emissionTemplate)
        {
            if (fixture != null) throw new InvalidOperationException("Bind material dependencies before fixture activation.");
            SandboxPrimitives.ValidateMaterialTemplates(fixtureShader, litTemplate, emissionTemplate);
            fixtureLitTemplate = litTemplate; fixtureEmissionTemplate = emissionTemplate;
        }

        public void BindFixtureClock(Func<double> clock)
        {
            if (fixture != null || clock == null) throw new InvalidOperationException("Bind the fixture clock before activation.");
            fixtureClock = clock;
        }

        public void BindPlayerCapture(SandboxPlayerCapture capture)
        {
            if (fixture != null || capture == null || capture.gameObject != gameObject || capture.Owner != this)
                throw new InvalidOperationException("Bind the explicitly owned generated capture component before fixture activation.");
            playerCapture = capture;
        }

        public void BindFixtureDiagnostics(Action<Exception> sink)
        {
            if (fixture != null || sink == null) throw new InvalidOperationException("Bind the explicit diagnostic sink before fixture activation.");
            fixtureDiagnostics = sink;
        }

        private void LateUpdate()
        {
            if (!resetRequested || stopping) return;
            resetRequested = false; StopFixture(); StartFixture();
        }

        private void FixedUpdate()
        {
            if (!smoke || smokeStopping || smokeFinished || fixture == null) return;
            try
            {
                if (smokeErrors) { BeginSmokeStop(); return; }
                fixture.ObservePlayerSmoke(); smokeFrames++;
                if (smokeFrames >= 120 && Time.realtimeSinceStartupAsDouble - smokeStartedAt >= 2)
                {
                    fixture.ObservePlayerSmoke(requirePhysicalSensors: true);
                    if (playerCapture == null || !playerCapture.AwaitingCompletion) BeginSmokeStop();
                }
            }
            catch (Exception exception) { smokeErrors = true; Debug.LogException(exception, this); BeginSmokeStop(); }
        }

        private void BeginSmokeStop()
        {
            if (smokeStopping) return;
            smokeStopping = true; stopping = true; smokeCleanupFrames = 0;
            try { StopFixture(); }
            catch (Exception exception) { smokeErrors = true; Debug.LogException(exception, this); }
        }

        private void Update()
        {
            if (!smokeStopping || smokeFinished || ++smokeCleanupFrames < 2) return;
            // Wait across deferred destruction so late teardown errors cannot precede a false success marker.
            var stopped = LastStoppedWorld;
            if (stopped == null || stopped.Epoch != smokeEpoch || stopped.Phase != WorldPhase.Stopped ||
                stopped.ActiveClaimCount != 0 || stopped.RegisteredObjectCount != 0 || stopped.PendingTimerCount != 0 ||
                stopped.ConnectedPlayerCount != 0 || LastStoppedPhysicalBindings != 0 || LastStoppedPhysicsObservations != 0)
                smokeErrors = true;
            long milliseconds = (long)Math.Floor((Time.realtimeSinceStartupAsDouble - smokeStartedAt) * 1000);
            Debug.Log($"CS_SANDBOX_PLAYER_STOPPED epoch={smokeEpoch:N} frames={smokeFrames} milliseconds={milliseconds} errors={(smokeErrors ? 1 : 0)} bindings={LastStoppedPhysicalBindings} bodies={LastStoppedPhysicsObservations} objects={stopped?.RegisteredObjectCount ?? -1} claims={stopped?.ActiveClaimCount ?? -1} timers={stopped?.PendingTimerCount ?? -1} connections={stopped?.ConnectedPlayerCount ?? -1}");
            smokeFinished = true; UnityApplication.logMessageReceived -= ObserveSmokeLog;
            UnityApplication.Quit(smokeErrors ? 20 : 0);
        }

        private void ObserveSmokeLog(string message, string stack, LogType type)
        { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) smokeErrors = true; }

        private void StopFixture()
        {
            if (fixture == null) return;
            var previous = fixture; fixture = null;
            try { previous.Dispose(); }
            finally
            {
                LastStoppedWorld = previous.Snapshot; LastStoppedPhysicalBindings = previous.PhysicalBindingCount;
                LastStoppedPhysicsObservations = previous.PhysicsObservationCount;
            }
        }

        // Editor Stop and Player quit notify this owner before hierarchy teardown.
        // Close the world before Unity disables required child adapters in its own order.
        private void OnApplicationQuit() { stopping = true; StopFixture(); }

        private void OnDisable()
        {
            stopping = true;
            try { StopFixture(); }
            finally
            {
                if (smoke && !smokeStopping && !smokeFinished)
                {
                    smokeErrors = true; smokeFinished = true;
                    Debug.LogError("Sandbox smoke was disabled before completing its lifetime."); UnityApplication.Quit(20);
                }
            }
        }
        private void OnDestroy()
        {
            stopping = true;
            try { StopFixture(); }
            finally { fixtureClock = null; fixtureDiagnostics = null; UnityApplication.logMessageReceived -= ObserveSmokeLog; }
        }
    }
}
