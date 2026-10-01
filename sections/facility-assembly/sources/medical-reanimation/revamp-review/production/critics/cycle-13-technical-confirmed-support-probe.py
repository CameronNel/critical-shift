"""Specific intended-support rays for six confirmed inherited-assembly families."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');O=R/'revamp-review/production/critics';source=Path('/workspace/scratch/medical-skill-full-cycle13.blend');sha=hashlib.sha256(source.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(source),link=False) as(a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
graph=json.loads((O/'cycle-13-technical-whole-contact-probe.json').read_text());nodes=graph['nodes'];allclusters=graph['clusters']
def geom(o):
 ev=o.evaluated_get(dep);m=ev.to_mesh();pts=[o.matrix_world@v.co for v in m.vertices];tree=BVHTree.FromPolygons(pts,[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return tree
trees={};records=[]
def probe(family,name,target,p,direction):
 o=s.objects[name];t=s.objects[target]
 for x in (o,t):
  if x.name not in trees:trees[x.name]=geom(x)
 own=trees[name];tree=trees[target];p=Vector(p);d=Vector(direction)
 ownpoint=own.find_nearest(p)[0];q,n,fi,distance=tree.ray_cast(ownpoint,d,.5)
 nearest=tree.find_nearest(ownpoint)
 cluster=next(c for c in allclusters if any(nodes[i]['object']==name for i in c['nodes']))
 ids=set(cluster['nodes']);lower=math.inf;lower_pair=None
 # Exhaustive AABB separation from all outside nonarchitectural islands.
 for i in ids:
  a=nodes[i]
  for j,b in enumerate(nodes):
   if j in ids:continue
   gap=math.sqrt(sum(max(a['lo'][k]-b['hi'][k],b['lo'][k]-a['hi'][k],0)**2 for k in range(3)))
   if gap<lower:lower=gap;lower_pair=[a['name'],b['name']]
 members=[{'object':nodes[i]['object'],'island':nodes[i]['island_ids'],'node':i} for i in sorted(ids)]
 record={'family':family,'object':name,'target':target,'part_surface_world':list(ownpoint),'part_surface_local':list(o.matrix_world.inverted()@ownpoint),'coordinate_parent':o.parent.name if o.parent else None,'part_surface_parent_local':list(o.parent.matrix_world.inverted()@ownpoint) if o.parent else list(ownpoint),'OCRU_local':list(s.objects['OCRU'].matrix_world.inverted()@ownpoint) if family in {'suit_service','jamb_fixings'} else None,'support_surface_world':list(q) if q is not None else None,'support_surface_target_local':list(t.matrix_world.inverted()@q) if q is not None else None,'direction_world':list(d),'ray_gap_m':distance,'nearest_surface_m':nearest[3],'source_surface_witness_distance_m':own.find_nearest(ownpoint)[3],'cluster_islands':len(ids),'cluster_rooted':cluster['rooted'],'cluster_members':members,'outside_island_AABB_lower_bound_m':lower,'outside_island_lower_bound_pair':lower_pair,'status':'CONFIRMED_DETACHED' if not cluster['rooted'] and lower>.005001 and distance is not None and distance>.005 else 'UNCONFIRMED'}
 records.append(record);print('CONFIRMED_SUPPORT',name,'to',target,'gap',distance,'cluster',len(ids),'lower',lower,record['status'],flush=True)
probe('battery','Battery supported drawer rail','Reserve folded back',(-2.15,8.935,.30),(0,1,0))
probe('battery','Battery supported drawer rail.001','Reserve folded back',(-2.15,8.935,.71),(0,1,0))
probe('cabinet_panes','Clear cabinet sliding pane','Cabinet formed edge',(3.261,8.37,1.89),(1,0,0))
probe('cabinet_panes','Clear cabinet sliding pane.001','Cabinet formed edge.001',(3.261,6.57,1.89),(1,0,0))
probe('suit_service','Suit service enclosure','Jamb folded cover.001',(-1.48875,6.4,1.25),(0,1,0))
probe('recovery_plaque','Engraved backing RECOVERY.001','Identity wall spacer',(3.974,4.7,1.75),(1,0,0))
probe('supplies_plaque','Engraved backing SUPPLIES','Identity wall spacer.001',(3.974,1.47,1.75),(1,0,0))
for suffix,z,target in [('',.55,'Jamb folded cover'),('.002',2.18,'Jamb folded cover'),('.003',.55,'Jamb folded cover.001'),('.005',2.18,'Jamb folded cover.001')]:
 o=s.objects['Jamb captive fastener'+suffix];p=o.matrix_world.translation.copy();p.x=min((o.matrix_world@Vector(v)).x for v in o.bound_box);probe('jamb_fixings',o.name,target,p,(-1,0,0))
result={'source_sha256':sha,'source_path':str(source),'records':records,'family_count':len(set(x['family'] for x in records)),'confirmed_records':sum(x['status']=='CONFIRMED_DETACHED' for x in records),'source_saved':False,'limits':['Ray witnesses measure specified intended mechanisms. Other graph suspects are not elevated to confirmed findings.','Outside-island AABB lower bound is exhaustive over every nonarchitectural island. Architectural targets were separately tested in whole-contact-probe; no root contact was found.']}
(O/'cycle-13-technical-confirmed-support-probe.json').write_text(json.dumps(result,indent=2)+'\n')
