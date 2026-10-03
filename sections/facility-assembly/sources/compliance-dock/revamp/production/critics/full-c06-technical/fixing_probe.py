import bpy,json,collections,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/critics/full-c06-technical');D=json.loads((O/'evaluated-surfaces.json').read_text());N=json.loads((O/'native-independent.json').read_text())['objects'];S=json.loads((O/'surface-independent.json').read_text());groups=collections.defaultdict(list)
def root(n):
 while n:
  o=N[n]
  if o['properties'].get('support_class')=='supported_assembly':return n
  n=o['parent']
 return None
for name,g in D.items():
 if N[name]['type']=='FONT':continue
 r=root(name)
 if not r:continue
 vs=[Vector(p) for p in g['points']]
 islands=S['islands'].get(name,[{'indices':list(range(len(vs))),'triangles':g['triangles'],'bounds':N[name]['bounds']}])
 for k,x in enumerate(islands):
  points=[vs[i] for i in x['indices']];index={old:i for i,old in enumerate(x['indices'])};ts=[[index[i] for i in t] for t in x['triangles']];b=BVHTree.FromPolygons(points,ts,all_triangles=True);groups[r].append({'name':name,'island':k,'points':points,'bvh':b,'bounds':x['bounds'],'triangles':len(ts)})
rows=[];pairs=[]
for root,items in groups.items():
 for i,a in enumerate(items):
  candidates=[]
  for j,b in enumerate(items):
   if i==j:continue
   sep=[max(a['bounds'][0][k]-b['bounds'][1][k],b['bounds'][0][k]-a['bounds'][1][k],0) for k in range(3)]
   if sum(x*x for x in sep)>.04**2:continue
   if a['bvh'].overlap(b['bvh']):dist=0.;closest=None
   else:
    dist=1e9;closest=None
    for p in a['points']:
     loc,no,face,length=b['bvh'].find_nearest(p,dist)
     if loc is not None and length<dist:dist=length;closest=[list(p),list(loc)]
    # reverse too; vertex-to-face minima can miss edge-edge gaps. Explicitly bounded by this limitation.
    for p in b['points']:
     loc,no,face,length=a['bvh'].find_nearest(p,dist)
     if loc is not None and length<dist:dist=length;closest=[list(loc),list(p)]
   candidates.append({'other_object':b['name'],'other_island':b['island'],'distance_m':dist,'nearest_points':closest})
  candidates.sort(key=lambda x:x['distance_m'])
  rows.append({'assembly':root,'object':a['name'],'island':a['island'],'bounds':a['bounds'],'triangles':a['triangles'],'nearest_assembly_surfaces':candidates[:4],'no_contact_within_5mm':not candidates or candidates[0]['distance_m']>.005001})
(O/'fixings-independent.json').write_text(json.dumps({'islands_measured':len(rows),'method':'Connected evaluated triangle islands; BVH triangle intersections plus bidirectional vertex to actual polygon distances; broadphase <=40mm; nearest distance can overestimate edge-edge gap and is treated only as investigation cue. Text geometry excluded.','islands':rows},indent=2))
print('FIXING_DONE',len(rows));print('DETACHED_CUES',sum(x['no_contact_within_5mm'] for x in rows))
for x in rows:
 if x['no_contact_within_5mm']:print(x['assembly'],x['object'],x['island'],x['bounds'],x['nearest_assembly_surfaces'][:1])
