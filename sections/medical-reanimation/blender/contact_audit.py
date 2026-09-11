"""Read-only construction audit; evaluated AABB adjacency flags disconnected parts for inspection."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();g={}
for o in s.objects:
 if o.type not in {'MESH','CURVE'}:continue
 e=o.evaluated_get(dg);me=e.to_mesh();v=[e.matrix_world@v.co for v in me.vertices]
 if v:g[o.name]={'lo':[min(p[i] for p in v) for i in range(3)],'hi':[max(p[i] for p in v) for i in range(3)],'object':o}
 e.to_mesh_clear()
def gap(a,b):return math.sqrt(sum(max(0,a['lo'][i]-b['hi'][i],b['lo'][i]-a['hi'][i])**2 for i in range(3)))
isolated=[]
for n,a in g.items():
 nearest=min(((gap(a,b),k) for k,b in g.items() if k!=n),default=(999,None))
 if nearest[0]>.008:isolated.append({'object':n,'nearest_gap':nearest[0],'nearest_object':nearest[1]})
dest=R/'production/validation'/s.get('revision','unknown');dest.mkdir(parents=True,exist_ok=True)
(dest/'contact_candidates.json').write_text(json.dumps({'method':'All mesh/curve evaluated AABB adjacency at 8mm; conservative candidate screen, not proof of internal mesh contact. Text is audited separately.','isolated':isolated},indent=2));print('CONTACT_CANDIDATES',len(isolated),isolated)
