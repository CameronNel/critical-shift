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
