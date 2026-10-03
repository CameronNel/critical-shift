"""Assemble the independent f06 technical review from read-only probes/pixel review."""
import json,hashlib
from datetime import datetime,timezone
from pathlib import Path
REPO=Path('/workspace/critical-shift')
R=REPO/'sections/facility-assembly/sources/compliance-dock'
P=R/'revamp/production'
O=P/'critics/full-c02-technical'
SHA='8d7588a5513a984a96c086e21fd12d3b38f65a51cf08dbae1464bb3b044934f7'
def read(f):return json.loads((O/f).read_text())
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
n=read('native-independent.json');b=read('bearing-and-normals.json');g=read('backing-and-consumed-fabric.json')
v=read('validator-independent.json');deps=read('dependency-and-protected-hashes.json')
beauty=read('beauty-image-verification.json');diagnostics=read('diagnostic-image-verification.json')
baseline=read('baseline-planning-counts.json');lintel=read('scanner-lintel-backing.json')
protected=[]
for item in deps['protected_inputs']:
    actual=digest(REPO/item['path'])
    protected.append(dict(item,actual_sha256=actual,matches=actual==item['expected_sha256']))
final_hashes={'native':digest(R/'module_overhaul_R1.blend'),'checkpoint':digest(P/'checkpoints/full-f06.blend'),
              'expected_source_sha256':SHA,'protected_inputs':protected}
final_hashes['source_unchanged']=final_hashes['native']==SHA and final_hashes['checkpoint']==SHA
(O/'final-integrity.json').write_text(json.dumps(final_hashes,indent=2)+'\n')
tarp=next(x for x in n['objects'] if x['name']=='Covered Trolley Draped Tarp')
fabric=tarp['consumed_uv_charts'][0]
rows={x['object']:x for x in g['backing_gap_witnesses']}
lintel_row=lintel['backing_gap_witnesses'][0]
critical=[
 {'id':'T8-C1','severity':'critical','surface':'Conveyor return belt','assembly':'Cargo Inspection Conveyor',
  'defect':'Exposed return slab has no real roller/end-wrap/frame bearing or lower support path.',
  'gap_m':rows['Conveyor return belt']['nearest_connected_surfaces'][0]['distance_m'],
  'witness':rows['Conveyor return belt']['nearest_connected_surfaces'][0],
  'views':['C05_CONVEYOR_LEAD_TUNNEL','HERO_CARGO'],
  'pixel_evidence':'Exposed black horizontal slab below conveyor frame in beauty and neutral C05; physical detachment established by native triangles/rays.',
  'fix':'Keep preserved parts/world poses and add a credible continuous return path/end wrap and bearing interface to existing supported conveyor geometry.'},
 {'id':'T8-C2','severity':'critical','surfaces':['Scanner status light '+str(i) for i in range(4)],'assembly':'Person Scanner Arch',
  'defect':'Four rear lens faces remain 5.9996 mm in front of the actual supported blue backing, without containment or connecting mount.',
  'gap_m':rows['Scanner status light 0']['nearest_connected_surfaces'][0]['distance_m'],
  'witnesses':[rows['Scanner status light '+str(i)]['nearest_connected_surfaces'][0] for i in range(4)],
  'views':['C04_SCANNER_APPROACH','HERO_SCANNER','C06_CART_GATE_G1'],
  'pixel_evidence':'Lenses are visible in scanner views, but a 6 mm rear gap is not reliably measurable from the beauty frame. Oriented +Y backing probes supply the decisive evidence.',
  'fix':'Add seated rear housings/mount bridges to the blue backing while preserving original lens world poses.'},
 {'id':'T8-C3','severity':'critical','surface':'Scanner lintel txt','assembly':'Person Scanner Arch',
  'defect':'Rear raised inscription surface is 7.0000 mm in front of Scanner lintel face, with no seated glyph backs or bridging mount.',
  'gap_m':lintel_row['nearest_connected_surfaces'][0]['distance_m'],
  'witness':lintel_row['nearest_connected_surfaces'][0],
  'views':['C04_SCANNER_APPROACH','HERO_SCANNER'],
  'pixel_evidence':'Inscription is present on the scanner head; image pixels alone do not resolve this rear gap. The actual glyph rear surface and opposed backing normal prove detachment.',
  'fix':'Back or seat the raised inscription against the actual scanner lintel face without changing the original text world pose.'}
]
noncritical=[
 {'id':'T8-N1','severity':'noncritical','surface':'Covered Trolley Draped Tarp','material':'CD | cotton',
  'defect':'Consumed CD_Fabric_Cut_1m is approximately 0.165 UV/m, inconsistent with the named one-metre chart/normalization claim; retained CD_Physical_1m is not the cotton shader input.',
  'consumed_chart':fabric,'views':['HERO_TROLLEY'],
  'pixel_evidence':'Actual consumed UV checker shows roughly six-times-larger checks on the drape. Island continuity follows the folds; beauty/neutral cloth remains coherent and matte.',
  'fix':'Correct actual chart/shader physical scale or explicitly document an intentional nonmetric fabric mapping; validate the consumed chart, not only the retained face audit.'},
 {'id':'T8-N2','severity':'noncritical','surfaces':['Skirting east','Skirting south east','Skirting south west','Skirting west'],
  'defect':'A few tiny coincident outer corner bevel triangles survive at south skirting joins. Most other coincident dado/wainscot faces are intentionally buried interfaces.',
  'witness_world':[6.79924393,0.00051133,0.05066667],
  'witness_normal':[0.70720816,-0.70700544,0.0],
  'method':'World triangle coincidence plus front/back other-surface probes; this witness has no covering other surface within 50 mm in either normal direction.',
  'pixel_evidence':'No discernible flicker or dominant duplicate-skin artifact in current fixed views. Runtime z-fighting remains untested.',
  'fix':'Trim/weld exposed corner seam faces in an allowed mesh construction repair before engine export.'}
]
views=[s['id'] for s in json.loads((P/'renders/full-cycle-02/manifest.json').read_text())['shots']]
full=['C05_CONVEYOR_LEAD_TUNNEL','HERO_CARGO','HERO_SCANNER','C06_CART_GATE_G1','C10_ROOF_SERVICES','HERO_TROLLEY',
      'C07_OFFICE_INTERIOR','DETAIL_CHECKIN','HERO_UTILITIES','WALL_OFFICE_FRONT']
spawn=['VALIDATE_Spawn','BRIEFING_INDIRECT','VALIDATE_LockerDoor','VALIDATE_Material_A']
unverified=[
 'Engine collision meshes, navigation, gameplay interaction, FPS, draw calls, shader portability and performance.',
 'Curved cart/body turns, moving-door swept collisions, handler space, ragdoll paths and structural load capacities.',
 'Completeness of authored circulation_solid classifications; inherited warning is conservative architectural inclusion, not a measured route obstruction.',
 'Sealed external access opening proof: authored sealed boundary, no current open geometric proof.',
 'Independent factory rebuild from the archived full recipe and final same-camera fresh-checkout cold-render pixel comparison. Native cold opening alone does not pass this gate.',
 'Owner art approval and map promotion; no authority to approve either.',
 'Minimum four complete full review cycles and final two materially stable cycles: this report covers current cycle 02 only.'
]
result={
 'schema_version':1,'review':'Compliance dock full cycle 02 independent technical critic','generated_utc':datetime.now(timezone.utc).isoformat(),
 'candidate':'full-f06','source':str(R/'module_overhaul_R1.blend'),'source_sha256':SHA,
 'category':{'number':8,'name':'Technical cleanliness, support contact, reproducibility and dependencies','score':90,
             'required_score_strictly_greater_than':93,'passes_score_gate':False},
 'verdict':'FAIL','critical_defect_count':len(critical),'visual_veto':False,
 'verdict_reason':'Three required-contact defects remain inside otherwise registered/support-anchored assemblies. A seven-check validator pass is not a pass for these exposed internal components.',
 'critical_defects':critical,'noncritical_defects':noncritical,
 'objective_evidence':{
  'planning_targets':{'triangles':450000,'material_submeshes':1150,'local_material_families':36},
  'baseline_counts':baseline,'current_counts':{'objects':1278,'triangles':433934,'material_submeshes':1119,'local_material_families':36},
  'source_planning_pass':True,'counts_are_runtime_budgets':False,
  'protected_input_hashes':protected,'preserved_world_pose_comparison':n['preserved_world_pose_comparison'],
  'independent_validator_summary':v['summary'],'independent_validator_checks':v['checks'],
  'registry':{'supported_roots':41,'anchors':87,'interpretation':'Metadata/selected anchors pass; does not establish every internal component bearing.'},
  'native_libraries':{'count':25,'all_exist':deps['all_exist'],'scope':'Only exact saved native library list; each separately SHA hashed in raw evidence.'},
  'local_geometry':{'local_scene_objects':1278,'linked_scene_objects':0,'linked_object_data':0},
  'images':{'count':119,'packed':sum(bool(x['packed']) for x in n['images']),
            'required_unpacked_missing':[x['name'] for x in n['images'] if not x['packed'] and not x['exists']]},
  'topology':{'zero_area_evaluated_triangles':0,'missing_consumed_uv_charts':[],'collapsed_consumed_uv_charts':[],
              'closed_normals_followup':'Centred float64 shell volumes clear all eight false negative float32 absolute-coordinate flags; raw follow-up is authoritative.'},
  'actual_contact_graph_groups':[{'root':x['root'],'geometry_members':x['tested_geometry_members'],
                                'disconnected_at_5mm':x['disconnected_from_support_at_5mm_contact_allowance']} for x in b['surface_connectivity']],
  'buried_interfaces':['Scanner column inset -1 and 1: centres and 12/12 sampled vertices inside corresponding solid columns, not exposed unsupported panels.',
                       'Gate motor/beam tower overlaps and most dado/wainscot/floor seams are intentional manufactured joints or buried interfaces.'],
  'oriented_bearing_witnesses':b['oriented_bearing_witnesses'],'webbing_drape_samples':b['webbing_to_drape'],
  'uv_distortion_threshold_invented':False},
 'pixels_consumed':{'beauty_overviews':views,'beauty_native_resolution':full,
                    'overview_method':'Five contact sheets, 533x300 per fixed frame, then named close views reopened at original 1067x600.',
                    'diagnostic_batches':diagnostics,'approved_spawn_originals':spawn,
                    'coverage_complete':len(views)==27,'no_full_verdict_from_counters_alone':True},
 'view_failures':[{'views':x.get('views',[]),'defect':x['id'],'evidence':x['pixel_evidence']} for x in critical+noncritical],
 'unverified':unverified,
 'independence':{'earlier_reports_or_scores_read':False,'scene_or_asset_writes':False,'subagents_spawned':False,
                 'blender_max_threads':1,'source_save_called':False,'source_read_handles_released':True},
 'final_integrity':final_hashes,
 'raw_evidence_directory':str(O)}
(P/'critics/full-c02-technical.json').write_text(json.dumps(result,indent=2)+'\n')
md=f'''# Compliance dock — full cycle 02 technical review

**Category 8: 90/100 — FAIL.** The required score is strictly greater than 93 and there must be zero critical defects. Three required-contact defects remain. No dominant visual veto is assigned by this technical critic; this is not an overall eight-category room score.

Reviewed current frozen **full-f06**, native `module_overhaul_R1.blend` and matching `checkpoints/full-f06.blend`, SHA-256 `{SHA}`. I did not consume previous critic reports/scores. The native source was opened read-only with Blender 5.2.2 using one thread; no save occurred. Every Blender process has exited and the source is explicitly released. Final source/checkpoint hashes are unchanged, and all five protected hashes match.

## Critical defects

1. **T8-C1 — `Conveyor return belt`: no real return/bearing path.** This exposed lower black slab is disconnected from the conveyor support graph. Its nearest supported surface is `Conveyor leg 3.98_9.9`, **52.1775 mm** away: belt point `(4.07026720, 9.84899902, 0.42799997)` to leg `(4.01985979, 9.86247444, 0.42799997)`, with opposed side normals. No downward bearing, end wrap, lower roller bridge or closed-mesh burial connects it to the supported conveyor. Beauty `C05_CONVEYOR_LEAD_TUNNEL` and `HERO_CARGO`, plus neutral C05, expose the slab beneath the frame. Add a plausible connected return path/bearings while preserving the authorized original world poses. Evidence: `backing-and-consumed-fabric.json`, `bearing-and-normals.json`.

2. **T8-C2 — `Scanner status light 0–3`: four unseated lenses.** Each rear lens is **5.9996 mm** ahead of `CD | Joined Person Scanner Arch / blue`. Light 0 witness: rear `(0.77999997, 6.81000042, 1.81995678)` to backing `(0.78000021, 6.81599998, 1.81995618)`. Lens rear faces point approximately +Y and the backing normal is −Y; directed +Y rays meet the same actual backing. No containment or connecting housing was found. This exceeds the protocol's 5 mm contact allowance. The lenses are visible in `HERO_SCANNER`, C04 and C06, but the beauty pixels do not independently resolve a 6 mm rear gap; native geometry is decisive. Add seated rear housings/bridges without moving the preserved lenses. Evidence: `backing-and-consumed-fabric.json`.

3. **T8-C3 — `Scanner lintel txt`: detached raised inscription.** The rear glyph surface is **6.99997 mm** ahead of `Scanner lintel face`: `(0.48560831, 6.79299974, 2.76473212)` to `(0.48560828, 6.79999971, 2.76473212)`, opposed +Y/−Y normals. Directed backing rays and containment probes confirm no seated glyph backs or bridge. The original lintel is farther behind; this failure uses the nearest real face plate, not an AABB. C04/`HERO_SCANNER` contain the inscription, but native surface witnesses establish the small gap. Seat/back the lettering while preserving its world pose. Evidence: `scanner-lintel-backing.json`.

These are required geometric-contact failures under protocol §14.1, which states that a room cannot pass while a required contact check fails. A registered floor-supported assembly root does not establish the internal return belt, lens or lettering bearing.

## Noncritical defects and actual UV evidence

**T8-N1 — consumed trolley fabric units disagree with the one-metre claim.** `CD | cotton` consumes `CD_Fabric_Cut_1m` for colour/roughness and the connected weave bump. `CD_Physical_1m` remains a separate metric audit layer and is not this shader input. For `Covered Trolley Draped Tarp`, 5,696 consumed triangles have UV area **0.18059050** over **6.59318654 m²** of evaluated surface. Edge UV/m is min **0.14034**, p01 **0.14734**, median **0.16505**, p99 **0.17703**, max **0.17950**. The shader has no intervening mapping compensation; other cotton surfaces use approximately one UV/m. The actual consumed-chart `HERO_TROLLEY` checker visibly has about six-times-larger checks on the cover. The top island stays continuous across folds; original beauty and neutral cloth read as coherent matte fabric. This is a unit/metadata consistency defect, not an invented numeric distortion failure or a dominant cloth veto. Correct/document the intended units and inspect the active chart again. Evidence: `native-independent.json`, `backing-and-consumed-fabric.json`, current UV `HERO_TROLLEY.png`.

**T8-N2 — tiny coincident outer skirting seam skins.** The world-triangle screen finds four corner interface pairs, totaling 46 coincident triangle groups: east/south and east/north wainscot; east/south-east and south-west/west skirting. Most witnesses are buried by floor, wall, dado or skirting. A few outer skirting bevel triangles remain uncovered by another surface along either normal direction within 50 mm, e.g. `(6.79924393, 0.00051133, 0.05066667)`, normal `(0.70720816, −0.70700544, 0)`. These are local corner seam faces, not duplicated full objects. No visible flicker appears in current fixed views; runtime z-fighting is untested. Trim/weld the exposed seams in an allowed mesh construction repair. Evidence: `native-independent.json` world-triangle witnesses.

## Verified objective and construction evidence

| Check | Independent evidence and limit |
| --- | --- |
| Planning counts | Original: **1,077 objects / 297,672 tris / 992 submeshes / 24 materials**. Current: **1,278 objects / 433,934 tris / 1,119 submeshes / 36 local families**. Current planning targets 450,000 / 1,150 / 36 pass; these are authoring counts, not engine budgets or draw calls. |
| Original world poses | All 1,077 original objects present; no matrix element changed beyond 1e−6. Maximum element delta **1.2371e−7**. Construction repairs may alter evaluated geometry as authorized by the brief. |
| Bounds and interfaces | Actual perimeter face rays confirm X ±6.8, Y 0…15.8: clear spans **13.60000038 × 15.80000009 m**. Portal sampled widths pass: entry 2.400 m; staff front/rear 1.050 m; cart gate 1.860 m; support north return 1.550 m; scanner 1.220 m. Sealed external opening remains unverified. |
| Routes | R1/R2/R3 pass triangle-versus-oriented-prism and floor-support probes in declared open poses. R3 is correctly blocked by saved closed D1/D2 leaves. Static checks do not establish cart curves, moving sweeps or gameplay. |
| Registry | Independent run of the existing validator returns **7 checks PASS / 0 errors / 1 classification warning / 5 unverified**. **41 roots / 87 anchors** pass selected support checks, maximum positive anchor gap 0; tiny maximum penetration 1.1921e−7 m. This does not waive the three internal component failures above. |
| Gate machinery | Real triangle contacts connect tracks, carriages, towers, beam, drive and pedestal to supports. Pedestal head underside and column top meet at z=1. Motor/tower and beam/post overlaps are manufactured joints: rays that start inside the tower hit its far exit, not a gap. C06 pixels confirm seated construction. |
| Conveyor motor/control | Motor underside z=.535 meets mounting-plate top with opposed ±Z normals; plate connects to added supported steel brackets (nearest actual interface about **0.543 mm**). Control-panel underside meets the operator desk arm. The motor support path passes; the separate return slab does not. |
| Roof services | Supply top z=4.175 and return top z=4.125 meet the actual hanger undersides with opposed ±Z normals. Both hanger paths reach roof underside z=4.4; return hanger tip is within **0.477 µm**. C10 beauty shows the same supported construction. |
| Trolley fabric/webbing | Actual drape/bed triangles contact; webbing follows drape at twelve sampled folds with top-surface offsets **2.291–2.381 mm**, corresponding to strap thickness. Buckles/brackets/frame/casters have a connected geometric path. Beauty/neutral `HERO_TROLLEY` confirms seated fabric/straps. |
| Buried interfaces | Scanner inset −1/+1 centres and 12/12 sampled vertices lie inside their closed corresponding columns: these are buried inset geometry, not exposed floating panels. Intended gate overlaps and most architectural corner interfaces are not duplicate-skin failures. |
| Topology/normals | Zero exactly collapsed evaluated world triangles and no nonfinite consumed UVs, missing consumed charts or collapsed consumed UV triangles. Open text/cable/hem/welt surfaces have object-specific render purpose. Eight initial float32 absolute-coordinate signed-volume flags were cleared by centred float64 closed-shell volumes; no inverted-shell defect is asserted. |
| Dependencies/editability | Exact **25 native libraries** resolve and are individually hashed. **119 packed images** are present; no required unpacked image is missing. Legacy external image paths with packed pixels are not missing dependencies. Scene object/data edits are local. No repository-wide historical LFS availability claim is made. |

## Pixels consumed and view failures

All **27** labelled 1067×600 beauty files were verified against their current manifest SHA hashes and inspected in five contact sheets (533×300 per frame). I then reopened these ten at original resolution: C05, C06, C07, C10, `HERO_CARGO`, `HERO_SCANNER`, `HERO_TROLLEY`, `HERO_UTILITIES`, `DETAIL_CHECKIN`, `WALL_OFFICE_FRONT`. Both current four-view diagnostic batches were opened at original resolution: C05, C07, `HERO_TROLLEY`, `HERO_UTILITIES`, each in UV and neutral light. All eight diagnostic image hashes and resolutions match complete manifests with the same f06 source SHA. The checker renderer selects the fabric chart when present, so the trolley evidence actually consumes the shader's chart. Neutral office and utilities show seated furniture and wall mounts; they reveal no additional technical veto.

The four approved spawn originals were actually opened: `VALIDATE_Spawn`, `BRIEFING_INDIRECT`, `VALIDATE_LockerDoor`, `VALIDATE_Material_A`. They calibrate grounded fixture construction and restrained materials; this review does not assign the colour/art categories.

| View evidence | Technical finding |
| --- | --- |
| C05 beauty/neutral; `HERO_CARGO` beauty | Exposed unsupported return slab, T8-C1. |
| C04 / `HERO_SCANNER` / C06 scanner front content | Lenses and raised inscription are present; small rear gaps require native surface witnesses, T8-C2/C3. |
| `HERO_TROLLEY` consumed UV | Six-times-larger checker features support T8-N1; continuity through folds is preserved. |
| Remaining inspected fixed frames | No newly observed dominant technical visual defect. This does not override the native required-contact failures. |

## Unverified gates and integrity

Runtime collision/navigation, FPS/draw calls, interaction, moving swept paths, structural capacity and shader portability remain **UNVERIFIED**. The conservative architectural classification warning is not a measured route obstruction. Independent full factory-recipe rebuild and final same-camera fresh-checkout cold-render comparison were not performed/consumed by this critic; parent-reported transfer cold-open evidence does not substitute for my cold-render verdict. Owner art approval and map promotion remain **UNVERIFIED**. Minimum four full cycles and stable final two are pending gates; this is only cycle 02.

All five protected input hash comparisons pass; exact paths/digests are in `dependency-and-protected-hashes.json` and the repeated `final-integrity.json`. The native and full-f06 checkpoint remain SHA `{SHA}`. Source handles are released, no native save/asset/recipe/map changes were made, and only this critic's reports/raw probes were written. Full raw evidence is in `critics/full-c02-technical/`; structured category result is `critics/full-c02-technical.json`.
'''
(P/'critics/full-c02-technical.md').write_text(md)
print(json.dumps({'score':90,'verdict':'FAIL','critical_defects':len(critical),'source_unchanged':final_hashes['source_unchanged'],
                  'protected_match':all(x['matches'] for x in protected),'reports':['full-c02-technical.md','full-c02-technical.json']}))
