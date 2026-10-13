import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('/workspace/critical-shift-spawn-runtime');sys.path.insert(0,str(root/'runtime/tools'));from mine_delivery_uv import surface_density
out=Path('/tmp/cs-mine-source-inventory-final12');out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(root/'runtime/unity/Assets/CriticalShift/Generated/Spawn/Room-mine.fbx'))
densities=[surface_density(o,o.data.uv_layers[0].name,4096) for o in bpy.data.objects if o.type=='MESH' and any(s in o.name.lower() for s in ['compressed air main','ventilation duct','tunnel floor'])]
(out/'delivered-density.json').write_text(json.dumps(densities,indent=2)+'\n')
source=root/'runtime/out/spawn-export-source/map/sections/facility-assembly/sources/mine-r39/module_r39_aaa.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
materials=[]
for m in bpy.data.materials:
 if m.name not in ['R39 | Tunnel dirt','R39 | Corroded pipe iron','R38 | Toon blackened iron']:continue
 nodes=[]
 for n in m.node_tree.nodes:
  inputs={}
  for i in n.inputs:
   if hasattr(i,'default_value'):
    v=i.default_value;inputs[i.name]={'default':list(v) if hasattr(v,'__len__') else v,'links':[(l.from_node.name,l.from_socket.name) for l in i.links]}
  r={'name':n.name,'type':n.type,'inputs':inputs,'properties':{k:getattr(n,k) for k in ['noise_dimensions','normalize','operation','vector_type','space','uv_map','attribute_name'] if hasattr(n,k)}}
  if n.type=='TEX_IMAGE' and n.image:r['image']={'name':n.image.name,'file':n.image.filepath,'size':list(n.image.size),'colorspace':n.image.colorspace_settings.name,'projection':n.projection,'extension':n.extension,'interpolation':n.interpolation}
  if n.type=='VALTORGB':r['ramp']=[{'position':e.position,'color':list(e.color)} for e in n.color_ramp.elements]
  nodes.append(r)
 materials.append({'name':m.name,'nodes':nodes})
objects=[]
for o in bpy.data.objects:
 if o.type=='MESH' and ('Lantern' in o.name or 'Compressed air main' in o.name or 'Tunnel floor' in o.name):
  counts={}
  for face in o.data.polygons:counts[str(face.material_index)]=counts.get(str(face.material_index),0)+1
  objects.append({'name':o.name,'visibleShadow':o.visible_shadow,'visibleDiffuse':o.visible_diffuse,'visibleGlossy':o.visible_glossy,'hideRender':o.hide_render,'matrix':list(list(row) for row in o.matrix_world),'bounds':[list(o.matrix_world@Vector(v)) for v in o.bound_box],'materials':[m.name if m else None for m in o.data.materials],'facesByMaterial':counts})
# Compare emitter centre/spherical-surface visibility for representative floor points.
meshes=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.visible_shadow and not any(m and m.use_nodes and any(n.type in ['PRINCIPLED_VOLUME','VOLUME_SCATTER'] for n in m.node_tree.nodes) for m in o.data.materials)]
verts=[];faces=[];ranges=[]
for o in meshes:
 ev=o.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles();base=len(verts);first=len(faces);verts.extend(o.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(base+i for i in t.vertices) for t in mesh.loop_triangles);ranges.append((first,len(faces),o.name));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True);del verts,faces
lanterns=[o for o in bpy.data.objects if o.type=='LIGHT' and o.data.type=='POINT' and 'lantern' in o.name.lower()];lanterns.sort(key=lambda o:o.matrix_world.translation.x,reverse=True)
records=[]
for light in lanterns[:4]:
 position=light.matrix_world.translation.copy();radius=light.data.shadow_soft_size
 for dy in [0,-1,1]:
  start=Vector((position.x,position.y+dy,-.08));direction=position-start;distance=direction.length;hit=bvh.ray_cast(start,direction.normalized(),distance-1e-4)
  occluder=next((name for a,b,name in ranges if hit[2] is not None and a<=hit[2]<b),None)
  hits=[]
  for i in range(64):
   z=1-2*(i+.5)/64;theta=i*math.pi*(3-math.sqrt(5));r=math.sqrt(1-z*z);target=position+Vector((r*math.cos(theta),r*math.sin(theta),z))*radius;d=target-start;h=bvh.ray_cast(start,d.normalized(),d.length-1e-4);hits.append(h[0] is not None)
  records.append({'light':light.name,'power':light.data.energy,'radius':radius,'lightPosition':list(position),'floorPoint':list(start),'centreOccluder':occluder,'centreDistance':hit[3],'sphericalSampleBlockedFraction':sum(hits)/64,'samples':64,'limit':'Geometry/source-shadow-visibility only; not a BSDF opacity or weighted spherical-emission integration.'})
(out/'inventory.json').write_text(json.dumps({'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'materials':materials,'objects':objects,'floorEmitterGeometryControls':records},indent=2)+'\n');print('CS_FINAL12_SOURCE_INVENTORY_OK',len(objects),len(materials),flush=True)
