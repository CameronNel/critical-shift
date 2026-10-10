# C82 rolling 140-item evidence map

**Candidate:** `/workspace/scratch/reactor-refinement-cycle82/hall_final.blend`  
**SHA-256:** `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36`  
**Status:** independent review in progress. 51 prior accepted rows are bounded carries; #16 and #30 are accepted from mixed C79/C80 gauge panels under exact cumulative deltas; #113 is accepted from exact C79 main08. Current C82 evidence additionally accepts #1, #2, #3, #5, #6, #10, #38, #56, #71, #112, #124, and #140 (the last is finite technical QA only). #112 uses the full-quality C80 lower splice plus C82 upper splice under the exact C80→C82 delta. #136 is accepted as a bounded C79 material-response carry. 77 rows remain pending or partial, including 3 partial rows. No overall score or area scores are assigned.

**Carry review:** [LUNA_C82_BOUNDED_CARRY_REVIEW.md](LUNA_C82_BOUNDED_CARRY_REVIEW.md). **Geometry review:** [LUNA_C82_DOOR_GEOMETRY_REVIEW.md](LUNA_C82_DOOR_GEOMETRY_REVIEW.md).

## Current C82 accepted evidence

- #1/#6/#10: exact C82 full-quality main10 shows the MAIN ACCESS header, COOLANT / POWER board, and RESERVE POWER A plaque clear; see [west wall sign review](LUNA_C82_MAIN10_SIGN_ACCEPTANCE.md).
- #2/#3/#5: exact C82 main09 plus bounded W4 trim contact geometry; see [north wall sign review](LUNA_C82_VIEW09_WALL_SIGNS_ACCEPTANCE.md).
- #56: native C82 view43 plus six sampled stool-foot contacts; see [stool review](LUNA_C82_VIEW43_STOOL_ACCEPTANCE.md).
- #71: native C82 view34 plus the saved annular channel depth; scope is the pool-ring trench, not every drain; see [drainage review](LUNA_C82_VIEW34_ANNULAR_DRAINAGE_ACCEPTANCE.md).
- #112: full-quality C80 lower splice 51 and C82 upper splice 53 together show both six-bolt splice plates; the exact C80→C82 delta leaves splice geometry, lighting, materials, and cameras unchanged. See [splice acceptance](LUNA_C82_SPLICES_112_ACCEPTANCE.md).
- #124: C82 views54–57 and bounded contact/topology probes; see [door hardware acceptance](LUNA_C82_VIEW57_DOOR_HARDWARE_ACCEPTANCE.md).
- #140: all14 current finite checks plus separate CR verification; see [finite geometry QA disposition](LUNA_C82_GEOMETRY_AUDIT_140_ACCEPTANCE.md). It is not an exhaustive collision certificate.
- #136: bounded C79 full01/full02 carry under the exact C79→C82 delta; see [material-family response review](LUNA_C82_MATERIAL_FAMILY_RESPONSE_CARRY.md).

## Technical gate and delta

- C82 checks: `/workspace/scratch/reactor-refinement-cycle82/checks.json` (14/14 pass). Separate control-room verifier: `/workspace/scratch/reactor-refinement-cycle82/control-room-check.log` (PASS).
- Exact C80→C82 scene delta: `/workspace/scratch/reactor-refinement-cycle82/scene-delta.json`. Six door-hardware STEEL meshes changed; 1,914 objects unchanged, no additions/removals/unexpected changes.
- Current source-bound geometry test for #124: [probe](LUNA_C82_DOOR_GEOMETRY_PROBE.py), [raw log](LUNA_C82_DOOR_GEOMETRY_PROBE.log), [summary](LUNA_C82_DOOR_GEOMETRY_PROBE_SUMMARY.json). All36 bearing samples, all30 joints, all6 topology checks pass. Current pixels now pass; see `LUNA_C82_VIEW57_DOOR_HARDWARE_ACCEPTANCE.md`.
- Bounded cold reconstruction comparison: [C82 cold door-geometry review](LUNA_C82_COLD_DOOR_GEOMETRY_REVIEW.md). Current and cold samples agree for the six door meshes, but the separately reported exact-array comparator mismatch and cold support gate are not waived here.

## Historical gauge evidence and preserved partials

- #16/#30: all16 native panels are independently reviewed across the14-panel C79 manifest and C80 panels07/08. They are accepted as bounded mixed-source carries only; image paths, hashes, source hashes and both exact cumulative deltas are in `LUNA_C82_DISPOSITIONS.json` and `LUNA_C82_MIXED_SOURCE_GAUGE_ACCEPTANCE.md`. Panels01/13 are marginal but readable; no panel is labeled a C82 render.
- #42: exact C80 P-10 native view18 is preserved at `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c80/p10/18_secondary_p10_casing.png` (SHA `e96ec2bd9b9522eb763ea0aa159b889be4c7362438f2f0161e4557c257352aa1`); issue42 is already among the 50 bounded carries.
- #112: exact C80 lower-splice view51 (SHA `43a5c45b33dd7e3cc71fe41aace4c3ac080d2407f1344dd466886ecd765d7659`) plus C82 upper-splice view53 (SHA `312c067e6b35ab5e3eb8fa93a1d7a1ef3d30bdb65a707ce9f4596e99b5900e41`) now accept both splice levels; see `LUNA_C82_SPLICES_112_ACCEPTANCE.md`.

## All 140 issue dispositions

| ID | Area | Issue | Status | Evidence note |
|---:|---|---|---|---|
| 1 | signage | MAIN ACCESS header lettering buried | accepted current C82 | Full-quality main10 shows the complete header lettering clear; see `LUNA_C82_MAIN10_SIGN_ACCEPTANCE.md`. |
| 2 | signage | FUEL HANDLING header lettering buried | accepted current C82 | Full-quality main09 shows the header legible and unobstructed; see `LUNA_C82_VIEW09_WALL_SIGNS_ACCEPTANCE.md`. |
| 3 | signage | Unsupported orange trim below transfer columns | accepted current C82 | Full-quality main09 plus bounded W4 flange/contact geometry: the strip starts at the transfer lintel and bears on the front flange; exact C80→C82 delta leaves it unchanged. |
| 4 | signage | Emergency-control legend inside pedestal | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 5 | signage | CONTAINMENT board obstructed | accepted current C82 | Full-quality main09 shows the board clear in the intended north-fuel view. |
| 6 | signage | COOLANT / POWER board obstructed | accepted current C82 | Full-quality main10 shows the board face and status segments without overlap; see `LUNA_C82_MAIN10_SIGN_ACCEPTANCE.md`. |
| 7 | signage | REACTOR STABILITY board obstructed | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 8 | signage | EMERGENCY COOLING plaque obstructed | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 9 | signage | STANDBY GENERATOR plaque obstructed | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 10 | signage | RESERVE POWER A plaque obstructed | accepted current C82 | Full-quality main10 shows the right-wall plaque and text clear; see `LUNA_C82_MAIN10_SIGN_ACCEPTANCE.md`. |
| 11 | signage | Duplicate control-bank headings | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 12 | signage | Faint obstructed WATCH THE GREEN instruction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 13 | signage | Overhead EXIT contrast | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 14 | signage | Wall EXIT contrast | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 15 | signage | D1/D2 identifiers subdued | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 16 | signage | Gauge information readability | accepted, bounded mixed-source carry | All16 full-quality native panels reviewed (14 C79, 2 C80); exact C79→C82 and C80→C82 deltas show gauge views/subjects unchanged. Image lineage remains historical; panels01/13 are marginal but legible. |
| 17 | signage | Switchgear channel identification | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 18 | signage | Pressure-vessel identification | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 19 | signage | Valve and circuit identification | pending current C82 evidence | Prior V-01/V-02 evidence retained; switchgear circuit labels remain open. |
| 20 | signage | Anonymous coloured label strips | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 21 | machinery | Turbine primary casing silhouette | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 22 | machinery | Turbine end cap construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 23 | machinery | Turbine coupling transition | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 24 | machinery | Turbine front guard construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 25 | machinery | Turbine base support construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 26 | machinery | Exhaust transition construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 27 | machinery | Stack duct section proportions | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 28 | machinery | Cabinet control grouping | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 29 | machinery | Cabinet access door construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 30 | machinery | Gauge housing depth | accepted, bounded mixed-source carry | All16 full-quality native panels show a raised rim/retainer or casing edge around each face; exact C79→C82 and C80→C82 deltas show gauge views/subjects unchanged. |
| 31 | machinery | Handwheel hub/spoke proportions | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 32 | machinery | Pressure vessel shell construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 33 | machinery | Paired vessel functional variation | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 34 | machinery | Vessel support construction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 35 | machinery | Level indicator mounts | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 36 | machinery | Blind pipe termination | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 37 | machinery | Valve body readability | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 38 | machinery | Pipe joint type distinction | accepted, current C82 image | Exact-C82 native steam-tap view17 (SHA `2e12007796333ae887fdb72f8d53927fd9d1d387a8ca38afd2b510bf026b7d53`) shows the saddle/neck, nipple/union and gauge connection together without a visible gap. See `LUNA_C82_VIEW17_STEAM_TAP_ACCEPTANCE.md`. |
| 39 | machinery | Pipe branch junctions | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 40 | machinery | Pipe support attachments | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 41 | machinery | Yellow caged machine identity | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 42 | machinery | Secondary equipment silhouettes | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 43 | props | Drum reinforcing hoops and proportions | confirmed open geometry defect | Historical full01 (C79) shows swollen rib profiles; exact C79→C82 delta leaves drums, materials and camera unchanged. Each raised band spans 105.6mm axially with 18.85mm projection. Requires narrowed rolled hoops and corrected-source pixels; see `LUNA_C82_DRUM_HOOP_FAILURE.md`. |
| 44 | props | Drum bung and lid construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 45 | props | Yellow drum fitting proportion | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 46 | props | Drum steel material response | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 47 | props | Drum identification | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 48 | props | Drum grouping and contact | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 49 | props | Cone silhouette | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 50 | props | Cone weighted base | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 51 | props | Cone coarse grime | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 52 | props | Portable barrier silhouette | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 53 | props | Barrier frame/support construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 54 | props | Bollard floor mounting | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 55 | props | Bollard cap/finish | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 56 | props | Stool construction | accepted current C82 | Native view43 shows seat/legs/foot ring; current audit has three passing floor anchors on each of two stools. |
| 57 | props | Containment tray construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 58 | floor | Puddle wet response | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 59 | floor | Puddle edges and shape | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 60 | floor | Puddle drainage relationships | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 61 | floor | Wet/oil/dirt separation | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 62 | floor | Physical slab joints | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 63 | floor | Slab material variation | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 64 | floor | Crack relief | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 65 | floor | Crack branch hierarchy | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 66 | floor | Route paint wear | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 67 | floor | White directional arrow shape | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 68 | floor | Route marking continuity | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 69 | floor | Rectangular drain construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 70 | floor | Circular cover seating | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 71 | floor | Drainage channel recess depth | accepted current C82, annular pool trench scope | Native view34 shows the ring trench recess; saved floor depth is z=−0.32m. It does not cover unrelated drains. |
| 72 | floor | Loose grille underside/contact | partial, current scope pending | Prior grille evidence retained only as context; current criterion remains pending. |
| 73 | floor | Equipment floor contact | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 74 | floor | Floor movement/wear pattern | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 75 | floor | Floor visual noise | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 76 | pool | Pool rim layer consolidation | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 77 | pool | Pool rim thickness hierarchy | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 78 | pool | Pool yellow marking repetition | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 79 | pool | Pool rim neutral material readability | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 80 | pool | Rail post terminations | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 81 | pool | Rail base attachment | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 82 | pool | Rail intersection joints | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 83 | pool | Pool gate construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 84 | pool | Pool lining joint depth | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 85 | pool | Pool wall port construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 86 | pool | Pool wall staining origins | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 87 | pool | Pool depth marking contrast | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 88 | pool | Water plane/depth readability | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 89 | pool | Pool control operating-face review | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 90 | pool | Pool service penetrations | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 91 | rods | Rod cluster primary hierarchy | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 92 | rods | Drive/absorber distinction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 93 | rods | Rod collar construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 94 | rods | Mechanical/status-light separation | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 95 | rods | Rod guide seating | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 96 | rods | Bank housing panel structure | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 97 | rods | Bank frame corner construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 98 | rods | Bank service access | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 99 | rods | Housing conduit entry | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 100 | rods | Controlled paired-bank variation | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 101 | rods | Bank suspension connection | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 102 | rods | Rod metallic roughness | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 103 | rods | Bank label/status hierarchy | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 104 | rods | Lower bank service identification | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 105 | rods | Housing louvre depth | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 106 | roof | Crane bridge silhouette | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 107 | roof | Crane end carriage/running gear | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 108 | roof | Trolley motor/drum construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 109 | roof | Crane track/support relationship | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 110 | roof | Girder section readability | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 111 | roof | Girder connection construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 112 | roof | Column splice construction | accepted, paired mixed-source views | C80 full-quality lower splice 51 + C82 full-quality upper splice 53 show both plates and six bolt heads; see `LUNA_C82_SPLICES_112_ACCEPTANCE.md`. |
| 113 | roof | Roof panel section depth | accepted, bounded C79 carry | Exact C79 full-quality main08 (SHA `1d1a5b45f28ab5a89aa22256595fbbb355ef3498e7132d47ddc9e1539c106cb2`) shows recessed roof-panel edges and section depth at native 1280×720. Cumulative C79→C82 delta confirms this roof geometry/material/camera is unchanged. See `LUNA_C82_ROOF_PANEL_DEPTH_CARRY.md`; #110/#111 remain open. |
| 114 | roof | Roof panel restrained variation | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 115 | roof | Cable/service type distinction | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 116 | roof | Cable termination check | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 117 | roof | Ceiling service diameter hierarchy | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 118 | roof | Roof fixture housing/mount | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 119 | roof | Crane identification/specification | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 120 | roof | Existing crane maintenance access readability | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 121 | walls | Concrete panel joint depth | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 122 | walls | Wall floor/plinth transition | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 123 | walls | Door leaf construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 124 | walls | Door operating hardware | accepted current C82 | Views54–56 show placement on all six leaves; view57 resolves handle/stem/fastener/hinge construction; bounded saved-mesh seating/joint checks pass. |
| 125 | walls | Door return staining | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 126 | walls | Circular vent depth | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 127 | walls | Upper pane frame/recess variation | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 128 | walls | Upper ledge/bracket supports | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 129 | walls | Wall box mounting/construction | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 130 | walls | Clock quantity/readability | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 131 | walls | Text curve resolution/spacing | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 132 | walls | Doorway task-lamp identity | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 133 | holistic | Neutral wall illumination | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 134 | holistic | Neutral roof illumination | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 135 | holistic | Dark machinery light separation | accepted, bounded carry | Prior independent acceptance preserved under exact C80→C82 delta; see carry report for original source/image lineage. |
| 136 | holistic | Material family response distinction | accepted, bounded C79 carry | Full-quality C79 views01/02 show separated concrete, painted-metal, bare-metal and rubber responses; exact C79→C82 delta preserves those materials, lights and cameras. See `LUNA_C82_MATERIAL_FAMILY_RESPONSE_CARRY.md`. |
| 137 | holistic | Material-specific wear | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 138 | holistic | Focal hierarchy | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 139 | holistic | Physical signage visibility audit | pending current C82 evidence | Await exact-C82 evidence; no criterion-specific C82 visual acceptance yet. |
| 140 | holistic | Geometry support/intersection audit | accepted current finite-QA scope | 2,804 registered samples/1,956 assemblies/26 owner groups; zero submitted contact/sign failures or empty registrations; 14 scoped checks + separate CR pass. Finite inventory only; not exhaustive all-pair collision coverage. |

## Score

No score assigned yet; unresolved criteria still need evidence and review. Final thresholds remain at least 90 overall and at least 85 in each of the nine areas: signage, machinery, props, floor, pool, rods, roof, walls, holistic.
