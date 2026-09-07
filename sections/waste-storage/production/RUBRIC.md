# Waste Storage review rubric

Independent reviewer: `/root/astra_reviewer`, model `gpt-6-astra`, reasoning `ultra`.

Each category is independently scored out of 100. The user requires every relevant category ≥90; an average never overrides a failing category. Technical assertions require measured evidence separately from visible pixels.

| Category | Weight | Evidence / acceptance |
|---|---:|---|
| Scale and circulation | 20 | adult scale, usable cart/carry route, valid doors, objective clearance checks |
| Shape and art direction | 20 | specific authored construction, approved reference fidelity, no blockout or toy forms |
| Hierarchy | 15 | entry read, segregation and machinery focal order, working negative space |
| Materials | 15 | tactile distinct concrete, paint, bare steel, rubber, glass and fabric; no universal gloss |
| Lighting | 10 | practical source logic, depth, readable shadow regions, stable exposure |
| Color | 5 | restrained coherent fields, functional accents, color-independent cues |
| Environmental storytelling | 10 | maintained working facility, selective wear, functional human traces |
| Technical correctness | 5 | original reproducible source, support contact, clean dependencies, cold-start proof |

Overall = weighted mean of the eight independent scores. Review files are the score authority. No score is inferred from successful script execution or builder intent.

| Revision | Scale | Shape | Hierarchy | Materials | Light | Color | Story | Visible technical | Weighted | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| slice-r01 | 76 | 67 | 74 | 54 | 61 | 80 | 55 | 72 | 67.0 | FAIL; full technical/circulation unverified |
| slice-r02 | 79 | 71 | 67 | 64 | 72 | 84 | 61 | 62 | 70.25 | FAIL; monitoring and ID regressions |
| slice-r03 | 80 | 73 | 80 | 69 | 73 | 85 | 70 | 80 | 75.5 | FAIL; schematic instruments, surface/light deficits |

Paused by user with partial r04 source unbuilt/unrendered. No new scores or acceptance apply to that source. See section CONTINUE.md.

Completed full-room review cycles: 0. A slice does not count as a full-room cycle.

At least four full ten-camera review cycles follow the first complete environment. Final two full cycles must be materially stable, all cameras pass and cold reopening/rendering must match. Any automatic visual veto from ART_DIRECTION blocks acceptance.
