"""Read-only evaluated-bounds connectivity broadphase. Not an exact support validator."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'exterior-R08.blend'),load_ui=False)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
ext=bpy.data.collections['EXTERIOR_compliance-dock']
original=bpy.data.objects['READ_ONLY_ORIGINAL_compliance-dock'].instance_collection
# Only render-visible mesh geometry; lights/cameras/curves do not establish support.
def bounds(ob):
 eo=ob.evaluated_get(dg);pts=[eo.matrix_world@Vector(p) for p in eo.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def separation(a,b):
 gaps=[max(0,a[0][i]-b[1][i],b[0][i]-a[1][i]) for i in range(3)]
 return math.sqrt(sum(x*x for x in gaps)),gaps
added=[o for o in ext.objects if o.type=='MESH' and not o.hide_render]
roots=[o for o in original.all_objects if o.type=='MESH' and not o.hide_render]
objs=added+roots;bs=[bounds(o) for o in objs];n=len(added);adj=[[] for _ in added];root_hits=[[] for _ in added]
for i in range(n):
 for j in range(i+1,len(objs)):
  dist,gaps=separation(bs[i],bs[j])
  if dist<=.005+1e-6:
   if j<n:adj[i].append(j);adj[j].append(i)
   else:root_hits[i].append(j)
connected=set(i for i in range(n) if root_hits[i]);todo=list(connected)
while todo:
 i=todo.pop()
 for j in adj[i]:
  if j not in connected:connected.add(j);todo.append(j)
unseen=set(range(n))-connected;components=[]
while unseen:
 start=unseen.pop();comp={start};todo=[start]
 while todo:
  i=todo.pop()
  for j in adj[i]:
   if j in unseen:unseen.remove(j);comp.add(j);todo.append(j)
 nearest=[]
 for i in comp:
  options=[]
  for j in list(connected)+list(range(n,len(objs))):
   dist,gaps=separation(bs[i],bs[j]);options.append((dist,j,gaps))
  for dist,j,gaps in sorted(options)[:3]:nearest.append({'object':objs[i].name,'candidate_support':objs[j].name,'candidate_is_original':j>=n,'aabb_distance_m':dist,'axis_gaps_m':gaps})
 components.append({'objects':[objs[i].name for i in sorted(comp)],'nearest_root_connected_candidates':sorted(nearest,key=lambda r:r['aabb_distance_m'])[:6]})
report={'revision':'R08','scope':'Evaluated world-AABB connectivity broadphase, not raycast/anchor/support-angle validation. Original render-visible mesh objects are root candidates; physical/collision suitability is not independently classified. AABB overlap can be empty space, contact does not imply load-bearing support, and deep penetration is accepted by this connectivity graph. Text/curves excluded. Model is not saved.','threshold_m':.005,'numerical_epsilon_m':.000001,'additive_mesh_count':n,'original_root_candidate_count':len(roots),'root_connected_additive_count':len(connected),'detached_components':components,'direct_original_candidates':[{'object':objs[i].name,'original_candidates':[objs[j].name for j in root_hits[i]]} for i in range(n) if root_hits[i]],'additive_bounds':[{'name':objs[i].name,'bounds':bs[i]} for i in range(n)]}
(out/'support-connectivity-R08.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['direct_original_candidates','additive_bounds']},indent=2))

