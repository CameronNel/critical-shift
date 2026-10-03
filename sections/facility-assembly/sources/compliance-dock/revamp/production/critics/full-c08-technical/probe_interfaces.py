import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');O=R/'revamp/production/critics/full-c08-technical';S=R/'module_overhaul_R1.blend';H='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False);bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def ray(names,p,d):
 hits=[]
 for name in names:
  ob=sc.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ob.matrix_world@q.co for q in me.vertices];t=[tuple(q.vertices) for q in me.loop_triangles];b=BVHTree.FromPolygons(v,t,all_triangles=True)
  q,n,fi,dist=b.ray_cast(Vector(p),Vector(d),30)
  if q is not None:hits.append({'object':name,'surface_point':list(q),'normal':list(n),'triangle':fi,'distance_m':dist})
  ev.to_mesh_clear()
 return min(hits,key=lambda h:h['distance_m']) if hits else None
defs=[('P1',2.4,2.6,(0,-.12,1.3),['South wall west'],['South wall east'],['South lintel P1']),('P2 sealed frame',4.6,3.5,(0,15.9,1.6),['P2 frame jamb -1'],['P2 frame jamb 1'],['P2 frame head lintel']),('D1 frame',1.05,2.2,(-5.4,3.6,1.1),['D1 frame jamb -1'],['D1 frame jamb 1'],['D1 frame head']),('D2 frame',1.05,2.2,(-5.4,9.6,1.1),['D2 frame jamb -1'],['D2 frame jamb 1'],['D2 frame head']),('worker scanner',1.2,2.25,(0,7,1.1),['Scanner portal column -1'],['Scanner portal column 1'],['Scanner portal lintel'])]
rows=[]
for name,cw,ch,p,left,right,head in defs:
 l=ray(left,p,(-1,0,0));r=ray(right,p,(1,0,0));h=ray(head,p,(0,0,1));f=ray(['Floor slab'],p,(0,0,-1))
 rows.append({'name':name,'contract_width_m':cw,'contract_height_m':ch,'ray_from_world':p,'left':l,'right':r,'head':h,'floor':f,'measured_width_m':l['distance_m']+r['distance_m'] if l and r else None,'measured_height_m':h['distance_m']+f['distance_m'] if h and f else None,'interpretation':'Frame surfaces only; sealed/openable leaves and hardware excluded explicitly. This does not prove a runtime opening.'})
rows.append({'name':'floor datum','hit':ray(['Floor slab'],(0,10,1),(0,0,-1))})
rows.append({'name':'interior side faces','west':ray(['West perimeter wall'],(0,10,1),(-1,0,0)),'east':ray(['East perimeter wall'],(0,10,1),(1,0,0))})
report={'source_sha256':H,'contract_sha256':hashlib.sha256((R/'contracts/interface.json').read_bytes()).hexdigest(),'independent_surface_rays':rows}
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
(O/'interfaces.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
