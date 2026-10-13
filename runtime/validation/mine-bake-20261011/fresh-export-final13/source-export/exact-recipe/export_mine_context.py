"""Bake source-authored front-end surfaces visible around the mine into a mesh overlay.

Original front-end mesh/collision assets and all Blender sources remain unchanged.
The overlay supplies UVs/materials for the same geometry, never duplicate objects.
Run in Blender on the pinned, patched combined-runtime-source.blend.
"""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_spawn_map import matrix, export
from export_spawn_materials import bake_atlas
from export_mine_materials import geometry_digest
from mine_lightmap_uv import generate

output=Path(sys.argv[sys.argv.index('--')+1])
manifest=json.loads((output/'map-bindings.json').read_text())
package=next(p for p in manifest['materials'] if p['room']=='mine')
front=next(r for r in manifest['rooms'] if r['key']=='front-end-area')
source=bpy.context.scene
view=source.view_settings
source_view={'transform':view.view_transform,'look':view.look,'exposure':view.exposure,'gamma':view.gamma}
instance=source.objects['ROOM_front-end-area']
members=list(instance.instance_collection.all_objects)
# The original preview manifest omitted SUN names and orientation. Keep this
# scoped source-light contract alongside the mine's existing context overlay,
# without changing other rooms' delivered meshes or legacy light records.
package['contextSunLights'] = [dict(name=o.name, type='SUN',
    position=list(matrix(o).translation), rotation=list(matrix(o).to_quaternion()),
    color=list(o.data.color), power=float(o.data.energy), angle=math.degrees(o.data.angle))
    for o in members if o.type == 'LIGHT' and o.data.type == 'SUN' and not o.hide_render]
old={r['source']:r for r in front['objects']}
dg=bpy.context.evaluated_depsgraph_get()
scene=bpy.data.scenes.new('CS_MINE_CONTEXT_EXPORT');bpy.context.window.scene=scene
root=bpy.data.objects.new('CS_ROOM_front-end-area',None);scene.collection.objects.link(root)
from export_mine_volumes import export_volumes
package['volumes']=export_volumes(scene,source.objects['ROOM_mine'],output,matrix)
made={};mappings=[]
def clone(o):
    if o in made:return made[o]
    parent=clone(o.parent) if o.parent in members else root
    mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg) if o.type in {'MESH','CURVE','FONT'} else None
    n=bpy.data.objects.new('CS_front-end-area_'+o.name,mesh);scene.collection.objects.link(n)
    n.parent=parent;n.matrix_basis=o.matrix_parent_inverse@o.matrix_basis if o.parent in members else matrix(o)
    n.visible_shadow=o.visible_shadow
    made[o]=n
    return n
selected=[]
for o in members:
    if o.type not in {'MESH','CURVE','FONT'} or o.hide_render:continue
    if o.name not in old:raise ValueError('Context object is not in the prepared assembly: '+o.name)
    bounds=[instance.matrix_world @ matrix(o) @ Vector(v) for v in o.bound_box]
    # Source depot west of the facility; includes the mine portal's ground, rail, fences,
    # vehicles and fixtures. The large context ground intersects this footprint.
    if max(v.x for v in bounds)<-116 or min(v.x for v in bounds)>-23 or max(v.y for v in bounds)<-99 or min(v.y for v in bounds)>-44:continue
    n=clone(o)
    if not n.data or not n.data.polygons:continue
    selected.append(n)
    binding=dict(old[o.name])
    # The front-end manifest can predate this visibility contract. Read the
    # current linked source rather than preserving a missing/default flag.
    binding['sourceShadowExcluded']=not o.visible_shadow
    mappings.append(binding)
frames={n.object for o in selected for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_COORD' and n.object}
keep={root,*made.values(),*frames}
for f in list(frames):
    while f.parent:f=f.parent;keep.add(f)
bpy.data.batch_remove([o for o in bpy.data.objects if o not in keep])
bpy.data.batch_remove([s for s in bpy.data.scenes if s!=scene])
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.context.view_layer.update()
before=geometry_digest(selected)
groups={k:[] for k in ('mine-context-ground','mine-context-structure','mine-context-props')}
for n,m in zip(selected,mappings):
    name=m['source'].lower()
    k='mine-context-ground' if name=='context_ground' or name.startswith(('yard_ground','yard_pad','ground_')) else 'mine-context-structure' if any(s in name for s in ('fence','wall','roof','rail','rock','cliff','column')) else 'mine-context-props'
    groups[k].append(n)
packages=[]
for k,meshes in groups.items():
    if not meshes:continue
    print('CS_MINE_CONTEXT_ATLAS',k,len(meshes),sum(len(o.data.vertices) for o in meshes),flush=True)
    p=bake_atlas(scene,meshes,mappings,output,source_view,k,room='mine')
    for d in p['definitions']:d['atlas']=len(package['atlases'])+len(packages)
    packages.append(p)
if before!=geometry_digest(selected):raise ValueError('Context baking changed source geometry.')
if generate(selected)!=len(selected):raise ValueError('Context UV coverage changed.')
mesh_file='MineContext.fbx';export(output/mesh_file,[root,*made.values()])
package['atlases'].extend(p['maps'] for p in packages)
package['definitions'].extend(d for p in packages for d in p['definitions'])
package['contextMesh']={'file':mesh_file,'sha256':hashlib.sha256((output/mesh_file).read_bytes()).hexdigest(),'colorSpace':'mesh','size':0}
package['contextObjects']=mappings
package['contextGeometrySha256']=before
(output/'map-bindings.json').write_text(json.dumps(manifest,indent=2)+'\n')
(output/'mine-context.json').write_text(json.dumps({'status':'Passed','meshes':len(selected),'geometryUnchanged':True,'geometrySha256':before,'mesh':package['contextMesh'],'nodes':[m['node'] for m in mappings],'limits':'UV/material overlay for existing front-end objects, not new placed geometry. Native validation required.'},indent=2)+'\n')
print('CS_MINE_CONTEXT_DELIVERY_OK',len(selected),flush=True)
