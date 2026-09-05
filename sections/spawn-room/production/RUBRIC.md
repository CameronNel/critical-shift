# Spawn Room — 100-Point Rubric

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Completion requires overall >= 90/100, every category >= 85% of available points, zero critical failures, stable final two cycles, and cold-start PASS.

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
