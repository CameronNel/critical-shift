"""A05 additive exterior integration. A04 and all room source bytes stay unchanged."""
import bpy,json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'blender/facility_master.blend';digest=hashlib.sha256(base.read_bytes()).hexdigest()
current=json.loads((ROOT/'exteriors/CURRENT.json').read_text())
layout=json.loads((ROOT/'production/LAYOUT.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False)
scene=bpy.context.scene;scene.name='FACILITY_A05_EXTERIORS'
overlays=bpy.data.collections.new('06_LINKED_EXTERIORS');scene.collection.children.link(overlays)
records=[]
for sid,rev in current.items():
 asset=ROOT/'exteriors'/sid/f'exterior-{rev}.blend'
 with bpy.data.libraries.load(str(asset),link=True) as (src,dst):
  names=['EXTERIOR_'+sid]
  if 'SOURCE_REVIEW_'+sid in src.collections:names.append('SOURCE_REVIEW_'+sid)
  dst.collections=names
 room=bpy.data.objects[sid]
 if len(dst.collections)>1:room.instance_collection=dst.collections[1]
 ob=bpy.data.objects.new('EXTERIOR_INSTANCE_'+sid,None);overlays.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=dst.collections[0];ob.matrix_world=room.matrix_world.copy()
 ob['module_id']=sid;ob['exterior_revision']=rev
 records.append({'section':sid,'revision':rev,'asset':str(asset.relative_to(ROOT)),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'meshes':sum(o.type=='MESH' for o in dst.collections[0].all_objects),'source_light_wrapper':len(dst.collections)>1})
scene['assembly_scope']='A05: twelve linked exterior candidates over unchanged A04 poses. Connector reservations remain unbuilt; independent art acceptance is recorded separately.'
out=ROOT/'blender/facility_master_A05_exteriors.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
(ROOT/'production/EXTERIOR_MASTER_MANIFEST.json').write_text(json.dumps({'revision':'A05','base_sha256':digest,'master_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'exteriors':records,'routes_unbuilt':len(layout['routes']),'source_geometry_unchanged':True},indent=2))
print('EXTERIOR_MASTER_SAVED',len(records),flush=True)
