using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Sandbox
{
    /// <summary>Composition and fixture lifetime only; game rules and physical updates live in their owners.</summary>
    [DisallowMultipleComponent]
    public sealed class SandboxBootstrap : MonoBehaviour
    {
        [SerializeField] private Shader fixtureShader;
        private SandboxFixture fixture;
        private bool resetRequested, stopping, started;

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
                fixture = new SandboxFixture(transform, fixtureShader, () => resetRequested = true);
                Debug.Log("CS_SANDBOX_READY local_host=true map_loaded=false epoch=" + fixture.Epoch);
            }
            catch (Exception exception)
            {
                StopFixture(); Debug.LogException(exception, this); enabled = false;
            }
        }

        public Shader FixtureShader => fixtureShader;
        public WorldSessionView World => fixture == null ? null : fixture.Snapshot;
        public WorldSessionView LastStoppedWorld { get; private set; }
        public int PhysicalBindingCount => fixture == null ? 0 : fixture.PhysicalBindingCount;
        public void BindFixtureShader(Shader shader)
        {
            if (fixture != null || shader == null) throw new InvalidOperationException("Bind the shader before fixture activation.");
            fixtureShader = shader;
        }

        private void LateUpdate()
        {
            if (!resetRequested || stopping) return;
            resetRequested = false; StopFixture(); StartFixture();
        }

        private void StopFixture()
        {
            if (fixture == null) return;
            fixture.Dispose(); LastStoppedWorld = fixture.Snapshot; fixture = null;
        }

        private void OnDisable() { stopping = true; StopFixture(); }
        private void OnDestroy() { stopping = true; StopFixture(); }
    }
}
