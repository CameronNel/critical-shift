# Cycle 14 technical preflight — unscored

Source SHA-256: `7b18f78e64c96b68dc992710947f780662615ce3ccf7d2d11df167809f19f867`. Source: `module_overhaul_R2.blend`, editable scene `REANIMATION_EDIT_LOCAL`. No native save or author edit performed.

**Blocked by confirmed support omissions. No formal /10 score.** The primary author aborted the current batch, and the manifest has complete=True, 23/24 PNGs. No pixel review, visual /90 score or acceptance claim is made.

The independently replayed cold checker reports PASS (102 registered objects, 111 anchors, 151 assembly-part contracts, 10 sewn checks, 26 component checks, 156 normals checks). All 25 linked libraries resolve and all 124 file images are packed. However, its support graph stops at inherited names. Those names are not valid architectural roots merely because they occur in the baseline.

The independent conservative scan covers 2,953 visible geometry nodes (evaluated mesh islands and curve/font bounds). It finds 26 components with no contact within 5.0001 mm to any outside geometry. Disconnection is a rigorous separation proof; connection through overlapping boxes is not a contact pass. Exact directed BVH rays below start on the actual component surface and measure the listed support path. The full JSON records points, directions, normals and all members.

## Entire strict 26-cluster batch

Positions below are world metres. The whole-cluster AABB figure is a lower bound to **every** outside island. A directed-ray gap is the actual gap along that one listed source-surface-to-target path. The chosen nearest outside target is evidence, not automatic approval of its mechanical role.

### 1. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw.007`.

1 islands; whole-cluster gap lower bound **94.65349 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw.007` → `Reserve folded cap.001` | 96.24555 | (-1.900000, 8.372000, 1.292000) → (-1.900000, 8.456172, 1.338672) |

### 2. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw.006`.

1 islands; whole-cluster gap lower bound **68.00079 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw.006` → `Battery plinth` | 68.00120 | (-1.891515, 8.372000, 0.131515) → (-1.891514, 8.440001, 0.131515) |

### 3. confirmed support-dependent compound or hardware separation

All members: `Coupling parking clip`, `Engraved 01`, `Engraved SUIT`, `Engraved backing 01`, `Engraved backing SUIT`, `Interface label mounting stem`, `Parked suit coupling`, `Suit collar lock lug`, `Suit collar lock lug.001`, `Suit collar lock lug.002`, `Suit collar lock lug.003`, `Suit collar lock lug.004`, `Suit collar lock lug.005`, `Suit collar lock lug.006`, `Suit collar lock lug.007`, `Suit coupling lock`, `Suit port socket`, `Suit service enclosure`, `Suit service hose`.

19 islands; whole-cluster gap lower bound **49.00026 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Suit service enclosure` → `Seal guide.001` | 49.00019 | (-1.531750, 6.400000, 1.032000) → (-1.531750, 6.449000, 1.032000) |
| `Suit service enclosure` → `Access jamb graphite return.001` | 63.69965 | (-1.531750, 6.400000, 1.032000) → (-1.531750, 6.463700, 1.032000) |
| `Suit service enclosure` → `Jamb folded cover.001` | 70.05847 | (-1.445750, 6.400000, 1.032000) → (-1.453750, 6.469601, 1.032000) |
| `Interface label mounting stem` → `Suit service enclosure` | 9.23078 | (-1.434519, 6.197000, 1.455000) → (-1.443750, 6.197000, 1.455000) |
| `Coupling parking clip` → `Suit service enclosure` | 4.99992 | (-1.528750, 6.290500, 1.090500) → (-1.533750, 6.290500, 1.090500) |

### 4. confirmed support-dependent compound or hardware separation

All members: `Screwdriver slot.082`.

1 islands; whole-cluster gap lower bound **39.04001 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Screwdriver slot.082` → `Reserve removable door` | 59.22254 | (-2.504073, 8.295871, 0.140872) → (-2.470310, 8.322248, 0.181757) |

### 5. confirmed support-dependent compound or hardware separation

All members: `Screwdriver slot.084`.

1 islands; whole-cluster gap lower bound **39.04001 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Screwdriver slot.084` → `Reserve removable door` | 59.22259 | (-2.196242, 7.901865, 0.140872) → (-2.162480, 7.928243, 0.181757) |

### 6. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw.004`.

1 islands; whole-cluster gap lower bound **28.00001 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw.004` → `Reserve removable door` | 43.44627 | (-2.408485, 8.364000, 0.148485) → (-2.430501, 8.346800, 0.181757) |

### 7. confirmed support-dependent compound or hardware separation

All members: `Battery carry handle`, `Battery carry handle.001`, `Battery supported drawer rail`, `Battery supported drawer rail.001`, `Battery terminal`, `Battery terminal.001`, `Battery terminal.002`, `Battery terminal.003`, `MED_R2 | Exposed reserve battery service construction`, `Reserve battery module`, `Reserve battery module.001`.

55 islands; whole-cluster gap lower bound **25.22945 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Battery carry handle` → `Reserve removable door` | 160.28893 | (-2.326766, 8.477231, 0.522794) → (-2.453075, 8.378548, 0.522794) |
| `Reserve battery module` → `Battery supported drawer rail` | 7.49995 | (-2.433500, 8.525001, 0.325000) → (-2.433500, 8.525001, 0.317500) |
| `Reserve battery module.001` → `Battery supported drawer rail.001` | 7.50004 | (-2.433500, 8.525001, 0.735000) → (-2.433500, 8.525001, 0.727500) |
| `Battery supported drawer rail` → `Reserve folded back` | 27.50056 | (-2.497000, 8.935000, 0.285500) → (-2.497000, 8.962501, 0.285500) |
| `Battery supported drawer rail.001` → `Reserve folded back` | 27.50056 | (-2.497000, 8.935000, 0.695500) → (-2.497000, 8.962501, 0.695500) |
| `Battery supported drawer rail` → `Reserve folded side` | 32.50019 | (-2.500000, 8.508000, 0.285500) → (-2.532500, 8.508000, 0.285500) |
| `Battery supported drawer rail.001` → `Reserve folded side.001` | 32.49996 | (-1.800000, 8.508000, 0.695500) → (-1.767500, 8.508000, 0.695500) |

### 8. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw.002`, `Screwdriver slot.080`.

2 islands; whole-cluster gap lower bound **15.78777 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw.002` → `Cartridge bank formed upright.001` | 17.38174 | (1.262000, 8.301999, 0.140000) → (1.278058, 8.308652, 0.140000) |

### 9. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw`, `Screwdriver slot.078`.

2 islands; whole-cluster gap lower bound **15.78765 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw` → `Cartridge bank formed upright` | 17.38164 | (0.738000, 8.301999, 0.140000) → (0.721942, 8.308651, 0.140000) |

### 10. confirmed support-dependent compound or hardware separation

All members: `Clear cabinet sliding pane`, `Clear cabinet sliding pane.001`, `Formed pull grip.001`, `Formed pull grip.002`, `Handle mounting boss.002`, `Handle mounting boss.003`, `Handle mounting boss.004`, `Handle mounting boss.005`, `MED_R2 | Medical cabinet fabricated face `, `MED_R2 | Medical cabinet fabricated face .001`, `MED_R2 | Neglected cabinet restraint seal`.

54 islands; whole-cluster gap lower bound **13.99994 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Clear cabinet sliding pane` → `Cabinet formed edge` | 13.99987 | (3.261000, 8.388000, 1.342000) → (3.275000, 8.388000, 1.342000) |
| `Clear cabinet sliding pane.001` → `Cabinet formed edge.001` | 14.00010 | (3.261000, 6.552000, 1.342000) → (3.275000, 6.552000, 1.342000) |
| `Clear cabinet sliding pane` → `Supply cabinet shelf.003` | 26.86401 | (3.260414, 8.311999, 2.439414) → (3.276171, 8.311999, 2.461172) |
| `Clear cabinet sliding pane.001` → `Supply cabinet shelf` | 44.60887 | (3.260414, 6.552000, 1.340586) → (3.277486, 6.552000, 1.299373) |

### 11. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw.001`, `Screwdriver slot.079`.

2 islands; whole-cluster gap lower bound **12.00104 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw.001` → `Shelf retaining lip.002` | 12.00144 | (0.750000, 8.301999, 1.292000) → (0.750000, 8.314000, 1.292000) |

### 12. confirmed support-dependent compound or hardware separation

All members: `Cabinet perimeter screw.003`, `Screwdriver slot.081`.

2 islands; whole-cluster gap lower bound **12.00104 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cabinet perimeter screw.003` → `Shelf retaining lip.002` | 12.00144 | (1.250000, 8.301999, 1.292000) → (1.250000, 8.314000, 1.292000) |

### 13. confirmed support-dependent compound or hardware separation

All members: `Jamb captive fastener`, `Screwdriver slot`.

2 islands; whole-cluster gap lower bound **11.00004 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Jamb captive fastener` → `Jamb folded cover` | 22.40007 | (-1.442750, 2.665400, 0.563000) → (-1.465150, 2.665400, 0.563000) |

### 14. confirmed support-dependent compound or hardware separation

All members: `Jamb captive fastener.002`, `Screwdriver slot.002`.

2 islands; whole-cluster gap lower bound **11.00004 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Jamb captive fastener.002` → `Jamb folded cover` | 22.40007 | (-1.442750, 2.665400, 2.193000) → (-1.465150, 2.665400, 2.193000) |

### 15. confirmed support-dependent compound or hardware separation

All members: `Jamb captive fastener.003`, `Screwdriver slot.003`.

2 islands; whole-cluster gap lower bound **11.00004 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Jamb captive fastener.003` → `Jamb folded cover.001` | 22.40007 | (-1.442750, 6.594600, 0.563000) → (-1.465150, 6.594600, 0.563000) |

### 16. confirmed support-dependent compound or hardware separation

All members: `Jamb captive fastener.005`, `Screwdriver slot.005`.

2 islands; whole-cluster gap lower bound **11.00004 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Jamb captive fastener.005` → `Jamb folded cover.001` | 22.40007 | (-1.442750, 6.594600, 2.193000) → (-1.465150, 6.594600, 2.193000) |

### 17. confirmed support-dependent compound or hardware separation

All members: `Decon ceiling lamp`, `Decon diffuser`.

2 islands; whole-cluster gap lower bound **10.00023 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Decon ceiling lamp` → `Decon ceiling` | 10.00016 | (1.976000, 10.016000, 2.540000) → (1.976000, 10.016000, 2.550000) |

### 18. confirmed support-dependent compound or hardware separation

All members: `Access panel fastener`, `Screwdriver slot.014`.

2 islands; whole-cluster gap lower bound **7.00021 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Access panel fastener` → `Serviceable inner access panel` | 20.20018 | (-3.626750, 2.720000, 0.881000) → (-3.646950, 2.720000, 0.881000) |

### 19. confirmed support-dependent compound or hardware separation

All members: `Access panel fastener.002`, `Screwdriver slot.016`.

2 islands; whole-cluster gap lower bound **7.00021 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Access panel fastener.002` → `Serviceable inner access panel` | 20.20018 | (-3.626750, 3.140000, 0.881000) → (-3.646950, 3.140000, 0.881000) |

### 20. confirmed support-dependent compound or hardware separation

All members: `Access panel fastener.004`, `Screwdriver slot.018`.

2 islands; whole-cluster gap lower bound **6.99997 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Access panel fastener.004` → `Serviceable inner access panel.001` | 20.19994 | (-3.626750, 6.120000, 0.881000) → (-3.646950, 6.120000, 0.881000) |

### 21. confirmed support-dependent compound or hardware separation

All members: `Access panel fastener.006`, `Screwdriver slot.020`.

2 islands; whole-cluster gap lower bound **6.99997 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Access panel fastener.006` → `Serviceable inner access panel.001` | 20.19994 | (-3.626750, 6.540000, 0.881000) → (-3.646950, 6.540000, 0.881000) |

### 22. confirmed support-dependent compound or hardware separation

All members: `Engraved RECOVERY.001`, `Engraved backing RECOVERY.001`.

2 islands; whole-cluster gap lower bound **6.00004 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Engraved backing RECOVERY.001` → `Identity wall spacer` | 5.99997 | (3.974000, 5.048000, 1.662000) → (3.980000, 5.048000, 1.662000) |

### 23. confirmed support-dependent compound or hardware separation

All members: `Engraved SUPPLIES`, `Engraved backing SUPPLIES`.

2 islands; whole-cluster gap lower bound **6.00004 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Engraved backing SUPPLIES` → `Identity wall spacer.001` | 5.99998 | (3.974000, 1.818000, 1.662000) → (3.980000, 1.818000, 1.662000) |

### 24. raised display element requires substrate contract

All members: `Telemetry status bar.002`.

1 islands; whole-cluster gap lower bound **5.49984 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Telemetry status bar.002` → `Monitor dark face` | 5.50024 | (-0.799000, 8.646501, 1.250000) → (-0.799000, 8.652000, 1.250000) |

### 25. Receiver assembly and C01 plaque require an architectural mount; their mutual 5.00011 mm separation is a numerical tolerance edge, but the combined cluster is separated from all outside geometry by at least 14.00018 mm.

All members: `Cartridge extraction tab`, `Cartridge retaining drawer`, `Engraved INSERT`, `Engraved RELEASE`, `Engraved backing INSERT`, `Engraved backing RELEASE`, `Interface label mounting stem.001`, `Interface label mounting stem.002`, `Keyed cartridge throat`, `Mechanical selector`, `Receiver captive bolt`, `Receiver captive bolt.001`, `Receiver captive bolt.002`, `Receiver captive bolt.003`, `Receiver cast housing`, `Receiver recessed face`, `Screwdriver slot.070`, `Screwdriver slot.071`, `Screwdriver slot.072`, `Screwdriver slot.073`, `Selector escutcheon`.

21 islands; whole-cluster gap lower bound **5.00011 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Cartridge extraction tab` → `Engraved backing C01` | 5.00016 | (-1.193750, 2.957000, 1.359500) → (-1.188750, 2.957000, 1.359500) |

### 26. Receiver assembly and C01 plaque require an architectural mount; their mutual 5.00011 mm separation is a numerical tolerance edge, but the combined cluster is separated from all outside geometry by at least 14.00018 mm.

All members: `Engraved C01`, `Engraved backing C01`.

2 islands; whole-cluster gap lower bound **5.00011 mm**.

| Object → possible target | Measured ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Engraved backing C01` → `Cartridge extraction tab` | 5.00016 | (-1.188750, 2.957000, 1.359500) → (-1.193750, 2.957000, 1.359500) |

## Receiver / C01 tolerance crosscheck

Clusters 25 and 26 are only 5.00011 mm apart, a marginal floating-point edge. Merging them at 5.001 mm does **not** restore an architectural path: their combined 23-island assembly stays at least **14.00018 mm** from all outside geometry. The real receiver host omission is substantive; its internal C01 separation need not be treated as a major defect.

| Object → possible target | Ray gap (mm) | Source point → target point (m) |
|---|---:|---|
| `Receiver cast housing` → `Seal guide` | 14.00010 | (-1.521750, 2.825000, 1.566000) → (-1.521750, 2.811000, 1.566000) |
| `Receiver cast housing` → `Access jamb graphite return` | 28.69980 | (-1.521750, 2.825000, 1.566000) → (-1.521750, 2.796300, 1.566000) |
| `Receiver cast housing` → `Jamb folded cover` | 35.51299 | (-1.521750, 2.825000, 1.566000) → (-1.513750, 2.790400, 1.566000) |

The nearest receiver target is a rubber seal guide. A new return or bracket should reach the structural graphite jamb or folded cover; touching a seal alone does not establish a plausible load path.

## Classification and repair implications

Glyph relief at roughly 1.85 mm above its plaque is within the recommended gap and is not a separate mechanical omission. The two plaque backings themselves are 6 mm from their wall spacers. The telemetry strip is a small 3 mm thick display element 5.5 mm off its screen: require an explicit substrate/relief contract, and keep that conditional display issue distinct from detached equipment and hardware.

The battery modules are 7.5 mm above their rails; the rails are 27.5 mm from the back and 32.5 mm from the side carcass. Their newly added service detail supplies internal contacts without solving the enclosure path. The cabinet pane/frame/handles likewise form an internally detailed cluster with a 14 mm gap to the carcass. The suit-service enclosure has a 49 mm gap even to the nearest seal guide, a 63.7 mm gap to the structural graphite jamb, and a 9.23 mm internal label-stem-to-enclosure gap.

Preserve original matrices and room placement. Add the actual mounting returns, retained rails, screw shoulders, ceiling mounting base and plaque spacers. The orphan reserve slots are attached to the rotated door hierarchy while the original perimeter screw heads stay fixed; add coherent native mounting substrates rather than counting their names or arbitrary crossings as roots. Validate each mechanism through its intended carcass/frame and then to floor/wall/ceiling.

## Coverage and limits

The independent baseline diff finds all 1,203 objects present and no dimension changes. It records the reserve door hierarchy and clipboard dressing pose changes; the replay verifier recognizes the declared pose exceptions. Protected source/map hashes are unchanged in the cold replay. No layout relocation is inferred from that comparison.

This bounded preflight does not clear connected AABB components, exhaustively validate every intended internal attachment, inspect actual shader consumers/UV scale, or perform a broad duplicate audit. The checker’s winding/declared-contact results remain useful evidence within their stated coverage. Cold dependency resolution is verified in this checkout; relocation portability, final camera stability, Unity and runtime performance are unverified.

Raw probe scripts and outputs: `/tmp/medical-tech14/`. The accompanying JSON embeds all 26 cluster member lists and measured directed contacts.
