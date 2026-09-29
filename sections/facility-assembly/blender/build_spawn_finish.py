"""Guarded, additive construction from approved spawn-yard concepts.

Slice writes a candidate only. Complete opens that candidate and extends it.
Original linked geometry, materials, global lighting and mine/refinery stay intact.
"""
import bpy,bmesh,math,random,json,hashlib,ctypes,shutil,ast,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/spawn-finish';SRC=Path(bpy.data.filepath)
MAIN=SRC.with_name('facility_environment.blend');CAND=SRC.with_name('facility_environment.spawn-candidate.blend')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inspection=json.loads((OUT/'inspection.json').read_text());assert sha(MAIN)==inspection['sha256'],'Main changed since inspection'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();complete='--complete' in sys.argv
for fname in ('fingerprint','material_sig'):
 tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
if not complete:
 assert sha(SRC)==inspection['sha256']
 backup=MAIN.with_name('facility_environment.spawn-before.blend')
 if backup.exists():assert sha(backup)==sha(MAIN),'Different existing recovery checkpoint'
 else:shutil.copy2(MAIN,backup)
 report=dict(before_sha256=sha(MAIN),backup=str(backup),original={o.name_full:fingerprint(o) for o in s.objects},materials={m.name_full:material_sig(m) for m in bpy.data.materials},libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries},panels=[],props=[],complete=False)
 coll=bpy.data.collections.new('ART | Spawn and medical courtyard');s.collection.children.link(coll)
else:
 report=json.loads((OUT/'construction.json').read_text());assert sha(SRC)==report['candidate_sha256'];coll=bpy.data.collections['ART | Spawn and medical courtyard']
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text().replace("'RFX | '","'SY | '"))
for fname in ('mesh','box','cyl','beam','pipe'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<construction>','exec'))
def material(key):return bpy.data.materials[key]
steel=material('RFX | Charcoal coated steel');grey=material('RFX | Faded slate cobalt');zinc=material('RFX | Dusty galvanized duct')
concrete=material('RFX | Weathered warm mineral concrete');patch=material('RFX | Repair panel mineral');dark=material('RFX | Recess and rubber')
oxide=material('RFX | Muted oxide maintenance enamel');ochre=material('RFX | Worn ochre safety enamel');rust=material('RFX | Local oxidation');bare=material('RFS | Exposed brushed edge metal')
rng=random.Random(92703)
RW_X=2.96
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return Vector(tuple(min(p[i] for p in pts) for i in range(3))),Vector(tuple(max(p[i] for p in pts) for i in range(3)))
def P(side,u,d,z):
 return {'N':(u,7.512+d,z),'E':(-19.688+d,u,z),'EN':(-26.088+d,u,z),'ENTRY':(u,12.49+d,z),'MS':(u,30.769-d,z),'MW':(-22.231-d,u,z),'RW':(RW_X-d,u,z)}[side]
def wb(name,side,u,d,z,w,depth,h,ma,bev=.004):return box(name,P(side,u,d,z),(depth,w,h) if side in ('E','EN','MW','RW') else (w,depth,h),ma,bev)
def ring(name,side,u,z,wo,ho,wi,hi,back,front,ma):
 vs=[]
 for d in (back,front):
  for w,h in ((wo,ho),(wi,hi)):
   vs.extend([P(side,u+a*w/2,d,z+b*h/2) for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))])
 fs=[]
 for k in range(4):
  j=(k+1)%4;fs.extend([(k,j,j+8,k+8),(k+4,k+12,j+12,j+4),(k,k+4,j+4,j),(k+8,j+8,j+12,k+12)])
 o=mesh(name,vs,fs,ma);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
def bolt(side,u,d,z,r=.012):
 cyl('Seated washer',P(side,u,d,z),P(side,u,d+.004,z),r*1.45,bare,12)
 cyl('Hex fastener',P(side,u,d+.004,z),P(side,u,d+.014,z),r,steel,6)
def facade(room,sides):
 row=next(o for o in inspection['objects'] if o['name'].startswith('MATERIAL_PREVIEW_EXTERIOR_INSTANCE_'+room))
 for c in row['components']:
  if c['mats']!=[0]:continue
  lo,hi=Vector(c['lo']),Vector(c['hi']);center=(lo+hi)*.5;dim=hi-lo
  side=None
  if room=='spawn-room':
   if dim.y<.07 and abs(center.y-7.487)<.05:side='N'
   elif dim.x<.07 and abs(center.x+19.713)<.05:side='E'
   elif dim.x<.07 and abs(center.x+26.113)<.05:side='EN'
  else:
   if dim.y<.07 and abs(center.y-30.794)<.05:side='MS'
   elif dim.x<.07 and abs(center.x+22.206)<.05:side='MW'
  if side not in sides:continue
  u=center.y if side in ('E','EN','MW') else center.x;w=dim.y if side in ('E','EN','MW') else dim.x
  # Keep existing full-height backing, add a true open reveal in front of it.
  wb('Recessed facade substrate',side,u,.032,center.z,w,.01,dim.z,dark,.001)
  cuts=sorted(set([float(lo.z),float(hi.z)]+[z for z in (.44,1.55,2.77,3.14) if lo.z<z<hi.z]))
  for a,b in zip(cuts,cuts[1:]):
   if b-a<.08:continue
   ma=patch if b<=.45 else oxide if room=='medical-reanimation' and a>=2.76 and b<=3.15 else concrete
   panel=wb('Solid '+room+' panel',side,u,.063,(a+b)/2,w-.012,.052,b-a-.024,ma,.004)
   for du in (-w/2+.10,w/2-.10):
    for zz in (a+.09,b-.09):
     if b-a>.25:bolt(side,u+du,.089,zz,.009)
   report['panels'].append(dict(object=panel.name,room=room,side=side,joint=.024,recess=.052))
  if dim.z>3:
   # Folded structural channels, with a visible inset web rather than a solid pier.
   for du in (-w/2,w/2):
    wb('Channel web',side,u+du,.060,1.73,.062,.022,3.44,steel)
    for off in (-.042,.042):wb('Channel return',side,u+du+off,.095,1.73,.018,.09,3.44,steel)
def vent(side,u,z,w=1.15,h=.55):
 wb('Vent cavity back',side,u,.11,z,w,.014,h,dark)
 ring('Hollow vent enclosure',side,u,z,w+.12,h+.12,w-.015,h-.015,.10,.33,zinc)
 ring('Vent compressed gasket',side,u,z,w+.145,h+.145,w-.005,h-.005,.326,.339,dark)
 ring('Removable vent flange',side,u,z,w+.18,h+.18,w+.012,h+.012,.344,.366,steel)
 for i in range(int(h/.092)):
  zz=z-h/2+.045+i*.092
  # Blades have real separated openings and 130 mm depth.
  wb('Vent separate louvre blade',side,u,.255,zz,w-.025,.13,.024,zinc,.003)
 for du in (-w/2-.053,w/2+.053):
  for dz in (-h/2-.048,h/2+.048):bolt(side,u+du,.367,z+dz)
def cabinet(side,u,z=1.25):
 for du in (-.29,.29):wb('Cabinet wall mounting rail',side,u+du,.125,z,.055,.08,1.12,zinc)
 wb('Cabinet closed back',side,u,.179,z,.78,.026,1.04,steel)
 ring('Cabinet folded enclosure',side,u,z,.80,1.07,.702,.972,.18,.43,grey)
 ring('Cabinet recessed door seal',side,u,z,.705,.975,.657,.927,.401,.412,dark)
 wb('Cabinet separate rebated door',side,u,.421,z,.684,.024,.954,grey,.008)
 for zz in (z-.30,z+.30):cyl('Cabinet hinge',P(side,u-.351,.447,zz-.065),P(side,u-.351,.447,zz+.065),.022,zinc,12)
 for zz in (z-.07,z+.07):wb('Handle return',side,u+.26,.465,zz,.025,.064,.022,steel)
 cyl('Handle grip',P(side,u+.26,.496,z-.07),P(side,u+.26,.496,z+.07),.014,steel,12)
 wb('Cabinet service label',side,u-.08,.436,z+.29,.21,.006,.095,ochre,.002)
 pipe('Cabinet supply conduit',[P(side,u-.15,.27,z+.54),P(side,u-.15,.27,2.7),P(side,u+.54,.27,2.7),P(side,u+.54,.04,2.7)],.027,zinc)
 for zz in (1.98,2.45):
  wb('Conduit standoff',side,u-.15,.17,zz,.085,.13,.043,steel)
  cyl('Conduit clamp',P(side,u-.15,.27,zz-.025),P(side,u-.15,.27,zz+.025),.034,steel,16)
 report['props'].append(dict(type='cabinet',side=side,u=u))
def canopy(side,u,z,w,d):
 wb('Entrance canopy folded top',side,u,d/2+.06,z,w,d,.065,steel,.01)
 wb('Canopy front fascia',side,u,d+.018,z-.08,w,.055,.18,steel,.008)
 for du in (-w/2+.20,w/2-.20):
  wb('Canopy wall anchor',side,u+du,.12,z-.35,.13,.08,.67,steel)
  beam('Canopy diagonal support',P(side,u+du,.18,z-.60),P(side,u+du,d-.16,z-.14),.08,.085,zinc)
  for zz in (z-.52,z-.2):bolt(side,u+du,.168,zz,.018)
 for du in (-w*.28,w*.28):
  wb('Canopy light housing',side,u+du,d*.60,z-.07,.54,.13,.045,steel)
  # Reuse the existing warm lens; do not alter shared light energies.
  lens=next((m for m in bpy.data.materials if m.name.startswith('A14 Exterior EXT medical warm lens')),concrete)
  wb('Canopy warm light diffuser',side,u+du,d*.60,z-.098,.45,.10,.008,lens,.001)
def saved_cameras():
 for name,pos,target,lens in [('01-front-yard',(-17,27,1.7),(-28,11,2.1),24),('02-east-side',(-10,8,1.7),(-28,9,2.0),24),('03-yard-reverse',(-27,16,1.7),(-18,29,1.5),24)]:
  data=bpy.data.cameras.new('SY CAMERA | '+name);cam=bpy.data.objects.new(data.name,data);coll.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_start=.08;data.clip_end=300
if not complete:
 facade('spawn-room',('N','EN','E'))
 vent('N',-23.7,3.38,2.40,.40);vent('E',5.9,3.38,1.15,.4)
 cabinet('EN',9.8);cabinet('N',-21.1)
 canopy('ENTRY',-28,3.63,3.86,1.00)
 saved_cameras()
else:
 # A local broad bounce for the occupied yard; original sun/world/lights remain intact.
 ld=bpy.data.lights.new('SY | Courtyard sky bounce','AREA');ld.energy=2300;ld.shape='DISK';ld.size=16;ld.color=(1,.93,.82)
 light=bpy.data.objects.new(ld.name,ld);coll.objects.link(light);light.location=(-18,23,10);light.rotation_euler=(Vector((-26,17,1))-light.location).to_track_quat('-Z','Y').to_euler()
 facade('medical-reanimation',('MS','MW'))
 vent('MW',33.2,2.35,1.40,.62);cabinet('MW',35.3)
 canopy('MS',-18,3.53,5.30,1.20)
 # The concept's tall yard-facing service bay is a local layer, not a reactor rebuild.
 ext=next(o for o in s.objects if o.name=='MATERIAL_PREVIEW_EXTERIOR_INSTANCE_reactor-room')
 inv=ext.matrix_world.inverted();origin=Vector((-5,40,8));direction=Vector((1,0,0))
 hit,loc,normal,face=ext.ray_cast(inv@origin,inv.to_3x3()@direction)
 assert hit,'Tall facade service attachment has no support'
 world=ext.matrix_world@loc;RW_X=world.x;assert 2<RW_X<7 and abs(world.y-40)<.001
 vent('RW',40,8,1.65,2.05)
 pipe('Tall service riser',[P('RW',41.8,.06,12.1),P('RW',41.8,.42,11.8),P('RW',41.8,.42,1.1),P('RW',41.8,.06,.8)],.115,zinc)
 for z in (1.6,4.1,6.6,9.1,11.5):
  wb('Tall riser wall bracket','RW',41.8,.20,z,.25,.34,.10,steel)
  for dz in (-.033,.033):cyl('Tall pipe flange',P('RW',41.8,.42,z+dz-.012),P('RW',41.8,.42,z+dz+.012),.162,zinc,24)
  cyl('Tall pipe sealed joint',P('RW',41.8,.42,z-.018),P('RW',41.8,.42,z+.018),.132,dark,24)
 report['tall_service_support']=dict(object=ext.name_full,point=list(world),normal=list(normal),face=face)
 # Attached rainwater/service risers, collars, real mounting brackets, no random piping.
 for side,u,zmax in [('MS',-21.65,3.40),('MW',36.0,3.45),('EN',11.8,3.45),('N',-25.72,3.80)]:
  pipe('Wall rainwater riser',[P(side,u,.12,zmax),P(side,u,.26,zmax-.17),P(side,u,.26,.27),P(side,u,.42,.13)],.065,zinc)
  for z in (.55,1.8,2.9):
   wb('Pipe bracket backplate',side,u,.105,z,.14,.05,.17,steel)
   wb('Pipe bracket spacer',side,u,.18,z,.04,.14,.055,steel)
   cyl('Pipe mounted clamp',P(side,u,.26,z-.026),P(side,u,.26,z+.026),.074,oxide,20)
   for du in (-.05,.05):bolt(side,u+du,.134,z,.009)
 # Existing brown storage blocks receive fitted case shells; footprints do not grow.
 for i,x in enumerate((-21.,-20.1,-19.2,-18.3)):
  ma=oxide if i==1 else steel
  box('Maintenance case lid',(x,16,.735),(.735,.92,.065),ma,.018)
  box('Maintenance case lid gasket',(x,16,.704),(.73,.912,.012),dark,.001)
  for yy in (15.548,16.452):
   box('Maintenance case folded skin',(x,yy,.368),(.724,.018,.676),ma,.012)
   for dx in (-.27,0,.27):box('Case reinforcing rib',(x+dx,yy+(.014 if yy>16 else -.014),.34),(.035,.032,.48),zinc,.008)
   for dx in (-.22,.22):box('Case over-centre latch',(x+dx,yy+(.027 if yy>16 else -.027),.66),(.06,.04,.11),zinc,.005)
  for xx in (x-.365,x+.365):box('Maintenance case end',(xx,16,.368),(.018,.905,.676),ma,.008)
  box('Case recessed handle socket',(x,16.474,.52),(.25,.026,.10),dark,.005)
  beam('Case carry handle',(x-.11,16.492,.52),(x+.11,16.492,.52),.028,.035,zinc)
  report['props'].append(dict(type='case-wrap',footprint=[x,16,.74,.93]))
 # Tight service storage at an already-occupied yard perimeter, not in circulation.
 for x,y in [(-33.9,25.9),(-10.0,29.8)]:
  box('Service storage pallet',(x,y,.075),(1.4,.70,.16),steel,.016)
  for dx in (-.45,.0,.45):
   box('Stored repair panel',(x+dx,y,.46),(.35,.63,.60),zinc,.02)
   box('Storage panel cap',(x+dx,y,.785),(.37,.65,.06),steel,.006)
  report['props'].append(dict(type='storage',xy=[x,y]))
 # Physical paving laid above the retained structural yard substrate. Open joints
 # reveal that substrate; additions change playable height by at most 14 mm.
 slabs=[]
 floor_mats=[m for m in bpy.data.materials if m.name.startswith('GF | Courtyard dimensional slab mineral')]
 assert len(floor_mats)>=4,'Expected approved courtyard material family'
 for ix in range(9):
  for iy in range(8):
   x=-34.5+ix*3;y=9+iy*3
   if x<-26 and y<14:continue
   # Existing spawn wing ends y7.56, medical frontage begins y30.77.
   y0=y-1.487;y1=min(y+1.487,30.70)
   o=box('Dimensional courtyard slab',(x,(y0+y1)/2,.001),(2.974,y1-y0,.016),floor_mats[(ix+iy*3)%4],.002)
   slabs.append(o)
 # Atlas-driven controlled edge wear and local dampness, using copies of the
 # approved material graph, not changing shaders shared with the mine/refinery.
 bpy.context.view_layer.update()
 N=128;cols=8;rows=math.ceil(len(slabs)/cols);pixels=np.zeros((rows*N,cols*N,4),np.float32);pixels[:,:,3]=1
 image=bpy.data.images.new('SY | Courtyard localized wear and moisture',width=cols*N,height=rows*N,alpha=True);image.colorspace_settings.name='Non-Color'
 newm=[]
 for ma in floor_mats[:4]:
  m=ma.copy();m.name='SY | '+ma.name.split('|')[-1].strip()
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':n.image=image
   elif n.type=='VALTORGB':
    for e in n.color_ramp.elements:e.color=(*(min(.8,c*1.15) for c in e.color[:3]),e.color[3])
  newm.append(m)
 for idx,o in enumerate(slabs):
  lo,hi=bounds(o);w,h=hi.x-lo.x,hi.y-lo.y;tx,ty=idx%cols,idx//cols
  yy,xx=np.mgrid[0:N,0:N];u=np.clip((xx-2)/(N-5),0,1);v=np.clip((yy-2)/(N-5),0,1);X=lo.x+u*w;Y=lo.y+v*h
  edge=np.minimum.reduce([u*w,(1-u)*w,v*h,(1-v)*h]);variation=.5+.24*np.sin(X*2.1+Y*3.2)+.17*np.sin(X*4.1-Y*1.8)
  wear=np.clip(1-edge/.075,0,1)*np.clip((variation-.46)*2.7,0,.52)
  wear=np.maximum(wear,np.exp(-((u-.44)/.22)**2)*np.clip((variation-.69)*1.8,0,.20))
  damp=np.clip(1-edge/.19,0,1)*np.clip((.56-variation)*2,0,.40)
  # A handful of soft connected damp patches, not equally repeated puddles.
  for px,py,sx,sy in [(-30,14,1.6,.6),(-25,19,1.3,.45),(-15,27,.9,1.1),(-12,12,1.3,.6)]:
   r=((X-px)/sx)**2+((Y-py)/sy)**2;damp=np.maximum(damp,np.clip(1-r+.11*np.sin(X*7+Y*4),0,1)*.94)
  pixels[ty*N:(ty+1)*N,tx*N:(tx+1)*N,:3]=np.stack((wear,damp,variation),axis=-1)
  uv=o.data.uv_layers.new(name='GF_FloorMask')
  for loop in o.data.loops:
   p=o.matrix_world@o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((tx*N+2.5+(p.x-lo.x)/w*(N-5))/(cols*N),(ty*N+2.5+(p.y-lo.y)/h*(N-5))/(rows*N))
  o.data.materials[0]=newm[(idx*3+idx//4)%4]
 image.pixels.foreach_set(pixels.ravel());image.pack()
 report['floor']=dict(slabs=len(slabs),top=.009,base=-.007,joint=.026,atlas=list(image.size),max_height_change=.014)
 # Two low retaining pockets at the cliff-side yard edge, clear of staff entry.
 rocksource=next((o for o in s.objects if o.name.startswith('CY |') and 'boulder' in o.name.lower()),None)
 if rocksource:
  for j,(x,y,sc) in enumerate([(-36.8,14.7,.8),(-36.7,17.3,1.1),(-36.6,19.7,.7)]):
   o=rocksource.copy();o.name='SY | Cliff-foot boulder '+str(j);coll.objects.link(o);lo,hi=bounds(o);dims=hi-lo
   scale=Vector((1.5*sc/max(dims.x,.01),1.3*sc/max(dims.y,.01),1.1*sc/max(dims.z,.01)))
   o.scale=Vector([o.scale[k]*scale[k] for k in range(3)]);bpy.context.view_layer.update();lo,hi=bounds(o);o.location+=Vector((x-(lo.x+hi.x)/2,y-(lo.y+hi.y)/2,-.015-lo.z))
   report['props'].append(dict(type='boulder',xy=[x,y]))
 # Stone coping over existing planters, no additional plants in circulation.
 for x,y,w,h,z in [(-32,18,2.4,1.1,.53),(-22,17,2.4,1.1,.53),(-33,30.8,2.4,1.1,.53)]:
  for yy in (y-h/2,y+h/2):box('Planter coping long',(x,yy,z+.025),(w+.10,.11,.06),concrete,.008)
  for xx in (x-w/2,x+w/2):box('Planter coping return',(xx,y,z+.025),(.11,h-.10,.06),concrete,.008)

bpy.context.view_layer.update()
objects_by_name={o.name_full:o for o in s.objects};materials_by_name={m.name_full:m for m in bpy.data.materials}
assert all(fingerprint(objects_by_name[n])==sig for n,sig in report['original'].items()),'Original object mutated'
assert all(material_sig(materials_by_name[n])==sig for n,sig in report['materials'].items()),'Original material mutated'
assert all(sha(p)==h for p,h in report['libraries'].items()),'Linked source changed'
bad=[]
for o in coll.objects:
 if o.type!='MESH' or o.name.startswith('SY | Cliff-foot'):continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces):bad.append(o.name)
 bm.free()
assert not bad,('New mesh construction failed',bad)
assert sha(MAIN)==inspection['sha256'],'Main changed concurrently'
s.camera=bpy.data.objects['SY CAMERA | 01-front-yard'];bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(CAND));report['candidate_sha256']=sha(CAND);report['complete']=complete;report['protected_objects']=len(report['original']);report['new_objects']=len(coll.objects);report['manifold_failures']=bad
(OUT/'construction.json').write_text(json.dumps(report,indent=2));print('SPAWN_CANDIDATE_READY',complete,len(coll.objects),flush=True)
