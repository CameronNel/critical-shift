"""A08 replayable vertical access and source portal controls; metres."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'connections/access';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
ext=bpy.data.collections.new('11_ACCESS_ARCHITECTURE');bpy.context.scene.collection.children.link(ext)
helpers=(ROOT/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
yellow=mat('ACCESS safety ochre',(.58,.36,.08),.62,.25)
green=mat('ACCESS enamel sage',(.21,.30,.23),.66,.25)
floor=mat('ACCESS galvanized tread',(.23,.25,.24),.62,.65)
dynamic=bpy.data.collections.new('12_ACCESS_MOVING_PARTS');bpy.context.scene.collection.children.link(dynamic)
def empty(name,loc=(0,0,0)):
 o=bpy.data.objects.new(name,None);dynamic.objects.link(o);o.location=loc;return o
def child_box(name,loc,size,m,parent):
 o=box(name,loc,size,m,.005);ext.objects.unlink(o);dynamic.objects.link(o);o.parent=parent;return o
def slab(name,x1,x2,y1,y2,z):return box(name,((x1+x2)/2,(y1+y2)/2,z-.10),(x2-x1,y2-y1,.2),floor)
def beam(name,a,b,width=.1,m=None):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,width,(b-a).length),m or steel,.005);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def rail(name,a,b):
 a,b=Vector(a),Vector(b)
 for dz in [.55,1.05]:rod(name+' rail',a+Vector((0,0,dz)),b+Vector((0,0,dz)),.025,yellow)
 for i in range(max(2,math.ceil((b-a).length/1.2)+1)):
  t=i/max(1,math.ceil((b-a).length/1.2));p=a.lerp(b,t);rod(name+' post',p,p+Vector((0,0,1.08)),.025,yellow)
# 36 equal risers, 34 treads, two flights. East flight passes BELOW the rescue deck.
for fi,(x,sign) in enumerate([(31.10,-1),(32.78,1)]):
 z0=-3*fi;y0=44.4 if fi==0 else 39.64
 for i in range(18):
  y=y0+sign*(i+.5)*.28;z=z0-(i+1)/6
  box(f'R19 flight {fi+1} tread {i+1:02}',(x,y,z-.045),(1.48,.28,.09),floor,.004)
  box('Contrasting nosing',(x,y-sign*.125,z+.002),(1.44,.025,.008),yellow,.001)
  if i<17:box('Closed stair riser',(x,y+sign*.14,z-.085),(1.48,.025,1/6),steel,.002)
 for xx in [x-.77,x+.77]:
  a=(xx,y0,z0-.18);b=(xx,y0+sign*5.04,z0-3-.18);beam('Continuous stair stringer',a,b,.12)
  rail('Stair guard',(xx,y0,z0),(xx,y0+sign*5.04,z0-3))
slab('Upper landing',30.25,31.95,44.4,46.5,0)
slab('Half landing',30.25,33.6,37.95,39.64,-3)
slab('Lower landing',30.25,35.5,44.4,46.65,-6)
rail('Half landing south',(30.25,37.95,-3),(33.6,37.95,-3))
rail('Lower landing west',(30.25,44.4,-6),(30.25,46.65,-6))
# Full-width lower passage and the lift branch; the door reveal ends at x48.3.
slab('Condenser passage',33.5,48.3,43.15,46.65,-6)
slab('Lift lower passage',31.15,35.5,33.3,36.5,-6)
slab('Lift branch',33.5,35.5,35,44.4,-6)
for y in [43.04,46.76]:
 box('Lower passage retaining wall',(41.25,y,-4.5),(13.5,.22,3),cream)
box('Lower passage ceiling',(41.25,44.9,-3.05),(13.5,3.7,.18),steel)
box('Lift branch east retaining wall',(35.62,39.3,-4.5),(.24,8.5,3),cream)
for y in [33.18,36.62]:box('Lift approach retaining wall',(32.3,y,-4.5),(2.3,.24,3),cream)
box('Lift branch west retaining wall',(33.68,40,-4.5),(.20,6.6,3),cream)
# Side guards around only the west opening: R14 x32..36 remains unobstructed.
rail('Ground stair west edge',(30.2,37.9,0),(30.2,44.4,0))
rail('Ground stair east edge',(31.90,37.9,0),(31.90,44.4,0))
rail('Ground stair south edge',(30.2,37.9,0),(31.9,37.9,0))
# Cart lift: east-facing 2.0m doorway, 2.0 x 2.8m clear cabin.
lift=empty('ACCESS_CART_LIFT');lift['access_lift']=True;lift['target_z']=0.;lift['floor_z']=0.;lift['speed']=1.0
lift.location=(0,0,0)
child_box('Lift platform',(30.05,34.85,-.10),(2.20,3.0,.2),floor,lift)
for y in [33.35,36.35]:child_box('Lift cabin side',(30.05,y,1.15),(2.2,.06,2.3),green,lift)
child_box('Lift cabin back',(28.95,34.85,1.15),(.06,3,2.3),green,lift)
child_box('Lift cabin roof',(30.05,34.85,2.4),(2.2,3,.12),steel,lift)
for x in [28.84,31.26]:
 for y in [33.22,36.48]:
  box('Lift shaft column',(x,y,-1.7),(.10,.10,9),steel)
  box('Lift shaft base',(x,y,-6.18),(.22,.22,.18),steel)
 for y in [33.20,36.50]:beam('Lift shaft diagonal',(x,y,-5.9),(x,y,2.7),.065)
for y in [33.2,36.5]:
 box('Lift shaft side safety screen',(30.05,y,-3),(2.5,.035,5.9),steel,.002)
box('Lift shaft back safety screen',(28.82,34.85,-3),(.035,3.3,5.9),steel,.002)
for z in [-6,0]:slab('Lift threshold bridge',31.15,32.1,33.35,36.35,z)
# Credible cantilever supports replace west R14 columns over new openings.
for y in [34.9375,39.5625,44.1875]:beam('R14 cantilever knee',(36.95,y,2.65),(33.5,y,3.55),.12)
bindings=json.loads((OUT/'DOOR_BINDINGS.json').read_text());poses=json.loads((ROOT/'production/LAYOUT_A07.json').read_text())['placements']
def door(key,c,n,w,h,group='',side='',gate=None):
 c=Vector(c);n=Vector(n);angle=math.atan2(-n.x,n.y)
 control=empty('DOOR_'+key,c);control.rotation_euler.z=angle
 control['access_door']=True;control['open']=1.;control['target']=1.;control['width']=w;control['height']=h;control['group']=group;control['side']=side
 if gate is not None:control['lift_gate_z']=gate
 # Roller collapses into the drum with its top fixed, preserving header clearance.
 pivot=empty('LEAF_'+key);pivot.parent=control;pivot.location=(0,0,h);pivot['door_leaf']=True
 child_box('Door steel curtain '+key,(0,0,-h/2),(w,.075,h),green,pivot)
 for zz in [.15+i*.25 for i in range(int(h/.25))]:child_box('Door horizontal seam',(0,-.043,-zz),(w,.008,.014),steel,pivot)
 pivot.scale.z=.015
 # Fixed housings and controls parented to the control but stay unscaled.
 child_box('Door roll housing '+key,(0,0,h+.13),(w+.16,.30,.26),steel,control)
 for x in [-w/2-.06,w/2+.06]:child_box('Door guide '+key,(x,0,h/2),(.08,.12,h),steel,control)
 child_box('Door call station '+key,(w/2+.16,-.07,1.15),(.16,.09,.30),yellow,control)
 return control
for d in bindings:
 p=poses[d['sid']];a=math.radians(p['rotation_z_degrees']);m=Matrix.Rotation(a,4,'Z');c=m@Vector(d['center'])+Vector(p['translation']);n=m.to_3x3()@Vector(d['normal'])
 door(d['id'],c,n,d['width'],d['height'],d['group'],d['side'])
for z in [0,-6]:door('lift_'+str(abs(z)),(31.20,34.85,z),(-1,0,0),2.8,2.3,gate=z)
# Two physical process-airlock boundaries and compliance pair.
for key,c,n,w,h,g,side in [('process_south',(14.2,25,0),(0,1,0),4,2.7,'process_airlock','fuel'),('process_north',(14.2,31,0),(0,1,0),4,2.7,'process_airlock','reactor'),('compliance_west',(-45.5,16,0),(1,0,0),3,2.7,'compliance_airlock','west'),('compliance_east',(-40,16,0),(1,0,0),3,2.7,'compliance_airlock','east')]:door(key,c,n,w,h,g,side)
# Warm practical light along basement; no cyan.
for x,y,z in [(35,44.9,-3.35),(40,44.9,-3.35),(45,44.9,-3.35),(32,38.2,-.9),(34.5,38,-3.4)]:
 box('Sealed bulkhead lamp',(x,y,z),(.5,.18,.08),ivory)
 data=bpy.data.lights.new('Access warm practical','AREA');data.energy=110;data.color=(1,.83,.61);data.shape='DISK';data.size=1.2;o=bpy.data.objects.new(data.name,data);ext.objects.link(o);o.location=(x,y,z-.08)
# Start with all interlocked doors safely shut; non-interlocked portals default open.
for o in dynamic.objects:
 if o.get('access_door') and (o.get('group') or o.get('lift_gate_z',0)==-6):
  o['open']=0.;o['target']=0.
  for ch in o.children:
   if ch.get('door_leaf'):ch.scale.z=1
bpy.data.libraries.write(str(OUT/'access-A08.blend'),{ext,dynamic},compress=True,path_remap='RELATIVE')
(OUT/'BUILD.json').write_text(json.dumps({'rise':6,'risers':36,'riser_m':1/6,'tread_m':.28,'clear_stair_width':1.48,'lift_clear_m':[2.0,2.8],'doors':sum(bool(o.get('access_door')) for o in dynamic.objects),'rescue_lane':[32,36],'floor_holes':[[30.25,31.95,37.9,44.4],[28.78,31.3,33.15,36.55]]},indent=2))
print('ACCESS_ASSET_READY',flush=True)
