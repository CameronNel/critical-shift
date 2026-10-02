# Worker movement and assignable scene interaction task

User-authorized code implementation, 2 October 2026. Baseline:
`75983b95efb99536b1cda1a5533d9b265a4c581f`; branch
`feat/unity-movement-animations-20261002`; draft PR 72. Primary author: Codex.
Independent review and maintainer merge are pending.

The user expanded the visual adapter to movement and interaction scene bindings,
then explicitly required that unfinished animation files remain untouched. No
Blender source, keyframes, `.blend`, FBX, `.anim` or final clip assets are edited,
exported or merged. The exact 49 existing take names and provisional calibration
are read from `claude/character-rig` revision `6792f25`. Inspector contact overrides
allow final timing changes without editing those animation files.

## Ownership, scope and decisions

Workers.Unity owns the CharacterController, camera, measured motion, Playables,
crouch IK and ragdoll/recovery projection. FacilityPhysics.Unity owns bounded-force
cargo/tool/cart/body attachments and conveyors. Interaction.Unity supplies scene
control, machine and material bindings. Unity.Shared carries only explicit engine
ports; Bootstrap composes one canonical WorldSession and real reach/clearance
policies. Controls gain an immutable Domain state and a typed Application command
within the existing connection receipt stream. No health, material, power, machine,
clock or custody owner is copied into a second Unity implementation.

The existing A02 roles cover these real consumers. D-03 uses the built-in physics
and inputlegacy `1.0.0` modules and keyboard/mouse input; IMGUI feedback reuses the
already pinned built-in module. No third-party framework or transport is installed.
D-08 is bounded to tagged objects with one primary and one helper under one lease:
helper loss leaves the primary; primary loss/expiry frees both; insertion needs
helper release; each worker retains a one-object limit. D-02 remains open.

Canonical Application plus seven Domain DLLs are generated from the existing .NET
Standard 2.1 projects, with explicit Unity importers and a source/binary hash manifest.
`runtime/tools/build_unity_rules.py` rebuilds them. No existing script GUID is changed;
new scene scripts have paired metadata. There are no old scenes/prefabs/controllers
or authored assets to migrate/delete. The diagnostic foundation scene remains its
own test fixture and is not a gameplay or map acceptance scene.

All 49 take names have routes documented in the [binding guide](../unity/Assets/CriticalShift/Features/Workers/README.md).
The editor tool adds components and wires explicit arrays; it never modifies an
animation. Final map assignment includes colliders, grip/slot/worker anchors,
Rigidbody/joints, material/recipe profiles and a compatible finished clip library.
OCRU resource accounting, mining yield, voice and exposure/restraint owners are not
present in the existing rules and are not invented by visual callbacks.

The change exceeds the H05 size trigger because motor, scene ports, canonical
command admission, physical projections and bindings form one executable scene
path. Keeping these coordinated on the already authorized PR avoids shipping
components with missing contracts/DLLs or unbound references. Independent cohesion
review remains required; native evidence does not exist.

Relevant contracts: A01-A03/A05-A07; S01/S03-S07; command/receipt, HOLD, PHYS,
WORKER, SHIFT/LIFE and ASSET validation rows. Observable acceptance includes
rejection without attachment, stale-release fencing, shared actor loss, clean
terminal teardown, measured blended gait speed, jump anticipation and resumed OCRU
idle. Actual physical/visual acceptance remains blocked on native execution.

## Evidence

Latest exact run and source hashes are in
[movement-animation-evidence.json](movement-animation-evidence.json).
The full offline verifier compiles canonical libraries and linked pure Unity logic
under C# 8 with .NET SDK 8.0.423. It checks exact NUnit discovery, 27 Python guards,
failing NUnit/scenario controls, repeated scenarios and report safety. Raw ignored
results are under `runtime/dotnet/artifacts/`; they are not a Unity test run.

Native tests: four animation binding/lifecycle EditMode cases and four physical
attachment/throw tests exist but are **NotRun**. Roslyn syntax parsing and static
GUID/asmdef/manifest checks are narrower checks, not native API/assembly resolution.
Unity compilation/import, final 49-clip contacts, PlayMode/Player, physics, shared
carry feel, camera/crouch/ragdoll review, multiplayer and performance are **Blocked**
here because the pinned activated editor and finished imported assets are unavailable.
No roadmap or technical/art/human acceptance gate advances.

An initial plugin-build attempt in the default command sandbox failed during restore
with no compiler diagnostics; a permitted-network rerun succeeded. The earlier
visual-only verifier's initial guard path error and repair remain in the evidence
history. No secret values, global SDK settings or asset sources were changed.

Changed: gameplay/physical scene adapters, control/shared-carry contracts, explicit
first-party DLL integration, scene setup/validation and regression fixtures.
Deliberately untouched: authored animations and map/art files. Validated: canonical
offline logic and scoped static checks. Not run/blocked: native checks above.
Open: D-02 and missing broader gameplay owners. Review/merge: draft, pending independent
review, no self-merge.
