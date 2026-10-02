# Bonk shovel: hit, procedural animation and tin sound

User-authorized implementation, 2 October 2026; baseline
`cd51c6a1b9cdf5dce9efb67212793e33da2cf7f7`; branch
`feat/unity-movement-animations-20261002`; draft PR
[72](https://github.com/CameronNel/critical-shift/pull/72). Codex is the primary
author. Independent human review/merge remains pending; no self-merge.

## Result and assignment

Left-click with the bonk shovel starts a procedural wind-up, strike and recovery.
A confirmed hit on another registered worker applies nonlethal Knockdown through
the canonical worker workflow and enters that worker's jointed ragdoll. Their
held claim is released; an alert worker stays alert with conscious-down agency.
Recovery is allowed after 2 s, subject to the existing physical checks. A solid
wall/object consumes the swing and starts recoil without hitting through it.
A miss completes its follow-through silently. E still uses a bound DigSite.

In **Critical Shift > Scene bindings**, bind the selected physical object as
**Shovel**, then wire/validate the scene. This adds BonkShovel and assigns the
included WAV to a dedicated child spatial AudioSource, with Doppler disabled.
Assign the actual root Rigidbody/grip and worker/ragdoll references using the
[existing binding guide](../unity/Assets/CriticalShift/Features/Workers/README.md).
No map, scene or prefab was generated as an acceptance fixture in this environment.

The animation is gameplay pose code layered after the existing held-tool playback:
grip wind-up, arm IK, strike, follow-through and contact-to-rest recoil. No `.blend`,
FBX, `.anim`, Animator controller, existing clip table, authored skeleton transform or
map/art file is edited. The original 49 take routes and SHOVEL_DIG remain intact.
Final imported assets still need native contact/pose inspection.

## Ownership and bounds

BonkOperations is a narrow Application action coordinator inside WorldSession.
Begin uses the existing command envelope/terminal receipt stream and current
exclusive claim generation. Replays return the same immutable swing/cause without
starting motion again. The shift clock owns a 180 ms wind-up, contact through
320 ms, 700 ms presentation and 950 ms start-to-start cooldown. Setup-only worker
and object capacities bound action/history storage. Claims, health and time retain
their existing owners.

Bootstrap supplies trusted host observations through BonkHitQuery: radial solid
obstruction, swept blade segment and side-contact visibility, using bounded
64-entry buffers and at most eight subdivisions per actor/tick. Saturation fails
closed and consumes the strike without inventing an impact sound. The default
volume is a 0.16 m radius along a 0.95–1.4 m eye-relative blade path. One confirmed
contact consumes a swing. Self, stale epoch/lease/sequence, wrong actor, early/late
and duplicate contacts cannot apply damage. A frame hitch beyond the strike window
does not queue a delayed hit. Ordered target/tool observations and the minted swing
cause flow into the existing impact trace.

Workers.Unity owns the procedural grip/arm projection; FacilityPhysics.Unity owns
temporary kinematic tool motion and restores dynamic carry, collision-detection
mode and interpolation afterward. Normal carry forces are suspended during its
accepted swing. Cancel, pause, release, actor impact/disconnect, ownership expiry,
disabled binding or destroyed owner/body stop it. Bootstrap composes the engine
ports without a peer implementation dependency. Built-in audio `1.0.0` is the only
added module; D-02 transport remains open. This host-scene path is not a multiplayer
implementation or proof.

## Sound and actual checks

**Current sound:** Harrisando's CC0 **Bonk.wav**, selected by the user after the
initial implementation. The high-quality public MP3 preview is converted to mono
48 kHz, 16-bit PCM (1.835 s), with headroom applied before quantization. Original
lossless download requires a Freesound login. The existing asset path/GUID and scene
bindings are retained. The superseded synthesis generator is removed. Current
source/conversion hashes and checks are in
[harrisando-bonk-evidence.json](harrisando-bonk-evidence.json). The sound-swap checks
do not constitute native Unity import/mix acceptance; those remain unverified.

The following synthesis and 784-test evidence is historical for the initial bonk
implementation at `a587d9e`; the gameplay/presentation C# is unchanged by this swap.

The initial sound was deterministic modal synthesis: a hollow low tin "tonk",
short bright rim and cartoon pitch scoop. No external samples or recordings were
used for that version. Its then-present `runtime/tools/make_bonk_sound.py` produced
a mono 48 kHz, 16-bit PCM WAV, 0.54 s, peak 0.820, with no clipped samples and zero
endpoints. Playback still occurs once after accepted player/solid-object contact,
at pitch 1 with spatial attenuation. Current source/import details are in the audio
folder README.

The final `python runtime/dotnet/tools/verify.py` run passed **784/784 tests** with
zero failures/skips: previous 765 plus 14 bonk rule cases and five pose cases linked
from their actual Unity source. All 27 Python guards, deliberate failure controls,
report-safety checks and twelve scenarios repeated twice passed. The initial full
783-test pass preceded additional contact-recoil/pause coverage; both runs passed.
The final verifier input inventory contains 117 matching source hashes. Raw TRX/logs
are in ignored `runtime/dotnet/artifacts/`; exact counts/input hashes are preserved
in [bonk-shovel-evidence.json](bonk-shovel-evidence.json).

Eight first-party rule DLLs rebuilt from current canonical source with zero warnings
or errors. Static checks passed for 105 metadata GUIDs, 14 asmdefs and current DLL
source/binary hashes. C# 8 syntax parsing found zero errors in 53 Unity files; this
is **not** Unity API/type resolution. WAV header/peak/endpoints/hash checks passed.

Eight new native bonk fixtures are written but **NotRun**; together with the prior
43, the current native feature inventory is 51. Complete host/rig/audio fixture
coverage is **Planned**. Native import/type compilation, physics/Player, finished
animation alignment, audio mix, multiplayer, performance and human feel acceptance
are **Blocked/unverified** because the pinned activated Unity Editor and finished
imported character are unavailable. No roadmap, technical, art or human gate advances.
This extension was self-reviewed by the primary author; previous ragdoll agent
reviews are not independent evidence for these new bonk changes. PR stays draft.
