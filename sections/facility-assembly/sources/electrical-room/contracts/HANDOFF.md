# Electrical Room integration handoff — E05 verified

Complete original room: 11.0 × 16.4 × 4.8 m main hall and 2.8 × 4.4 × 3.6 m reserve bay. Strict Valorant direction, cream/charcoal/oxide palette, no teal. The final independent review and cold pixel comparison are recorded in production/critics and production/validation/E05; both saved-artifact verification and independent cold visual review pass.

## Inspect

Open blender/electrical_room.blend. Ten fixed C01–C10 cameras and four W01–W04 player-height views cover the room. Final repeat renders are in production/renders/final. The live Electrical Blender window is separate from Turbine; its MCP lease was released. Viewport preparation changed only the current UI, without resaving the verified artifact.

architecture/floorplan.svg and floorplan.png show the dimensioned room. architecture/CONNECTIONS.md and interface.json define matching identifiers, positions, normals, elevations, opening sizes, proposed transforms and ownership. architecture/EQUIPMENT_CHECKLIST.md maps specification functions to authored machines and engine hooks.

## Integrate without rebuilding neighbors

- Use local metres, +Y inward from D01 at (0,0,0), +Z up.
- Proposed Electrical origin in Turbine coordinates: (0,25.45,0), Rz0. Electrical D01 outer face y−0.25 meets saved Turbine reveal y25.20. U01 outer bus face matches its 0.4 × 0.3 m input at z3.88.
- Proposed Waste origin in Electrical coordinates: (0,16.97,0), Rz0. Its measured 0.32 m front wall meets Electrical exterior y16.65. Owned seam reaches Waste floor without moving Waste.
- D01/D02 remain 2.4 × 2.7 m; Waste receiving opening is 3.0 × 3.2 m. P03 is internal, 2.4 m wide along Y and 3.2 m high.
- U02 outgoing facility distribution and U03 external backup supply remain unbound. Do not connect them to an invented neighboring socket.

## Player and machine operation

Static 0.60 m body-envelope sweeps sample 758 positions over six approach/service routes. Protected main corridor is 2.4 m wide. Transformer guard has two 1.52 m hinged leaves: measured minimum world X during opening is 1.6145 m, beyond the central aisle edge x1.2. Keep main route free during interactions. Dynamic carrying, collider skin, animated mechanisms and engine navmesh remain untested.

The required turbine isolation, feeder load shedding, reserve priority, manual transfer, reserve service, portable input and repair controls have named hooks. The scene represents physical mechanisms and visible states; host electrical simulation, shared reserve economy, incidents, damage/repair consequences, audio, interaction logic, network state and animation interlocks are engine work. MEDICAL priority maps to OCRU reanimation. No electrical rating or certification is inferred from shapes or generated text.

## Source and recovery

The reproducible pipeline is build_room.py (factory-empty original shell and full_hall.py assemblies), followed by final_adjustments.py (floor value, lighting fill, W02 framing and curve-end caps). run.ps1 -Mode full runs both and then renders through the shared GPU gate. E01–E05 source receipts and failed/interim checks remain available; the inherited S-series slice is historical, not the delivered full room. Private runtime/cache files and Blender backup files are ignored.

All materials are procedural. Bfont Regular uses Blender's builtin font; the generic MCP dependency audit incorrectly resolves its <builtin> sentinel as a disk path and reports it missing. Raw evidence is retained. Saved glyph geometry and cold images verify availability. Open-mesh inventory is retained and classified: surface wear sheets, font tessellation and swept-curve tessellation, not an unreported shell opening.

## Remaining limits

Waste is still a partial receiving slice, with a measured 2 mm threshold lip. Reciprocal global placement is proposed, not accepted whole-map traversal. Fuel Corridor and external utility routing are integrator-owned. This is local integration readiness, not final whole-map polish or end-to-end facility validation.

