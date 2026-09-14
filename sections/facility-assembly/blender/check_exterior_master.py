"""Fresh-process A05 local integration validation; no rendering or source writes."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'blender/facility_master_A05_exteriors.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
L=json.loads((ROOT/'production/LAYOUT.json').read_text());C=json.loads((ROOT/'exteriors/CURRENT.json').read_text());S=json.loads((ROOT/'production/SOURCES.json').read_text())
bpy.context.view_layer.update();checks=[]
for row in S:
 sid=row['id'];room=bpy.data.objects[sid];ext=bpy.data.objects['EXTERIOR_INSTANCE_'+sid];pose=L['placements'][sid]
 assert room.instance_collection and room.instance_collection.library
 assert ext.instance_collection and ext.instance_collection.library
 assert max(abs(room.location[i]-pose['translation'][i]) for i in range(3))<.0001
 assert abs(math.degrees(room.rotation_euler.z)-pose['rotation_z_degrees'])<.0001
 assert max(abs(v-1) for v in room.scale)<.0001
 assert max(abs(ext.matrix_world[i][j]-room.matrix_world[i][j]) for i in range(4) for j in range(4))<.0001
 assert hashlib.sha256((ROOT/row['frozen']).read_bytes()).hexdigest()==row['source_sha256']
 assert ext['exterior_revision']==C[sid]
 audit=json.loads((ROOT/'exteriors'/sid/f'audit-{C[sid]}.json').read_text());assert audit['status']=='PASS'
 support=json.loads((ROOT/'exteriors'/sid/f'support-connectivity-{C[sid]}.json').read_text())
 defects=support.get('mesh_defects',[r for r in support.get('normal_checks',[]) if r['signed_volume']<=0 or r['nonmanifold'] or r['inconsistent'] or r['degenerate']])
 assert not defects and not support['detached_components'],sid
 assert support['root_connected_additive_count']==support['additive_mesh_count'],sid
 checks.append({'section':sid,'exterior_revision':C[sid],'source_hash_match':True,'pose_and_unit_scale':True,'portal_and_reservation_check':'PASS','mesh_and_support_broadphase':'PASS'})
missing=[i.name for i in bpy.data.images if i.source=='FILE' and i.users and not i.packed_file and not Path(bpy.path.abspath(i.filepath,library=i.library)).exists()]
assert not missing,missing
delta=(bpy.data.objects['turbine-room'].matrix_world@Vector((4.6,11.45,0))-bpy.data.objects['condenser-bay'].matrix_world@Vector((3,4.05,6))).length
assert delta<.0001
clashes=json.loads((ROOT/'production/EXTERIOR_LAYOUT_AUDIT.json').read_text());assert not clashes['foreign_geometry_candidates'] and not clashes['route_candidates']
report={'status':'PASS','revision':'A05','rooms':checks,'U04_centres_delta_m':delta,'missing_images':missing,'connector_count_unbuilt':len(L['routes']),'scope':'Fresh process linked libraries, exact A04 poses, frozen source hashes, exterior mesh/support broadphase and reserved gap checks. No art-score, runtime navigation or finished connector acceptance implied.'}
(ROOT/'production/COLD_EXTERIOR_MASTER_CHECK.json').write_text(json.dumps(report,indent=2));print('COLD_EXTERIOR_MASTER_PASS',len(checks),flush=True)
