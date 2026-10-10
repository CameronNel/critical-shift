# C89 Route Marking Continuity Review

**Candidate:** C89, source SHA-256 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`

## Current full-quality pixels

- Main03, `03_floor_access_lane.png`, SHA-256 `b22f107f4f1726af8af84c6ca28c19569735f91ec5212be5d004201cfaca789b`; manifest SHA-256 `00b89048097d63e94eedc291eba95e436c4d19b88a13d8f3c9ba5cdfe0fb5485`.
- Main04, `04_floor_pool_circulation.png`, SHA-256 `2a3ac3d2a793445e8134fc18bcdfbfe570c17d0c8b98c453ae1bc2c02765a27a`; manifest SHA-256 `0a03204f7ca70f81ae03778b5b422ff91e5d2c35542a896481150009359f852a`.

Both are exact-C89 1280×720 Cycles frames with 96 maximum samples, 32 minimum samples, 16-bit color, and no preview scaling.

## Finding

The two views resolve route continuity at different scales. Main03 shows the floor arrows, aisle edges, and worn route paint through the wet-floor area. Main04 follows the route around the pool and shows the broad room circulation markings with the continuous safety circle. The line network remains traceable around grates and pool staging; cones do not cover the directional arrows or painted aisle edges in the viewed compositions.

The exact-C89 `floor-guidance.json` (SHA-256 `9115601cc15cdd88ea406d814a5cf3ed2f45e5ee900e5056a473429603fae4ed`) checks all eight cone rubber footprints against the saved white-arrow and yellow-aisle-edge faces: eight records, zero failures, and zero measured arrow/aisle overlap area. This is finite footprint evidence, not a general floor-collision test.

I accept #68, Route marking continuity, for C89. This closes only route continuity and the mapped cone obstruction question. It does not close the separate wet/oil/dirt distinction (#61), traffic wear (#74), pool-port construction, or broader material-wear criterion (#137).
