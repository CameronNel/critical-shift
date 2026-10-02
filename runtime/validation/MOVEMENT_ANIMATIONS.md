# Movement animation source task

User-authorized Unity movement animation logic, 2 October 2026. Baseline:
`75983b95efb99536b1cda1a5533d9b265a4c581f`; task branch:
`feat/unity-movement-animations-20261002`. Primary author: Codex.
Independent review and maintainer merge are pending.

## Decision and scope before implementation

Implement one visual adapter under `Features/Workers/Unity` and its clip-library
editor tool under `Features/Workers/Editor`. The adapter alone writes its bound
Animator. Its lifetime is the bound worker component; disable clears transition
history and disables animation. Supplied observations describe actual local velocity,
ground contact, stance and whether the physical owner permits animation. They are
presentation inputs, never a second health, movement, custody or recovery owner.

The runtime assembly depends only on UnityEngine and base C#; the editor assembly
depends on that runtime assembly and UnityEditor. These are existing A02-allowlisted
roles. Add `com.unity.modules.animation` version `1.0.0`, the required built-in engine
module. No third-party animation, movement, input or networking framework is selected.
Keep the recorded Unity 6000.4.3f1 target and other package versions.

The main checkout has no movement FBX/animation clips, Animator controllers or bound worker
prefabs. After the user's clarification, a remote-branch search found Claude's 49-clip
source on `claude/character-rig`, revision `6792f25d89430c5b1ff701d37957f88f3ae20e8a`.
Its README confirms that the FBX exports are uncommitted and native import is untested.
Use those exact clip IDs, loop flags and gait speeds, explicit clip bindings and a
runtime Playables mixer. Keep the art branch separate; no competing authoring source
or guessed crouch clips are created. No source
art exports/imports or scene/prefab migrations are included. There is no old runtime
animation implementation to remove and no changed existing asset/script GUIDs.

Relevant contracts: A01-A03, A05-A07, S01/S07 and H04/H06. Acceptance: tested selection
from measured velocity; jump/fall/landing interruption; independent tool/carry
presentation; suspension and clean reset. Canonical pure selection source and tests
are linked into the existing offline NUnit suite. Native clip-library binding and
Animator lifecycle tests require the pinned activated editor. This isolated visual
source work does not advance Gate 0/1 or implement the PHYS-01 handoff fixture.

Actual clip mapping, rig/avatar compatibility, physical-controller integration, native
import/Player execution and movement feel remain required before playable acceptance.

## Execution

**Passed:** .NET SDK 8.0.423 on Linux; `python runtime/dotnet/tools/verify.py`
compiled the linked canonical selection code under C# 8.0 with zero compiler
warnings/errors. Exact expected discovery: 714 executed/passed, zero failed/skipped,
including all 26 movement cases. The 27 Python guards passed; intentional failing
NUnit and scenario controls were correctly rejected. All versioned scenarios ran
twice and report-safety checks passed. The full result counters, scenarios, source
hashes and limitations are retained in
[movement-animation-evidence.json](movement-animation-evidence.json). Raw ignored
logs/TRX and the original verifier summary remain in `runtime/dotnet/artifacts/`.

Static source/metadata checks passed: 35 paired unique GUIDs, eight asmdefs and
13 C# files. All 49 take names were compared against the fetched rig-branch source
and matched. Documentation links and whitespace checks passed. These are scoped
static checks, not a resolved Unity reference graph.

The first guard attempt had 27 fixture setup errors: unresolved `../` link paths
created `dotnet/src` before `copytree`. Resolving the paths corrected the fixture;
the subsequent guards and full verification passed. The initial error and repair
are retained in the evidence record. The SDK's first restore also needed a writable
temporary CLI/cache location; no repository credentials or global toolchain were
changed. The SDK was acquired into `/tmp`, not installed into the Unity project.

**NotRun / Blocked native acceptance:** no Unity Editor is installed in this
environment. The driver, Playables evaluation, editor clip-library creation, three
native binding/lifecycle cases, asset/avatar import, first-person camera, physical
handoff and Player build were not executed. Native asset/feel acceptance needs the
authored FBX exports and the pinned activated editor. Performance is unmeasured.

The implementation is one bounded visual feature: the 49-entry mapping, selector,
Playables consumer, setup tool and its tests belong together. It exceeds the H06
500-line review trigger because both selection and native binding/teardown behavior
need review; it introduces no unrelated feature scaffolding. No existing runtime
consumer or serialized identity was replaced. Map/art, host gameplay, input,
networking and physics source were deliberately preserved. Open Avatar/clip/physical
integration choices remain listed in the feature README. Independent review and
maintainer merge are pending; no gate acceptance is claimed.
