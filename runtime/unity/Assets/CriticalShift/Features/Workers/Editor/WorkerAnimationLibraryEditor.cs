using System;
using System.Collections.Generic;
using CriticalShift.Features.Workers.Unity;
using UnityEditor;
using UnityEngine;

namespace CriticalShift.Features.Workers.Editor
{
    public static class WorkerAnimationLibraryBuilder
    {
        [MenuItem("Critical Shift/Workers/Create animation library from selected folder")]
        public static void CreateFromSelectedFolder()
        {
            string folder = AssetDatabase.GetAssetPath(Selection.activeObject);
            if (!AssetDatabase.IsValidFolder(folder))
                throw new InvalidOperationException("Select the folder containing the imported worker FBX clips.");
            var bindings = new Dictionary<MovementClip, AnimationClip>();
            var paths = new HashSet<string>();
            foreach (string filter in new[] { "t:Model", "t:AnimationClip" })
                foreach (string guid in AssetDatabase.FindAssets(filter, new[] { folder }))
                    paths.Add(AssetDatabase.GUIDToAssetPath(guid));
            foreach (string path in paths)
                foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(path))
                {
                    if (!(asset is AnimationClip clip) || clip.name.StartsWith("__preview__", StringComparison.Ordinal)) continue;
                    if (!Enum.TryParse(clip.name, out MovementClip id) || id.ToString() != clip.name) continue;
                    if (bindings.ContainsKey(id)) throw new InvalidOperationException("Ambiguous clip name: " + id);
                    bindings.Add(id, clip);
                }
            var library = ScriptableObject.CreateInstance<WorkerAnimationLibrary>();
            try
            {
                var serialized = new SerializedObject(library);
                var list = serialized.FindProperty("clips");
                list.arraySize = bindings.Count;
                int index = 0;
                foreach (MovementClip id in Enum.GetValues(typeof(MovementClip)))
                {
                    if (!bindings.TryGetValue(id, out var clip)) continue;
                    var row = list.GetArrayElementAtIndex(index++);
                    row.FindPropertyRelative("id").intValue = (int)id;
                    row.FindPropertyRelative("clip").objectReferenceValue = clip;
                }
                serialized.ApplyModifiedPropertiesWithoutUndo();
                library.CreateClipTable(); // Reject missing clips/incorrect loops before creating any asset.
                string destination = AssetDatabase.GenerateUniqueAssetPath(folder + "/WorkerAnimations.asset");
                AssetDatabase.CreateAsset(library, destination);
                AssetDatabase.SaveAssets();
                Selection.activeObject = library;
                EditorGUIUtility.PingObject(library);
            }
            catch
            {
                if (!AssetDatabase.Contains(library)) UnityEngine.Object.DestroyImmediate(library);
                throw;
            }
        }
    }

    [CustomEditor(typeof(WorkerAnimationLibrary))]
    public sealed class WorkerAnimationLibraryEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();
            if (GUILayout.Button("Validate all 49 clip bindings"))
            {
                try
                {
                    ((WorkerAnimationLibrary)target).CreateClipTable();
                    Debug.Log("Worker animation library: all 49 clips and loop flags are valid.", target);
                }
                catch (Exception error) { Debug.LogError(error.Message, target); }
            }
        }
    }
}
