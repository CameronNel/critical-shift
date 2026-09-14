"""Replay R03 -> R04: contact repairs and irregular curved planting."""
import bpy,bmesh,json,random,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R03.blend'),load_ui=False)
ext=bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'];random.seed(904)
for ob in list(ext.objects):
 if ob.name.startswith('Spare pipe rack foot') or ob.name=='Wall planting bed.002':
  ob.location.z-=.0325;ob.dimensions.z+=.065
 if ob.name.startswith('Localised mineral finish wear'):bpy.data.objects.remove(ob,do_unlink=True)
# Rebuild the south conduit clear of the retained rainwater downpipe.
for ob in list(ext.objects):
 if any(ob.name.startswith('South '+n) for n in ['utility run','wall return','wall gland','saddle','split collar']):bpy.data.objects.remove(ob,do_unlink=True)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
steel=bpy.data.materials['S01 graphite folded steel'];orange=bpy.data.materials['S01 burnt orange identification'];base=bpy.data.materials['S01 plinth stone']
a=Vector((-34.8,.35,.45));b=Vector((-31.45,.35,.45));n=Vector((0,-1,0))
rod('South utility run',a,b,.055,steel)
for end in [a,b]:
 q=end-n*.50;rod('South wall return',end,q,.055,steel);rod('South wall gland',q-n*.018,q+n*.035,.097,orange)
for fac in [.05,.32,.65,.95]:
 p=a.lerp(b,fac);rod('South saddle',p-n*.50,p,.023,steel);rod('South split collar',p-Vector((0,0,.042)),p+Vector((0,0,.042)),.068,base)
ob=bpy.data.objects['S01 grouped broad leaf foliage'];bm=bmesh.new();bm.from_mesh(ob.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if max(v.co.z for v in f.verts)<1.4],context='FACES');bm.to_mesh(ob.data);bm.free()
verts=[];faces=[];indices=[]
def clump(x,y,z):
 for j in range(random.randint(7,13)):
  angle=random.random()*math.tau;h=random.uniform(.16,.43);bend=random.uniform(.06,.21);width=random.uniform(.012,.026);k=len(verts)
  side=Vector((-math.sin(angle),math.cos(angle),0));direction=Vector((math.cos(angle),math.sin(angle),0));root=Vector((x+random.uniform(-.03,.03),y+random.uniform(-.03,.03),z))
  for step in range(4):
   t=step/3;c=root+direction*bend*t*t+Vector((0,0,h*t));w=width*(1-t)*side
   verts.extend([c-w,c+w])
  for step in range(3):faces.append((k+step*2,k+step*2+1,k+step*2+3,k+step*2+2));indices.append(random.randrange(4))
build=json.loads((O/'BUILD_R03.json').read_text())
for x,y,sx,sy in build['planted_beds']:
 count=max(3,int(max(sx,sy)/.16))
 for j in range(count):clump(x+random.uniform(-1,1)*max(0,sx/2-.07),y+random.uniform(-1,1)*max(0,sy/2-.07),.22)
for x,y in [(-32,18),(-22,17),(-8.6,22.5),(-33,30.8)]:
 for j in range(18):clump(x+random.uniform(-.7,.7),y+random.uniform(-.25,.25),.69)
me=bpy.data.meshes.new('Curved irregular planting');me.from_pydata(verts,[],faces)
for i in range(4):me.materials.append(bpy.data.materials['S01 leaf mass '+str(i)])
for p,i in zip(me.polygons,indices):p.material_index=i
ob=bpy.data.objects.new('S01 curved planted grasses',me);ext.objects.link(ob)
bpy.context.view_layer.update();dest=R/'blender/facility_spawn_concept02_R04.blend';bpy.context.scene.name='FACILITY_SPAWN_CONCEPT02_R04'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
build.update(revision='R04',file=str(dest),repairs=['Rack and east bed bases extended to actual -0.065m apron','South return moved clear of downpipe','Curved irregular planting replaces even grass rows','Removed arbitrary pale wall patches'])
(O/'BUILD_R04.json').write_text(json.dumps(build,indent=2));print('R04_SAVED',flush=True)
