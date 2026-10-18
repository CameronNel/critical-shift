using System;
using System.IO;
using System.Security.Cryptography;
using CriticalShift.Application;
using UnityEngine;
using UnityEngine.Rendering;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Sandbox
{
    /// <summary>Explicit development-Player capture of the owned scratch fixture; no normal input or screenshot service.</summary>
    [DisallowMultipleComponent]
    public sealed class SandboxPlayerCapture : MonoBehaviour
    {
        private const string Flag = "--cs-sandbox-capture";
        private const double TimeoutSeconds = 30;
        private const long MaximumPngBytes = 64 * 1024 * 1024;
        [SerializeField] private SandboxBootstrap owner;
        private string destination, temporary, outputRoot;
        private bool requested, issued, finished;
        private int renderedFrames, width, height;
        private double beganAt;
        private Guid epoch;
        public SandboxBootstrap Owner => owner;
        public bool AwaitingCompletion => requested && !finished;

        public void Configure(SandboxBootstrap bootstrap)
        {
            if (requested || bootstrap == null || bootstrap.gameObject != gameObject)
                throw new ArgumentException("Bind the generated capture component to its own sandbox bootstrap before startup.");
            owner = bootstrap;
        }

        private void Awake()
        {
            if (UnityApplication.isEditor) { enabled = false; return; }
            string[] args = Environment.GetCommandLineArgs(); int at = Array.IndexOf(args, Flag);
            if (at < 0) { enabled = false; return; }
            requested = true; beganAt = Time.realtimeSinceStartupAsDouble;
            try
            {
                if (!Debug.isDebugBuild || UnityApplication.platform != RuntimePlatform.WindowsPlayer ||
                    SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
                    throw new InvalidOperationException("Capture requires a Win64 development Player with a real graphics device; omit -nographics.");
                if (Array.IndexOf(args, "--cs-sandbox-smoke") < 0 || Array.LastIndexOf(args, Flag) != at || at + 1 >= args.Length)
                    throw new ArgumentException("Pass one --cs-sandbox-capture absolute.png together with --cs-sandbox-smoke.");
                if (owner == null || owner.gameObject != gameObject)
                    throw new InvalidOperationException("Regenerate the sandbox scene with its explicitly bound capture component.");
                outputRoot = FindOutputRoot(); destination = CanonicalLocalPath(args[at + 1]);
                if (!destination.StartsWith(outputRoot + "\\", StringComparison.OrdinalIgnoreCase) ||
                    !string.Equals(Path.GetExtension(destination), ".png", StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("The explicit screenshot must be a new .png beneath this Player's runtime/out directory.");
                GuardDirectory(Path.GetDirectoryName(destination)); RejectExisting(destination);
                temporary = Path.Combine(Path.GetDirectoryName(destination), ".cs-sandbox-capture-" + Guid.NewGuid().ToString("N") + ".png");
                RejectExisting(temporary);
                RenderPipelineManager.endCameraRendering += ObserveRenderedCamera;
            }
            catch (Exception error) { Fail(error.Message); }
        }

        private void ObserveRenderedCamera(ScriptableRenderContext context, Camera camera)
        {
            if (!AwaitingCompletion || issued || owner == null || owner.World == null || owner.World.Phase != WorldPhase.Running ||
                camera == null || !camera.isActiveAndEnabled || camera.cameraType != CameraType.Game ||
                camera.targetTexture != null || camera.targetDisplay != 0 || !camera.transform.IsChildOf(owner.transform)) return;
            // A completed owned Game-camera callback proves rendering progressed; no EndOfFrame coroutine is used.
            renderedFrames++;
        }

        private void Update()
        {
            if (!AwaitingCompletion) return;
            try
            {
                if (Time.realtimeSinceStartupAsDouble - beganAt >= TimeoutSeconds)
                    throw new TimeoutException("No complete rendered fixture PNG arrived before the capture deadline.");
                if (owner == null || !owner.isActiveAndEnabled ||
                    (issued && (owner.World == null || owner.World.Epoch != epoch || owner.World.Phase != WorldPhase.Running)))
                    throw new InvalidOperationException("The captured fixture ended or changed epoch before PNG completion.");
                if (!issued)
                {
                    if (renderedFrames < 2 || owner.World == null || owner.World.Phase != WorldPhase.Running) return;
                    width = Screen.width; height = Screen.height;
                    if (width < 1 || height < 1) throw new InvalidOperationException("The rendered display has no usable dimensions.");
                    GuardDirectory(Path.GetDirectoryName(destination)); RejectExisting(destination); RejectExisting(temporary);
                    epoch = owner.World.Epoch; issued = true;
                    ScreenCapture.CaptureScreenshot(temporary, 1);
                    Debug.Log("CS_SANDBOX_CAPTURE_REQUESTED build=" + UnityApplication.buildGUID + " epoch=" + epoch.ToString("N") +
                        " frame=" + Time.frameCount + " width=" + width + " height=" + height + " path=" + Quoted(destination));
                }
                else TryComplete();
            }
            catch (Exception error) { Fail(error.Message); }
        }

        private void TryComplete()
        {
            if (!File.Exists(temporary)) return;
            GuardDirectory(Path.GetDirectoryName(temporary));
            if ((File.GetAttributes(temporary) & (FileAttributes.ReparsePoint | FileAttributes.Directory)) != 0)
                throw new IOException("The native capture output became an aliased path.");
            string hash; long bytes;
            try
            {
                // Wait for the native writer to close, then require the PNG signature, IHDR dimensions and complete IEND.
                using (var input = new FileStream(temporary, FileMode.Open, FileAccess.Read, FileShare.None))
                {
                    if (input.Length < 45) return;
                    if (input.Length > MaximumPngBytes) throw new InvalidOperationException("The native PNG exceeds the bounded capture size.");
                    var header = new byte[24]; if (input.Read(header, 0, header.Length) != header.Length) return;
                    byte[] signature = { 137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82 };
                    for (int i = 0; i < signature.Length; i++)
                        if (header[i] != signature[i]) throw new InvalidOperationException("The native capture is not a PNG with an IHDR header.");
                    if (BigEndian(header, 16) != width || BigEndian(header, 20) != height)
                        throw new InvalidOperationException("The native PNG dimensions differ from the requested rendered display.");
                    input.Seek(-12, SeekOrigin.End); var tail = new byte[12];
                    if (input.Read(tail, 0, tail.Length) != tail.Length) return;
                    byte[] end = { 0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130 };
                    for (int i = 0; i < end.Length; i++) if (tail[i] != end[i]) return;
                    bytes = input.Length; input.Position = 0;
                    using (var digest = SHA256.Create()) hash = BitConverter.ToString(digest.ComputeHash(input)).Replace("-", "").ToLowerInvariant();
                    // A valid envelope alone is insufficient: require the engine to decode actual image data.
                    input.Position = 0; var png = new byte[(int)bytes]; int read = 0;
                    while (read < png.Length)
                    {
                        int count = input.Read(png, read, png.Length - read);
                        if (count == 0) throw new InvalidOperationException("The captured PNG ended before its declared size.");
                        read += count;
                    }
                    var decoded = new Texture2D(2, 2, TextureFormat.RGBA32, false, true);
                    try
                    {
                        if (!ImageConversion.LoadImage(decoded, png, true) || decoded.width != width || decoded.height != height)
                            throw new InvalidOperationException("The native capture does not decode to the requested rendered image.");
                    }
                    finally { UnityEngine.Object.Destroy(decoded); }
                }
            }
            catch (IOException) { return; } // Native writer may still hold its file.
            GuardDirectory(Path.GetDirectoryName(destination)); RejectExisting(destination);
            // File.Move without overwrite refuses a destination created after preflight; the engine never writes the requested path.
            File.Move(temporary, destination);
            finished = true; Detach();
            Debug.Log("CS_SANDBOX_CAPTURE_COMPLETED build=" + UnityApplication.buildGUID + " epoch=" + epoch.ToString("N") +
                " width=" + width + " height=" + height + " bytes=" + bytes +
                " sha256=" + hash + " path=" + Quoted(destination));
            enabled = false;
        }

        private static int BigEndian(byte[] bytes, int at) => (bytes[at] << 24) | (bytes[at + 1] << 16) | (bytes[at + 2] << 8) | bytes[at + 3];
        private static string Quoted(string value) => "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        private static string CanonicalLocalPath(string value)
        {
            if (string.IsNullOrWhiteSpace(value) || value.Length > 240 || value.Length < 4 || !char.IsLetter(value[0]) ||
                value[1] != ':' || value[2] != '\\' || value.IndexOf('/') >= 0 || value.IndexOf(':', 2) >= 0 ||
                !string.Equals(Path.GetFullPath(value), value, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Use one canonical absolute local Windows path, without relative, UNC, device or stream aliases.");
            foreach (string part in value.Substring(3).Split('\\'))
            {
                string stem = part.Split('.')[0].ToUpperInvariant();
                if (part.Length == 0 || part.EndsWith(".", StringComparison.Ordinal) || part.EndsWith(" ", StringComparison.Ordinal) ||
                    part.IndexOf('~') >= 0 || part.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 ||
                    stem == "CON" || stem == "PRN" || stem == "AUX" || stem == "NUL" ||
                    (stem.Length == 4 && (stem.StartsWith("COM", StringComparison.Ordinal) || stem.StartsWith("LPT", StringComparison.Ordinal)) &&
                     stem[3] >= '1' && stem[3] <= '9'))
                    throw new ArgumentException("Aliased or invalid Windows path components are not accepted for capture.");
            }
            return value;
        }
        private static string FindOutputRoot()
        {
            var directory = new DirectoryInfo(Path.GetDirectoryName(UnityApplication.dataPath));
            while (directory != null)
            {
                if (string.Equals(directory.Name, "out", StringComparison.OrdinalIgnoreCase) &&
                    directory.Parent != null && string.Equals(directory.Parent.Name, "runtime", StringComparison.OrdinalIgnoreCase))
                {
                    string root = CanonicalLocalPath(directory.FullName); GuardDirectory(root); return root;
                }
                directory = directory.Parent;
            }
            throw new InvalidOperationException("Launch the newly built Player from beneath runtime/out to request capture.");
        }
        private static void GuardDirectory(string path)
        {
            for (var directory = new DirectoryInfo(path); directory != null; directory = directory.Parent)
                if (!directory.Exists || (directory.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Capture requires existing, non-aliased parent directories.");
        }
        private static void RejectExisting(string path)
        {
            try { File.GetAttributes(path); }
            catch (FileNotFoundException) { return; }
            catch (DirectoryNotFoundException) { return; }
            throw new IOException("Capture refuses an existing file or directory: " + path);
        }
        private void Detach() => RenderPipelineManager.endCameraRendering -= ObserveRenderedCamera;
        private void Fail(string reason, bool requestQuit = true)
        {
            if (!AwaitingCompletion) return;
            finished = true; Detach();
            Debug.LogError("CS_SANDBOX_CAPTURE_FAILED reason=" + Quoted(reason.Replace('\r', ' ').Replace('\n', ' ')));
            if (requestQuit) UnityApplication.Quit(21);
            enabled = false;
        }
        private void OnDisable() { if (AwaitingCompletion) Fail("Capture component was disabled before completion."); Detach(); }
        private void OnDestroy() { if (AwaitingCompletion) Fail("Capture component was destroyed before completion.", false); Detach(); }
        private void OnApplicationQuit() { if (AwaitingCompletion) Fail("Player quit before capture completed.", false); }
    }
}
