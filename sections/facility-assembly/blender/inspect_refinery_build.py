"""Read-only refinery and nearby pavilion inspection."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/refinery-build';out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)]
 if hi[0]<-14 or lo[0]>12 or hi[1]<-28 or lo[1]>-4:continue
 row=dict(name=o.name_full,local=o.library is None,lo=lo,hi=hi,materials=[m.name if m else None for m in o.data.materials],matrix=[list(v) for v in o.matrix_world])
 # Components enable surgical removal of the pavilion from a combined site mesh.
 if 'refinery' in o.name.lower() or (lo[0]<9 and hi[0]>3 and lo[1]<-12 and hi[1]>-20):
  me=o.data;adj=[[] for _ in me.vertices]
  for e in me.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
  seen=set();components=[]
  for v in me.vertices:
   if v.index in seen:continue
   stack=[v.index];seen.add(v.index);inds=[]
   while stack:
    k=stack.pop();inds.append(k)
    for j in adj[k]:
     if j not in seen:seen.add(j);stack.append(j)
   pts=[o.matrix_world@me.vertices[i].co for i in inds]
   cl=[min(p[i] for p in pts) for i in range(3)];ch=[max(p[i] for p in pts) for i in range(3)]
   if ch[0]>=-12 and cl[0]<=10 and ch[1]>=-27 and cl[1]<=-6:
    components.append(dict(first=inds[0],count=len(inds),lo=cl,hi=ch))
  row['components']=components
 rows.append(row)
data=dict(source=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),objects=rows)
(out/'inspection.json').write_text(json.dumps(data,indent=2));print('INSPECT_COMPLETE',len(rows),flush=True)
