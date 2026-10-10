# C84 drum hoop review (#43)

**Candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**Candidate SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`  
**Current disposition:** Geometry pass; preview visual pass only. #43 remains open until exact-C84 full-quality view31 is reviewed.

## Geometry

The narrowed 18 mm × 6 mm bead profile passed the independent local shell/topology probe on C83. The C84 stage reports 4,992 moved profile vertices and 4,992 selected edge-sharp changes with the same measured profile dimensions. My exact-C84 probe independently finds, for all thirteen drums, 48 vertices and 48 circumferential edges at each of the eight expected levels, with all 4,992 profile-ring edges marked sharp and no radial/profile connector between levels marked sharp. The C82→C84 scene delta confines changes to the five drum material meshes. Probe result: `LUNA_C84_DRUM_EDGE_PROBE.json` and `.log`; local manifold/area/volume evidence: `LUNA_C83_DRUM_LOCAL_SURFACE_PROBE.json` and `.log`.

All thirteen connected lathed bodies remain closed manifold components in that bounded test: 962 vertices, 1,968 edges, 1,008 faces, no boundary or >2-face edges, no degenerate polygon below `1e-12 m²`, and positive signed volume. The ring-face shoulders and crowns have outward-facing normals. C84’s edge flags remove the C83 shoulder-smear defect while retaining the measured bead profile.

## Visual preview

C84 preview [`31_props_drum_group.png`](/workspace/scratch/c84-drum-preview/31_props_drum_group.png) has SHA-256 `94b74e1339dd55d6e098f510c4e5e7a033df52599caef7b89c670067e822569b`. This is a 480×270, 16-sample preview with unchanged exposure. Compared with the C83 preview, the broad tonal smears are gone; the hoops now read as narrow crisp rolled beads while the shells, tops, and bungs remain visually distinct. I approve this preview framing/geometry direction.

The preview is not final acceptance: #43 still needs the exact-C84 1280×720 full-quality view31 so the metal edge response, hoop readability on all drum colors, and overall detail can be judged at final resolution.
