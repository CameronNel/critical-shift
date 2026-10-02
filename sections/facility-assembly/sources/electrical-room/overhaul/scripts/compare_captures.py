"""Verify cold-repeat provenance and report pixel differences; requires Pillow11.3."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

p=argparse.ArgumentParser()
p.add_argument('--previous',required=True);p.add_argument('--cold',required=True)
p.add_argument('--out',required=True)
transition=p.add_mutually_exclusive_group()
transition.add_argument('--legacy-compatibility-receipt',help='Explicit input/output hash receipt for the unused-ID-only transition; omit for strict same-source cold verification')
transition.add_argument('--visual-repair-receipt',help='Exact staged hash/signature receipt for declared door/contact and surface changes; this is a visual iteration, not a cold repeat')
a=p.parse_args();prior=Path(a.previous);cold=Path(a.cold)
left=json.loads((prior/'manifest.json').read_text())
right=json.loads((cold/'manifest.json').read_text())
failures=[];results=[]
same_source=left['source_sha256']==right['source_sha256']
mode='same_source_cold_repeat'
if a.legacy_compatibility_receipt:
    receipt=json.loads(Path(a.legacy_compatibility_receipt).read_text())
    mode='explicit_legacy_material_id_transition'
    if (left['source_sha256']!=receipt['input_sha256'] or right['source_sha256']!=receipt['output_sha256']
        or not receipt['visible_material_assignments_unchanged']):failures.append('source transition does not match compatibility receipt')
elif a.visual_repair_receipt:
    receipt=json.loads(Path(a.visual_repair_receipt).read_text())
    mode='declared_visual_finish_iteration'
    valid_hashes=left['source_sha256']==receipt['input_sha256'] and right['source_sha256']==receipt['output_sha256']
    if receipt.get('repair_kind')=='door_contact_and_surface_response':
        door=receipt['door_stage'];surface=receipt['surface_stage']
        surface_changes=surface['declared_changes']
        floor_support=surface_changes.get('floor_contact_support',{})
        floor_registration=((surface_changes['new_registered_service_assemblies']==0
                             and surface_changes.get('new_floor_polygon_layer_omitted')
                             and surface_changes.get('localized_floor_contacts')==0)
                            or surface_changes['new_registered_service_assemblies']==1
                            or (surface_changes['new_registered_service_assemblies']==5
                                and len(floor_support.get('moved_contacts',[]))==4
                                and floor_support.get('new_registered_support_roots')==4
                                and floor_support.get('remaining_original_floor_contacts')==2))
        bounded=(door['input_sha256']==receipt['input_sha256'] and door['output_sha256']==surface['input_sha256']
                 and surface['output_sha256']==receipt['output_sha256']
                 and door['all_other_matrices_geometry_material_assignments_visibility_lights_unchanged']
                 and len(door['retired_original_decorative_wear'])==104 and door['distinct_leaf_histories']==4
                 and door['new_supported_contact_assemblies']==8 and surface['original_geometry_matrices_unchanged']
                 and len(surface['declared_changes']['material_profiles'])==5
                 and floor_registration)
    elif receipt.get('repair_kind') in {'service_floor_contact_height_repair','service_floor_contact_exposure_repair'}:
        changes=receipt['declared_changes']
        bounded=(receipt['all_other_matrices_geometry_material_assignments_visibility_lights_unchanged']
                 and len(changes['moved_contacts'])==4
                 and all(abs(v['vertical_shift_m']-.0013)<1e-6 for v in changes['moved_contacts'])
                 and changes['new_registered_support_roots']==4
                 and changes['remaining_original_floor_contacts']==2
                 and changes['existing_floor_root_restricted_to_its_two_contacts'])
        if receipt['repair_kind']=='service_floor_contact_exposure_repair':
            bounded=bounded and changes['all_contours_clear_of_insulating_mats'] and len(changes['exposed_surface_probes'])>=32
    elif receipt.get('repair_kind')=='retire_new_floor_polygons':
        expected={'EOH | Individual service floor contact '+str(i) for i in range(6)}
        expected.add('EOH | Localized service plinth contacts')
        bounded=(receipt['all_other_matrices_geometry_material_assignments_visibility_lights_unchanged']
                 and set(receipt['removed_new_object_names'])==expected
                 and receipt['removed_new_meshes']==6 and receipt['removed_support_roots']==1
                 and receipt['unused_new_material_removed'])
    elif receipt.get('repair_kind') in {'service_lead_and_vision_finish','lead_vision_and_reserve_service_finish'}:
        lead=receipt.get('lead_stage',receipt)
        changes=lead['declared_changes']
        expected={'EOH | '+n+s for n in ['Coiled test lead','Lead reel hook','Test lead hanging tail',
                                       'Lead terminal insulated grip','Resting test lead'] for s in ['', '.001']}
        bounded=(lead['all_other_matrices_geometry_material_assignments_visibility_lights_unchanged']
                 and set(changes['changed_existing_mesh_objects'])==expected
                 and len(changes['measured_winding_supports'])==8
                 and all(abs(v['support_gap_m'])<.0015 for v in changes['measured_winding_supports'])
                 and changes['trolley_jack_and_probe_endpoints_preserved']
                 and len(changes['measured_trolley_endpoints'])==2
                 and all(max(v['endpoint_errors_m'])<1e-6 for v in changes['measured_trolley_endpoints'])
                 and lead['changed_material_definitions']==['EOH | Wired vision glass']
                 and lead['all_other_material_definitions_unchanged'])
        if receipt.get('repair_kind')=='lead_vision_and_reserve_service_finish':
            reserve=receipt['reserve_stage'];rc=reserve['declared_changes']
            bounded=(bounded and lead['input_sha256']==receipt['input_sha256']
                     and lead['output_sha256']==reserve['input_sha256']
                     and reserve['output_sha256']==receipt['output_sha256']
                     and reserve['repair_kind']=='additive_reserve_service_lighting'
                     and reserve['all_existing_object_signatures_unchanged']
                     and reserve['all_existing_material_definitions_unchanged']
                     and len(rc['new_service_lights'])==9
                     and len(rc['measured_jamb_contacts'])==18
                     and all(v['support_gap_m']<.00001 for v in rc['measured_jamb_contacts'])
                     and rc['existing_rack_support_roots_reused']==3
                     and rc['new_material_names']==['EOH | Reserve service LED diffuser'])
    else:
        bounded=(receipt['all_other_matrices_geometry_material_assignments_visibility_lights_unchanged']
                 and len(receipt['retired_original_decorative_wear'])==104
                 and receipt['distinct_leaf_histories']==4 and receipt['new_supported_contact_assemblies']==8)
    if not valid_hashes or not bounded:
        failures.append('source transition does not match declared bounded visual-finish receipts')
elif not same_source:failures.append('manifest mismatch:source_sha256')
for key in ['blender','embedded_python','samples','resolution','renderer']:
    if left[key]!=right[key]:failures.append('manifest mismatch:'+key)
lm={v['camera']:v for v in left['views']};rm={v['camera']:v for v in right['views']}
if set(lm)!=set(rm):failures.append('view sets differ')
for name in sorted(set(lm)&set(rm)):
    if any(lm[name][k]!=rm[name][k] for k in ['matrix','lens']):failures.append('camera changed:'+name)
    lp=prior/(name+'.png');rp=cold/(name+'.png')
    for path,record in [(lp,lm[name]),(rp,rm[name])]:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:failures.append('image hash invalid:'+str(path))
    with Image.open(lp) as im_left,Image.open(rp) as im_right:
        l=im_left.convert('RGB');r=im_right.convert('RGB')
        if l.size!=r.size:failures.append('image dimensions differ:'+name);continue
        diff=ImageChops.difference(l,r);stat=ImageStat.Stat(diff)
        results.append({'camera':name,'decoded_pixels_identical':diff.getbbox() is None,
                        'mean_absolute_difference_8bit_rgb':stat.mean,'rms_difference_8bit_rgb':stat.rms,
                        'maximum_channel_difference_8bit':max(v[1] for v in diff.getextrema())})
report={'scope':'Hash-valid images, explicit source provenance, identical toolchain/settings/cameras and measured decoded-pixel differences. Declared source transitions are not same-source cold repeats. Independent visual review determines improvement and stability.',
        'mode':mode,'source_sha256':right['source_sha256'],'previous_source_sha256':left['source_sha256'],
        'source_bytes_identical':same_source,'previous':str(prior),'cold':str(cold),
        'views':results,'all_decoded_pixels_identical':all(r['decoded_pixels_identical'] for r in results),
        'failures':failures,'provenance_pass':not failures}
Path(a.out).write_text(json.dumps(report,indent=2))
print('CAPTURE_PROVENANCE',mode,report['provenance_pass'],'PIXELS_IDENTICAL',report['all_decoded_pixels_identical'])
raise SystemExit(0 if not failures else 1)
