"""Read-only player-sized sweep of the saved local environment, not engine physics."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector

s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();records=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'} or o.hide_render:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh()
 if me and me.vertices:
  vv=[o.matrix_world@v.co for v in me.vertices]
  lo=[min(v[i] for v in vv) for i in range(3)];hi=[max(v[i] for v in vv) for i in range(3)]
  records.append((o.name,lo,hi))
 ev.to_mesh_clear()
paths={
 'D01_TO_D02':[(0,-.24),(0,16.95)],
 'SWITCHGEAR_APPROACH':[(0,2.8),(-2.2,2.8),(-2.2,11.4),(0,11.4)],
 'TRANSFORMER_SERVICE':[(0,4.4),(2.15,4.4),(2.15,8.6),(0,8.6)],
 'TRANSFER_SERVICE':[(0,9.2),(3.1,9.2),(3.1,11.4),(0,11.4)],
 'RESERVE_APPROACH_AND_RETURN':[(0,13.2),(6.4,13.2),(6.4,14.8),(6.4,11.7),(6.4,13.2),(0,13.2)],
 'WORKBENCH_SERVICE':[(0,12.3),(-2.2,12.3),(-2.2,15.3),(0,15.3)]}
results=[]
for name,route in paths.items():
 samples=[]
 for a,b in zip(route,route[1:]):
  n=math.ceil(math.dist(a,b)/.10)
  for k in range(n+1):
   x,y=[a[i]+(b[i]-a[i])*k/n for i in range(2)]
   lo=[x-.30,y-.30,.025];hi=[x+.30,y+.30,1.85]
   hits=[on for on,ol,oh in records if all(min(hi[i],oh[i])-max(lo[i],ol[i])>.001 for i in range(3))]
   samples.append({'eye':[round(x,4),round(y,4),1.68],'obstructions':hits})
 results.append({'route':name,'path_xy':route,'samples':samples,'pass':not any(p['obstructions'] for p in samples)})
gate_sweeps=[]
for gate in [o for o in s.objects if o.name.startswith('TX_GUARD_SERVICE_PIVOT_')]:
 old=gate.rotation_euler.copy();positions=[]
 for angle in range(0,91,5):
  gate.rotation_euler.z=math.radians(angle*(1 if gate['open_rotation_z_degrees']>0 else -1));bpy.context.view_layer.update()
  vv=[]
  for o in gate.children:
   if o.type not in {'MESH','CURVE','FONT'}:continue
   ev=o.evaluated_get(dg);me=ev.to_mesh();vv.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
  positions.append({'degrees':angle,'minimum_world_x':min(v.x for v in vv)})
 gate.rotation_euler=old;bpy.context.view_layer.update()
 gate_sweeps.append({'gate':gate.name,'states':positions,'pass':all(p['minimum_world_x']>1.2 for p in positions)})
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True)
report={'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'revision':s.get('revision'),'method':'0.60m square body envelope, z0.025..1.85, eye1.68, path samples <=0.10m, conservative evaluated world AABBs','routes':results,'pass':all(r['pass'] for r in results),'limits':['Local static geometry only.','No engine collision, head motion, carried body, navmesh or neighboring module traversal claimed.','Door leaves are parked open; machinery service states need engine animation and isolation logic.']}
report['transformer_gate_sweeps']=gate_sweeps
report['pass']=report['pass'] and len(gate_sweeps)==2 and all(g['pass'] for g in gate_sweeps)
out.write_text(json.dumps(report,indent=2),encoding='utf-8');print('WALKTHROUGH',report['pass'],out)
if not report['pass']:raise RuntimeError('Player route envelope intersects geometry')
