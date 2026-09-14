"""Broadphase all added bounds against foreign modules and reserved routes."""
import json,math
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];L=json.loads((ROOT/'production/LAYOUT.json').read_text());C=json.loads((ROOT/'exteriors/CURRENT.json').read_text())
def world(sid,b):
 p=L['placements'][sid];a=math.radians(p['rotation_z_degrees']);c,s=math.cos(a),math.sin(a);t=p['translation']
 pts=[(t[0]+c*x-s*y,t[1]+s*x+c*y,t[2]+z) for x in [b[0][0],b[1][0]] for y in [b[0][1],b[1][1]] for z in [b[0][2],b[1][2]]]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def overlap(a,b):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>.004 for i in range(3))
sources={}
for sid in C:
 s=json.loads((ROOT/'sources'/sid/'survey.json').read_text())
 rows=[(r['name'],world(sid,r['bounds'])) for r in s['records'] if r.get('bounds') and not r['hide_render'] and r['type']=='MESH']
 sources[sid]=([r[0] for r in rows],np.array([r[1] for r in rows]))
hits=[];route_hits=[]
for sid,rev in C.items():
 audit=json.loads((ROOT/'exteriors'/sid/f'audit-{rev}.json').read_text())
 for r in audit['records']:
  b=r['bounds_world']
  for other,(names,boxes) in sources.items():
   if other==sid:continue
   indices=np.nonzero(np.all(np.minimum(boxes[:,1,:],b[1])-np.maximum(boxes[:,0,:],b[0])>.004,axis=1))[0]
   matches=[names[i] for i in indices]
   if matches:hits.append({'section':sid,'object':r['name'],'foreign_section':other,'foreign_objects':matches[:8]})
  if b[0][2]>=2.4 or b[1][2]<=.10:continue
  for route in L['routes']:
   found=False
   for a,z in zip(route['points'],route['points'][1:]):
    if abs(a[2])>.1 or abs(z[2])>.1:continue
    dx,dy=z[0]-a[0],z[1]-a[1];d=math.hypot(dx,dy)
    if d<.01:continue
    for j in range(int(d/.2)+1):
     t=j/max(1,int(d/.2));x,y=a[0]+dx*t,a[1]+dy*t
     if min(math.dist((x,y,0),route['points'][0]),math.dist((x,y,0),route['points'][-1]))<4:continue
     for off in [-route['width_m']/2+.1,0,route['width_m']/2-.1]:
      px,py=x-dy/d*off,y+dx/d*off
      if b[0][0]<px<b[1][0] and b[0][1]<py<b[1][1]:found=True;break
     if found:break
    if found:break
   if found:route_hits.append({'section':sid,'object':r['name'],'route':route['id']})
report={'foreign_geometry_candidates':hits,'route_candidates':route_hits,'scope':'Conservative transformed object AABBs and 0.2m route samples; 4m endpoint transitions excluded. Candidates require exact mesh review, not proof of collisions. Source geometry remains untouched.'}
(ROOT/'production/EXTERIOR_LAYOUT_AUDIT.json').write_text(json.dumps(report,indent=2));print(json.dumps({'foreign_candidates':len(hits),'route_candidates':route_hits},indent=2))
