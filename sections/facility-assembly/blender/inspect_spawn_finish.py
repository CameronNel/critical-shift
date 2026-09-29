"""Read-only measured components for the approved spawn-yard concept."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/spawn-finish';out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
def bounds(points):return [[round(min(p[i] for p in points),4) for i in range(3)],[round(max(p[i] for p in points),4) for i in range(3)]]
rows=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 lo,hi=bounds([o.matrix_world@Vector(v) for v in o.bound_box])
 if hi[0]<-38 or lo[0]>-7 or hi[1]<-2 or lo[1]>43 or lo[2]>16:continue
 row=dict(name=o.name_full,library=o.library.filepath if o.library else None,bounds=[lo,hi],materials=[m.name if m else None for m in o.data.materials],verts=len(o.data.vertices),collections=[c.name for c in o.users_collection])
 print('INSPECTING',o.name,len(o.data.vertices),flush=True)
 if any(k in o.name.lower() for k in ('spawn','medical','horizontal','floor','continuous','exterior_instance','cleanup','quiet concrete','network_scenery','courtyard')) and len(o.data.vertices)<1500000:
  me=o.data;adj=[[] for _ in me.vertices]
  for e in me.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
  remaining=set(range(len(adj)));parts=[];vertex_part={}
  while remaining:
   start=remaining.pop();todo=[start];ids=[]
   while todo:
    v=todo.pop();ids.append(v)
    for w in adj[v]:
     if w in remaining:remaining.remove(w);todo.append(w)
   pts=[o.matrix_world@me.vertices[i].co for i in ids];a,b=bounds(pts)
   idx=len(parts)
   for i in ids:vertex_part[i]=idx
   parts.append(dict(first=start,count=len(ids),lo=a,hi=b,mats=set()))
  for p in me.polygons:
   if p.vertices:parts[vertex_part[p.vertices[0]]]['mats'].add(p.material_index)
  for p in parts:p['mats']=sorted(p['mats'])
  row['components']=[p for p in parts if p['hi'][0]>-38 and p['lo'][0]<-7 and p['hi'][1]>-2 and p['lo'][1]<43 and p['lo'][2]<16]
 rows.append(row)
src=Path(bpy.data.filepath)
(out/'inspection.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),units=s.unit_settings.system,scale=s.unit_settings.scale_length,objects=rows),indent=2))
print('INSPECTED',len(rows),flush=True)
