# C89 circular wall fan depth review

Candidate: `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
Source SHA-256: `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`

## Exact object mapping

The reviewed subject for issue #126 is the repeated circular wall fan/grille authored by `a_fan` in `scripts/rh_walls.py`. It is distinct from the rectangular eight-louvre `a_vent` unit and from the crane hardware. In the saved scene, each fan barrel is a disconnected 160-vertex component inside the merged mesh `RH walls assets AUDI_SATIN`. The component has a 0.88 m circular envelope and a 0.15 m deep barrel, matching the builder's 40-sided rings at radii 0.40/0.44 m and wall-normal depths 0.05/0.20 m.

A source-bound projection probe maps the visible fans to their saved world centers:

- View25 left grille: `(7.0156, 9.4281, 9.45)` m, projected to approximately pixel `(183, 246)`.
- View25 middle grille: `(10.5600, 4.0500, 9.45)` m, projected to approximately pixel `(503, 280)`.
- View26 lower-right grille: `(-6.8506, 9.5293, 9.45)` m, projected to approximately pixel `(1143, 560)`.

The projected view26 center matches the grille visible in the lower-right of the actual render. It is another instance of the same `a_fan` mesh family, on the northwest diagonal wall, rather than a different machine grille. Views03 and04 do not frame this upper-wall fan family.

## Pixel review and disposition

View25 is a wide 1280×720, 96-sample room view. It identifies multiple wall-fan instances in context but the fan barrels are too small there to establish their depth by themselves. View26 is also a full-quality 1280×720, 96-sample render. Its lower-right fan shows a protruding cylindrical barrel, layered concentric rings, radial grille members and a dark recessed core. The square carrier plate is clipped at the far-right image edge, but the circular fan and depth-bearing barrel remain in frame. That is sufficient for the narrowly named “Circular vent depth” criterion; this review does not claim that every carrier edge or every wall utility is fully shown.

- View25 image SHA-256: `edc16b5b1eaa5d0dadfde5ce9630fe49a23e7584174698f527c121cfbb5b33ae`; manifest SHA-256: `ecd8f92c0fdfe36b5cfdb3facd6e7824c153096612c93361f5b2ec3ccf0be672`.
- View26 image SHA-256: `a66e4de936cdd0207119222154eba19d9047bb96d0ecd62f5ebc34afd50595a0`; manifest SHA-256: `676325deb06f2ac19a510eef81fef77a7ed5cddba352f0ce812d3d0b341ebf0d`.
- Fan-mapping probe: `evidence/LUNA_C89_WALL_FAN_MAPPING_PROBE.py`; result `evidence/LUNA_C89_WALL_FAN_MAPPING_PROBE.json`, SHA-256 `f4a9f0729928643aaad075c1b167e558157a1b1ac22840e01565542be67040fa`.

**Disposition:** Accept #126 on these exact C89 pixels and the saved mesh mapping. This is a criterion-specific C89 visual acceptance. Any carry to a later candidate must independently bind the wall-fan mesh/material, cameras, and lighting through that candidate's exact scene-delta lineage. It does not waive the mandatory fresh main views or the broader #139 signage audit.
