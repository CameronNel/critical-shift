using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor.Build;
using UnityEditor.Compilation;
using UnityEditor.PackageManager;
using UnityEngine;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Sandbox.Editor
{
    /// <summary>Native compiler-description checks for the source trial; never substitutes for Player or gameplay evidence.</summary>
    internal static class SandboxAssemblyGraph
    {
        [Serializable] private sealed class Definition
        {
            public string name = "";
            public string[] references = Array.Empty<string>();
            public string[] includePlatforms = Array.Empty<string>();
            public bool noEngineReferences = false;
        }

        internal static int Validate()
        {
            var assemblies = CompilationPipeline.GetAssemblies(AssembliesType.Editor)
                .Where(item => item.name.StartsWith("CriticalShift.", StringComparison.Ordinal) && !item.name.Contains(".Tests."))
                .ToArray();
            if (assemblies.Length == 0 || !assemblies.Any(item => item.name == "CriticalShift.Application") ||
                !assemblies.Any(item => item.name == "CriticalShift.Sandbox.Bootstrap"))
                throw new BuildFailedException("The native compiler did not resolve the required gameplay source assemblies.");
            foreach (var assembly in assemblies)
            {
                string path = CompilationPipeline.GetAssemblyDefinitionFilePathFromAssemblyName(assembly.name);
                if (string.IsNullOrEmpty(path)) throw new BuildFailedException("A first-party compiler assembly has no source definition: " + assembly.name);
                var definition = JsonUtility.FromJson<Definition>(File.ReadAllText(PhysicalPath(path)));
                if (definition == null || definition.name != assembly.name || definition.references == null ||
                    definition.references.Any(reference => reference.StartsWith("GUID:", StringComparison.Ordinal)))
                    throw new BuildFailedException("The sandbox trial requires explicit named assembly definitions: " + assembly.name);
                var declared = new HashSet<string>(definition.references, StringComparer.Ordinal);
                var resolved = new HashSet<string>(assembly.assemblyReferences.Select(reference => reference.name), StringComparer.Ordinal);
                var expected = new HashSet<string>(declared, StringComparer.Ordinal);
                // The pinned editor injects both bundled runners into Editor-only
                // assemblies even without TestAssemblies. Native Bee response files
                // establish this for all three production Editor assemblies. Keep
                // exact equality so unrelated SDK or first-party edges still fail.
                bool editorOnly = definition.includePlatforms != null && definition.includePlatforms.SequenceEqual(new[] { "Editor" });
                if (editorOnly) expected.UnionWith(new[] { "UnityEditor.TestRunner", "UnityEngine.TestRunner" });
                if (!expected.SetEquals(resolved))
                    throw new BuildFailedException("Native project references differ from the declaration for " + assembly.name +
                        "; declared=" + string.Join(",", declared.OrderBy(value => value)) +
                        "; implicit=" + (editorOnly ? "UnityEditor.TestRunner,UnityEngine.TestRunner" : "") +
                        "; resolved=" + string.Join(",", resolved.OrderBy(value => value)));
                bool pure = assembly.name == "CriticalShift.Application" || assembly.name == "CriticalShift.ProcessLifetime" || assembly.name.EndsWith(".Domain", StringComparison.Ordinal);
                if (definition.noEngineReferences != pure || (pure && assembly.compiledAssemblyReferences.Any(IsEngineReference)))
                    throw new BuildFailedException("The native compiler resolved an engine dependency into a pure assembly: " + assembly.name);
                if (!File.Exists(PhysicalPath(assembly.outputPath)))
                    throw new BuildFailedException("The native compiled output is missing for " + assembly.name);
            }
            Debug.Log("CS_SANDBOX_ASSEMBLIES count=" + assemblies.Length);
            return assemblies.Length;
        }

        private static bool IsEngineReference(string path)
        {
            string name = Path.GetFileNameWithoutExtension(path);
            return name.StartsWith("UnityEngine", StringComparison.Ordinal) || name.StartsWith("UnityEditor", StringComparison.Ordinal);
        }

        private static string PhysicalPath(string value)
        {
            if (Path.IsPathRooted(value)) return value;
            string path = value.Replace('\\', '/');
            if (path.StartsWith("Packages/", StringComparison.Ordinal))
            {
                var package = PackageInfo.FindForAssetPath(path);
                int separator = path.IndexOf('/', "Packages/".Length);
                if (package == null || separator < 0 || string.IsNullOrEmpty(package.resolvedPath))
                    throw new BuildFailedException("Could not resolve the local package's physical source path.");
                return Path.GetFullPath(Path.Combine(package.resolvedPath, path.Substring(separator + 1)));
            }
            return Path.GetFullPath(Path.Combine(UnityApplication.dataPath, "..", path));
        }
    }
}
