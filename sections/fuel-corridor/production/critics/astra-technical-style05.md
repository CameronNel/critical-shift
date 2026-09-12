# Astra technical review — frozen style05

**Verdict: FAIL.** The reported support failures are substantive, and full circulation is intentionally **NOT_RUN** for this slice. The two frozen authoring files match the saved-source hashes in the CPU evidence. Reproducibility provenance and object-specific payload checks still need strengthening before technical acceptance.

Reviewer: `/root/astra_reviewer`, with a separate frozen-source payload check by `/root/astra_reviewer/refinery_source_recheck`. Only this report was written. No scene, source, neighbor or live Blender session was changed; no Blender process or GPU render was run by these reviewers. This is an independent inspection of frozen source and supplied measured evidence, not a new saved-scene evaluation.

## Evidence identity and scope

Authoritative authoring input for this review is `production/checkpoints/style05/build.py` plus its sibling `valorant_details.py`. The builder is editing later mutable source; that later source is not credited to style05.

| File / evidence | SHA256 |
|---|---|
| Frozen style05 `build.py` | `9949de0cdeee2e7aac0f16f7ec22dad3f815e025bf6f7f42c6641275fb2b0bb8` |
| Frozen style05 `valorant_details.py` | `9a384ca54e830aa3c273a57aae355a8a719cf704282fcd7d4cccffe9a658b722` |
| `production/evidence/technical_style05.json` | `416d4ba69134d010fea1de5e392d72273f388d7b975010366183e0441a40fe4e` |
| Validator source inspected during this review | `72162c0070506cc68bfd811b6c256e1882fc597ef69e7956fc50b4ce721d56aa` |

The supplied CPU report records style05/slice, Blender 5.2.0 LTS, background evaluation at 2026-09-10 19:45:41 UTC, no render/save, and matching hashes for **both** authoring files. Its positive results include ten camera/settings checks, 1,101 evaluated geometric objects / 90,090 polygons, no exact duplicate failures, and no external dependency failures. Those positives do not override the reported failures.

The validator was not frozen beside this checkpoint, and its hash is absent from the original report. The inspected validator explains the supplied output, but this review cannot prove byte identity between today's validator and the validator used at that timestamp.

## 1. Two-file authoring works; the frozen replay package is incomplete

Frozen `build.py:502–503` resolves `valorant_details.py` beside **its own file**, compiles it into the shared namespace, then calls the resulting functions. This correctly uses the frozen sibling when replaying the snapshot. The operative trolley is the replacement in `valorant_details.py:53–115`; the older `build.py` trolley definition is overridden and must not be measured as current geometry.

`build.py:538–540` stores both source hashes in the scene, and `validate.py:715–718,741` compares both. This is useful two-file provenance.

**Remaining high-priority provenance gap:** the checkpoint contains only those two Python files. The scene file, `interface.json`, validator, and complete invocation are not frozen with it. `build.py:409,456` reads the external interface, and the validator reads the mutable interface at `:700`. The render manifest at frozen `build.py:568` omits detail-source, interface, validator and saved-blend hashes. The CPU report also omits the saved `.blend` hash. Therefore the current bundle cannot uniquely identify every input or prove that a later file at the same scene path is the audited style05 file.

The snapshot's default `ROOT` also differs from the production layout (`build.py:9`). Direct execution from `production/checkpoints/style05` needs an explicit `FUEL_CORRIDOR_ROOT`; otherwise it resolves under `production/checkpoints`. An override pointed at the active section then reads mutable inputs and writes the active scene. A replay record must define a complete isolated root/input set and the actual stage, width and samples rather than implying the two archived files alone are a standalone rebuild.

**Technical correction/check:** bind each reviewed revision to the two sources, exact interface, validator, Blender version, build invocation, saved scene and render files using hashes. Reopen and rebuild should be distinct evidence. `bpy.app.background` plus a nonempty filepath (`validate.py:748–749`) detects background saved-file context; by itself it does not prove that a newly rebuilt scene reproduces the frozen revision.

## 2. Cask dimensions: core compatible; transport hardware is larger

The replacement cask body and closures match the requested reactor core envelope:

- Body length **1.180 m**, radius at most **.155 m**.
- Closure centers at X±.605 m, each .035 m thick, radius **.170 m**.
- Complete body/closure envelope **1.245 m × Ø.340 m**, from `valorant_details.py:87–96`.

The complete authored cask includes added grips/latches/lifting eyes. Source-derived bounds are **(2.0275,12.098,.590)..(3.2725,12.490,1.007)**, giving **1.245 × .392 × .417 m**. The grip reaches Y−.222 relative to the axis (`:103`) while a closure reaches Y+.170; the lifting eye reaches Z1.007 (`:105`). **Ø.340 is the core/closure diameter, not the complete hardware envelope.** These complete-cask bounds are source-derived, not a separate evaluated measurement in the supplied JSON.

**Coverage gap:** `validate.py:728–740` checks the whole carrier envelope but does not independently assert payload count, core length/diameter, complete-cask dimensions, or saddle spacing. A wrong-sized cartridge could still fit inside the carrier and pass that gate. The carrier gate is also optional: if `Long_cask_carrier` or its evaluated descendants are absent, the check is omitted rather than failed.

**Technical correction/check:** require the expected carrier/payload inventory; independently measure the evaluated core and full hardware groups in their assembly-local frame; compare each with its explicitly named contract. Assert that missing or oversize payloads fail. Avoid treating a world XYZ bounding box as length/width after a carrier is rotated.

## 3. Carrier and saddle support

The supplied measured complete carrier bounds are **(1.85,11.87,0)..(3.45,12.77,1.247)** and dimensions **1.600 × .900001 × 1.247 m**. This passes the reported **1.60 × .90 × 1.30 m** allowance with 2 mm tolerance (`technical_style05.json:2059–2082`). It is smaller than the previously discussed 2.20 m carrier; the frozen source and supplied report agree on the new 1.60 m design. The rubber edge sets plan dimensions and the handle sets height.

Nominal bearing contact is present through the bands. Saddles and bands share world X centers **2.22 / 3.08**, separation **.86 m**. Saddle inner radius and band outer radius both equal **.163 m** (`valorant_details.py:79–98`). Saddle axial thickness is 78 mm versus 64 mm bands, leaving 7 mm saddle overhang at each side. The core body alone is 8 mm inside that radius; the band is the intended contact surface.

The stored support result reports four tyre/floor anchors and **126/126** carrier members connected. This is useful evidence that the old disconnected carrier problem is no longer reported in style05.

**Limit:** equal source radii do not establish exact evaluated bearing fit because saddle and band polygon sampling differ. Their chord insets are below approximately .36 mm / .20 mm respectively. The bands are solid cylinder primitives intersecting the body, and the support graph accepts intersections or sampled surface proximity within 5 mm. An undirected connectivity graph proves neither bearing orientation nor appropriate mechanical support, and does not enforce the 2 mm penetration rule between every pair of internal parts.

**Technical correction/check:** add a targeted evaluated saddle/band seating measurement at both bearing stations, including contact direction, maximum separation, and unintended penetration outside accepted embedded-part interfaces. Keep approved intra-assembly overlaps explicit rather than allowing any overlap to substitute for support.

## 4. Reported support failures require correction

These are the style05 measured findings, not claims about the builder's later corrections:

| Assembly | Recorded finding | Technical implication |
|---|---|---|
| `Bay_steelwork` | A wall flange lies 28 mm in front of the declared concrete target at one bearing anchor. | The declared support plane bypasses intervening architecture. |
| `Cask_task_light` | A panel cross seam lies 3.5 mm ahead of the declared concrete support. | Exceeds the validator's 2 mm intervening-surface tolerance; intended target/contact is unresolved. |
| `Staging_cable_ladder` | Four `Laid_power_cable` members have no support chain; nearest sampled rung separation about **11.038 mm**. | Exceeds the 5 mm contact threshold. The sampled nearest value is not a universal exact minimum. |
| `Staging_vent` | Anchor-to-flange signed gap approximately **−27.999 mm**. | Reported support penetration far exceeds 2 mm. |
| `Freight_gate_drive` | Local plate/cover anchor passes, but dependency does not reach a registered architectural support surface. | Its 18 connected members are not enough to establish a supported whole assembly. |

Frozen `build.py:541–565` chooses support targets by searching near the supplied anchor plane. The independent validator appropriately rejects skipped nearer architecture. Correct the actual support relationship and registration together; changing a label or widening tolerances is not evidence of repair. The gate drive also needs its supporting door/structure relationship covered rather than an isolated local-contact pass.

## 5. Circulation coverage is correctly pending, with one exclusion weakness

`internal_routes` is **NOT_RUN** because the saved stage is a slice (`validate.py:566–569`). No full freight route, bypass turn, stretcher route, door operation, service approach or adjacent passage can be passed from this evidence. The full-stage gate is appropriately included in the overall failure.

The planned full validator samples 2.4×2.2 m freight clearance, 2.0×2.2 m bypass clearance, 3 m freight operating cylinders and a nominal stretcher turn. These remain finite ray/sampling approximations. They do not establish 2.6 m nominal width everywhere, wheel steering, operator reach or runtime collision. A local slice route/access check would be useful before expansion, but must be labelled as local evidence.

**Coverage weakness:** `routes_audit` removes **all `hide_render` objects** as well as the two explicit presentation-cap classes (`:570`). Thus the documentation's “only external cap members are excluded” description is incomplete. A barrier hidden for presentation could disappear from the route audit even if it remains physically relevant. Define/validate collision participation separately or tightly enumerate justified exclusions, and add a negative control in which a hidden internal barrier still fails. Render visibility alone should not determine a physical clearance pass.

The slice's missing external caps are correctly reported as absent with **through passage NOT_CERTIFIED**. The reactor-owned closed doors documented in the interface remain a separate integration blocker.

## Required next technical evidence

1. A new, revision-bound CPU report after the five support findings are corrected; preserve the strict thresholds and inspect dependency paths.
2. Mandatory carrier/payload presence and evaluated core/full-hardware envelope checks, plus explicit saddle seating checks.
3. A frozen replay package with interface, validator and scene identity as well as the two authoring files. Test changed/missing detail source and changed interface as provenance failures.
4. Full-stage route evidence, an exclusion audit, and a hidden-barrier negative control. Keep full assembly/runtime limits explicit.
5. Updated technical documentation: the existing `production/technical_audit.md` still describes slice03 cameras/settings and old carrier defects; it should not serve as current style05 acceptance evidence.

Existing self-test evidence covers several useful contact, fabricated-anchor, duplicate and route-barrier cases. This review ran no additional tests and awards no visual or overall technical score. The next source revision is outside this report's scope.
