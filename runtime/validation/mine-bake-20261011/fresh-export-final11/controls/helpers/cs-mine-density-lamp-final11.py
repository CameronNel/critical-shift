import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path('/workspace/critical-shift-spawn-runtime');sys.path.insert(0,str(root/'runtime/tools'));from mine_delivery_uv import surface_density
out=Path('/tmp/cs-mine-density-lamp-final11');out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(root/'runtime/unity/Assets/CriticalShift/Generated/Spawn/Room-mine.fbx'))
density=[]
for o in bpy.data.objects:
 if o.type=='MESH' and 'duct' in o.name.lower():
  r=surface_density(o,o.data.uv_layers[0].name,4096);density.append(r)
(out/'density.json').write_text(json.dumps(density,indent=2)+'\n');print('CS_PIPE_DENSITY',len(density),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'runtime/out/spawn-export-source/map/sections/facility-assembly/sources/mine-r39/module_r39_aaa.blend'),load_ui=False)
material=next(m for m in bpy.data.materials if m.name=='R39 | Riveted duct iron');nodes=[]
for node in material.node_tree.nodes:
 nodes.append({'name':node.name,'type':node.type,'links':[(l.from_node.name,l.from_socket.name,l.to_socket.identifier) for l in material.node_tree.links if l.to_node==node],'image':{'file':node.image.filepath,'projection':node.projection,'extension':node.extension,'interpolation':node.interpolation} if node.type=='TEX_IMAGE' else None})
(out/'duct-links.json').write_text(json.dumps(nodes,indent=2)+'\n')
# Nearest visible source surface. Bounds filter only eliminates objects whose
# minimum possible distance is already larger than the measured current best.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();meshes=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not any(m and m.use_nodes and any(n.type in {'PRINCIPLED_VOLUME','VOLUME_SCATTER'} for n in m.node_tree.nodes) for m in o.data.materials)]
def world(o):return o.matrix_world
bounds={o:([min((world(o)@Vector(v))[i] for v in o.bound_box) for i in range(3)],[max((world(o)@Vector(v))[i] for v in o.bound_box) for i in range(3)]) for o in meshes}
cache={};records=[]
for light in [o for o in bpy.data.objects if o.type=='LIGHT' and o.data.type=='POINT' and not o.hide_render]:
 p=light.matrix_world.translation;distance=1e9;near=None
 candidates=sorted(meshes,key=lambda o:sum(max(bounds[o][0][i]-p[i],0,p[i]-bounds[o][1][i])**2 for i in range(3)))
 for o in candidates:
  bd=math.sqrt(sum(max(bounds[o][0][i]-p[i],0,p[i]-bounds[o][1][i])**2 for i in range(3)))
  if bd>distance:break
  if o not in cache:
   evaluated=o.evaluated_get(dg);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();verts=[o.matrix_world@v.co for v in mesh.vertices];faces=[tuple(t.vertices) for t in mesh.loop_triangles];cache[o]=BVHTree.FromPolygons(verts,faces,all_triangles=True);evaluated.to_mesh_clear()
  hit=cache[o].find_nearest(p)
  if hit and hit[3]<distance:distance=hit[3];near=o.name
 radius=light.data.shadow_soft_size
 records.append({'light':light.name,'power':light.data.energy,'radius':radius,'nearestVisibleSurface':near,'nearestDistanceMetres':distance,'pointVsFiniteEmitterRatioAtNearest':1+radius*radius/(distance*distance) if distance else None})
(out/'lamp-surfaces.json').write_text(json.dumps(records,indent=2)+'\n');print('CS_LAMP_SURFACES',len(records),flush=True)
