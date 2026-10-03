# Compliance dock C7 — independent technical category8 review

**90.0/100 — FAIL.** Category8 must be strictly greater than93. **Critical0; high1; medium2.** No overall visual score is assigned.

The frozen scene is `COMPLIANCE_EDIT_LOCAL` in `module_overhaul_R1.blend`, SHA256 `22176ab474d914156cdf5a083571c19b04c6e6e11cfa50ab8ba681013bc124a6`. The source and identical `full-f13.blend` checkpoint remain byte-exact. Every protected input and native-recorded source/font/license recipe hash matches. All27 beauty,4 neutral and4 UV images were complete and independently hash-verified before final review; I opened all35 individually at original resolution, plus the4 approved spawn references. [Image inspection ledger](full-c07-technical/pixel-inspection.json).

## Defects that prevent category acceptance

1. **High — two transit drums visibly intersect.** Actual evaluated side rays at Z0.15,0.30,0.50,0.70 and0.85m show **147.869mm** shared solid length. Centers are0.328024m apart; top skins share0.0319285m². This is separate blue/yellow drum volume, not a joint or box-based suspicion. It is visible in [HERO_UTILITIES](../renders/full-cycle-07/HERO_UTILITIES.png), near pixel827,498, and [PLAYER_PINCH](../renders/full-cycle-07/PLAYER_PINCH.png), near754,296. [Actual triangles/cross sections](full-c07-technical/drum-actual-interpenetration.json).
2. **Medium — P1 exposed reveal/head skins are coplanar duplicates.** Corridor side skins and south-wall reveals share the same outward planes; a representative east-side triangle overlap is0.480435m². Corridor ceiling and south lintel share the downward surface at Z2.60m; a representative triangle overlap is0.319992m², with charcoal/plaster assignments. First-hit camera rays place these skins directly in [PLAYER_REVERSE](../renders/full-cycle-07/PLAYER_REVERSE.png) and [C10_ROOF_SERVICES](../renders/full-cycle-07/C10_ROOF_SERVICES.png). This differs from opposed hidden contact faces. [Coplanar measurements](full-c07-technical/coplanar-overlap.json) and [named-view witnesses](full-c07-technical/named-view-coplanar-visibility.json).
3. **Medium — scanner crowns do not conform to bridge underside.** Downward rays to the actual crowns and upward rays to the bridge measure3.904–9.180mm hidden penetration at six samples. At X±0.76,Y7m, column top is Z2.668411m and bridge underside Z2.659231m. The seam has engagement, but misses the recommended2mm clean-bearing allowance. Testing only the bridge against a mathematical expected crown point cannot establish the real joint. The mismatch is hidden in [HERO_SCANNER](../renders/full-cycle-07/HERO_SCANNER.png); it is not called a visible floating hero or a critical room failure. [Both actual surfaces](full-c07-technical/actual-bearing-surfaces.json).

## What independently passed

| Measurement | Actual result |
|---|---:|
| Evaluated triangles / cap |385,180 /450,000|
| Authoring material submeshes / cap |1,149 /1,150|
| Local used material families / cap |36 /36|
| Inherited objects retained |1,077|
| Maximum inherited world-matrix delta |1.1921×10⁻⁷m|
| Supported assemblies / actual anchor seats |45 /92|
| Maximum registered anchor gap or penetration |2.3842×10⁻⁷m|
| Evaluated connected islands |2,732|
| Closed / intentionally open islands |1,903 /829|
| Zero-area triangles, inconsistent directed edges, nonmanifold edges, negative closed volumes |0 each|
| Native relative linked dependencies |25, all resolved and hashed|
| Packed inherited file images |119, payloads hashed|

[Fresh existing validator](full-c07-technical/existing-validator.json) passed7 checks with0 errors/0 warnings, using explicit `contracts/interface.json`. Its pass does not erase the finer defects above. Interior clear faces measure X±6.80000019m and Y≈0/15.80000019m. Sampled usable widths are P1 2.39999986m, D1/D2 1.04999930m, human scanner1.21999979m, G1 1.85999960m, and north return1.54999876m. Saved closed doors and declared open poses are distinguished. Floor envelope remains inherited X±7.1m, not claimed to equal the contract's±7.08m wall allowance.

Every evaluated disconnected island received real BVH surface samples rather than bounds-only acceptance.22 initial sparse-contact warnings were refined using all evaluated vertices plus actual triangle intersection; all proved engaged, including glazing/mullions, curtains/clamps, cart hoop and scanner conduits. The40 cargo rib-to-shield seat samples match within0.24µm. Hidden carcass/plinth joints and intersecting seats are separated from same-outward exposed skins. [Island probes](full-c07-technical/island-surface-contacts.json), [refinements](full-c07-technical/refined-contact-candidates.json), [bearing probes](full-c07-technical/actual-bearing-surfaces.json).

Actual shader-output traversal confirms physical UV use for hard surfaces and `CD_Fabric_Cut_1m` for textiles. Every tested physical edge over0.1mm preserves metric length within1%, with no collapsed geometry/UV triangles. Actual textile charts are finite and continuous on the visible broad cloth: tarp top area ratio1.000000054; upholstery total area ratios≈1.0. Local textile distortions remain (tarp0.848–1.085 edge ratios; cushion maxima1.668–1.779; small return/seam charts down to0.445), so the independent physical audit chart is not substituted for the consumed cloth coordinates. No atlas/lightmap claim is made. [Actual consumed UVs](full-c07-technical/consumed-textile-uv.json), [shader and packed-resource hashes](full-c07-technical/resources-normals.json).

Fresh pinned Blender5.2.2 LTS (`d13f752e3b9c`), threads1, repeatedly cold-opened the source with25 relative native dependencies. Local room shaders consume no images; all119 packed images belong to immutable linked map context. The packed local DejaVu font resolves relatively and its retained license hash matches. [Cold dependency results](full-c07-technical/portability.json), [recipe comparison](full-c07-technical/recipe-verification.json).

## Limits and reproducibility

- No full builder or native save was run. Rebuild determinism from factory-empty source is therefore unverified; static current/checkpoint recipe hashes match native-recorded hashes and all recipes are retained.
- This review cold-opened the native source repeatedly with pinned Blender, but did not cold-render all35 views itself or test a separately relocated checkout. The supplied35 images were hash-verified and individually inspected.
- Static validator uses labelled bulky obstacles plus inferred architecture and declared open poses; this is not engine physics, collision ownership, navigation, import, runtime FPS/draw calls, animation, or moving-door sweep proof. P2 open aperture/operation remains explicitly unverified.
- All2732 evaluated connected islands have actual sampled surfaces/intersection evidence; finite nearest-point sampling cannot certify every buried penetration or continuous structural load path.22 sparse-contact candidates were refined with all vertices and BVH triangle intersections and all proved engaged.
- All92 registered anchors were measured against target surfaces and independently recomputed component seats. The40 cargo rib seat samples and6 scanner crown/bridge pairs use both actual surfaces. Internal fixing-sized disconnected parts are included in island probes; individual fastener strength, torque and every full fixing-seat penetration were not exhaustively certified.
- Same-facing coplanar candidate counts are not a defect count. Of2520 positive pair overlaps, many are buried or legitimate corner/seat contacts. Decisive findings use visible perspective-view rays and actual object construction. The recorded orthographic camera rays use an explicitly documented perspective approximation; those results are excluded from decisive findings.
- The local36 material families consume no images. All119 packed file images belong to linked read-only map context. Packed payloads and dependency hashes were verified, but a new full third-party licensing audit of the immutable assembled map was not performed. The local delivered font is packed, resolves relatively, and has a matching retained DejaVu license.
- Physical charts are finite and preserve every tested evaluated edge over0.1mm within1%; actual textile shaders use CD_Fabric_Cut_1m. Their continuous area-normalized/projected charts intentionally have local distortion: tarp edge ratios0.848–1.085, cushion maxima1.668–1.779, tiny seam/return charts down to0.445. Global area normalization is not local isometry or a unique/lightmap atlas claim.
- Native envelope follows the measured preserved source, including floor X bounds±7.1m, versus contract exterior wall allowance±7.08m. Blueprint labels are not presented as newly verified whole envelope dimensions.

The failed literal executable-path attempt and failed first coplanar probe parse are preserved with their original scripts/logs; successful retries are separate. No builder, modeling pipeline, native save, source repair, or protected input edit was run. All my Blender processes have exited and all subprocess sessions and file/image read handles are released. [End source/protection/resource audit](full-c07-technical/input-hashes-end.json).
