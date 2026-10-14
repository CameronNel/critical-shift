# Cafeteria review rubric

Authority: `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`, grounded stylized semi-realism from `design/ART_DIRECTION.md`, and the original front-end design. A completion claim requires at least 90/100 overall, every category at least 85%, zero critical failures, all fixed cameras and numerical checks passing, four or more full review cycles, two final cycles without material regression, and fresh-process build/open/render evidence.

| Category | Available | Minimum |
|---|---:|---:|
| Layout and route readability | 20 | 17 |
| Art direction and silhouettes | 20 | 17 |
| Hero objects and focal clarity | 15 | 12.75 |
| Materials and anti-plastic quality | 15 | 12.75 |
| Lighting and atmosphere | 10 | 8.5 |
| Dressing and worldbuilding | 10 | 8.5 |
| Technical cleanliness and reproducibility | 10 | 8.5 |

## Recorded diagnostic reviews

The first three reviews scored visible pixels only; the technical category was unscored. These are diagnostic scores, not overall acceptance scores.

| Cycle | Visual / 90 | Main findings |
|---|---:|---|
| R1 | 64 | Critical voids beyond door leaves, weak games lighting, repeated graphics, primitive furniture and uniform table dressing |
| R2 | 72 | Door presentation fixed, curved dining chairs and calmer walls improved; armchairs, kiosk, sharp light transitions and plants remained weak |
| R3 | 78 | Club chairs, kiosk, games and dining stories improved; horizontal ficus blades regressed, coffee camera occluded the authored machine |

R3 category scores: layout 18/20, art 17/20, heroes 14/15, materials 13/15, lighting 8/10, storytelling 8/10. No critical failure, but the score and stability gates were not met.

Fresh-context R4 review: [review_r4.md](critics/review_r4.md). **90.55/100**, with all 13 cameras visually passing and no critical visible defect. Layout 19/20, art 18.2/20, heroes 13.8/15, materials 13.35/15, lighting 9.1/10, storytelling 8.9/10, technical 8.2/10. Formal completion failed because technical cleanliness was below 85%: inherited prop support coverage was incomplete, and the bull surfaces overlapped. Cold render comparison was still pending at that review.

R5 independent review: [review_r5.md](critics/review_r5.md), **91.55/100**. All 13 cameras passed. Technical score 9.2/10 reflected complete classified support coverage, a verified missing-registration failure gate and consolidated palette shaders, while retaining a minor bull-cap defect. The second final cycle was pending at that snapshot.

R6 final independent review: [review_r6.md](critics/review_r6.md), **91.90/100 — authored Blender review PASS**.

| Category | Earned / available | Percent |
|---|---:|---:|
| Layout | 19 / 20 | 95 |
| Art direction | 18.2 / 20 | 91 |
| Hero objects | 13.95 / 15 | 93 |
| Materials | 13.35 / 15 | 89 |
| Lighting | 9.1 / 10 | 91 |
| Storytelling | 8.9 / 10 | 89 |
| Technical | 9.4 / 10 | 94 |

All 13 cameras pass, zero critical current defects, complete classified support coverage and its negative rejection gate pass, and R5/R6 show no material regression. The corrected bull annulus and separate red plug are independently verified. All three asset studio renders and thirteen room views reproduce from fresh Blender processes with packed dependencies. This passes the stated authored-Blender bar; owner approval, combined-map integration and runtime acceptance are separate.
