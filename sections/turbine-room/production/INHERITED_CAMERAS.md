# Fixed camera contract

Exact positions, targets and focal lengths are in `cameras.json`, embedded in the saved scene and the build manifest. Transforms were established before formal slice review and have not been changed. Review setting: 1280 × 800, Cycles HIP, 48 samples, denoising, seed28, AgX Medium High Contrast, exposure0.45. Lighting/material changes are authored scene changes, not camera cheats.

| Camera | Intended coverage | Evidence state |
|---|---|---|
| C01_entry | Reactor entry / hall readability | Defined, full hall not built |
| C02_hero | Main conversion train | Defined, full hall not built |
| C03_reverse | Reverse equipment / return route | Defined, full hall not built |
| C04_route | Primary path toward electrical | Defined, full hall not built |
| C05_east_service | Machinery service aisle / pinch | Defined, full hall not built |
| C06_throttle | Throttle / load / output control | Defined, controls not built |
| C07_coupling | Shaft / coupling / guard | Defined, machine not built |
| C08_maintenance | Secondary maintenance bay / electrical doorway | Slice pixels rendered and reviewed |
| C09_generator | Generator / output service | Defined, generator not built |
| C10_materials | Close material / contact evidence | Slice pixels rendered and reviewed |

Once full formal review starts, compare identical framing/settings in each complete cycle. Rendered C08/C10 alone cannot certify circulation, blind areas, or the complete ten-camera requirement.
