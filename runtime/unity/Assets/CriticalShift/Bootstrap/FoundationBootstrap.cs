using System;
using CriticalShift.Application;
using UnityEngine;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Bootstrap
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class FoundationBootstrap : MonoBehaviour
    {
        private readonly ProcessLifetime lifetime = new ProcessLifetime();
        private bool smoke;
        private bool sawError;
        private int frames;
        private double readyAt;
        public ProcessPhase Phase => lifetime.Phase;
        public bool HasErrors => sawError;

        private void Awake()
        {
            if (lifetime.Phase != ProcessPhase.Created) return;
            smoke = !UnityApplication.isEditor &&
                Array.IndexOf(Environment.GetCommandLineArgs(), "--cs-smoke") >= 0;
            UnityApplication.logMessageReceived += OnLog;
            if (!ValidateCamera()) return;
            UnityApplication.runInBackground = true;
        }

        private void Start()
        {
            if (lifetime.Phase != ProcessPhase.Created) return;
            if (sawError)
            {
                FailStartup();
                return;
            }
            if (!ValidateCamera()) return;
            lifetime.MarkReady();
            readyAt = Time.realtimeSinceStartupAsDouble;
            Debug.Log($"CS_FOUNDATION_READY unity={UnityApplication.unityVersion} build={UnityApplication.buildGUID}");
        }

        private void Update()
        {
            if (lifetime.Phase != ProcessPhase.Ready) return;
            frames++;
            if (smoke && frames >= 12 && Time.realtimeSinceStartupAsDouble - readyAt >= 0.25)
                Quit();
        }

        private void OnGUI()
        {
            if (smoke) return;
            GUI.Box(new Rect(24, 24, 440, 160), "CRITICAL SHIFT | FOUNDATION");
            GUI.Label(new Rect(44, 58, 400, 25), "Process: " + lifetime.Phase);
            GUI.Label(new Rect(44, 88, 400, 25), "Toolchain fixture only. No map or gameplay loaded.");
            if (!UnityApplication.isEditor && GUI.Button(new Rect(44, 128, 140, 30), "Close fixture"))
                Quit();
        }

        private void Quit()
        {
            StopProcess();
            UnityApplication.Quit(sawError ? 20 : 0);
        }

        public void StopProcess()
        {
            UnityApplication.logMessageReceived -= OnLog;
            if (lifetime.Stop())
                Debug.Log($"CS_FOUNDATION_STOPPED frames={frames} errors={(sawError ? 1 : 0)}");
        }

        private bool ValidateCamera()
        {
            var cameraComponent = GetComponent<Camera>();
            if (cameraComponent != null && cameraComponent.enabled) return true;
            sawError = true;
            Debug.LogError("Foundation requires its enabled local Camera.", this);
            FailStartup();
            return false;
        }

        private void FailStartup()
        {
            StopProcess();
            if (smoke) UnityApplication.Quit(20);
        }

        private void OnLog(string message, string stackTrace, LogType type)
        {
            if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert)
                sawError = true;
        }

        private void OnApplicationQuit() => StopProcess();

        private void OnDestroy() => StopProcess();
    }
}
