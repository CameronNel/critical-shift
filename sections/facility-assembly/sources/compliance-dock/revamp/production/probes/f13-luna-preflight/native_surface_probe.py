import bpy,hashlib,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend')
SOURCE=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/full_repairs.py')
EXPECTED='73b85e9a84b577d2059a07371abd366666536800eb45c9e56a7d7788a21b77a3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(BLEND)!=EXPECTED:raise RuntimeError('f12 source hash changed')
bpy.ops.wm.open_mainfile(filepath=str(BLEND),load_ui=False)
S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def evaluated_surface(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];polys=[list(p.vertices) for p in me.polygons];tree=BVHTree.FromPolygons(pts,polys,all_triangles=False);ev.to_mesh_clear();return tree,pts
cache={}
def tree(name):
 if name not in cache:cache[name]=evaluated_surface(S.objects[name])[0]
 return cache[name]
def ray(label,target,origin,direction,dist=.1):
 h=tree(target).ray_cast(Vector(origin),Vector(direction),dist)
 return {'label':label,'target':target,'origin':list(origin),'direction':list(direction),'distance_m':float(h[3]) if h[0] is not None else None,'hit_m':list(h[0]) if h[0] is not None else None,'normal':list(h[1]) if h[1] is not None else None}
def bounds(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
R={'f12_sha256':sha(BLEND),'repair_sha256':sha(SOURCE),'blender':bpy.app.version_string,'mode':'read-only native surfaces plus analytical proposed bounds; no full source builder/native save'}
# Proposed reassurance backing exact source dims/location and observed notice/glass surfaces.
R['notice']={'notice_island_bounds_f12_m':[[-3.704999924,3.590500117,1.600000024],[-3.315000057,3.591500044,1.699999928]],'proposed_backing_bounds_m':[[-3.717,3.5915,1.593],[-3.303,3.5995,1.707]],'glass_object_bounds_f12_m':bounds(S.objects['Hatch speaking aperture plate']),'notice_to_backing_rays':[],'backing_to_notice_rays':[],'clip_to_glass_rays':[],'backing_to_clip_rays':[],'glass_intersection_depth_m':0.008}
notice='CD | Joined Checkin Counter Hatch / ivory'
for x in [-3.69,-3.33]:
 for z in [1.61,1.69]:
  R['notice']['notice_to_backing_rays'].append(ray('notice back y=3.5915 to proposed backing',notice,(x,3.5715,z),(0,1,0),.05))
  R['notice']['backing_to_notice_rays'].append(ray('proposed backing y=3.5915 to actual notice',notice,(x,3.6115,z),(0,-1,0),.05))
# The source folded clip bounds Y=[3.5995,3.6135], Z=[1.545,1.658], X centered at +/-0.194 from center.
for x in [-3.704,-3.316]:
 R['notice']['clip_to_glass_rays'].append(ray('clip meets glass at y=3.6075', 'Hatch speaking aperture plate',(x,3.6275,1.56),(0,-1,0),.05))
 R['notice']['backing_to_clip_rays'].append({'x':x,'proposed_backing_front_y_m':3.5995,'clip_face_y_m':3.5995,'gap_m':0.0})
# Move text transform in-memory to proposed y to inspect its world extent vs backing; restore immediately.
R['notice']['proposed_text_bounds_m']={}
for n in ['CD | Reassurance headline','CD | Reassurance qualification']:
 o=S.objects[n];old=o.location.copy();o.location.y=3.59042;bpy.context.view_layer.update();R['notice']['proposed_text_bounds_m'][n]=bounds(o);o.location=old;bpy.context.view_layer.update()
# Scanner rails: source-recipe outputs at X +/-0.808,+/-0.652, Y back 7.180, full z .21..2.49.
R['scanner']={'proposed_edges':[],'proposed_seams':[]}
for x in [-.808,-.652,.652,.808]:
 for z in [.21,.55,1.35,2.15,2.49]:
  row=ray('proposed edge back Y7.180 to actual scanner column','Scanner portal column '+str(-1 if x<0 else 1),(x,7.14,z),(0,1,0),.08)
  row['part_back_y_m']=7.180;row['signed_clearance_part_to_surface_m']=None if row['hit_m'] is None else 7.180-row['hit_m'][1];row['part_x_center_m']=x;row['z_sample_m']=z;R['scanner']['proposed_edges'].append(row)
# Proposed horizontal seam boxes are 150mm wide, with exact back plane at Y7.180; sample across full width.
for x in [-.73,.73]:
 for z in [.56,1.22,1.88]:
  for dx in [-.075,-.0375,0,.0375,.075]:
   row=ray('proposed seam back Y7.180 to actual scanner column','Scanner portal column '+str(-1 if x<0 else 1),(x+dx,7.14,z),(0,1,0),.08)
   row.update({'part_back_y_m':7.180,'signed_clearance_part_to_surface_m':None if row['hit_m'] is None else 7.180-row['hit_m'][1],'seam_center_x_m':x,'z_sample_m':z,'offset_x_m':dx});R['scanner']['proposed_seams'].append(row)
# P2 shoe geometry formulas compared to measured real steel closure surfaces; y front=15.710, heel=15.728, half width .055.
R['p2']={'proposed_shoes':[],'retained_aperture':{'clear_opening_x_m':[-2.3,2.3],'left_jamb_bounds_m':bounds(S.objects['P2 frame jamb -1']),'right_jamb_bounds_m':bounds(S.objects['P2 frame jamb 1'])}}
for x in [-2.23,2.23]:
 for z in [.2,3.2]:
  target='CD | Joined P2 blast leaf '+('west' if x<0 else 'east')+' / steel'
  row={'shoe_center_x_m':x,'z_center_m':z,'proposed_bounds_m':[[x-.055,15.710,z-.09],[x+.055,15.728,z+.09]],'closure_surface_rays':[],'aperture_edge_intrusion_m':max(0,abs(x)+.055-2.3)}
  for dx in [-.045,-.02,0,.02,.045]:
   row['closure_surface_rays'].append(ray('shoe heel Y15.728 to actual steel closure',target,(x+dx,15.68,z),(0,1,0),.10))
  R['p2']['proposed_shoes'].append(row)
R['f12_native_hash_after_probe']=sha(BLEND)
out=Path(sys.argv[sys.argv.index('--')+1]);out.write_text(json.dumps(R,indent=2)+'\n');print('WROTE',out)
