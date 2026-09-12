# Fixed evaluation cameras

All scene coordinates are metres, Z up. Eye height is 1.70 m except the explicit material inspection at 1.60 m. Camera values are independently mirrored by `blender/validate.py`.

| Camera | Position XYZ | Look-at XYZ | Lens mm | Evidence |
|---|---|---|---:|---|
| C01_ENTRY | 0, 1.4, 1.70 | .25, 9.9, 1.65 | 25 | Refinery seam, initial route |
| C02_PRIMARY_ROUTE | 3, 9, 1.70 | 13, 10.4, 1.70 | 27 | Cross passage and freight gate |
| C03_HERO | −1.45, 6, 1.70 | 1.1, 11.5, 1.8 | 22 | Staging, workbench, service and freight routes |
| C04_REVERSE | 1, 10.5, 1.70 | −.15, 1, 1.60 | 26 | Reverse entry and return leg |
| C05_EAST_TURN | 11.15, 8.45, 1.70 | 14.2, 17, 1.65 | 25 | Second freight turn |
| C06_REACTOR_THRESHOLD | 13.5, 19.4, 1.70 | 14.3, 24, 2.10 | 26 | Enlarged adapter / closed presentation cap |
| C07_BYPASS | .45, 14, 1.70 | −.2, 19.7, 1.65 | 25 | Narrow service bypass |
| C08_SERVICE_JUNCTION | 1.7, 19.85, 1.70 | 7.6, 20, 1.6 | 25 | Northern clean-service header |
| C09_MATERIALS | 3.7, 9.9, 1.60 | 2.65, 12.32, .85 | 42 | Current cartridge, restraints and carrier materials |
| C10_PLANT_HEADER | −.7, 17.2, 1.70 | −5.4, 17.4, 1.45 | 25 | Plant header and dead-end condition |

Style05 rebaselined C03 because earlier framing excluded the workbench and freight threshold, and C09 because the corrected parked carrier moved out of the bypass. Historical slice01–04 images are retained as historical evidence, not identical-camera comparisons. C03 and C09 have stayed fixed since style05, before any complete-scene review.

Formal settings: 1440×960, Cycles HIP, 32 samples, denoising, seed 71, maximum 8 bounces, AgX Medium High Contrast, exposure +0.10, RGB PNG. Earlier 1200×800 /24-sample slices are historical. The final cold reopen must render all ten cameras from the saved file with the frozen formal settings.

Supplemental fixed inspection cameras, established at style10 and independently mirrored in the validator:

| Camera | Position XYZ | Look-at XYZ | Lens mm |
|---|---|---|---:|
| D01_CARRIER_OPERATION | 1.17,10.2,1.24 | 2.38,12.32,.63 | 42 |
| D02_WORKBENCH | −.2,8.75,1.65 | −1.8,10.58,1.26 | 40 |
| D03_UTILITY | 3.8,11,1.72 | 3.8,13.15,1.72 | 46 |
| D04_REACTOR_WIDE | 13.5,17.1,1.7 | 14.2,23.5,2.45 | 19 |
| D05_GATE_MECHANISM | 5.1,8.45,3.98 | 6.01,8.85,3.87 | 35 |
| D06_SERVICE_RECESS | .70,15.2,1.72 | −1.49,15.08,1.72 | 32 |

These supplement the original ten and do not replace any formal camera.

D04–D06 were introduced for full02. D04 proves complete reactor floor/head coverage that C06's fixed close view cannot show. D06 inspects the actual recessed equipment. D05's full02 position(4.65,9.5,2.75), target(6.35,10,3.5),24mm was independently proven invalid for its intended machinery evidence: the sign and lamp dominated, and the drive was cropped. The attempted full03 replacement also failed, as detailed below. From eng07 onward, the current table establishes the corrected diagnostic pose. Enclosed roller contact/motion remains separately verified in evaluated geometry. The ten mandatory camera transforms and all other diagnostics remain unchanged.

The attempted full03 D05 pose was(5.25,8.10,4.05), target(6.38,8.75,3.92),35mm. Its image was black: a read-only mesh-ray probe found the tray support only5.8mm ahead of the lens, inside its40mm near clip. That attempt is preserved as failed evidence, not approved or substituted retrospectively. The current table gives the corrected next pose: independent-of-transform CPU candidate rays reach actual motor, chain and drive-cover surfaces at0.85–1.30m. A new central near-camera obstruction gate and positive/negative controls were added after this failure. Saved eng07 and eng08 previews show the motor clearly; eng08 still needed material/light and construction corrections against approved C10. Final pixel approval remains pending. The ten mandatory views remain fixed.

