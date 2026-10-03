import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent;D=json.loads((P/'evaluated-surfaces.json').read_text());N=json.loads((P/'native-independent.json').read_text())['objects'];S=json.loads((P/'surface-independent.json').read_text())['islands'];name='CD | Joined Checkin Counter Hatch / ivory';island=S[name][2];ivs=[Vector(D[name]['points'][i]) for i in island['indices']];idx={old:i for i,old in enumerate(island['indices'])};it=[[idx[i] for i in t] for t in island['triangles']];ib=BVHTree.FromPolygons(ivs,it,all_triangles=True);allnear=[]
for n,g in D.items():
 if n==name or N[n]['hide_render'] or N[n]['type']=='FONT':continue
 lo,hi=N[n]['bounds'];sep=[max(lo[k]-island['bounds'][1][k],island['bounds'][0][k]-hi[k],0) for k in range(3)]
 if sum(x*x for x in sep)>.1**2:continue
 vs=[Vector(p) for p in g['points']];b=BVHTree.FromPolygons(vs,g['triangles'],all_triangles=True);overlap=bool(ib.overlap(b));nearest=(0.,None,None) if overlap else (1e9,None,None)
 for p in ivs:
  loc,no,fi,dist=b.find_nearest(p,nearest[0])
  if loc is not None and dist<nearest[0]:nearest=(dist,list(p),list(loc))
 for p in vs:
  loc,no,fi,dist=ib.find_nearest(p,nearest[0])
  if loc is not None and dist<nearest[0]:nearest=(dist,list(loc),list(p))
 allnear.append({'object':n,'triangle_intersection':overlap,'distance_m':nearest[0],'notice_point':nearest[1],'external_point':nearest[2]})
allnear.sort(key=lambda x:x['distance_m']);scanner=[]
for i,side,kind in [(51,-1,'outer'),(52,-1,'inner'),(61,1,'inner'),(62,1,'outer')]:
 ix=S['CD | Joined Person Scanner Arch / steel'][i];rail=[Vector(D['CD | Joined Person Scanner Arch / steel']['points'][k]) for k in ix['indices']];column=[Vector(p) for p in D[f'Scanner portal column {side}']['points']];sx=side if kind=='outer' else -side;axis=Vector((sx*2,1,0)).normalized();railmin=min(p.dot(axis) for p in rail);colmax=max(p.dot(axis) for p in column);lower=railmin-colmax;scanner.append({'object':'CD | Joined Person Scanner Arch / steel','island':i,'kind':kind,'actual_column':f'Scanner portal column {side}','separating_axis':list(axis),'rail_min_projected':railmin,'column_max_projected':colmax,'all_surface_gap_lower_bound_m':lower,'rail_bounds':ix['bounds']})
# Rays through reassurance center into full scene, showing no immediate attachment.
ray=[]
for p,d in [([-3.51,3.58,1.65],[0,1,0]),([-3.51,3.62,1.65],[0,-1,0])]:
 hits=[]
 for n,g in D.items():
  if N[n]['hide_render'] or n==name or N[n]['type']=='FONT':continue
  b=BVHTree.FromPolygons([Vector(v) for v in g['points']],g['triangles'],all_triangles=True);loc,no,fi,dist=b.ray_cast(Vector(p),Vector(d),.05)
  if loc is not None:hits.append({'object':n,'point':list(loc),'distance_m':dist})
 ray.append({'origin':p,'direction':d,'range_m':.05,'hits':hits})
(P/'support-witness-independent.json').write_text(json.dumps({'notice':{'object':name,'island':2,'component_name':'CD | Worker reassurance glass notice','bounds':island['bounds'],'nearby_all_scene_actual_surfaces':allnear,'forward_reverse_backing_rays':ray},'scanner_separating_surface_witnesses':scanner},indent=2));print('ALL_SCENE_NOTICE',allnear);print('SCANNER_EXACT_SEPARATION',scanner)
