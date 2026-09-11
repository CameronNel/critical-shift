# Player-height review coverage

The hall is inspected at1.68m eye height, with the inherited C07 coupling camera at1.5m. This is Blender view and evaluated-clearance evidence, not an engine locomotion test. No navmesh, physics controller or multiplayer simulation is claimed.

The path is D01 → main lane → west controls → west machinery apron/oil service → north crossover/D02 → east service aisle → steam service → south crossover → D01. The bench apron branches from the north end. Both crossovers support the ideal.8×2.2m cart's2.341m rotation disc. Full LP casing halves stay in-room; no large-part cart extraction is claimed.

| Path segment | Evidence cameras | Measured clear design volume |
|---|---|---|
| Entry and return approach | C01, W01, W03 | D01 2.4×2.7m, level threshold |
| Through lane | C01, C03, C04 | x−1.2..1.2, y0..24, headroom≥2.7m |
| Control station | C06, W02 | West bay; no furniture enters main lane |
| Turbine maintenance and oil service | C02, C07, W05 | x1.2..2.5 protected apron |
| North crossover and exit | C03, C04, W04 | y20.4..23,2.6m crossover; D02 2.4×2.7m |
| Bench approach | C08, C10, W04 |1.42m bench-to-lane apron |
| East maintenance loop | C05, C09, W06 | x7.1..9.3,2.2m aisle |
| South crossover | W03 | y1.1..4.9,3.8m depth |

The saved validator clips evaluated triangles against every protected route volume and checks full door apertures. This catches curved-pipe overshoot that a centreline-only plan missed in R01. Its contact-island graph checks each evaluated visible object for a chain to shell structure; it is not a strength calculation. Ten fixed cameras remain unchanged, while supplemental views can be corrected when their framing fails to show an approach.

Known review correction: R04 W01 was too close to show the whole entry sign/door assembly. It is rejected as complete approach evidence and moved back along the same clear route in the subsequent build. The ten acceptance cameras are not moved to hide defects.
