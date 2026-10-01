# Independent style-validation slice review — skill-slice-8c

**Decision: FAIL — do not expand this visual language yet.**

This is a fresh pixel-based review of the changed OCRU and clinical supply bench only. The untouched room shell, restart console, cartridge storage, decon station and surrounding baseline are excluded from the verdict. No prior reviews/scores or author implementation code were read. No source scene or implementation files were edited.

The slice has a clear red focal zone, useful negative space and several recognizable bench props. It does not yet demonstrate sufficiently authored primary/secondary construction on the OCRU hero. Under the final lighting, the bed deck, upholstery and mechanism also lose the material separation required by the approved spawn target. The bench is substantially closer and should be retained for focused correction rather than rebuilt wholesale.

## Authority and inspected evidence

Read the shared `.agents/skills/blender-headless/SKILL.md`, its `references/visual-review.md`, `design/ART_DIRECTION.md`, `design/ART_REFERENCE_INDEX.md` and the style-slice gate in `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`. Applied the owner's supplied target: retain room layout/boundaries; match the approved spawn palette/fidelity/detail with a bleak neglected clinic mood, angular grounded construction, one red bed practical and dim warm bench illumination.

Opened actual pixels in:

- `renders/skill-slice-8c/ENTRY.png`
- `renders/skill-slice-8c/HERO_OCRU.png`
- `renders/skill-slice-8c/DETAIL_OCRU.png`
- `renders/skill-slice-8c/DETAIL_SUPPLIES.png`
- `../spawn-reference/VALIDATE_Spawn.png`
- `../spawn-reference/VALIDATE_Material_A.png`
- `renders/skill-diagnostic-8-clay/HERO_OCRU.png`
- `renders/skill-diagnostic-8-uv/DETAIL_OCRU.png`
- `renders/skill-diagnostic-8-uv/DETAIL_SUPPLIES.png`
- `renders/skill-diagnostic-8-neutral/HERO_OCRU.png`
- `renders/skill-diagnostic-8-neutral/DETAIL_SUPPLIES.png`

Diagnostic clay/UV/neutral images were used to identify form and response issues, not substituted for final-art acceptance. Geometry counts, object names and hidden implementation intent received no credit. Technical clearance, support contact, UV completeness and cold-start behavior were not independently tested by this visual review.

## Visible defects and corrections

| View / region | Visible defect | Recommended correction | Evidence / status |
| --- | --- | --- | --- |
| `HERO_OCRU.png`, back bank behind bed; clay/neutral equivalents | The central bank is dominated by three tall framed flat slabs, two tall narrow side boxes and small shallow grille boxes. Secondary shape mostly repeats panel frames and clipped corners. The assembly reads as a panel arrangement before it reads as specialized clinical machinery. The darkness in the beauty view makes its existing recesses even less useful. | Keep the envelope and footprint. Give the central assembly one deliberate depth hierarchy: a main manufactured housing, a recessed service face, an actual access-door reveal and a small number of mechanically justified attachments. Let side service units have a clear shell/recess/closure relationship instead of matching the central slab language. Use folded-sheet returns and selective cast/molded transitions; do not add more decorative vents, labels or bolts as the remedy. | **Blocking form issue.** Most evident in the clay and neutral diagnostic; still the dominant silhouette in final HERO. |
| `HERO_OCRU.png`, two supports below bed; `DETAIL_OCRU.png`, lower right; clay/UV equivalents | Supports read as stacks of nearly identical rectangular plates on rectangular feet. Their load path and lifting action are not visually clear. The front cylinder/rail and thin parallel members do not resolve the supports into an authoritative carriage. In beauty they collapse into dark block stacks. | Preserve both support positions and the bed height. Resolve each into a believable guided lift or telescoping support: one clear load-bearing spine/sleeve, a readable connection to the bed frame, and either continuous rubber bellows or a few functionally separated metal stages. Shape the feet as a manufactured base with a clear bearing/anchor relationship. Keep hoses/cables secondary to the load-bearing structure. | **Blocking secondary-construction issue.** Clay shows it independently of textures. |
| `DETAIL_OCRU.png`, main pad and pillow | The central pad remains a very broad, nearly uniform rounded rectangle. Stitch marks and edge piping add detail, but do not give much compression or material thickness variation. The pillow has more useful broad deformation, yet the final red illumination makes both read close to the hard deck. | Retain broad clean planes. Add a restrained compression break at an edge or shoulder/hip region, a clearer soft return into the seam, and local thickness variation. Make the upholstery edge treatment visibly different from the folded metal deck. Avoid small noisy folds or full-surface grunge. | **Form/material correction required.** The UV diagnostic confirms a shaped pillow; that does not repair the pad's broad slab read. |
| `HERO_OCRU.png` and `DETAIL_OCRU.png`, red-lit deck, rails and lower mechanism | The red practical provides a strong focal point, but red saturation/value grouping merges the deck, mattress and rail highlights. The support-to-bed relationship and darker back housings are largely unavailable in the final art. The bright red underside strip becomes another graphic emphasis while the structure remains hidden. | Retain the single red focal practical. Reduce its saturation/strength or tune its direction/size so broad bed materials retain distinguishable values. Use a very restrained directional/indirect reveal of the mechanism rather than a second conspicuous glowing band. Check pad matte response, painted-metal semi-matte response and rubber darkness under the final red light. Do not expose the hidden bag/note while repairing the mechanism readability. | **Blocking final-lighting/material-read issue.** Neutral diagnostics reveal some separation that the production views fail to retain. |
| `DETAIL_SUPPLIES.png`, upper-left stack of pale pads and lower-left wrapped packages | The stacked pads have thick, regular board-like layers and very similar edge profiles. The packages also rely on broad rectangular forms. Their purpose is plausible, but the cluster's soft/paper character depends too much on color. | Make pad edges compress slightly and vary the broad stack contour; thin or stagger the layer edges so they read as soft folded supplies. Give packaging a few large paper creases/folded corners and plausible tape tension, maintaining the current quiet composition. | **Focused bench correction.** Do not replace the recognizable bottle/glove/instrument work. |
| `DETAIL_SUPPLIES.png`, upright tape roll and medicine bottles | Tape roll outer wall and bottle shoulders show obvious repeated facet bands at this close camera. Tape layers are recognizable, and bottle caps/pump/labels are useful specific cues, but the hard polygon bands pull these simple objects toward generic low-poly. | Smooth the broad cylindrical silhouette just enough at the required view; retain the cap ribs and tape-layer detail. Make tape more matte/paper-like and distinguish its wall from the smoother molded bottle. Avoid increasing detail density everywhere. | **Secondary finish issue.** The geometry problem also appears in neutral/UV diagnostics. |

## What works and should survive repair

- The supply bottles have shoulder/cap/pump construction, the gloves have cuff and finger form, and the instrument reads as a specific clinical object. These give the bench more identity than a pile of generic cubes.
- The warm work surface contrasts with the restrained blue/charcoal material family. It is not dominated by uniform glossy plastic.
- The OCRU threshold has substantial framing and a distinct bed silhouette. The horizontal bed and clear surrounding negative space preserve the functional focal composition.
- A single red practical is the clear primary light cue in the final OCRU views. The mood is suitably oppressive; adding bright accent lights would weaken it.
- The bag remains closed and visually subordinate in the final hero view. No body content is exposed. The separate barely-visible note cannot be reliably assessed from these four final views; it is not a reason for this FAIL.

## Reference comparison and repair priority

The approved spawn images establish quiet institutional color blocks and modest lighting, but also visible manufactured edge returns, recessed doors, supporting frames and tactile separation at ordinary camera distance. Matching its blue/off-white/orange palette is only part of the target. Here, the clinical bench approaches that restraint; the OCRU still uses repetition of framed slabs and stacked blocks for much of its construction, and the final red lighting conceals the missing hierarchy rather than resolving it.

Repair in this order:

1. Resolve OCRU load-bearing supports and carriage connections in clay.
2. Establish a stronger depth/construction hierarchy on the rear machine bank without changing room boundaries or adding greebles.
3. Recover upholstery/painted metal/rubber distinction under the final red practical, then refine pad/package softness and roll silhouettes.

Rerender the same four 600p fixed views and the same clay/neutral diagnostics. Expansion can pass when the hero remains convincing with labels and color removed, the final red view still exposes its key construction/material hierarchy, and the bench's soft and paper supplies no longer read as rigid layered boards. This report does not certify full-room completion, numerical geometry checks or runtime readiness.
