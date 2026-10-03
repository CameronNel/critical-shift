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
ports and stateless engine targeting queries; Bootstrap composes one canonical WorldSession and real reach/clearance
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

The change exceeds the H06 size trigger because motor, scene ports, canonical
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

The polishing pass on `752b69e` fixes cursor resumption after Escape/focus loss,
initiating-key cancellation, destruction of an action target before its cue,
cancelled jump anticipation and short-loop cue catch-up. Targeting excludes the
worker/carried shape, retains solid obstruction and fails closed on a saturated
64-hit buffer. Secondary-grip loss releases only the helper through the existing
receipt stream; primary carry/push/pull mode changes preserve their accepted lease.
Reachable-target prompts and expiring feedback improve the local interaction view.
No canonical runtime rule or generated DLL changed in this pass.

This is still a broad host-scene implementation draft, not the assign-and-play
milestone. The 49/49 take routes are written. Finished-clip calibration, native
compilation, physical behavior and human feel have no acceptance evidence here.
The missing broader gameplay owners and D-02 remain open.

Latest exact run and source hashes are in
[movement-animation-evidence.json](movement-animation-evidence.json).
The full offline verifier compiles canonical libraries and linked pure Unity logic
under C# 8 with .NET SDK 8.0.423. It checks exact NUnit discovery, 27 Python guards,
failing NUnit/scenario controls, repeated scenarios and report safety. Raw ignored
results are under `runtime/dotnet/artifacts/`; they are not a Unity test run.

The latest offline run passed 747/747 tests, including 42 linked movement/mechanics
cases, eight control cases and nine shared-carry cases; no failures or skips.
The 27 guards, intentional failing controls and twelve scenarios repeated twice
also passed their declared checks. Prior runs remain recorded in Git/evidence history.

Native tests: four animation binding/lifecycle EditMode cases and ten physical
attachment/throw/targeting tests exist but are **NotRun**. Roslyn syntax parsing and static
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


## Ragdoll audit and implementation, 2 October 2026

The user authorized a physics audit, fixes and complete ragdoll code while preserving
unfinished animation assets. The adapter now has a repeatable 16-segment weighted
rig builder; bounded CharacterJoint/solid-shape inventory, mass and root-convention
validation; sampled linear/angular momentum handoff; capped aggregate impacts;
continuous dynamic collision for supported shapes; fault latching and clean teardown.
Body carrying targets the actual pelvis and applies aggregate-mass force/gravity
support. Collision scopes preserve their original policy across owned lifetimes.
Conscious Down adds bounded crawl/brace, camera tracking, help feedback and nearby
fixed-handle gripping through the canonical claim/lease/receipt stream. Recovery
uses current supported pelvis placement, front/back anatomical axes, standing
clearance, a pose-preserving root move and elapsed-time bounded playback.

Audit fixes include the wrong Schedule argument order, interaction reentry within a
capsule move, stale motor state after get-up, body reach tied to the old root,
reset momentum on repeated hits, tangential impact classification, root Rigidbody
competition, missing Editor assembly reference, destroyed held-body cleanup,
helper collision policy restoration, and malformed/unbounded rigs. Station cycles
now fence patient/epoch/injury/timer/presentation and reserve before cosmetic effects;
blocked locker exits wait rather than enabling a capsule in obstructed space.
The calibrated A-pose elbow axis was corrected without editing bone transforms or
animation files. Setup/control instructions live in the worker binding guide.

Latest verifier: **765/765 offline tests passed**, including the previous 747 plus
11 downed-handle cases and seven ragdoll tuning/station-ticket cases; 27 guards,
intentional failing controls, report-safety checks and twelve scenarios repeated
twice passed. All eight shipped canonical rule libraries rebuilt with zero warnings
or errors. Static inventory: 93 metadata GUIDs, 13 asmdefs, 46 C# files; C# 8 syntax
parsing reports zero errors. Exact input/source hashes and earlier runs remain in
the evidence JSON. The first focused compile used a nonexistent `InteractionReply.Claim`
member; the corrected `State` access passed the focused and full checks.

There are **43 native feature cases written but NotRun**: four animation binding,
14 carry/handle/targeting, 23 ragdoll physics/validation and two rig builder cases.
Native station callback admission/complete-scene regression fixtures remain Planned;
source review/ticket tests cover only their stated portion. Native import/type
compilation, physics/Player execution, all finished 49-clip contacts, multiplayer,
performance and human feel remain **Blocked/unverified** without the pinned activated
Editor and finished assets. No acceptance gate advances. Four read-only audit agents
reviewed separate concerns; root authored fixes. Independent PR/human review remains
pending and the PR stays draft. No animation source, clip, Animator controller,
map or art file changed.

## Bonk shovel follow-up, 2 October 2026

The next authorized extension adds shovel hits, a procedural bonk pose and original
tin sound while preserving unfinished animation assets. Its current 784-test run,
51-case unexecuted native inventory and exact source/audio hashes are recorded
separately in [BONK_SHOVEL.md](BONK_SHOVEL.md) and
[bonk-shovel-evidence.json](bonk-shovel-evidence.json). The results above remain
historical evidence for the ragdoll baseline `cd51c6a`; neither record establishes
native compilation, finished-clip acceptance or a multiplayer test.
