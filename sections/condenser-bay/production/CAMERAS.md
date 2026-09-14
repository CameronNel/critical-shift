# Fixed condenser evidence cameras

The 18 primary/player cameras render the complete scene with walls enabled. Six proven-invalid camera transforms were corrected as documented in CAMERA_CORRECTIONS.md; the other twelve remain unchanged. The saved matrices in validation/R34/astra-saved-audit.json are authoritative.

Supplemental S01–S06 provide close or wider coverage of local U02, CW endpoints, roof, glass, feet and operator work. S07 is explicitly labelled as a mesh cutaway and supplements the exhaust views; it is never substituted for a player view.

## Saved R34 transforms

| Camera | Position (x, y, z m) | Lens (mm) |
|---|---|---:|
| C01_ENTRY | (0.000, -1.120, 1.550) | 22.0 |
| C02_HERO | (-1.350, 1.200, 1.700) | 22.0 |
| C03_REVERSE | (3.050, 9.050, 1.720) | 22.0 |
| C04_EXHAUST | (5.820, 4.350, 5.450) | 26.0 |
| C05_RETURN | (0.450, 8.550, 1.580) | 24.0 |
| C06_COOLING | (6.550, 2.200, 2.450) | 28.0 |
| C07_OPERATOR | (1.180, 4.050, 1.520) | 26.0 |
| C08_MAINT | (5.900, 4.200, 5.450) | 28.0 |
| C09_ROOF | (5.800, 6.000, 5.450) | 28.0 |
| C10_MATERIALS | (2.500, 5.920, 1.120) | 32.0 |
| W01_ENTRY_CORNER | (0.250, 1.550, 1.520) | 22.0 |
| W02_SW_TURN | (0.500, 1.700, 1.580) | 24.0 |
| W03_NW | (-1.350, 8.900, 1.600) | 24.0 |
| W04_NE | (8.550, 7.150, 1.620) | 24.0 |
| W05_SE | (8.500, 1.580, 1.620) | 24.0 |
| W06_WEST_AISLE | (0.120, 6.850, 1.550) | 24.0 |
| W07_EAST_PULL | (8.200, 2.350, 1.580) | 26.0 |
| W08_GALLERY_TURN | (5.850, 5.400, 5.450) | 28.0 |

C01 covers the D01 threshold; C02 the condenser hero; C03 the reverse return-aisle face; C04 the external exhaust joint; C05 the return pumps; C06 the cooling isolators; C07 the operator panel; C08 maintenance access; C09 roof services; C10 material detail. W01–W08 supply entry, corners, ground aisles and gallery turns. Tight C04/C06/C09 views require their same-revision supplemental companions.

Historical Grok camera documentation is retained in CAMERAS_R21.md. Acceptance requires the full fixed18 and supplemental evidence, with independent cold renders.
