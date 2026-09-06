# Spawn Room — 100-Point Rubric

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Completion requires overall >= 90/100, every category >= 85% of available points, zero critical failures, stable final two cycles, and cold-start PASS.

## Maintained-wear revision assessment — 2026-09-06

**Builder self-review: PASS, 92/100.** This is not user approval. All eleven fixed views and two details were inspected, including the full fresh-open comparison. Materials improve to 14/15: tactile plaster/concrete, restrained paint loss, softer fabric/rubber and localized real surface depth. Other category judgments remain stable against the same cameras; no visual veto or material regression was identified.

| Category | Score | Current evidence |
|---|---:|---|
| Layout / route readability | 18/20 | Unchanged fixed routes and measured clearances; Spawn, ExitReverse, Walk_A/B/C |
| Art direction / silhouettes | 18/20 | Maintained institutional construction with restrained surface irregularity; all fixed views |
| Hero objects / focal clarity | 14/15 | LockerDoor, LockerReverse and Hero_A; readouts remain readable |
| Materials / anti-plastic | 14/15 | Material_A, HallForward, both DETAIL views; concrete, plaster, fabric, rubber, paint, laminate and glass separate |
| Lighting / atmosphere | 9/10 | Local practical falloff and contact remain stable through full cold comparison |
| Dressing / worldbuilding | 9/10 | Targeted damage/use, portraits and functional work clusters; DETAIL views |
| Technical cleanliness / reproducibility | 10/10 | 83 contacts, 29 objective checks, packed-byte verification, SOLID startup and documented source recovery |

Correction and rejection evidence: critics/worn-surface-review.md. Exact differences and delivered-file provenance: worn_cold_start_comparison.json, worn_recovery_comparison.json and renders/final/render_provenance.json. No score is based merely on object count or successful rendering.

## Original pre-wear rebuild assessment — 2026-09-06

**Historical pre-wear score: 91.5/100.** Current wear-revision findings are in `critics/worn-surface-review.md`; this earlier score is not a new user approval. Reviewer: builder self-review, not independent critic or user acceptance. Slice checkpoint: **8.5/10**, no veto identified, reviewed before expansion. Final visual average: **8.7/10**; art/layout subtotal **81.5/90**, technical **10/10**. All category floors are met. No critical failure or visual veto was identified in builder review.

| Category | Final score | Reference / evidence |
|---|---:|---|
| Layout / route readability | 18/20 | 00–03, 17, 23–24; left/right/forward navigation, four bays, four chairs, measured circulation |
| Art direction / silhouettes | 18/20 | 04–09, 13, 20–21; folded sheet, sewn cloth, tubular furniture, continuous door apertures |
| Hero objects / focal clarity | 14/15 | 03–07, 22; central test machine, editable mechanism and distinct PPE stations |
| Materials / anti-plastic | 13.5/15 | 10, 20; cloth nap, curved visor, matte rubber, paint, laminate grain, enamel and clear glass |
| Lighting / atmosphere | 9/10 | 11, 16; physical practical fixtures, quieter centre, cooler operations, grounded feet |
| Dressing / worldbuilding | 9/10 | 12, 14–15, 18–19; two portraits, one notice cluster, cards/cartridges/clipboard/mug and contact wear |
| Technical cleanliness / reproducibility | 10/10 | 59 contact checks, 29 objective checks; fresh rebuild PASS; all eleven cold-start PNGs pixel-identical |

Full visual breakdown: scale 9; shape specificity 8.5; material separation 8.5; lighting/grounding 8.5; colour 9; human storytelling 8.5; density 9; signage 9; PPE 8.5; commercial game read 8.5. The room is intentionally restrained and clinical. The scores do not claim photoreal detail, a finished runtime integration, or perfection.

Failed passes and exact fixes are retained in `critics/full-room-review.md` and the numbered render folders. The final two cycles are materially stable; see stability_comparison.json and cold_start_comparison.json. The original slice category mean is 8.45/10, reported as 8.5 at one decimal. The final room category mean is 8.7/10 (correcting an earlier arithmetic transcription of 8.75).

| Category | Points | Pass floor |
|---|---:|---:|
| Layout / route readability | 20 | 17 |
| Art direction / silhouettes | 20 | 17 |
| Hero objects / focal clarity | 15 | 13 |
| Materials / anti-plastic | 15 | 13 |
| Lighting / atmosphere | 10 | 9 |
| Dressing / worldbuilding | 10 | 9 |
| Technical cleanliness / reproducibility | 10 | 9 |
| **Total** | **100** | **90 overall** |

## Critical failures
Any one of these blocks completion regardless of score:
- spawn view does not clearly communicate briefing-left, locker-right, exit-forward;
- locker-room view does not clearly show two suits left, two suits right and integrity chamber center;
- a primary route is obstructed;
- room reads as final greybox/default primitives;
- dominant plastic/default-PBR appearance;
- room no longer matches the global stylized art direction;
- cold-start build/render fails;
- missing required source/dependencies;
- final two review cycles contain unresolved material regression;
- any required support-dependent prop is unregistered, floating beyond tolerance, excessively embedded, attached to the wrong target, or fails support orientation/contact validation.


## Visual rubric — grounded stylized semi-realism

Score each category 0–10:

| Category | Pass evidence |
|---|---|
| Believable scale | architecture, furniture, PPE and devices feel built for adult humans |
| Shape specificity | assets remain identifiable in flat grey; no universal bevel-box language |
| Material separation | painted metal, plastic, rubber, fabric, concrete, floor and glass respond differently |
| Lighting & grounding | practical lights create falloff; contact shadows anchor props |
| Colour hierarchy | restrained structure with purposeful hazard/interaction accents |
| Human storytelling | sparse used objects imply workers without random clutter |
| Detail density | focal clusters are separated by quiet negative space |
| Signage restraint | text supports function rather than replacing environment design |
| PPE quality | suit reads as believable protective clothing with simplified folds/construction |
| Commercial game read | screenshot plausibly belongs to a released stylized PC game |

### Automatic vetoes
- repeated bevelled cuboids dominate;
- uniform glossy/satin plastic;
- generic sci-fi panels/screens;
- flat even lighting;
- toy-like hazmat mannequins;
- excessive signs;
- random decorative plant/filler props;
- floating/supportless props;
- photoreal AAA texture noise;
- obvious Three.js/web-demo read.

**Style-validation slice pass:** average 8/10+ and no veto.
**Full-room pass:** average 8.5/10+ and no veto, with no regression from approved slice.


## Reference adherence modifier

If the builder cannot point to the relevant numbered reference plate when defending a major Spawn decision, that category cannot score above **7/10**.

Examples:
- suit proportions → plate 05 / 21
- chamber form → plate 06 / 22
- hallway density → plate 01 / 13
- materials → plate 10
- lighting → plate 11
- signage → plate 12
- first-person scale → plate 24

This prevents “I interpreted the style differently” from becoming an escape hatch.
