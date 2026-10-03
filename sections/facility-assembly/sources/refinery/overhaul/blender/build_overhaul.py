"""Refinery additive interior overhaul. Run after loading original module.blend.
Never overwrites the original module, accepted snapshot, or assembled map.
"""
import bpy, math, json, hashlib, sys, random
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'module.blend'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
REV=int(args[0]) if args else 0
SLICE='slice' in args
COLDSTART='coldstart' in args
PRODUCTION_OUTPUT=ROOT/'production/coldstart'/f'R{REV:02d}' if COLDSTART else ROOT/'production'
PRODUCTION_OUTPUT.mkdir(parents=True,exist_ok=True)
random.seed(117)
s=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
protected_names=['Floor','Ceiling','North_wall','West_front_pier','West_main','West_header','East_front_pier','East_main','East_header','South_left','South_right','South_header']+[o.name for o in s.objects if any(q in o.name for q in ['external_sill','threshold_return','threshold_soffit','door_jamb','door_lintel','ENTRY_jamb','ENTRY_lintel'])]
def geom(o):
 return dict(matrix=[list(r) for r in o.matrix_world],vertices=[list(v.co) for v in o.data.vertices] if o.type=='MESH' else [])
protected={n:geom(bpy.data.objects[n]) for n in protected_names}
retired_decor=set()
def remove_object(o):
 # Removing a source parent must never reset attached detail into room coordinates.
 bpy.context.view_layer.update()
 for child in list(o.children):
  matrix=child.matrix_world.copy();child.parent=None;child.matrix_world=matrix
  if child.name.startswith('ART_'):retired_decor.add(child.name)
 bpy.data.objects.remove(o,do_unlink=True)

col=bpy.data.collections.new('REFINERY_OVERHAUL');s.collection.children.link(col)
lights=[];supports=[];new=[]
def tag(o,support=None):
 o['overhaul_revision']=REV;o['authoring_owner']='refinery-overhaul';new.append(o.name)
 if support:o['support_group']=support
 return o
def link(o):
 col.objects.link(o);return tag(o)
def mat(name,color,rough=.6,metal=0,variation=.02,emission=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes;n.clear();p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 if variation:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.7;tex.inputs['Detail'].default_value=1.8
  coord=n.new('ShaderNodeTexCoord');m.node_tree.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[1].position=.8
  ramp.color_ramp.elements[0].color=(*[max(0,c*(1-variation)) for c in color],1);ramp.color_ramp.elements[1].color=(*[min(1,c*(1+variation)) for c in color],1)
  m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac']);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
 return m
M={}
for k,c,r,metal,v in [
 ('oxide',(.28,.071,.028),.58,.22,.15),('oxide_edge',(.4,.14,.067),.68,.18,.06),
 ('green',(.075,.16,.142),.65,.12,.12),('warmwall',(.29,.265,.218),.88,0,.1),('wallpatch',(.34,.31,.26),.91,0,.08),
 ('dado',(.058,.102,.091),.76,.08,.1),('concrete',(.185,.174,.147),.88,0,.16),('epoxy',(.064,.073,.066),.75,0,.09),
 ('steel',(.27,.285,.27),.38,.78,.09),('dark',(.035,.044,.041),.54,.68,.06),('black',(.012,.017,.017),.9,0,.05),
 ('brass',(.35,.255,.093),.41,.64,.09),('ochre',(.65,.365,.048),.69,.12,.06),('ivory',(.59,.52,.373),.74,.08,.07),
 ('paper',(.72,.65,.48),.95,0,.05),('ink',(.033,.043,.036),.9,0,0),('cork',(.16,.09,.035),.98,0,.16),
 ('wood',(.19,.086,.035),.75,0,.14),('leather',(.26,.135,.055),.87,0,.08),('ceramic',(.5,.41,.247),.29,0,.02),
 ('red',(.38,.029,.017),.59,.16,.05),('dust',(.2,.183,.136),.95,0,.1),('blue',(.053,.105,.135),.65,.15,.1)]: M[k]=mat('RF1_'+k,c,r,metal,v)
M['lens']=mat('RF1_warm_lamp',(1,.75,.43),.25,0,0,5)
M['coldlens']=mat('RF1_task_lamp',(.7,.88,1),.25,0,0,4)
M['signal']=mat('RF1_status_amber',(1,.31,.028),.3,0,0,1.5)
# Existing cast/pressed asset edge modifiers receive the same sharper edge direction.
for o in s.objects:
 if o.name in protected_names:continue
 for mod in o.modifiers:
  if mod.type=='BEVEL':mod.width=min(mod.width,.004);mod.segments=1
# Replace entire old blue/white scheme with material-specific responses.
remap={'REF_teal':'oxide','REF_edge_blue':'oxide_edge','REF_rub_blue':'oxide_edge','REF_pale':'ivory','REF_edge_white':'ivory','REF_wall':'warmwall','REF_dado':'dado','REF_concrete':'concrete','REF_patch':'wallpatch','REF_darksteel':'dark','REF_steel':'steel','REF_rubber':'black','REF_gasket':'black','REF_yellow':'ochre','REF_ready':'ochre','REF_paper':'paper','REF_scratch':'steel','REF_cloth':'leather','REF_plastic':'green','REF_screen':'black','REF_lamp':'lens','REF_red':'red','REF_fault':'signal','REF_dirtyfilter':'dust','REF_ink':'ink','REF_fuel':'steel','REF_ore':'dust'}
for o in list(s.objects):
 if hasattr(o.data,'materials'):
  for i,m in enumerate(o.data.materials):
   if m and m.name in remap:o.data.materials[i]=M[remap[m.name]]
 if o.type=='LIGHT':remove_object(o)
# Cast control enclosures use dull green frames while interaction faces stay readable.
for o in s.objects:
 if o.type=='MESH' and o.name.endswith('_Control_enclosure'):
  if len(o.data.materials):o.data.materials[0]=M['green']
 if o.type=='MESH' and o.name.startswith('Column_pilaster'):
  o.data.materials[0]=M['dado']
# Restrained physical-scale grain and roughness variation, below silhouette/detail frequency.
for key,strength,distance,scale in [('warmwall',.13,.006,135),('wallpatch',.13,.006,135),('concrete',.16,.007,90),('oxide',.06,.002,70),('green',.06,.002,70),('leather',.13,.003,80)]:
 material=M[key];nodes=material.node_tree.nodes;links=material.node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 tc=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=1.5
 links.new(tc.outputs['Object'],noise.inputs['Vector']);bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance
 links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
# No environment radiance; no hidden fill. Only actual fixture lenses emit.
s.world=bpy.data.worlds.new('REFINERY_PRACTICAL_ONLY_WORLD');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
s.world.color=(0,0,0)
def mesh(name,verts,faces,m):
 me=bpy.data.meshes.new('RF1 '+name);me.from_pydata(verts,[],faces);me.materials.append(M[m] if isinstance(m,str) else m);o=link(bpy.data.objects.new('RF1 | '+name,me));return o
def bevel(o,w=.01,segments=2):
 # Owner requested sharper edges: small planar chamfers, no inflated rounds.
 w=min(w,.006) if o.type=='MESH' else w
 segments=1
 if w:
  b=o.modifiers.new('Construction edge','BEVEL');b.width=w;b.segments=segments
  b.affect='EDGES';b.limit_method='ANGLE'
  n=o.modifiers.new('Face weighted normals','WEIGHTED_NORMAL');n.keep_sharp=True;n.weight=25
 return o
def box(name,p,d,m='dark',b=.006):
 x,y,z=d;verts=[(a*x/2,bb*y/2,c*z/2) for a,bb,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 o=mesh(name,verts,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m);o.location=p
 for f in o.data.polygons:f.flip()
 return bevel(o,b)
def cyl(name,p,r,depth,m='steel',axis=(0,0,1),n=24):
 verts=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z in [-depth/2,depth/2] for i in range(n)]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh(name,verts,faces,m);o.location=p;o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
 for f in o.data.polygons:
  if len(f.vertices)==4:f.use_smooth=True
 return bevel(o,.002,2)
def rod(name,a,b,r=.018,m='steel',n=16):
 a,b=Vector(a),Vector(b);return cyl(name,(a+b)/2,r,(b-a).length,m,b-a,n)
def pipe(name,points,r=.035,m='steel'):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 cu.materials.append(M[m]);o=link(bpy.data.objects.new('RF1 | '+name,cu));return o
def ring(name,p,r,thick=.018,m='steel',axis=(0,0,1)):
 verts=[];N=32;K=8
 for i in range(N):
  a=i*2*math.pi/N
  for j in range(K):
   b=j*2*math.pi/K;verts.append(((r+thick*math.cos(b))*math.cos(a),(r+thick*math.cos(b))*math.sin(a),thick*math.sin(b)))
 faces=[(i*K+j,((i+1)%N)*K+j,((i+1)%N)*K+(j+1)%K,i*K+(j+1)%K) for i in range(N) for j in range(K)]
 o=mesh(name,verts,faces,m);o.location=p;o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
 for f in o.data.polygons:f.use_smooth=True
 return o
def lathe(name,p,profile,m='oxide',N=40):
 vs=[(r*math.cos(i*2*math.pi/N),r*math.sin(i*2*math.pi/N),z) for z,r in profile for i in range(N)]
 fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(len(profile)-1) for i in range(N)]
 fs+=[tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))]
 o=mesh(name,vs,fs,m);o.location=p
 for f in o.data.polygons:
  if len(f.vertices)==4:f.use_smooth=True
 return o
def plate(name,center,width,height,depth,m='oxide',cut=.15):
 # Authored clipped corners in XZ; front faces -Y.
 x,z=width/2,height/2;ps=[(-x+cut,-z),(x-cut,-z),(x,-z+cut),(x,z-cut),(x-cut,z),(-x+cut,z),(-x,z-cut),(-x,-z+cut)]
 vs=[(a,y,b) for y in [-depth/2,depth/2] for a,b in ps];fs=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 o=mesh(name,vs,fs,m);o.location=center
 for f in o.data.polygons:f.flip()
 return bevel(o,.009,2)
def text(name,body,p,size=.12,m='ivory',rot=(math.pi/2,0,0),align='LEFT'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.0003;cu.align_x=align;cu.space_character=1.1
 cu.materials.append(M[m]);o=link(bpy.data.objects.new('RF1 | '+name,cu));o.location=p;o.rotation_euler=rot;return o
def support(group,anchor,target,direction):
 supports.append(dict(group=group,anchor=list(anchor),target=target,direction=list(direction),max_gap=.005,max_penetration=.002))
def practical(name,p,target,energy,color,size,lens):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='RECTANGLE';d.size=size[0];d.size_y=size[1]
 o=link(bpy.data.objects.new('RF1 LIGHT | '+name,d));o.location=p;o.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler();o['fixture_lens']=lens.name;o['practical_only']=True
 lights.append(dict(name=o.name,lens=lens.name,energy=energy,location=list(p)));return o
# Primary shell is untouched. New interior fabric is seated to its original surfaces.
for i,x in enumerate([-6.0,-3.0,0,3.0,6.0]):
 panel=box('North acoustic concrete bay '+str(i),(x,6.406,2.72),(2.956,.052,3.58),'wallpatch' if i in [0,3] else 'warmwall',.008)
 support(panel.name,(x,6.432,2.72),'North_wall',(0,1,0))
 # Bottom wall feet and flange create material-dependent architecture, not greeble.
 if i in [0,2,4]:
  box('North vertical pier '+str(i),(x+1.4,6.28,2.42),(.19,.28,4.8),'dark',.009)
  box('North pier base '+str(i),(x+1.4,6.26,.16),(.31,.32,.32),'dark',.006)
box('North warm protective rail',(0,6.33,1.45),(14.8,.08,.095),'ivory',.012)
for side in [-1,1]:
 for y in [-.7,2.4,5.4]:
  o=box('Side flush panel',(side*7.478,y,2.79),(.052,2.88,3.47),'warmwall',.008);support(o.name,(side*7.504,y,2.79),'West_main' if side<0 else 'East_main',(side,0,0))
 # Cap the old wall protection with a narrow functional rail.
 box('Side rail',(side*7.442,1.92,1.45),(.08,8.8,.095),'ivory',.01)
# Structural ceiling: I sections have webs and flanges, alternating concrete infill.
for y in [-5.15,-.64,3.86]:
 box('I girder lower flange',(0,y,4.575),(14.98,.36,.055),'dark',.003)
 box('I girder web',(0,y,4.666),(14.98,.07,.182),'dark',.002)
 for side in [-1,1]:
  rod('Girder diagonal haunch',(side*7.24,y,3.94),(side*6.66,y,4.56),.06,'dark')
for x in [-5.0,0,5.0]:box('Ceiling service rail',(x,0,4.74),(.11,12.55,.075),'dark',.003)
# Floor overlays are at or below 2 mm; retain the original slab and travel elevations.
box('Process epoxy field',(0,4.775,.0006),(14.5,3.25,.0012),'epoxy',0)
box('Fabrication epoxy field',(5.94,-.65,.0007),(2.35,7.8,.0014),'epoxy',0)
# Quiet long routes with broken ochre edge paint, deliberately worn segments.
for y in [3.17]:
 for x in [-6.8,-5.55,-4.3,-3.05,-1.8,-.55,.7,1.95,3.2,4.45,5.7,6.95]:box('Process clearance stripe',(x,y,.0015),(.83,.058,.001),'ochre',0)
# Background hero lettering replaces the small floating pale identity panel.
for o in list(s.objects):
 if 'Section_identity'==o.name or 'Section_subtitle'==o.name or any(q in o.name for q in ['ART_Refining_sign_backing','ART_ART_Refining_sign_backing','ART_Sign_mount']):remove_object(o)
text('Wall department numeral','02',(-1.75,6.379,2.8),1.05,'dado')
text('Department title','MATERIAL RECOVERY',(1.9,6.379,3.45),.20,'ivory')
text('Department subline','FUEL FABRICATION / SHIFT 07',(1.91,6.379,3.15),.095,'ivory')
for name in ['Processor_sealed_hatch','Processor_seam_band','Processor_seam_band.001']:
 if bpy.data.objects.get(name):bpy.data.objects[name].data.materials[0]=M['steel']
# Rebuild the processor's major silhouette, retaining interactive components.
for o in list(s.objects):
 if any(o.name.startswith(q) for q in ['Processor_pressure_shell','Processor_dished_top','Processor_dished_bottom','ART_Processor_pressure_shell_surface_scuffs','ART_Processor_dished_top_surface_scuffs']):remove_object(o)
lathe('PV05 cast pressure vessel',(1.043,4.984,0),[(.67,.25),(.79,.49),(1.01,.66),(2.45,.66),(2.64,.59),(2.83,.3),(2.89,.21)],'oxide')
for z in [1.05,2.43]:
 ring('PV05 rolled seam',(1.043,4.984,z),.669,.026,'dark')
 for i in range(10):
  a=i*math.tau/10;cyl('Vessel band fixing',(1.043+.687*math.cos(a),4.984+.687*math.sin(a),z),.024,.016,'steel',(math.cos(a),math.sin(a),0),6)
# Cast plinth and diagonal braces replace the fragile four-leg read.
box('PV05 service plinth',(1.043,4.984,.2),(1.49,1.46,.4),'dark',.028)
for x in [.44,1.65]:
 plate('PV05 cast saddle',(x,4.984,.66),.14,.67,1.05,'dark',.06)
 support('PV05', (x,4.984,0),'Floor',(0,0,-1))
# Gauge, sight tube, manifold and process return: readable from route.
for x,z in [(1.0,2.3),(1.37,2.28)]:
 cyl('Pressure gauge backing',(x,4.307,z),.13,.07,'dark',(0,-1,0));cyl('Pressure gauge ivory face',(x,4.265,z),.109,.004,'paper',(0,-1,0))
 for a in [-2.3,-1.6,-.9,-.2,.5,1.2]:
  rod('Gauge tick',(x+.076*math.cos(a),4.260,z+.076*math.sin(a)),(x+.093*math.cos(a),4.260,z+.093*math.sin(a)),.003,'ink',8)
 rod('Gauge needle',(x,4.255,z),(x+.07,4.255,z+.042),.003,'red',8)
pipe('Vessel manifold',[(1.68,4.86,1.4),(2.0,4.83,1.4),(2.12,4.5,1.28),(2.12,4.02,.44)],.059,'steel')
for z in [.53,1.12]:cyl('Manifold union',(2.12,4.02,z),.083,.095,'dark')
ring('Brass isolation wheel',(2.12,3.95,.97),.18,.022,'brass',(0,-1,0))
for a in [0,2.1,4.2]:rod('Valve spoke',(2.12,3.95,.97),(2.12+.18*math.cos(a),3.95,.97+.18*math.sin(a)),.014,'brass')
# Two physical task lamps seated to north wall provide hero hierarchy.
for i,x in enumerate([.25,2.25]):
 back=box('PV task wall anchor',(x,6.340,3.88),(.18,.18,.24),'dark',.01)
 rod('PV task arm',(x,6.31,3.88),(x,5.96,3.65),.026,'dark')
 shade=box('PV task folded hood',(x,5.88,3.59),(.44,.29,.09),'dark',.012)
 lens=box('PV task actual lens',(x,5.88,3.542),(.36,.22,.006),'lens',.002)
 support(back.name,(x,6.430,3.88),'North_wall',(0,1,0))
 practical('PV hood '+str(i),(x,5.88,3.537),(1.1,4.6,1.6),95,(1,.69,.4),(.34,.2),lens)
# Visible practical ceiling pendants; source lenses and housings remain in place.
pendants=[(-4.85,-2.5,105,(.76,.87,1)),(-4.4,3.25,380,(1,.76,.5)),(0,3.1,460,(1,.75,.47)),(4.8,2.3,230,(1,.80,.58)),(4.8,-2,230,(.69,.83,1)),(-1.5,-3.3,140,(1,.79,.53))]
for i,(x,y,power,color) in enumerate(pendants):
 name='Pendant_diffuser'+('' if i==0 else '.'+str(i).zfill(3));lens=bpy.data.objects[name]
 lens.data.materials[0]=M['coldlens' if i in [0,4] else 'lens']
 practical('Ceiling pendant '+str(i),(x,y,4.405),(x,y,0),power,color,(1.22,.245),lens)
# Actual existing wall fixture lenses; reduce fill to small maintenance pools.
for i,x in enumerate([-5.75,-1.75,2.75,6.75]):
 lens=bpy.data.objects['ART_Wall_fixture_diffuser'+('' if i==0 else '.'+str(i).zfill(3))]
 practical('Wall service lamp '+str(i),(x,6.258,2.846),(x,5.7,.8),25,(1,.72,.46),(.19,.075),lens)
# Relocate the original utility cabinet assembly along the same wall, clear of the nook.
for o in list(s.objects):
 if any(q in o.name for q in ['Utility_cabinet','Utility_door','Utility_handle']):o.matrix_world.translation.x+=3.25
# Worker maintenance cluster: created with construction and contact, never random filler.
def bench(x,y,w=1.8):
 for xx in [x-w/2+.12,x+w/2-.12]:
  for yy in [y-.24,y+.24]:
   foot=box('Workbench base foot',(xx,yy,.025),(.16,.16,.05),'dark',.008);support(foot.name,(xx,yy,0),'Floor',(0,0,-1));box('Workbench folded leg',(xx,yy,.47),(.07,.08,.84),'dark',.005)
 box('Workbench lower shelf',(x,y,.27),(w-.12,.55,.04),'green',.008)
 top=box('Workbench timber top',(x,y,.94),(w,.64,.08),'wood',.014)
 for xx in [x-w/2+.06,x+w/2-.06]:box('Timber steel end strap',(xx,y,.945),(.075,.65,.083),'dark',.004)
 return top
# Build the maintenance cluster locally, then seat it in the clear personnel-side corner.
nook_start=len(new);nook_support_start=len(supports)
# Worker nook components.
top=bench(-6.66,1.52,1.1)
board=box('Shift notice cork backing',(-7.446,1.52,2.04),(.12,1.18,.84),'cork',.008);support(board.name,(-7.506,1.52,2.04),'West_main',(-1,0,0))
for zz in [1.61,2.47]:box('Shift board frame',(-7.365,1.52,zz),(.04,1.24,.034),'wood',.004)
for yy in [.9,2.14]:box('Shift board frame',(-7.365,yy,2.04),(.04,.034,.9),'wood',.004)
for j,(yy,zz,ww,hh) in enumerate([(1.22,2.19,.34,.43),(1.76,2.12,.33,.51),(1.12,1.79,.27,.2)]):
 paper=box('Pinned shift paper '+str(j),(-7.383,yy,zz),(.003,ww,hh),'paper',0)
 cyl('Drawing pin',(-7.378,yy,zz+hh/2-.025),.012,.016,'red',(-1,0,0),12)
 for k in range(3):box('Paper ink rule',(-7.379,yy,zz+.09-k*.06),(.001,ww*.68,.003),'ink',0)
text('Shift board note','07 / NIGHT',(-7.378,1.22,2.3),.06,'ink',(math.pi/2,0,math.pi/2),align='CENTER')
def mug(x,y,z):
 lathe('Worker enamel mug',(x,y,z),[(0,.074),(.01,.08),(.13,.08),(.135,.074),(.13,.064),(.019,.064)],'ceramic',28)
 ring('Mug handle',(x+.09,y,z+.08),.046,.012,'ceramic',(0,1,0));cyl('Coffee surface',(x,y,z+.106),.063,.002,'ink');support('Enamel mug',(x,y,z),top.name,(0,0,-1))
mug(-6.65,1.59,.98)
# Glove: broad leather cuff, palm, fingers, opposed thumb.
for g in [0,1]:
 x=-6.53+g*.17;y=1.27
 palm=plate('Work glove palm',(x,y,.991),.095,.13,.022,'leather',.02);palm.rotation_euler=(math.pi/2,0,.22*g)
 for k in range(4):
  box('Glove finger',(x-.033+k*.023,y+.1,.9985),(.018,.086-.009*k,.017),'leather',.009)
 box('Glove gauntlet cuff',(x,y-.084,.9925),(.109,.07,.025),'leather',.007)
 rod('Glove thumb',(x-.048,y+.01,.998),(x-.081,y+.066,.998),.015,'leather')
# Radio has handle, grille, dial, aerial and a restrained LED.
radio=plate('Pocket radio',(-6.66,1.77,1.092),.22,.22,.10,'green',.025)
for k in range(6):box('Radio speaker slit',(-6.715+k*.018,1.712,1.09),(.005,.006,.065),'black',.002)
cyl('Radio tuning dial',(-6.59,1.7,1.12),.026,.016,'brass',(0,-1,0))
rod('Radio aerial',(-6.62,1.77,1.20),(-6.60,1.77,1.47),.004,'steel')
pipe('Radio carry loop',[(-6.75,1.77,1.2),(-6.74,1.77,1.26),(-6.59,1.77,1.26),(-6.57,1.77,1.2)],.008,'black')
# A genuine task fixture lights the nook, seated to the existing wall.
anchor=box('Nook lamp wall base',(-7.433,1.4,2.65),(.146,.16,.20),'dark',.008)
rod('Nook lamp arm',(-7.35,1.4,2.65),(-7.03,1.4,2.51),.019,'dark')
hood=box('Nook light hood',(-6.96,1.4,2.49),(.34,.28,.065),'dark',.014)
lens=box('Nook light lens',(-6.96,1.4,2.454),(.27,.22,.005),'lens',.002)
support(anchor.name,(-7.506,1.4,2.65),'West_main',(-1,0,0));practical('Work nook lamp',(-6.96,1.4,2.45),(-6.67,1.52,.96),60,(1,.72,.44),(.26,.21),lens)
# Relocate the cluster as one assembly: the original west-wall location was obscured
# by the conveyor and wall pier. This south-wall corner has a clear approach.
bpy.context.view_layer.update()
relocation=Matrix.Translation(Vector((2.42,1.07238,0))) @ Matrix.Rotation(math.pi/2,4,'Z')
for name in new[nook_start:]:
 o=bpy.data.objects[name];o.matrix_world=relocation@o.matrix_world;o['support_group']='WorkNook'
bpy.context.view_layer.update()
radio_pivot=relocation@Vector((-6.66,1.77,1.092))
radio_turn=Matrix.Translation(radio_pivot)@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-radio_pivot)
for name in new[nook_start:]:
 if 'radio' in name.lower():bpy.data.objects[name].matrix_world=radio_turn@bpy.data.objects[name].matrix_world
for record in supports[nook_support_start:]:
 record['anchor']=list(relocation@Vector(record['anchor']));record['direction']=list(relocation.to_3x3()@Vector(record['direction']))
 if record['target']=='West_main':record['target']='South_right'
for record in lights:
 if 'Work nook' in record['name']:record['location']=list(bpy.data.objects[record['name']].location)
# Full-room expansion after the slice gate.
if not SLICE:
 # Crusher: sloped industrial cowling, ribbed drive enclosure and service guards.
 plate('Crusher angular front cowling',(-5.56,4.05,2.62),2.0,1.13,.10,'oxide',.20)
 box('Crusher mouth gasket',(-5.56,3.986,2.58),(1.28,.04,.65),'black',.017)
 box('Crusher jaw shadow',(-5.56,3.953,2.56),(1.10,.02,.51),'dark',.016)
 for x in [-6.06,-5.86,-5.66,-5.46,-5.26,-5.06]:plate('Crusher worn tooth',(x,3.928,2.56),.14,.39,.07,'steel',.035)
 for x in [-6.43,-4.69]:
  plate('Crusher cast gusset',(x,4.37,1.47),.19,.91,.68,'dark',.06)
  for z in [1.18,1.85,2.15]:cyl('Crusher cast bolt',(x,3.998,z),.033,.027,'steel',(0,-1,0),6)
 # Drive belt cover with explicit louvers and gasket separation.
 drive=plate('Crusher drive guard',(-4.56,4.76,1.55),.35,.95,.92,'green',.11)
 for k in range(7):box('Crusher guard cooling slots',(-4.739,4.48+k*.08,1.55),(.006,.044,.24),'black',.001)
 # Dust hood/extraction above crusher with broad galvanised band.
 lathe('Crusher extraction taper',(-5.55,4.96,3.11),[(0,.6),(.08,.6),(.43,.20),(.63,.20)],'dark',24)
 pipe('Crusher dust trunk',[(-5.55,4.96,3.69),(-5.55,5.88,4.15),(-5.55,6.08,4.23),(-1.1,6.08,4.23)],.115,'steel')
 for x in [-5.55,-3.45,-1.25]:ring('Dust trunk coupling',(x,6.08,4.23),.118,.027,'dark',(1,0,0))
 # Sorter hood: two broad folded guard cheeks, an inspection slot and task diode.
 for x in [-3.2,-2.3]:
  plate('Sorter guarding wing',(x,4.89,1.77),.09,.72,.89,'green',.03)
 box('Sorter sensor canopy',(-2.75,4.88,2.1),(1.13,1.06,.17),'green',.028)
 box('Sorter recessed optics',(-2.75,4.329,1.96),(.77,.018,.16),'black',.012)
 box('Sorter warm scanner glass',(-2.75,4.315,1.96),(.48,.005,.045),'signal',.004)
 text('Sorter bay id','GRADE / 04',(-3.08,4.31,2.085),.052,'ivory')
 # Dryer redesigned thermal jacket with chamfered shoulders and access split.
 plate('Dryer folded insulation facade',(4.09,4.091,1.57),2.39,1.55,.16,'green',.21)
 plate('Dryer recessed service seal',(4.09,3.997,1.54),1.82,.99,.024,'black',.09)
 plate('Dryer insulation hatch',(4.09,3.973,1.54),1.73,.90,.026,'oxide',.08)
 for x in [3.38,4.8]:
  for z in [1.21,1.89]:
   box('Dryer overcentre lock',(x,3.946,z),(.13,.058,.055),'steel',.009)
   rod('Dryer hatch handle',(x,3.906,z-.05),(x,3.906,z+.045),.017,'dark')
 box('Dryer hatch label',(4.09,3.951,1.66),(.44,.005,.12),'ivory',.002)
 text('Dryer cast label','DR-06 / THERMAL',(3.906,3.946,1.63),.04,'ink')
 for k in range(8):box('Dryer ventilation louvre',(3.55+k*.085,3.947,1.35),(.045,.015,.16),'dark',.003)
 # Brass utility loops and correctly joined pipe route.
 pipe('Dryer insulated steam line',[(4.11,5.3,2.17),(4.11,5.30,2.63),(4.36,5.70,2.93),(4.36,6.12,3.84)],.071,'ivory')
 for z in [2.36,2.62,3.42]:ring('Dryer steam joint',(4.36 if z>3 else 4.11,6.12 if z>3 else 5.3,z),.076,.023,'dark')
 # Press: authored cast pillars and clipped crown replace thin rectilinear silhouette.
 for yy in [.60,1.70]:
  plate('Fabrication cast upright',(6.145,yy,1.63),.36,1.55,.22,'oxide',.10)
 box('Press stepped crown',(6.06,1.15,2.47),(.82,1.55,.27),'oxide',.027)
 for yy in [.57,1.73]:box('Press steel bearing block',(5.94,yy,2.35),(.24,.21,.16),'steel',.008)
 cyl('Press drive motor',(6.09,1.15,2.74),.21,.42,'dark',(0,0,1))
 for zz in [2.59,2.65,2.71,2.77,2.83]:ring('Motor cast cooling fin',(6.09,1.15,zz),.222,.015,'dark')
 # Side console stepped housing and slab-mounted base.
 console=box('Fabrication control pedestal',(5.24,2.55,.72),(.34,.31,1.44),'green',.026);support(console.name,(5.24,2.55,0),'Floor',(0,0,-1))
 plate('Fabrication control housing',(5.24,2.53,1.49),.52,.43,.27,'green',.06)
 for xx,m in [(5.1,'ochre'),(5.26,'red'),(5.41,'ivory')]:cyl('Fabrication push button',(xx,2.377,1.45),.028,.016,m,(0,-1,0))
 # Physical press lamp attached to the cast crown, no free fill.
 box('Press fixture casing',(5.81,1.15,2.425),(.23,.85,.055),'dark',.005)
 lens=box('Press actual lens',(5.81,1.15,2.395),(.18,.75,.004),'coldlens',.001)
 practical('Press task bar',(5.81,1.15,2.391),(5.88,1.15,1.06),35,(.67,.81,1),(.17,.74),lens)
 # Inspection small precision cluster: low clutter, uses the existing benchtop.
 for yy in [-2.8,-2.5,-2.2]:
  lathe('Inspection sample tin',(6.05,yy,1.04),[(0,.045),(.10,.045),(.11,.039)],'steel',20)
  cyl('Sample colored cap',(6.05,yy,1.156),.047,.018,'green')
  box('Sample ivory band',(6.05,yy-.047,1.105),(.057,.003,.026),'paper',.001)
 # Ledger lies seated to existing inspection top, with visible page stack and diagonal pencil.
 box('Inspection batch ledger',(5.59,-2.47,1.058),(.29,.38,.025),'paper',.003)
 for yy in [-2.61,-2.55,-2.49,-2.43,-2.37]:box('Ledger handwritten rule',(5.59,yy,1.071),(.20,.003,.001),'ink',0)
 rod('Inspection pencil',(5.41,-2.25,1.077),(5.7,-2.20,1.077),.006,'ochre')
 # Opposite side corner floor-mounted parts cabinet and human pinboard.
 cab=plate('Parts cabinet cast facade',(-7.03,4.0,.94),.61,1.88,.52,'green',.065)
 support(cab.name,(-7.03,4.0,0),'Floor',(0,0,-1))
 for z in [.43,.78,1.13,1.48]:
  plate('Parts drawer face',(-7.03,3.727,z),.53,.29,.018,'green',.027)
  box('Drawer label holder',(-7.15,3.709,z+.04),(.13,.01,.043),'ivory',.002)
  pipe('Drawer pull',[(-7.02,3.699,z),(-7.02,3.67,z),(-6.86,3.67,z),(-6.86,3.699,z)],.011,'steel')
 # Hung spare drive belts beside the process service cabinet; seated hooks to west wall.
 for yy in [.92,1.12]:
  rod('Belt hook',(-7.50,yy,1.44),(-7.22,yy,1.44),.011,'steel')
  o=ring('Hung drive belt',(-7.28,yy,1.23),.19,.022,'black',(0,1,0));o.scale=(.65,1,1.18)
 # Real floor contact for wheeled maintenance trolley, original frame preserved.
 for xx in [-.505,.305]:
  for yy in [-5.304,-4.864]:
   ring('Trolley rubber tyre',(xx,yy,.082),.064,.018,'black',(1,0,0))
 # Rag draped over trolley: broad folds, no microscopic noise.
 vs=[];fs=[]
 for i in range(8):
  for j in range(8):
   xx=-.08+i*.035;yy=-5.2+j*.05;zz=.87+.009*math.sin(i*1.9)+.006*math.sin(j*1.7)
   if j>5:zz-=.1*(j-5);yy=-4.81+.009*(j-5)
   vs.append((xx,yy,zz))
 for i in range(7):
  for j in range(7):a=i*8+j;fs.append((a,a+1,a+9,a+8))
 rag=mesh('Trolley draped shop rag',vs,fs,'leather');solid=rag.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.003
 # Oil can has a recognisable tapered spout and pump handle.
 lathe('Trolley oil can',(-.38,-5.09,.861),[(0,.065),(.12,.072),(.14,.05)],'red',24)
 pipe('Oil can spout',[(-.38,-5.09,1.0),(-.33,-5.08,1.06),(-.26,-5.08,1.12)],.007,'steel')
 rod('Oil pump lever',(-.39,-5.09,1.01),(-.45,-5.09,1.05),.008,'dark')
 # Small postcard on the new nook corkboard; apply the same rigid assembly transform.
 postcard_start=len(new)
# Small postcard: colleague's pressure-vessel doodle.
 box('Crew postcard',(-7.383,1.73,1.84),(.003,.29,.18),'ivory',0)
 ring('Postcard doodled vessel',(-7.382,1.73,1.85),.05,.002,'oxide',(1,0,0))
 bpy.context.view_layer.update()
 for name in new[postcard_start:]:bpy.data.objects[name].matrix_world=relocation@bpy.data.objects[name].matrix_world
 # Mounted clock on back wall: functional silhouette, precise restraint.
 rod('Shift clock wall stud',(-3.5,6.427,3.08),(-3.5,6.346,3.08),.024,'dark')
 cyl('Shift clock body',(-3.5,6.292,3.08),.20,.11,'dark',(0,-1,0));cyl('Shift clock face',(-3.5,6.234,3.08),.174,.007,'paper',(0,-1,0))
 for a in range(12):
  t=a*math.tau/12;rod('Clock tick',(-3.5+.145*math.cos(t),6.227,3.08+.145*math.sin(t)),(-3.5+.159*math.cos(t),6.227,3.08+.159*math.sin(t)),.003,'ink',8)
 rod('Clock hour',(-3.5,6.222,3.08),(-3.57,6.222,3.13),.006,'ink');rod('Clock minute',(-3.5,6.222,3.08),(-3.38,6.222,3.1),.004,'ink')
 # Maintenance clipboard and one overtly human scribble on existing machine, no clutter spam.
 box('PV taped shift note',(1.58,4.29,1.81),(.17,.004,.12),'paper',.002)
 text('PV shift note writing','CHECK SEAL',(1.508,4.285,1.815),.020,'ink')
# R02 structural correction: construction variety, human-scale process dressing.
if REV>=2 and not SLICE:
 bpy.context.view_layer.update()
 # Ergonomic control-head tilt, preserving every separated interactive component.
 originals=[o for o in s.objects if not o.get('authoring_owner')]
 for head in [o for o in originals if o.type=='MESH' and o.name.endswith('_Control_enclosure')]:
  corners=[head.matrix_world@Vector(v) for v in head.bound_box];lo=Vector([min(v[i] for v in corners) for i in range(3)]);hi=Vector([max(v[i] for v in corners) for i in range(3)]);pivot=(lo+hi)/2
  side=(hi.x-lo.x)<(hi.y-lo.y);axis='Y' if side else 'X';angle=(math.radians(18) if pivot.x>0 else -math.radians(18)) if side else -math.radians(18)
  transform=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,axis)@Matrix.Translation(-pivot)
  if REV>=4:
   # Snapshot an entire operator head before touching its parents. Front buttons
   # sit outside the enclosure bbox and must share the same rigid transform.
   prefix=head.name.removesuffix('Control_enclosure')
   members=[o for o in originals if o==head or ((o.name.startswith(prefix) or o.name.startswith('ART_'+prefix)) and any(q in o.name for q in ['_button','_engraving','Control_enclosure']))]
   matrices={o.name:o.matrix_world.copy() for o in members}
   def depth(o):
    count=0
    while o.parent:count+=1;o=o.parent
    return count
   for o in sorted(members,key=depth):
    o.matrix_world=transform@matrices[o.name];o['control_head_tilt_degrees']=18
   bpy.context.view_layer.update()
   continue
  for o in originals:
   if o.type not in {'MESH','FONT'}:continue
   center=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
   if all(lo[i]-.022<=center[i]<=hi[i]+.022 for i in range(3)):
    o.matrix_world=transform@o.matrix_world;o['control_head_tilt_degrees']=18
 # Recast the dryer as a recognisable horizontal thermal vessel with an access manifold.
 for o in list(s.objects):
  if any(o.name.startswith(q) for q in ['Dryer_insulated_tunnel','ART_Dryer_insulated_tunnel_surface_scuffs','Dryer_portal','ART_Dryer_portal','Dryer_sealed_access_door','ART_Dryer_sealed_access_door','Dryer_door','ART_Dryer_door','RF1 | Dryer folded insulation facade','RF1 | Dryer recessed service seal','RF1 | Dryer insulation hatch']):remove_object(o)
 drum=lathe('DR06 horizontal thermal drum',(4.09,4.97,1.52),[(-1.18,.30),(-1.05,.58),(-.87,.67),(.87,.67),(1.05,.58),(1.18,.30)],'green',36);drum.rotation_euler=(0,math.pi/2,0)
 for xx in [3.18,3.65,4.55,5.00]:ring('DR06 thermal jacket rolled band',(xx,4.97,1.52),.679,.025,'steel',(1,0,0))
 for xx in [3.38,4.80]:
  # Saddles and hold-downs have deliberately different profile from machine table frames.
  plate('DR06 cast cradle',(xx,4.97,.98),.19,.55,1.12,'dark',.04)
  for yy in [4.46,5.48]:cyl('Thermal cradle securing bolt',(xx,yy,.74),.03,.055,'steel',(0,0,1),6)
 plate('DR06 flanged cleanout',(4.09,4.289,1.53),1.34,.86,.052,'dark',.16)
 plate('DR06 thermal access face',(4.09,4.255,1.53),1.22,.76,.021,'oxide',.13)
 # Existing hatch locks remain separated and usable; trim/relocate them onto the drum's panel.
 for o in list(s.objects):
  if o.name.startswith('RF1 | Dryer overcentre lock') or o.name.startswith('RF1 | Dryer hatch handle') or o.name.startswith('RF1 | Dryer hatch label') or o.name.startswith('RF1 | Dryer cast label') or o.name.startswith('RF1 | Dryer ventilation louvre'):
   o.location.y+=.29
 # View through the press's guard to mechanism, with tinted edge and low glare.
 glass=mat('RF1_clear_guard_glass',(.93,.98,.98),.028,0,0)
 p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Transmission Weight'].default_value=.96;p.inputs['IOR'].default_value=1.44
 for o in s.objects:
  if hasattr(o.data,'materials'):
   for i,m in enumerate(o.data.materials):
    if m and m.name=='REF_glass':o.data.materials[i]=glass
 # Construction-jointed floor: thin seated screed panels, broad tonal changes, no noisy scan.
 floor_mats=[mat('RF1_screed_'+str(i),(.157+i*.007,.151+i*.006,.13+i*.004),.89,0,.10) for i in range(4)]
 for ix in range(8):
  for iy in range(6):
   x=-6.54+ix*1.865;y=-5.34+iy*1.98
   if y>2.4 or x>4.5:continue
   slab=box('Worked floor panel',(x,y,.0006),(1.854,1.969,.0012),floor_mats[(ix+2*iy)%4],0)
 for o in s.objects:
  if o.name.startswith('Floor_route_arrow'):o.location.z+=.002
 # Drainage grate edge stays flat to the original travel plane.
 box('Process drainage dark reveal',(0,3.37,.0009),(13.6,.21,.0018),'black',0)
 for i in range(110):box('Process drainage grate rung',(-6.66+i*.122,3.37,.0022),(.03,.205,.0012),'steel',0)
 for y in [3.25,3.49]:box('Drain rolled border',(0,y,.0019),(13.6,.014,.0018),'dark',0)
 # A used maintenance cart in a recess between process line and route: active aisle stays clear.
 cx,cy=-3.40,2.67
 for xx in [cx-.30,cx+.30]:
  for yy in [cy-.23,cy+.23]:
   cyl('Service cart caster',(xx,yy,.095),.095,.062,'black',(1,0,0),20)
   cyl('Caster metal axle cap',(xx-.034,yy,.095),.033,.01,'steel',(1,0,0),16)
   box('Caster fork',(xx,yy,.205),(.073,.10,.15),'dark',.003)
   support('MaintenanceCart', (xx,yy,0),'Floor',(0,0,-1))
 cart=box('Service cart folded cabinet',(cx,cy,.58),(.72,.57,.69),'oxide',.004)
 for z in [.38,.56,.74]:
  box('Service cart drawer gasket',(cx,cy-.294,z),(.66,.013,.147),'black',.002)
  box('Service cart drawer front',(cx,cy-.308,z),(.64,.018,.136),'oxide',.003)
  rod('Cart drawer pull',(cx-.12,cy-.338,z+.02),(cx+.12,cy-.338,z+.02),.012,'dark')
  box('Cart drawer label',(cx+.22,cy-.32,z+.02),(.10,.002,.027),'paper',0)
 carttop=box('Service cart stainless tray',(cx,cy,.951),(.79,.63,.052),'steel',.003)
 for xx in [cx-.387,cx+.387]:box('Cart tray folded return',(xx,cy,.998),(.018,.63,.08),'steel',.002)
 pipe('Cart tubular push rail',[(cx+.33,cy-.26,.94),(cx+.47,cy-.26,1.08),(cx+.47,cy+.26,1.08),(cx+.33,cy+.26,.94)],.018,'dark')
 # Open spanner, oil bottle, shop-rag, spare bearing and folded cloth make a purposeful cluster.
 rod('Cart service spanner shaft',(cx-.27,cy-.08,.986),(cx+.16,cy+.10,.986),.016,'steel')
 ring('Spanner box end',(cx-.27,cy-.08,.986),.046,.012,'steel')
 box('Spanner fork left',(cx+.21,cy+.08,.986),(.09,.022,.025),'steel',.002)
 box('Spanner fork right',(cx+.17,cy+.15,.986),(.09,.022,.025),'steel',.002)
 cyl('Cart spare bearing',(cx-.12,cy+.18,1.0),.06,.045,'dark');ring('Bearing visible race',(cx-.12,cy+.18,1.024),.047,.008,'steel')
 oil=lathe('Service bottle',(cx+.23,cy-.15,.977),[(0,.044),(.14,.049),(.19,.025),(.22,.023)],'ivory',24)
 cyl('Bottle ribbed screw cap',(cx+.23,cy-.15,1.202),.026,.03,'dark')
 box('Bottle taped label',(cx+.23,cy-.199,1.057),(.06,.003,.043),'paper',.001)
 for i in range(3):box('Folded cart rag',(cx-.22,cy+.05,1.002+i*.009),(.20,.16,.011),'leather',.005)
 # Reinforce the old machine stands with specific diagonal load paths, not generic ornament.
 for xa,xb,y,z in [(-6.69,-4.43,5.66,.94),(-4.1,-2.35,5.32,1.12),(-2.35,-.60,5.32,1.12),(3.04,5.15,5.63,.63)]:
  rod('Machine stand diagonal brace',(xa,y,.10),(xb,y,z),.024,'dark')
 # Legible process marking on the thermal drum; no wall label clutter.
 text('DR06 jacket stencil','DR-06 / DRYING',(3.56,4.22,1.94),.088,'ivory')
 text('Crusher guard warning','03 / CRUSHING',(-6.24,3.991,3.04),.084,'ivory')
 text('Cart maintenance mark','MAINT / 07',(cx-.23,cy-.321,.86),.059,'ivory')

# R03: activity, practical-lit threshold depth, specific service work.
if REV>=3 and not SLICE:
 M['ore']=mat('RF1_ore_stone',(.105,.132,.112),.86,.025,.17)
 def stone(name,center,scale):
  N=12 if REV>=6 else 14;K=7 if REV>=6 else 9;vs=[]
  for k in range(K):
   t=math.pi*(k+.25)/(K-.5)
   for i in range(N):
    a=i*math.tau/N;r=1+random.uniform(-.17,.17) if REV>=6 else 1+random.uniform(-.085,.085)
    vs.append((math.cos(a)*math.sin(t)*scale[0]*r,math.sin(a)*math.sin(t)*scale[1]*r,math.cos(t)*scale[2]*r))
  fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(K-1) for i in range(N)]
  fs+=[tuple(reversed(range(N))),tuple((K-1)*N+i for i in range(N))]
  o=mesh(name,vs,fs,'ore');o.location=center
  if REV>=5:
   for f in o.data.polygons:f.flip()
  bevel(o,.002,1);return o
 # A consolidated granular mound rests on the original cart's measured 0.73m internal floor.
 mound=lathe('Contained cart ore mound',(-5.66,-4.05,0),[(.731,.30),(.86,.42),(1.08,.55),(1.23,.38)],'ore',28);mound.scale=(1.45,.90,1)
 support('Contained ore load',(-5.66,-4.05,.731),'CSM_Welded_hopper_shell',(0,0,-1))
 # Load is contained by the original ore cart, a coherent process story rather than floor clutter.
 for ix in range(6):
  for iy in range(4):
   x=-6.37+ix*.282;y=-4.61+iy*.32;z=1.2+.035*math.sin(ix+iy)
   stone('Receiving cart loaded ore',(x,y,z),(.19,.21,.17))
 for ix in range(5):
  for iy in range(3):stone('Ore load upper layer',(-6.24+ix*.283,-4.43+iy*.31,1.37),(.18,.20,.145))
 for o in list(s.objects):
  if o.name.startswith('Consolidated_ore_batch'):
   center=o.matrix_world.translation.copy();center.z+=.01;remove_object(o)
   for off in [-.08,.07]:stone('Moving ore batch',center+Vector((off,0,0)),(.11,.09,.082))
 # Credible cleanup cluster by the maintained safety/eyewash station.
 rack=box('Cleanup wall mounting rail',(-5.67,-6.394,1.84),(.74,.075,.095),'green',.004);support(rack.name,(-5.67,-6.4315,1.84),'South_left',(0,-1,0))
 for x in [-5.91,-5.43]:
  rod('Cleanup tool retaining hook',(x,-6.35,1.84),(x,-6.18,1.84),.012,'steel')
 # Broom is supported at the floor and clipped to the hook, natural work scale.
 rod('Wood broom shaft',(-5.91,-6.17,.16),(-5.91,-6.17,1.99),.017,'wood')
 broom=box('Broom bristle block',(-5.91,-6.17,.056),(.34,.14,.112),'leather',.004);support(broom.name,(-5.91,-6.17,0),'Floor',(0,0,-1))
 box('Broom timber head',(-5.91,-6.17,.135),(.36,.155,.045),'wood',.003)
 for i in range(12):box('Broom simplified bristle cut',(-6.066+i*.028,-6.089,.045),(.008,.002,.082),'dark',0)
 rod('Long cleanup brush',(-5.43,-6.18,.27),(-5.43,-6.18,1.98),.016,'dark')
 plate('Cleanup dustpan back',(-5.43,-6.18,.29),.24,.26,.018,'ochre',.015)
 box('Dustpan base lip',(-5.43,-6.075,.161),(.24,.23,.018),'ochre',.002)
 # Proper stainless eyewash splashback connects the rinse point to believable construction.
 plate('Eyewash stainless splash shield',(-6.41,-6.395,1.23),.86,.61,.035,'steel',.08)
 box('Eyewash water isolator wall base',(-6.94,-6.385,1.60),(.14,.095,.20),'green',.004)
 pipe('Eyewash rinse pipe',[(-6.94,-6.33,1.69),(-6.94,-6.33,2.56),(-6.68,-6.33,2.73),(-6.43,-6.33,2.73)],.026,'steel')
 ring('Safety station isolation wheel',(-6.94,-6.309,1.60),.10,.015,'brass',(0,1,0))
 for a in [0,2.094,4.188]:rod('Safety wheel spoke',(-6.94,-6.309,1.6),(-6.94+.1*math.cos(a),-6.309,1.6+.1*math.sin(a)),.009,'brass')
 # Visible fixture over the eyewash; cold-neutral pool differentiates safety corner.
 anchor=box('Eyewash lamp mount',(-6.40,-6.404,2.59),(.12,.06,.18),'dark',.002);support(anchor.name,(-6.40,-6.434,2.59),'South_left',(0,-1,0))
 rod('Eyewash lamp arm',(-6.40,-6.36,2.59),(-6.40,-6.09,2.54),.018,'steel')
 box('Eyewash lamp folded hood',(-6.40,-6.045,2.51),(.40,.27,.05),'dark',.002)
 lens=box('Eyewash fixture lens',(-6.40,-6.045,2.482),(.34,.22,.004),'coldlens',.001)
 practical('Eyewash service practical',(-6.40,-6.045,2.478),(-6.40,-6.08,.9),45,(.72,.9,1),(.33,.21),lens)
 # Threshold lights are inside the module and physically fitted to existing header planes.
 for side,title in [(-1,'Mine'),(1,'Fuel transfer')]:
  x=side*7.475;mount=box(title+' lintel mount',(x,-4.084,3.34),(.06,.14,.18),'dark',.002)
  support(mount.name,(side*7.505,-4.084,3.34),'West_header' if side<0 else 'East_header',(side,0,0))
  rod(title+' fixture arm',(side*7.435,-4.084,3.32),(side*7.17,-4.084,3.25),.022,'dark')
  box(title+' fixture hood',(side*7.16,-4.084,3.22),(.31,.64,.06),'dark',.002)
  lens=box(title+' fixture lens',(side*7.16,-4.084,3.187),(.26,.57,.004),'coldlens' if side<0 else 'lens',.001)
  practical(title+' threshold practical',(side*7.16,-4.084,3.183),(side*7.47,-4.084,.12),90,(.69,.84,1) if side<0 else (1,.74,.44),(.25,.56),lens)
 mount=box('Personnel lintel fixture mount',(-1.8,-6.401,2.98),(.13,.06,.17),'dark',.002);support(mount.name,(-1.8,-6.431,2.98),'South_header',(0,-1,0))
 rod('Personnel fixture support',(-1.8,-6.369,2.98),(-1.8,-6.16,2.86),.02,'dark')
 box('Personnel fixture hood',(-1.8,-6.16,2.83),(.68,.30,.06),'dark',.002)
 lens=box('Personnel fixture lens',(-1.8,-6.16,2.797),(.60,.24,.004),'lens',.001)
 practical('Personnel threshold practical',(-1.8,-6.16,2.793),(-1.8,-6.28,.1),65,(1,.8,.55),(.59,.23),lens)
 # One batch record shelf at process control, with a filled ledger and pencil.
 for yy in [4.18,4.32]:
  box('Process ledger steel shelf bracket',(-.4,yy,1.15),(.055,.10,.21),'dark',.002)
 rod('Ledger shelf cantilever',(-.45,4.504283,1.23),(-.27,4.25,1.252),.018,'dark')
 support('Process ledger shelf',(-.45,4.504283,1.23),'Sorter_sideframe.001',(0,1,0))
 shelf=box('Process batch ledger shelf',(-.27,4.25,1.267),(.43,.33,.03),'green',.002)
 box('Process ledger pages',(-.27,4.25,1.30),(.26,.27,.035),'paper',.002)
 for z in [1.314,1.319]:box('Process ledger paper edge',(-.27,4.105,z),(.24,.002,.001),'ivory',0)
 for yy in [4.16,4.20,4.24,4.28,4.32]:box('Process ledger written line',(-.27,yy,1.319),(.18,.003,.001),'ink',0)
 rod('Process ledger pencil',(-.15,4.13,1.323),(-.16,4.34,1.323),.005,'ochre')
 # Source fixtures stay motivated; reduce the broad forecourt ceiling wash now that doors have lamps.
 for name in ['RF1 LIGHT | Ceiling pendant 0','RF1 LIGHT | Ceiling pendant 5']:
  bpy.data.objects[name].data.energy*=.65
 # Human crew note, drawn as flat linework and text on the existing postcard.
 old=bpy.data.objects.get('RF1 | Postcard doodled vessel')
 if old:remove_object(old)
 text('Crew handwritten postcard','KEEP IT\nFLOWING',(.81,-6.306,1.88),.032,'ink',(math.pi/2,0,math.pi),align='CENTER')
 # Broad local foot/handling wear: a few long repaired route rubs, not full-surface noise.
 for x,y,length in [(-5.58,-3.0,.40),(-5.77,-2.9,.47),(4.5,-4.1,.36),(4.43,-4.0,.32),(-3.6,2.14,.26)]:
  o=box('Handling route rubbed patch',(x,y,.0024),(length,.045,.0007),'dust',0);o.rotation_euler.z=.11

if REV>=4 and not SLICE:
 exec(compile((ROOT/'blender/revision_R04.py').read_text(),str(ROOT/'blender/revision_R04.py'),'exec'))

if REV>=5 and not SLICE:
 exec(compile((ROOT/'blender/revision_R05.py').read_text(),str(ROOT/'blender/revision_R05.py'),'exec'))

if REV>=6 and not SLICE:
 exec(compile((ROOT/'blender/revision_R06.py').read_text(),str(ROOT/'blender/revision_R06.py'),'exec'))

if REV>=7 and not SLICE:
 exec(compile((ROOT/'blender/revision_R07.py').read_text(),str(ROOT/'blender/revision_R07.py'),'exec'))

if REV>=8 and not SLICE:
 exec(compile((ROOT/'blender/revision_R08.py').read_text(),str(ROOT/'blender/revision_R08.py'),'exec'))

if REV>=9 and not SLICE:
 exec(compile((ROOT/'blender/revision_R09.py').read_text(),str(ROOT/'blender/revision_R09.py'),'exec'))

if REV>=10 and not SLICE:
 exec(compile((ROOT/'blender/revision_R10.py').read_text(),str(ROOT/'blender/revision_R10.py'),'exec'))

if REV>=11 and not SLICE:
 exec(compile((ROOT/'blender/revision_R11.py').read_text(),str(ROOT/'blender/revision_R11.py'),'exec'))

if REV>=12 and not SLICE:
 exec(compile((ROOT/'blender/revision_R12.py').read_text(),str(ROOT/'blender/revision_R12.py'),'exec'))

if REV>=13 and not SLICE:
 exec(compile((ROOT/'blender/revision_R13.py').read_text(),str(ROOT/'blender/revision_R13.py'),'exec'))

if REV>=14 and not SLICE:
 exec(compile((ROOT/'blender/revision_R14.py').read_text(),str(ROOT/'blender/revision_R14.py'),'exec'))

if REV>=15 and not SLICE:
 exec(compile((ROOT/'blender/revision_R15.py').read_text(),str(ROOT/'blender/revision_R15.py'),'exec'))

if REV>=16 and not SLICE:
 exec(compile((ROOT/'blender/revision_R16.py').read_text(),str(ROOT/'blender/revision_R16.py'),'exec'))

if REV>=17 and not SLICE:
 exec(compile((ROOT/'blender/revision_R17.py').read_text(),str(ROOT/'blender/revision_R17.py'),'exec'))

if REV>=18 and not SLICE:
 exec(compile((ROOT/'blender/revision_R18.py').read_text(),str(ROOT/'blender/revision_R18.py'),'exec'))

if REV>=19 and not SLICE:
 exec(compile((ROOT/'blender/revision_R19.py').read_text(),str(ROOT/'blender/revision_R19.py'),'exec'))

if REV>=20 and not SLICE:
 exec(compile((ROOT/'blender/revision_R20.py').read_text(),str(ROOT/'blender/revision_R20.py'),'exec'))

if REV>=21 and not SLICE:
 exec(compile((ROOT/'blender/revision_R21.py').read_text(),str(ROOT/'blender/revision_R21.py'),'exec'))

if REV>=22 and not SLICE:
 exec(compile((ROOT/'blender/revision_R22.py').read_text(),str(ROOT/'blender/revision_R22.py'),'exec'))

if REV>=23 and not SLICE:
 exec(compile((ROOT/'blender/revision_R23.py').read_text(),str(ROOT/'blender/revision_R23.py'),'exec'))

if REV>=24 and not SLICE:
 exec(compile((ROOT/'blender/revision_R24.py').read_text(),str(ROOT/'blender/revision_R24.py'),'exec'))

# Retire decorative children of replaced source bodies; keep independent functional parts.
while retired_decor:
 name=retired_decor.pop();o=bpy.data.objects.get(name)
 if o:remove_object(o)
# Surface wear stays local: chip fragments at latches/cast-base contact, swept route wheel traces.
for i in range(28):
 x=random.uniform(-.1,2.1);y=random.uniform(3.15,3.42)
 box('Service floor scuff',(x,y,.0022),(random.uniform(.09,.29),random.uniform(.006,.02),.0006),'dust',0)
# Dedicated close detail evidence supplements, never replaces, existing room cameras.
for name,position,target,lens in [('CAM_WORK_NOOK',(-.60,-3.15,1.68),(.92,-5.91,1.50),31),('CAM_HERO_DETAIL',(-.30,2.15,1.68),(1.18,4.79,1.9),34)]:
 data=bpy.data.cameras.new(name);data.lens=lens;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=position;o.rotation_euler=(Vector(target)-Vector(position)).to_track_quat('-Z','Y').to_euler()
# Reconcile modified practical outputs into the persisted fixture registry.
bpy.context.view_layer.update()
for record in lights:
 o=bpy.data.objects.get(record['name'])
 if o:
  record['energy']=o.data.energy;record['location']=list(o.matrix_world.translation)
  record['matrix']=[list(r) for r in o.matrix_world]
# Save staged source and exact validation evidence. No source map mutation.
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.seed=73;s.cycles.max_bounces=8
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=8
s.camera=bpy.data.objects['CAM_ENTRY'];s['practical_only']=True;s['overhaul_baseline_sha256']=source_hash;s['overhaul_revision']=REV
s['support_registry']=json.dumps(supports);s['light_registry']=json.dumps(lights)
# Source-local edits retain the unmodified outer shell.
assert all(geom(bpy.data.objects[n])==g for n,g in protected.items()),'Interface geometry mutated'
(PRODUCTION_OUTPUT/'baseline_interfaces.json').write_text(json.dumps(dict(source_sha256=source_hash,protected=protected),indent=2))
filename='module_overhaul_slice_R0.blend' if SLICE else 'module_overhaul_R1.blend'
out=PRODUCTION_OUTPUT/'candidate.blend' if COLDSTART else ROOT.parent/filename
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False,compress=True)
report=dict(revision=REV,slice=SLICE,coldstart_rebuild=COLDSTART,output=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),baseline_sha256=source_hash,protected_interfaces=len(protected),new_objects=len(new),object_count=len(s.objects),lights=lights,supports=supports,world_strength=0)
(PRODUCTION_OUTPUT/('build_slice.json' if SLICE else f'build_R{REV:02d}.json')).write_text(json.dumps(report,indent=2))
print('REFINERY_OVERHAUL_SAVED',filename,len(s.objects),flush=True)
