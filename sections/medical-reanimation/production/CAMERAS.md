# Fixed camera coverage

All fourteen saved cameras have eye height1.68m and are retained across visual correction passes. Metric locations/lenses/rotations are recorded directly from the saved artifact in the render manifest; use those exact values for comparisons. The ten `CAM_*` cameras are the formal fixed set. Four `W*` views supplement approaches.

| Camera | Purpose |
|---|---|
| CAM_ENTRY | Entry-to-rear overall room and process hierarchy |
| CAM_HERO | OCRU manufactured enclosure and primary interfaces |
| CAM_REVERSE | Reverse circulation, entry and opposite room surfaces |
| CAM_ROUTE | Central rescue/transfer route and rear work zone |
| CAM_CONSOLE | Restart controls and status display readability |
| CAM_DECON | Wand, reel, shower, drain, PPE collection |
| CAM_RECOVERY | Recovery berth, linen, frame and player approach |
| CAM_PINCH | OCRU close approach, transfer hardware, service details |
| CAM_MATERIALS | Reserve power cabinet, controls and material response |
| CAM_MAINT | Rear corner, isolation, decon and cabinet access |
| W01_ENTRY_OUTSIDE | Exterior approach through owned door/frame |
| W02_CART | Parked transport cart, casters, lifting frame and handles |
| W03_SUPPLIES | Workbench, sink, supply artifacts and materials |
| W04_REAR_SERVICE | Stock/console/decon service relationship |

Supplemental `S01..S06` are in-memory poses of the saved scene: adult proxy/cart transfer, dropped-cart bypass, decon cart apron with extended wand, closed entry, open battery service door and the corrected lateral cart extraction. The neutral adult proxy is validation dressing, not a delivered character asset. These images are not substituted for any fixed camera. No saved default scene is overwritten by the state renderer.
