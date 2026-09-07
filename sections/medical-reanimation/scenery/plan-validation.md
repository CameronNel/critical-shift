# P01 plan checks

8 September 2026. Scope: authored documentation and 2D floorplan only.

- JSON and SVG parse successfully.
- The coordinate polygon independently gives 80.36 m² using the shoelace formula, matching the rectangular area calculation.
- Exactly one portal is marked `exterior_pedestrian`; recovery is an internal opening. No global connection is assigned.
- Planned route widths are 2.20 m arrival, 1.05 m west, 2.10 m east, and 0.95 m rear. The battery sub-bay is outside those route reservations.
- The wash-bay rectangle is nominal. The authored basin outer bounds x = −3.89…−2.91, y = 1.06…2.24 exceed both nominal X edges by 0.04 m and remain outside essential route reservations; complete fixture bounds remain a final-geometry handoff check.
- The `obstruction-test` layer contains the specified 1.80 × 0.70 m body centred at (0.00, 1.90) and 2.00 × 0.75 m transverse cart centred at (0.00, 2.90). Their exact bounds are x = −0.90…0.90, y = 1.55…2.25 and x = −1.00…1.00, y = 2.525…3.275 respectively. Both diagnostic positions remain outside the east bypass reservation and canonical loading destination (0.55, 4.00); arbitrary placements can still block doorway or loading access and require physical clearing. Individual and combined runtime tests belong to production validation.
- The SVG was rasterized with Sharp to [floorplan-preview.png](floorplan-preview.png) at 1600 × 1150 and its pixels inspected. The preview was regenerated after moving the diagnostic footprints, repositioning the arrival label, clarifying alcove opening height and identifying the nominal wash bay.

These checks validate the plan's data and presentation. They do not validate Blender object extents, door motion, cart turning, ragdoll physics, engine interactions, rendered art quality or production acceptance. Those checks belong to the builder's production evidence.
