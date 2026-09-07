# Fixed evaluation cameras

Preliminary slice cameras S01_style and S02_material were reframed in s02/s03 because the first views cut off threshold, sign and countertop props. Those were evidence corrections before the full baseline. Transforms have been fixed since s03. Actual transforms/lenses are stored in each revision's cameras.json.

The ten full-room cameras below are planned at 1.65 m gameplay eye height. They become fixed when the first complete formal batch is rendered. A camera that proves physically invalid must be documented and rebased before comparisons.

| Camera | Purpose |
|---|---|
| C01_entry | Facility arrival, route and department readability |
| C02_hero | Person and cargo inspection, control hierarchy |
| C03_reverse | Look back from dock, reveal blind-side construction |
| C04_route | Cart bypass, recovery and primary circulation |
| C05_person_scan | Narrow person threshold, height and side clearance |
| C06_cargo_machine | Conveyor, checking cavity, drives and service access |
| C07_staff | Staff working space, furniture and shortcut |
| C08_concealment | Tarp trolley/support bay and rear staff access |
| C09_materials | Counter, glass, paper, fabric, rubber and painted/bare metal |
| C10_arrival | Sealed outside access, dock scale and arrival staging |

Formal settings planned: Cycles HIP, deterministic seed8217, AgX Medium High Contrast, 1440x810 PNG, 64 samples with denoising. Ten matching frames per cycle; a full fresh-process cold render after final stability. No marketing-only framing substitutes for the above.
