"""Exterior lighting layer with original interior lights retained separately."""
import bpy,json,math,random,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R02.blend'),load_ui=False)
s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
room_names={o.name for o in bpy.data.collections['01_LINKED_ROOMS'].objects}
lights=[(i.object.original,i.matrix_world.copy()) for i in dg.object_instances if i.object.type=='LIGHT' and i.parent and i.parent.name in room_names and i.show_self]
col=bpy.data.collections.new('30_RETAINED_INTERIOR_LIGHTING');s.collection.children.link(col)
for original,matrix in lights:
 cp=original.copy();cp.name='INTERIOR_'+original.name;col.objects.link(cp);cp.matrix_world=matrix
col.hide_viewport=True;col.hide_render=True
memo={}
def without_lights(c):
 if c.as_pointer() in memo:return memo[c.as_pointer()]
 cc=bpy.data.collections.new('EXT_LIGHTING_'+c.name);memo[c.as_pointer()]=cc
 for o in c.objects:
  if o.type!='LIGHT':cc.objects.link(o)
 for ch in c.children:cc.children.link(without_lights(ch))
 return cc
for inst in bpy.data.collections['01_LINKED_ROOMS'].objects:
 if inst.instance_collection:inst.instance_collection=without_lights(inst.instance_collection)
sun=next(o for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN' and not o.library)
sun.rotation_euler=(.65,.35,2.4);sun.data.energy=3.0;sun.data.color=(1,.93,.81);sun.data.angle=.055
# A quiet blue physical sky without photographic/noisy background textures.
w=s.world.copy();w.name='S01 exterior daylight';s.world=w
sky=next(n for n in w.node_tree.nodes if n.type=='TEX_SKY');sky.sky_type='HOSEK_WILKIE';sky.sun_direction=sun.rotation_euler.to_matrix()@Vector((0,0,1));sky.turbidity=2.5;sky.ground_albedo=.3
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Strength'].default_value=.35
# Fill light provides modest daylight in shaded facades, rather than room bounce emitters leaking outside.
ld=bpy.data.lights.new('S01 broad exterior skylight','AREA');ld.energy=18000;ld.shape='DISK';ld.size=42;ld.color=(.87,.91,1)
ob=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(ob);ob.location=(-28,15,27)
# Non-traversable background terrain is outside every playable section/reservation.
terrain=bpy.data.collections.new('31_DISTANT_EXTERIOR_BACKDROP');s.collection.children.link(terrain);random.seed(3102)
materials=[]
for idx,c in enumerate([(.18,.24,.25),(.22,.29,.29),(.29,.35,.33),(.26,.30,.25)]):
 m=bpy.data.materials.new('S01 distant terrain '+str(idx));m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=1;materials.append(m)
N=96;verts=[];faces=[]
for ring,radius in enumerate([142,195,270]):
 for i in range(N):
  a=i*math.tau/N;height=-2 if ring==0 else 16+ring*7+9*math.sin(a*5+.4)+7*math.cos(a*9)+random.uniform(-3,3)
  verts.append((-14+radius*math.cos(a),10+radius*math.sin(a),height))
for ring in range(2):
 for i in range(N):
  a=ring*N+i;b=ring*N+(i+1)%N;c=(ring+1)*N+i;d=(ring+1)*N+(i+1)%N;faces.extend([(a,b,c),(b,d,c)])
me=bpy.data.meshes.new('Distant landscape planes');me.from_pydata(verts,[],faces)
for m in materials:me.materials.append(m)
for p in me.polygons:p.material_index=random.randrange(len(materials))
ob=bpy.data.objects.new('Non-walkable distant landscape',me);terrain.objects.link(ob);ob['collision']='NONE_BACKGROUND_ONLY';ob['minimum_radius_from_map_center_m']=142
s['lighting_mode']='EXTERIOR_REVIEW';s['interior_lighting_note']='Original interior lights retained in collection30; enable for interior review. No source light datablocks edited.'
s.name='FACILITY_SPAWN_CONCEPT02_R03';dest=R/'blender/facility_spawn_concept02_R03.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
build=json.loads((O/'BUILD_R02.json').read_text());build.update(revision='R03',file=str(dest),retained_interior_lights=len(lights),lighting_mode='EXTERIOR_REVIEW',background_min_radius_m=142)
(O/'BUILD_R03.json').write_text(json.dumps(build,indent=2));print('LIGHTING_R03_SAVED',len(lights),flush=True)
