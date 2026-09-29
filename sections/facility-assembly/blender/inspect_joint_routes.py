"""Read-only pre-edit foot-support baseline for comparison with the joint pass."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/exterior-joints'
r=json.loads((OUT/'verification.json').read_text());assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==r['before_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
routes=json.loads((ROOT/'runtime/out/environment/refinery-build/build-verification.json').read_text())['route_samples']+json.loads((ROOT/'runtime/out/environment/courtyard/build-verification.json').read_text())['route_samples']
def floor(x,y):
 p=Vector((x,y,.34))
 for i in range(16):
  hit,co,n,fi,o,m=s.ray_cast(dg,p,Vector((0,0,-1)),distance=1.05)
  if not hit:return None
  if 'fog' not in o.name.lower() and 'haze' not in o.name.lower() and n.z>.45:return float(co.z)
  p=co-Vector((0,0,.002))
 return None
rows=[]
for q in routes:
 x,y=q['xy'];rows.append(dict(route=q['route'],xy=[x,y],heights=[floor(x+dx,y+dy) for dx,dy in ((0,0),(.12,0),(-.12,0),(0,.12),(0,-.12))]))
(OUT/'route-baseline.json').write_text(json.dumps(dict(source_sha256=r['before_sha256'],samples=rows),indent=2));print('JOINT_ROUTE_BASELINE',len(rows),flush=True)
