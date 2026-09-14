"""R11 -> R12: calm stone pigment and rounded clustered tree foliage."""
import bpy,json,random,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R11.blend'),load_ui=False)
m=bpy.data.materials['S01 warm broad-plane exterior stone']
for n in m.node_tree.nodes:
 if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=.2;n.inputs['Detail'].default_value=.7
 if n.type=='VALTORGB':
  n.color_ramp.interpolation='EASE'
  for e,c in zip(n.color_ramp.elements,[(.28,.21,.14,1),(.31,.24,.17,1),(.34,.27,.19,1),(.38,.30,.21,1)]):e.color=c
ext=bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'];old=bpy.data.objects['S01 grouped broad leaf foliage'];bpy.data.objects.remove(old,do_unlink=True)
random.seed(912);V=[];F=[];I=[]
for x,y in [(-32,18),(-22,17),(-8.6,22.5),(-33,30.8)]:
 for cluster in range(9):
  a=cluster*math.tau/9;center=Vector((x+.43*math.cos(a),y+.43*math.sin(a),2.2+random.uniform(-.2,.28)));shade=random.randrange(3)
  for j in range(95):
   p=center+Vector((random.uniform(-.35,.35),random.uniform(-.35,.35),random.uniform(-.3,.3)))
   d=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.55,.55))).normalized();w=d.cross(Vector((0,0,1))).normalized();length=random.uniform(.08,.12);width=random.uniform(.055,.075);k=len(V)
   for t in range(10):
    a=t*math.tau/10;V.append(p+d*math.cos(a)*length+w*math.sin(a)*width)
   V.append(p+Vector((0,0,.016)))
   for t in range(10):F.append((k+t,k+(t+1)%10,k+10));I.append(min(3,shade+(j%5==0)))
me=bpy.data.meshes.new('S01 rounded olive canopy leaves');me.from_pydata(V,[],F)
for i in range(4):me.materials.append(bpy.data.materials['S01 leaf mass '+str(i)])
for p,i in zip(me.polygons,I):p.material_index=i
ob=bpy.data.objects.new('S01 grouped rounded tree foliage',me);ext.objects.link(ob)
s=bpy.context.scene;s.name='FACILITY_SPAWN_CONCEPT02_R12';dest=R/'blender/facility_spawn_concept02_R12.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R11.json').read_text());b.update(revision='R12',file=str(dest),repairs_R12=['Removed camouflage bands from rock pigment','Rounded broad clustered tree leaves']);(O/'BUILD_R12.json').write_text(json.dumps(b,indent=2));print('R12_SAVED',flush=True)
