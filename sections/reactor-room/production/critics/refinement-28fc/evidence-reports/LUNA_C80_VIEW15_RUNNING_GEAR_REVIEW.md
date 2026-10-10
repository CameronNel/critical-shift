# C80 view 15: crane end carriage and running gear

**Disposition: accept issue 107, narrowly.** This is a current-candidate visual acceptance for the depicted end carriage and its running gear only; it does not accept the crane as a whole or any roof construction rows.

- Candidate scene: `hall_final.blend`, SHA-256 `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`.
- Full-quality image: [15_roof_running_gear.png](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/inspection-720p/15_roof_running_gear.png), SHA-256 `54c8de0185d709fa6436982b35d5fe79fa2b4c481aabc7f1d47e9ff7e9c9b6a2`.
- Render manifest: [render_manifest.json](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/inspection-720p/render_manifest.json): Blender 5.2.2, Cycles CPU, 1280×720, 96 maximum samples, 32 minimum adaptive samples, 16-bit output; view 15 completed in 1832.86 seconds.

The wheel is dark, but its rounded tread and separate side flange remain visible through the reflection and edge lighting. The frame shows the bearing box/fork, axle-side structure and wheel positioned on the red runway rail at useful scale. The dark recess does not erase the wheel silhouette or make it read as a flat black patch. The wheel/rail relationship is independently consistent with the authored dimensions: the `disc` helper takes the first radius argument as the wheel radius (0.19 m), and its center at z=14.61 m puts the bottom at z=14.42 m, the rail-top contact plane. I initially misread the second helper argument as an outer radius; it is axial thickness, so there is no 70 mm rail penetration.

This image resolves the earlier end-truck scale and silhouette concern. I would not add a global or local light based on this view. Keep other carriage, trolley and roof criteria on their own evidence routes.
