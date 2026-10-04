"""Replay Waste Storage's owner-directed neglected finish from the untouched module."""
import bpy,sys,json,hashlib,math,random,re
from pathlib import Path
from mathutils import Vector
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'scenery/WASTE_OVERHAUL.md').is_file());REPO=ROOT.parents[4]
args=sys.argv[sys.argv.index('--')+1:];REV=args[0];SLICE=REV.startswith('slice');COLD='coldstart' in args
if not re.fullmatch(r'(?:R\d+[a-z]?|slice\d+[a-z]?)',REV):
 raise ValueError('Revision must be a basename such as R46 or slice16; paths are forbidden')
if args[1:] not in ([],['coldstart']):
 raise ValueError('Only the optional coldstart argument is supported')
if not COLD and ((ROOT/'production/checkpoints'/(REV+'.blend')).exists() or (ROOT/'blender/history'/(REV+'_build.py')).exists()):
 raise FileExistsError('Revision already archived; choose an unused revision or replay with coldstart')
planned_dir=ROOT/'production/coldstart'/REV if COLD else ROOT/'production/checkpoints'
planned_outputs=[planned_dir/(REV+'.blend'),planned_dir/(REV+'_build.json'),ROOT/'blender/history'/(REV+'_build.py'),ROOT/'blender/history'/(REV+'_full_room.py')]
if not COLD:planned_outputs.append(ROOT.parent/('module_overhaul_slice_R0.blend' if SLICE else 'module_overhaul_R1.blend'))
for destination in planned_outputs:
 if destination.is_symlink() or destination.resolve()==(ROOT.parent/'module.blend').resolve():
  raise ValueError('Output must not be a symlink or resolve to the immutable source')
BUILDER_BYTES=Path(__file__).read_bytes()
source=ROOT.parent/'module.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==source.resolve()
assert source_hash=='8912b5c3b3d2525abb64e838d1fe83a1ea90aa12fea0c9b5a730d4449caecedf'
s=bpy.context.scene;random.seed(613)
original_names=set(bpy.data.objects.keys());original_mats={m.name:m for m in bpy.data.materials}
added=bpy.data.collections.new('WS OVERHAUL | Authored neglect and worker traces');s.collection.children.link(added)
supports=[]
def bsdf(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
def material(name,color,rough=.85,metal=0):
 m=bpy.data.materials.new('WS | '+name);m.diffuse_color=(*color,1);m.use_nodes=True;b=bsdf(m);b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def weather(m,color,rough,metal,scale=1.7,amount=.15):
 b=bsdf(m);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes;links=m.node_tree.links;geom=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65;links.new(geom.outputs['Position'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*(c*(1-amount) for c in color),1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*(c*(1+amount) for c in color),1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],b.inputs['Base Color'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.075;bump.inputs['Distance'].default_value=.0015;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],b.inputs['Normal'])
palette={
 'Warm architectural concrete':((.20,.23,.21),.97,0,1.1,.23),
 'Replacement cast concrete':((.13,.15,.135),.96,0,2.0,.18),
 'Replacement concrete':((.17,.185,.17),.95,0,2.0,.16),
 'Ceiling dust grey':((.075,.089,.081),.96,0,1.4,.19),
 'Dry graphite traffic floor':((.075,.084,.074),.93,0,1.6,.14),
 'Ivory industrial enamel':((.22,.265,.225),.79,.08,4.0,.15),
 'Oxide painted steel':((.15,.092,.055),.84,.18,4.0,.22),
 'Ochre safety enamel':((.30,.26,.11),.83,.04,5.0,.20),
 'Standby ochre enamel':((.155,.115,.067),.88,.08,5.0,.20),
 'Brushed galvanized steel':((.19,.205,.185),.59,.74,6.0,.15),
 'Exposed steel at contact wear':((.20,.215,.19),.67,.64,5.0,.15),
 'Galvanized bus casing':((.115,.15,.132),.77,.37,3.0,.16),
 'Structural warm graphite':((.033,.049,.041),.85,.15,4.0,.13),
 'Used bench plywood':((.063,.043,.021),.94,0,7.0,.24),
 'Cotton electrician rag':((.052,.064,.050),.99,0,8.0,.18),
 'Work order paper':((.23,.21,.15),.99,0,9.0,.12),
 'Isolator vermilion':((.18,.055,.035),.78,.08,4.0,.15),
 'Exposed ochre primer':((.17,.115,.055),.95,.05,4.0,.18),
}
for name,parameters in palette.items():weather(original_mats[name],*parameters)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
rust=material('Dry corrosion',(.115,.055,.024),.96,.12);flaked=material('Missing paint charcoal',(.029,.037,.028),.92,.3);water=material('Old damp residue',(.034,.057,.038),.93);edge=material('Worn folded-steel edges',(.19,.20,.16),.67,.52);chalk=material('Worn service paint',(.30,.30,.21),.98);ply=material('Unvarnished exposed plywood',(.10,.075,.040),.97);ink=material('Faded paper ink',(.06,.07,.047),.99);rubber=material('Worn PPE rubber',(.035,.044,.037),.96);ceramic=material('Chipped mug glaze',(.14,.155,.12),.65);coffee=material('Dried coffee',(.018,.012,.006),.86);paper=original_mats['Work order paper'];steel=original_mats['Brushed galvanized steel'];wood=original_mats['Used bench plywood'];cloth=original_mats['Cotton electrician rag']
def finish(o,mat):
 o.data.materials.clear();o.data.materials.append(mat)
 for c in list(o.users_collection):c.objects.unlink(o)
 added.objects.link(o);o['overhaul_added']=True;return o
def cube(name,pos,size,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name='WS | '+name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Construction edge finish','BEVEL');b.width=bevel;b.segments=2
  o.modifiers.new('Face-weighted corner normals','WEIGHTED_NORMAL')
 return finish(o,mat)
def cyl(name,pos,radius,depth,mat,vertices=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=pos);o=bpy.context.object;o.name='WS | '+name;finish(o,mat);b=o.modifiers.new('Machined lip','BEVEL');b.width=.0015;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def mesh(name,vertices,faces,mat):
 data=bpy.data.meshes.new('WS | '+name);data.from_pydata(vertices,[],faces);data.update();o=bpy.data.objects.new('WS | '+name,data);added.objects.link(o);o.data.materials.append(mat);o['overhaul_added']=True;return o
def support(o,target,anchor,direction=(0,0,-1),gap=.005,penetration=.002):
 o['support_target']=target;o['support_anchor_world']=list(anchor);o['support_direction_world']=list(direction);supports.append(dict(object=o.name,target=target,anchor=list(anchor),direction=list(direction),max_gap=gap,max_penetration=penetration))
def text(name,body,pos,size,mat,rotation=(0,0,0)):
 bpy.ops.object.text_add(location=pos,rotation=rotation);o=bpy.context.object;o.name='WS | '+name;o.data.body=body;o.data.size=size;o.data.extrude=.00008;o.data.align_x='CENTER';finish(o,mat);return o
# All nineteen pre-existing sources are paired with their real lens; five circuits fail.
lenses=[o for o in s.objects if o.type=='MESH' and any(m and m.name=='Warm prismatic diffuser' for m in o.data.materials)]
failed={'Practical pool.008','Practical pool.007','Dispatch practical wall cone.001'}
fixture_pairs=[]
for light in sorted((o for o in s.objects if o.type=='LIGHT'),key=lambda o:o.name):
 lens=min(lenses,key=lambda o:(o.matrix_world.translation-light.matrix_world.translation).length)
 distance=(lens.matrix_world.translation-light.matrix_world.translation).length;assert distance<.16,(light.name,lens.name,distance)
 lensmat=original_mats['Warm prismatic diffuser'].copy();lensmat.name='WS | Lens '+light.name;b=bsdf(lensmat)
 dead=light.name in failed;light.data.energy=0 if dead else (55 if light.data.type=='AREA' else 85)
 if light.name=='Practical pool.007' and not dead:light.data.energy=55
 if light.name=='Practical pool.004':light.data.energy=190
 if light.name=='Practical pool.002':light.data.energy=70
 if light.name=='Practical pool.006':light.data.energy=95
 if light.name=='Practical pool.009':light.data.energy=45
 if light.name in {'Practical pool.001','Practical pool.003','Practical pool.005'}:light.data.energy={'Practical pool.001':105,'Practical pool.003':125,'Practical pool.005':75}[light.name]
 if light.name in {'Dispatch practical wall cone.002','Directed practical wash.005'}:light.data.energy=45
 light.data.color=(.76,.87,.83) if light.data.type=='AREA' else (.86,.84,.70)
 b.inputs['Base Color'].default_value=(.035,.047,.037,1) if dead else (.45,.58,.51,1);b.inputs['Emission Color'].default_value=(*light.data.color,1);b.inputs['Emission Strength'].default_value=0 if dead else (.55 if light.data.energy<=60 else .95 if light.data.energy<=110 else 1.2)
 lens.data=lens.data.copy();lens.data.materials.clear();lens.data.materials.append(lensmat);light['physical_lens']=lens.name;light['failed_fixture']=dead;lens['light_source']=light.name
 fixture_pairs.append(dict(source=light.name,lens=lens.name,offset=distance,energy=light.data.energy,emission=b.inputs['Emission Strength'].default_value,failed=dead))
assert len({p['lens'] for p in fixture_pairs})==len(fixture_pairs)==19
# Sharp, worn repair corner is the validation slice. The wider room retains original geometry.
for o in s.objects:
 if o.type=='MESH':
  for modifier in o.modifiers:
   if modifier.type=='BEVEL':modifier.width=min(modifier.width,.007)
# Missing tool leaves an interrupted rather than showroom-perfect rack.
for name in ['Ring wrench end.002','Wrench shank.002']:
 if name in bpy.data.objects:bpy.data.objects[name].hide_render=True
# Damp follows the repair wall's lower seam and one overhead service leak.
for i,(x,z,width,length) in enumerate([(3.45,1.10,.58,.73),(5.30,1.35,.52,1.08),(5.52,3.98,.18,1.65)]):
 pts=[(-.50,0),(-.35,.035),(-.16,-.08),(0,.02),(.28,-.12),(.50,-.09),(.39,-.56),(.22,-.64),(.13,-1),(-.07,-.87),(-.28,-.69),(-.43,-.74)]
 verts=[(x+u*width,17.999,z+v*length) for u,v in pts];o=mesh('Repair corner damp run '+str(i),verts,[tuple(range(len(verts)))],water);support(o,'Dispatch wall.001',(x,17.999,z-length*.5),(0,1,0))
# Real interrupted-use cluster on the inherited worktop (top = 0.9575).
worktop=bpy.data.objects['Thick plywood worktop'];top=max((worktop.matrix_world@Vector(v)).z for v in worktop.bound_box)
# A thin folded glove with a palm and five tapered fingers, seated directly on the wood.
for hand in range(2):
 center=Vector((5.23+hand*.095,16.48+hand*.055,top+.003));angle=.23-hand*.45
 outline=[(-.038,-.075),(.039,-.075),(.042,-.005),(.079,.026),(.077,.048),(.051,.044),(.044,.035),(.040,.096),(.025,.104),(.017,.047),(.013,.122),(-.003,.125),(-.010,.05),(-.019,.108),(-.034,.105),(-.031,.036),(-.042,.071),(-.054,.064),(-.046,.009)]
 verts=[]
 for z in (-.003,.007):
  for x,y in outline:verts.append((center.x+x*math.cos(angle)-y*math.sin(angle),center.y+x*math.sin(angle)+y*math.cos(angle),center.z+(z if z<0 else (.007+.009*max(0,1-abs(y)/.13)+.003*math.sin(x*65+y*25)))))
 count=len(outline);faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
 o=mesh('Slumped glove '+str(hand),verts,faces,rubber);be=o.modifiers.new('Fabric-soft finger edges','BEVEL');be.width=.002;be.segments=2;support(o,worktop.name,(center.x,center.y,top))
# A chipped cup with an actual open cavity and handle, distinct from a solid cylinder.
x,y=4.55,16.47
verts=[];N=32
for ring,(radius,z) in enumerate([(.037,top),(.043,top+.083),(.034,top+.083),(.030,top+.010)]):
 for i in range(N):
  a=2*math.pi*i/N;zz=z-(.009 if ring in (1,2) and i in (18,19) else 0);verts.append((x+radius*math.cos(a),y+radius*math.sin(a),zz))
faces=[]
for j in range(3):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.append(tuple(range(3*N,4*N)));faces.append(tuple(reversed(range(N))));o=mesh('Cold abandoned cup',verts,faces,ceramic);support(o,worktop.name,(x,y,top))
bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=(x-.049,y,top+.047),major_radius=.027,minor_radius=.006,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='WS | Cup handle';finish(o,ceramic);o.parent=bpy.data.objects['WS | Cold abandoned cup'];o.matrix_parent_inverse=o.parent.matrix_world.inverted()
o=cyl('Cold coffee residue',(x,y,top+.0105),.030,.001,coffee);o.parent=bpy.data.objects['WS | Cold abandoned cup'];o.matrix_parent_inverse=o.parent.matrix_world.inverted();o['intrinsic_attachment']='Settled contents on cavity bottom'
# Stained work slip, physically on the worktop, with compact rather than decorative text.
o=cube('Overdue seal work slip',(4.75,16.47,top+.0005),(.20,.13,.001),paper);support(o,worktop.name,(4.75,16.47,top))
o=text('Work slip printing','FILTER 06\nOVERDUE',(4.75,16.455,top+.0011),.020,ink);o.parent=bpy.data.objects['WS | Overdue seal work slip'];o.matrix_parent_inverse=o.parent.matrix_world.inverted();o['intrinsic_attachment']='Ink printed on work slip'
# Scarred wood and vice damage are localized at the actual working/contact surfaces.
for i in range(9):
 x0=3.98+i*.145;length=.08+random.random()*.17;o=cube('Bench vise scratch '+str(i),(x0,16.49+random.random()*.35,top+.0002),(length,.002,.0004),ply);support(o,worktop.name,(x0,o.location.y,top))
# Cast vice side ribs and a replaceable jaw face establish secondary shape at the existing vice.
for i in range(3):
 o=cube('Cast vice reinforcing rib '+str(i),(4.025+i*.068,16.72,1.0575),(.018,.045,.12),original_mats['Oxide painted steel'],.0015);support(o,'Vice cast base',(o.location.x,16.72,.9975))
# Author primary and secondary silhouettes instead of preserving the plain slabs.
def remesh(name,verts,faces,mat):
 o=bpy.data.objects[name];data=bpy.data.meshes.new('WS authored | '+name);inv=o.matrix_world.inverted();data.from_pydata([inv@Vector(v) for v in verts],[],faces);data.update();o.data=data;o.data.materials.append(mat);o['overhaul_modified']=True;return o
# Seat every legacy emitter at its real outward lens face and match its aperture.
for light in [o for o in s.objects if o.type=='LIGHT']:
 lens=s.objects[light['physical_lens']]
 if light.name.startswith('Practical pool'):
  light.location=lens.matrix_world.translation+Vector((0,0,-.0145));light.rotation_euler=(0,0,0);light.data.shape='RECTANGLE';light.data.size=1.28;light.data.size_y=.17
 elif light.name.startswith('Directed practical wash'):
  centre=Vector(((-1 if light.location.x<0 else 1)*5.885,lens.matrix_world.translation.y,3.463));dims=(.12,.27,.006);v=[centre+Vector((dx*dims[0]/2,dy*dims[1]/2,dz*dims[2]/2)) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];mat=lens.data.materials[0];remesh(lens.name,v,f,mat);light.location=centre+Vector(((.037 if centre.x<0 else -.037),0,-.005));light.rotation_euler=(0,0,0);light.data.shadow_soft_size=.016
 else:
  light.location=lens.matrix_world.translation+Vector((0,0,-.0095));light.rotation_euler=(0,0,0);light.data.shadow_soft_size=.035
bpy.context.view_layer.update()
# Plywood laminate has a broken front corner, narrow edge seams and a worn working edge.
outline=[(3.70,16.37),(3.88,16.37),(3.91,16.395),(3.945,16.385),(3.975,16.37),(5.27,16.37),(5.40,16.425),(5.40,17.13),(3.70,17.13)]
verts=[(x,y,z) for z in (top-.075,top) for x,y in outline];n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
remesh(worktop.name,verts,faces,wood)
for layer in range(3):
 o=cube('Exposed plywood edge ply '+str(layer),(4.50,16.3697,top-.013-layer*.023),(1.24,.0006,.0014),ply);support(o,worktop.name,(4.50,16.37,top-.013-layer*.023),(0,1,0))
# A bolted folded-steel lip protects the battered front edge of the wooden slab.
o=cube('Workbench worn steel front edge',(4.58,16.3685,top-.032),(1.20,.003,.050),original_mats['Structural warm graphite'],.0004);support(o,worktop.name,(4.58,16.37,top-.032),(0,1,0))
for i in range(5):
 x=4.04+i*.27;o=cyl('Workbench edge captive rivet '+str(i),(x,16.3655,top-.030),.005,.003,edge,8);o.rotation_euler=(math.pi/2,0,0);support(o,'WS | Workbench worn steel front edge',(x,16.367,top-.030),(0,1,0))
# Folded maintenance board: chamfered corners, shallow return, split service panels.
poly=[(3.775,1.00),(5.285,1.00),(5.325,1.04),(5.325,1.68),(5.285,1.72),(3.815,1.72),(3.775,1.68)];n=len(poly);verts=[(x,y,z) for y in (17.0375,17.0435) for x,z in poly];faces=[tuple(range(n)),tuple(reversed(range(n,n*2)))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)];remesh('Tool backboard',verts,faces,original_mats['Galvanized bus casing'])
for label,pos,size in [('upper',(4.55,17.030,1.66),(1.42,.012,.020)),('lower',(4.55,17.030,1.055),(1.42,.012,.020)),('split',(4.55,17.036,1.335),(1.43,.003,.006))]:
 o=cube('Tool board folded '+label+' rail',pos,size,original_mats['Structural warm graphite'],.0005);support(o,'Tool backboard',(pos[0],17.0375,pos[2]),(0,1,0))
# Long grain and nicks are aligned with the wood rather than applied as blanket noise.
b=bsdf(wood);nodes=wood.node_tree.nodes;links=wood.node_tree.links;geom=nodes.new('ShaderNodeNewGeometry');stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(2,95,18);noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2;links.new(geom.outputs['Position'],stretch.inputs[0]);links.new(stretch.outputs['Vector'],noise.inputs['Vector']);ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.044,.028,.013,1);ramp.color_ramp.elements[1].color=(.090,.062,.030,1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],b.inputs['Base Color'])
# Rolled-angle legs with a real return and separate thin flanges.
for name in ['Bench angle leg','Bench angle leg.001','Bench angle leg.002','Bench angle leg.003']:
 old=bpy.data.objects[name];x,y=old.matrix_world.translation.xy;poly=[(-.0325,-.0325),(.0325,-.0325),(.0325,-.0265),(-.0265,-.0265),(-.0265,.0325),(-.0325,.0325)];n=len(poly);verts=[(x+a,y+b,z) for z in (0,.88) for a,b in poly];faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];remesh(name,verts,faces,original_mats['Structural warm graphite'])
# Flatten and taper the forged spanner bodies. Their ring heads still sit on source pegs.
for idx,length in [(0,.37),(1,.31),(3,.255),(4,.205)]:
 suffix='' if idx==0 else '.'+str(idx).zfill(3);name='Wrench shank'+suffix;old=bpy.data.objects[name];x,y=old.matrix_world.translation.xy;zt=1.482;profile=[(-.017,0),(.017,0),(.014,-.10),(.013,-length+.045),(.035,-length+.027),(.034,-length),(.015,-length+.012),(.007,-length+.031),(-.008,-length+.031),(-.017,-length+.012),(-.034,-length),(-.035,-length+.027),(-.013,-length+.045),(-.014,-.10)];n=len(profile);verts=[(x+a,yy,zt+b) for yy in (y-.007,y+.007) for a,b in profile];faces=[tuple(range(n)),tuple(reversed(range(n,n*2)))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)];faces=[tuple(reversed(f)) for f in faces];remesh(name,verts,faces,steel)
# Replace the block rag with a folded, draped woven cloth that hangs over the front lip.
bpy.data.objects['Service cloth'].hide_render=True
verts=[];nx=7;ny=12
for j in range(ny):
 y=16.30+j*.027
 for i in range(nx):
  x=4.33+i*.026;z=top+.001+(.017*math.sin(i*1.8+j*.45)**2 if y>=16.37 else -(16.37-y)*1.0-.015*math.sin(i*1.1)**2);verts.append((x,y,z))
faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)];o=mesh('Greasy rag draped over bench lip',verts,faces,cloth);support(o,worktop.name,min((v for v in verts if v[1]>=16.37),key=lambda v:v[2]));o.modifiers.new('Woven cloth thickness','SOLIDIFY').thickness=.001
# Use-oriented edge scars, smeared seal residue, and peeling pegboard enamel.
for i in range(14):
 x=3.93+i*.097;y=16.385+random.random()*.05;size=.008+random.random()*.025
 o=mesh('Bench worked edge scar '+str(i),[(x-size,y,top+.00015),(x,y-.005,top+.00015),(x+size*.7,y+.002,top+.00015),(x+size*.2,y+.008,top+.00015)],[(0,1,2,3)],ply);support(o,worktop.name,(x,y,top))
for i in range(12):
 x=3.92+random.random()*1.23;z=1.03+random.random()*.59;w=.012+random.random()*.04;h=.009+random.random()*.025
 o=mesh('Pegboard rubbed paint '+str(i),[(x-w,17.0372,z),(x+w,17.0372,z+h*.3),(x+w*.45,17.0372,z+h),(x-w*.2,17.0372,z+h*.7)],[(0,1,2,3)],edge);support(o,'Tool backboard',(x,17.0372,z+h*.4),(0,1,0))
# Correct and register the small inherited bench props as well as the new dressing.
bpy.data.objects['Inventory tag stack'].hide_render=True
seal=bpy.data.objects['Replacement seal'];world=seal.matrix_world.copy();world.translation=Vector((5.0,16.645,top+.018));seal.matrix_world=world;support(seal,worktop.name,(5.14,16.645,top))
# A formed tray with a shallow open cavity replaces the opaque block below the fasteners.
verts=[]
for hx,hy,z in [(.185,.130,top),(.185,.130,top+.025),(.180,.125,top+.025),(.180,.125,top+.003)]:
 verts.extend([(5-hx,16.94-hy,z),(5+hx,16.94-hy,z),(5+hx,16.94+hy,z),(5-hx,16.94+hy,z)])
faces=[]
for j in range(3):
 for i in range(4):faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
faces.extend([tuple(reversed(range(4))),tuple(range(12,16))]);tray=remesh('Fastener tray',verts,faces,original_mats['Galvanized bus casing']);support(tray,worktop.name,(5.17,16.94,top))
for i in range(6):
 name='Spare captive fastener'+('' if i==0 else '.'+str(i).zfill(3));bolt=bpy.data.objects[name];world=bolt.matrix_world.copy();world.translation.z=top+.0205;world.translation.y+=.09;bolt.matrix_world=world;support(bolt,tray.name,(world.translation.x,world.translation.y,top+.003))
# Cast vice jaws taper into their feet; the drive has a visible machined thread.
for name in ['Vice jaw body','Vice jaw body.001']:
 obj=bpy.data.objects[name];cy=obj.matrix_world.translation.y;poly=[(4.06,1.03),(4.24,1.03),(4.275,1.077),(4.275,1.145),(4.27,1.15),(4.03,1.15),(4.025,1.145),(4.025,1.077)];n=len(poly);verts=[(x,y,z) for y in (cy-.0225,cy+.0225) for x,z in poly];faces=[tuple(range(n)),tuple(reversed(range(n,n*2)))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)];remesh(name,verts,faces,original_mats['Oxide painted steel'])
verts=[];steps=1024;cross=8
for i in range(steps):
 a=2*math.pi*i/20;y=16.49+i*.0002
 for j in range(cross):
  b=2*math.pi*j/cross;r=.0193+.0013*math.cos(b);verts.append((4.15+r*math.cos(a),y+.0013*math.sin(b),1.035+r*math.sin(a)))
faces=[]
for i in range(steps-1):
 for j in range(cross):faces.append((i*cross+j,i*cross+(j+1)%cross,(i+1)*cross+(j+1)%cross,(i+1)*cross+j))
faces.extend([tuple(reversed(range(cross))),tuple(range((steps-1)*cross,steps*cross))]);o=mesh('Vice machined drive thread',verts,faces,edge);support(o,'Vice feed screw',(4.168,16.49,1.035),(-1,0,0))
# Clear real drive bores through the cast guide feet rather than burying the shaft in solid casts.
for name in ['Vice jaw body','Vice jaw body.001']:
 obj=bpy.data.objects[name];cy=obj.matrix_world.translation.y;bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.022,depth=.09,location=(4.15,cy,1.035),rotation=(math.pi/2,0,0));cutter=bpy.context.object;modifier=obj.modifiers.new('Drive guide bore through casting','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter;bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True);obj.modifiers.new('Cast bore corner normals','WEIGHTED_NORMAL')
# Bite marks are restricted to the replaceable jaw plates.
for name in ['Vice replaceable jaw','Vice replaceable jaw.001']:
 obj=bpy.data.objects[name];cy=obj.matrix_world.translation.y;facey=cy-.0052
 for i in range(10):
  x=4.048+i*.021;verts=[(x,facey,1.085),(x+.0014,facey,1.085),(x+.0214,facey,1.138),(x+.020,facey,1.138)];o=mesh(name+' hardened gripping score '+str(i),verts,[(0,1,2,3)],flaked);support(o,name,(x+.0107,facey,1.1115),(0,1,0))
# Spare fasteners have bores and shafts, and are loose rather than identical solid hex blocks.
for i in range(6):
 name='Spare captive fastener'+('' if i==0 else '.'+str(i).zfill(3));obj=bpy.data.objects[name];cx=obj.matrix_world.translation.x;cy=obj.matrix_world.translation.y;verts=[];faces=[];N=12
 if i in (0,5):
  angle=math.radians(20 if i==0 else 158);axis=Vector((math.cos(angle),math.sin(angle),0));rot=axis.to_track_quat('Z','Y');local=[]
  for radius,z in [(.0225,0),(.0225,.012),(.009,.012),(.009,.068)]:
   for j in range(N):
    a=2*math.pi*j/N;r=radius*(1 if j%2==0 or radius==.009 else .8660254);local.append(rot@Vector((r*math.cos(a),r*math.sin(a),z)))
  minz=min(v.z for v in local);verts=[(cx+v.x,cy+v.y,top+.003+v.z-minz) for v in local]
  for k in range(3):
   for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
  faces.extend([tuple(reversed(range(N))),tuple(range(3*N,4*N))])
 else:
  angle=i*.17
  for outer,z in [(True,top+.003),(True,top+.019),(False,top+.019),(False,top+.003)]:
   for j in range(N):
    a=2*math.pi*j/N+angle;r=.0225*(1 if j%2==0 else .8660254) if outer else .008;verts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
  for k in range(4):
   for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j))
 remesh(name,verts,faces,steel)
 supports[:]=[r for r in supports if r['object']!=name];support(obj,'Fastener tray',min(verts,key=lambda v:v[2]))
# A visibly failed old gasket stays beside the inherited replacement, with a physical service tag.
verts=[];segments=31;cross=8
for i in range(segments):
 a=2*math.pi*(i+.6)/32;r=.065+.0015*math.sin(i*1.8)
 for j in range(cross):
  b=2*math.pi*j/cross;verts.append((5.275+(r+.004*math.cos(b))*math.cos(a),16.86+(r+.004*math.cos(b))*math.sin(a),top+.004+.004*math.sin(b)))
faces=[]
for i in range(segments-1):
 for j in range(cross):faces.append((i*cross+j,(i+1)*cross+j,(i+1)*cross+(j+1)%cross,i*cross+(j+1)%cross))
faces.extend([tuple(range(cross)),tuple(reversed(range((segments-1)*cross,segments*cross)))]);o=mesh('Brittle removed seal',verts,faces,rubber);support(o,worktop.name,min(verts,key=lambda v:v[2]))
o=cube('Removed seal attached tag',(5.30,16.965,top+.001),(.058,.065,.002),paper);support(o,worktop.name,(5.30,16.965,top))
o=text('Seal rejection mark','REJECT',(5.30,16.958,top+.0021),.009,ink);o.parent=bpy.data.objects['WS | Removed seal attached tag'];o.matrix_parent_inverse=o.parent.matrix_world.inverted();o['intrinsic_attachment']='Printed tag ink'
# A dented folded tray and spent cloth-backed filter occupy the quiet lower service shelf.
shelf=bpy.data.objects['Bench lower shelf'];shelftop=max((shelf.matrix_world@Vector(v)).z for v in shelf.bound_box)
o=cube('Lower shelf folded salvage tray',(4.86,16.76,shelftop+.006),(.51,.38,.012),original_mats['Galvanized bus casing'],.0015);support(o,shelf.name,(4.86,16.76,shelftop))
for side,pos,size in [('front',(4.86,16.574,shelftop+.045),(.51,.008,.066)),('back',(4.86,16.946,shelftop+.045),(.51,.008,.066)),('left',(4.609,16.76,shelftop+.045),(.008,.36,.066)),('right',(5.111,16.76,shelftop+.045),(.008,.36,.066))]:
 o=cube('Salvage tray '+side+' return',pos,size,original_mats['Galvanized bus casing']);support(o,'WS | Lower shelf folded salvage tray',(pos[0],pos[1],shelftop+.012));
for i in range(8):
 o=cube('Dust loaded spare filter pleat '+str(i),(4.77+i*.023,16.78,shelftop+.022),(.011,.22,.020),cloth,.001);support(o,'WS | Lower shelf folded salvage tray',(o.location.x,16.78,shelftop+.012))
# A supported articulated bench lamp puts the practical source in the slice itself.
bracket=cube('Bench task lamp bolted bracket',(5.25,17.0295,1.675),(.08,.016,.10),original_mats['Structural warm graphite'],.0015);support(bracket,'Tool backboard',(5.25,17.0375,1.675),(0,1,0))
def intrinsic(o,root,reason):
 bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=world;o['intrinsic_attachment']=reason;return o
points=[Vector((5.25,17.018,1.675)),Vector((5.25,16.925,1.98)),Vector((4.92,16.66,1.98)),Vector((4.84,16.60,1.82))]
for i in range(3):
 a,b=points[i:i+2];o=cyl('Bench lamp articulated arm '+str(i),(a+b)/2,.009,(b-a).length,original_mats['Structural warm graphite'],12);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();intrinsic(o,bracket,'Fastened arm and pivot joints')
for i,pivot in enumerate(points[:-1]):
 o=cyl('Lamp hex pivot '+str(i),pivot,.019,.025,edge,6);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,bracket,'Articulation bolt joins arm ends')
centre=points[-1];axis=Vector((-.30,-.16,-.94)).normalized();rot=axis.to_track_quat('-Z','Y');verts=[];N=12
for radius,z in [(.042,.055),(.087,-.055),(.079,-.055),(.034,.048)]:
 for i in range(N):
  a=2*math.pi*i/N;verts.append(centre+rot@Vector((radius*math.cos(a),radius*math.sin(a),z)))
faces=[]
for j in range(3):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.append(tuple(range(3*N,4*N)));faces.append(tuple(reversed(range(N))));faces=[tuple(reversed(f)) for f in faces];shade=mesh('Pressed steel task lamp shade',verts,faces,original_mats['Galvanized bus casing']);intrinsic(shade,bracket,'Shade threaded to last arm end')
lenspos=centre+rot@Vector((0,0,-.055));lensmat=material('Bench lamp frosted lens',(.48,.48,.33),.55);b=bsdf(lensmat);b.inputs['Emission Color'].default_value=(.84,.78,.58,1);b.inputs['Emission Strength'].default_value=.4
lens=cyl('Bench task lamp real lens',lenspos,.076,.002,lensmat,24);lens.rotation_euler=rot.to_euler();intrinsic(lens,bracket,'Diffuser seated in shade mouth')
data=bpy.data.lights.new('WS | Bench task lamp emitter','AREA');data.energy=26;data.shape='DISK';data.size=.08;data.color=(.84,.78,.58);light=bpy.data.objects.new('WS | Bench task lamp emitter',data);added.objects.link(light);light.location=centre+rot@Vector((0,0,-.057));light.rotation_euler=rot.to_euler();intrinsic(light,bracket,'Emitter directly below physical lens');light['physical_lens']=lens.name;light['failed_fixture']=False;lens['light_source']=light.name
fixture_pairs.append(dict(source=light.name,lens=lens.name,offset=.002,energy=data.energy,emission=.4,failed=False))
# The visible east-wall panel carries a localized old service leak and cracked repairs.
for i,(y,z,w,h,mat) in enumerate([(16.55,3.58,.42,1.65,water),(16.73,2.55,.75,.54,original_mats['Replacement cast concrete']),(15.82,.78,.64,.58,water)]):
 pts=[(-.5,0),(-.25,.045),(-.08,-.02),(.24,.03),(.5,-.10),(.43,-.32),(.19,-.5),(.26,-.79),(.07,-1),(-.14,-.75),(-.4,-.66),(-.32,-.27)];verts=[(5.9995,y+u*w,z+v*h) for u,v in pts];o=mesh('Repair wall damaged patch '+str(i),verts,[tuple(reversed(range(len(verts))))],mat);support(o,'East Wall.001',(5.9995,y,z-h*.5),(1,0,0))
# Narrow branched fissures connect the patched plaster, with restrained chalky exposed edges.
for i,(y,z,dy,dz) in enumerate([(16.58,2.02,.20,-.22),(16.78,1.80,-.09,-.20),(16.69,1.60,.13,-.17),(16.77,1.78,.19,-.08)]):
 verts=[(5.9992,y-.002,z),(5.9992,y+.002,z),(5.9992,y+dy+.003,z+dz),(5.9992,y+dy-.003,z+dz)];o=mesh('Repair wall hairline fracture '+str(i),verts,[(0,1,2,3)],flaked);support(o,'East Wall.001',(5.9992,y+dy*.5,z+dz*.5),(1,0,0))
# Oxidation and exposed cast edges stay at vise-jaw contacts, not spread evenly over the scene.
for i,(x,z,w,h,mat) in enumerate([(4.052,1.076,.025,.036,rust),(4.225,1.110,.03,.031,rust),(4.12,1.044,.055,.011,edge)]):
 verts=[(x-w,16.6472,z),(x+w,16.6472,z+.002),(x+w*.62,16.6472,z+h),(x-w*.55,16.6472,z+h*.73)];o=mesh('Cast vise contact wear '+str(i),verts,[(0,1,2,3)],mat);support(o,'Vice jaw body.001',(x,16.6472,z+h*.4),(0,1,0))
# Close view supplements, rather than replaces, the twenty protected original cameras.
data=bpy.data.cameras.new('D01_SealRepair');data.lens=40;cam=bpy.data.objects.new('D01_SealRepair',data);s.collection.objects.link(cam);cam.location=(4.30,15.85,1.68);cam.rotation_euler=(Vector((4.85,16.65,.96))-cam.location).to_track_quat('-Z','Y').to_euler()
# A suspended drawer carcass is bolted to the source apron; it has folded sheet returns.
cabmat=material('Battered maintenance cabinet enamel',(.105,.125,.107),.87,.12);weather(cabmat,(.105,.125,.107),.87,.12,5,.15)
cap=cube('Bolted under-bench drawer carcass cap',(4.15,16.7075,.7825),(.61,.545,.005),cabmat,.001);support(cap,'Workbench longitudinal apron',(4.15,16.46,.785),(0,0,1))
for label,pos,size in [('left side',(3.847,16.7075,.6125),(.004,.545,.335)),('right side',(4.453,16.7075,.6125),(.004,.545,.335)),('back return',(4.15,16.978,.6125),(.61,.004,.335)),('lower folded shelf',(4.15,16.7075,.4475),(.61,.545,.005)),('left face stile',(3.865,16.438,.6125),(.04,.008,.33)),('right face stile',(4.435,16.438,.6125),(.04,.008,.33))]:
 o=cube('Drawer cabinet '+label,pos,size,cabmat,.0007);intrinsic(o,cap,'Welded folded carcass')
for idx,z in enumerate([.529,.695]):
 fronty=16.437 if idx==0 else 16.418
 front=cube('Maintenance drawer '+str(idx)+' front',(4.15,fronty,z),(.52,.009,.137),cabmat,.0015);intrinsic(front,cap,'Captive drawer runners retain the open drawer')
 for side,x in [('left',3.97),('right',4.33)]:
  o=cube('Drawer '+str(idx)+' '+side+' handle boss',(x,fronty-.018,z),(.022,.028,.028),original_mats['Structural warm graphite'],.002);intrinsic(o,cap,'Handle mounts fastened to drawer face')
 o=cyl('Drawer '+str(idx)+' worn bail grip',(4.15,fronty-.031,z),.007,.35,edge,12);o.rotation_euler=(0,math.pi/2,0);intrinsic(o,cap,'Bail handle fixed in two bosses')
 for j in range(5):
  x=3.916+j*.104;zz=z-.061+(.005 if j%2 else 0);verts=[(x-.012,fronty-.0047,zz),(x+.022,fronty-.0047,zz+.003),(x+.014,fronty-.0047,zz+.011),(x-.007,fronty-.0047,zz+.014)];o=mesh('Drawer '+str(idx)+' rubbed lower lip '+str(j),verts,[(0,1,2,3)],rust if j%2 else edge);intrinsic(o,cap,'Surface paint loss at drawer handling edge')
# Through-slots are actual negative geometry in the folded side panel.
panel=bpy.data.objects['WS | Drawer cabinet left side']
for i in range(3):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(3.847,16.715,.555+i*.055));cutter=bpy.context.object;cutter.dimensions=(.025,.29,.010);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);modifier=panel.modifiers.new('Actual service aperture '+str(i),'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter;bpy.context.view_layer.objects.active=panel;bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
# The note has a damaged corner and one folded edge, rather than clean office-paper framing.
obj=bpy.data.objects['WS | Overdue seal work slip'];outline=[(4.65,16.405,0),(4.84,16.405,0),(4.85,16.417,.002),(4.844,16.437,.005),(4.85,16.48,0),(4.845,16.535,0),(4.65,16.535,0)];n=len(outline);verts=[(x,y,top+dz+thick) for thick in (0,.001) for x,y,dz in outline];faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];remesh(obj.name,verts,faces,paper)
# Replace the cutout-like wall damage by pigment integrated into the actual wall shader.
for obj in list(added.objects):
 if obj.name.startswith(('WS | Repair corner damp','WS | Repair wall damaged patch','WS | Repair wall hairline fracture')):supports[:]=[r for r in supports if r['object']!=obj.name];bpy.data.objects.remove(obj,do_unlink=True)
wall=bpy.data.objects['East Wall.001'];wallmat=wall.data.materials[0].copy();wallmat.name='WS | Repair corner concrete with old damp';wall.data.materials[0]=wallmat;nodes=wallmat.node_tree.nodes;links=wallmat.node_tree.links;b=bsdf(wallmat);base=b.inputs['Base Color'].links[0].from_socket
for y,z,sy,sz,strength in [(16.55,2.60,2.6,1.1,.65),(16.68,2.08,20,1.8,.72),(16.55,1.70,25,1.5,.60),(16.33,.50,1.5,3,.65)]:
 geom=nodes.new('ShaderNodeNewGeometry');sub=nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(6,y,z);scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1,sy,sz);length=nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';fade=nodes.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.15;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=strength;fade.inputs['To Max'].default_value=0;fade.clamp=True;mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.33,.46,.32,1);links.new(geom.outputs['Position'],sub.inputs[0]);links.new(sub.outputs['Vector'],scale.inputs[0]);links.new(scale.outputs['Vector'],length.inputs[0]);links.new(length.outputs['Value'],fade.inputs['Value']);links.new(fade.outputs['Result'],mix.inputs[0]);links.new(base,mix.inputs[1]);base=mix.outputs[0]
links.new(base,b.inputs['Base Color'])
# Old oil is concentrated at the vice and seal work, with softened stain boundaries.
oil=material('Vice oil soaked into wood',(.020,.020,.009),.94)
verts=[(3.97,16.54,top+.00012),(4.06,16.49,top+.00012),(4.20,16.51,top+.00012),(4.30,16.59,top+.00012),(4.29,16.78,top+.00012),(4.16,16.88,top+.00012),(4.00,16.78,top+.00012)];o=mesh('Vice accumulated oily use stain',verts,[tuple(range(len(verts)))],oil);support(o,worktop.name,(4.13,16.64,top))
# Old seal impressions and coffee rings give the working area a specific contact history.
for label,x,y,radius,width in [('Old gasket oil impression',4.95,16.71,.140,.017),('Old cup coffee ring',4.62,16.58,.042,.009)]:
 verts=[];N=64
 for ring,r in enumerate([radius-width/2,radius,radius+width/2]):
  for i in range(N):
   a=2*math.pi*i/N;rr=r+.0015*math.sin(i*2.3);verts.append((x+rr*math.cos(a),y+rr*math.sin(a),top+.00015))
 faces=[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(2) for i in range(N)];obj=mesh(label,verts,faces,oil);attr=obj.data.attributes.new('WS_Damp_Mask','FLOAT','POINT')
 for i,v in enumerate(attr.data):v.value=(.20+.14*math.sin(i*.75)) if N<=i<2*N else 0
 support(obj,worktop.name,verts[0])
# Oxidation and paint loss track the tool mounts, with rough rusty response instead of chrome paint.
board=bpy.data.objects['Tool backboard'];m=board.data.materials[0].copy();m.name='WS | Tool board worn around mounts';board.data.materials[0]=m;nodes=m.node_tree.nodes;links=m.node_tree.links;b=bsdf(m);base=b.inputs['Base Color'].links[0].from_socket
for x,z,sx,sz in [(3.99,1.40,22,5),(4.25,1.37,25,5),(4.77,1.44,24,6),(5.03,1.47,28,8)]:
 geom=nodes.new('ShaderNodeNewGeometry');sub=nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(x,17.0375,z);scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(sx,1,sz);length=nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';fade=nodes.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.15;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=.7;fade.inputs['To Max'].default_value=0;fade.clamp=True;mix=nodes.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.083,.043,.019,1);links.new(geom.outputs['Position'],sub.inputs[0]);links.new(sub.outputs['Vector'],scale.inputs[0]);links.new(scale.outputs['Vector'],length.inputs[0]);links.new(length.outputs['Value'],fade.inputs['Value']);links.new(fade.outputs['Result'],mix.inputs[0]);links.new(base,mix.inputs[1]);base=mix.outputs[0]
links.new(base,b.inputs['Base Color']);b.inputs['Metallic'].default_value=.10;b.inputs['Roughness'].default_value=.91
for obj in list(added.objects):
 if obj.name.startswith('WS | Pegboard rubbed paint'):supports[:]=[r for r in supports if r['object']!=obj.name];bpy.data.objects.remove(obj,do_unlink=True)
# Vertex masks soften the authored footprints; this is localized damage, not global grunge.
def soften_stain(o,mat):
 if o.type!='MESH' or len(o.data.polygons)!=1:return
 old=[v.co.copy() for v in o.data.vertices];centre=sum(old,Vector())/len(old);n=len(old);vertices=old+[centre+(v-centre)*.76 for v in old]+[centre];faces=[]
 for i in range(n):j=(i+1)%n;faces.extend([(i,j,n+j,n+i),(n+i,n+j,2*n)])
 data=bpy.data.meshes.new(o.name+' fading edges');data.from_pydata(vertices,[],faces);data.update();o.data=data;o.data.materials.append(mat);attr=data.attributes.new('WS_Damp_Mask','FLOAT','POINT')
 for i,v in enumerate(attr.data):v.value=0 if i<n else (.60+.15*math.sin(i*1.7) if i<2*n else .80)
for mat in [water,oil]:
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');shader=bsdf(mat);mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent');attribute=nodes.new('ShaderNodeAttribute');attribute.attribute_name='WS_Damp_Mask';links.new(attribute.outputs['Fac'],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(shader.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
 for obj in list(added.objects):
  if obj.type=='MESH' and mat in list(obj.data.materials):soften_stain(obj,mat)
# Full expansion is deliberately blocked until slice reviews pass.
FULL_BYTES=None
if not SLICE:
 fullpath=Path(__file__).with_name(REV+'_full_room.py') if Path(__file__).parent.name=='history' else ROOT/'blender/full_room.py'
 FULL_BYTES=fullpath.read_bytes();exec(compile(FULL_BYTES,str(fullpath),'exec'),globals())
for o in s.objects:
 if o.type=='MESH' and o.get('overhaul_modified') and not o.hide_render:
  assert len(o.data.vertices)>=3 and len(o.data.polygons)>=1,'Empty modified visible mesh: '+o.name
for p in fixture_pairs:p.pop('offset',None)
s['fixture_registry']=json.dumps(fixture_pairs);s['support_registry']=json.dumps(supports);s['overhaul_revision']=REV;s['overhaul_original_sha256']=source_hash;s['world_fixture_only']=True
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.max_bounces=8
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
outdir=ROOT/'production/coldstart'/REV if COLD else ROOT/'production/checkpoints';outdir.mkdir(parents=True,exist_ok=True)
output=outdir/(REV+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(output),check_existing=False,compress=True)
if not COLD:
 active=ROOT.parent/('module_overhaul_slice_R0.blend' if SLICE else 'module_overhaul_R1.blend');active.write_bytes(output.read_bytes())
record={'revision':REV,'source':source.relative_to(REPO).as_posix(),'source_sha256':source_hash,'output':output.relative_to(REPO).as_posix(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'object_count':len(s.objects),'new_objects':sorted(set(bpy.data.objects.keys())-original_names),'fixture_pairs':fixture_pairs,'supports':supports,'coldstart':COLD,'world_strength':0,'slice':SLICE}
record['builder_sha256']=hashlib.sha256(BUILDER_BYTES).hexdigest();history=ROOT/'blender/history';history.mkdir(exist_ok=True);snapshot=history/(REV+'_build.py');snapshot.write_bytes(BUILDER_BYTES);record['builder_snapshot']=snapshot.relative_to(REPO).as_posix()
if FULL_BYTES is not None:
 fullsnapshot=history/(REV+'_full_room.py');fullsnapshot.write_bytes(FULL_BYTES);record['full_room_snapshot']=fullsnapshot.relative_to(REPO).as_posix();record['full_room_sha256']=hashlib.sha256(FULL_BYTES).hexdigest()
report=outdir/(REV+'_build.json');report.write_text(json.dumps(record,indent=2)+'\n');print('WASTE_OVERHAUL_SAVED',REV,len(s.objects),'supports',len(supports),flush=True)
