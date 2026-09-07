# Sol independent technical review — Reactor Art08

**Reviewer:** Sol
**Review date:** 2026-09-08
**Decision:** **FAIL — not technically acceptance-ready**
**Acceptance rule:** every applicable rubric category must independently score at least 90/100 and there must be zero critical defects.

This is a read-only review of the frozen Art08 source, saved scene, ten fixed renders and three diagnostics. I did not edit or save the source or `.blend`, did not render, and did not commit or push. The active `blender/` files changed during the review and were excluded after that change; all findings below are pinned to the archived Art08 pair.

## Controlling evidence

| Artifact | Size | Modified (UTC) | SHA-256 |
|---|---:|---|---|
| `production/revisions/art-08/build_scene.py` | 97,450 B | 2026-09-07 22:03:08.1631083 | `9C2D57BA4ACA3243CB0C4AF66483E002A1CAC50DDD1086BBE5607C6FB7061593` |
| `production/revisions/art-08/reactor_scene.blend` | 2,080,171 B | 2026-09-07 22:03:08.8676584 | `EA7D792ACCD43F02F80597D1FB04FDCF0B756C94E1829673763FF36F545D89A2` |

The reopened scene reports `art_revision = art-08`, layout `P02`, visual targets `A02 / B01`, 4,831 objects, 4,028 mesh datablocks and 34 materials. Its stored `source_sha256` exactly matches the source above. No external libraries or image textures are linked; the only path-like dependency is Blender's built-in Bfont. Static source inspection found no append, library, file-import or image-load call.

The archived pair and Art08 output files are untracked against repository HEAD `14a56726b0e9d9df955d5c69f42fb092cd4f031f`, and their Windows read-only flags are false. “Immutable” is therefore a process condition, not VCS or ACL enforcement; the hashes above are the identity boundary for this review.

## Audit method and reproducibility

Blender MCP exposed no reachable reactor instance, so I used Blender 5.2.0 LTS directly in background mode with a private reviewer profile. The run used `--factory-startup`, `--disable-autoexec`, two CPU threads, the archived blend, and a reviewer script that only queried datablocks/evaluated geometry and wrote JSON to this review worktree. It made no `save` or `render` call.

```powershell
$env:BLENDER_USER_CONFIG = 'C:\Users\Camer\.codex\worktrees\8ad3\critical-shift\.tmp-art08-audit\profile\config'
$env:BLENDER_USER_SCRIPTS = 'C:\Users\Camer\.codex\worktrees\8ad3\critical-shift\.tmp-art08-audit\profile\scripts'
$env:BLENDER_USER_DATAFILES = 'C:\Users\Camer\.codex\worktrees\8ad3\critical-shift\.tmp-art08-audit\profile\datafiles'
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background --factory-startup --disable-autoexec --threads 2 `
  'C:\Users\Camer\Games\critical-shift\worktrees\reactor-valorant\sections\reactor-room\production\revisions\art-08\reactor_scene.blend' `
  --python 'C:\Users\Camer\.codex\worktrees\8ad3\critical-shift\.tmp-art08-audit\sol_art08_audit.py' -- `
  'C:\Users\Camer\.codex\worktrees\8ad3\critical-shift\.tmp-art08-audit\sol_art08_audit.json' `
  'C:\Users\Camer\Games\critical-shift\worktrees\reactor-valorant\sections\reactor-room\production\revisions\art-08\build_scene.py'
```

Reviewer script SHA-256: `20BA36E57E531B886722106DBB304299281BEFBA95347E472D4F8DE977E75022`
Reviewer JSON SHA-256: `6AC4944738423FA68EA4D1267112BB1ECDE1A0A2D0EC24948EB6E903D2FF0DF0`

The mesh audit covered evaluated topology, winding, signed volume, object/world bounds, selected BVH endpoint states, action data, moving-bank engagement, service endpoints, support contacts and duplicate bounds. All ten fixed PNGs and all three diagnostic PNGs were also inspected at native resolution. The P02 architectural PDF, current art direction, rubric, camera brief and approved A02/B01 references were used as the comparison set.

## Acceptance blockers and defects

### SOL-08-T01 — Critical: primary floor meshes have invalid winding and open topology

- All 48 `Hall floor segment*` meshes are incidence-closed but inconsistently wound. Their top caps point down (`-Z`), their bottom caps point up (`+Z`), and adjacent cap/side edges run in the same direction. Each segment produced 36 shared-edge orientation conflicts. A signed-volume-only test does not detect this mixed winding.
- The 68 `Sealed floor slab*` objects contain 298 disconnected slab pieces with upward top faces, inward side faces and no bottom faces. Static reconstruction counted 1,108 open bottom boundary edges and 16 zero-area side quads caused by duplicated clipped coordinates.
- Across 4,763 evaluated geometry objects, 3,843 were closed manifold and 920 were open/nonmanifold. Exactly 116 objects had shared-edge orientation conflicts: the 48 hall segments and the 68 sealed-floor slab objects above. Open geometry elsewhere was not automatically classified as defective.

These are broad, primary architectural surfaces, not hidden microscopic residue. This is a critical technical-cleanliness failure even though double-sided rendering prevents a uniform black or missing-floor symptom in the submitted pixels.

### SOL-08-T02 — Major: full-span ring generator creates coincident seam faces

Thirty-six full-circle `ring()` meshes duplicate the 0/2π vertices and contain two coincident, oppositely facing radial end caps at the same seam. The affected set includes the floor inlay, curb/datum rings, bank guide flanges and collars, tank bands, one replacement seal and one mug. The 288 intentionally partial ring arcs are a separate case and were not included in this defect count.

No exact duplicate world bounds were found among objects larger than 0.05 m, so this is an intra-mesh seam defect rather than duplicated whole objects.

### SOL-08-T03 — Major: saved articulation evidence does not establish complete mechanical articulation

- The service gate has a stored fake-user action from 0° to 90° over frames 1–36. Its four moving children are three yellow rails and the latch stile. The action is detached on reopen, so the saved default state is static and the action must be assigned to demonstrate motion.
- The fixed rail-post gap measures `1.399999976 m`; the 24 nm numerical shortfall from 1.4 m is floating-point noise and is accepted by the producer's `1e-5 m` tolerance. Reviewer BVH tests found no triangle-surface intersection at the closed and open endpoints.
- Two static objects are both named `Gate hinge`, at X `-0.76 m` and `+0.76 m`, while the gate pivot is X `-0.7375 m`. Only the left object is aligned with the motion axis; the right object remains static when the leaf opens. The saved assembly therefore presents mechanically ambiguous hinge/latch hardware.
- D01 and D02 each preserve a detached ±90° fake-user action over frames 1–40. Each pivot has four moving children: leaf, vision glass, panic bar and marking. The hinge itself is an Empty, with no visible knuckle or pin represented by that parenting count. Endpoint BVH tests found no triangle-surface intersection at either door's stored closed/open states.

The BVH test sampled endpoints only. It does not certify the full continuous sweeps between endpoints.

### SOL-08-T04 — Major: reproduction evidence is internally inconsistent

- `production/revisions/art-08/fresh-build-validation.json` reports 4,831 objects, 4,029 meshes, 36 materials, `cold_start:false`, and 716.74 s.
- `art/renders/art-08/validation.json` reports 4,831 objects, 4,028 meshes, 34 materials, `cold_start:true`, and 131.4 s. It was overwritten by the later diagnostic reopen rather than preserving the ten-render batch state.
- The source authors 34 materials. The initial extra two materials and one mesh are consistent with unpurged startup/orphan datablocks: the builder deletes objects/collections but does not purge datablocks.
- Both JSON files repeat the scene's stored source hash; neither independently hashes the executing source or records the blend hash.
- The archived script is byte-identical to the builder copy, but its `ROOT = Path(__file__).resolve().parents[1]` assumption points at `production/` when executed in the archive folder. The frozen archive is therefore not directly runnable in place as a self-contained build entrypoint.
- `old_3d_imports: []` is a hard-coded result, not an independent scan.

The logs and files do establish that all ten fixed renders and all three diagnostics exist. They do not establish one internally consistent, immutable, cold-start archive package.

### SOL-08-T05 — Moderate: several automated “passes” are narrower than their labels

- The producer's clearance checks use arithmetic constants for several requirements rather than evaluated scene geometry.
- The reviewer's first polar circulation test returned `cycle_found:false`, but that result is invalid and excluded: evaluated object bounding boxes for numerous parented curve objects were unsuitable as navigation obstacles and produced false blockage. The hard bottleneck and portal measurements below pass, and PLAN pixels show an apparent loop, but a valid mesh-level full dressed-route sweep was not completed. The continuous 1.2 m loop is therefore not conclusively certified by this audit.
- Door checks establish parenting and stored endpoint transforms, not hinge hardware or continuous swept clearance.
- Bank validation samples seven frames and axial extents. Because the location curves are Bezier and intermediate extrema were not sampled continuously, keyed-state success is not a proof against between-key overshoot.

### SOL-08-T06 — Moderate: additional small normal and degeneracy defects

- 182 closed evaluated meshes have negative signed volume. All are smaller than 0.25 m in maximum dimension; only seven are at least 0.1 m. They are concentrated in fasteners, rivets, shell/light details, CRT chart-grid pieces and contact-wear details. No additional large closed solid was found with negative volume.
- Every generated hatch edge-chip quad and the 14 actuator localized paint-chip quads face local `+Y`, into backing faces whose exposed side is local `-Y`.
- Six floor scuffs are distinct, upward-facing, non-shadow-casting overlays at `0.00015 m` above six different service-ring sectors. They are intentional decal/contact layers, not duplicate or coplanar-shadow defects.
- The 16 sealed-riser chamfer panels are now closed, conflict-free and positive-volume (`0.612148–0.634619 m³`). The three control-room glazing solids are also conflict-free and positive-volume. These previous-risk areas pass.

## Objective P02 checks

| Requirement / check | Saved-scene measurement | Result |
|---|---:|---|
| Hall span | authored 21.600 m; evaluated bevel bounds 21.606 × 21.606 m | Pass |
| Pool aperture / rim / service envelope | 6.8 / 7.8 / 10.4 m nominal | Pass |
| Service-ring radial width | 1.300736859 m across 32 pieces | Pass |
| Water level to pool bottom | `-0.450000018` to `-6.5 m`; depth `6.049999982 m` | Pass |
| Turbine P02 envelope to service ring | `1.312488004 m` (hard minimum 1.31 m) | Pass, 2.488 mm margin |
| Actual turbine skid to service ring | `1.353685726 m` | Pass |
| Main / fuel / cooling / east-control portals | `6.000999907 / 5.000999928 / 5.000998497 / 3.999999881 m` | Pass |
| D01 clear opening | `1.200000286 × 2.099999905 m` | Pass within floating-point tolerance |
| D02 clear opening | `1.199999809 × 2.100000381 m` | Pass within floating-point tolerance |
| Stair enclosure plan | `6.249999046 × 3.200000048 m` | Pass |
| Four flight clear widths | `1.200000239 / 1.2 / 1.200000239 / 1.2 m` | Pass |
| Stair count | 13 tread meshes per flight; 48 intermediate risers plus four landing rises = 56 rises | Pass |
| Landing clear dimension | 1.300 m slab short dimension; 1.250 m after 25 mm rail radius each side | Pass |
| Control room | floor top +10.0 m; 6.400000095 m clear depth; centered Y; two desks | Pass |
| Registered grounded supports | 38 tested; maximum absolute floor delta 0.0 m | Pass for registered set |
| Full continuous dressed route | hard pinch points pass; PLAN appears continuous; valid full nav sweep absent | Not conclusively verified |

The south-side SCRAM, alarm-acknowledge and bypass controls are present as distinct named assemblies with interaction metadata. In fixed view 03, the illuminated ACK button visibly occludes part of the `ACKNOWLEDGE` word, weakening label readability.

## Moving-bank stroke and engagement

Exactly two moving roots are present at X ±1.4 m, with 75 moving descendants per bank. Each fixed housing is separate and is not parented under the moving root.

| State | Bank A root Z | Bank B root Z | Upper engagement per bank | Lower engagement per bank | Axis offset |
|---|---:|---:|---:|---:|---:|
| Frame 1 nominal | 8.600000381 m | 8.600000381 m | 2.045000076 m | 0.205000162 m | 0.0 m |
| Frame 90 | 8.479999542 m | 8.560000420 m | 1.924999237 / 2.005000114 m | 0.325001001 / 0.245000124 m | 0.0 m |
| Frame 192 down | 6.800000191 m | 6.800000191 m | 0.244999886 m | 2.005000114 m | 0.0 m |
| Frame 196 rebound | 6.840000153 m | 6.840000153 m | 0.284999847 m | 1.965000153 m | 0.0 m |
| Frames 201 and 240 down | 6.800000191 m | 6.800000191 m | 0.244999886 m | 2.005000114 m | 0.0 m |

The keyed stroke is 1.8 m. The minimum sampled upper engagement is 0.244999886 m and the minimum sampled lower engagement is 0.205000162 m, leaving approximately 45 mm and 5 mm over the source's 0.2 m criterion. Source dimensions give 50 mm radial clearance at the upper slider/bore and 10 mm at the submerged guide. Fixed housings remain stationary. The keyed states pass; continuous Bezier extrema remain unproven as noted above.

## Services and assembly contact

The four named service families are present: coolant supply/return, sampling, vent, and cable/power. Exact endpoint checks found:

- pump-to-supply and supply-to-turbine gaps: 0 m;
- turbine return endpoint gap: `2.38e-7 m`;
- return-to-pump suction gap: `4.77e-7 m`;
- ECCS branch-to-supply gap: `9.83e-7 m`;
- manifold wall-tie to upper-tie gap: `9.83e-7 m`.

The coolant endpoint alignment passes at numerical precision. Each `tube()` is nevertheless a separately capped curve, so coincident joins are capped-solid contact/interpenetration rather than one welded watertight network. I classify these as intentional assembly contacts, not accidental clipping. The local sampling inlet is free-ended and is not demonstrated as a continuous global line.

Other intentional contacts include approximately 0.150 m gantry lower-flange/saddle engagement, 0.085 m neck/saddle contact, 0.105 m neck/housing contact, and approximately 0.025 m moving-flange engagement with carriage/column parts. Their location and role are consistent with support or bearing contact. No major free-floating machine or registered support gap was found.

## Render-pixel technical inspection

All 13 required PNGs exist, are non-zero and decode at their intended native dimensions: view 01 `1440×1800`, 02 `1440×990`, 03–08 `1440×900`, 09 `1440×1843`, 10 `1440×1080`, CONTROL `1280×960`, and PLAN/POOL `1280×1280`. No frame is corrupt, blank, or globally clipped. Sampled saturated-white pixels occupy at most about 0.034% of a production frame; localized diagnostic pool lighting reaches about 0.16%. View 09 has the largest sampled near-black area, about 3.663%, concentrated in ceiling voids.

Observed camera-level defects and limitations:

- **01 HERO:** the assembly is grounded and the banks connect into the pool, but the cream wall panels show broad pillowed/dented highlight bands. The gate state is not clearly readable.
- **02 WEST ENTRY:** bright multi-lobed bloom behind the rods reduces ceiling/control-room detail; wall-panel undulation recurs.
- **03 SOUTH GATE:** the illuminated ACK control overlaps the `ACKNOWLEDGE` label. The saved gate articulation is not clearly communicated by the still.
- **04 TURBINE AISLE:** the skid reads grounded and no visible hard intersection appears. Wall pillowing remains visible.
- **05 REVERSE NORTH:** major service runs appear continuous; wall highlight warping remains visible.
- **06 CONTROL ROOM:** foreground glazing sill/mullions obscure much of the hall and bright cyan/white reflections weaken clearance evidence.
- **07 COMPACT STAIR:** flights and landings read connected. A left half-landing practical is tangent to or partly occluded by the upper flight/stringer; pixels alone do not establish whether it intersects.
- **08 MATERIAL SLICE:** pipes, flanges and supports read continuously with no obvious pixel-level clipping.
- **09 BANK MECHANISMS:** this is the clearest articulation view, but dark ceiling voids lose beam detail.
- **10 EAST HIGH:** banks are visibly connected into the pool; upper housings are cropped.
- **CONTROL diagnostic:** floor/support contact is readable, but ceiling-practical reflections ghost across the glass and the right bank is cropped.
- **PLAN diagnostic:** the service loop appears continuous, but the image is not a measured clearance proof.
- **POOL diagnostic:** rods reach the lower collars/bases; localized cyan-white bloom obscures the exact lowest-contact read.

The recurring cream-wall pillowing is a real pixel defect across views 01–05 and 10 relative to the flatter A02 reference. The mesh audit did not identify a corresponding large wall winding failure, so this report classifies it as an unresolved shading/material-response artifact rather than claiming geometric deformation.

## Applicable category scores

| Rubric category | Score | Technical basis |
|---|---:|---|
| 1. Scale, construction and circulation | **86/100 — Fail** | P02 dimensions, portals, stair widths, hard bottleneck and registered grounding pass; full dressed-route continuity is not independently certified, and gate/door mechanical evidence is incomplete. |
| 3. Reactor hierarchy / focal clarity | **87/100 — Fail** | Bank/pool hierarchy is legible in the strongest views, but bloom, cropping and ambiguous gate presentation obscure technical relationships in several required views. |
| 7. Environmental credibility | **82/100 — Fail** | Core coolant endpoints and support contacts are credible; capped-curve joins, a free-ended sampling inlet and ambiguous static hinge hardware reduce system credibility. |
| 8. Technical cleanliness / reproduction | **58/100 — Fail** | Critical primary-floor winding/open-boundary faults, degenerate faces, 36 ring seam duplicates, smaller inverted details and inconsistent cold-start/archive evidence. |

Categories 2 (shape specificity/art direction), 4 (material separation/tactile quality), 5 (lighting/depth/exposure) and 6 (colour/detail discipline) are not scored here because their acceptance judgment belongs to the Luna visual review. Pixel defects relevant to technical legibility are recorded above. No weighted overall is claimed from a partial category set.

## Verdict

Art08 passes most explicit P02 dimensional checks, the keyed moving-bank engagement checks, registered support grounding, service endpoint alignment, and open/closed articulation endpoint collision probes. It does **not** pass technical acceptance. The primary-floor topology/winding defect is critical, and the ring seams, articulation ambiguity, incomplete circulation proof and internally inconsistent reproduction evidence keep every applicable score below 90. The honest Sol verdict is **FAIL**.
