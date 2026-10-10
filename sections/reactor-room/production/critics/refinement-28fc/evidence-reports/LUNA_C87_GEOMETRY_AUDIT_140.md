# C87 finite geometry and support review (#140)

**Candidate:** `/workspace/scratch/reactor-refinement-cycle87/hall_final.blend`  
**Source SHA-256:** `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13`  
**Parent:** C86 `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`  
**Status:** accepted only for the requested finite support/intersection QA scope. No final artistic score or all-item acceptance.

## Source scope

The exact C86→C87 object comparison is [`scene-delta.json`](/workspace/scratch/reactor-refinement-cycle87/scene-delta.json), SHA-256 `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be`. It passes with exactly three changed entries: `R2 floor`, `RH services R2 PIPING diffuser STEEL`, and `RH services R2 PIPING diffuser slot BLACK`; 1,930 unchanged, no added/removed/unexpected objects. The comparator covers the declared object transforms/parents, mesh arrays/materials, visibility/driver and material graph fields, light settings, and camera optics. It is not a whole-scene dynamic or all-pair equivalence claim.

## Current finite gates

- Warm [`checks.json`](/workspace/scratch/reactor-refinement-cycle87/checks.json) SHA-256 `d55ef41a311dbb62174d41cd7326f0eaefaf37b38f9aad2c4976f83015c60128`: 14/14 authoring checks pass for exact C87 source.
- Separate control-room verifier: [`control-room-check.log`](/workspace/scratch/reactor-refinement-cycle87/control-room-check.log) SHA-256 `6b47ee0aded62c20168e51fae46e6abc9869c30085e70ff54b5a448682648c88` reports PASS.
- [`audit.json`](/workspace/scratch/reactor-refinement-cycle87/audit.json) SHA-256 `fbf2ca37e37328f6b838b257e10054689c585b12fa16a1c892f97506112ed5c2` is source-bound; 290 protected objects unchanged; 203 signage records, zero blocked; 2,809 sampled support/contact records, zero failures; 1,957 registered assemblies across 27 owner groups; no empty registrations.
- Cold [`checks.json`](/workspace/scratch/reactor-refinement-c87-cold/checks.json) SHA-256 `8b35d85f0afe770fbfa5c5e519ec92e491204ed1d3770ba1b7c71e03dec2a180` passes 14/14 on cold source `b073d81c2e0d51f14565ec167b37daa7f3272111b9a289357521f765f7fb2960`; separate cold control-room verifier [`control-room-check.log`](/workspace/scratch/reactor-refinement-c87-cold/control-room-check.log) SHA-256 `fb5306c8a79f1dd711241430f882b59afa7503af4f070ee7808401ca05fbb291` reports PASS.
- Cold [`scope.json`](/workspace/scratch/reactor-refinement-c87-cold/scope.json) SHA-256 `7c4f78c01f310684ddc8da57417971e229ebb47e0a79fface326041af5672ca0` matches 56/56 declared owned comparisons. This is limited to those comparisons, not full-scene equivalence.

## Independent diffuser geometry probe

The read-only, exact-source [`diffuser-probe.json`](/workspace/scratch/reactor-refinement-cycle87/diffuser-probe.json) SHA-256 `5c3daf39172401d1c2fef5452b20bcd9d7c9de6cb92a71e1a21fa64d635ecdd4` confirms the two changed diffuser meshes rebuild idempotently and have closed manifold surfaces, positive signed volume, no degenerate faces, and no sampled liner intersections:

| Mesh | Vertices | Faces | Signed volume (m³) | Minimum sampled liner gap |
|---|---:|---:|---:|---:|
| Diffuser steel shell | 1,152 | 1,232 | 0.00059817 | 7.946 mm |
| Dark recessed channel/support core | 150 | 107 | 0.00064236 | 13.943 mm |

The geometry has a 70 mm outer shell radius, 6 mm shell wall, 40 actual side-window gaps, dark recessed core, and three upper support links. The fitted flange remains at 75 mm radius. The probe uses finite mesh/liner overlap and vertex-gap checks; it does not certify every ray, load, or dynamic pose.

This closes #140 only as the requested bounded geometry/support audit. It does not prove all geometry everywhere, or substitute for full-resolution artistic inspection of the modified floor material and pool inlet.
