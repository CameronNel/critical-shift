import bpy,json,ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();cam=bpy.data.objects['SY CAMERA | 01-front-yard'];s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
frame=cam.data.view_frame(scene=s);xmin=min(v.x for v in frame);xmax=max(v.x for v in frame);ymin=min(v.y for v in frame);ymax=max(v.y for v in frame);z=frame[0].z
hits=[]
for px,py in [(700,600),(300,600),(600,490),(1000,600),(650,420),(450,550)]:
 direction=cam.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/1280,ymax-(ymax-ymin)*py/720,z)).normalized()
 hit,p,n,face,o,matrix=s.ray_cast(deps,cam.location,direction)
 if hit:
  mat=o.material_slots[o.data.polygons[face].material_index].material
  hits.append(dict(pixel=[px,py],object=o.name_full,point=list(p),face=face,material=mat.name if mat else None))
img=bpy.data.images['SY | Courtyard localized wear and moisture'];a=np.empty(len(img.pixels),np.float32);img.pixels.foreach_get(a);a=a.reshape(-1,4)
mats=[]
uvtest=[]
for o in s.objects:
 if o.name.startswith('SY | Dimensional courtyard slab'):
  p=o.location
  if abs(p.x+25.5)<.1 and abs(p.y-18)<.1 or o.name.endswith('.030'):
   uv=o.data.uv_layers['GF_FloorMask'];poly=o.data.polygons[27];coords=[list(uv.data[i].uv) for i in poly.loop_indices]
   uvtest.append(dict(name=o.name,pos=list(p),uv=coords))
for m in bpy.data.materials:
 if m.name.startswith('SY | Courtyard dimensional slab mineral'):
  mats.append(dict(name=m.name,nodes=[dict(name=n.name,type=n.type,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None,uv=n.uv_map if n.type=='UVMAP' else None) for n in m.node_tree.nodes],links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]))
out=Path(__file__).resolve().parents[3]/'runtime/out/environment/spawn-finish/floor-probe.json';out.write_text(json.dumps(dict(hits=hits,uvtest=uvtest,image_min=a.min(axis=0).tolist(),image_max=a.max(axis=0).tolist(),image_mean=a.mean(axis=0).tolist(),materials=mats),indent=2));print('PROBED',flush=True)
