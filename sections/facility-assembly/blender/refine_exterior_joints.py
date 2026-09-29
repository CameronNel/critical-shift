"""Physical panel reveals and seated fittings. Never rebuilds the main environment."""
import bpy,bmesh,math,json,hashlib,ctypes,shutil,ast,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/exterior-joints';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inspection=json.loads((OUT/'inspection.json').read_text());mode='complete' if '--complete' in sys.argv else 'slice'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
main=SRC.with_name('facility_environment.blend');assert sha(main)==inspection['sha256'],'Main changed concurrently'
if mode=='slice':
 assert sha(SRC)==inspection['sha256']
 backup=SRC.with_name('facility_environment.joints-before.blend')
 if backup.exists():assert sha(backup)==sha(SRC),'Different recovery checkpoint'
 else:shutil.copy2(SRC,backup)
 report=dict(before_sha256=sha(SRC),backup=str(backup),removed=[],changed=[],joints=[],complete=False)
 for fname in ('fingerprint','material_sig'):
  tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
 report['original_objects']={o.name_full:fingerprint(o) for o in s.objects};report['materials']={m.name_full:material_sig(m) for m in bpy.data.materials};report['libraries']={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
 coll=bpy.data.collections.new('ART | Exterior construction joints');s.collection.children.link(coll)
 print('JOINT_BASELINE_RECORDED',len(report['original_objects']),flush=True)
else:
 report=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==report['candidate_sha256'];coll=bpy.data.collections['ART | Exterior construction joints']
base_objs=list(s.objects);pending_remove=set()
for name,key in [('steel','Charcoal coated steel'),('grey','Faded slate cobalt'),('zinc','Dusty galvanized duct'),('concrete','Weathered warm mineral concrete'),('edge','Repair panel mineral'),('dark','Recess and rubber'),('oxide','Muted oxide maintenance enamel'),('rust','Local oxidation')]:globals()[name]=bpy.data.materials['RFX | '+key]
bare=bpy.data.materials['RFS | Exposed brushed edge metal'];seal=bpy.data.materials['RFS | Joint sealant']
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text())
for name in ('mesh','box','cyl','beam','P','wb'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<mesh>','exec'))
def bounds(o):
 vs=[o.matrix_world@Vector(v) for v in o.bound_box];return Vector(tuple(min(p[i] for p in vs) for i in range(3))),Vector(tuple(max(p[i] for p in vs) for i in range(3)))
def side_of(o):
 lo,hi=bounds(o);c=(lo+hi)*.5
 if hi.x-lo.x<.6 and c.x<-10.5:return 'W'
 if hi.x-lo.x<.6 and c.x>2.5:return 'E'
 return 'S' if c.y<-23.8 else 'N'
def ud(side,p):
 return (p.y,-10.87-p.x) if side=='W' else (p.y,p.x-2.72) if side=='E' else (p.x,-24.5-p.y) if side=='S' else (p.x,p.y+8.7)
def remove(o):
 if o.name_full in report['original_objects']:report['removed'].append(o.name_full)
 pending_remove.add(o.name);o.hide_render=True;o.hide_viewport=True
def changed(o):
 if o.name_full in report['original_objects'] and o.name_full not in report['changed']:report['changed'].append(o.name_full)
def face_mat(o):return o.material_slots[0].material
def norm(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
def ring(name,side,u,z,wo,ho,wi,hi,back,front,mat):
 # A continuous closed rectangular annulus: actual empty centre, not a dark rectangle.
 vs=[]
 for d in (back,front):
  for w,h in ((wo,ho),(wi,hi)):
   vs.extend([P(side,u+a*w/2,d,z+b*h/2) for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))])
 fs=[]
 for k in range(4):
  j=(k+1)%4;fs.extend([(k,j,j+8,k+8),(k+4,k+12,j+12,j+4),(k,k+4,j+4,j),(k+8,j+8,j+12,k+12)])
 o=mesh(name,vs,fs,mat);norm(o);return o
def top_ring(name,x,y,wo,ho,wi,hi,z0,z1,mat):
 # Same closed ring mapped from a vertical section onto the ground/roof.
 o=ring(name,'S',0,0,wo,ho,wi,hi,0,z1-z0,mat)
 for v in o.data.vertices:
  xx,yy,zz=v.co;v.co=(x+xx,y+zz,z0+(-24.5-yy))
 norm(o);return o
def fastener(side,u,d,z,r=.017):
 cyl('Joint fixing washer',P(side,u,d,z),P(side,u,d+.005,z),r*1.5,bare,16)
 return cyl('Joint hex bolt',P(side,u,d+.004,z),P(side,u,d+.018,z),r,steel,6)
def cut_box(target,center,dim):
 cutter=box('Temporary joint pocket cutter',center,dim,dark,0)
 bpy.context.view_layer.objects.active=target;target.select_set(True);target.data=target.data.copy();mod=target.modifiers.new('Measured access pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);target.select_set(False);bpy.data.objects.remove(cutter,do_unlink=True);changed(target)
def selected_side(o):return mode=='complete' and side_of(o)!='E' or mode=='slice' and side_of(o)=='E'

# One façade first. The full pass applies identical measured construction to the rest.
panels=[o for o in base_objs if o.name.startswith('RFX | Mineral panel face') and selected_side(o)]
for o in panels:
 lo,hi=bounds(o);side=side_of(o);u,d=ud(side,(lo+hi)/2);w=(hi.y-lo.y) if side in 'WE' else (hi.x-lo.x);h=hi.z-lo.z;z=(lo.z+hi.z)/2;ma=face_mat(o)
 # Existing panel faces sit ~1mm ahead of the original shell. Place a real 41mm panel
 # on that substrate, with a 4mm chamfer and a 22-26mm open joint at its perimeter.
 panel=wb('Solid mineral facade panel',side,u,d+.024,z,w-.010,.044,h-.010,ma,.004)
 panel.data.materials.append(edge)
 for p in panel.data.polygons:
  # Side/rear returns use the cut mineral colour; retain the existing authored face.
  axis=0 if side in 'WE' else 1
  if abs(p.normal[axis])<.95:p.material_index=1
 wb('Recessed panel joint bedding',side,u,d+.001,z,w+.016,.004,h+.012,seal,.001)
 # Side support clips terminate behind the mineral face, within the recessed joint.
 for du in (-w/2+.08,w/2-.08):
  for zz in (-h*.33,h*.33):wb('Panel concealed support clip',side,u+du,d+.006,z+zz,.07,.012,.06,steel,.002)
 report['joints'].append(dict(type='facade',side=side,u=u,z=z,front_depth=round(d+.046,5),recess_depth=.043,horizontal_gap=.022,vertical_gap=.026));remove(o)
for o in list(base_objs):
 if o.name not in bpy.data.objects:continue
 if o.name.startswith(('RFX | Wall panel sealed','RFX | Lower wall repair')) and selected_side(o):remove(o)

# Hollow structural channels, supported bearing plates, and bolted straps.
for o in base_objs:
 if o.name not in bpy.data.objects or not o.name.startswith('RFX | Facade structural pier') or not selected_side(o):continue
 side=side_of(o);u,d=ud(side,o.location);lo,hi=bounds(o)
 cross=[(-.13,-.005),(.13,-.005),(.13,.225),(.093,.225),(.093,.035),(-.093,.035),(-.093,.225),(-.13,.225)]
 vs=[P(side,u+a,b,z) for z in (.603,hi.z) for a,b in cross];N=len(cross);fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 ch=mesh('Formed steel facade channel',vs,fs,grey);norm(ch)
 bm=bmesh.new();bm.from_mesh(ch.data);bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.003,segments=2,affect='EDGES',clamp_overlap=True);bm.to_mesh(ch.data);bm.free()
 wb('Column bearing plate',side,u,.15,.588,.43,.285,.025,steel,.004)
 for du in (-.165,.165):
  for dd in (.047,.26):cyl('Base anchor washer',P(side,u+du,dd,.601),P(side,u+du,dd,.606),.025,bare,16);cyl('Base anchor nut',P(side,u+du,dd,.605),P(side,u+du,dd,.628),.017,steel,6)
 for z in (1,3.6,4.5):
  for du in (-.11,.11):fastener(side,u+du,.281,z,.016)
 remove(o)

# Correct the screenshot's electrical cabinets: hollow shells with rebated door
# openings, a visible 7mm perimeter reveal, and a real wall mounting gap.
if mode=='slice':
 for o in base_objs:
  if o.name.startswith('RFX | Service cabinet enclosure'):
   u=o.location.y;lo,hi=bounds(o);back=lo.x-2.72
   ring('Cabinet folded enclosure','E',u,1.15,.68,1.0,.584,.894,back,.607,grey)
   wb('Cabinet rear closure','E',u,back+.009,1.15,.65,.018,.97,grey,.004)
   ring('Cabinet recessed door seal','E',u,1.15,.589,.899,.556,.866,.567,.579,dark)
   for du in (-.225,.225):
    wb('Cabinet wall mounting rail','E',u+du,.085,1.15,.06,.068,1.03,steel,.004)
    for z in (.74,1.56):fastener('E',u+du,.12,z,.014)
   # Compression gland joins the existing conduit to the enclosure top.
   cyl('Cabinet cable gland',(3.0,u,1.628),(3.0,u,1.727),.048,steel,12)
   cyl('Cabinet gland locknut',(3.0,u,1.658),(3.0,u,1.687),.062,bare,6)
   report['joints'].append(dict(type='cabinet',u=u,door_gap=.007,door_setback=.0195));remove(o)
  elif o.name.startswith('RFX | Service cabinet wall bracket'):remove(o)

# Service coupling collars become two physical flange faces and a recessed gasket.
for o in base_objs:
 if o.name not in bpy.data.objects or not o.name.startswith('RFX | Header coupling collar') or not selected_side(o):continue
 center=o.location.copy();axis=o.rotation_euler.to_matrix()@Vector((0,0,1));radius=max(v.co.xy.length for v in o.data.vertices)
 for sign in (-1,1):cyl('Separated flange face',center+axis*sign*.012,center+axis*sign*.045,radius,zinc,24)
 cyl('Flange recessed gasket',center-axis*.011,center+axis*.011,radius*.84,dark,24)
 report['joints'].append(dict(type='pipe flange',position=list(center),separation=.024,gasket_diameter_ratio=.84));remove(o)

# Vent front cover/flange seats ahead of the louvres with a real gasket recess.
vents=[('E',-13.8,2.85,2.55,1.15)] if mode=='slice' else [('W',-17.9,2.8,3.2,1.25),('N',-7.5,2.65,2.1,1.15)]
for side,u,z,w,h in vents:
 ring('Vent cover recessed gasket',side,u,z,w+.20,h+.20,w-.12,h-.14,.661,.677,dark)
 ring('Vent removable front flange',side,u,z,w+.24,h+.24,w-.075,h-.105,.694,.722,grey)
 for du in (-w/2-.066,w/2+.066):
  for dz in (-h*.41,0,h*.41):fastener(side,u+du,.724,z+dz,.014)
 report['joints'].append(dict(type='vent cover',side=side,u=u,flange_setback=.028,gasket_recess=.017))

if mode=='complete':
 # Correct roof filter access doors, removing the later duplicate surface panels.
 for o in list(base_objs):
  if o.name.startswith(('RFX | Filter access face','RFX | Filter recessed panel seal')):remove(o)
 for body in [o for o in base_objs if o.name.startswith('RFX | Filter unit housing')]:
  y=body.location.y
  for x in (-6.65,-5.45):
   cut_box(body,(x,y-1.30,6.0),(1.07,.28,.94))
   d=-24.5-(y-1.365)
   ring('Filter door folded rim','S',x,6.0,1.13,1.00,1.04,.91,d-.025,d,grey)
   ring('Filter access gasket','S',x,6.0,1.049,.919,1.004,.874,d-.043,d-.028,dark)
   for z in (5.86,6.16):beam('Filter handle return',(x+.32,y-1.356,z),(x+.32,y-1.4,z),.035,.035,steel)
  for o in base_objs:
   if o.name.startswith('RFX | Removable filter door') and abs(o.location.y-(y-1.321))<.01:
    ma=face_mat(o);x=o.location.x;remove(o);box('Folded filter service door',(x,y-1.347,6.0),(1.02,.018,.89),ma,.003)
 # Real gasket gap under roof hatches; replace solid curbs with hollow rings.
 for o in base_objs:
  if o.name.startswith('RFX | Roof access hatch curb'):
   x,y=o.location.xy;top_ring('Hollow hatch curb',x,y,1.5,1.3,1.37,1.17,5.04,5.280,steel);top_ring('Hatch compression gasket',x,y,1.46,1.26,1.38,1.18,5.280,5.300,dark);remove(o)
  elif o.name.startswith('RFX | Roof hatch lid'):
   changed(o);o.location.z+=.008
   for x in (-2.5,-2.1):box('Hatch handle return foot',(x,o.location.y,5.419),(.035,.055,.043),steel,.003)
 # True open grating modules, not bars on a solid plate.
 for o in base_objs:
  if o.name.startswith(('RFX | Maintenance deck substrate','RFX | Deck serrated tread')):remove(o)
 for i in range(5):
  ya=-20.9+i*2.06;yb=ya+2.044;ym=(ya+yb)/2
  top_ring('Catwalk grating module frame',-9.1,ym,1.18,yb-ya,1.10,yb-ya-.08,5.12,5.26,steel)
  for y in np.arange(ya+.072,yb-.05,.065):box('Open catwalk bearing bar',(-9.1,float(y),5.2375),(1.10,.025,.045),zinc,.002)
  for x in (-9.42,-9.1,-8.78):box('Grating underside cross tie',(x,ym,5.202),(.018,yb-ya-.08,.026),steel,.002)
 # Feet have a bolted plate rather than a pole sunk into the walking surface.
 for o in base_objs:
  if o.name.startswith('RFX | Guardrail stanchion'):
   lo,hi=bounds(o);x,y=o.location.xy;box('Guardrail foot plate',(x,y,5.272),(.15,.16,.024),steel,.003)
   for dx in (-.045,.045):cyl('Guardrail foot bolt',(x+dx,y,5.283),(x+dx,y,5.303),.012,bare,6)
 # Flat paving skins become shallow solids; lower the existing joint bed so the
 # visible gaps have depth without raising player foot height or door thresholds.
 for o in base_objs:
  if o.name.startswith(('RFX | Warm apron paving','RFX | Receiving apron slab')):
   lo,hi=bounds(o);ma=face_mat(o);z=lo.z;box('Solid apron paving slab',((lo.x+hi.x)/2,(lo.y+hi.y)/2,z-.007),(hi.x-lo.x,hi.y-lo.y,.014),ma,.002);remove(o)
  elif o.name.startswith('RFX | Dark mortar beneath apron joints'):changed(o);o.location.z-=.0055
  elif o.name.startswith('RFX | Receiving apron joint underlay'):changed(o);o.location.z-=.0085
 bpy.context.view_layer.update()
 for o in base_objs:
  if o.name.startswith('RFX | Cover drainage slot'):remove(o)
  elif o.name.startswith('RFX | Inset inspection surround'):
   x,y=o.location.xy;top_ring('Apron inspection cover bearing',x,y,.52,.66,.41,.55,-.009,.004,steel);top_ring('Apron inspection rebated rim',x,y,.52,.66,.456,.596,.004,.015,grey);box('Apron inspection dark well',(x,y,-.005),(.42,.56,.001),dark,0);remove(o)
  elif o.name.startswith('RFX | Inset inspection cover'):
   x,y=o.location.xy
   for i in range(7):cut_box(o,(x,y-.23+i*.075,.012),(.34,.018,.05))
   for tile in [t for t in coll.objects if t.name.startswith('RFX | Solid apron paving slab')]:
    lo,hi=bounds(tile)
    if lo.x<x<hi.x and lo.y<y<hi.y:cut_box(tile,(x,y,0),(.42,.56,.08))
 # Courtyard retaining coping: bedding separation instead of interpenetration.
 for o in base_objs:
  if o.name.startswith('CY | Retaining coping'):
   changed(o);o.location.z+=.0475;lo,hi=bounds(o);box('Retaining coping recessed bedding',((lo.x+hi.x)/2,(lo.y+hi.y)/2,1.316),(hi.x-lo.x-.045,hi.y-lo.y-.060,.015),edge,.002)
 # Existing courtyard paving already has genuine 36mm gaps: retain it. Rebuild
 # its four drains with actual openings cut only into the owned paving slabs.
 drain_centers=[]
 for o in base_objs:
  if o.name.startswith('CY | Drain collar'):
   lo,hi=bounds(o);x,y=(lo.x+hi.x)/2,(lo.y+hi.y)/2;w,h=hi.x-lo.x,hi.y-lo.y;drain_centers.append((x,y,w,h));remove(o)
 for o in base_objs:
  if o.name not in bpy.data.objects:continue
  if o.name.startswith(('CY | Drain recess','CY | Drain grating bar')):remove(o)
 for x,y,w,h in drain_centers:
  wi,hi=w-.14,h-.14
  for slab in [q for q in base_objs if q.name in bpy.data.objects and q.name.startswith('CY | Patched yard slab')]:
   lo,up=bounds(slab)
   if lo.x<x<up.x and lo.y<y<up.y:cut_box(slab,(x,y,.06),(wi,hi,.30))
  top_ring('Courtyard drain rebated collar',x,y,w,h,wi,hi,.112,.156,concrete)
  top_ring('Drain recessed steel seat',x,y,wi,hi,wi-.035,hi-.035,.104,.126,steel)
  top_ring('Drain sump lining',x,y,wi,hi,wi-.025,hi-.025,-.031,.113,steel)
  box('Drain sump floor',(x,y,-.025),(wi,hi,.012),dark,.002)
  n=max(3,int(wi/.055))
  for i in range(n):box('Open drain grating',(x-wi/2+.023+i*(wi-.046)/(n-1),y,.14),(.019,hi-.016,.028),steel,.002)
  report['joints'].append(dict(type='courtyard drain',position=[x,y],pit_depth=.17,open_grate_gap=.036))
 # Recessed joints between volute halves, both refinery and courtyard pumps.
 for o in base_objs:
  if o.name not in bpy.data.objects or not o.name.startswith(('RFX | Pump volute','CY | Volute housing')):continue
  c=o.location.copy();ax=o.rotation_euler.to_matrix()@Vector((0,0,1));r=max(v.co.xy.length for v in o.data.vertices);length=max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices);ma=face_mat(o)
  for sign in (-1,1):cyl('Pump split volute half',c+ax*sign*.006,c+ax*sign*length/2,r,ma,24)
  cyl('Pump casing recessed seal',c-ax*.005,c+ax*.005,r*.92,dark,24)
  v=Vector((0,1,0));v=(v-ax*v.dot(ax)).normalized();q=ax.cross(v)
  for k in range(6):
   p=c+(v*math.cos(k*math.pi/3)+q*math.sin(k*math.pi/3))*r*.8;cyl('Volute flange through bolt',p-ax*(length/2+.013),p+ax*(length/2+.013),.018,steel,6)
  remove(o)
 # Stored skip panels are welded construction, not cabinet doors: retain tight
 # seams and add the visible weld returns at their real lower corner joints.
 for o in base_objs:
  if o.name.startswith('CY | Tapered skip panel'):
   vs=[o.matrix_world@v.co for v in o.data.vertices]
   beam('Skip lower weld return',vs[0],vs[1],.012,.012,rust)

bpy.context.view_layer.update()
# Seat existing authored wall markings on all completed panels, including the
# first slice when completing the other sides. Do not touch source-room text.
for panel in [o for o in coll.objects if o.name.startswith('RFX | Solid mineral facade panel')]:
 lo,hi=bounds(panel);side=side_of(panel);u,d=ud(side,(lo+hi)/2);w=hi.y-lo.y if side in 'WE' else hi.x-lo.x;front=d+.022
 for detail in base_objs:
  if detail.type=='FONT' and not detail.name.startswith('RFS |'):continue
  if detail.type!='FONT' and not detail.name.startswith(('RFX | Wall identification rule','RFX | Service warning backing')):continue
  uu,dd=ud(side,detail.location)
  if abs(uu-u)<w/2 and lo.z<detail.location.z<hi.z and front-.07<dd<front:
   desired=front+.001
   if detail.name.startswith('RFX | Service warning backing'):desired=front+.013
   elif detail.name.startswith('RFS | Service caution'):desired=front+.027
   elif detail.type!='FONT':desired=front+.006
   changed(detail);direction=Vector(P(side,0,1,0))-Vector(P(side,0,0,0));detail.location+=direction*(desired-dd)
if mode=='complete':
 # Seat every bearing plate on recessed grout, including the first reviewed bay.
 for plate in [o for o in coll.objects if o.name.startswith('RFX | Column bearing plate')]:
  side=side_of(plate);u,d=ud(side,plate.location)
  wb('Column recessed grout pad',side,u,.15,.5675,.39,.25,.016,edge,.002)
 # First-slice rails were too far into the panel: bring their backs to its face.
 for rail in [o for o in coll.objects if o.name.startswith('RFX | Cabinet wall mounting rail')]:
  rail.location.x+=.030;rail.scale.x*=.68
for name in pending_remove:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bpy.context.view_layer.update()
errors=[]
audit_objects=set(coll.objects)|{bpy.data.objects[n] for n in report['changed'] if n in bpy.data.objects}
for o in audit_objects:
 if o.type!='MESH' or o.get('intentional_surface_overlay'):continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces) or abs(bm.calc_volume())<1e-12:errors.append(o.name)
 bm.free()
assert not errors,errors
report['new_objects']=[o.name for o in coll.objects];report['mesh_errors']=errors
# Save a player-height detail view of the exact wall bay the user challenged.
if mode=='slice':
 cam=bpy.data.objects.new('JNT CAMERA | WALL DETAIL',bpy.data.cameras.new('JNT CAMERA | WALL DETAIL'));coll.objects.link(cam);cam.location=(5.8,-23.8,1.7);target=Vector((2.76,-20.6,1.9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=40
else:
 for name,pos,target,lens in [('COURTYARD SOUTH',(-10.9,-35.8,1.7),(-18,-40.4,1.0),25),('COURTYARD NORTH',(-14.5,-20.5,1.85),(-24,-13.6,.95),32)]:
  cam=bpy.data.objects.new('JNT CAMERA | '+name,bpy.data.cameras.new('JNT CAMERA | '+name));coll.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['JNT CAMERA | WALL DETAIL'];assert sha(main)==inspection['sha256']
target=main.with_name('facility_environment.joints-candidate.blend') if mode=='slice' else main
bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False)
if mode=='slice':report['candidate_sha256']=sha(target)
else:report['saved_sha256']=sha(target)
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('JOINTS_SAVED',mode,sha(target),flush=True)
s.render.filepath=str(OUT/'wall-detail.png');bpy.ops.render.render(write_still=True);print('JOINT_DETAIL_RENDERED',flush=True)
if mode=='complete':
 s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];s.cycles.samples=8;s.render.filepath=str(OUT/'entry.png');bpy.ops.render.render(write_still=True);print('JOINT_ENTRY_RENDERED',flush=True)
