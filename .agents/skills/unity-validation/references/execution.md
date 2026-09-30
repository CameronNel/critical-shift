# Execution and evidence

Use with [unity-validation](../SKILL.md). Prefer current repository runners and
contracts over ad hoc commands. This file installs no runner and contains no new tests.

## Readiness and isolation

Read the current runtime README and relevant validation records. Check editor version,
package lock, OS/target/backend, activation and build modules. Keep credentials out of
commands recorded in PRs and logs. Source-only preparation and historical success are
not evidence that the current revision has imported or built successfully.

Use an authorized validator's disposable-copy mechanism when applicable and confirm
that its copied inputs actually include the changed content. Preserve source
`.meta` identities, scenes and package settings. Do not let an editor upgrade or asset
reimport silently rewrite the canonical checkout. Compare any intended serialized
changes explicitly before promoting them. Never delete another session's lock files
or run concurrent editor jobs on one project copy to evade project locking.

## Foundation coverage is not asset acceptance

At the inspected baseline, `runtime/tools/run_foundation.py` copies the foundation's
`runtime/unity` project inputs and toolchain profile, uses foundation-only expected
tests, and reports WP-01-only results. It does not import the map. Its native phases,
including Player startup, cannot establish imported-asset, material, collider, binding,
gameplay or visual acceptance. Keep this limit even when every foundation test passes.

For asset/feature claims, identify a separately authorized validator and fixture that
exercise the changed export/import revision, relevant scene or prefab, required logical
bindings and actual behavior. Verify copied dependencies and material conversions,
collider/serialization assertions and the target build when required. List the exact
coverage and omissions before interpreting results; a broad suite name is not evidence.
If no applicable validator exists, tests are Planned and acceptance is Blocked. Existing
but unexecuted tests are NotRun. Do not present the foundation result as a fallback pass
or expand its source/test catalogue without separate implementation authorization.

## Command-line pitfalls

Unity's Editor executable arguments and the newer Unity CLI are different interfaces.
Use the interface actually installed and supported by the repository. For any manual
invocation, inspect the matching editor and Test Framework documentation first.

`-batchmode` does not establish that rendering is available. `-nographics` suppresses
graphics initialization and cannot support a claim that visual tests or screenshots
were checked. Use a supported graphics context for those checks or mark them Blocked.
Do not add `-quit` to `-runTests`: the Unity 6.4 reference warns it exits before ongoing
tests finish. Use the existing runner's completion/result handling and bounded timeout.
Preserve process failures through shell pipelines and retain full diagnostic logs.

## Test and build evidence

Follow V00 exactly. Match the expected test IDs and counts from the current runner,
parse result files, reject empty/malformed/stale results, and detect unexpected skips
or errors. A zero exit code with no intended tests is a failure. Do not use synchronous
execution or a broad exclusion filter that silently drops multi-frame Unity tests.
Record output hashes/revision so old artifacts cannot masquerade as a fresh pass.

Compile/import, EditMode, PlayMode, target Player startup, interaction and shutdown
answer different questions. Run only the suites required by the task, but do not claim
a stronger layer from weaker evidence. A serialized binding change may need native
and Player checks even when the editor-free suite passes. Multiplayer evidence needs
the real required processes and profiles, not multiple cameras in one simulation.

## Profiling

Follow V05 rather than installing generic performance budgets. Record fixture, revision,
hardware, OS, resolution, graphics settings, target/backend, warm-up and sampling.
Compare repeated representative runs and report frame-time distributions, memory and
relevant simulation/rendering costs. Keep local multi-process contention separate
from distributed-client results. No target-hardware access means target performance
is unmeasured; a pretty Blender preview is not performance evidence.

## Sources

[Unity 6.4 Editor command-line reference](https://docs.unity3d.com/6000.4/Documentation/Manual/EditorCommandLineArguments.html)
and [Test Framework 1.4 command-line reference](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html)
were consulted for these pitfalls. The latter is a reference version, not a package
selection. Use documentation matching the project's actual pinned package at execution.
