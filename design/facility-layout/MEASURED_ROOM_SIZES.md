# Measured room sizes

Measured 2026-10-04 in headless Blender 5.2.2 from the module files on `main`.
Method: world-space bounding box of every visible mesh, curve and text object in each file (evaluated, so modifiers count).
Lights and cameras are excluded. Sizes are in metres, in each module's own local frame (not map orientation).
Files were copied to a scratch folder; nothing in the repo was opened for writing.

"Outer" includes sills, roof overhangs, annexes and external fittings. "Interior" is the number from the room's interface contract.

| Room | File measured | Outer X x Y x Z | Interior (contract) | Notes |
|---|---|---|---|---|
| Reactor | `reactor-room/module.blend`, `module_overhaul_R1.blend` | 27.5 x 27.5 x 23.1 (hall), 34.0 wide with east annex | hall floor 21.6 x 21.6 | Z runs -6.7 (pool) to 16.4. East control room and stair project 6.5 m past the hall. Overhaul R1 holds only the equipment, not the shell. |
| Spawn | `spawn-room/module.blend` | 17.4 x 13.4 x 5.0 | facility hall 15.7 x 13.2 | Exit is on the +Y side. Briefing room 6.0 x 5.7, locker room 6.6 x 6.9. |
| Compliance dock | `compliance-dock/module.blend`, `module_overhaul_R1.blend` | shell 14.2 x 18.2 x 4.6; with roof 15.8 x 18.7 x 6.2 | portals: facility entry 2.4 wide, sealed external arrival 4.6 wide | Long axis runs facility side to outside arrival. |
| Refinery | `refinery/module.blend`, `module_overhaul_R1.blend` | 17.6 x 14.8 x 6.2 | 15.0 x 12.9 x 4.8 | Outer length includes a ~1.1 m sill at each end door. |
| Turbine | `turbine-room/module.blend`, `rebuild/turbine_room_v2_geo.blend` | 15.4 x 29.6 x 9.4 (module, includes a 4 m reactor-side stub); 14.8 x 27.8 x 10.0 (rebuild geometry) | 14 x 24 x 7.2 | Contract external footprint is 14.8 x 25.5. |
| Electrical | `electrical-room/module.blend`, `overhaul/checkpoints/full-R11.blend` | 15.4 x 17.2 x 5.7 | 11.0 x 16.4 x 4.8 | Both files measure the same. The extra width is the east reserve annex. |
| Cooling plant | `cooling-plant/module.blend`, `module_aaa_A1.blend` | 12.9 x 15.0 x 7.2 | 11 x 13 x 5.8 | AAA finish measures the same as the original. |
| Waste storage | `waste-storage/module.blend`, `module_aaa_A1.blend` | 14.9 x 20.8 x 5.9 | 12 x 18 x 4.8 | Same in both files. |
| Medical | `medical-reanimation/module.blend`, `module_overhaul_R2.blend` | 9.8 x 13.0 x 5.3 | 8 x 9 x 3.6 | Same in both files. |
| Fuel corridor | `fuel-corridor/module.blend`, `accepted.blend` | 23.1 x 24.0 x 6.4 | freight path 38.2 m (L shape) | Envelope matches the L path: 10 m, 14.2 m across, 14 m. |
| Condenser bay | `condenser-bay/module_aaa_A1.blend` | 13.2 x 12.8 x 8.4 | - | Not used in the current plan. |

## Corrections to earlier plan estimates
- Spawn: 17.4 x 13.4 m, not 12 x 26.
- Dock: 14.2 x 18.2 m shell, not 19 x 14.
- Reactor: 27.5 x 27.5 m plus annex, not 29 x 29.
- All contract interior sizes understate the real footprint by 2 to 3 m per side.

## Not measured
- Cafeteria, hall, yard and lobby do not exist yet, so their sizes are still proposals.
- Door positions were read from the interface contracts, not from the meshes.
