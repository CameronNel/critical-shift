# Electrical Room — complete E05 scene

Original detailed Critical Shift Electrical Room, with strict Valorant art direction and no teal. Open **blender/electrical_room.blend**. See **HANDOFF.md** for measured connection proposals, equipment, routes, source reproduction and remaining engine/neighbor work.

- Main hall: 11 × 16.4 × 4.8 m; reserve bay: 2.8 × 4.4 × 3.6 m nominal.
- Six switchgear bays, guarded transformer, manual transfer/priority station, three reserve cabinets, portable input, repair bench and service cart.
- Dimensioned plan: architecture/floorplan.svg and floorplan.png.
- Exact local connection contract: interface.json and architecture/CONNECTIONS.md.
- Required functions: architecture/EQUIPMENT_CHECKLIST.md.
- Approved guidance and rejected concept history: art/concepts and production/critics.
- Ten fixed camera renders plus four player-height views: production/renders/final.
- Saved-file checks and cold evidence: production/validation/E05.

The saved geometry, source and cold fingerprints pass; all eight independent warm and cold visual categories score 91–94. Final cold visual approval is PASS. Render repeats are numerically stable, not pixel-identical; the exact-comparison failure and measured differences are retained.

## Reproduce

From the repository, use blender/run.ps1 -Mode full -Revision E05 -Samples 48. It runs the original factory-empty build, deterministic final art pass, then GPU-gated renders. The section uses Blender 5.2, procedural materials and builtin Bfont, without imported geometry or external texture dependencies. All GPU renders must use the shared facility-run/gpu_gate.py.

Validate the saved artifact with blender/validate_scene.py, walkthrough_audit.py and aperture_audit.py. cold_snapshot.py fingerprints separate cold opens; production/verify_package.py compares those fingerprints, source bytes and decoded render pixels. Do not infer visual approval from geometry checks.

Inherited S-series slice evidence and INHERITED_ documents are historical. Only Electrical is owned. Neighbor transforms are measured proposals; engine collision/navmesh, shared reserve simulation, interactions, sound and whole-map validation remain integration work.

