import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'exteriors/reactor-room'
bpy.ops.wm.open_mainfile(filepath=str(out/'exterior-R02.blend'),load_ui=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
frame=(Matrix.Translation((8.4,-8.4,0))@Matrix.Rotation(math.radians(-135),4,'Z')).inverted()
lo=(-2.5,0,0);hi=(2.5,3.7,5);hits=[];candidates=[]
def clip(poly,axis,value,sign):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a[axis]-value);db=sign*(b[axis]-value)
  if da>=0:result.append(a)
  if (da>=0)!=(db>=0):result.append(a+(b-a)*(da/(da-db)))
 return result
for o in bpy.data.collections['EXTERIOR_reactor-room'].objects:
 if o.type not in ['MESH','FONT','CURVE']:continue
 eo=o.evaluated_get(dg);me=eo.to_mesh();vs=[frame@eo.matrix_world@v.co for v in me.vertices]
 if all(min(max(v[i] for v in vs),hi[i])-max(min(v[i] for v in vs),lo[i])>.003 for i in range(3)):
  candidates.append(o.name);count=0
  for f in me.polygons:
   poly=[vs[i] for i in f.vertices]
   for axis in range(3):
    poly=clip(poly,axis,lo[axis]+.003,1) if poly else []
    poly=clip(poly,axis,hi[axis]-.003,-1) if poly else []
   if len(poly)>=3 and sum((poly[i]-poly[0]).cross(poly[i+1]-poly[0]).length for i in range(1,len(poly)-1))>1e-10:count+=1
  if count:hits.append({'object':o.name,'clipped_faces':count})
 eo.to_mesh_clear()
r={'revision':'R02','portal_frame':'T(8.4,-8.4,0) Rz(-135deg)','box':[lo,hi],'inset_tolerance_m':.003,'bound_candidates':candidates,'surface_intrusions':hits,'scope':'Evaluated polygon clipping to inset portal box; no solid-containment test. All additive meshes/fonts/curves included.','samples':[]}
for n in ['Reactor exterior Shell 1 field','Shell 1 field']:
 o=bpy.data.objects[n];r['samples'].append({'name':n,'location':list(o.location),'matrix':[list(v) for v in o.matrix_world],'parent':o.parent.name if o.parent else None})
(out/'diagonal-portal-R02.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
