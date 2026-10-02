import bpy,json,importlib.util,math
from pathlib import Path
from mathutils import Vector
r=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');p=r/'revamp/production/critics/full-c03-technical'
spec=importlib.util.spec_from_file_location('v',r/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
dg=bpy.context.evaluated_depsgraph_get();shapes=[v.Shape(o,dg) for o in bpy.context.scene.objects if o.type in v.GEOMETRY_TYPES];by={s.name:s for s in shapes}
result=[]
for row in json.loads((p/'probe.json').read_text())['isolated_component_candidates']:
 a=by[row['object']];candidates=[]
 for b in shapes:
  if b==a or not b.bvh or not v.overlaps(a.bounds,b.bounds,.1):continue
  best=None;witness=None
  for sa,sb in ((a,b),(b,a)):
   for vert in sa.vertices:
    hit=sb.bvh.find_nearest(vert,.100001)
    if hit[0] is not None and (best is None or hit[3]<best):best=float(hit[3]);witness=[list(vert),list(hit[0])]
  if best is not None:
   # enclosed vertices explain insets without needing contacting outer surfaces
   samples=[a.vertices[i] for i in set((0,len(a.vertices)//4,len(a.vertices)//2,3*len(a.vertices)//4,len(a.vertices)-1))]
   contained=sum(b.contains(vert) for vert in samples)
   candidates.append({'other':b.name,'same_assembly':a.owner==b.owner,'distance_m':best,'witness':witness,'sample_vertices_inside_other':contained,'sample_count':len(samples)})
 result.append({**row,'nearest_candidates':sorted(candidates,key=lambda x:x['distance_m'])[:8]})
# Test the physical fabric chart continuity across shared mesh edges by vertex UV consistency.
o=bpy.data.objects['Covered Trolley Draped Tarp'];me=o.data;layer=me.uv_layers['CD_Fabric_Cut_1m'];byvert={};seams=0
for poly in me.polygons:
 for i in poly.loop_indices:
  vi=me.loops[i].vertex_index;uv=layer.data[i].uv
  if vi in byvert and (uv-byvert[vi]).length>1e-6:seams+=1
  else:byvert[vi]=uv.copy()
(p/'bearing-candidates.json').write_text(json.dumps({'isolated_candidates':result,'woven_chart':{'vertex_chart_discontinuities':seams,'source_vertices':len(me.vertices),'source_loops':len(me.loops),'consumed_uv':'CD_Fabric_Cut_1m'}},indent=2));print('BEARINGS_COMPLETE',len(result),'woven_chart_discontinuities',seams)
