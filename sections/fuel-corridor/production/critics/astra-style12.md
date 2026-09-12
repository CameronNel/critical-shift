# Astra independent visual review — style12 slice

Date: 2026-09-10. Decision: **FAIL — retain the style gate.** Four visual categories remain below 90. This is a review of rendered pixels, not a full-stage or technical approval.

## Evidence and authority

Viewed the actual style12 `C03_HERO`, `C09_MATERIALS`, `D01_CARRIER_OPERATION`, `D02_WORKBENCH`, and `D03_UTILITY` PNGs. Compared them directly with `art/reference/current/reactor-a05.png`, `mine-heading.png`, `mine-entry.png`, `mine-sump.png`, `art/concepts/C06-style05-paintover-r01.png`, and `C01-freight-r04.png`. These current references govern this review; the older teal references in the legacy rubric do not.

The manifest identifies revision style12, stage slice, blend SHA-256 `58511635e4394538d6c1f8c25ddd2454574431ecbde5a1686757809f40ee339a`. Following the pixel review, I reopened the hash-matching frozen style12 checkpoint in a fresh CPU-only Blender process solely to identify the floor fragments described below. This was not a general technical audit. I make no pixel-identical comparison or regression claim against style11. Missing full-stage geometry is outside this slice judgment, not a reason to excuse the visible finish.

## Scores

| Category | Score / 100 | Visible basis |
|---|---:|---|
| Scale / circulation | **91, local slice only** | C03 reads as a usable industrial junction. The cart is inside a marked staging bay, with visibly open floor at the service and freight approaches. Door, bench and cart proportions are coherent. These pixels do not establish continuous route widths or remote turns. |
| Shape / art direction | **86** | The panel-and-steel architectural language fits the approved direction, but the close-up tools, gloves, toolbox and regulator retain a conspicuously simplified asset finish. They do not achieve the references' degree of authored mechanical detail and surface definition. |
| Hierarchy | **90** | Service opening, freight opening, orange travel cue and staged carrier are easy to distinguish in C03. Bench and air station read as secondary functions. The service sign is relatively low contrast, and the wide blank wall fields weaken the focal emphasis, but local wayfinding is clear. |
| Materials | **85** | Painted white payload, orange restraints, dark rubber and silver fittings are distinguishable. However, many bench and utility surfaces converge on a soft satin grey response. The cask's repeated linear scuffs, very clean equipment surfaces, and weak cloth/glove character remain conspicuous in the detail views. |
| Lighting | **87** | Exposure is readable and practical lights have a plausible presence. C03 is broadly filled and comparatively flat: wall fields receive similar brightness while upper dark steel loses detail. The approved concepts produce more concentrated warm pools, clearer steel-edge response and stronger separation between working areas and secondary structure. |
| Color | **92** | Restrained off-white, gunmetal and orange consistently match the current corridor concepts and reactor palette. Color supports routing and controls without overwhelming the neutral architecture. |
| Environmental storytelling | **87** | Staging marks, cart restraints/brakes, gauge, hose, clipboard and maintenance props establish the intended work. The bench arrangement, pristine can/flask/toolbox and identical-looking tool presentation still feel freshly staged; the references communicate more handling and use through the props themselves. |
| Technical correctness | **Not scored** | A targeted CPU ray/projection inspection identifies the floor fragments below. It does not cover the validator, assembly support, route constraints or general technical correctness, so it cannot support a category score. |

## Top observed defects

1. **Major — workbench props fall below the established art finish (D02).** The spanners have very similar straight shafts and blunt, simplified end profiles. The two gloves read as tidy padded extrusions with little fabric behavior; the pale cloth reads almost like a smooth sheet. The toolbox, flask and grease tin remain generic, uniformly clean volumes. This is particularly noticeable because the close camera gives these objects substantial screen space. The paintover's tools, cloth/packaging and used work items maintain more individual character.

2. **Major — surface response is too uniform across equipment (D02, D03, also C09/D01).** The bench objects, shelf/table surfaces and utility hardware share broad soft highlights. D03's filter bowl has little legible glass depth, and the regulator/pipe assembly looks unusually pristine. The reference metal has more precise highlight structure and clearer differences between coating, exposed steel, rubber and other surfaces. This is a material-read judgment, not an assertion that any particular shader is absent.

3. **Moderate — cask wear reads as applied repeated graphics (C09, D01).** Several long grey marks have closely related tapered horizontal silhouettes and isolated placement. They are more readily perceived as a recurring scratch motif than as varied contact history. The cart and payload construction are understandable, but their finish does not yet carry the specificity seen in the approved handling concept.

4. **Moderate — lighting reduces the intended depth and focus (C03).** The service sign and adjacent pale wall share a broad bright field; large wall panels dominate the midtones, while several ceiling beams become nearly featureless dark bands. C06/C01 retain stronger local practical-light emphasis and more tactile dark steel. D03 similarly loses small hardware definition against the backplate.

5. **Moderate — floor decals read as pale angular fragments (D01).** Two isolated tan polygon-like slivers are visible in the lower foreground below/right of the carrier. At least one reads as a separate upright fragment rather than a continuous floor marking or floor texture. A subsequent CPU inspection confirms that these are horizontal `Parked_wheel_rub` decal prisms, not tilted pieces of floor geometry. Their hard silhouette and contrasting surface still create the misleading fragment read in the submitted pixels. The verified diagnosis is a visual integration issue; it is not a claim of physically upright geometry.

The dominant palette, comprehensible staging function and readable local circulation are already credible. They do not compensate for the unresolved close-up finish. Expansion cannot be justified by this review: shape/art direction, materials, lighting and storytelling still miss the required 90 in the actual submitted pixels.

## Targeted floor-fragment diagnosis

Evidence: `astra-style12-floor-probe.json`; replay script: `astra-style12-floor-probe.py`, both beside this report. Fresh Blender 5.2.0 LTS, CPU only, no rendering, no save. The checkpoint SHA-256 matched the manifest before and after inspection. Pixel coordinates below use the 1440 × 960 D01 image, origin at the upper-left; they identify observed evidence, not a modeling prescription.

| Visible patch | Confirmed object | Projected bounds in pixels | Sample ray |
|---|---|---|---|
| Right foreground sliver | `Parked_wheel_rub.002` | x 1084.9–1123.1, y 846.0–936.3 | (1098, 889) hits its top face at world Z ≈ 0.0014 m, normal (0, 0, 1). |
| Lower foreground sliver | `Parked_wheel_rub.001` | x 832.5–902.0, y 912.0–1019.2; clipped at image bottom | (870, 945) hits its top face at world Z ≈ 0.0014 m, normal (0, 0, 1). |

Both are parented to `Bay_floor_finish`, render-visible, and span world Z 0.0007–0.0014 m. Rays just outside the right patch hit `Floor_west_turn` at Z ≈ 0. These results reject the initial possible interpretation of substantially raised or rotated fragments. Their intended sub-2 mm height is confirmed. The remaining complaint concerns how the decals read in the actual render.

## Image identity

| Image | SHA-256 |
|---|---|
| C03_HERO.png | `404d25b1bb906d208d95652041db4419a0f7abf3b35788dca8095dae94908f54` |
| C09_MATERIALS.png | `02d6aa162491fcf9707fab58e1d4c8cf87830346f696f127ce3b77d1618719cc` |
| D01_CARRIER_OPERATION.png | `f5aa38d775136f022c14b25a1a796ab96c34a4d82f7fe592a33554abc4631f6c` |
| D02_WORKBENCH.png | `7863a0caf67c702a117283b11651f47b2132fef7f3e74c84062cf865e75903cb` |
| D03_UTILITY.png | `4e7101006a790dbee46deb04f6141dea14664415be1779432aa88d4a3e401cd0` |

No modeling, source edits, neighbor edits or renders were performed. A bounded read-only second look at D02/D03 corroborated the material separation and staged-prop concerns; the scores and gate decision above are Astra's independent judgment.
