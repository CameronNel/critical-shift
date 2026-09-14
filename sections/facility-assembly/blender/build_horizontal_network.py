"""Replayable horizontal facility network. Route envelopes remain unobstructed."""
import bpy,math,json,os,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network';OUT.mkdir(parents=True,exist_ok=True)
REV=os.environ.get('NETWORK_REVISION','R01')
L=json.loads((ROOT/'production/LAYOUT_CONNECTIONS_PLAN.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
ext=bpy.data.collections.new('09_FINISHED_HORIZONTAL_CONNECTIONS');scene.collection.children.link(ext)
helpers=(ROOT/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
sage=mat('NETWORK sage clean circulation',(.20,.29,.21),.73,.1)
ochre=mat('NETWORK ochre process',(.43,.27,.09),.7,.1)
paving=mat('NETWORK walkway concrete',(.46,.435,.37),.92)
timber=mat('NETWORK bench timber',(.25,.14,.07),.85)
soil=mat('NETWORK planting soil',(.07,.055,.03),1)
foliage=mat('NETWORK foliage olive',(.14,.22,.085),.86)
lens=mat('NETWORK warm lamp',(.82,.69,.43),.5)
# Ground-level route strips plus the reserved vertical approach, which must stay open.
segments=[]
for r in L['routes']:
 for a,b in zip(r['points'],r['points'][1:]):
  a,b=Vector(a),Vector(b)
  if abs(a.z)>.1 or abs(b.z)>.1 or (b-a).xy.length<.01:continue
  segments.append((r['id'],a,b,r['width_m']))
ports=[Vector(p) for p in L['ports'].values() if abs(p[2])<.1]
# Actual module bounds are conservative clipping boundaries for connector props.
rooms=[]
for sid,pose in L['placements'].items():
 if sid=='condenser-bay':continue
 survey=json.loads((ROOT/'sources'/sid/'survey.json').read_text());bounds=survey['all_visible_bounds'];ang=math.radians(pose['rotation_z_degrees']);c,s=math.cos(ang),math.sin(ang);t=pose['translation']
 # Keep oriented bounds rather than the excessively broad rotated world box.
 rooms.append((sid,bounds,c,s,t))

def in_room(x,y,pad=.1):
 for sid,b,c,s,t in rooms:
  xx=(x-t[0])*c+(y-t[1])*s;yy=-(x-t[0])*s+(y-t[1])*c
  if b[0][0]-pad<xx<b[1][0]+pad and b[0][1]-pad<yy<b[1][1]+pad:return True
 return False

def lane(x,y,extra=0):
 for rid,a,b,w in segments:
  v=b-a;v.z=0;t=max(0,min(1,((Vector((x,y,0))-a).dot(v))/(v.length_squared)))
  if (Vector((x,y,0))-(a+t*v)).length < w/2+extra:return True
 return False

def free(x,y,r=.2):
 # Keep C01 court, source door approaches and every crossing clear.
 if -35-r<x<-7+r and 15-r<y<32+r:return False
 if lane(x,y,r+.06):return False
 return not any(in_room(x+dx,y+dy,.04) for dx,dy in [(0,0),(r,r),(r,-r),(-r,r),(-r,-r)])

obstacles=[]
def place(name,pos,size,material,angle=0,check=True):
 # Axis-aligned bounding radius is deliberately conservative at intersections.
 if check and pos[2]-size[2]/2<2.3 and pos[2]+size[2]/2>.08:
  radius=math.hypot(size[0],size[1])/2
  if not free(pos[0],pos[1],radius):return None
 ob=box(name,pos,size,material,.008);ob.rotation_euler.z=angle
 if check and pos[2]-size[2]/2<2.3 and pos[2]+size[2]/2>.08:obstacles.append(ob.name)
 return ob

styles={'R01':'ore yard','R02':'transfer hall','R03':'process airlock','R04':'machinery hall','R05':'power courtyard','R06':'receiving court','R07':'rescue service street','R08':'service vestibule','R09':'clean promenade','R10':'spawn garden walk','R11':'medical approach','R12':'compliance airlock','R13':'clean vestibule','R14':'junction gallery','R15':'cooling garden route','R16':'cooling vestibule','R17':'power service court','R18':'waste service gallery','R20':'refinery personnel walk','R21':'maintenance crossover','R22':'rescue courtyard diagonal'}
closed={'R02','R03','R04','R08','R12','R13','R16'}
covered={'R14','R18'}
report=[];seen=set();floors=[]
for r in L['routes']:
 rid=r['id']
 if rid=='R19':continue
 before=set(ext.objects);w=r['width_m'];h=r['height_m'];colour=sage if r['kind']=='clean' else ochre if r['kind']=='freight' else accent
 for si,(aa,bb) in enumerate(zip(r['points'],r['points'][1:])):
  a,b=Vector(aa),Vector(bb);v=b-a;length=v.length
  if length<.02:continue
  u=v/length;n=Vector((-u.y,u.x,0));angle=math.atan2(u.y,u.x)
  key=tuple(sorted((tuple(a),tuple(b))))
  if key not in seen:
   seen.add(key)
   # Under original courtyard paving, above foundation. Union below removes duplicates.
   mid=(a+b)/2;ob=place(rid+' pavement',(*mid.xy,-.045),(length+.03,w+1.45,.05),paving,angle,False);floors.append(ob)
  step=1.0;count=max(1,math.ceil(length/step));pitch=length/count
  for i in range(count):
   d=(i+.5)*pitch;p=a+u*d
   for side in [-1,1]:
    q=p+n*side*(w/2+.80)
    if rid in closed:
     ob=place(rid+' insulated wall bay',(*q.xy,h/2),(pitch-.015,.22,h),cream,angle)
     if ob:
      place(rid+' wall plinth',(*(q-n*side*.13).xy,.22),(pitch-.02,.045,.44),base,angle,False)
      place(rid+' department stripe',(*(q-n*side*.14).xy,1.25),(pitch-.02,.02,.18),colour,angle,False)
      place(rid+' wall top flashing',(*q.xy,h+.035),(pitch+.02,.31,.07),steel,angle,False)
    elif i%2==0:
     # Raised planting/utility edges never close a route intersection.
     if rid in {'R01','R05','R06','R17','R18','R21'}:
      post=place(rid+' service edge post',(*q.xy,.58),(.08,.08,1.16),steel,angle)
      if post:
       for z in [.45,1.05]:place(rid+' edge guard rail',(*q.xy,z),(pitch,.05,.05),steel,angle)
   if rid in closed|covered:
    # Roofs span clear lanes. Source rooms stop roofs at actual door threshold.
    if not in_room(p.x,p.y,-.05):
     place(rid+' roof deck',(*p.xy,h+.13),(pitch+.02,w+2.1,.18),cream,angle,False)
     for side in [-1,1]:
      q=p+n*side*(w/2+.99);place(rid+' roof edge gutter',(*q.xy,h+.12),(pitch+.02,.16,.18),steel,angle,False)
  # Repeated structural bays, task lights and visibly supported overhead pipes.
  count=max(1,int(length/4));spacing=length/count
  for i in range(count):
   d=(i+.5)*spacing;p=a+u*d
   if in_room(p.x,p.y,.2):continue
   if rid in closed|covered:
    feet=[]
    for side in [-1,1]:
     q=p+n*side*(w/2+.95)
     col=place(rid+' frame upright',(*q.xy,h/2),(.14,.14,h),steel,angle)
     if col:
      place(rid+' anchor plate',(*q.xy,.025),(.34,.34,.05),steel,angle,False);feet.append(q)
    if feet:
     place(rid+' cross beam',(*p.xy,h-.10),(.18,w+2.25,.23),steel,angle,False)
     place(rid+' lamp housing',(*p.xy,h-.26),(.50,1.05,.10),steel,angle,False)
     place(rid+' lamp diffuser',(*p.xy,h-.318),(.42,.91,.012),lens,angle,False)
     ld=bpy.data.lights.new(rid+' task illumination','AREA');ld.energy=95;ld.color=(1,.85,.65);ld.shape='RECTANGLE';ld.size=1.1;lo=bpy.data.objects.new(ld.name,ld);ext.objects.link(lo);lo.location=(*p.xy,h-.35)
    if rid in closed:
     for off in [-.65,.65]:
      q=p+n*off;start=q-u*min(spacing*.48,1.8);end=q+u*min(spacing*.48,1.8)
      rod(rid+' supported overhead pipe',(*start.xy,h-.50),(*end.xy,h-.50),.10,colour)
      rod(rid+' pipe hanger',(*q.xy,h-.50),(*q.xy,h-.10),.02,steel)
      for endp in [start,end]:rod(rid+' pipe coupling',(*(endp-u*.045).xy,h-.50),(*(endp+u*.045).xy,h-.50),.14,steel)
   else:
    # Open sky routes get edge lighting and occasional shade bays.
    side=1 if i%2 else -1;q=p+n*side*(w/2+1.0)
    pole=place(rid+' path light column',(*q.xy,1.8),(.10,.10,3.6),steel)
    if pole:
     place(rid+' path lamp',(*q.xy,3.58),(.45,.45,.16),steel,0,False);place(rid+' path lamp lens',(*q.xy,3.49),(.34,.34,.025),lens,0,False)
    if i%3==1 and length>12:
     feet=[]
     for side in [-1,1]:
      q=p+n*side*(w/2+.7)
      if place(rid+' shade column',(*q.xy,1.65),(.15,.15,3.3),steel):
       place(rid+' shade baseplate',(*q.xy,.03),(.34,.34,.06),steel,0,False);feet.append(q)
     if len(feet)==2:
      for off in [-1.35,1.35]:
       q=p+u*off;place(rid+' shade beam',(*q.xy,3.30),(.18,w+1.65,.22),steel,angle,False)
      for off in [-1.2,-.8,-.4,0,.4,.8,1.2]:
       q=p+u*off;place(rid+' open shade slat',(*q.xy,3.47),(.22,w+1.6,.09),timber,angle,False)
  # Furnished side pockets: clean benches/planters vs utility supplies.
  for i in range(max(1,int(length/9))):
   p=a+u*((i+.5)*length/max(1,int(length/9)))
   for side in [-1,1]:
    q=p+n*side*(w/2+1.5)
    if not free(q.x,q.y,1.35):continue
    place(rid+' furnished alcove paving',(*q.xy,-.04),(3,2.4,.05),paving,angle,False)
    if r['kind']=='clean' or rid=='R15':
     place(rid+' planter',(*q.xy,.28),(2.1,.8,.56),cream,angle)
     place(rid+' planting soil',(*q.xy,.565),(1.96,.66,.02),soil,angle,False)
     for k in [-.7,-.35,0,.35,.7]:
      f=q+u*k;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.34,location=(*f.xy,.85));ob=bpy.context.object;ob.name=rid+' clipped olive shrub';ob.scale=(1,.7,.85)
      for c in list(ob.users_collection):c.objects.unlink(ob)
      ext.objects.link(ob);ob.data.materials.append(foliage)
     q=q+n*side*.8
     for dx in [-.65,.65]:
      f=q+u*dx;place(rid+' bench legs',(*f.xy,.23),(.10,.48,.44),steel,angle)
     for dy in [-.15,0,.15]:
      f=q+n*dy;place(rid+' timber seat',(*f.xy,.48),(1.8,.12,.06),timber,angle)
    else:
     for dx in [-.8,.8]:
      f=q+u*dx;place(rid+' spare rack legs',(*f.xy,.35),(.10,1.0,.7),steel,angle)
     for dz in [.45,.78]:
      for off in [-.3,0,.3]:
       f=q+n*off;rod(rid+' loose service pipe',(*(f-u*1.1).xy,dz),(*(f+u*1.1).xy,dz),.105,colour)
       for sg in [-1,1]:
        e=f+u*sg*1.04;rod(rid+' spare flange',(*(e-u*.035).xy,dz),(*(e+u*.035).xy,dz),.16,steel)
  # Destination plaques face along the approach and sit above player clearance.
  p=(a+b)/2
  if not in_room(p.x,p.y,.2) and (rid in closed|covered):
   place(rid+' destination sign',(*p.xy,h-.55),(.08,min(w-1,3),.38),colour,angle,False)
   text(rid+' route label',styles[rid].upper(),(*p.xy,h-.65),.16)
   ob=bpy.data.objects[rid+' route label'];ob.rotation_euler=(math.pi/2,0,angle-math.pi/2);ob.location-=u*.05
 # Open sliding-leaf architecture for airlocks. Animation/interlocks remain runtime binding.
 if rid in {'R03','R06','R12'}:
  a,b=Vector(r['points'][0]),Vector(r['points'][1]);u=(b-a).normalized();n=Vector((-u.y,u.x,0));angle=math.atan2(u.y,u.x)
  for d in [1.0,max(1.5,(b-a).length-1)]:
   p=a+u*d
   for side in [-1,1]:
    q=p+n*side*(w/2+.4)
    jamb=place(rid+' airlock jamb',(*q.xy,1.55),(.28,.25,3.1),steel,angle)
    if jamb:
     q2=p+n*side*(w/2+1.35)
     leaf=place(rid+' retracted sliding leaf',(*q2.xy,1.5),(.16,1.55,2.95),base,angle)
     if leaf:leaf['runtime_state']='OPEN; interlock and animation not bound'
     place(rid+' status lamp',(*(q-u*.2).xy,2.4),(.07,.14,.25),sage,angle,False)
   place(rid+' airlock header',(*p.xy,3.22),(.38,w+1.05,.32),steel,angle,False)
 report.append({'route':rid,'architecture':styles[rid],'objects':len(set(ext.objects)-before),'points':r['points'],'width_m':w,'status':'BUILT_HORIZONTAL_ARCHITECTURE'})
# Framed lateral junctions keep crossing routes open while completing hall edges.
framed=set()
for rid,a,b,w in segments:
 if rid not in closed:continue
 u=(b-a).normalized();n=Vector((-u.y,u.x,0));length=(b-a).length
 for other,c,d,ww in segments:
  if other==rid:continue
  v=d-c;den=u.x*v.y-u.y*v.x
  if abs(den)<.01:continue
  delta=c-a;t=(delta.x*v.y-delta.y*v.x)/den;q=(delta.x*u.y-delta.y*u.x)/den
  if not (0<=t<=length and 0<=q<=1):continue
  center=a+u*t
  key=(rid,round(center.x,2),round(center.y,2),round(ww,2))
  if key in framed:continue
  framed.add(key)
  hh=min(3.3,next(r['height_m'] for r in L['routes'] if r['id']==rid)-.25)
  for side in [-1,1]:
   p=center+n*side*(w/2+.8);posts=[]
   for sg in [-1,1]:
    e=p+u*sg*(ww/2+.36)
    ob=place(rid+' crossing portal jamb',(*e.xy,hh/2),(.16,.20,hh),steel,math.atan2(u.y,u.x))
    if ob:posts.append(e)
   if len(posts)==2:
    place(rid+' crossing portal lintel',(*p.xy,hh+.10),(ww+.9,.24,.20),steel,math.atan2(u.y,u.x),False)
    if rid in {'R02','R03','R12'}:
     place(rid+' retracted crossing shutter housing',(*p.xy,hh+.32),(ww+.85,.42,.24),base,math.atan2(u.y,u.x),False)
     for off in [-.06,0,.06]:place(rid+' rolled shutter lamella',(*(p+n*off).xy,hh+.23),(ww+.55,.018,.04),steel,math.atan2(u.y,u.x),False)
# Union overlapping roof panels at bends, leaving no coplanar roof patches.
roofs=[o for o in ext.objects if 'roof deck' in o.name]
if roofs:
 keep=roofs[0];tmp=bpy.data.collections.new('ROOF_UNION');scene.collection.children.link(tmp)
 for ob in roofs:
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 for ob in roofs[1:]:tmp.objects.link(ob)
 bpy.context.view_layer.objects.active=keep;mod=keep.modifiers.new('Continuous roof junctions','BOOLEAN');mod.operation='UNION';mod.operand_type='COLLECTION';mod.collection=tmp;mod.solver='EXACT';bpy.ops.object.modifier_apply(modifier=mod.name)
 for ob in roofs[1:]:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.collections.remove(tmp);keep.name='Network joined roof decks'
# Merge pavement overlaps by exact union, preventing coplanar artifacts.
if floors:
 base_floor=floors[0];tmp=bpy.data.collections.new('NETWORK_PAVING_UNION');scene.collection.children.link(tmp)
 for ob in floors:
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 for ob in floors[1:]:tmp.objects.link(ob)
 bpy.context.view_layer.objects.active=base_floor;mod=base_floor.modifiers.new('Union route paving','BOOLEAN');mod.operation='UNION';mod.operand_type='COLLECTION';mod.collection=tmp;mod.solver='EXACT';bpy.ops.object.modifier_apply(modifier=mod.name)
 for ob in floors[1:]:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.collections.remove(tmp);base_floor.name='Continuous horizontal network paving'
asset=OUT/f'network-{REV}.blend';bpy.data.libraries.write(str(asset),{ext},path_remap='RELATIVE',compress=True)
(OUT/f'BUILD_{REV}.json').write_text(json.dumps({'revision':REV,'routes':report,'objects':len(ext.objects),'excluded':'R19 vertical access is step 2, not part of horizontal build. Source door actuation remains step 2.','screened_obstacles':obstacles},indent=2))
# Review context: world-coordinate display cache, original source rooms untouched.
for filename,cname in [('walkthrough_proxy_meshes.blend','07_FAST_WALKTHROUGH_PROXIES'),('whole_map_floor.blend','08_WHOLE_MAP_FLOOR')]:
 with bpy.data.libraries.load(str(ROOT/'blender'/filename),link=False) as (src,dst):dst.collections=[cname]
 col=dst.collections[0];scene.collection.children.link(col);col.hide_render=False
 for ob in col.objects:
  ob.hide_render=False
  if ob.name in ['WALK_PROXY_medical-reanimation','WALK_PROXY_EXTERIOR_INSTANCE_medical-reanimation']:ob.location+=Vector((11,-6,0))
with bpy.data.libraries.load(str(ROOT/'connections/rescue-courtyard/courtyard-R04.blend'),link=False) as (src,dst):dst.collections=['CONNECTION_C01_RESCUE_COURTYARD']
scene.collection.children.link(dst.collections[0])
views=[('TOP',(-14,10,200),(-14,10,0),220),('PROCESS',(8,28,1.7),(18,28,1.7),None),('TRANSFER',(-5,-4,1.7),(3,-4,1.7),None),('POWER',(80,51,16),(69,35,0),None),('PROMENADE',(-35,28,1.7),(-10,28,1.7),None),('COOLING',(-31,47,14),(-10,57,0),None),('WASTE',(54,20,13),(46,11,0),None),('COMPLIANCE',(-49,9,12),(-41,20,0),None),('LOWER',(30,-13,15),(28,-3,0),None),('MINE',(4,-37,12),(-3,-25,0),None)]
for name,loc,target,ortho in views:
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();data.lens=28;data.clip_end=600
 if ortho:data.type='ORTHO';data.ortho_scale=ortho
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Warm facility sky');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.58,.67,.8,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.45;scene.world=world
ld=bpy.data.lights.new('Network afternoon sun','SUN');ld.energy=2.8;ld.angle=.12;ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.rotation_euler=(.55,-.55,-.8)
scene.view_settings.view_transform='AgX';scene.camera=bpy.data.objects['TOP']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'review-{REV}.blend'),compress=True)
print('NETWORK_BUILT',REV,len(ext.objects),flush=True)
