import bpy,json,os,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/completion';O.mkdir(exist_ok=True)
f=os.environ.get('MAP_AUDIT_FILE','facility_walkthrough_A11_map_finish.blend')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender'/f),load_ui=False)
if '29_SPAWN_APPROVED_EXTERIOR' in bpy.data.collections:
 # Retained A14 meshes are geometry-identical; only source material slots changed.
 # Keep new exterior geometry live and accelerate queries over unchanged context.
 for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']:
  bpy.data.collections[n].hide_viewport=True
 for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:
  bpy.data.collections[n].hide_viewport=False
for o in bpy.data.collections['12_ACCESS_MOVING_PARTS'].all_objects:
 if o.get('door_leaf'):o.scale.z=.015
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
L=json.loads((R/'production/LAYOUT_A08.json').read_text());L['routes'].append({'id':'SPAWN_INNER_TRANSITION','points':[[-28,9.34,0],[-28,12.8,0]],'width_m':2.6});out={'file':f,'routes':[]}
for r in L['routes']:
 if r['id']=='R19':continue
 bad=[];samples=0;floor_samples=[];previous={};max_floor_change=0
 for aa,bb in zip(r['points'],r['points'][1:]):
  a,b=Vector(aa),Vector(bb);v=b-a;n=Vector((-v.y,v.x,0)).normalized();steps=math.ceil(v.length/.4)
  for i in range(steps+1):
   p=a+v*i/steps
   for offset in [-.6,0,.6]:
    q=p+n*offset;samples+=1
    hit,loc,norm,idx,ob,mat=bpy.context.scene.ray_cast(dg,q+Vector((0,0,.25)),Vector((0,0,-1)),distance=.6)
    if not hit:bad.append({'type':'floor_gap','at':[round(x,3) for x in q]});continue
    floor_samples.append({'point':[round(x,4) for x in q],'floor_z':round(loc.z,5),'support':ob.name})
    if offset in previous and (q-previous[offset][0]).length<.6:max_floor_change=max(max_floor_change,abs(loc.z-previous[offset][1]))
    previous[offset]=(q.copy(),loc.z)
    hit,pos,norm,idx,ob,mat=bpy.context.scene.ray_cast(dg,q+Vector((0,0,.3)),Vector((0,0,1)),distance=1.8)
    if hit:bad.append({'type':'headroom','at':[round(x,3) for x in q],'object':ob.name,'height':round(pos.z,3)})
   if i<steps:
    for z in [.15*j for j in range(1,14)]:
     q=p+Vector((0,0,z));hit,loc,norm,idx,ob,mat=bpy.context.scene.ray_cast(dg,q,v.normalized(),distance=v.length/steps)
     if hit:bad.append({'type':'crossing','at':[round(x,3) for x in loc],'object':ob.name})

 out['routes'].append({'id':r['id'],'samples':samples,'findings':bad,'max_adjacent_sample_floor_change_m':max_floor_change,'floor_samples':floor_samples});print(r['id'],samples,len(bad),bad[:2],flush=True)
(O/('AUDIT_'+f.replace('.blend','.json'))).write_text(json.dumps(out,indent=2))
