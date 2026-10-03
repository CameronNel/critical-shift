"""Read-only exact convex clipping of selected measured destructive-crossing candidates."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;DG=bpy.context.evaluated_depsgraph_get()
def shape(name):
 O=S.objects[name];E=O.evaluated_get(DG);M=E.to_mesh();M.calc_loop_triangles();V=[O.matrix_world@v.co for v in M.vertices];T=[tuple(t.vertices)for t in M.loop_triangles];E.to_mesh_clear();return V,T
def clip(poly,n,d):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=n.dot(a)-d;db=n.dot(b)-d
  if da<=1e-8:out.append(a)
  if (da>1e-8)!=(db>1e-8):out.append(a+(b-a)*(da/(da-db)))
 return out
def area(poly):return sum((poly[i]-poly[0]).cross(poly[i+1]-poly[0]).length/2 for i in range(1,len(poly)-1)) if len(poly)>2 else 0.
def measurement(subject,target):
 V,T=shape(subject);W,U=shape(target);planes={};convex=True
 for t in U:
  a,b,c=[W[i]for i in t];n=(b-a).cross(c-a).normalized();d=n.dot(a)
  if any(n.dot(w)-d>2e-6 for w in W):convex=False
  planes[tuple(round(x,7)for x in [*n,d])]=(n,d)
 result={'subject':subject,'target':target,'target_convex':convex,'target_unique_planes':len(planes),'penetrating_surface_area_m2':None,'triangle_witnesses':[]}
 if not convex:return result
 total=0.
 for tid,t in enumerate(T):
  poly=[V[i]for i in t]
  for n,d in planes.values():
   poly=clip(poly,n,d)
   if not poly:break
  ar=area(poly)
  if ar>1e-10:
   total+=ar;result['triangle_witnesses'].append({'triangle':tid,'clipped_area_m2':ar,'clipped_polygon':[list(v)for v in poly]})
 result['penetrating_surface_area_m2']=total;return result
pairs=[(f'Truss diag B {y}_0.8','Main ventilation supply trunk')for y in ['2.2','5.2','8.2','11.2','13.9']]
pairs+=[('CD | Joined CD | Warm Fluorescent SW suspended fixture / steel','Return ventilation trunk')]
rows=[measurement(a,b)for a,b in pairs]
(P/'crossing-area.json').write_text(json.dumps({'method':'Every subject evaluated triangle clipped against all target outward halfspaces; targets independently checked convex against every evaluated vertex. Areas are actual subject surface embedded in target solid, not overlap volume; intended embedded fixings must be classified separately.','measurements':rows},indent=2));print('CLIPPED_AREAS',[(r['subject'],r['penetrating_surface_area_m2'])for r in rows],flush=True)
