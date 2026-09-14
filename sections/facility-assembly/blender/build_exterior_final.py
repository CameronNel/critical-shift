"""A14 concept-led ground-level exterior pass. Additive assembly-only work."""
import bpy,math,json,random,bmesh,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'connections/exterior-final';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A13_roof_services.blend'),load_ui=False)
bpy.context.view_layer.update();scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
L=json.loads((R/'production/LAYOUT_A12.json').read_text());bindings=json.loads((R/'connections/access/DOOR_BINDINGS.json').read_text())
ext=bpy.data.collections.new('22_EXTERIOR_FINISH_GEOMETRY');scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
sage=mat('A14 sage recovery enamel',(.17,.25,.13),.65,.2);ochre=mat('A14 ochre power enamel',(.50,.29,.075),.65,.2);terra=mat('A14 terracotta process enamel',(.38,.145,.075),.72,.15)
wood=mat('A14 oiled timber',(.26,.13,.06),.8);soil=mat('A14 dark planter earth',(.065,.048,.027),1);leafm=[mat('A14 olive leaf '+str(i),c,.88) for i,c in enumerate([(.13,.20,.065),(.22,.29,.11),(.29,.33,.15)])]
report={'entrances':[],'gutters':0,'downpipes':0,'planting_beds':0,'reference':'concepts/SCENE_PAINTOVER.png'}
def safe(x,y,r=.2):
 p=Vector((x,y))
 for route in L['routes']:
  if route['id']=='R19':continue
  for aa,bb in zip(route['points'],route['points'][1:]):
   a,b=Vector(aa).xy,Vector(bb).xy;v=b-a
   if v.length_squared<1e-6:continue
   t=max(0,min(1,(p-a).dot(v)/v.length_squared))
   if (p-a-v*t).length<route['width_m']/2+r:return False
 return True
def beam(name,a,b,width,height,material):
 a,b=Vector(a),Vector(b);v=b-a;o=box(name,(a+b)/2,(v.length,width,height),material,.006);o.rotation_euler.z=math.atan2(v.y,v.x);return o
def lettering(name,body,center,normal,width,size,material):
 c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.0005
 o=bpy.data.objects.new(name,c);ext.objects.link(o);o.location=center;o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();c.materials.append(material);return o
def lamp(center,normal,name):
 center=Vector(center);n=Vector(normal);x=n.cross(Vector((0,0,1))).normalized();p=center+n*.13
 backing=box(name+' lamp wall plate',center,(.16,.07,.48),steel,.009);backing.rotation_euler.z=math.atan2(n.y,n.x)-math.pi/2
 body=box(name+' opal lamp',p,(.14,.14,.28),ivory,.02)
 for z in [-.2,.2]:box(name+' lamp weather cap',p+Vector((0,0,z)),(.25,.25,.055),steel,.012)
 for dx in [-.10,.10]:rod(name+' lamp guard',p+x*dx+Vector((0,0,-.2)),p+x*dx+Vector((0,0,.2)),.012,steel)
 li=bpy.data.lights.new(name+' warm entrance light','POINT');li.energy=38;li.color=(1,.76,.48);li.shadow_soft_size=.3;ob=bpy.data.objects.new(li.name,li);ext.objects.link(ob);ob.location=p+n*.16
# Framed signs and mounted lamps, above the existing door opening.
labels={'spawn-room':'STAFF / ARRIVAL','mine':'GULLET MINE','refinery':'FUEL REFINERY','fuel-corridor':'FUEL TRANSFER','reactor-room':'REACTOR','cooling-plant':'COOLING PLANT','turbine-room':'TURBINE HALL','condenser-bay':'CONDENSER BAY','electrical-room':'ELECTRICAL','waste-storage':'WASTE HANDLING','medical-reanimation':'MEDICAL + RECOVERY','compliance-dock':'COMPLIANCE'}
seen=set()
for d in bindings:
 sid=d['sid']
 if sid in seen:continue
 seen.add(sid);pose=L['placements'][sid];m=Matrix.Translation(Vector(pose['translation']))@Matrix.Rotation(math.radians(pose['rotation_z_degrees']),4,'Z');n=(m.to_3x3()@Vector(d['normal'])).normalized();c=m@Vector(d['center']);w=d['width'];h=d['height'];t=Vector((n.y,-n.x,0));color=sage if sid in ['medical-reanimation','spawn-room','cooling-plant','compliance-dock'] else ochre if sid in ['electrical-room','turbine-room'] else terra
 # Spawn's final outer doorway, not its inner airlock, carries the exterior identity.
 if sid=='spawn-room':c=Vector((-28,12.38,0));h=2.7
 p=c+n*.19+Vector((0,0,h+.22));o=box(sid+' department fascia',p,(max(w,2.7),.10,.42),color,.012);o.rotation_euler.z=math.atan2(t.y,t.x)
 lettering(sid+' exterior identity',labels[sid],p+n*.061,n,w,.19 if len(labels[sid])>15 else .25,ivory)
 for sign in [-1,1]:
  q=c+t*sign*(w/2+.20)+n*.10+Vector((0,0,min(h-.2,2.35)));lamp(q,n,sid)
 report['entrances'].append(sid)
print('A14_ENTRANCES',len(seen),flush=True)
# Rainwater construction follows exact existing coping transforms.
for inst in bpy.data.collections['06_LINKED_EXTERIORS'].objects:
 if not inst.instance_collection:continue
 sid=inst.name.replace('EXTERIOR_INSTANCE_','');parts=list(inst.instance_collection.objects);caps=[o for o in parts if o.type=='MESH' and any(k in o.name.lower() for k in ['coping','weather cap','roof edge flashing','rear roof flashing']) and max(o.dimensions.x,o.dimensions.y)>2]
 if not caps:continue
 center=sum((inst.matrix_basis@o.location for o in caps),Vector())/len(caps)
 for j,o in enumerate(caps):
  m=inst.matrix_basis@o.matrix_basis;axis=Vector((1,0,0)) if o.dimensions.x>=o.dimensions.y else Vector((0,1,0));t=(m.to_3x3()@axis).normalized();length=max(o.dimensions.x,o.dimensions.y);c=m.translation;n=Vector((-t.y,t.x,0))
  if n.dot(c-center)<0:n=-n
  p=c+n*.13-Vector((0,0,.14));a=p-t*length/2;b=p+t*length/2
  beam(sid+' gutter tray',a,b,.18,.035,steel)
  for side in [-1,1]:beam(sid+' gutter folded lip',a+n*side*.09+Vector((0,0,.045)),b+n*side*.09+Vector((0,0,.045)),.025,.11,steel)
  for k in range(max(2,int(length/1.3))):
   q=a+(b-a)*(k+.5)/max(2,int(length/1.3));rod(sid+' gutter bracket',q-n*.19-Vector((0,0,.08)),q+Vector((0,0,-.04)),.016,steel)
  report['gutters']+=1
  if j%2:continue
  q=a+t*.22+n*.055
  if not safe(q.x,q.y,.23):continue
  hit,loc,*_=scene.ray_cast(dg,Vector((q.x,q.y,.3)),Vector((0,0,-1)),distance=8)
  if not hit or loc.z<-.3:continue
  foot=Vector((q.x,q.y,loc.z+.10));rod(sid+' rainwater downpipe',foot,q,.065,steel)
  for z in np.arange(foot.z+.35,q.z,.95):
   u=Vector((q.x,q.y,float(z)));rod(sid+' downpipe stand-off',u-n*.25,u,.018,steel);rod(sid+' pipe collar',u-Vector((0,0,.045)),u+Vector((0,0,.045)),.078,ivory)
  box(sid+' drain shoe',foot,(.30,.30,.14),steel,.02);report['downpipes']+=1
print('A14_RAINWATER',report['gutters'],report['downpipes'],flush=True)
# Fine leaf geometry with no alpha planes; existing planters define occupied footprints.
leafverts=[];leaffaces=[];leafids=[];random.seed(1409)
def leafcloud(x,y,z,r,count):
 for i in range(count):
  ang=random.uniform(0,math.tau);rr=r*math.sqrt(random.random());p=Vector((x+rr*math.cos(ang),y+rr*math.sin(ang),z+random.uniform(-r*.65,r*.65)));d=Vector((math.cos(ang),math.sin(ang),random.uniform(-.6,.6))).normalized()*.13;w=Vector((-d.y,d.x,.035)).normalized()*.028;k=len(leafverts);leafverts.extend([p-d,p+w,p+d,p-w,p+Vector((0,0,.018))]);leaffaces.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)]);leafids.extend([random.randrange(3)]*4)
def tree(x,y,z=0,r=.8):
 rod('Olive trunk',(x,y,z+.5),(x+.1,y,z+2.2),.065,wood)
 for j in range(7):
  a=j*math.tau/7;q=Vector((x+r*.6*math.cos(a),y+r*.6*math.sin(a),z+2.05+random.uniform(-.25,.35)));rod('Olive branching stem',(x+.1,y,z+1.6),q,.024,wood);leafcloud(*q,r*.58,100)
# Existing courtyard beds: layer fine foliage over the retained shrub mass.
for x,y in [(-32,18),(-22,17),(-8.6,22.5),(-33,30.8)]:
 tree(x,y,r=.75)
 for dx in [-.8,0,.8]:leafcloud(x+dx,y,.9,.4,90)
 report['planting_beds']+=1
# Route-screened new courtyard/service edge beds and bench pockets.
for x,y,sx,sy in [(9,58.3,3,.9),(19.5,58.3,3,.9),(70,38.8,3,.9),(78,42,2.8,.9),(-34,25,2,.8),(-10,31.1,2,.8),(44,20,2.5,.8),(42,-8,3,.8)]:
 if not all(safe(x+dx,y+dy,.1) for dx in [-sx/2,0,sx/2] for dy in [-sy/2,0,sy/2]):continue
 hit,loc,*_=scene.ray_cast(dg,Vector((x,y,.25)),Vector((0,0,-1)),distance=.6)
 if not hit:continue
 box('A14 planted edge bed',(x,y,.29),(sx,sy,.58),cream,.035);box('A14 planter terracotta band',(x,y,.20),(sx+.009,sy+.009,.10),terra,.004);box('A14 planter earth',(x,y,.595),(sx-.14,sy-.14,.03),soil,0)
 for dx in np.linspace(-sx*.35,sx*.35,4):
  rod('Shrub stem',(x+dx,y,.61),(x+dx+.04,y,1.10),.017,wood);leafcloud(x+dx,y,1.0,.38,90)
 report['planting_beds']+=1
# Fine planting in existing network beds; no change to their boundaries.
for o in bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'].objects:
 if 'planter' in o.name.lower() and o.type=='MESH':
  p=o.location;leafcloud(p.x,p.y,.96,.40,100)
me=bpy.data.meshes.new('Olive leaf geometry');me.from_pydata(leafverts,[],leaffaces)
for m in leafm:me.materials.append(m)
for p,idx in zip(me.polygons,leafids):p.material_index=idx
ob=bpy.data.objects.new('Olive leaf geometry',me);ext.objects.link(ob)
# Replace the repeated half-metre rail posts with merged straight retaining runs.
old=bpy.data.objects['A12 retaining guards and perimeter'];coords=np.array([v.co[:] for v in old.data.vertices]);n=len(coords)//8;groups={};remove=[]
for i in range(n):
 a=coords[i*8:(i+1)*8];lo=a.min(axis=0);hi=a.max(axis=0);c=(lo+hi)/2;sz=hi-lo
 if lo[2]<.1 or hi[2]>1.2 or abs(c[0])>100 or c[0]>80 or c[1]<-65 or c[1]>84:continue
 remove.append(i)
 if sz[2]>.10:continue
 if abs(c[2]-1.1)>.02:continue
 axis=0 if sz[0]>sz[1] else 1;fixed=round(float(c[1-axis]),3);groups.setdefault((axis,fixed),[]).append((float(lo[axis]),float(hi[axis])))
# Original mesh contains isolated eight-vertex boxes; rebuild retained components precisely.
keep=[p for p in old.data.polygons if p.vertices[0]//8 not in set(remove)];faces=[tuple(p.vertices) for p in keep];ids=[p.material_index for p in keep];me=bpy.data.meshes.new('A14 retained foundations and perimeter');me.from_pydata(coords.tolist(),[],faces)
for m in old.data.materials:me.materials.append(m)
for p,i in zip(me.polygons,ids):p.material_index=i
old.data=me;runs=0
for (axis,fixed),spans in groups.items():
 merged=[]
 for a,b in sorted(spans):
  if merged and a<=merged[-1][1]+.03:merged[-1][1]=max(merged[-1][1],b)
  else:merged.append([a,b])
 for a,b in merged:
  p=Vector((a,fixed,0)) if axis==0 else Vector((fixed,a,0));q=Vector((b,fixed,0)) if axis==0 else Vector((fixed,b,0))
  beam('Continuous retaining upstand',p+Vector((0,0,.32)),q+Vector((0,0,.32)),.13,.64,cream)
  for z in [.85,1.1]:beam('Retaining steel cap rail',p+Vector((0,0,z)),q+Vector((0,0,z)),.055,.055,steel)
  steps=max(1,math.ceil((b-a)/2))
  for j in range(steps+1):u=p+(q-p)*j/steps;rod('Retaining post',u+Vector((0,0,.6)),u+Vector((0,0,1.1)),.025,steel)
  runs+=1
report['merged_retaining_runs']=runs
# Cohesive material response on assembly-owned surfaces, preserving source libraries.
for m in bpy.data.materials:
 if m.library or not m.use_nodes:continue
 p=m.node_tree.nodes.get('Principled BSDF')
 if not p:continue
 name=m.name.lower()
 if any(k in name for k in ['concrete','mineral','plaster','paving']):p.inputs['Roughness'].default_value=.86
 if 'timber' in name:p.inputs['Roughness'].default_value=.75
sun=next((o for o in bpy.data.objects if o.type=='LIGHT' and o.data.type=='SUN'),None)
if sun:sun.data.energy=3.2;sun.data.color=(1,.88,.70);sun.data.angle=.065;sun.rotation_euler=(.55,-.5,-.8)
if scene.world and scene.world.use_nodes:
 bg=next((n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'),None)
 if bg:bg.inputs['Color'].default_value=(.53,.62,.74,1);bg.inputs['Strength'].default_value=.45
scene.view_settings.view_transform='AgX'
# Batched display; lights stay in a small independent collection.
lights=bpy.data.collections.new('24_EXTERIOR_PRACTICAL_LIGHTS');scene.collection.children.link(lights)
for o in list(ext.objects):
 if o.type=='LIGHT':ext.objects.unlink(o);lights.objects.link(o)
cache=bpy.data.collections.new('23_EXTERIOR_FINISH_VIEWPORT_CACHE');scene.collection.children.link(cache)
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in list(ext.objects):
 if o.type not in {'MESH','CURVE','FONT'}:continue
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.select_set(True);copies.append(cp)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='WALK_PROXY_EXTERIOR_FINISH';cache.hide_render=True;ext.hide_viewport=True
scene.name='FACILITY_A14_EXTERIOR';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[name].hide_viewport=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']:bpy.data.collections[name].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A14_exterior.blend'),compress=True)
report['authoring_objects']=len(ext.objects);report['viewport_cache_objects']=1;(O/'BUILD.json').write_text(json.dumps(report,indent=2));print('A14_SAVED',report,flush=True)
