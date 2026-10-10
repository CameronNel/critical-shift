# C84 full view06 rod-shaft review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**Candidate SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`  
**View06:** `/workspace/scratch/reactor-refinement-cycle84/parallel-720p/main/green/06/06_control_rods_pool.png`  
**Image SHA-256:** `3714f9da21bffdeb0f2894a0ba09ea6da65b1f45662f6e394429939a83fad73f` (1280×720, 96 samples)  
**Rod-guide fit audit:** `/workspace/scratch/reactor-refinement-cycle84/rod-guide.json` (SHA-256 `f0c5295c590b74cdf378c7eee347331648d84fa4fbf41c0dc2cc072be52d945b`)  
**Motion audit:** `/workspace/scratch/reactor-refinement-cycle84/motion.json` (SHA-256 `6d60d770f513c470a2309dc6eba2c5bd8f4fb42e1540344ce3d38e5914422f5f`)

## Accepted

- **#91 — Rod cluster primary hierarchy.** The paired shaft bundles read as the main vertical mechanical assemblies, with grouped pins and repeated supports visible over a substantial length.
- **#93 — Rod collar construction.** Multiple separate collars are legible along each cluster; they read as physical rings around the shafts, rather than just green illumination.
- **#94 — Mechanical/status-light separation.** The gray metal collars remain visually distinct from the narrow green state accents carried at their inner edge. The view resolves the mechanical rings previously hidden in view05.
- **#102 — Rod metallic roughness.** The shafts show controlled elongated highlights and remain satin metallic. Reflections do not collapse into the earlier mirror-like rod response.

These appearance findings are corroborated by the unchanged C82→C84 scope for the rod geometry and the exact C84 rod-guide audit: both banks pass full-height housing/guide fit over 480 poses, with zero sampled housing/guide intersections. The audits are finite and do not claim exhaustive collision proof.

## Remains open

- **#92 — Drive/absorber distinction.** The pin clusters are apparent, but this view does not clearly distinguish the central drive column from the absorber pins at normal viewing scale. The similar reflective vertical lines blend together around the centers of the bundles. Keep for a closer angle or additional visual evidence.
- **#97–101 and #104** are not closed by this view: corner joints, service access, conduit entries, paired-bank variation, suspension terminations, and lower service text are too small or occluded here.

## Diagnostic follow-up for #92 (not acceptance evidence)

A transient material-only contrast trial on view06 is `/workspace/scratch/c84-rod-contrast-diagnostic/06_control_rods_pool.png`, SHA-256 `25c345a055e1effa0c851fdee395799e2d395e9c5ba7314fba171d8b1b830b78`; it changes the two owned absorber/guide material parameters in memory. A second trial frames the guide entry from `(0, -4.0, 9.05)` toward `(0, 0, 8.95)` at 28 mm: `/workspace/scratch/c84-rod-48-reframed-diagnostic/48_rod_guide_housing_entry.png`, SHA-256 `7be73524e2d6a3b2d5a0f24b2ed1c732742293f9458e1acd30e4608027ef8394`. The upper guide/yoke body begins to separate from the thinner pin bundle, but the crop omits most of the pin length and parts of both housing edges. These are 480×270/16 previews with in-memory material changes. They point to a useful full-quality evidence angle; neither closes #92. A full view must retain the guide-to-pin transition and enough visible slender pins to make the distinction convincing.

No overall score is assigned here.
