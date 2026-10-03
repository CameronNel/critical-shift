import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');P=R/'revamp/production';O=P/'critics/full-c07-technical';S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;D=bpy.context.evaluated_depsgraph_get();G={};cloth=[]
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(D);m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=D);m.calc_loop_triangles();ps=[o.matrix_world@x.co for x in m.vertices];ts=[tuple(t.vertices) for t in m.loop_triangles];G[o.name]=(ps,ts,o.hide_render)
 cut=m.uv_layers.get('CD_Fabric_Cut_1m')
 if cut:
  edges=[];areas=[];zero=0;finite=True;topw=0;topu=0;tw=0;tu=0
  nxny=o.get('textile_grid');limit=(nxny[0]+1)*(nxny[1]+1) if nxny else None
  for t in m.loop_triangles:
   p=[ps[i] for i in t.vertices];uv=[cut.data[i].uv.copy() for i in t.loops];w=(p[1]-p[0]).cross(p[2]-p[0]).length*.5;u=abs((uv[1]-uv[0]).cross(uv[2]-uv[0]))*.5;tw+=w;tu+=u
   if u==0:zero+=1
   if not all(math.isfinite(c) for pt in uv for c in pt):finite=False
   if limit and all(v<limit for v in t.vertices):topw+=w;topu+=u
   if w>1e-12:areas.append(u/w)
   for i in range(3):
    d=(p[(i+1)%3]-p[i]).length
    if d>.0001:edges.append((uv[(i+1)%3]-uv[i]).length/d)
  edges.sort();areas.sort();cloth.append({'object':o.name,'triangles':len(ts),'finite':finite,'zero_uv_triangles':zero,'world_area_m2':tw,'uv_area_m2':tu,'area_ratio':tu/tw,'top_world_area_m2':topw,'top_uv_area_m2':topu,'top_area_ratio':topu/topw if topw else None,'edge_ratio_min':edges[0],'edge_ratio_p01':edges[int(len(edges)*.01)],'edge_ratio_median':edges[len(edges)//2],'edge_ratio_p99':edges[int(len(edges)*.99)],'edge_ratio_max':edges[-1],'triangle_area_ratio_p01':areas[int(len(areas)*.01)],'triangle_area_ratio_p99':areas[int(len(areas)*.99)]})
 ev.to_mesh_clear()
(O/'consumed-textile-uv.json').write_text(json.dumps(cloth,indent=2))
pairs=json.loads((O/'coplanar-overlap.json').read_text())['pairs'];M=json.loads((P/'renders/full-cycle-07/manifest.json').read_text());views=[];cache={};data=bpy.data.cameras.new('TECHNICAL TEMP evidence camera');cam=bpy.data.objects.new('TECHNICAL TEMP evidence camera',data);S.collection.objects.link(cam)
for shot in M['shots']:
 hidden=set(shot['temporary_hidden_geometry']);key=tuple(sorted(hidden))
 if key not in cache:
  ps=[];ts=[];names=[]
  for n,(v,t,h) in G.items():
   if h or n in hidden:continue
   off=len(ps);ps.extend(v);ts.extend([tuple(i+off for i in tr) for tr in t]);names.extend([(n,i) for i in range(len(t))])
  cache[key]=(BVHTree.FromPolygons(ps,ts,all_triangles=True),names)
 tree,names=cache[key];cam.matrix_world=Matrix(shot['camera_matrix_world']);data.type=shot['projection'];data.lens=shot['actual_lens_mm'];data.sensor_width=36
 # Orthographic fixed evidence uses renderer source's fixed width.
 if data.type=='ORTHO':data.ortho_scale=shot.get('ortho_scale',21.5)
 shown=[]
 for i,pair in enumerate(pairs):
  if pair['a'][0] in hidden or pair['b'][0] in hidden:continue
  point=Vector(pair['center']);eye=cam.matrix_world.translation;direction=point-eye;dist=direction.length
  if direction.dot(Vector(pair['normal']))>=0:continue
  ndc=world_to_camera_view(S,cam,point)
  if ndc.z<=0 or not(0<=ndc.x<=1 and 0<=ndc.y<=1):continue
  direction.normalize();h=tree.ray_cast(eye,direction,dist+.0001)
  if h[0] is not None and abs(h[3]-dist)<.0001:
   shown.append({'pair_index':i,'a':pair['a'],'b':pair['b'],'overlap_m2':pair['same_orientation_overlap_m2'],'pixel':[ndc.x*1067,(1-ndc.y)*600],'center':pair['center'],'ray_first_hit':names[h[2]],'first_hit_distance_m':h[3],'target_distance_m':dist})
 views.append({'id':shot['id'],'projection':shot['projection'],'visible_coplanar_candidates':shown});print('view',shot['id'],len(shown),flush=True)
(O/'named-view-coplanar-visibility.json').write_text(json.dumps({'method':'ray to overlap centroid in current fixed beauty camera; respects each manifest cutaway hidden objects; tests same-facing hemisphere and FOV; .1mm first-hit tolerance; ORTHO visibility rays originate at camera eye (perspective approximation, excluded from decisive finding)','views':views},indent=2));bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data);print('DONE',flush=True)
