# C80 crane identity geometry and bounded carry review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle80/hall_final.blend`  
**SHA-256:** `ba9c8d99b05a79a6c91ecb44750c15280561cdea9fcdf845e0797defba30b051`  
**Disposition:** mount geometry and bounded C79 carry verified from the exact saved C80 blend. Current full-quality direct view50 confirms the complete readable marking and physical mount. Issue #119 remains open only until exact C80 main07 confirms the identifier in the required crane composition.

## Exact C79→C80 scene delta

The saved comparator `/workspace/scratch/reactor-refinement-cycle80/scene-delta.json` passes. It reports one changed existing object (`RH refine crane identity`), three additions (the nameplate, spacers, and fixing heads), no removals or unexpected changes, and 1,916 unchanged objects. The changed font retains the same text body, font size, extrusion, material, parent, and animation identity; its transform is moved to the newly mounted plate. The comparison covers per-object transforms, parents, render visibility, animation driver/action names, mesh geometry/material indices/smoothing, font attributes, material graphs, lights, and cameras. It does not compare dynamic action keyframes or every custom property.

This local crane-sign change does not modify the accepted C79 subjects. In particular, the new plate lies entirely within the retained bridge mesh’s world bounds: bridge x=`[-10.325,10.325] m`, y=`[4.10,5.10] m`, z=`[14.50,15.350] m`; plate x=`[-5.525,-2.875] m`, y=`[4.1948,4.2048] m`, z=`[14.90,15.18] m`. The small label also lies within those x/z bounds. The bridge body, track, wheels, roof panels, luminaires, gauges, valves, and all other subjects accepted in C79 are unchanged within the comparator’s declared scope. This supports carrying all 46 accepted C79 issue dispositions listed in the rolling map. It does not close any currently open criterion.

## Independent saved-C80 mount measurements

I opened the exact saved C80 blend in portable Blender 5.2.2 and probed the evaluated meshes without modifying the scene.

| Mesh | World-y bounds (m) | Vertices / faces | Non-manifold edges | Signed volume (m³) |
|---|---:|---:|---:|---:|
| `RH refine crane bridge identity plate PANEL` | 4.19479990–4.20480013 | 24 / 26 | 0 | +0.00741431 |
| `RH refine crane bridge identity spacers STEEL` | 4.20480013–4.25000000 | 64 / 40 | 0 | +0.0000184093 |
| `RH refine crane bridge identity fixings STEEL` | 4.19079971–4.19479990 | 64 / 40 | 0 | +0.00000289658 |

The four stand-offs bridge the plate back at y=`4.2048 m` to the actual bridge-web face at y=`4.25 m`. The heads’ rear face is flush with the plate front at y=`4.19479990 m`; there is no 2 mm penetration. The text is `CRANE C-01 / CAPACITY: SEE CERTIFICATE`, retains its 0.4 mm extrusion, and seats at the same y=`4.1948 m` face. The backing plate sits 0.2 mm ahead of the bridge rib-tip plane at y=`4.205 m`.

I independently ran the same BVH anchor check used in the support audit. All 12 registered contacts pass: four stand-off-to-bridge, four plate-to-spacer, and four fixing-head-to-plate contacts. Target-gap residuals are `9.35e-8–9.72e-8 m`; face-angle errors are `0–0.0198°`; nearest subject-surface distance is at most `2.4e-7 m`. These are finite anchors, not an all-pair collision proof.

## Parent motion and sampled sightlines

The text and all three added meshes are children of `R2 crane bridge crane OLIVE`. Their relative transforms against the bridge stayed exactly constant in 23 sampled frames (`1,31,61,91,121,150,181,211,241,271,300,331,361,391,421,450,481,511,541,571,600,750,900`); maximum sampled relative-matrix delta was `0`. The bridge action remains `R2 crane bridge crane OLIVEAction`.

Using the exact C80 saved scene, I sampled 101 front-glyph points in each of the main07 and main08 camera views at those 23 frames. All 46 camera/pose rows had all 101 points unobstructed. This is a finite sampled check, not continuous motion coverage and not final-image proof of legibility. The C80 saved audit also reports the mandatory main07 identity sightline clear (`101/101`) and its main02 sign regressions clear.

## Direct rendered identity evidence

Exact-C80 full-quality view50 (`50_crane_identity_mount.png`, 1280×720/96 maximum samples; image SHA-256 `acd32914746a23c06c312d2d77d52915d9714589c3253ac72aaf78e933f61cf1`) was independently reviewed. The entire `CRANE C-01 / CAPACITY: SEE CERTIFICATE` line is readable on the backing plate. Its ivory lettering is somewhat muted against charcoal but still legible; the nearby highlight does not wash it out. The supports and fixing heads read as a mounted assembly, with no visible floating edge, clipping, or text obstruction. This resolves the direct close-up portion of #119 only. Current full07 remains necessary to close the criterion in the room's crane view.

## Technical checks and limitations

The exact C80 package has all 13 scoped authoring checks passing and the separate control-room verifier passing. The saved audit records 191 signage records with zero blocked samples; 2,744 registered support contacts across 1,920 assemblies with zero failures; no empty registrations; and all 290 protected objects unchanged. These are bounded checks, not exhaustive all-vertex or all-pair testing.

The evidence supports the C79→C80 carry of 46 already accepted issues because the only changed retained object and three new objects are confined to the crane identity sign. The direct sign appearance is now confirmed at full quality; main07 remains open under #119. All ten required C80 main views and any mapped current detail/state views remain necessary for the issues they cover. No overall score or final acceptance is assigned here.
