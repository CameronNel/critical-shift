"""Cold-source checks for the concrete latest user constraints, plus existing routes."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import inhabit_spawn as life
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else HERE.parent/'production/valorant-reference/verified'
out.mkdir(parents=True,exist_ok=True)
report=life.validate(out)
def local_bounds(ob):
    return [[round(min(v.co[i] for v in ob.data.vertices),5),round(max(v.co[i] for v in ob.data.vertices),5)] for i in range(3)]
shells={}
for i in range(1,5):
    prefix='PPE_%02d'%i
    shells[prefix]={}
    for o in bpy.data.objects[prefix].children_recursive:
        if o.type=='MESH' and o.name.startswith(prefix) and '_rubbed_paint' not in o.name and any(x in o.name for x in ['_back','_side','_return_lip','_shelf']):
            shells[prefix][o.name[len(prefix):]]=local_bounds(o)
floor_mats=[]
for i in range(5):
    m=bpy.data.materials['floor_timber_%d'%i];p=m.node_tree.nodes['Principled BSDF']
    floor_mats.append({'material':m.name,'coat':p.inputs['Coat Weight'].default_value,'specular':p.inputs['Specular IOR Level'].default_value,'rough_ranges':[[n.inputs['To Min'].default_value,n.inputs['To Max'].default_value] for n in m.node_tree.nodes if n.type=='MAP_RANGE']})
new_checks={
 'identical_locker_shell_mesh_bounds':all(v==shells['PPE_01'] for v in shells.values()),
 'matching_eight_locker_door_angles':all(abs(abs(bpy.data.objects['BELONG_%02d_door_%s'%(i,s)].rotation_euler.z)-1.88495559215)<.0001 for i in range(1,5) for s in ['L','R']),
 'no_small_mismatched_cabinets':not any(bpy.data.objects.get(n) for n in ['LOCKER_personal_north','LOCKER_personal_south']),
 'matte_wood_no_coat':all(m['coat']==0 and m['specular']<.13 and all(r[0]>.89 for r in m['rough_ranges']) for m in floor_mats),
 'small_porcelain_tile_pitch':abs(bpy.data.objects['V_LOCKER_porcelain_tiles']['tile_pitch_m']-.1)<1e-6,
 'modern_staff_door_no_old_door':bool(bpy.data.objects.get('V_REAR_staff_door')) and not bpy.data.objects.get('HALL_rear_door'),
 'plants_in_all_three_rooms':all(any(o.name.startswith('V_'+room) and o.get('asset_role')=='potted_plant' for o in bpy.data.objects) for room in ['HALL','BRIEF','LOCKER']),
 'clear_pod_preserved':bool(bpy.data.objects.get('INTEGRITY_POD')) and 'pod_optical_glass' in bpy.data.materials,
 'used_texture_files_packed':all(im.packed_file or im.packed_files for im in bpy.data.images if im.users and im.source=='FILE'),
}
data={'status':'PASS' if report['status']=='PASS' and all(new_checks.values()) else 'FAIL','checks':new_checks,'inherited_checks_status':report['status'],'shell_bounds':shells,'floor_materials':floor_mats,'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()}
(out/'user_constraints.json').write_text(json.dumps(data,indent=2))
print('USER_CONSTRAINTS',json.dumps({'status':data['status'],'checks':new_checks}),flush=True)
