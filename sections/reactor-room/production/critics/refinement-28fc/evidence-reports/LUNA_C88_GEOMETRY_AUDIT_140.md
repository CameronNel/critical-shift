# C88 finite geometry and support review (#140)

**Candidate:** `/workspace/scratch/reactor-refinement-cycle88/hall_final.blend`  
**Source SHA-256:** `85766edcb5cf1ba1d5fa9bc624a956132885298e9c379aad3867a1fca0560cf6`  
**Parent:** C87 `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`  
**Status:** accepted only for the finite requested support/intersection QA scope. No final artistic score or all-item acceptance.

## Source scope

The exact C87→C88 comparator [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle88/scene-delta.json), SHA-256 `852b2d50e4293200ea86437a776ab3c31a3fbec68af745bccc10046d1cb028dd`, passes with only `RH walls girders STEEL` changed; 1,932 objects are unchanged, with no additions, removals, or unexpected changes. The change is a cloned neutral-gray roof-girder finish (RGB 0.22, metallic 0.12, nominal roughness 0.56). The comparator reports unchanged transforms, mesh geometry, lighting, camera optics, and other material graphs within its declared scope. It is not a whole-scene runtime or exhaustive collision comparison.

## Current finite gates

- Warm [`checks.json`](/workspace/scratch/reactor-refinement-cycle88/checks.json), SHA-256 `8bf6350f534796e954f28986a9a88451e45e359eea4a00d68cdfea6db997517d`: 14/14 checks pass for exact C88.
- Separate current control-room verifier [`control-room-check.log`](/workspace/scratch/reactor-refinement-cycle88/control-room-check.log), SHA-256 `8f4b34e45944eb78ece61136f635f0a20fbb063fde45cb5e5d9470f1e3d930a1`: PASS.
- Current [`audit.json`](/workspace/scratch/reactor-refinement-cycle88/audit.json), SHA-256 `d9b0396ad79ee07038d1cca26dcd34455c165da4aa94ca922ac87fc909e192d8`: 290 protected objects unchanged; 203 signage records, zero blocked; 2,809 sampled support/contact records, zero failures; 1,957 registered assemblies across 27 owner groups; no empty registrations.
- Cold [`checks.json`](/workspace/scratch/reactor-refinement-c88-cold/checks.json), SHA-256 `fdee201978191ede5b125d36b671cea7e5a2184893660be926836e74f888dcde`, passes 14/14 on cold source `4edfc4f2add196c039790605949105994ded9e1629db75c398b59fe846adc086`. Separate cold control-room verifier [`control-room-check.log`](/workspace/scratch/reactor-refinement-c88-cold/control-room-check.log), SHA-256 `abd265a24dedf3441f9bb6adedba6c76dca3d1c6ae809622015adb0d343400cd`, reports PASS.
- Cold [`scope.json`](/workspace/scratch/reactor-refinement-c88-cold/scope.json), SHA-256 `f1307cb3b896f3e33c04bc601d43dc8d324ca7dfaa788882abb888b912c57f42`, matches 57/57 declared owned comparisons. This does not assert complete scene equivalence.

The C88 material change adds no new geometry or support interface, so the finite C87 review scope remains current after the exact scoped material delta. A separate exact-source roof-finish probe, [`roof-finish-probe.json`](/workspace/scratch/reactor-refinement-cycle88/roof-finish-probe.json), SHA-256 `cb0529b2958fce9fb2e4d10fb40329c56d5cf7e07bc031849f4b719fb01148e8`, confirms the original shared material, world/exposure and light settings remain unchanged; two in-memory stage applications are idempotent. This closes #140 only as the requested finite QA. It is not an exhaustive all-pair, all-vertex, or full-scene collision certificate, and it does not replace any visual evidence.

