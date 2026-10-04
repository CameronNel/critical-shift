"""Whole-room expansion; executed in the fresh source builder's authored context."""
from mathutils import Matrix
# Preserve each piece's functional geometry while localizing neglect to its handling surfaces.
def stain_material(obj,spots,label,tint=(.26,.22,.12),strength=.65):
 if obj.type!='MESH' or not obj.data.materials:return
 for slot,old in enumerate(list(obj.data.materials)):
  if not old or not old.use_nodes:continue
  m=old.copy();m.name='WS | '+label+' '+str(slot);obj.data.materials[slot]=m;nodes=m.node_tree.nodes;links=m.node_tree.links;b=bsdf(m)
  base=b.inputs['Base Color'].links[0].from_socket if b.inputs['Base Color'].is_linked else None
  if base is None:
   rgb=nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=b.inputs['Base Color'].default_value;base=rgb.outputs[0]
  for centre,scales in spots:
   geom=nodes.new('ShaderNodeNewGeometry');sub=nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=centre;scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=scales;length=nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';fade=nodes.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.12;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=strength;fade.inputs['To Max'].default_value=0;fade.clamp=True;mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(*tint,1);links.new(geom.outputs['Position'],sub.inputs[0]);links.new(sub.outputs['Vector'],scale.inputs[0]);links.new(scale.outputs['Vector'],length.inputs[0]);links.new(length.outputs['Value'],fade.inputs['Value']);links.new(fade.outputs['Result'],mix.inputs[0]);links.new(base,mix.inputs[1]);base=mix.outputs[0]
  links.new(base,b.inputs['Base Color']);b.inputs['Roughness'].default_value=max(.80,b.inputs['Roughness'].default_value)
# Unit-specific corrosion at collars and lower contact bands, not identical global speckle.
for idx,rootname in enumerate(['RA01','RA02','RA03','SC01','SC02']):
 rootobj=bpy.data.objects[rootname];cx,cy=rootobj.matrix_world.translation.xy;shield=rootname.startswith('SC');radius=.5073 if shield else .3827
 for obj in list(rootobj.children_recursive):
  if obj.type!='MESH':continue
  if obj.name.startswith('Continuous inner vessel'):
   stain_material(obj,[((cx+radius,cy+.12,.59),(3,3,3)),((cx+radius,cy-.20,1.52 if shield else .85),(3,5,3)),((cx,cy,.47),(1,1,8))],rootname+' old enamel',(.28,.29,.18),.75)
  elif obj.name.startswith(('Protective forged collar','Collar rolled edge','Carrier bearing','Sealed vessel lower shoulder','Lift eye')):
   stain_material(obj,[((cx,cy,.35),(1,1,5)),((cx+.25,cy-.25,2.09 if shield else 1.08),(2,2,7))],rootname+' oxidized joints',(.33,.19,.08),.73)
# Damp originates at selected panel joints and service drops; quiet wall spans remain quiet.
for name,spots in [('West Wall',[((-6,9.05,3.5),(1,4,.8)),((-6,13.75,1.0),(1,3,1.3)),((-6,6.6,2.7),(1,18,1))]),('East Wall.001',[((6,9.05,3.6),(1,5,.8)),((6,13.75,.60),(1,2,2)),((6,11.2,2.6),(1,16,1))]),('Dispatch wall',[((-4.85,18,2.8),(2,1,.8)),((-3.2,18,.70),(1.5,1,2))]),('Receiving wall',[((-4.3,0,1.2),(1.5,1,1.6))])]:
 stain_material(bpy.data.objects[name],spots,name+' aged concrete',(.29,.40,.26),.72)
# Rust collects on handling equipment, forklift contact areas and the extraction service faces.
for name in ['DR01','DR02','QH01','CT01_TRANSFER_CART','HJ01_HANDLING_JIB','VF01_EXTRACTION']:
 rootobj=bpy.data.objects[name];c=rootobj.matrix_world.translation
 for obj in rootobj.children_recursive:
  if obj.type!='MESH' or not any(t in obj.name.lower() for t in ['wall','corner casting','panel','deck','pedestal','plenum','cassette','motor terminal','rubber push']):continue
  p=obj.matrix_world.translation;stain_material(obj,[((p.x,p.y,p.z-.26),(2,2,5)),((p.x+.17,p.y-.08,p.z+.12),(7,5,8))],name+' working corrosion',(.35,.23,.11),.74)
# Break the original showroom-fresh lane paint while keeping the freight route legible.
for name in ['Cart lane paint','Cart lane paint.001']:bpy.data.objects[name].hide_render=True
for side,x in enumerate([-1.81,1.81]):
 for i in range(72):
  y=.10+i*.246
  if i in ({8,9,21,52,67} if side==0 else {4,18,19,37,63,64}):continue
  length=.244;width=.042+random.random()*.015
  if i%11==3:length*=.42
  verts=[(x-width/2,y,.00018),(x+width/2,y+.003,.00018),(x+width*.40,y+length,.00018),(x-width*.5,y+length-.004,.00018),(x-width*.33,y+length*.56,.00018)];obj=mesh('Worn freight lane '+str(side)+' '+str(i),verts,[(0,1,2,3,4)],original_mats['Ochre safety enamel']);support(obj,'Floor',(x,y+length*.4,.00018))
# Bounded tire contact traces at receiving and rear turning zones; all are flush surface marks.
track=material('Old rubber wheel contact',(.025,.028,.021),.97)
for zone,basey in [('receiving',.7),('dispatch',14.9)]:
 for side in (-1,1):
  for i in range(9):
   y=basey+i*.19;x=side*(.58+.10*math.sin(i*.34));obj=cube(zone+' wheel contact '+str(side)+' '+str(i),(x,y,.00015),(.10,.115,.0003),track);support(obj,'Floor',(x,y,0))
# Residue stays under the storage/service equipment, avoiding arbitrary clutter in the lane.
for idx,(x,y,w,h) in enumerate([(-4.85,8.40,.65,.40),(-5.1,13.0,.70,.48),(-4.75,16.70,.76,.36),(4.88,12.75,.55,.25)]):
 verts=[(x-w*.5,y,.00015),(x-w*.15,y-h*.5,.00015),(x+w*.5,y-h*.3,.00015),(x+w*.35,y+h*.5,.00015),(x-w*.2,y+h*.38,.00015)];obj=mesh('Old contained service residue '+str(idx),verts,[(0,1,2,3,4)],oil);soften_stain(obj,oil);support(obj,'Floor',(x,y,.00015))
# A used securing strap belongs on the parked cart, not in its travel lane.
cartdeck=bpy.data.objects['Folded load deck'];carttop=max((cartdeck.matrix_world@Vector(v)).z for v in cartdeck.bound_box)
verts=[];segments=48
for i in range(segments):
 a=i*2*math.pi/20;r=.025+i*.00065
 for rad,z in [(r-.001,carttop),(r+.001,carttop),(r+.001,carttop+.023),(r-.001,carttop+.023)]:verts.append((3.69+rad*math.cos(a),3.72+rad*math.sin(a),z))
faces=[]
for i in range(segments-1):
 for j in range(4):faces.append((i*4+j,(i+1)*4+j,(i+1)*4+(j+1)%4,i*4+(j+1)%4))
faces.extend([tuple(range(4)),tuple(reversed(range((segments-1)*4,segments*4)))]);obj=mesh('Discarded cart securing strap coil',verts,faces,cloth);support(obj,cartdeck.name,verts[0]);
# Inventory desk: a stained logbook, abandoned shift note, and folded photograph clipped to the housing.
desk=bpy.data.objects['Steel desk top'];desktop=max((desk.matrix_world@Vector(v)).z for v in desk.bound_box)
stain_material(desk,[((-3.60,1.12,desktop),(4,5,1)),((-4.20,2.16,desktop),(4,3,1))],'Inventory handled desk',(.3,.31,.22),.68)
obj=cube('Inventory abandoned shift note',(-4.35,1.79,desktop+.0005),(.22,.15,.001),paper);support(obj,desk.name,(-4.35,1.79,desktop));note=obj
obj=text('Inventory shift note printing','NO RELIEF\nSHIFT 06',(-4.35,1.78,desktop+.0011),.018,ink);intrinsic(obj,note,'Ink printed on paper')
# A small cracked photo on a supported tabletop easel, with abstract faded silhouettes.
base=cube('Family photo easel foot',(-4.36,1.95,desktop+.005),(.07,.14,.010),original_mats['Structural warm graphite'],.001);support(base,desk.name,(-4.36,1.95,desktop))
frame=cube('Worn photo frame',(-4.36,1.95,desktop+.095),(.014,.14,.17),original_mats['Oxide painted steel'],.001);intrinsic(frame,base,'Frame supported by easel foot and hinge')
imageface=cube('Faded family photo paper',(-4.352,1.95,desktop+.095),(.001,.12,.15),paper);intrinsic(imageface,base,'Paper held in frame rabbet')
for i,(y,z,r) in enumerate([(1.923,desktop+.12,.014),(1.967,desktop+.112,.013)]):
 obj=cyl('Faded photo figure '+str(i),(-4.3513,y,z),r,.0002,ink,16);obj.rotation_euler=(0,math.pi/2,0);intrinsic(obj,base,'Faded printed photograph silhouettes')
 obj=cube('Faded photo torso '+str(i),(-4.3513,y,z-.027),(.0002,.026,.038),ink,.002);intrinsic(obj,base,'Printed silhouette on photograph')
# A damaged maintenance note belongs to the extractor's actual service cassette.
cassette=bpy.data.objects['Removable filter cassette.001'];front=min((cassette.matrix_world@Vector(v)).y for v in cassette.bound_box)
obj=cube('Extractor overdue service tag',(-4.32,front-.0015,1.01),(.20,.003,.11),paper);support(obj,cassette.name,(-4.32,front,1.01),(0,1,0));tag=obj
obj=text('Extractor service tag printing','FILTER 06\nOVERDUE',(-4.32,front-.0031,1.024),.018,ink,(math.pi/2,0,0));intrinsic(obj,tag,'Printed service label')
# Rust masks and paint keep original identity/control lettering intact; no new wall slogans.

# Object-specific layered paint failure: broad aged enamel, torn oxide islands and small pits.
def aged_finish(obj,paint,seed,lower=False,amount=.50):
 if obj.type!='MESH':return
 m=material(obj.name+' aged finish',paint,.82,.12);obj.data.materials.clear();obj.data.materials.append(m)
 ns=m.node_tree.nodes;ls=m.node_tree.links;shader=bsdf(m)
 geo=ns.new('ShaderNodeNewGeometry');coord=ns.new('ShaderNodeVectorMath');coord.operation='ADD';coord.inputs[1].default_value=(seed*1.73,seed*3.13,seed*.71);ls.new(geo.outputs['Position'],coord.inputs[0])
 broad=ns.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=4.8;broad.inputs['Detail'].default_value=2;ls.new(coord.outputs['Vector'],broad.inputs['Vector'])
 fine=ns.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=33;fine.inputs['Detail'].default_value=1;ls.new(coord.outputs['Vector'],fine.inputs['Vector'])
 mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';ls.new(broad.outputs['Fac'],mul.inputs[0]);ls.new(fine.outputs['Fac'],mul.inputs[1])
 ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.17;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.32-amount*.045;ramp.color_ramp.elements[1].color=(1,1,1,1);ls.new(mul.outputs[0],ramp.inputs[0])
 mask=ramp.outputs['Color']
 if lower:
  split=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],split.inputs[0]);height=ns.new('ShaderNodeMapRange');height.inputs['From Min'].default_value=.42;height.inputs['From Max'].default_value=1.02;height.inputs['To Min'].default_value=1;height.inputs['To Max'].default_value=.12;height.clamp=True;ls.new(split.outputs['Z'],height.inputs['Value']);mul2=ns.new('ShaderNodeMath');mul2.operation='MULTIPLY';ls.new(mask,mul2.inputs[0]);ls.new(height.outputs['Result'],mul2.inputs[1]);mask=mul2.outputs[0]
 mix=ns.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*paint,1);mix.inputs[2].default_value=(.155,.071,.027,1);ls.new(mask,mix.inputs[0]);ls.new(mix.outputs[0],shader.inputs['Base Color'])
 rough=ns.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.62;rough.inputs['To Max'].default_value=.96;ls.new(mask,rough.inputs['Value']);ls.new(rough.outputs[0],shader.inputs['Roughness'])
 bump=ns.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0007;bump.inputs['Strength'].default_value=.24;ls.new(mask,bump.inputs['Height']);ls.new(bump.outputs[0],shader.inputs['Normal'])
for i,rootname in enumerate(['RA01','RA02','RA03','SC01','SC02']):
 colors=[(.26,.225,.16),(.18,.23,.20),(.27,.26,.21),(.30,.30,.245),(.16,.20,.225)]
 rootobj=bpy.data.objects[rootname]
 for obj in rootobj.children_recursive:
  if obj.type!='MESH':continue
  if obj.name.startswith('Continuous inner vessel'):aged_finish(obj,colors[i],i+1,True,.65)
  elif obj.name.startswith(('Protective forged collar','Carrier bearing plate')):aged_finish(obj,(.17,.18,.155),i+10,False,.26)
# Localized patch histories on container walls and lids, not a shared uniform finish.
for i,rootname in enumerate(['DR01','DR02','QH01']):
 for obj in bpy.data.objects[rootname].children_recursive:
  if obj.type=='MESH' and obj.name.startswith(('Folded sidewall','Folded lid','Sealed end panel')):aged_finish(obj,[(.19,.22,.195),(.27,.255,.18),(.19,.155,.125)][i],i+30,obj.name.startswith('Folded sidewall'),.45)
# Forklift-worn cell faces carry different exposure histories at the bottom, not random high-wall clutter.
for i in range(8):
 suffix='' if i==0 else '.'+str(i).zfill(3);o=bpy.data.objects['Cell transverse concrete separator'+suffix];p=o.matrix_world.translation
 stain_material(o,[((p.x+(.65 if i%2 else -.42),p.y,.26),(1.0,1,2.7)),((p.x+1.3,p.y,.67),(2.0,1,2.1))],'Cell '+str(i)+' old handling grime',(.16,.23,.15),.94)
# The booth's original working task lamp is a modeled diffuser with a seated power source.
lens=bpy.data.objects['Task diffuser'];lm=material('Inventory aged fluorescent glass',(.40,.46,.39),.60);b=bsdf(lm);b.inputs['Emission Color'].default_value=(.75,.82,.68,1);b.inputs['Emission Strength'].default_value=.6;lens.data=lens.data.copy();lens.data.materials.clear();lens.data.materials.append(lm)
data=bpy.data.lights.new('WS | Inventory task tube emitter','AREA');data.energy=4;data.shape='RECTANGLE';data.size=.07;data.size_y=.14;data.color=(.75,.82,.68);o=bpy.data.objects.new(data.name,data);added.objects.link(o);o.location=lens.matrix_world.translation+Vector((.105,0,-.007));o.rotation_euler=(0,0,0);o['physical_lens']=lens.name;o['failed_fixture']=False;lens['light_source']=o.name;intrinsic(o,bpy.data.objects['Task lamp hood'],'Emitter seated below the original modeled tube');fixture_pairs.append(dict(source=o.name,lens=lens.name,energy=data.energy,emission=.6,failed=False))
for name in ['Keycap.007','Keycap.019','Keycap.032']:bpy.data.objects[name].hide_render=True
# Three actual small weatherproof portal fixtures; wall brackets, pressed hoods and glass bottoms.
for label,pos,target,anchor,direction,watts in [
 ('Receiving',(1.93,.112,3.43),'Receiving wall.001',(1.93,0,3.43),(0,-1,0),22),
 ('Dispatch',(1.55,17.888,3.12),'Dispatch wall.001',(1.55,18,3.12),(0,1,0),20),
 ('Personnel',(5.75,2.4,2.65),'Personnel lintel',(6,2.4,2.65),(1,0,0),15)]:
 x,y,z=pos;dims=(.30,.224,.13) if label!='Personnel' else (.50,.30,.13)
 housing=cube(label+' corroded bulkhead hood',pos,dims,original_mats['Structural warm graphite'],.003);support(housing,target,anchor,direction)
 lx=x-.17 if label=='Personnel' else x
 lens=cube(label+' bulkhead glass',(lx,y,z-.069),(.25,.14,.006) if label!='Personnel' else (.14,.25,.006),lm,.001);intrinsic(lens,housing,'Gasketed lamp lens held by the folded hood')
 data=bpy.data.lights.new('WS | '+label+' bulkhead emitter','AREA');data.energy=watts;data.shape='RECTANGLE';data.size=.24 if label!='Personnel' else .13;data.size_y=.13 if label!='Personnel' else .24;data.color=(.79,.82,.68);o=bpy.data.objects.new(data.name,data);added.objects.link(o);o.location=(lx,y,z-.074);o.rotation_euler=(0,0,0);intrinsic(o,housing,'Emitter seated 2mm outside the physical glass');o['physical_lens']=lens.name;o['failed_fixture']=False;lens['light_source']=o.name;fixture_pairs.append(dict(source=o.name,lens=lens.name,energy=watts,emission=.6,failed=False))
# A flush replacement patch with real corner fasteners on the dry cell's much-handled front.
obj=cube('Dry store riveted repair patch',(4.45,5.9266,.53),(.34,.003,.28),edge,.001);support(obj,'Folded sidewall',(4.45,5.9284,.53),(0,1,0));patch=obj
for i,(x,z) in enumerate([(4.30,.41),(4.60,.41),(4.30,.65),(4.60,.65)]):
 o=cyl('Dry patch captive rivet '+str(i),(x,5.9236,z),.008,.003,original_mats['Structural warm graphite'],8);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,patch,'Captive patch fastener')
# Broad extractor service staining around the removable cassette's seams.
for i,name in enumerate(['Removable filter cassette','Removable filter cassette.001','Connected filter plenum']):aged_finish(bpy.data.objects[name],(.21,.24,.205),60+i,True,.45)
