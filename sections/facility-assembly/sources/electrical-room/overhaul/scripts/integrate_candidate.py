"""Create a reviewable whole-map candidate; never save over the canonical map."""
import bpy,json,hashlib,math,sys,argparse,os
from pathlib import Path
from mathutils import Matrix,Vector
p=argparse.ArgumentParser();p.add_argument('--module',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(__file__).resolve().parents[6];overhaul=Path(__file__).resolve().parents[1]
source=root/json.loads((root/'MAP.json').read_text())['authoring_scene'];module=Path(a.module).resolve();out=Path(a.output).resolve()
assert out!=source and out!=root/'sections/facility-assembly/blender/facility_spawn_material_preview_R17.blend'
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
protected={o.name:tuple(sum((list(row) for row in o.matrix_world),[])) for o in bpy.context.scene.objects}
library_hashes={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
cache=bpy.data.objects['VC | Roof-finished MATERIAL_PREVIEW_electrical-room']
report={'main_before_sha256':before,'module_sha256':sha(module),'retired_cache':cache.name,'retired_lights':[],'neighbor_transforms_changed':[]}
assert cache.get('preview_source')=='electrical-room'
bpy.data.objects.remove(cache,do_unlink=True)
pose=json.loads((root/'sections/facility-assembly/production/LAYOUT_A12.json').read_text())['placements']['electrical-room']
mat=Matrix.Translation(Vector(pose['translation']))@Matrix.Rotation(math.radians(pose['rotation_z_degrees']),4,'Z')
baseline=json.loads((overhaul/'renders/baseline/inspection.json').read_text())
# Original practicals are parented: local locations are not room-world positions.
light_positions=[mat@Vector((o['matrix'][3],o['matrix'][7],o['matrix'][11])) for o in baseline['records'] if o['type']=='LIGHT']
for o in list(bpy.context.scene.objects):
    if o.type=='LIGHT' and o.library is None and o.name.startswith('VC | Restored INTERIOR_') and any((o.matrix_world.translation-p).length<.001 for p in light_positions):
        report['retired_lights'].append(o.name);bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(module),link=True,relative=True) as (src,dst):
    assert 'MODULE_electrical-room' in src.collections;dst.collections=['MODULE_electrical-room']
linked=dst.collections[0];coll=bpy.data.collections.new('INTEGRATION | Electrical room overhaul candidate');bpy.context.scene.collection.children.link(coll)
inst=bpy.data.objects.new('INSTANCE | electrical-room current source',None);coll.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=linked;inst.matrix_world=mat
inst['source_module']=str(module.relative_to(root));inst['candidate_module_sha256']=sha(module)
# Cameras copy the saved fixed local source transforms through the established map pose.
for rec in baseline['records']:
    if rec['type']!='CAMERA':continue
    name=rec['name'];m=rec['matrix'];matrix=Matrix([m[i:i+4] for i in range(0,16,4)])
    cam_data=bpy.data.cameras.new('EI_'+name);cam=bpy.data.objects.new(cam_data.name,cam_data);coll.objects.link(cam);cam.matrix_world=mat@matrix
    # Lens is measured from the unchanged source camera library.
    camera=next(o for o in linked.all_objects if o.name==name);cam_data.lens=camera.data.lens
bpy.context.view_layer.update()
for name,old in protected.items():
    o=bpy.data.objects.get(name)
    if name==report['retired_cache'] or name in report['retired_lights']:continue
    if not o or tuple(sum((list(row) for row in o.matrix_world),[]))!=old:report['neighbor_transforms_changed'].append(name)
assert not report['neighbor_transforms_changed']
assert sha(source)==before and all(sha(path)==value for path,value in library_hashes.items())
out.parent.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['candidate_sha256']=sha(out);report['main_unchanged']=sha(source)==before;report['dependency_hashes_unchanged']=True
report['scope']='Review candidate only. Canonical map ownership/promotion unchanged. Inherits pre-existing missing spawn wrapper datablocks from base map; electrical module has no missing dependency.'
(overhaul/'integration-candidate.json').write_text(json.dumps(report,indent=2));print('INTEGRATION_CANDIDATE_SAVED',out,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
