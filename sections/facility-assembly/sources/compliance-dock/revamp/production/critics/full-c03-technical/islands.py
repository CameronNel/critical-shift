import bpy,json,importlib.util,hashlib
from pathlib import Path
r=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');p=r/'revamp/production/critics/full-c03-technical'
spec=importlib.util.spec_from_file_location('v',r/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
dg=bpy.context.evaluated_depsgraph_get();shapes=[v.Shape(o,dg) for o in bpy.context.scene.objects if o.type in v.GEOMETRY_TYPES];by={s.name:s for s in shapes};q=json.loads((p/'probe.json').read_text());val=json.loads((p/'validator.json').read_text());cand=json.loads((p/'bearing-candidates.json').read_text())
result=[]
for assembly in q['internal_surface_contacts']:
 name=assembly['assembly'];parts={s.name:s for s in shapes if s.owner and s.owner.name==name};adj={k:set() for k in parts}
 for c in assembly['contact_pairs']:adj[c['a']].add(c['b']);adj[c['b']].add(c['a'])
 for c in cand['isolated_candidates']:
  if c['assembly']!=name:continue
  for target in c['nearest_candidates']:
   if target['same_assembly'] and target['sample_vertices_inside_other']==target['sample_count']:
    adj[c['object']].add(target['other']);adj[target['other']].add(c['object'])
 anchors={x['nearest_component'] for x in val['support_table'] if x['assembly']==name and x['status']=='pass'}
 seen=set()
 for start in parts:
  if start in seen:continue
  group=set();todo=[start]
  while todo:
   k=todo.pop()
   if k in group:continue
   group.add(k);todo.extend(adj[k]-group)
  seen.update(group)
  if group&anchors:continue
  # Independently grounded component groups can legitimately contact an external target.
  hits=[]
  for k in group:
   a=by[k]
   for b in shapes:
    if b.name in parts or not b.bvh or not v.overlaps(a.bounds,b.bounds,.00501):continue
    overlaps=a.bvh.overlap(b.bvh);best=0. if overlaps else None
    if best is None:
     for sa,sb in ((a,b),(b,a)):
      for vertex in sa.vertices:
       h=sb.bvh.find_nearest(vertex,.00501)
       if h[0] is not None and (best is None or h[3]<best):best=float(h[3])
    if best is not None:hits.append({'object':k,'external':b.name,'gap_m':best})
  result.append({'assembly':name,'component_island':sorted(group),'external_contacts':hits,'has_external_contact':bool(hits)})
# Woven chart seams: show location and maximum uv mismatch for source vertex.
o=bpy.data.objects['Covered Trolley Draped Tarp'];me=o.data;layer=me.uv_layers['CD_Fabric_Cut_1m'];byvert={}
for poly in me.polygons:
 for i in poly.loop_indices:byvert.setdefault(me.loops[i].vertex_index,[]).append(layer.data[i].uv.copy())
seams=[]
for i,uvs in byvert.items():
 delta=max((a-b).length for a in uvs for b in uvs)
 if delta>1e-6:seams.append({'vertex':i,'co':list(me.vertices[i].co),'max_uv_delta':delta,'loop_uvs':[list(x) for x in uvs]})
(p/'islands.json').write_text(json.dumps({'unsupported_island_candidates':[x for x in result if not x['has_external_contact']],'all_non_anchor_islands':result,'woven_seam_vertices':seams,'native_hash':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()},indent=2));print('ISLANDS_COMPLETE',len(result),len([x for x in result if not x['has_external_contact']]),'seamverts',len(seams))
