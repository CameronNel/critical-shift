import bpy,json,importlib.util
from pathlib import Path
r=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');p=r/'revamp/production/critics/full-c03-technical';spec=importlib.util.spec_from_file_location('v',r/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
dg=bpy.context.evaluated_depsgraph_get();shapes=[v.Shape(o,dg) for o in bpy.context.scene.objects if o.type in v.GEOMETRY_TYPES];by={s.name:s for s in shapes};q=json.loads((p/'probe.json').read_text());results=[]
selected=['P2 blast leaf west','P2 blast leaf east','P2 frame head lintel','P2 frame jamb -1','P2 frame jamb 1','Key box glass','Key box label']+[s.name for s in shapes if ('Scanner plate' in s.name or 'Scanner txt' in s.name)]
for name in selected:
 a=by[name];candidates=[]
 for b in shapes:
  if b==a or not b.bvh or not v.overlaps(a.bounds,b.bounds,.12):continue
  overlap=a.bvh.overlap(b.bvh);best=0. if overlap else None;witness=None
  for sa,sb in ((a,b),(b,a)):
   for vertex in sa.vertices:
    h=sb.bvh.find_nearest(vertex,.120001)
    if h[0] is not None and (best is None or h[3]<best):best=float(h[3]);witness=[list(vertex),list(h[0])]
  if best is not None:candidates.append({'other':b.name,'same_assembly':a.owner==b.owner,'gap_m':best,'overlap_triangles':len(overlap),'witness':witness})
 results.append({'object':name,'bounds':[list(x) for x in a.bounds],'nearest':sorted(candidates,key=lambda x:x['gap_m'])[:10]})
# Separate cloth top/bottom faces (2mm solidification rim uses an intentional separate chart).
o=bpy.data.objects['Covered Trolley Draped Tarp'];me=o.data;layer=me.uv_layers['CD_Fabric_Cut_1m'];xy=[(v.co.x,v.co.y) for v in me.vertices];xmin=min(x for x,y in xy);xmax=max(x for x,y in xy);ymin=min(y for x,y in xy);ymax=max(y for x,y in xy);byvertex={}
for face in me.polygons:
 # Rim quads have vertices sharing XY positions. Exclude the thin solidified edge strip.
 if min((me.vertices[face.vertices[(i+1)%len(face.vertices)]].co-me.vertices[face.vertices[i]].co).length for i in range(len(face.vertices)))<.0021:continue
 for i in face.loop_indices:byvertex.setdefault(me.loops[i].vertex_index,[]).append(layer.data[i].uv.copy())
bad=[]
for i,uvs in byvertex.items():
 if max((a-b).length for a in uvs for b in uvs)>1e-6:bad.append(i)
(p/'focus-extra.json').write_text(json.dumps({'bearing_targets':results,'fabric_main_face_chart_discontinuous_vertices':bad,'source_mesh_name':me.name},indent=2));print('FOCUS_COMPLETE',len(results),'cloth_main_seams',len(bad))
