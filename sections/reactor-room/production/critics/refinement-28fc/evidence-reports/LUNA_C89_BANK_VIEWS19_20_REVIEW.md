# C89 full views 05, 19, and 20: bank service and suspension

**Candidate blend SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`

| View | Image SHA-256 | Manifest SHA-256 | Relevant coverage |
|---|---|---|---|
| Main 05, `05_control_rods_upper.png` | `46e17bd10ddd4e86e5f2f6233019b8ef845663bb205f435ea3fdc15db7d01349` | `98c81e641631091d2674014bb257d3a02c981a9124e56cabd1e2b3b99e4b87ad` | Both bank fronts and service-panel layout |
| Inspection 19, `19_bank_service_face.png` | `4c41e8ecce7bb39b4c00514b5cbc4d9bd250a5660c1ad02de340b29f69c4d45f` | `be6b0350f0ad6145baca82e5daa6730851feb2c35524dd60ff28c78479ec82e4` | Bank A louvred service panel, handle, and adjacent side conduit |
| Inspection 20, `20_bank_suspension.png` | `2d195a8c88d06bba962d93f18f15b2f54e5043421ab133cad086e851c047fe49` | `75730dff5bc2c61f2b88b241f40fc0cea57ca204d57d39874be8808bac66b90c` | Both fixed-housing support paths and upper terminations |

All three are exact-C89 full-quality originals: 1280×720, Cycles, 96 maximum / 32 minimum samples, 16-bit, no preview.

## #98: bank service access — accepted, limited to visible access layout

Main 05 shows both A and B service fronts with separate labeled access panels and louvres. Inspection 19 resolves the A-side panel, louvre depth, and side handle at close range; the paired B panel is visible in the wider full-quality view. The faces and handles are unobstructed, with clear approach space in front. The matching bank geometry and naming are corroborated by the current source and the separate paired-bank report.

This accepts the visible paired service-panel/access provision. It does not claim a human-clearance measurement, internal serviceability, or completion of frame-corner, conduit-entry, or suspension criteria.

## #101: bank suspension connection — accepted, limited to fixed support interfaces

Inspection 20 shows the bank support rods, lower ferrules at the housing tops, and upper yoke/plate terminations. The exact-C89 support audit records four lower-hanger seats per bank against the corresponding fixed housing and four upper-yoke seats per bank against `RH pool girder YELLOW`. All 16 A/B lower and upper registered support records pass; the audit reports zero support failures. The attachment targets and anchor coordinates are in `/workspace/scratch/reactor-refinement-cycle89/audit.json` (SHA-256 `a0fbaac8de6b62d7d6d49f582e05d4f63c78dbe5b83289315fef2d0ee3740537`).

This accepts the visible fixed suspension load path and those sampled seating interfaces. It is not an exhaustive collision test or a dynamic load claim. The separate motion report is not used to claim suspension animation behavior.

## Still open

- **#97, bank frame corner construction:** views 05 and 20 show the paired assemblies and support structure, but the relevant frame-member corner intersections remain too small or occluded to verify as joined construction. View 19 is a service-face view and does not resolve those corners.
- **#99, housing conduit entry:** views 05, 19, and 20 show service routing and one close A-side route, but the actual entry endpoint into both housings is not sufficiently clear in the pixels to accept the complete paired criterion. The separate wall-bore report records eight clear service cores, including bank A and B, but that geometric evidence alone does not prove the visible housing connection.

These remaining rows are evidence gaps, not newly identified source defects.
