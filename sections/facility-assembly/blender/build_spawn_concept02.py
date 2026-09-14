"""Replayable approved Concept02 exterior pass. Source room libraries stay read-only."""
import bpy,math,json,random,hashlib,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review';REV=os.environ.get('SPAWN_REV','R01')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_master_A14_exterior.blend'),load_ui=False)
scene=bpy.context.scene;random.seed(215)
ext=bpy.data.collections.new('29_SPAWN_APPROVED_EXTERIOR');scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
def paint(name,color,rough=.8,metal=0):
 m=mat('S01 '+name,color,rough,metal)
 # Broad restrained pigment variation, no microscopic grain/bump.
 for n in list(m.node_tree.nodes):
  if n.type=='BUMP':m.node_tree.nodes.remove(n)
  elif n.type=='TEX_NOISE':n.inputs['Scale'].default_value=2.3;n.inputs['Detail'].default_value=0
  elif n.type=='VALTORGB':
   n.color_ramp.elements[0].color=(*(c*.91 for c in color),1);n.color_ramp.elements[1].color=(*(min(c*1.045,1) for c in color),1)
 return m
cream=paint('warm mineral ivory',(.58,.48,.33));olive=paint('deep olive painted sheet',(.105,.135,.064),.7,.12);steel=paint('graphite folded steel',(.045,.059,.060),.62,.3)
orange=paint('burnt orange identification',(.63,.205,.036),.72,.12);ivory=paint('sign ivory',(.83,.76,.56),.66)
wood=paint('warm timber',(.33,.135,.037),.83);soil=paint('dark earth',(.055,.037,.018),1);paving=paint('courtyard limestone concrete',(.53,.45,.33),.92);base=paint('plinth stone',(.24,.235,.195),.87)
wear=paint('restrained mineral wear',(.44,.39,.29),.91);rubber=paint('gasket rubber',(.024,.03,.027),.94)
leafm=[paint('leaf mass '+str(i),c,.91) for i,c in enumerate([(.095,.14,.035),(.17,.235,.068),(.29,.34,.095),(.41,.40,.12)])]
spawn=bpy.data.objects['EXTERIOR_INSTANCE_spawn-room'];materials={};overrides=[]
def material_for(m):
 if not m:return None
 n=m.name.lower()
 if 'locker olive' in n:return olive
 if any(k in n for k in ['mineral','concrete']):return cream
 if any(k in n for k in ['charcoal','coping','steel']):return steel
 if 'plinth' in n:return base
 return m
# A14 exterior wrapper is already local. Copy its object links before overriding slots.
def clone(c):
 new=bpy.data.collections.new('S01_'+c.name)
 for o in list(c.objects):
  cp=o.copy();new.objects.link(cp)
  if cp.type=='MESH':
   for sl in cp.material_slots:
    m=sl.material;replacement=material_for(m)
    if replacement!=m:sl.link='OBJECT';sl.material=replacement
   overrides.append(cp.name)
 for child in c.children:new.children.link(clone(child))
 return new
spawn.instance_collection=clone(spawn.instance_collection)
# Scope all shared-scene overrides to this courtyard, leaving other departments intact.
def in_courtyard(o):
 p=o.matrix_basis.translation
 return -38<p.x<-7 and 13<p.y<32
for cn in ['CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS','15_FINISHED_NETWORK_SCENERY','22_EXTERIOR_FINISH_GEOMETRY']:
 for o in bpy.data.collections[cn].objects:
  if o.type!='MESH' or not in_courtyard(o):continue
  for sl in o.material_slots:
   if not sl.material:continue
   name=sl.material.name.lower();rep=None
   if any(k in name for k in ['timber','wood']):rep=wood
   elif any(k in name for k in ['concrete','paving','mineral']):rep=paving
   elif 'soil' in name or 'earth' in name:rep=soil
   if rep:sl.link='OBJECT';sl.material=rep
for o in bpy.data.collections['22_EXTERIOR_FINISH_GEOMETRY'].objects:
 if o.type=='MESH' and o.name.startswith('spawn-room department fascia'):
  for sl in o.material_slots:sl.link='OBJECT';sl.material=orange
def label(name,body,p,normal,size,material=ivory):
 c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.0004
 o=bpy.data.objects.new(name,c);ext.objects.link(o);o.location=p;o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();c.materials.append(material);return o
ledger=[]
def fixture(o,purpose,support):o['purpose']=purpose;o['support']=support;ledger.append({'object':o.name,'purpose':purpose,'support':support});return o
# Controlled orange arrival surround. Existing 2.6m rear aperture stays unchanged.
for x in [-29.58,-26.42]:
 fixture(box('Arrival orange jamb inlay',(x,12.49,2.77),(.16,.025,.60),orange,.006),'entry identification','existing rear pier')
fixture(box('South canopy orange folded fascia',(-28,-.966,3.20),(2.95,.032,.14),orange,.004),'shift entry accent','existing south canopy fascia')
# Compact exterior cabinets on real wall faces; no live rating claims.
def cabinet(prefix,c,normal):
 c=Vector(c);n=Vector(normal);t=Vector((-n.y,n.x,0));angle=math.atan2(t.y,t.x)
 def panel(name,center,size,mat):
  o=box(prefix+' '+name,center,size,mat,.014);o.rotation_euler.z=angle;return o
 panel('mounting backing',c,(.91,.08,1.02),steel)
 body=panel('enclosure',c+n*.16,(.79,.31,.87),base);fixture(body,'local exterior service disconnect','backing plate and four wall anchors')
 panel('folded door',c+n*.324,(.72,.035,.80),cream)
 panel('rain hood',c+n*.18+Vector((0,0,.51)),(.99,.47,.055),steel)
 panel('door handle',c+n*.36+t*.25,(.035,.044,.17),steel)
 for xx in [-.37,.37]:
  for z in [-.43,.43]:rod(prefix+' wall fixing',c+t*xx+Vector((0,0,z))-n*.16,c+t*xx+Vector((0,0,z))+n*.09,.028,steel)
 label(prefix+' name','LOCAL SERVICE',c+n*.35+Vector((0,0,.24)),n,.072,steel)
 label(prefix+' caution','!',c+n*.35+Vector((0,0,.03)),n,.19,orange)
 for z in [-.12,-.16,-.20]:panel('door vent',c+n*.347+Vector((0,0,z)),(.25,.008,.011),steel)
 return c
south=cabinet('South service',(-33.65,.70,1.10),(0,-1,0))
east=cabinet('East service',(-19.64,3.0,1.12),(1,0,0))
# Pipework physically turns into the building through labelled wall glands.
for prefix,a,b,n in [('South',(-35.1,.35,.45),(-31.45,.35,.45),Vector((0,-1,0))),('East',(-19.34,2,.65),(-19.34,6.25,.65),Vector((1,0,0)))]:
 a,b=Vector(a),Vector(b);fixture(rod(prefix+' utility run',a,b,.055,steel),'local service conduit','wall saddles; wall glands at both ends')
 for end in [a,b]:
  q=end-n*.50;rod(prefix+' wall return',end,q,.055,steel);rod(prefix+' wall gland',q-n*.018,q+n*.035,.097,orange)
 for fac in [.05,.32,.65,.95]:
  p=a.lerp(b,fac);rod(prefix+' saddle',p-n*.50,p,.023,steel);rod(prefix+' split collar',p-Vector((0,0,.042)),p+Vector((0,0,.042)),.068,base)
# South hose: closed stowed coils on a wall reel, safely beside the doorway.
for j in range(4):
 pts=[Vector((-32.35+(.235-j*.035)*math.cos(i*math.tau/32),.33-j*.012,1.22+(.235-j*.035)*math.sin(i*math.tau/32))) for i in range(33)]
 for a,b in zip(pts,pts[1:]):rod('Stowed hose coil',a,b,.019,orange)
fixture(box('Hose reel mounting',(-32.35,.64,1.22),(.18,.34,.25),steel,.015),'stowed maintenance hose','south wall')
# Spare pipes on a low rack along the east apron, kept off the route.
for y in [4.45,6.05]:
 fixture(box('Spare pipe rack foot',(-19.27,y,.075),(.48,.12,.15),steel),'stored spare pipe rack','east apron ground')
 box('Spare pipe rack cradle',(-19.27,y,.19),(.45,.12,.12),base)
for dx,z in [(-.11,.33),(.11,.33),(0,.50)]:
 rod('Capped spare pipe',(-19.27+dx,4.20,z),(-19.27+dx,6.30,z),.085,orange)
 for y in [4.21,6.29]:rod('Spare pipe end cap',(-19.27+dx,y-.015,z),(-19.27+dx,y+.015,z),.094,steel)
for y in [4.53,5.94]:box('Pipe storage strap',(-19.27,y,.40),(.42,.048,.32),steel,.004)
# Narrow planted beds along existing wall aprons, never across an entrance.
beds=[(-22.75,.27,5.3,.40),(-33.65,.56,3.25,.32),(-19.46,7.0,.34,.72),(-23.25,7.63,5.45,.36),(-33.35,6.45,3.5,.32),(-29.99,10.3,.30,3.1),(-26.0,10.3,.30,3.1)]
L=json.loads((R/'production/LAYOUT_A12.json').read_text())
def on_route(x,y,margin=.02):
 p=Vector((x,y))
 for route in L['routes']:
  if route['id']=='R19':continue
  for aa,bb in zip(route['points'],route['points'][1:]):
   a,b=Vector(aa).xy,Vector(bb).xy;d=b-a
   if d.length_squared<1e-8:continue
   q=a+d*max(0,min(1,(p-a).dot(d)/d.length_squared))
   if (p-q).length<route['width_m']/2+margin:return True
 return False
V=[];F=[];I=[]
def leaf(center,direction,length,width,index):
 d=Vector(direction).normalized()*length;w=d.cross(Vector((0,0,1)))
 if w.length<.001:w=Vector((1,0,0))
 w.normalize();w*=width;c=Vector(center);k=len(V)
 V.extend([c-d,c-d*.42+w*.72,c+d*.38+w,c+d,c+d*.38-w,c-d*.42-w*.72,c+Vector((0,0,.018))])
 for a in range(6):F.append((k+a,k+(a+1)%6,k+6));I.append(index)
def grass(x,y,z):
 for k in range(11):
  a=k*2.4;d=Vector((math.cos(a)*.11,math.sin(a)*.11,random.uniform(.24,.40)))
  leaf(Vector((x,y,z))+d*.5,d,d.length*.65,.026,random.randrange(4))
accepted=[]
for x,y,sx,sy in beds:
 if any(on_route(x+dx,y+dy) for dx in [-sx/2,sx/2] for dy in [-sy/2,sy/2]):continue
 fixture(box('Wall planting bed',(x,y,.10),(sx,sy,.20),base,.025),'maintained planted wall margin','existing exterior apron')
 box('Bed inset earth',(x,y,.205),(max(sx-.07,.05),max(sy-.07,.05),.02),soil,.001)
 for i in range(max(2,int(max(sx,sy)/.23))):
  u=(i+.5)/max(2,int(max(sx,sy)/.23))-.5;grass(x+u*max(sx-.12,0),y+u*max(sy-.12,0),.24)
 accepted.append((x,y,sx,sy))
# Fill the EXISTING courtyard tree canopies with broader, deliberately grouped leaves.
for x,y in [(-32,18),(-22,17),(-8.6,22.5),(-33,30.8)]:
 for j in range(8):
  a=j*math.tau/8;center=Vector((x+.48*math.cos(a),y+.48*math.sin(a),2.15+random.uniform(-.18,.36)))
  for k in range(130):
   d=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.8,.8)));q=center+d*.44
   leaf(q,d,.10+random.random()*.04,.053,random.randrange(4))
 for dx in [-.7,-.35,0,.35,.7]:grass(x+dx,y,.70)
me=bpy.data.meshes.new('S01 shaped foliage');me.from_pydata(V,[],F)
for m in leafm:me.materials.append(m)
for p,i in zip(me.polygons,I):p.material_index=i
ob=bpy.data.objects.new('S01 grouped broad leaf foliage',me);ext.objects.link(ob)
# Retained roof machinery gains explicit visible service pads and subtle membrane seams.
# The existing A13 unit already has a membrane pad and anchored load spreaders.
for x in [-34,-32.5,-25.7,-24.2,-22.7,-21.2]:
 z=3.58 if x<-30 else 3.98
 box('Roof membrane lap seam',(x,3.6,z),(.014,5.0,.004),base,0)
# Selective broad plaster/paint wear: small designed polygon marks, not a noise blanket.
for x,y,z,n in [(-34,.773,1.8,'S'),(-30.9,.773,.9,'S'),(-22.7,.450,1.2,'S'),(-19.62,5.7,1.9,'E'),(-19.62,4.1,2.9,'E')]:
 for j in range(3):
  a=.08+random.random()*.09;b=.07+random.random()*.14;dx=random.uniform(-.20,.20);dz=random.uniform(-.20,.20)
  pts=[(-a,-b),(-a*.75,b*.4),(-a*.1,b),(.3*a,.6*b),(a,b*.7),(.55*a,-b)]
  vv=[(x+u+dx,y,z+v+dz) if n=='S' else (x,y+u+dx,z+v+dz) for u,v in pts]
  mesh=bpy.data.meshes.new('paint wear');mesh.from_pydata(vv,[],[tuple(range(6))]);mesh.materials.append(wear);oo=bpy.data.objects.new('Localised mineral finish wear',mesh);ext.objects.link(oo)
# Warm readable directional sunlight; no ray tracing required by this preview.
for ob in bpy.data.objects:
 if ob.type=='LIGHT' and ob.data.type=='SUN' and not ob.library:
  if ob.data.library:ob.data=ob.data.copy()
  ob.data.energy=2.5;ob.data.color=(1,.91,.76);ob.data.angle=.04
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
scene.name='FACILITY_SPAWN_CONCEPT02_'+REV
dest=R/'blender'/('facility_spawn_concept02_'+REV+'.blend')
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={'revision':REV,'approved_concept':'SPAWN_EXTERIOR_CONCEPT_02.png','approval':'Cameron: Implement that','file':str(dest),'new_objects':len(ext.objects),'new_faces':sum(len(o.data.polygons) for o in ext.objects if o.type=='MESH'),'spawn_exterior_overrides':len(overrides),'planted_beds':accepted,'fixture_ledger':ledger,'scope':'Spawn exterior + adjoining courtyard. Source room libraries unchanged. Neighbor mine rock and distant landscape remain separate-section work.'}
(O/('BUILD_'+REV+'.json')).write_text(json.dumps(report,indent=2));print('SPAWN_BUILD_SAVED',dest,flush=True)
