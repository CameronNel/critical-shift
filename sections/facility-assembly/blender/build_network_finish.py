"""Finish all horizontal connector types against the existing network concept."""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish';random.seed(109)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(R/'connections/network/network-R03.blend'),link=False) as (src,dst):dst.collections=['09_FINISHED_HORIZONTAL_CONNECTIONS']
baseline=dst.collections[0];bpy.context.scene.collection.children.link(baseline)
ext=bpy.data.collections.new('15_FINISHED_NETWORK_SCENERY');bpy.context.scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
sage=mat('FINISH circulation sage enamel',(.23,.29,.19),.72,.2)
ochre=mat('FINISH process ochre enamel',(.50,.29,.075),.68,.3)
timber=mat('FINISH seasoned bench timber',(.30,.185,.075),.84)
metal=mat('FINISH service galvanized metal',(.29,.30,.27),.60,.65)
leaves=mat('FINISH olive foliage',(.14,.23,.08),.88)
L=json.loads((R/'production/LAYOUT_A08.json').read_text());routes={r['id']:r for r in L['routes']}
removed=set(json.loads((R/'connections/access/FINALIZE.json').read_text())['removed_access_obstructions'])
removed|=set(json.loads((R/'connections/access/INTEGRATION_walkthrough.json').read_text())['network_replaced'])
segments=[];rooms=[]
for rid,r in routes.items():
 if rid=='R19':continue
 for aa,bb in zip(r['points'],r['points'][1:]):
  a,b=Vector(aa),Vector(bb)
  if (b-a).length>.02:segments.append((rid,a,b,float(r['width_m'])))
for sid,p in L['placements'].items():
 if sid=='condenser-bay':continue
 bounds=json.loads((R/'sources'/sid/'survey.json').read_text())['all_visible_bounds'];a=math.radians(p['rotation_z_degrees']);rooms.append((bounds,math.cos(a),math.sin(a),p['translation']))
def room(x,y,pad=.20):
 for b,c,s,t in rooms:
  xx=(x-t[0])*c+(y-t[1])*s;yy=-(x-t[0])*s+(y-t[1])*c
  if b[0][0]-pad<xx<b[1][0]+pad and b[0][1]-pad<yy<b[1][1]+pad:return True
 return False
def safe(x,y,pad=.1):
 if room(x,y,pad):return False
 if 28.7-pad<x<32+pad and 33-pad<y<46.8+pad:return False
 # The finished medical courtyard retains its dedicated scenery.
 if -35-pad<x<-7+pad and 15-pad<y<32+pad:return False
 p=Vector((x,y,0))
 for rid,a,b,w in segments:
  v=b-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared))
  if (p-(a+t*v)).length<w/2+pad:return False
 return True
def textface(name,body,loc,size,normal,material=ivory):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0005
 ob=bpy.data.objects.new(name,cu);ext.objects.link(ob);ob.location=loc;ob.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();cu.materials.append(material);return ob
def locbox(name,p,size,m,angle=0,bev=.004):
 o=box(name,p,size,m,bev);o.rotation_euler.z=angle;return o
report={rid:0 for rid in routes if rid!='R19'}
# Detail the actual surviving wall bays. No new wall spans or route closures.
wallcounts={}
for o in baseline.objects:
 if o.name in removed or 'insulated wall bay' not in o.name:continue
 rid=o.name[:3];before=len(ext.objects);wallcounts[rid]=wallcounts.get(rid,0)+1
 p=o.location.copy();a=o.rotation_euler.z;u=Vector((math.cos(a),math.sin(a),0));n=Vector((-u.y,u.x,0))
 candidates=[(aa,bb) for rr,aa,bb,w in segments if rr==rid]
 aa,bb=min(candidates,key=lambda ab:((ab[0]+ab[1])/2-p).length)
 v=bb-aa;t=max(0,min(1,(p-aa).dot(v)/v.length_squared));inward=(aa+t*v)-p;inward.z=0
 if inward.dot(n)<0:n=-n
 span=o.dimensions.x;q=p+n*.137;h=o.dimensions.z
 locbox(rid+' lower service skin',(q.x,q.y,.73),(span-.035,.03,.88),sage if routes[rid]['kind']=='clean' else base,a)
 for xx in [-span*.40,span*.40]:
  f=q+u*xx+n*.02
  for z in [.37,1.08]:rod(rid+' wall skin captive bolt',(f.x,f.y,z),(f.x+n.x*.015,f.y+n.y*.015,z),.017,metal)
 # Rigid conduit runs are clipped to the wall rather than floating in space.
 p1=q-u*(span/2-.025)+n*.03;p2=q+u*(span/2-.025)+n*.03
 rod(rid+' wall electrical conduit',(*p1.xy,2.25),(*p2.xy,2.25),.022,metal)
 locbox(rid+' conduit saddle',(*q.xy,2.25),(.07,.10,.06),steel,a)
 if wallcounts[rid]%6==2:
  f=q+n*.11;locbox(rid+' local junction enclosure',(*f.xy,1.62),(.35,.20,.46),sage,a,.01)
  f+=n*.111;textface(rid+' enclosure stencil','LOCAL\nISOLATOR',(*f.xy,1.61),.065,n)
  f=q+n*.04;rod(rid+' enclosure conduit drop',(*f.xy,1.85),(*f.xy,2.25),.022,metal)
 if wallcounts[rid]%7==1:
  f=q+n*.026;textface(rid+' route stencil',rid+' / '+routes[rid].get('kind','SERVICE').upper(),(*f.xy,1.74),.095,n,steel)
 report[rid]+=len(ext.objects)-before
# Visible fasteners on surviving post feet.
for o in baseline.objects:
 if o.name in removed or 'anchor plate' not in o.name:continue
 if o.name.startswith('R14') and 30.7<o.location.x<31.4 and 33<o.location.y<44.5:continue
 rid=o.name[:3];p=o.location
 for dx in [-.11,.11]:
  for dy in [-.11,.11]:rod(rid+' structural anchor', (p.x+dx,p.y+dy,.047),(p.x+dx,p.y+dy,.071),.020,metal)
 report[rid]+=4
# Replace the visually disconnected overhead spools with continuous supported runs.
closed={'R02','R03','R04','R08','R12','R13','R16'}
for rid,a,b,w in segments:
 before=len(ext.objects);v=b-a;length=v.length;u=v/length;n=Vector((-u.y,u.x,0));ang=math.atan2(u.y,u.x);h=routes[rid]['height_m']
 if rid in closed:
  for off in [-.65,.65]:
   aa=a+u*.32+n*off;bb=b-u*.32+n*off
   rod(rid+' continuous overhead service',(*aa.xy,h-.50),(*bb.xy,h-.50),.10,ochre if off<0 else metal)
   for i in range(max(2,math.ceil(length/2.8))):
    t=.45+i*(length-.9)/(max(2,math.ceil(length/2.8))-1);p=a+u*t+n*off
    rod(rid+' overhead union',(*(p-u*.045).xy,h-.50),(*(p+u*.045).xy,h-.50),.13,steel)
    rod(rid+' threaded hanger',(*p.xy,h-.50),(*p.xy,h-.07),.019,metal)
    locbox(rid+' hanger roof plate',(*p.xy,h-.025),(.20,.16,.035),steel,ang)
 # Edge drainage is checked against EVERY route, including crossing routes.
 count=max(1,int(length/.9));pitch=length/count
 for i in range(count):
  p=a+u*((i+.5)*pitch)
  for side in [-1,1]:
   q=p+n*side*(w/2+.35)
   if not all(safe(*(q+u*off).xy,.12) for off in [-pitch*.48,0,pitch*.48]):continue
   locbox(rid+' inset edge drain',(*q.xy,-.009),(pitch-.02,.18,.016),steel,ang,.001)
   for off in [-pitch*.32,0,pitch*.32]:
    z=q+u*off;locbox(rid+' drain grate slot',(*z.xy,.001),(.025,.145,.004),rubber,ang,.0005)
 # A line of small, supported direction markers outside the walking lane.
 for frac in [.25,.75]:
  q=a+u*(length*frac)+n*(w/2+.62)
  if not safe(q.x,q.y,.22):continue
  locbox(rid+' department edge marker',(*q.xy,.43),(.24,.10,.86),sage if routes[rid]['kind']=='clean' else ochre,ang,.008)
  textface(rid+' marker id',rid,(*(q-n*.058).xy,.62),.11,-n)
 report[rid]+=len(ext.objects)-before
# Finish clean-area seating and add shade trees rooted in existing planters.
for o in baseline.objects:
 rid=o.name[:3]
 if rid not in report:continue
 if 'planter' in o.name and 'soil' not in o.name and routes[rid]['kind']=='clean':
  p=o.location.copy();p.z=.55
  if not safe(p.x,p.y,.16):continue
  rod(rid+' young olive trunk',p,(p.x+.08,p.y,2.8),.05,timber)
  for a in [0,2.1,4.2]:
   q=Vector((p.x+.43*math.cos(a),p.y+.43*math.sin(a),2.62));rod(rid+' olive branch',(p.x,p.y,1.8),q,.025,timber)
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.56,location=q+Vector((0,0,.20)));tree=bpy.context.object;tree.name=rid+' olive canopy';tree.scale=(1,1,.65)
   for c in list(tree.users_collection):c.objects.unlink(tree)
   ext.objects.link(tree);tree.data.materials.append(leaves)
  report[rid]+=7
 if 'bench legs' in o.name:
  p=o.location.copy();ang=o.rotation_euler.z;n=Vector((-math.sin(ang),math.cos(ang),0));q=p+n*.28
  if safe(q.x,q.y,.08):locbox(rid+' bench back support',(*q.xy,.66),(.055,.055,.68),steel,ang);report[rid]+=1
# Bolt lids and pipe-rack base shoes make the retained outdoor hardware sit properly.
for o in baseline.objects:
 if o.name in removed or 'spare rack legs' not in o.name:continue
 p=o.location
 if not safe(p.x,p.y,.18):continue
 rid=o.name[:3];locbox(rid+' rack foot shoe',(*p.xy,.023),(.27,.27,.045),steel,o.rotation_euler.z);report[rid]+=1
baseline.hide_viewport=True;baseline.hide_render=True
cache=bpy.data.collections.new('16_NETWORK_FINISH_VIEWPORT_CACHE');bpy.context.scene.collection.children.link(cache)
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in list(ext.objects):
 if o.type not in {'MESH','CURVE','FONT'}:continue
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.select_set(True);copies.append(cp)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='WALK_PROXY_NETWORK_FINISH';cache.hide_render=True
bpy.data.libraries.write(str(O/'network-finish-A10.blend'),{ext,cache},compress=True,path_remap='RELATIVE')
(O/'NETWORK_BUILD.json').write_text(json.dumps({'route_added_objects':report,'authoring_objects':len(ext.objects),'viewport_faces':len(bpy.context.object.data.polygons),'concept':'../network/art/concept-network.png','clearance_rule':'New low-level edge scenery is screened against every route and room footprint.'},indent=2))
print('NETWORK_FINISH_BUILT',len(ext.objects),report,flush=True)
