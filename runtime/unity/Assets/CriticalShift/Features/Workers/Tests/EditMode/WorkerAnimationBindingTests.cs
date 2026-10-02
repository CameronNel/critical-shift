using System;
using System.Collections.Generic;
using CriticalShift.Features.Workers.Unity;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace CriticalShift.Features.Workers.Tests
{
    // Requires the native Unity Test Runner. These tests are not linked into the offline suite.
    public sealed class WorkerAnimationBindingTests
    {
        private readonly List<UnityEngine.Object> owned = new List<UnityEngine.Object>();

        [TearDown]
        public void TearDown()
        {
            for (int i = owned.Count - 1; i >= 0; i--)
                if (owned[i] != null) UnityEngine.Object.DestroyImmediate(owned[i]);
            owned.Clear();
        }

        private WorkerAnimationLibrary Library()
        {
            var library = ScriptableObject.CreateInstance<WorkerAnimationLibrary>();
            owned.Add(library);
            var serialized = new SerializedObject(library);
            var rows = serialized.FindProperty("clips");
            rows.arraySize = MovementClipInfo.Count;
            for (int i = 0; i < MovementClipInfo.Count; i++)
            {
                var id = (MovementClip)i;
                var clip = new AnimationClip { name = id.ToString() };
                owned.Add(clip);
                AnimationUtility.SetEditorCurve(clip,
                    EditorCurveBinding.FloatCurve("", typeof(Transform), "m_LocalPosition.x"),
                    AnimationCurve.Linear(0, 0, 1, 0));
                var settings = AnimationUtility.GetAnimationClipSettings(clip);
                settings.loopTime = MovementClipInfo.For(id).Loop;
                AnimationUtility.SetAnimationClipSettings(clip, settings);
                var row = rows.GetArrayElementAtIndex(i);
                row.FindPropertyRelative("id").intValue = i;
                row.FindPropertyRelative("clip").objectReferenceValue = clip;
            }
            serialized.ApplyModifiedPropertiesWithoutUndo();
            return library;
        }

        [Test]
        public void LibraryRejectsMissingAndDuplicateBindings()
        {
            var library = Library();
            Assert.That(library.CreateClipTable().Length, Is.EqualTo(49));
            var serialized = new SerializedObject(library);
            var rows = serialized.FindProperty("clips");
            rows.GetArrayElementAtIndex(1).FindPropertyRelative("id").intValue = 0;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            Assert.Throws<InvalidOperationException>(() => library.CreateClipTable());
            rows.arraySize = 0;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            Assert.Throws<InvalidOperationException>(() => library.CreateClipTable());
        }

        [Test]
        public void LibraryRejectsWrongLoopSettings()
        {
            var library = Library();
            var clip = library.CreateClipTable()[(int)MovementClip.JUMP];
            var settings = AnimationUtility.GetAnimationClipSettings(clip);
            settings.loopTime = true;
            AnimationUtility.SetAnimationClipSettings(clip, settings);
            Assert.Throws<InvalidOperationException>(() => library.CreateClipTable());
        }

        [Test]
        public void PlayableLifetimeSuspendsAndRestartsWithoutOldActions()
        {
            var library = Library();
            var worker = new GameObject("Worker animation lifecycle fixture");
            owned.Add(worker);
            worker.SetActive(false);
            var animator = worker.AddComponent<Animator>();
            animator.applyRootMotion = true;
            var driver = worker.AddComponent<WorkerMovementAnimator>();
            var serialized = new SerializedObject(driver);
            serialized.FindProperty("animator").objectReferenceValue = animator;
            serialized.FindProperty("library").objectReferenceValue = library;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            for (int cycle = 0; cycle < 10; cycle++)
            {
                worker.SetActive(true);
                Assert.That(driver.Ready, Is.True);
                Assert.That(animator.enabled, Is.False);
                driver.ApplySample(new MovementAnimationSample(0, 0, 0, true), 0);
                Assert.That(animator.enabled, Is.True);
                Assert.That(animator.applyRootMotion, Is.False);
                Assert.That(driver.TryPlayAction(MovementClip.RADIO, 1), Is.True);
                driver.ApplySample(new MovementAnimationSample(0, 0, 0, true, animated: false), 0);
                Assert.That(animator.enabled, Is.False);
                Assert.That(driver.ActiveAction, Is.Null);
                worker.SetActive(false);
                Assert.That(driver.Ready, Is.False);
                Assert.That(animator.applyRootMotion, Is.True);
            }
        }
    }
}
