using System;
using UnityEngine;

namespace CriticalShift.Sandbox
{
    /// <summary>Composition and fixture lifetime only; game rules and physical updates live in their owners.</summary>
    [DisallowMultipleComponent]
    public sealed class SandboxBootstrap : MonoBehaviour
    {
        [SerializeField] private Shader fixtureShader;
        private SandboxFixture fixture;
        private bool resetRequested, stopping;

        private void Start() => StartFixture();

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
            fixture.Dispose(); fixture = null;
        }

        private void OnDisable() { stopping = true; StopFixture(); }
        private void OnDestroy() { stopping = true; StopFixture(); }
    }
}
