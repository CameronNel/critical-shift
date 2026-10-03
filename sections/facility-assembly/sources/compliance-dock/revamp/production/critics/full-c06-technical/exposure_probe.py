import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent;D=json.loads((P/'evaluated-surfaces.json').read_text());N=json.loads((P/'native-independent.json').read_text())['objects'];S=json.loads((P/'surface-independent.json').read_text())['islands'];G={n:BVHTree.FromPolygons([Vector(p) for p in g['points']],g['triangles'],all_triangles=True) for n,g in D.items() if g['triangles']};rows=[]
def rays(label,p,d,names=None,dist=2):
 out=[]
 for n in names or G:
  if N[n]['hide_render']:continue
  loc,normal,face,length=G[n].ray_cast(Vector(p),Vector(d),dist)
  if loc is not None:out.append({'object':n,'point':list(loc),'normal':list(normal),'triangle':face,'distance_m':length})
 out.sort(key=lambda x:x['distance_m']);rows.append({'label':label,'origin':p,'direction':d,'hits':out[:10]});return out
# exposure: rays from free space to actual surfaces (all geometry, beyond local counterparts).
for z in [.15,1.7,3.2]:rays('P2 center closure exposed front duplicate',[0,15.60,z],[0,1,0],dist=.2)
for x,z in [(-2.25,.2),(-2.25,3.2),(2.25,.2),(2.25,3.2)]:rays('P2 guide shoe and closure exposed coplanarity',[x,15.60,z],[0,1,0],dist=.2)
# paper top overlap point not covered by the third staggered page; .5mm strip near x=-3.99/y=7.31
for x,y in [(-3.835,7.14),(-3.97,7.247),(-3.70,7.04),(-3.95,7.309),(-3.98,7.10)]:rays('paper blotter overlap exposure',[x,y,.9],[0,0,-1],dist=.2)
# precise component face and support ray from rear scanner service details.
for side in [-1,1]:
 for x in [.619,.625,.631,.6375,.73,.8225,.829,.835,.841]:
  xx=x*side;rays('scanner rear strip true column backing',[xx,7.22,1.35],[0,-1,0],names=[f'Scanner portal column {side}','CD | Joined Person Scanner Arch / steel'],dist=.1)
 # non-tie height and tie height
 for z in [.56,1.22,1.88]:rays('scanner module rear seam backing',[.73*side,7.22,z],[0,-1,0],names=[f'Scanner portal column {side}','CD | Joined Person Scanner Arch / steel'],dist=.1)
# local island-specific surfaces to locate rear rail facing body and exact nearest distances
nearest=[]
for i in [51,52,53,54,55,61,62,63,64,65]:
 x=S['CD | Joined Person Scanner Arch / steel'][i];pts=[Vector(p) for p in D['CD | Joined Person Scanner Arch / steel']['points']];sample=Vector([(x['bounds'][0][j]+x['bounds'][1][j])*.5 for j in range(3)]);sample.y=x['bounds'][0][1];side=-1 if sample.x<0 else 1;loc,normal,face,length=G[f'Scanner portal column {side}'].find_nearest(sample);nearest.append({'object':'CD | Joined Person Scanner Arch / steel','island':i,'bounds':x['bounds'],'back_face_center':list(sample),'column_nearest':list(loc),'distance_m':length})
(P/'exposure-independent.json').write_text(json.dumps({'rays':rows,'scanner_nearest':nearest},indent=2));print('EXPOSURE_DONE');
for x in rows[:12]:print(x)
print('SCANNER_NEAREST',nearest)
