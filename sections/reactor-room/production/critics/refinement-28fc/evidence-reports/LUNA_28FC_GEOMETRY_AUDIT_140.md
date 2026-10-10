# 28fc finite geometry audit — issue 140

## Source and declared change

Current source: `/workspace/scratch/reactor-refinement-generator-visible-working/hall_final.blend`, SHA-256 `28fc09a259369b685ca1f96ad78cfd19bc0992f4ae67b200cb2143d9272905e3`. Cold reproduction: `/workspace/scratch/reactor-refinement-generator-visible-working-cold/hall_final.blend`, SHA-256 `2f50f597c56f9c06db8514392ccc57be8219c52b6ac6798e24a54fdff940bec4`. The exact 870b→28fc comparison `/workspace/scratch/reactor-refinement-generator-visible-working/scene-delta.json` (SHA-256 `d460a1f10d05647b5076d4211f048fbcce791685bccdd5c591f151ba1836de28`) changes only the five listed generator plaque/lettering/trim/spacer objects; 1,963 objects are unchanged, with no additions, removals or unexpected changes. This report is limited to the declared finite geometry/authoring checks below.

## Evidence reviewed

| Check | Source-bound evidence | Result |
|---|---|---|
| Warm authoring checks | `/workspace/scratch/reactor-refinement-generator-visible-working/checks.json` SHA `288dd3243efaeddf5b8b88c3775d890592103b2f0f0b38de9709112a5baf004b` | 14/14 pass; all exits 0; file declares source `28fc09a259369b685ca1f96ad78cfd19bc0992f4ae67b200cb2143d9272905e3` |
| Warm control-room aggregate | `/workspace/scratch/reactor-refinement-generator-visible-working/control-room-check.log` SHA `b3083af6e9824945fb685afe6965cc50a116c7b2d76ad9fcce169f3ee71d53fe` | `RESULT: PASS`; reachability summary reports 100% of free area, but copier/printer/rack/locker-front subchecks are individually marked `BLOCKED`. This audit does not treat the aggregate as proof of those individual fronts. |
| Warm sign/support audit | `/workspace/scratch/reactor-refinement-generator-visible-working/audit.json` SHA `c07c0439df2328e36cce3df996ebd04a173511c7a3280f1b1f5446db90402d88` | 204 sign records, zero failures; 738 camera visibility records; all 13 required sightlines pass. Support: 3,521 sampled records, zero failures; 2,148 registered assemblies / 29 owner groups, no empty registrations; 290 protected objects unchanged. |
| Generator spacer clearance | `/workspace/scratch/reactor-refinement-generator-visible-working/generator-mount-clearance.json` SHA `40a8b1296a4f38cb3b89a21e4f8f7446d3d5181c859e784107d927dfcf321f5d` | 12 records: four extended spacer centerlines × three named conduit/support/clip targets; 101 samples per line; minimum centerline-to-surface distance 0.173000 m with 12 mm radius; all pass. |
| Named service-core bores | `/workspace/scratch/reactor-refinement-generator-visible-working/wall-bores.json` SHA `97a4c8f8d216d2aca64bc6d73a34303033e66680e6a4c2b0e4531aa2a2e8d1bd` | Eight service cores, 65 rays each (520 total), no enclosure hits. |
| Cold authoring checks | `/workspace/scratch/reactor-refinement-generator-visible-working-cold/checks.json` SHA `042cfa2b9483ad6e75745d43f3440be8cb7c4f30a76df368ab38e53fc3d73717` | 14/14 pass; all exits 0; file declares cold source `2f50f597c56f9c06db8514392ccc57be8219c52b6ac6798e24a54fdff940bec4` |
| Cold control-room aggregate | `/workspace/scratch/reactor-refinement-generator-visible-working-cold/control-room-check.log` SHA `8212fa80ab337cf9447a8917d89c84e9c3b6010c3ff4314f4edad4a69cdea3ca` | `RESULT: PASS`; same local blocked-front subchecks remain visible in the log and are not individually passed. |
| Cold sign/support audit | `/workspace/scratch/reactor-refinement-generator-visible-working-cold/audit.json` SHA `b1d14ed91da16317982985e7ae5e544e7ed01d467de9db7dfa5e4e0b80e23571` | 204 sign records, zero failures; 3,521 sampled support records, zero failures; 2,148 registered assemblies; 290 protected objects unchanged. |
| Declared warm/cold comparison | `/workspace/scratch/reactor-refinement-generator-visible-working-cold/scope.json` SHA `554f7cb52862853027f1a20f650ef62d7824694df0546de8a25efd5881016a52` | 124/124 named owned comparisons match. It does not compare every inherited scene object or all animation keys. |

## Disposition and limits

Accept #140 for this exact finite 28fc scope. The sampled checks support the generator mount clearance and registered assembly, sign-sampling, named-bore and declared warm/cold comparison results. They do not prove exhaustive all-pairs collision absence, whole-scene cold equivalence, rendered sign legibility, global visual quality or final art score. In particular, passing sampled #140 records does not close #9 or #139: current full-quality pixels are still required to review intended sign visibility.
