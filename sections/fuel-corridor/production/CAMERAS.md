# Fixed camera evidence

Original 16 camera transforms and lenses are retained and numerically checked.
Three supplementary player-height portal views have been fixed since F3.
The full review renders native frame 1 at 1280×853, Cycles CPU, 32 samples, seed 7,
denoising on, AgX / Medium High Contrast, exposure −0.15. The closed freight
view is a disposable leaf-pose diagnostic; the editable source keeps the gate open.

| Camera | Position in metres | Lens mm |
|---|---|---:|
| C01_ENTRY | 0.00, 1.40, 1.70 | 25 |
| C02_PRIMARY_ROUTE | 3.00, 9.00, 1.70 | 27 |
| C03_HERO | -1.45, 6.00, 1.70 | 22 |
| C04_REVERSE | 1.00, 10.50, 1.70 | 26 |
| C05_EAST_TURN | 11.15, 8.45, 1.70 | 25 |
| C06_REACTOR_THRESHOLD | 13.50, 19.40, 1.70 | 26 |
| C07_BYPASS | 0.45, 14.00, 1.70 | 25 |
| C08_SERVICE_JUNCTION | 1.70, 19.85, 1.70 | 25 |
| C09_MATERIALS | 3.70, 9.90, 1.60 | 42 |
| C10_PLANT_HEADER | -0.70, 17.20, 1.70 | 25 |
| D01_CARRIER_OPERATION | 1.17, 10.20, 1.24 | 42 |
| D02_WORKBENCH | -0.20, 8.75, 1.65 | 40 |
| D03_UTILITY | 3.80, 11.00, 1.72 | 46 |
| D04_REACTOR_WIDE | 13.50, 17.10, 1.70 | 19 |
| D05_GATE_MECHANISM | 5.10, 8.45, 3.98 | 35 |
| D06_SERVICE_RECESS | 0.70, 15.20, 1.72 | 32 |

Supplementary views: E01_WASTE_APPROACH, E02_CLEAN_APPROACH, E03_FREIGHT_LEAF.
Their complete transforms/lenses and PNG hashes are in each render manifest.
Temporal captures use the same named cameras at explicit frames and preserve
24 fps / fps_base 1.0. Preview resolution/sample changes are labeled in their
own manifests; previews do not replace full-resolution craft review.
