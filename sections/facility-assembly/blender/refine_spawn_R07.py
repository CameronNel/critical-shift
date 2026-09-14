"""R06 -> R07: warm material grouping, restrained fill and broad-leaf beds."""
import bpy,bmesh,json,random,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R06.blend'),load_ui=False)
s=bpy.context.scene;ext=bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'];random.seed(907)
for ob in s.objects:
 if ob.type=='LIGHT' and not ob.library and 'sky fill' in ob.name:
  ob.data.energy*=.36;ob.data.color=(1,.96,.87)
print('LOCAL_SUNS',[(o.name,o.data.energy) for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN' and not o.library],flush=True)
bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.40,.55,.76,1);bg.inputs['Strength'].default_value=.6
for mat in bpy.data.materials:
 if not mat.name.startswith('S01 ') or not mat.use_nodes:continue
 for node in mat.node_tree.nodes:
  if node.type=='VALTORGB':
   for element in node.color_ramp.elements:
    c=element.color;factor=.92 if element.position<.5 else 1.015;element.color=(min(c[0]*factor*1.035,1),c[1]*factor,c[2]*factor*.94,c[3])
# Remove retained needle foliage only in the approved courtyard region.
for ob in bpy.data.collections['26_FINE_PLANTING'].objects:
 if ob.type!='MESH':continue
 ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(-38<(ob.matrix_world@v.co).x<-7 and 13<(ob.matrix_world@v.co).y<33 for v in f.verts)],context='FACES');bm.to_mesh(ob.data);bm.free()
V=[];F=[];I=[]
def plant(x,y,z,sx,sy):
 for j in range(9):
  a=random.random()*math.tau;h=random.uniform(.20,.42);dx=math.cos(a)*min(.16,sx*.28);dy=math.sin(a)*min(.16,sy*.28);side=Vector((-math.sin(a),math.cos(a),0));k=len(V);width=min(.045,sy*.12,sx*.12)
  for q in range(5):
   t=q/4;p=Vector((x+dx*t*t,y+dy*t*t,z+h*t));w=width*math.sin(math.pi*t)*side;V.extend([p-w,p+w])
  for q in range(4):F.append((k+q*2,k+q*2+1,k+q*2+3,k+q*2+2));I.append(random.randrange(3))
b=json.loads((O/'BUILD_R06.json').read_text())
for x,y,sx,sy in b['planted_beds']:
 for j in range(max(3,int(max(sx,sy)/.20))):
  t=random.uniform(-.43,.43);plant(x+t*max(0,sx-.20),y+t*max(0,sy-.20),.22,sx,sy)
for x,y in [(-32,18),(-22,17),(-8.6,22.5),(-33,30.8)]:
 for j in range(23):plant(x+random.uniform(-.66,.66),y+random.uniform(-.24,.24),.70,.4,.4)
me=bpy.data.meshes.new('S01 broad curved border leaves');me.from_pydata(V,[],F)
for i in range(3):me.materials.append(bpy.data.materials['S01 leaf mass '+str(i)])
for p,i in zip(me.polygons,I):p.material_index=i
ob=bpy.data.objects.new('S01 broad border planting',me);ext.objects.link(ob)
# Visible local conduit identification sleeves, no facility-loop claim.
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
orange=bpy.data.materials['S01 burnt orange identification']
for y in [2.25,4.2,6.0]:rod('East service identification sleeve',(-19.34,y-.075,.65),(-19.34,y+.075,.65),.061,orange)
# Keep panelisation while giving the courtyard paving readable smaller aggregate variation.
m=bpy.data.materials['S01 courtyard limestone concrete'];nodes=m.node_tree.nodes;p=nodes.get('Principled BSDF')
for node in nodes:
 if node.type=='VALTORGB':
  node.color_ramp.elements[0].color=(.29,.245,.175,1);node.color_ramp.elements[1].color=(.43,.37,.27,1)
 if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=5.5;node.inputs['Detail'].default_value=1
s.name='FACILITY_SPAWN_CONCEPT02_R07';dest=R/'blender/facility_spawn_concept02_R07.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b.update(revision='R07',file=str(dest),repairs_R07=['Reduced cool fill','Broader planting in retained beds','Removed old needle foliage only inside courtyard','Clear local conduit identification','Warmer paving variation']);(O/'BUILD_R07.json').write_text(json.dumps(b,indent=2));print('R07_SAVED',flush=True)
