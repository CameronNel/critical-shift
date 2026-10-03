import json, hashlib, pathlib, datetime
from PIL import Image

root = pathlib.Path('/workspace/critical-shift')
dock = root/'sections/facility-assembly/sources/compliance-dock'
production = dock/'revamp/production'
evidence = production/'critics/full-c05-technical'
source_sha = 'cf5b4c12c6567b142a060c2a8878e767ef001d192933d9fa9c08c0e61257d035'
renderer_sha = '9993f999e0eddef5d3c106591728c665647cc49364e44199253780cb9bc89c57'
def sha(p):
    with open(p,'rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()
def save(name, obj):
    (evidence/name).write_text(json.dumps(obj,indent=2)+'\n')

images=[]
batches=[]
for batch, count, kind in [('full-cycle-05',27,'beauty'),('full-cycle-05-uv',4,'supplemental UV'),('full-cycle-05-uv-standard',4,'standard UV'),('full-cycle-05-neutral',4,'standard neutral')]:
    folder=production/'renders'/batch
    m=json.loads((folder/'manifest.json').read_text())
    assert m['complete'] and len(m['shots'])==count
    assert m['source_sha256']==source_sha and m['renderer_sha256']==renderer_sha
    batches.append({'batch':batch,'count':count,'source_sha256':m['source_sha256'],'renderer_sha256':m['renderer_sha256'],'manifest_sha256':sha(folder/'manifest.json'),'complete':True,'cold_open':m['cold_open']})
    for shot in m['shots']:
        p=folder/(shot['id']+'.png')
        actual=sha(p)
        assert actual==shot['image_sha256']
        with Image.open(p) as im: dims=list(im.size)
        assert dims==[1067,600]
        note='Individually inspected at original resolution; no additional technical pixel defect assigned.'
        if shot['id'] in ['C06_CART_GATE_G1','HERO_SCANNER','HERO_CARGO']:
            note='G1 leaf 1 black bay fields corroborate native coplanarity where visible; same construction persists in supplemental UV.'
        if kind=='standard UV': note='Original-resolution checker inspected; no additional UV scale defect assigned.'
        if shot['id']=='C07_OFFICE_INTERIOR': note+=' Desk paper layering visually inspected; ink exposure independently ray-checked against all overlapping paper and all local meshes.'
        images.append({'path':str(p.relative_to(root)),'kind':kind,'id':shot['id'],'sha256':actual,'matches_manifest':True,'source_sha256':source_sha,'dimensions':dims,'opened_original':True,'observation':note})
folder=production/'renders/spawn-reference'
m=json.loads((folder/'reference-provenance.json').read_text())
assert m['source_sha256']=='9635f41aec585768285317399af9d6a3943411a66e20e2e3d96b05ad86dcfa40'
for entry in m['images']:
    p=folder/entry['name']; actual=sha(p); assert actual==entry['sha256']
    with Image.open(p) as im: dims=list(im.size)
    assert dims==[1280,720]
    images.append({'path':str(p.relative_to(root)),'kind':'approved spawn reference','id':p.stem,'sha256':actual,'matches_manifest':True,'source_sha256':m['source_sha256'],'dimensions':dims,'opened_original':True,'observation':'Individually inspected approved spawn reference at original resolution; reference provenance is reused capture, not a new acceptance render.'})
assert len(images)==43
save('image-audit.json',{'count':43,'beauty':27,'standard_diagnostics':8,'supplemental_diagnostics':4,'approved_spawn_references':4,'all_opened_original':True,'all_hashes_match':True,'batches':batches,'images':images})
protected=json.loads((evidence/'protected-hashes-start.json').read_text())
for path,item in protected.items():
    actual=sha(root/path); assert actual==item['expected_sha256']
    item.update({'sha256':actual,'matches':True})
save('protected-hashes-end.json',protected)
native=dock/'module_overhaul_R1.blend'
assert sha(native)==source_sha
recipes=json.loads((evidence/'recipe-hashes.json').read_text())
for path,item in recipes.items():
    actual=sha(dock/path); assert actual==item['expected']; item.update(actual=actual,matches=True)
save('recipe-hashes-end.json',recipes)
g1=json.loads((evidence/'g1-interface-analysis.json').read_text())
report={
 'review':'fresh independent full-cycle-05 technical critic', 'category':8, 'category_name':'Technical hygiene, reproducibility, performance hygiene, no critical defects',
 'score':92, 'threshold_strictly_greater_than':93, 'verdict':'FAIL', 'critical_defect_count':1,
 'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'native':str(native.relative_to(root)), 'native_sha256':source_sha, 'scene':'COMPLIANCE_EDIT_LOCAL','blender':'5.2.2 LTS','threads_per_critic_process':1,
 'critical_defects':[{'id':'G1-01','severity':'critical','description':'Two pressed bays on G1 leaf 1 have exposed front faces exactly coplanar with the 40 mm parent panel; visible black fields persist in beauty and supplemental UV.',
 'panel_front_y_m':6.980000019073486,'panel_rear_y_m':7.019999980926514,'bay_front_y_m':6.980000019073486,'bay_rear_y_m':6.985000133514404,'bay_penetration_m':0.005000114440917969,
 'coincident_exposed_area_m2':sum(b['front_face_area_m2'] for b in g1 if b['leaf']==1),'material':'CD | wear','witnesses':[b for b in g1 if b['leaf']==1],
 'repair':'Seat each bay back on its own measured panel front and carry captive fixings; preserve inherited matrices. Independently remeasure and rerender repaired source.'}],
 'other_measured_caveats':[
 {'id':'REG-01','severity':'major evidence deficiency','description':'Six inherited support witnesses hit target floor but fail actual assembly geometry within 5 mm: P2 contacts 0/1 and D2 contacts 0/1 have no child hit; D1 contacts 0/1 first reach leaf seal 40.00008 mm above floor. Actual jamb feet do reach floor. Target-only rays cannot establish those six witnesses.'},
 {'id':'ROUTE-01','severity':'inherited interface discrepancy','description':'Inherited G1 pedestal head intrudes approximately 60 mm into nominal R1 ±0.6 m straight reservation; baseline bounds identical. No unobstructed nominal 1.2 m route or runtime opened-door route certified.'},
 {'id':'UV-01','severity':'export caveat','description':'Unused retained UVMap layers have 32202 zero-area faces. Active physical/fabric charts have none. Physical charts intentionally overlap and are not bake/lightmap atlases.'},
 {'id':'MESH-01','severity':'authoring caveat','description':'120 meshes retain boundary edges; open tube/curve and planar details were not certified watertight collision solids.'}],
 'independent_native_results':{'local_objects':1321,'mesh_objects':1096,'font_objects':53,'empty_objects':137,'light_objects':23,'camera_objects':12,'evaluated_triangles_including_fonts':381032,'material_submeshes':1150,'local_material_families':36,'planning_limits':[450000,1150,36],'planning_targets_met':True,'submesh_and_material_headroom':0,'relative_libraries_resolved':25,'packed_present_images':119,'inherited_objects_retained':1077,'inherited_matrix_changes_over_1e_6':0,'support_assemblies':45,'target_anchor_rays_hit':92,'reverse_geometry_witnesses_within_5mm':86,'manifest_glyph_vertices':4249,'manifest_buried_vertices':0,'manifest_clearance_m':0.001000046730041504,'desk_glyph_vertices':816,'desk_buried_or_occluded_vertices':0,'desk_top_paper_clearance_m':[9.98377799987793e-05,0.00010007619857788086],'physical_UV_meshes':1096,'maximum_relative_metric_edge_error':0.0064998,'exact_whole_object_geometry_duplicates':0,'degenerate_faces':0,'nonfinite_vertices':0,'inverted_closed_meshes':0,'protected_inputs_match':True,'recipe_font_license_hashes_match':True},
 'nested_interface_evidence':['Scanner 12 pod seats and optic collars plus 18 service-cover samples independently checked.','Cargo lifting stems, display edge capture/apertures, collar side contacts and recessed roof bridge independently checked.','Custody emitter 15-sample outgoing grid clear; actual diffuser approximately 3 mm behind.','Four P2 carriage units actual track/leaf contacts, journal/bore/groove/retaining clip radii and axial engagement checked.','Key glazing ledges and hook/back-web seats checked.','All three G1 parent/front/bay/fixing interfaces measured.','Manifest fonts and handover/incident fonts ray-checked; desk test includes all overlapping papers and every local mesh.'],
 'reproducibility_scope':'Independent fresh-process native open and resolved resources; current recipes/font/license association hashes verified. Author build was not run. Remote GitHub cold-source evidence was supplied by root and was not independently reproduced by this critic; no cold-render equivalence claimed.',
 'unverified_runtime':['FPS','engine draw calls','physics and collision bindings','navigation and opened-door/cart trajectories','body dragging turn envelopes','networking','sound','Unity material equivalence'],
 'limitations':['No full author recipe rebuild under frozen read-only instruction.','No independent remote checkout or cold render comparison.','No historical cycle-count or final-two-cycle stability certification.','Source planning counters are not runtime budgets.','Only category 8 assigned a score; no overall score or categories 1–7 assigned.'],
 'actual_images_opened':images,'image_count':43,'all_image_hashes_match':True,
 'raw_evidence_directory':str(evidence.relative_to(root)),
 'raw_evidence_files':['native_probe.py','native-probe.json','native-probe-full.log','nested_probe.py','nested-probe.json','nested-probe.log','nested-g1-probe.log','g1-interface-analysis.json','p2-journal-analysis.json','contact_uv_probe.py','contact-uv-probe.json','contact-uv-probe.log','contact-uv-desk-probe.log','image-audit.json','protected-hashes-start.json','protected-hashes-end.json','recipe-hashes.json','recipe-hashes-end.json'],
 'production_source_changed':False,'all_critic_blender_processes_exited':True,'source_handles_released':True}
(production/'critics/full-c05-technical.json').write_text(json.dumps(report,indent=2)+'\n')
md=(evidence/'report-draft.md').read_text()
md+='\n## Actual image audit and release\n\nAll **43** images were opened individually at original resolution: 27 beauty images, 8 established standard diagnostics, 4 supplemental UV views and 4 approved-spawn references. Every image hash matches its batch manifest/provenance. All 39 cycle05 images associate with the exact frozen f11 native and renderer SHA `'+renderer_sha+'`. Diagnostic manifests are complete; they are authored renderer evidence with `cold_open=false`, not cold-render equivalence. Standard UV and neutral continuity views cover C05 conveyor, C07 office, HERO_TROLLEY and HERO_UTILITIES. The original-resolution standard checkers reveal no further assigned UV defect. Detailed paths, hashes, dimensions and observations are in `full-c05-technical/image-audit.json` and the JSON report.\n\nThe end-of-review native, six recipe/font/license and five protected-input hash checks all match their released/start values. All critic Blender processes have exited and all source handles are released. Root may begin the repair after other consumers release.\n\n'
md+='| Batch | Actual images opened | Resolution |\n|---|---|---|\n'
for kind in ['beauty','standard UV','standard neutral','supplemental UV','approved spawn reference']:
    entries=[i for i in images if i['kind']==kind]
    md+='| '+kind+' | '+', '.join(i['id'] for i in entries)+' | '+str(entries[0]['dimensions'][0])+' × '+str(entries[0]['dimensions'][1])+' |\n'
(production/'critics/full-c05-technical.md').write_text(md)
print(json.dumps({'score':92,'verdict':'FAIL','critical':1,'images':len(images),'native_sha256':sha(native),'source_handles_released':True}))
