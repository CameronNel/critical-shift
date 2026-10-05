# Fixed review cameras (front-end area)

Plan coordinates (metres, x east, y north, z up); module-local = plan + (-8, +80). Rendered by `render_views.py`
(Cycles CPU, OIDN, AgX, 40 samples, 1280 x 720).

| Camera | Eye (x, y, z) | Target (x, y, z) | Lens | Checks |
|---|---|---|---|---|
| FE_01_SPAWN_EXIT_NORTH | 8.0, -80.4, 1.65 | 8.0, -30.0, 2.4 | 20 | first view on leaving the spawn room: cafeteria, kiosk, rec corner, hall opening |
| FE_02_CAFE_DOOR_WEST_YARD | -7.5, -70.0, 1.65 | -48.0, -70.4, 2.2 | 22 | yard seen from the cafeteria door: rail, junk, mine portal |
| FE_03_HALL_WEST_TO_EAST | -3.4, -55.6, 1.7 | 32.0, -53.0, 2.4 | 20 | hall clutter, cave-ins, clear door line |
| FE_04_AERIAL | 14.0, -140.0, 66.0 | -6.0, -68.0, 0.0 | 32 | layout of the three zones (roofs hidden) |
| FE_05_CAFE_REVERSE_NORTH_TO_SOUTH | 8.0, -60.6, 1.65 | 8.0, -85.0, 1.8 | 20 | dining east, living room west |
| FE_06_YARD_REVERSE_PORTAL_TO_EAST | -47.4, -70.4, 1.65 | -8.0, -70.0, 2.6 | 22 | mine lane toward the cafeteria porch |
| FE_07_HALL_SPINE_DOOR_BACK | 8.0, -48.6, 1.65 | 8.0, -62.0, 2.2 | 20 | hall from the reactor-spine door |
| FE_08_LOUNGE_CORNER | 7.4, -71.0, 1.7 | -5.0, -70.6, 1.1 | 18 | living room (south) and recreation corner (north) |
| FE_09_MINE_FRONT | -30.5, -70.9, 1.7 | -48.0, -70.0, 2.3 | 24 | the R39 portal front, tunnel mouth, rail start |

FE_08 was re-aimed and FE_09 added after the owner's review notes (the old FE_08 looked at a lounge that no longer exists).

## Cafeteria inspection cameras (revision 4)

| Camera | Eye (x, y, z) | Target (x, y, z) | Lens | Checks |
|---|---|---|---|---|
| CAF_01_ENTRY_NORTH | 8.0, -79.2, 1.65 | 8.0, -60.0, 2.3 | 20 | first view from the airlock: hall sign, directory, kiosk, serving |
| CAF_02_DINING | 9.5, -78.8, 1.7 | 21.5, -72.5, 1.0 | 22 | dining tables, booths, drinks, recycling, medical door |
| CAF_03_SERVING | 9.6, -70.9, 1.7 | 20.5, -64.5, 1.4 | 24 | counter, menu boards, kiosk, queue, kitchen door |
| CAF_04_LOUNGE | 3.4, -71.2, 1.65 | -5.0, -77.0, 1.0 | 20 | lounge, TV wall, bookcase, yard door |
| CAF_05_GAME_CORNER | 3.0, -67.0, 1.65 | -5.0, -62.5, 1.2 | 20 | arcade, foosball, darts, rules board |
| CAF_X1_AIRLOCK_DOOR | 8.0, -71.5, 1.65 | 8.0, -80.0, 1.7 | 20 | spawn airlock leaves and sign |
| CAF_X2_YARD_DOOR | 1.5, -70.0, 1.65 | -8.0, -70.0, 1.7 | 20 | yard door leaves and exit sign |
| CAF_X3_MEDICAL_DOOR | 18.5, -70.0, 1.65 | 26.0, -70.0, 1.7 | 20 | medical door and sign |

## Hall inspection cameras (revision 6)

| Camera | Eye (x, y, z) | Target (x, y, z) | Lens | Checks |
|---|---|---|---|---|
| HAL_01_FROM_CAFETERIA | 8.0, -59.4, 1.65 | 8.0, -48.0, 2.3 | 20 | first view from the cafeteria opening: blast door, gantry, stair, safety station |
| HAL_02_WEST_LOCKERS | 30.5, -54.0, 1.65 | -3.5, -55.5, 1.5 | 20 | the long hall: dispatch, desk, status board, lockers, west door |
| HAL_03_LOCKERS_AND_PPE | 5.6, -54.2, 1.65 | -3.0, -58.2, 1.2 | 22 | locker room, PPE issue, west door |
| HAL_04_DESK_AND_DISPATCH | 12.0, -53.4, 1.65 | 24.0, -58.5, 1.3 | 22 | shift desk, radios, dispatch bays, east door |
| HAL_05_SAFETY_STATUS | 17.0, -54.6, 1.65 | 16.0, -48.2, 2.1 | 24 | safety station, hose cabinet, status board |
| HAL_06_MAINTENANCE_BAY | 6.4, -54.6, 1.65 | -2.4, -50.4, 1.5 | 22 | workbench, tool wall, stair, parts shelving |
| HAL_X1_BLAST_DOOR | 8.0, -53.0, 1.65 | 8.0, -48.0, 2.2 | 24 | blast door, beacons, console, bollards |
| HAL_X2_WEST_DOOR | 6.0, -54.0, 1.65 | -4.0, -54.0, 1.9 | 20 | west double door and signs |
| HAL_X3_EAST_DOOR | 26.0, -54.0, 1.65 | 32.0, -54.0, 1.9 | 20 | east double door, muster area |
