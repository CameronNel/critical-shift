"""Write a separate room-in-map review. Load the current environment; never save it."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[1];repo=root.parents[4]
a=sys.argv[sys.argv.index('--')+1:];revision=a[0]
candidate=root/'production/checkpoints'/f'{revision}.blend'
map_path=repo/'sections/facility-assembly/blender/facility_environment.blend'
assert Path(bpy.data.filepath).resolve()==map_path.resolve()
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_hash=hashfile(map_path);candidate_hash=hashfile(candidate)
layout=json.loads((repo/'sections/facility-assembly/production/LAYOUT_A12.json').read_text())['placements']['refinery']
transform=Matrix.Translation(Vector(layout['translation']))@Matrix.Rotation(math.radians(layout['rotation_z_degrees']),4,'Z');inverse=transform.inverted()
map_scene=bpy.context.scene
# Respect collection render visibility from the authoritative map.
visible=set()
def visit(collection,hidden=False):
 hidden=hidden or collection.hide_render
 if not hidden:visible.update(collection.objects)
 for child in collection.children:visit(child,hidden)
visit(map_scene.collection)
selected=[]
for o in map_scene.objects:
 if o not in visible or o.hide_render or o.type not in {'MESH','CURVE','FONT'}:continue
 if 'MATERIAL_PREVIEW_refinery' in o.name or o.name.startswith('FLR | Refinery dimensional slab'):continue
 if o.type!='MESH':continue
 points=[inverse@o.matrix_world@Vector(p) for p in o.bound_box]
 lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
 # Real nearby connector/yard/adjacent-room geometry, never invented backdrop geometry.
 if any(hi[i]<[-12,-11,-2][i] or lo[i]>[12,11,7][i] for i in range(3)):continue
 # Exclude any supplemental interior-only map surface from double-drawing the candidate.
 if all(lo[i]>[-7.31,-6.12,-.05][i] and hi[i]<[7.31,6.12,4.8][i] for i in range(3)):continue
 selected.append((o,o.name,o.matrix_world.copy(),[list(lo),list(hi)]))
# Prefix in-memory map IDs so appended room names and its camera identifiers remain exact.
for o in list(bpy.data.objects):
 if not o.library:o.name='MAP REVIEW INPUT | '+o.name
with bpy.data.libraries.load(str(candidate),link=False) as (source,destination):
 assert len(source.scenes)==1,source.scenes
 destination.scenes=[source.scenes[0]]
review=destination.scenes[0];review.name=f'Refinery {revision} | Actual map context, practicals only'
bpy.context.window.scene=review
snapshots={o:o.matrix_world.copy() for o in review.objects}
def depth(o):
 n=0
 while o.parent:n+=1;o=o.parent
 return n
for o in sorted(snapshots,key=depth):o.matrix_world=transform@snapshots[o]
bpy.context.view_layer.update()
context=bpy.data.collections.new('REVIEW ONLY | Existing adjacent map geometry');review.collection.children.link(context)
records=[]
for original,name,matrix,bounds in selected:
 copy=original.copy();copy.parent=None;copy.matrix_world=matrix;copy.name='CONTEXT | '+name;context.objects.link(copy)
 copy['context_provenance']='current facility_environment.blend';records.append(dict(source_object=name,context_object=copy.name,local_bounds=bounds))
assert len([o for o in review.objects if o.type=='LIGHT'])==21
assert review.world.node_tree.nodes['Background'].inputs['Strength'].default_value==0
out=root/'production/context'/f'refinery_context_{revision}.blend';out.parent.mkdir(exist_ok=True)
review['review_only']=True;review['context_source_sha256']=original_hash;review['candidate_source_sha256']=candidate_hash
# libraries.write restricts the artifact to the new review scene and its dependencies.
bpy.data.libraries.write(str(out),{review},path_remap='RELATIVE',fake_user=True,compress=True)
review_name=review.name
bpy.ops.wm.open_mainfile(filepath=str(out))
review=bpy.data.scenes[review_name];bpy.context.window.scene=review
for other in list(bpy.data.scenes):
 if other!=review:bpy.data.scenes.remove(other)
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False,compress=True)
assert hashfile(map_path)==original_hash and hashfile(candidate)==candidate_hash
report=dict(output=out.relative_to(repo).as_posix(),sha256=hashfile(out),context_source=map_path.relative_to(repo).as_posix(),context_sha256=original_hash,candidate=candidate.relative_to(repo).as_posix(),candidate_sha256=candidate_hash,transform=[list(r) for r in transform],objects=records,new_external_lights=0,light_count=21,world_strength=0,source_files_unchanged=True,review_only=True,limitations='Context geometry is copied from the current map; all map light objects are omitted. Only candidate practicals light the preview. This is not promotion or a refreshed whole-map cache.')
(root/'production/context'/f'manifest_{revision}.json').write_text(json.dumps(report,indent=2))
print('CONTEXT_PREVIEW_WRITTEN',len(records),out,flush=True)
