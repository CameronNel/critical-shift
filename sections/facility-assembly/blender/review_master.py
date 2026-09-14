import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'production/LAYOUT.json').read_text())
sources=json.loads((ROOT/'production/SOURCES.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/facility_master.blend'),load_ui=False)
scene=bpy.context.scene;bpy.context.view_layer.update()
checks=[]
for row in sources:
 sid=row['id'];ob=bpy.data.objects[sid];pose=layout['placements'][sid]
 assert ob.instance_collection and ob.instance_collection.library
 assert max(abs(ob.location[i]-pose['translation'][i]) for i in range(3))<.0001
 assert abs(math.degrees(ob.rotation_euler.z)-pose['rotation_z_degrees'])<.0001
 assert max(abs(x-1) for x in ob.scale)<.0001
 assert hashlib.sha256((ROOT/row['frozen']).read_bytes()).hexdigest()==row['source_sha256']
 assert Path(bpy.path.abspath(ob.instance_collection.library.filepath)).exists()
 checks.append({'room':sid,'linked_objects':len(ob.instance_collection.all_objects),'unit_scale':True,'pose_match':True,'frozen_source_hash_match':True})
t=bpy.data.objects['turbine-room'];c=bpy.data.objects['condenser-bay']
tu=t.matrix_world@Vector((4.6,11.45,0));cu=c.matrix_world@Vector((3,4.05,6));delta=(tu-cu).length
assert delta<.0001,delta
missing=[i.name for i in bpy.data.images if i.source=='FILE' and i.users and not i.packed_file and not Path(bpy.path.abspath(i.filepath,library=i.library)).exists()]
assert not missing,missing
report={'status':'PASS','revision':layout['revision'],'room_count':len(checks),'rooms':checks,'missing_images':missing,'U04_centres_delta_m':delta,'U04_world':list(tu),'scope':'Fresh-process linked-library/transform/unit-scale/dependency verification. U04 centres match; surrounding mating hardware and utility caps remain integration work. No corridor or engine traversal claimed.'}
(ROOT/'production/COLD_MASTER_CHECK.json').write_text(json.dumps(report,indent=2))
print('COLD_MASTER_PASS',len(checks),'rooms; U04 delta',delta,flush=True)
out=ROOT/'production/renders';out.mkdir(exist_ok=True)
for name in ['A01_AERIAL','A02_TRUE_PLAN','A03_POWER_WING']:
 scene.camera=bpy.data.objects[name];scene.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True);print('ASSEMBLY_RENDER_DONE',name,flush=True)
print('ASSEMBLY_REVIEW_COMPLETE',flush=True)
