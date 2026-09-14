"""Assemble linked portable room collections at unit scale; reserve gaps only."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'production/LAYOUT.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.name='FACILITY_A04_SPATIAL_ASSEMBLY'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
def collection(name):
 c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
rooms=collection('01_LINKED_ROOMS');guides=collection('02_UNBUILT_CONNECTION_RESERVATIONS');volumes=collection('03_RESERVED_VOLUMES');labels=collection('04_PLANNING_LABELS');cameras=collection('05_ASSEMBLY_CAMERAS')
palette={'freight':(0.92,.47,.12,1),'service':(.78,.72,.46,1),'maintenance':(.58,.68,.53,1),'clean':(.85,.84,.75,1),'controlled':(.63,.34,.34,1),'waste':(.66,.52,.37,1)}
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=color;return m
mats={k:material('RESERVED '+k,v) for k,v in palette.items()}
def line(name,pts,mat,radius=.045):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=0
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);guides.objects.link(ob);cu.materials.append(mat);return ob
def text(name,body,loc,size=.9):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=0
 ob=bpy.data.objects.new(name,cu);labels.objects.link(ob);ob.location=loc;cu.materials.append(mats['clean']);return ob
linked=[]
for sid,pose in layout['placements'].items():
 source=ROOT/'sources'/sid/'module.blend';name='MODULE_'+sid
 with bpy.data.libraries.load(str(source),link=True) as (src,dst):
  assert name in src.collections,(sid,src.collections);dst.collections=[name]
 ob=bpy.data.objects.new(sid,None);rooms.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=dst.collections[0];ob.location=pose['translation'];ob.rotation_euler.z=math.radians(pose['rotation_z_degrees']);ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.5
 ob['module_id']=sid;ob['source_sha256']=hashlib.sha256((ROOT/'sources'/sid/'accepted.blend').read_bytes()).hexdigest();ob['unit_scale_preserved']=True
 linked.append({'id':sid,'library':f'../sources/{sid}/module.blend','source_sha256':ob['source_sha256'],'translation':list(ob.location),'rotation_z_degrees':pose['rotation_z_degrees']})
 # Top labels are planning annotations, separately toggleable.
 survey=json.loads((ROOT/'sources'/sid/'survey.json').read_text());b=survey['all_visible_bounds'];local=Vector(((b[0][0]+b[1][0])/2,(b[0][1]+b[1][1])/2,0));world=ob.matrix_basis@local
 label={'spawn-room':'SPAWN','mine':'MINE','refinery':'REFINERY','fuel-corridor':'FUEL CORRIDOR','reactor-room':'REACTOR','cooling-plant':'COOLING','turbine-room':'TURBINE','electrical-room':'ELECTRICAL','waste-storage':'WASTE','medical-reanimation':'MEDICAL','compliance-dock':'COMPLIANCE','condenser-bay':'CONDENSER  [-6 m]'}[sid]
 label_pos=(world.x,world.y,b[1][2]+pose['translation'][2]+.8) if sid!='condenser-bay' else (33,40,7)
 text('LABEL_'+sid,label,label_pos,1.1 if sid!='condenser-bay' else .65)
for route in layout['routes']:
 pts=route['points'];mat=mats[route['kind']]
 for i,(a,b) in enumerate(zip(pts,pts[1:])):
  a=Vector(a);b=Vector(b);length=(b-a).length;steps=max(1,math.ceil(length/1.5))
  for j in range(steps):
   t0=j/steps;t1=min((j+.56)/steps,1)
   p=a.lerp(b,t0);q=a.lerp(b,t1);p.z+=.12;q.z+=.12
   line(route['id']+f' dashed reservation {i}-{j}',[p,q],mat)
  # Width boundary lines; actual connector remains absent.
  if abs(a.z-b.z)<.01:
   side=Vector((-(b-a).y,(b-a).x,0)).normalized()*route['width_m']/2
   for sign in [-1,1]:line(route['id']+' width allowance',[a+side*sign+Vector((0,0,.1)),b+side*sign+Vector((0,0,.1))],mat,.018)
 mid=Vector(pts[len(pts)//2]);text('LABEL_'+route['id'],route['id']+' RESERVED',(*mid.xy,1.0),.55)
for r in layout['reserved_volumes']:
 c=Vector(r['center']);s=Vector(r['size'])/2
 pts=[c+Vector((x*s.x,y*s.y,z*s.z)) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 for i,p in enumerate(pts):
  for j,q in enumerate(pts):
   if i<j and sum(abs(p[k]-q[k])>.01 for k in range(3))==1:line(r['id'],[p,q],mats['service'],.035)
 text('LABEL_'+r['id'],r['id'].replace('_',' '),(c.x,c.y,max(c.z+s.z,0)+.2),.65)
def camera(name,loc,target,scale):
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);cameras.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;data.clip_end=1000;return ob
camera('A01_AERIAL',(-145,-170,185),(-9,10,0),200)
camera('A02_TRUE_PLAN',(-9,10,220),(-9,10,0),210)
camera('A03_POWER_WING',(103,-17,86),(38,42,0),112)
scene.camera=bpy.data.objects['A01_AERIAL']
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=2200;scene.render.resolution_y=1800;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('Assembly World');scene.world.color=(.035,.04,.047)
scene['assembly_scope']='Existing modules at real scale. Dashed routes/wire volumes reserve connecting structures; no finished corridors or runtime traversal claimed.'
scene['spec']='GAME_SPEC 23.1–23.4, 4.2, 4.5; canonical Valorant art direction; approved mine adit supersedes legacy mine-lift list.'
bpy.context.view_layer.update()
# Keep the saved viewport inexpensive and useful without an automatic render.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='SOLID';area.spaces.active.overlay.show_overlays=False;area.spaces.active.region_3d.view_distance=150;area.spaces.active.region_3d.view_location=(-9,10,0)
out=ROOT/'blender/facility_master.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(ROOT/'production/MASTER_MANIFEST.json').write_text(json.dumps({'revision':layout['revision'],'linked_modules':linked,'room_count':len(linked),'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'unbuilt_routes':len(layout['routes']),'rendering':'Workbench layout evidence; source materials retained; not renewed room art scoring'},indent=2))
print('MASTER_SAVED',len(linked),'linked rooms; sources unchanged',flush=True)
