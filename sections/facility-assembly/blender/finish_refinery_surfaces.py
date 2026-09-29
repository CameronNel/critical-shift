"""Reversible refinery finish slice; headless CPU only, no linked-library edits."""
import bpy,bmesh,math,json,hashlib,ctypes,shutil,ast,random,sys
from pathlib import Path
from mathutils import Vector,Matrix
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-finish';OUT.mkdir(parents=True,exist_ok=True)
SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(SRC);assert before==json.loads((OUT/'inspection.json').read_text())['sha256'],'Concurrent main revision'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rng=random.Random(271903)
backup=SRC.with_name('facility_environment.refinery-finish-before.blend')
if backup.exists():assert sha(backup)==before,'Different finish checkpoint'
else:shutil.copy2(SRC,backup)
coll=bpy.data.collections.new('ART | Refinery authored surface finish');s.collection.children.link(coll)
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text())
for name in ('mesh','box','cyl','beam','P','wb'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<geometry>','exec'))
# Reuse helper geometry, but ownership is this finish collection.
def surface(name,col,rough=.8,metal=0,scale=.8,relief=.002,existing=None,vertical=False):
 m=existing or bpy.data.materials.new('RFS | '+name);m.use_nodes=True;m.diffuse_color=(*col,1);nt=m.node_tree;nt.nodes.clear()
 fr=nt.nodes.new('NodeFrame');fr.label='Surface Colour And Micro Relief'
 def node(t,x,y=0):
  n=nt.nodes.new(t);n.parent=fr;n.location=(x,y);n.width=180;return n
 geo=node('ShaderNodeNewGeometry',0);mapping=node('ShaderNodeVectorMath',230);mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,1,.19 if vertical else 1)
 no=node('ShaderNodeTexNoise',460);no.inputs['Scale'].default_value=scale;no.inputs['Detail'].default_value=2;no.inputs['Roughness'].default_value=.62
 ramp=node('ShaderNodeValToRGB',700);r=ramp.color_ramp;r.elements.remove(r.elements[1]);r.elements[0].position=.22
 for pos,k in ((.22,.58),(.43,.84),(.66,1.11),(.83,1.27)):
  e=r.elements[0] if pos==.22 else r.elements.new(pos);e.color=(*(min(.95,c*k) for c in col),1)
 fine=node('ShaderNodeTexNoise',460,-320);fine.inputs['Scale'].default_value=62 if metal else 28;fine.inputs['Detail'].default_value=1.8
 bump=node('ShaderNodeBump',940,-320);bump.inputs['Strength'].default_value=.2 if metal else .32;bump.inputs['Distance'].default_value=relief
 rr=node('ShaderNodeMapRange',700,-320);rr.inputs['To Min'].default_value=max(.25,rough-.14);rr.inputs['To Max'].default_value=min(.98,rough+.11)
 bs=node('ShaderNodeBsdfPrincipled',1190);bs.inputs['Metallic'].default_value=metal;bs.inputs['Specular IOR Level'].default_value=.3
 out=node('ShaderNodeOutputMaterial',1470)
 for a,b in [(geo.outputs['Position'],mapping.inputs[0]),(mapping.outputs[0],no.inputs[0]),(no.outputs['Fac'],ramp.inputs[0]),(geo.outputs['Position'],fine.inputs[0]),(fine.outputs['Fac'],rr.inputs[0]),(fine.outputs['Fac'],bump.inputs['Height']),(ramp.outputs[0],bs.inputs['Base Color']),(rr.outputs[0],bs.inputs['Roughness']),(bump.outputs[0],bs.inputs['Normal']),(bs.outputs[0],out.inputs[0])]:nt.links.new(a,b)
 return m
def old(name,col,**kw):return surface(name,col,existing=bpy.data.materials['RFX | '+name],**kw)
steel=old('Charcoal coated steel',(.048,.060,.066),rough=.56,metal=.65,relief=.001)
blue=old('Faded slate cobalt',(.082,.126,.158),rough=.68,metal=.3,vertical=True)
zinc=old('Dusty galvanized duct',(.27,.285,.258),rough=.57,metal=.6,scale=2,relief=.0009,vertical=True)
concrete=old('Weathered warm mineral concrete',(.28,.24,.183),rough=.88,scale=1.35,relief=.006,vertical=True)
patch=old('Repair panel mineral',(.19,.18,.148),rough=.93,scale=1.2,relief=.005)
ochre=old('Worn ochre safety enamel',(.56,.325,.055),rough=.69,metal=.15,relief=.001)
dark=old('Recess and rubber',(.013,.018,.02),rough=.95,relief=.0005)
rust=old('Local oxidation',(.185,.073,.023),rough=.93,relief=.002)
bare=surface('Exposed brushed edge metal',(.29,.33,.32),rough=.43,metal=.78,relief=.0005)
blade=surface('Louvre folded blue grey metal',(.125,.18,.20),rough=.53,metal=.55,relief=.0008)
cream=surface('Worn warm ivory stencil',(.61,.565,.415),rough=.85,scale=14,relief=.0003)
shadow=surface('Joint sealant',(.024,.021,.017),rough=.96,relief=.0004)
soot=surface('Mineral runoff',(.113,.098,.068),rough=.96,relief=.002)

def decal(name,side,pts,d,ma):
 o=mesh(name,[P(side,u,d,z) for u,z in pts],[tuple(range(len(pts)))],ma);o['intentional_surface_overlay']=True;return o
def label(name,body,side,u,d,z,size,ma=cream):
 cu=bpy.data.curves.new('RFS | '+name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.00025;cu.space_character=1.13
 o=bpy.data.objects.new(cu.name,cu);coll.objects.link(o);o.location=P(side,u,d,z)
 # Text local +Z points out of wall, local +Y points up.
 right=Vector((0,1,0) if side=='W' else (0,-1,0) if side=='E' else (1,0,0) if side=='S' else (-1,0,0));up=Vector((0,0,1));normal=right.cross(up)
 o.rotation_euler=Matrix((right,up,normal)).transposed().to_euler();cu.materials.append(ma);return o
def bolt(side,u,d,z,r=.025):
 return cyl('Finish hex fixing',P(side,u,d-.007,z),P(side,u,d+.02,z),r,bare,6)
def chips(side,u,d,z,w,h,count,ma=rust):
 # Purposeful edge-localised chips, not an all-over camouflage texture.
 for j in range(count):
  a=u+rng.uniform(-w*.48,w*.48);b=z+rng.uniform(-h*.48,h*.48);ww=rng.uniform(.018,.067);hh=rng.uniform(.025,.115)
  pts=[(a-ww,b-hh*.22),(a-ww*.45,b-hh*.52),(a+ww*.6,b-hh*.39),(a+ww,b+hh*.12),(a+ww*.2,b+hh*.47),(a-ww*.52,b+hh*.28)]
  decal('Edge paint loss',side,pts,d,ma)
def vent_finish(side,u,z,w,h,number):
 # Recessed gasket, two serviceable louvre bays, folded lips and fasteners.
 for du in (-w/2,w/2):
  wb('Vent dark face gasket',side,u+du,.611,z,.115,.023,h+.18,dark,.004)
  wb('Vent bolted outer face',side,u+du,.632,z,.088,.025,h+.12,blue,.004)
  for zz in (-h*.39,0,h*.39):bolt(side,u+du,.65,z+zz)
 wb('Vent centre mullion',side,u,.61,z,.085,.10,h,blue,.008)
 for dz in (-h/2,h/2):
  wb('Vent folded face cap',side,u,.65,z+dz,w+.20,.105,.09,blue,.01)
  wb('Vent exposed fold edge',side,u,.709,z+dz+.026,w+.15,.014,.018,bare,.003)
 for k in range(8):
  zz=z-h*.43+k*h*.123
  wb('Louvre polished leading lip',side,u,.594,zz+.065,w-.18,.025,.025,bare,.004)
 wb('Vent identification plaque',side,u-w*.29,.72,z-h/2-.005,.66,.016,.085,dark,.003)
 label('Vent asset code','EX-'+number+' / FILTER',side,u-w*.29,.732,z-h/2,.055)
 for du in (-w/2,w/2):chips(side,u+du,.649,z,.075,h,6)
 # Narrow tapered drips start at fixings, not in the middle of clean panels.
 for du in (-w*.42,w*.42):
  a=u+du;decal('Vent runoff tail',side,[(a-.026,z-h/2-.1),(a+.03,z-h/2-.1),(a+.01,z-h/2-.51),(a-.006,z-h/2-.66)],.007,soot)
 wb('Service warning backing',side,u-w*.5-.22,.023,z,.21,.024,.26,ochre,.012)
 label('Service caution','!',side,u-w*.5-.22,.039,z,.19,dark)

# Existing metal panels need deliberate face separation, not a single solid colour.
for o in list(bpy.data.objects):
 if not o.name.startswith('RFX |'):continue
 if o.name.startswith(('RFX | Vent projecting jamb','RFX | Vent folded sill')):o.data.materials[0]=blue
 elif o.name.startswith('RFX | Angled louvre blade'):o.data.materials[0]=blade
 elif o.name.startswith('RFX | Localized joint oxidation'):o.hide_render=True;o.hide_viewport=True

vent_finish('E',-13.8,2.85,2.55,1.15,'02')

# Entry-side authored wall panel joints and repairs. No geometry crosses the door.
for u in (-23.55,-21.55,-16.05,-14.95,-12.45,-11.15,-9.6):
 wb('Entry wall recessed vertical joint','E',u,.004,1.88,.018,.008,3.35,shadow,.002)
 for z in (1.05,2.1):
  length=.88 if u>-17 else .72
  wb('Entry wall horizontal panel joint','E',u+.46,.006,z,length,.009,.016,shadow,.002)
for u in (-23.8,-20.4,-16.4,-11,-9.5):
 decal('Lower wall worn mineral repair','E',[(u-.22,.14),(u+.3,.14),(u+.26,.4),(u+.18,.42),(u+.12,.59),(u-.16,.56),(u-.21,.36)],.012,patch)
for u in (-24,-20.6,-16.9,-9.15):
 chips('E',u,.231,1.8,.21,2.5,13,rust)
 chips('E',u-.095,.233,2.3,.012,3.0,7,bare)
label('Personnel wayfinding','REFINING / 02','E',-18.4,.015,2.72,.22)
label('Entry instruction','PERSONNEL ACCESS','E',-18.4,.016,2.48,.105)
label('Service bay number','02','E',-15.85,.016,1.50,.52)
wb('Wall identification rule','E',-15.85,.017,1.15,.75,.01,.025,ochre,.002)
label('Service bay subtitle','EXTRACTION','E',-15.85,.017,1.00,.075)

# Discrete layered cabinet doors, screws, hinges, warning marks and drip caps.
for u in (-22.5,-10.1):
 wb('Cabinet folded drip hood','E',u,.36,1.89,.82,.7,.045,blue,.01)
 for du in (-.31,.31):
  for z in (.60,1.7):bolt('E',u+du,.69,z,.021)
 wb('Cabinet recessed service plate','E',u,.683,1.46,.38,.012,.16,dark,.005)
 label('Cabinet code','PWR / 02','E',u,.695,1.46,.068)
 wb('Cabinet warning enamel','E',u-.13,.686,1.1,.15,.014,.2,ochre,.007)
 label('Electrical caution','!','E',u-.13,.7,1.1,.15,dark)
 chips('E',u,.688,.66,.61,.12,8)

# Ground surface is bounded to the refinery east apron, over measured flat paving.
# 3 mm top, versus the source at -5 mm: no kerb or step is introduced at the door.
paving=[surface('Dust worn paving '+str(i),(.205+i*.01,.17+i*.009,.118+i*.008),rough=.93,scale=1.55,relief=.0035) for i in range(4)]
asphalt=surface('Dark service aggregate',(.056,.054,.045),rough=.93,scale=1.2,relief=.006)
repair=surface('Older concrete infill',(.13,.129,.111),rough=.92,scale=2.4,relief=.004)
def groundpoly(name,pts,z,ma):
 o=mesh(name,[(x,y,z) for x,y in pts],[tuple(range(len(pts)))],ma);o['intentional_surface_overlay']=True;return o
def groundrect(name,x1,x2,y1,y2,z,ma):return groundpoly(name,[(x1,y1),(x2,y1),(x2,y2),(x1,y2)],z,ma)
for ix,(xa,xb) in enumerate(((3.55,4.90),(4.925,6.30))):
 for j in range(8):
  ya=-25.7+j*2.04;yb=min(-9.38,ya+2.017)
  groundrect('Warm apron paving',xa,xb,ya,yb,.003,paving[(ix+2*j)%4])
groundrect('Dark service strip',6.325,8.95,-25.7,-9.38,.003,asphalt)
for x,y,w,h in ((7.5,-22.2,1.3,2.1),(7.2,-14.8,1.0,1.35),(4.45,-24,1.0,.5),(5.2,-16.2,.67,1.1)):
 groundpoly('Uneven old paving repair',[(x-w/2,y-h/2),(x+w*.4,y-h/2),(x+w/2,y-h*.27),(x+w*.45,y+h/2),(x-w*.42,y+h*.47)],.005,repair)
# Slender broken safety stripe follows the existing drain, leaving the entry open.
for j in range(22):
 y=-25.4+j*.71
 if -19.9<y<-16.9:continue
 groundpoly('Worn apron boundary dash',[(3.70,y),(3.78,y+.018),(3.78,y+.34),(3.73,y+.32),(3.70,y+.36)],.008,ochre)
for x,y in ((5.8,-23.4),(4.0,-15.3),(5.8,-11.7)):
 points=[(x-.5,y-.2),(x-.2,y+.05),(x-.11,y+.29),(x+.1,y+.40),(x+.31,y+.74)]
 for (a,b),(c,d) in zip(points,points[1:]):groundpoly('Hairline paving settlement',[(a,b),(a+.009,b),(c+.009,d),(c,d)],.006,shadow)
# Low-profile drain inspection covers, set on the surface rather than protruding props.
for x,y in ((5.6,-21.3),(5.6,-12.6)):
 box('Inset inspection surround',(x,y,.002),(.52,.66,.008),blue,.004)
 box('Inset inspection cover',(x,y,.008),(.45,.59,.008),steel,.004)
 for i in range(7):box('Cover drainage slot',(x,y-.23+i*.075,.013),(.34,.018,.003),dark,.001)

# Preserve every earlier non-refinery object and shared material; validate after cold-open.
report=json.loads((ROOT/'runtime/out/environment/refinery-build/build-verification.json').read_text())
report=dict(before_sha256=before,protected_fingerprints=report['protected_fingerprints'],libraries=report['libraries'],route_samples=report['route_samples'],backup=str(backup),scope='Refinery owned materials, entry vent and paving finish slice',new_objects=[o.name for o in coll.objects])
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY']
assert sha(SRC)==before,'Concurrent main change'
candidate=SRC.with_name('facility_environment.refinery-finish-candidate.blend');bpy.ops.wm.save_as_mainfile(filepath=str(candidate),check_existing=False)
report['candidate']=str(candidate);report['candidate_sha256']=sha(candidate);(OUT/'verification.json').write_text(json.dumps(report,indent=2))
print('FINISH_CANDIDATE_SAVED',report['candidate_sha256'],flush=True)
s.render.filepath=str(OUT/'entry.png');bpy.ops.render.render(write_still=True);print('FINISH_SLICE_RENDERED',flush=True)
