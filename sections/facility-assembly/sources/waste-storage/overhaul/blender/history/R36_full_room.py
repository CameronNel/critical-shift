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
lane_mat=material('Nearly erased ochre route paint',(.16,.145,.074),.97)
for side,x in enumerate([-1.81,1.81]):
 for i in range(72):
  y=.10+i*.246
  if i in ({8,9,21,52,67} if side==0 else {4,18,19,37,63,64}) or (13<i<57 and (i+side*3)%9 in [0,1,2,3]):continue
  length=.244;width=.042+random.random()*.015
  if i%11==3:length*=.42
  verts=[(x-width/2,y,.00018),(x+width/2,y+.003,.00018),(x+width*.40,y+length,.00018),(x-width*.5,y+length-.004,.00018),(x-width*.33,y+length*.56,.00018)];obj=mesh('Worn freight lane '+str(side)+' '+str(i),verts,[(0,1,2,3,4)],lane_mat);support(obj,'Floor',(x,y+length*.4,.00018))
# Curved tire rubs follow the turn at each handoff, rather than a dotted texture.
track=material('Old rubber wheel contact',(.024,.027,.020),.98)
for zone,basey in [('receiving',2.30),('dispatch',15.95)]:
 for side in (-1,1):
  verts=[];N=48
  for j in range(N):
   a=-.90+j*1.8/(N-1);radius=.91 if side==-1 else 1.21
   for dr in [-.026,.026]:verts.append((side*.19+(radius+dr)*math.cos(a),basey+(radius+dr)*math.sin(a),.00013))
  faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(N-1)];obj=mesh(zone+' curved old tire rub '+str(side),verts,faces,oil);attr=obj.data.attributes.new('WS_Damp_Mask','FLOAT','POINT')
  for j,v in enumerate(attr.data):v.value=.37*max(0,math.sin(math.pi*(j//2)/(N-1)))**.5*(.65+.35*math.sin(j*.44)**2)
  support(obj,'Floor',verts[N])
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
 m=material(obj.name+' aged finish',paint,.82,.05);obj.data.materials.clear();obj.data.materials.append(m)
 ns=m.node_tree.nodes;ls=m.node_tree.links;shader=bsdf(m)
 geo=ns.new('ShaderNodeNewGeometry');coord=ns.new('ShaderNodeVectorMath');coord.operation='ADD';coord.inputs[1].default_value=(seed*1.73,seed*3.13,seed*.71);ls.new(geo.outputs['Position'],coord.inputs[0])
 broad=ns.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=4.8;broad.inputs['Detail'].default_value=2;ls.new(coord.outputs['Vector'],broad.inputs['Vector'])
 fine=ns.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=33;fine.inputs['Detail'].default_value=1;ls.new(coord.outputs['Vector'],fine.inputs['Vector'])
 mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';ls.new(broad.outputs['Fac'],mul.inputs[0]);ls.new(fine.outputs['Fac'],mul.inputs[1])
 ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.27;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.43-amount*.025;ramp.color_ramp.elements[1].color=(1,1,1,1);ls.new(mul.outputs[0],ramp.inputs[0])
 mask=ramp.outputs['Color']
 if lower:
  split=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],split.inputs[0]);height=ns.new('ShaderNodeMapRange');vessel=obj.name.startswith('Continuous inner vessel');height.inputs['From Min'].default_value=.52 if vessel else .42;height.inputs['From Max'].default_value=.74 if vessel else 1.02;height.inputs['To Min'].default_value=1;height.inputs['To Max'].default_value=.025;height.clamp=True;ls.new(split.outputs['Z'],height.inputs['Value']);mul2=ns.new('ShaderNodeMath');mul2.operation='MULTIPLY';ls.new(mask,mul2.inputs[0]);ls.new(height.outputs['Result'],mul2.inputs[1]);mask=mul2.outputs[0]
 # The two long dimensions locate actual panel rims; thin face depth is excluded.
 if not obj.name.startswith('Continuous inner vessel'):
  localspan=[max(v[i] for v in obj.bound_box)-min(v[i] for v in obj.bound_box) for i in range(3)]
  # Generated coordinates are normalized within the actual mesh, independent of the assembly pose.
  axes=[2] if obj.name.startswith('Protective forged collar') else sorted(range(3),key=lambda i:obj.dimensions[i],reverse=True)[:2]
  tex=ns.new('ShaderNodeTexCoord');split=ns.new('ShaderNodeSeparateXYZ');ls.new(tex.outputs['Generated'],split.inputs[0]);edge_masks=[]
  for axis in axes:
   physical_span=max(localspan[axis]*abs(obj.scale[axis]),.026)
   sub=ns.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5;ls.new(split.outputs[axis],sub.inputs[0]);absolute=ns.new('ShaderNodeMath');absolute.operation='ABSOLUTE';ls.new(sub.outputs[0],absolute.inputs[0]);edgefade=ns.new('ShaderNodeMapRange');edgefade.inputs['From Min'].default_value=.5-.012/physical_span;edgefade.inputs['From Max'].default_value=.5-.002/physical_span;edgefade.clamp=True;ls.new(absolute.outputs[0],edgefade.inputs['Value']);edge_masks.append(edgefade.outputs[0])
  maximum=ns.new('ShaderNodeMath');maximum.operation='MAXIMUM';ls.new(edge_masks[0],maximum.inputs[0]);ls.new(edge_masks[-1],maximum.inputs[1]);gated=ns.new('ShaderNodeMath');gated.operation='MULTIPLY';ls.new(mask,gated.inputs[0]);ls.new(maximum.outputs[0],gated.inputs[1]);mask=gated.outputs[0]
  if obj.name.startswith('Folded lid'):
   # Oxidation belongs to a few retaining-shoe and hinge contacts, not every rim equally.
   weights=[.95,.35,.70,0] if seed%2==0 else [.55,.85,0,.40]
   centres=[(.025,.025),(.975,.025),(.025,.975),(.975,.975),(.99,.28),(.99,.72)]
   regions=[]
   for index,(u,v) in enumerate(centres):
    sub=ns.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(u,v,.5);scale=ns.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(localspan[0]*abs(obj.scale[0])/.13,localspan[1]*abs(obj.scale[1])/.13,0);length=ns.new('ShaderNodeVectorMath');length.operation='LENGTH';fade=ns.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.68;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=weights[index] if index<4 else .65;fade.inputs['To Max'].default_value=0;fade.clamp=True;ls.new(tex.outputs['Generated'],sub.inputs[0]);ls.new(sub.outputs['Vector'],scale.inputs[0]);ls.new(scale.outputs['Vector'],length.inputs[0]);ls.new(length.outputs['Value'],fade.inputs[0]);regions.append(fade.outputs[0])
   region=regions[0]
   for other in regions[1:]:
    maximum=ns.new('ShaderNodeMath');maximum.operation='MAXIMUM';ls.new(region,maximum.inputs[0]);ls.new(other,maximum.inputs[1]);region=maximum.outputs[0]
   localized=ns.new('ShaderNodeMath');localized.operation='MULTIPLY';ls.new(mask,localized.inputs[0]);ls.new(region,localized.inputs[1]);mask=localized.outputs[0]
 else:
  # One old condensation/contact run on each vessel replaces the broad lower speckle band.
  centre=obj.parent.matrix_world.translation;radius=.50 if obj.parent.name.startswith('SC') else .37
  sub=ns.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(centre.x+radius,centre.y+(.16 if seed%2 else -.13),.47);scale=ns.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(5,12,2.6);length=ns.new('ShaderNodeVectorMath');length.operation='LENGTH';fade=ns.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.58;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;fade.clamp=True;ls.new(geo.outputs['Position'],sub.inputs[0]);ls.new(sub.outputs['Vector'],scale.inputs[0]);ls.new(scale.outputs['Vector'],length.inputs[0]);ls.new(length.outputs['Value'],fade.inputs[0]);localized=ns.new('ShaderNodeMath');localized.operation='MULTIPLY';ls.new(mask,localized.inputs[0]);ls.new(fade.outputs[0],localized.inputs[1]);mask=localized.outputs[0]
 mix=ns.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*paint,1);mix.inputs[2].default_value=(.065,.032,.013,1);ls.new(mask,mix.inputs[0]);ls.new(mix.outputs[0],shader.inputs['Base Color'])
 # Quiet broad coating fade differs from sharp losses at handling/contact zones.
 fade_noise=ns.new('ShaderNodeTexNoise');fade_noise.inputs['Scale'].default_value=1.1;fade_noise.inputs['Detail'].default_value=1;ls.new(coord.outputs['Vector'],fade_noise.inputs['Vector']);fade_ramp=ns.new('ShaderNodeValToRGB');fade_ramp.color_ramp.elements[0].position=.20;fade_ramp.color_ramp.elements[0].color=(*(c*.86 for c in paint),1);fade_ramp.color_ramp.elements[1].position=.80;fade_ramp.color_ramp.elements[1].color=(*(c*1.07 for c in paint),1);ls.new(fade_noise.outputs['Fac'],fade_ramp.inputs[0]);ls.new(fade_ramp.outputs['Color'],mix.inputs[1])
 rough=ns.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.78;rough.inputs['To Max'].default_value=.96;ls.new(mask,rough.inputs['Value']);ls.new(rough.outputs[0],shader.inputs['Roughness'])
 bump=ns.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0007;bump.inputs['Strength'].default_value=.24;ls.new(mask,bump.inputs['Height']);ls.new(bump.outputs[0],shader.inputs['Normal'])
for i,rootname in enumerate(['RA01','RA02','RA03','SC01','SC02']):
 colors=[(.13,.16,.135),(.175,.195,.17),(.23,.175,.105),(.23,.255,.21),(.095,.145,.165)]
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
data=bpy.data.lights.new('WS | Inventory task tube emitter','AREA');data.energy=4;data.shape='RECTANGLE';data.size=.03;data.size_y=.28;data.color=(.75,.82,.68);o=bpy.data.objects.new(data.name,data);added.objects.link(o);o.location=lens.matrix_world.translation+Vector((.060,0,-.007));o.rotation_euler=(0,0,0);o['physical_lens']=lens.name;o['failed_fixture']=False;lens['light_source']=o.name;intrinsic(o,bpy.data.objects['Task lamp hood'],'Emitter seated below the original modeled tube');fixture_pairs.append(dict(source=o.name,lens=lens.name,energy=data.energy,emission=.6,failed=False))
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

# The large storage covers are formed caps, with a shallow pressed panel and a real hollow return.
for name in ['Folded lid','Folded lid.001','Folded lid.002']:
 obj=bpy.data.objects[name];bbox=[Vector(p) for p in obj.bound_box];lo=Vector([min(p[i] for p in bbox) for i in range(3)]);hi=Vector([max(p[i] for p in bbox) for i in range(3)]);span=hi-lo
 outline=[(.025,0),(.975,0),(1,.045),(1,.955),(.975,1),(.025,1),(0,.955),(0,.045)]
 rings=[(.027,.48),(0,1.0),(0,0),(.006,0),(.006,.94),(.027,.40)];verts=[]
 for inset,z in rings:
  for u,v in outline:verts.append(obj.matrix_world@(lo+Vector(((inset+u*(1-2*inset))*span.x,(inset+v*(1-2*inset))*span.y,z*span.z))))
 caps=[tuple(range(8)),tuple(reversed(range(40,48)))]
 if name=='Folded lid.001':
  for ring in [0,40]:
   centre=sum((Vector(v) for v in verts[ring:ring+8]),Vector())/8;centre.z-=.012;verts.append(centre)
  caps=[(i,(i+1)%8,48) for i in range(8)]+[(40+(i+1)%8,40+i,49) for i in range(8)]
 faces=caps+[(r*8+i,(r+1)*8+i,(r+1)*8+(i+1)%8,r*8+(i+1)%8) for r in range(5) for i in range(8)]
 mat=obj.data.materials[0];remesh(name,verts,faces,mat)
# A spent pleated filter stands entirely within the open quarantine tub's closure envelope.
x,y,z=4.65,11.15,.300;N=48;verts=[]
for radius,height in [(.15,z),(.15,z+.76),(.07,z+.76),(.07,z)]:
 for i in range(N):
  a=i*2*math.pi/N;r=radius+(.009 if radius>.1 and i%2==0 else 0);verts.append((x+r*math.cos(a),y+r*math.sin(a),height))
faces=[(r*N+i,r*N+(i+1)%N,((r+1)%4)*N+(i+1)%N,((r+1)%4)*N+i) for r in range(4) for i in range(N)]
obj=mesh('Quarantined spent pleated filter',verts,faces,cloth);support(obj,'Tub floor.002',(x+.15,y,z));aged_finish(obj,(.30,.27,.17),81,True,.55)
for height,label in [(z+.015,'lower'),(z+.745,'upper')]:
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(x,y,height),major_radius=.148,minor_radius=.009);o=bpy.context.object;o.name='WS | Filter '+label+' crimp';finish(o,original_mats['Oxide painted steel']);intrinsic(o,obj,'Rolled metal end binding of the spent cartridge')
# Grease and condensation explain the booth's quiet wall areas.
stain_material(bpy.data.objects['West Wall'],[((-6,1.4,2.5),(1,8,.8)),((-6,2.0,.40),(1,1.2,2.2))],'Inventory old condensation',(.20,.30,.21),.86)
# An exhausted blister pack is a small personal trace beside the shift paperwork.
desk=bpy.data.objects['Steel desk top'];foot=cube('Empty medication foil',(-3.83,1.89,desktop+.0006),(.062,.12,.0012),edge,.001);support(foot,desk.name,(-3.83,1.89,desktop))
for i in range(6):
 px=-3.845+(i%2)*.029;py=1.85+(i//2)*.035
 o=cyl('Collapsed empty blister '+str(i),(px,py,desktop+.0025),.009,.003,original_mats['Structural warm graphite'],12);intrinsic(o,foot,'Crushed blister pocket on used foil')
# Structural pass: different waste functions have different containment construction.
# The dry cells use pressed sheet skins in open rolled channels; quarantine uses broader
# horizontal folded panels. All stay inside the original separators' X/Y reservations.
import bmesh
def outward_mesh(obj):
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
def prism_points(poly,axis,start,end):
 verts=[]
 for value in [start,end]:
  for a,b in poly:
   verts.append((value,a,b) if axis=='X' else ((a,value,b) if axis=='Y' else (a,b,value)))
 n=len(poly);faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return verts,faces
for idx in [4,5,6,7]:
 suffix='.'+str(idx).zfill(3);name='Cell transverse concrete separator'+suffix;wall=bpy.data.objects[name];cy=wall.matrix_world.translation.y
 if idx in [4,5]:
  profile=[];steps=28
  for i in range(steps+1):
   x=2.15+3.85*i/steps;y=cy-.062+(.027 if i%4 in [1,2] else 0);profile.append((x,y))
  profile+=list(reversed([(x,y+.004) for x,y in profile]));verts,faces=prism_points(profile,'Z',0,1.10)
 else:
  verts=[];faces=[]
  for xa,xb in [(2.15,4.04),(4.11,6.0)]:
   profile=[]
   for i in range(13):
    z=i*1.1/12;y=cy-.057+(.024 if i%4 in [1,2] else 0);profile.append((y,z))
   profile+=list(reversed([(y+.004,z) for y,z in profile]));v,f=prism_points(profile,'X',xa,xb);offset=len(verts);verts+=v;faces += [tuple(j+offset for j in face) for face in f]
 wall=remesh(name,verts,faces,original_mats['Galvanized bus casing']);outward_mesh(wall);support(wall,'Floor',verts[0]);wall['construction']='Pressed folded containment skins inside original bay boundary'
 aged_finish(wall,(.135,.19,.19) if idx in [4,5] else (.105,.135,.13),idx+100,False,.35)
 posts=[]
 for j,cx in enumerate([2.25,4.075,5.90]):
  section=[(cx-.04,cy-.075),(cx+.04,cy-.075),(cx+.04,cy+.075),(cx+.035,cy+.075),(cx+.035,cy-.069),(cx-.035,cy-.069),(cx-.035,cy+.075),(cx-.04,cy+.075)]
  v,f=prism_points(section,'Z',0,1.136);o=mesh('Cell '+str(idx)+' rolled channel '+str(j),v,f,original_mats['Structural warm graphite']);outward_mesh(o);support(o,'Floor',(cx,cy-.072,0));posts.append(o)
 capname='Cell impact coping'+suffix;cap=bpy.data.objects[capname]
 section=[(cy-.115,1.10),(cy-.111,1.10),(cy-.111,1.136),(cy+.111,1.136),(cy+.111,1.10),(cy+.115,1.10),(cy+.115,1.14),(cy-.115,1.14)]
 v,f=prism_points(section,'X',2.15,6.0);cap=remesh(capname,v,f,steel);outward_mesh(cap);support(cap,posts[1].name,(4.075,cy-.072,1.136))
 # Real diagonal tie plates brace quarantine's two wide panels.
 if idx in [6,7]:
  for j,(xa,xb) in enumerate([(2.32,3.94),(4.20,5.81)]):
   y=cy-.063;v=[(xa,y,.22),(xa+.025,y,.21),(xb,y,.95),(xb-.025,y,.96)];o=mesh('Quarantine bracing strap '+str(idx)+' '+str(j),v,[(0,1,2,3)],original_mats['Structural warm graphite']);intrinsic(o,wall,'Welded tie strap against folded containment panel')
# One impact crack stays in the original safety pane; it does not invent missing glazing.
glass=bpy.data.objects['Booth window glass'];crackmat=material('Old safety glass fracture',(.19,.235,.21),.83)
paths=[[(1.15,1.48),(1.03,1.64),(.93,1.91),(.75,2.06)],[(1.15,1.48),(1.28,1.70),(1.42,1.87)],[(1.15,1.48),(1.34,1.39),(1.51,1.18)],[(1.15,1.48),(.99,1.27),(.92,1.09)],[(1.03,1.64),(.85,1.71)],[(1.28,1.70),(1.49,1.74)]]
verts=[];faces=[]
for path in paths:
 for (y0,z0),(y1,z1) in zip(path,path[1:]):
  dy,dz=y1-y0,z1-z0;length=math.hypot(dy,dz);oy=-dz/length*.00045;oz=dy/length*.00045;offset=len(verts);verts += [(-2.3918,y0+oy,z0+oz),(-2.3918,y1+oy,z1+oz),(-2.3918,y1-oy,z1-oz),(-2.3918,y0-oy,z0-oz)];faces.append(tuple(range(offset,offset+4)))
o=mesh('Booth old laminated pane impact fracture',verts,faces,crackmat);support(o,glass.name,verts[0],(-1,0,0))

# One closed filter overpack is seated between the cart's existing restraint dogs.
# It gives the receiving-to-storage handoff a readable carried load, without lane clutter.
saddle=bpy.data.objects['Load saddle'];cz=max((saddle.matrix_world@Vector(v)).z for v in saddle.bound_box);cx,cy=3.4,3.82;N=24;verts=[]
profile=[(.225,cz),(.225,cz+.03),(.208,cz+.065),(.208,cz+.38),(.220,cz+.43),(.225,cz+.44)]
for radius,z in profile:
 for i in range(N):a=i*2*math.pi/N;verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z))
faces=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]+[(r*N+i,r*N+(i+1)%N,(r+1)*N+(i+1)%N,(r+1)*N+i) for r in range(len(profile)-1) for i in range(N)]
overpack=mesh('Receiving filter overpack on transfer saddle',verts,faces,original_mats['Ivory industrial enamel']);outward_mesh(overpack);support(overpack,saddle.name,(cx+.15,cy,cz));aged_finish(overpack,(.25,.24,.19),144,True,.35)
for label,z in [('base',cz+.02),('closure',cz+.419)]:
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(cx,cy,z),major_radius=.224,minor_radius=.012);o=bpy.context.object;o.name='WS | Overpack '+label+' rolled band';finish(o,original_mats['Structural warm graphite']);intrinsic(o,overpack,'Rolled chime formed around sealed overpack shell')
for i in range(6):
 a=i*2*math.pi/6+math.pi/6;o=cyl('Overpack closure captive bolt '+str(i),(cx+.18*math.cos(a),cy+.18*math.sin(a),cz+.448),.012,.016,steel,6);intrinsic(o,overpack,'Captive closure bolt through bolted lid; clear of both web paths')
# Attached faded hold tag belongs to the actual incoming load.
o=cube('Incoming overpack hold tag',(cx-.21,cy,cz+.27),(.003,.12,.09),paper);intrinsic(o,overpack,'Paper transport tag held against the overpack wall')
# The extractor is an actual hollow plenum with sealed filter inspection windows.
def cut_volume(obj,name,pos,dims):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);cutter=bpy.context.object;cutter.name='TEMP | '+name;cutter.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);obj['overhaul_modified']=True # Preserve Boolean's inward cavity normals.
clear_window=material('Dusty transmissive inspection glass',(.94,.95,.91),.065);bsdf(clear_window).inputs['Transmission Weight'].default_value=1;bsdf(clear_window).inputs['IOR'].default_value=1.46
plenum=bpy.data.objects['Connected filter plenum'];cut_volume(plenum,'Hollow filter air plenum',(-4.73,16.10,1.16),(1.50,.97,1.67))
for idx,cx in enumerate([-5.13,-4.33]):
 name='Removable filter cassette'+('' if idx==0 else '.001');panel=bpy.data.objects[name];cut_volume(panel,'Sealed inspection aperture '+str(idx),(cx,15.54,1.45),(.25,.12,.32));cut_volume(plenum,'Plenum inspection aperture '+str(idx),(cx,15.60,1.45),(.25,.15,.32))
 frame=cube('Extractor window lower folded rim '+str(idx),(cx,15.519,1.28),(.28,.006,.018),original_mats['Structural warm graphite'],.001);support(frame,panel.name,(cx,15.522,1.28),(0,1,0))
 for label,pos,dims in [('upper',(cx,15.519,1.62),(.28,.006,.018)),('left',(cx-.135,15.519,1.45),(.018,.006,.32)),('right',(cx+.135,15.519,1.45),(.018,.006,.32))]:
  o=cube('Extractor window '+label+' rim '+str(idx),pos,dims,original_mats['Structural warm graphite'],.001);intrinsic(o,frame,'Window frame welded to the cassette rim')
 o=cube('Extractor sealed dirty viewport '+str(idx),(cx,15.527,1.45),(.247,.004,.317),clear_window);intrinsic(o,frame,'Sealed glass retained behind the rim gasket')
 # Folded paper pleats face the real viewport, with clear air space behind them.
 verts=[]
 for z in [1.291,1.609]:
  for i in range(17):verts.append((cx-.119+i*.238/16,15.588+(.013 if i%2 else 0),z))
 faces=[(i,i+1,17+i+1,17+i) for i in range(16)];o=mesh('Extractor loaded filter pleats '+str(idx),verts,faces,paper);intrinsic(o,frame,'Pleated cartridge held within the sealed cassette');stain_material(o,[((cx-.035,15.60,1.41),(7,1,5))],'Clogged filter '+str(idx),(.16,.19,.12),.88)
 for j in range(3):
  o=cube('Extractor viewport safety wire '+str(idx)+' '+str(j),(cx-.08+j*.08,15.523,1.45),(.002,.002,.334),edge);intrinsic(o,frame,'Wire guard captured by the upper and lower folded window rims')
# Adult canvas gloves have palm volume and bent individual finger sections, not flat cutouts.
glove_mat=material('Exhausted canvas glove',(.06,.065,.043),.98)
def glove_loft(name,sections,centre,angle,drape=False):
 verts=[];N=12
 for x,y,z,w,h in sections:
  for i in range(N):
   a=i*2*math.pi/N;xx=x+w*math.cos(a);zz=z+h*math.sin(a)-(max(0,y-.073)*1.1 if drape else 0);verts.append((centre[0]+xx*math.cos(angle)-y*math.sin(angle),centre[1]+xx*math.sin(angle)+y*math.cos(angle),top+zz))
 faces=[tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))]+[(r*N+i,r*N+(i+1)%N,(r+1)*N+(i+1)%N,(r+1)*N+i) for r in range(len(sections)-1) for i in range(N)]
 if name in bpy.data.objects:o=remesh(name,verts,faces,glove_mat)
 else:o=mesh(name,verts,faces,glove_mat)
 outward_mesh(o)
 for polygon in o.data.polygons:polygon.use_smooth=len(polygon.vertices)==4
 return o
glove_poses=[((5.23,16.48),.23),((5.34,16.44),math.pi+.18)]
for hand in range(2):
 centre,angle=glove_poses[hand];rootname='WS | Slumped glove '+str(hand)
 palm=glove_loft(rootname,[(0,-.074,.009,.028,.006),(0,-.042,.012,.035,.010),(0,0,.016,.039,.016),(0,.032,.014,.037,.010)],centre,angle,hand==1)
 if hand==1:
  supports[:]=[r for r in supports if r['object']!=palm.name];support(palm,worktop.name,(centre[0]+.074*math.sin(angle),centre[1]-.074*math.cos(angle),top))
 for finger,(x,length) in enumerate([(-.026,.043),(-.009,.070),(.009,.063),(.026,.044)]):
  o=glove_loft('Glove '+str(hand)+' collapsed finger '+str(finger),[(x,.025,.013,.010,.007),(x,.045,.017,.009,.007),(x-.003,.055+length*.4,.024,.008,.005),(x-.006,.030+length,.015,.004,.003)],centre,angle,hand==1);intrinsic(o,palm,'Bent cloth finger sewn into glove palm')
 o=glove_loft('Glove '+str(hand)+' creased thumb',[(.029,-.008,.012,.012,.008),(.048,.008,.017,.010,.007),(.059,.025,.012,.005,.004)],centre,angle,hand==1);intrinsic(o,palm,'Sewn thumb of collapsed work glove')

# A captured pin fixes the paper transport tag to the overpack shell.
o=cyl('Overpack retained tag pin',(3.1895,3.82,cz+.30),.005,.009,original_mats['Structural warm graphite'],8);o.rotation_euler=(0,math.pi/2,0);intrinsic(o,overpack,'Tag pin seated into shell with 2mm anchoring depth')
# Remove the original flat paint films from the new east steel skins.
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('Divider oxide lower band'):
  centre=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  if centre.x>0:o.hide_render=True;o['overhaul_modified']=True
# Existing identity plates keep their protected assemblies and gain real stand-off studs.
for idx,cy in [(4,4.8),(6,9.4)]:
 wallname='Cell transverse concrete separator.'+str(idx).zfill(3)
 for x in [3.24,4.56]:
  if idx==4:
   t=(x-2.15)/(.1375);i=min(27,int(t));f=t-i;d0=.027 if i%4 in [1,2] else 0;d1=.027 if (i+1)%4 in [1,2] else 0;surface=cy-.062+d0*(1-f)+d1*f
  else:
   # Quarantine's horizontal fold is evaluated separately at each fastening height.
   surface=None
  for z in [.37,.87]:
   if idx==6:
    t=z/(1.1/12);i=min(11,int(t));f=t-i;d0=.024 if i%4 in [1,2] else 0;d1=.024 if (i+1)%4 in [1,2] else 0;surface=cy-.057+d0*(1-f)+d1*f
   start=cy-.079
   if idx==6:
    from mathutils.bvhtree import BVHTree
    slope=(d1-d0)/(1.1/12);direction=Vector((0,1,-slope*.5)).normalized();origin=Vector((x,start,z));bpy.context.view_layer.update();evaluated=bpy.data.objects[wallname].evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();bv=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);point,normal,index,distance=bv.ray_cast(origin,direction,.2);evaluated.to_mesh_clear();assert point is not None
    end=point+direction*.001;length=(end-origin).length;o=cyl('East cell '+str(idx)+' identity stand-off '+str(x)+' '+str(z),(origin+end)/2,.005,length,steel,12);o.rotation_euler=direction.to_track_quat('Z','Y').to_euler();support(o,wallname,point,direction)
   else:
    end=surface+.001;o=cyl('East cell '+str(idx)+' identity stand-off '+str(x)+' '+str(z),(x,(start+end)/2,z),.005,end-start,steel,12);o.rotation_euler=(math.pi/2,0,0);support(o,wallname,(x,surface,z),(0,1,0))

# Two generations of wall paint: an abraded dark wash below the old lime-grey concrete.
# The broken height band gives architecture a readable history at room scale.
for wallname in ['West Wall','East Wall','East Wall.001','Receiving wall','Receiving wall.001','Dispatch wall','Dispatch wall.001']:
 wall=bpy.data.objects[wallname];m=wall.data.materials[0].copy();m.name='WS | '+wallname+' failing lower wash';wall.data.materials[0]=m;ns=m.node_tree.nodes;ls=m.node_tree.links;b=bsdf(m);base=b.inputs['Base Color'].links[0].from_socket
 geo=ns.new('ShaderNodeNewGeometry');split=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],split.inputs[0]);noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.6;noise.inputs['Detail'].default_value=2;ls.new(geo.outputs['Position'],noise.inputs['Vector'])
 width=ns.new('ShaderNodeMath');width.operation='MULTIPLY';width.inputs[1].default_value=.08;ls.new(noise.outputs['Fac'],width.inputs[0]);height=ns.new('ShaderNodeMath');height.operation='ADD';ls.new(split.outputs['Z'],height.inputs[0]);ls.new(width.outputs[0],height.inputs[1]);band=ns.new('ShaderNodeMapRange');band.inputs['From Min'].default_value=1.215;band.inputs['From Max'].default_value=1.285;band.inputs['To Min'].default_value=1;band.inputs['To Max'].default_value=0;band.clamp=True;ls.new(height.outputs[0],band.inputs[0])
 wash=ns.new('ShaderNodeMath');wash.operation='MULTIPLY';wash.inputs[1].default_value=.65;ls.new(band.outputs[0],wash.inputs[0]);mix=ns.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.105,.132,.111,1);ls.new(base,mix.inputs[1]);ls.new(wash.outputs[0],mix.inputs[0]);base=mix.outputs[0]
 # Paint fails at selected low impact/leak areas, rather than across the whole band.
 chipnoise=ns.new('ShaderNodeTexNoise');chipnoise.inputs['Scale'].default_value=8.5;chipnoise.inputs['Detail'].default_value=2;ls.new(geo.outputs['Position'],chipnoise.inputs['Vector']);tear=ns.new('ShaderNodeValToRGB');tear.color_ramp.elements[0].position=.57;tear.color_ramp.elements[1].position=.585;ls.new(chipnoise.outputs['Fac'],tear.inputs[0])
 centres=[(wall.matrix_world.translation.x,yy,zz) for yy,zz in [(5.9,.44),(9.3,.78),(13.5,.32),(16.5,.52)]] if 'Wall' in wallname else [(xx,wall.matrix_world.translation.y,zz) for xx,zz in [(-1.85,.22),(-4.7,.68),(1.80,.32),(4.1,.42)]]
 regions=[]
 for centre in centres:
  sub=ns.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=centre;scale=ns.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1,1.9,2.8) if 'Wall' in wallname else (1.9,1,2.8);length=ns.new('ShaderNodeVectorMath');length.operation='LENGTH';fade=ns.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.72;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;fade.clamp=True;ls.new(geo.outputs['Position'],sub.inputs[0]);ls.new(sub.outputs['Vector'],scale.inputs[0]);ls.new(scale.outputs['Vector'],length.inputs[0]);ls.new(length.outputs['Value'],fade.inputs[0]);regions.append(fade.outputs[0])
 reg=regions[0]
 for r in regions[1:]:maximum=ns.new('ShaderNodeMath');maximum.operation='MAXIMUM';ls.new(reg,maximum.inputs[0]);ls.new(r,maximum.inputs[1]);reg=maximum.outputs[0]
 mask=ns.new('ShaderNodeMath');mask.operation='MULTIPLY';ls.new(tear.outputs[0],mask.inputs[0]);ls.new(reg,mask.inputs[1]);gated=ns.new('ShaderNodeMath');gated.operation='MULTIPLY';ls.new(mask.outputs[0],gated.inputs[0]);ls.new(band.outputs[0],gated.inputs[1]);mask=gated
 chip=ns.new('ShaderNodeMixRGB');chip.inputs[2].default_value=(.115,.122,.105,1);ls.new(mask.outputs[0],chip.inputs[0]);ls.new(base,chip.inputs[1]);ls.new(chip.outputs[0],b.inputs['Base Color']);b.inputs['Roughness'].default_value=.96
 bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.0018;ls.new(mask.outputs[0],bump.inputs['Height']);ls.new(bump.outputs[0],b.inputs['Normal'])
# Strong wet streaks grow from a few failed service seams; most upper panels stay quiet.
for name,spots in [('West Wall',[((-6,12.85,2.22),(1,1.05,.82)),((-6,13.10,1.35),(1,4,1.05)),((-6,9.20,2.64),(1,3.6,.85))]),('East Wall.001',[((6,12.95,2.60),(1,1.8,.62)),((6,13.10,1.9),(1,6,.75)),((6,16.72,3.0),(1,2.8,.7))]),('Dispatch wall',[((-3.70,18,2.5),(1.45,1,.8)),((-3.75,18,1.35),(4.5,1,.9))])]:
 stain_material(bpy.data.objects[name],spots,'Visible service seepage '+name,(.10,.16,.08),.94)
# Shallow irregular spalls remove actual wall material, leaving a jagged aggregate recess.
aggregate=material('Exposed old wall aggregate',(.085,.091,.081),.99);weather(aggregate,(.085,.091,.081),.99,0,9,.28)
next(n for n in aggregate.node_tree.nodes if n.type=='BUMP').inputs['Distance'].default_value=.008
for idx,(name,y,z,w,h,side) in enumerate([('West Wall',12.80,2.13,.86,.73,-1),('West Wall',6.10,1.56,.54,.46,-1),('East Wall.001',12.86,2.05,.73,.55,1),('East Wall.001',16.72,2.58,.60,.38,1)]):
 wall=bpy.data.objects[name];wall.data.materials.append(aggregate);verts=[];corners=[(-.50,-.20),(-.38,-.48),(-.10,-.50),(.16,-.38),(.44,-.40),(.50,-.13),(.32,.05),(.49,.23),(.27,.43),(-.02,.5),(-.16,.28),(-.44,.32)];outline=[]
 for i,(u,v) in enumerate(corners):
  un,vn=corners[(i+1)%len(corners)];du,dv=un-u,vn-v;length=math.hypot(du,dv)
  for j in range(4):
   t=j/4;k=i*4+j;jitter=.015*math.sin(k*2.13+idx*.9)*math.sin(math.pi*t);outline.append((u+du*t-dv/length*jitter,v+dv*t+du/length*jitter))
 N=len(outline)
 for depth,scale in [(5.985,1),(6.009,.95),(6.029,.69)]:
  verts.extend([(side*depth,y+u*w*scale,z+v*h*scale) for i,(u,v) in enumerate(outline)])
 verts.append((side*(6.055+idx*.001),y+.023*idx,z-.021*idx));faces=[tuple(reversed(range(N)))]+[(2*N+i,2*N+(i+1)%N,3*N) for i in range(N)]+[(r*N+i,r*N+(i+1)%N,(r+1)*N+(i+1)%N,(r+1)*N+i) for r in range(2) for i in range(N)]
 cutter=mesh('Wall spall cutter '+str(idx),verts,faces,aggregate);outward_mesh(cutter);bpy.context.view_layer.update();mod=wall.modifiers.new('Actual shallow aggregate loss '+str(idx),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);wall['overhaul_modified']=True
# Cask heads have a pressed crown and thin underside, while their lifting pads stay seated.
for idx,name in enumerate(['Shallow dished cover','Shallow dished cover.001','Shallow dished cover.002','Shallow dished cover.003','Shallow dished cover.004']):
 o=bpy.data.objects[name];cx,cy,cz=o.matrix_world.translation;rad=.3698 if idx<3 else .4902;N=32;verts=[]
 rings=[(rad,cz-.035),(rad,cz-.005),(rad*.91,cz+.018),(rad*.68,cz+.051),(rad*.36,cz+.077),(rad*.10,cz+.086)]
 for radius,z in rings:
  for j in range(N):a=j*2*math.pi/N;verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z))
 faces=[tuple(reversed(range(N))),tuple(range((len(rings)-1)*N,len(rings)*N))]+[(r*N+j,r*N+(j+1)%N,(r+1)*N+(j+1)%N,(r+1)*N+j) for r in range(len(rings)-1) for j in range(N)];remesh(name,verts,faces,original_mats['Ivory industrial enamel']);outward_mesh(o)
 # Cast seating recesses preserve the original lifting shoes at their exact poses.
 for shoe in [x for x in o.parent.children if x.name.startswith('Lift eye welded base')]:
  pts=[shoe.matrix_world@Vector(v) for v in shoe.bound_box];lo=Vector([min(v[k] for v in pts) for k in range(3)]);hi=Vector([max(v[k] for v in pts) for k in range(3)]);cut_volume(o,'Cast lifting shoe seat',((lo.x+hi.x)/2,(lo.y+hi.y)/2,(lo.z+cz+.12)/2),(hi.x-lo.x+.002,hi.y-lo.y+.002,cz+.12-lo.z))
 aged_finish(o,[(.13,.16,.135),(.175,.195,.17),(.23,.175,.105),(.23,.255,.21),(.095,.145,.165)][idx],190+idx,False,.24)
# Handling uprights and overhead joints keep oxide in the creases, not white corrosion noise.
for o in list(s.objects):
 if o.type=='MESH' and o.name.startswith(('Column flange','Column shoe','Roof knee brace','Roof beam web','Duct joint flange')):
  p=o.matrix_world.translation;stain_material(o,[((p.x,p.y,.17 if 'Column' in o.name else p.z-.14),(2.4,4,3.5))],'Neglected structural joint '+o.name,(.20,.12,.055),.78)

# A sealed quarantine inspection pane reveals the actual cartridge below the closed-lid limit.
# It sits between existing pressed reinforcement ribs and keeps the identity plate intact.
qside=bpy.data.objects['Folded sidewall.004'];cut_volume(qside,'Quarantine sealed inspection opening',(4.2,11.15,.68),(.16,.32,.36))
qframe=cube('Quarantine inspection lower rim',(4.171,11.15,.49),(.008,.36,.018),original_mats['Structural warm graphite'],.001);support(qframe,qside.name,(4.175,11.15,.489),(1,0,0))
for label,pos,dims in [('upper',(4.171,11.15,.87),(.008,.36,.018)),('left',(4.171,10.98,.68),(.008,.018,.36)),('right',(4.171,11.32,.68),(.008,.018,.36))]:
 o=cube('Quarantine inspection '+label+' rim',pos,dims,original_mats['Structural warm graphite'],.001);intrinsic(o,qframe,'Inspection frame welded to steel wall outside the sealed aperture')
o=cube('Quarantine sealed double glass',(4.184,11.15,.68),(.006,.316,.356),clear_window);intrinsic(o,qframe,'Retained gasketed inspection glazing keeps the quarantine shell sealed')
for j in range(3):
 o=cube('Quarantine inspection captured guard wire '+str(j),(4.168,11.06+j*.09,.68),(.002,.002,.392),steel);intrinsic(o,qframe,'Guard wire captured in the window rims')
# A real web restraint bends over the carried overpack and ends at a saddle-fixed buckle.
web=material('Oily overpack restraint webbing',(.039,.052,.044),.99)
weather(web,(.039,.052,.044),.99,0,160,.16)
next(n for n in web.node_tree.nodes if n.type=='BUMP').inputs['Distance'].default_value=.00025
welt=material('Dirty sewn restraint edges',(.14,.155,.115),.99)
padmat=material('Dusty overpack felt wear protector',(.15,.135,.082),.99);weather(padmat,(.15,.135,.082),.99,0,45,.12)
pad=cube('Overpack supported crown wear pad',(3.4,3.82,1.3525),(.27,.29,.015),padmat,.002);support(pad,overpack.name,(3.4,3.82,1.345))
for strap,xc in enumerate([3.31,3.49]):
 path=[(3.485,.905,0),(3.614,.916,.227),(3.633,.970,.210),(3.633,1.285,.210),(3.618,1.335,.222),(3.614,1.348,.227),(3.675,1.3616,0),(3.965,1.3616,0),(4.026,1.348,.227),(4.022,1.335,.222),(4.007,1.285,.210),(4.007,.970,.210),(4.026,.916,.227),(4.155,.905,0)];verts=[]
 for y,z,radius in path:
  for x in [xc-.025,xc+.025]:
   yy=y if radius==0 else 3.82+(-1 if y<3.82 else 1)*math.sqrt(radius**2-(x-3.4)**2);verts.append((x,yy,z))
 faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(path)-1)];o=mesh('Overpack captive restraint strap '+str(strap),verts,faces,web);support(o,'Load saddle',(xc,3.485,.905));support(o,pad.name,(xc,3.82,1.360));o.modifiers.new('Webbing fabric thickness','SOLIDIFY').thickness=.0016
 for edgeindex,fractions in enumerate([(.075,.125),(.875,.925)]):
  seamverts=[]
  for i in range(len(path)):
   left,right=Vector(verts[2*i]),Vector(verts[2*i+1]);previous=Vector(verts[2*max(0,i-1)]);following=Vector(verts[2*min(len(path)-1,i+1)]);normal=(right-left).cross(following-previous).normalized()
   seamverts.extend([tuple(left.lerp(right,f)+normal*.00025) for f in fractions])
  seam=mesh('Restraint '+str(strap)+' sewn welt '+str(edgeindex),seamverts,faces,welt);intrinsic(seam,o,'Sewn edge follows the actual web surface across both sides and the crown')
 # Open ratchet frame, transverse spool and hinged handle explain the retention mechanism.
 buckle=cube('Saddle restraint buckle '+str(strap),(xc-.031,3.491,.926),(.012,.078,.042),edge,.001);support(buckle,'Load saddle',(xc-.031,3.491,.905))
 o=cube('Ratchet second frame cheek '+str(strap),(xc+.031,3.491,.926),(.012,.078,.042),edge,.001);intrinsic(o,buckle,'Paired ratchet cheeks seated on the load saddle')
 for k,yy in enumerate([3.461,3.521]):
  o=cyl('Ratchet captive transverse spool '+str(strap)+' '+str(k),(xc,yy,.927),.010,.074,original_mats['Structural warm graphite'],12);o.rotation_euler=(0,math.pi/2,0);intrinsic(o,buckle,'Retained spindle spans both ratchet cheeks')
 for dx in [-.026,.026]:
  o=cube('Ratchet raised locking lever '+str(strap)+' '+str(dx),(xc+dx,3.469,.957),(.010,.064,.012),edge,.001);intrinsic(o,buckle,'Raised steel handle pivots on the front spool')
 o=cube('Ratchet captive hand grip '+str(strap),(xc,3.441,.958),(.066,.013,.016),original_mats['Structural warm graphite'],.002);intrinsic(o,buckle,'Hand grip joins the two ratchet lever arms')
# The booth bears hand wear and ash-like dust; the actual electronics do not glow as fill.
for name,spots in [('Steel desk top',[((-3.90,1.57,.98),(3.5,3.5,1)),((-3.82,2.20,.98),(6,5,1))]),('Keyboard housing',[((-3.81,1.45,1.03),(8,4,1)),((-3.95,1.65,1.01),(9,8,1))]),('Dose meter cast housing',[((-4.12,2.25,1.47),(1,6,6))])]:
 stain_material(bpy.data.objects[name],spots,'Long shift handled '+name,(.17,.16,.075),.93)
for i in [0,1,2,8,9,10,20,21,22,30,31]:
 name='Keycap'+('' if i==0 else '.'+str(i).zfill(3));key=bpy.data.objects[name];key.data=key.data.copy();aged_finish(key,(.16,.19,.145),270+i,False,.2)
# Dust collects in the desk corners and around the log, staying off the main freight spine.
for i,(x,y,w,h) in enumerate([(-4.37,1.04,.16,.12),(-4.27,2.27,.24,.19),(-3.77,2.21,.11,.08)]):
 verts=[(x-w*.5,y-h*.35,desktop+.00014),(x+w*.45,y-h*.5,desktop+.00014),(x+w*.5,y+h*.27,desktop+.00014),(x-w*.30,y+h*.5,desktop+.00014)];o=mesh('Inventory neglected desktop residue '+str(i),verts,[(0,1,2,3)],oil);soften_stain(o,oil);support(o,'Steel desk top',(x,y,desktop))

# The original gasket was a solid backing slab; author its actual perimeter opening.
# This removes the occluder behind both new inspection panes without unsealing the cassette.
for idx in range(2):
 name='Filter gasket'+('' if idx==0 else '.001');g=bpy.data.objects[name];cx=-5.13 if idx==0 else -4.33;cut_volume(g,'Actual filter gasket centre opening',(cx,15.572,1.20),(.66,.12,1.34))

# Two actual maintenance inspection lamps make the filter media readable through sealed panes.
# They are mounted to their equipment, with modeled shades/lenses and matched outward emitters.
def inspection_emitter(label,hood,lens,watts,angle,aperture):
 lm=material(label+' aged inspection lens',(.50,.57,.43),.42);b=bsdf(lm);b.inputs['Emission Color'].default_value=(.71,.79,.66,1);b.inputs['Emission Strength'].default_value=.25;lens.data.materials.clear();lens.data.materials.append(lm)
 data=bpy.data.lights.new('WS | '+label+' inspection emitter','AREA');data.energy=watts;data.shape='RECTANGLE';data.size=aperture[0];data.size_y=aperture[1];data.color=(.71,.79,.66);o=bpy.data.objects.new(data.name,data);added.objects.link(o);o.rotation_euler=(angle,0,0);axis=o.rotation_euler.to_matrix()@Vector((0,0,-1));o.location=lens.matrix_world.translation+axis*.005;intrinsic(o,hood,'Emitter sits 2mm outside the modeled sealed lens');o['physical_lens']=lens.name;o['failed_fixture']=False;lens['light_source']=o.name;fixture_pairs.append(dict(source=o.name,lens=lens.name,energy=watts,emission=.25,failed=False))
poly=[(4.225,.991),(4.225,1.045),(4.232,1.045),(4.232,1.027),(4.38,1.027),(4.38,1.021),(4.232,1.021),(4.232,.991)];v,f=prism_points(poly,'Y',11.125,11.175);bracket=mesh('Quarantine captured inspection lamp bracket',v,f,original_mats['Structural warm graphite']);outward_mesh(bracket);support(bracket,'Folded sidewall.004',(4.225,11.15,1.01),(-1,0,0))
hood=cube('Quarantine sealed inspection hood',(4.37,11.15,1.010),(.14,.26,.024),original_mats['Structural warm graphite'],.001);intrinsic(hood,bracket,'Pressed hood captured under the welded bracket within the closure height')
lens=cube('Quarantine inspection lamp glass',(4.37,11.15,.994),(.12,.23,.006),clear_window,.0005);intrinsic(lens,hood,'Sealed lamp diffuser retained below the actual hood');inspection_emitter('Quarantine',hood,lens,8,0,(.11,.22))
plate=cube('Extractor inspection lamp bolted mount',(-4.73,15.58,1.91),(.065,.020,.12),original_mats['Structural warm graphite'],.001);support(plate,'Connected filter plenum',(-4.73,15.59,1.91),(0,1,0))
angle=math.radians(27);rot=Matrix.Rotation(angle,3,'X');centre=Vector((-4.73,15.29,1.81));points=[Vector((-4.73,15.57,1.93)),Vector((-4.73,15.285,1.93)),centre+rot@Vector((0,0,.031))]
for i in range(2):
 a,b=points[i:i+2];o=cyl('Extractor inspection arm '+str(i),(a+b)/2,.007,(b-a).length,edge,12);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();intrinsic(o,plate,'Welded steel arm joins mount to inspection hood')
hood=cube('Extractor pressed inspection light hood',centre,(1.05,.105,.060),original_mats['Structural warm graphite'],.002);hood.rotation_euler=(angle,0,0);intrinsic(hood,plate,'Pressed hood fixed to the two-section steel arm')
lens=cube('Extractor inspection lamp glass',centre+rot@Vector((0,0,-.034)),(1.035,.085,.006),clear_window,.001);lens.rotation_euler=(angle,0,0);intrinsic(lens,hood,'Gasketed diffuser retained below the angled shade');inspection_emitter('Extractor',hood,lens,12,angle,(1.00,.065))

# Shielded storage gains a specific angular capture backhood behind the cask/hoist volume.
# It is a hollow folded enclosure with an actual front intake and a branch to the header.
replaced=['Cell extract drop.001','Extract grille frame.001','Extract drop sealed coupling.001']+['Extract grille vane.'+str(i).zfill(3) for i in range(6,12)]
for name in replaced:bpy.data.objects[name].hide_render=True;bpy.data.objects[name]['overhaul_modified']=True
s['replaced_capture_members']=json.dumps(replaced)
hoodmat=material('Old shield-bay capture steel',(.070,.095,.080),.83,.42);weather(hoodmat,(.070,.095,.080),.83,.42,3,.12)
outer=[(-6.0,2.58),(-5.72,2.58),(-5.30,2.80),(-5.30,3.03),(-5.78,3.25),(-6.0,3.25)]
inner=[(-5.984,2.596),(-5.724,2.596),(-5.316,2.807),(-5.316,3.021),(-5.784,3.234),(-5.984,3.234)]
v,f=prism_points(outer,'Y',9.72,13.10);capture=mesh('Shield bay angular capture backhood',v,f,hoodmat);outward_mesh(capture);support(capture,'West Wall',(-6.0,11.40,3.18),(-1,0,0))
v,f=prism_points(inner,'Y',9.736,13.084);cutter=mesh('Temporary capture hollow cutter',v,f,hoodmat);outward_mesh(cutter);mod=capture.modifiers.new('Real folded capture cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=capture;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
cut_volume(capture,'Actual capture intake aperture',(-5.30,11.41,2.915),(.09,2.94,.16));aged_finish(capture,(.070,.095,.080),310,False,.32)
grille=cube('Shield capture lower intake rim',(-5.2925,11.41,2.822),(.015,2.98,.018),edge,.001);support(grille,capture.name,(-5.30,11.41,2.820),(-1,0,0))
for label,pos,dims in [('upper',(-5.2925,11.41,3.008),(.015,2.98,.018)),('near end',(-5.2925,9.93,2.915),(.015,.018,.18)),('far end',(-5.2925,12.89,2.915),(.015,.018,.18))]:
 o=cube('Shield capture '+label+' grille rim',pos,dims,edge,.001);intrinsic(o,grille,'Welded folded rim around the actual open intake')
for j in range(13):
 y=9.98+j*.24;o=cube('Shield capture vertical grille bar '+str(j),(-5.288,y,2.915),(.006,.011,.186),original_mats['Structural warm graphite'],.0007);intrinsic(o,grille,'Intake bars captured in both formed rims')
# A thin perforated lint mesh is captured behind the safety bars, rather than an opaque plane.
for j in range(5):
 o=cube('Shield capture horizontal wire '+str(j),(-5.307,11.41,2.851+j*.032),(.002,2.94,.002),original_mats['Structural warm graphite']);intrinsic(o,grille,'Fine intake wires held in the folded perimeter frame')
# A rectangular hollow branch seats on the sloping roof and penetrates the existing header 1mm.
roof=lambda x:3.03+(-x-5.30)*(.22/.48)
# Open the folded roof and the hollow header only inside the branch's inner perimeter.
header=bpy.data.objects['Longitudinal extract header']
for modifier in header.modifiers:
 if modifier.type=='BEVEL':modifier.width=.0015
cut_volume(header,'Header actual clean air path',(-5.45,10.95,4.03),(.40,13.67,.42))
cut_volume(capture,'Capture roof branch air opening',(-5.54,11.50,roof(-5.54)),(.368,.448,.25))
cut_volume(header,'Header connected capture inlet',(-5.45,11.50,3.805),(.368,.448,.08))
verts=[]
for inner_ring,top_ring in [(False,False),(False,True),(True,True),(True,False)]:
 xa,xb=((-5.634,-5.266) if top_ring else (-5.724,-5.356)) if inner_ring else ((-5.650,-5.250) if top_ring else (-5.740,-5.340));ya,yb=(11.276,11.724) if inner_ring else (11.260,11.740)
 for x,y in [(xa,ya),(xb,ya),(xb,yb),(xa,yb)]:verts.append((x,y,3.806 if top_ring else roof(x)-.001))
faces=[(r*4+j,r*4+(j+1)%4,((r+1)%4)*4+(j+1)%4,((r+1)%4)*4+j) for r in range(4) for j in range(4)];branch=mesh('Shield capture hollow header branch',verts,faces,hoodmat);outward_mesh(branch);support(branch,capture.name,(-5.348,11.50,roof(-5.348)),(-.416,0,-.909));support(branch,header.name,(-5.258,11.50,3.805),(0,0,1));aged_finish(branch,(.085,.112,.090),317,False,.28)
# Actual annular joint flanges keep the branch air path open and expose its construction.
for label,outer,inner,is_upper_flange in [('upper',(-5.672,-5.228,11.235,11.765),(-5.634,-5.266,11.276,11.724),True),('lower',(-5.755,-5.325,11.245,11.755),(-5.724,-5.356,11.276,11.724),False)]:
 verts=[]
 for inner_ring,upper in [(False,False),(False,True),(True,True),(True,False)]:
  xa,xb,ya,yb=inner if inner_ring else outer
  for xx,yy in [(xa,ya),(xb,ya),(xb,yb),(xa,yb)]:verts.append((xx,yy,(3.793 if is_upper_flange else roof(xx)-.001)+(.013 if upper else 0)))
 faces=[(r*4+j,r*4+(j+1)%4,((r+1)%4)*4+(j+1)%4,((r+1)%4)*4+j) for r in range(4) for j in range(4)];flange=mesh('Capture branch '+label+' open joint flange',verts,faces,edge);outward_mesh(flange);intrinsic(flange,branch,'Continuous annular flange clamps the open branch to its receiving surface')
 xa,xb,ya,yb=outer
 for xx,yy in [(xa+.014,ya+.014),(xb-.014,ya+.014),(xb-.014,yb-.014),(xa+.014,yb-.014)]:
  normal=Vector((0,0,-1)) if is_upper_flange else Vector((.416,0,.909)).normalized();point=Vector((xx,yy,3.793 if is_upper_flange else roof(xx)+.012));o=cyl('Capture '+label+' flange captive bolt '+str(xx)+' '+str(yy),point+normal*.004,.007,.008,original_mats['Structural warm graphite'],6);o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();intrinsic(o,flange,'Captive flange bolt head seated on the receiving face')
# Cast-off drips create one small wet service footprint below the overdue extractor.
wet=material('Extractor old service water',(.026,.034,.023),.20);b=bsdf(wet);b.inputs['IOR'].default_value=1.33;nodes=wet.node_tree.nodes;links=wet.node_tree.links;out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent');attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='WS_Damp_Mask';links.new(attr.outputs['Fac'],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(b.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
verts=[(-5.72,15.15,.00015),(-5.60,14.98,.00015),(-5.39,15.04,.00015),(-5.24,15.30,.00015),(-5.33,15.56,.00015),(-5.53,15.64,.00015),(-5.76,15.47,.00015)];o=mesh('Extractor old contained leak footprint',verts,[tuple(range(7))],wet);soften_stain(o,wet);support(o,'Floor',(-5.5,15.3,.00015))

# The inventory terminal has a cast front shoulder and tapered ventilated rear casing.
# Preserve the screen, fasteners, rear vent plane and original mounting stem.
for name,rear_inset,chamfer in [('Instrument rear casing',.038,.022),('Dose meter cast housing',.012,.028)]:
 o=bpy.data.objects[name];points=[Vector(v) for v in o.bound_box];lo=Vector([min(v[k] for v in points) for k in range(3)]);hi=Vector([max(v[k] for v in points) for k in range(3)]);verts=[]
 for yy,inset,cut in [(lo.y,0,chamfer),(lo.y+.025,.002,chamfer),(hi.y,rear_inset,chamfer*.60)]:
  xa,xb=lo.x+inset,hi.x-inset;za,zb=lo.z+inset*.50,hi.z-inset*.50
  outline=[(xa+cut,za),(xb-cut,za),(xb,za+cut),(xb,zb-cut),(xb-cut,zb),(xa+cut,zb),(xa,zb-cut),(xa,za+cut)]
  verts.extend([o.matrix_world@Vector((xx,yy,zz)) for xx,zz in outline])
 faces=[tuple(reversed(range(8))),tuple(range(16,24))]+[(r*8+j,r*8+(j+1)%8,(r+1)*8+(j+1)%8,(r+1)*8+j) for r in range(2) for j in range(8)];remesh(name,verts,faces,original_mats['Ivory industrial enamel'] if name.startswith('Instrument') else original_mats['Galvanized bus casing']);outward_mesh(o);aged_finish(o,(.145,.175,.145) if name.startswith('Instrument') else (.10,.14,.12),350,False,.42)

# The replacement is a flat profiled compression seal, rather than a smooth torus.
seal=bpy.data.objects['Replacement seal'];cx,cy=seal.matrix_world.translation.xy;profile=[(.122,.002),(.124,0),(.156,0),(.158,.002),(.158,.005),(.157,.007),(.153,.012),(.148,.015),(.142,.016),(.139,.018),(.137,.023),(.129,.023),(.125,.018),(.122,.014)];N=64;verts=[]
for radius,height in profile:
 for j in range(N):
  a=j*2*math.pi/N;verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),top+height))
faces=[(r*N+j,r*N+(j+1)%N,((r+1)%len(profile))*N+(j+1)%N,((r+1)%len(profile))*N+j) for r in range(len(profile)) for j in range(N)];remesh(seal.name,verts,faces,rubber);outward_mesh(seal)
for polygon in seal.data.polygons:polygon.use_smooth=True

# Hollow, wrinkled cuffs give the abandoned gloves cloth volume and a real opening.
for hand in range(2):
 centre,angle=glove_poses[hand];verts=[];N=12
 for yy,ww,hh in [(-.078,.033,.014),(-.052,.034,.013),(-.052,.030,.009),(-.078,.029,.010)]:
  for j in range(N):
   a=j*2*math.pi/N;xx=ww*math.cos(a);zz=.014+hh*math.sin(a)+.0015*math.sin(3*a+hand);verts.append((centre[0]+xx*math.cos(angle)-yy*math.sin(angle),centre[1]+xx*math.sin(angle)+yy*math.cos(angle),top+zz))
 faces=[(r*N+j,r*N+(j+1)%N,((r+1)%4)*N+(j+1)%N,((r+1)%4)*N+j) for r in range(4) for j in range(N)];o=mesh('Glove '+str(hand)+' wrinkled open cuff',verts,faces,glove_mat);outward_mesh(o);intrinsic(o,bpy.data.objects['WS | Slumped glove '+str(hand)],'Hollow cuff sewn around the collapsed glove wrist')
weather(glove_mat,(.055,.063,.045),.99,0,58,.20)
# Work-contact discoloration separates handled, oil-soaked wood from quiet grain.
stain_material(worktop,[((4.88,16.68,top),(2.3,3.0,1)),((4.15,16.69,top),(3.2,3.6,1)),((5.30,16.53,top),(7,5,1))],'Seal station soaked working grain',(.21,.19,.13),.64)

# Two flared, rolled-return intake mouths distinguish capture stations from a flat soffit.
# Their foremost edge stays 15mm behind the casks' rear envelope and out of the hoist.
for station,yy in enumerate([10.58,12.22]):
 verts=[]
 for xx,w,h,zz in [(-5.245,1.26,.360,2.925),(-5.301,1.02,.178,2.915),(-5.301,.988,.146,2.915),(-5.245,1.228,.328,2.925)]:
  verts.extend([(xx,yy-w/2,zz-h/2),(xx,yy+w/2,zz-h/2),(xx,yy+w/2,zz+h/2),(xx,yy-w/2,zz+h/2)])
 faces=[(r*4+j,r*4+(j+1)%4,((r+1)%4)*4+(j+1)%4,((r+1)%4)*4+j) for r in range(4) for j in range(4)];o=mesh('Shield station '+str(station)+' flared folded intake',verts,faces,edge);outward_mesh(o);support(o,capture.name,(-5.301,yy,2.829),(-1,0,0));aged_finish(o,(.11,.135,.11),375+station,False,.34)

# Outward-facing tensioners remain visible on the near web sections.
for strap,xc in enumerate([3.31,3.49]):
 webobj=bpy.data.objects['WS | Overpack captive restraint strap '+str(strap)];edges_y=[3.82-math.sqrt(.210**2-(x-3.4)**2) for x in [xc-.025,xc+.025]];ys=sum(edges_y)/2;slope=(edges_y[1]-edges_y[0])/.050;normal=Vector((-slope,1,0)).normalized();pivot=Vector((xc,ys,1.115))
 plate=cube('Overpack visible tensioner backing '+str(strap),(xc,ys-.0015,1.115),(.074,.003,.088),edge,.001);support(plate,webobj.name,pivot,normal)
 for side in [-1,1]:
  o=cube('Overpack tensioner cheek '+str(strap)+' '+str(side),(xc+side*.031,ys-.014,1.115),(.012,.025,.080),edge,.001);intrinsic(o,plate,'Ratchet cheek fixed to backing plate over taut web')
 for zz in [1.083,1.143]:
  o=cyl('Overpack tensioner roll '+str(strap)+' '+str(zz),(xc,ys-.025,zz),.009,.074,original_mats['Structural warm graphite'],12);o.rotation_euler=(0,math.pi/2,0);intrinsic(o,plate,'Retained transverse spool spans both cheeks')
 profile=[(xc-.033,1.155),(xc-.021,1.155),(xc-.021,1.090),(xc+.021,1.090),(xc+.021,1.155),(xc+.033,1.155),(xc+.033,1.078),(xc-.033,1.078)]
 v,f=prism_points(profile,'Y',ys-.060,ys-.047);o=mesh('Overpack tensioner open locking fork '+str(strap),v,f,steel);outward_mesh(o);intrinsic(o,plate,'Open U lever pivots on the upper spool; the taut web is visible between the arms')
 for dx in [-.027,.027]:
  o=cube('Overpack locking fork pivot ear '+str(strap)+' '+str(dx),(xc+dx,ys-.040,1.143),(.012,.030,.022),edge,.001);intrinsic(o,plate,'Formed pivot ear connects the raised fork to the retained transverse spool')
 for dx in [-.039,.039]:
  o=cyl('Overpack ratchet pivot retainer '+str(strap)+' '+str(dx),(xc+dx,ys-.025,1.143),.011,.005,edge,6);o.rotation_euler=(0,math.pi/2,0);intrinsic(o,plate,'Captured hex pivot head retains the fork and transverse spool')
 # Rotate the entire attached ratchet group around its contact point to follow the web.
 plate.rotation_euler.z=math.atan(slope);plate.location=pivot-normal*.0015;bpy.context.view_layer.update()

# Both service seals share the mating diameter; the rejected one is split and distorted.
bsdf(rubber).inputs['Base Color'].default_value=(.019,.026,.022,1);bsdf(rubber).inputs['Roughness'].default_value=.96;bsdf(rubber).inputs['Specular IOR Level'].default_value=.18
removed=bpy.data.objects['WS | Brittle removed seal'];verts=[];N=60;section=[(-.014,.002),(-.012,0),(.012,0),(.014,.002),(.014,.005),(.012,.008),(.010,.012),(.006,.015),(0,.016),(-.002,.018),(-.003,.021),(-.010,.021),(-.013,.018),(-.015,.014),(-.016,.006)];Q=len(section)
for i in range(N):
 a=.16+i*(2*math.pi-.36)/(N-1);rad=.14+.005*math.sin(3*a)+.002*math.sin(9*a)
 lift=.024*math.exp(-(i/7)**2);compression=.64+.36*abs(math.sin(a-.3))
 for dr,dz in section:verts.append((4.62+(rad+dr)*math.cos(a),16.955+(rad+dr)*math.sin(a),top+lift+dz*compression))
faces=[(i*Q+j,(i+1)*Q+j,(i+1)*Q+(j+1)%Q,i*Q+(j+1)%Q) for i in range(N-1) for j in range(Q)]+[tuple(range(Q)),tuple(reversed(range((N-1)*Q,N*Q)))];remesh(removed.name,verts,faces,rubber);outward_mesh(removed)
for polygon in removed.data.polygons[:-2]:polygon.use_smooth=True
supports[:]=[r for r in supports if r['object']!=removed.name];support(removed,worktop.name,verts[(N//2)*Q])
# Move the associated tag beside the actual rejected part, keeping its ink attached.
tag=bpy.data.objects['WS | Removed seal attached tag'];tag.location.x=4.61;tag.location.y=16.955;supports[:]=[r for r in supports if r['object']!=tag.name];support(tag,worktop.name,(4.61,16.955,top));bpy.context.view_layer.update()

# Shallow control joints give the main floor actual poured-slab construction.
floor=bpy.data.objects['Floor']
for xx in [-3,0,3]:cut_volume(floor,'Floor longitudinal control joint '+str(xx),(xx,9,0),(.004,17.98,.003))
for yy in [3,6,9,12,15]:cut_volume(floor,'Floor transverse control joint '+str(yy),(0,yy,0),(11.98,.004,.003))

# Residue bays have profiled cast shoulders; shielded bays use inset replaceable crash channels.
westcoat=material('Old cell protective lower paint',(.066,.083,.067),.96)
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('Divider oxide lower band') and not o.hide_render:o.data.materials.clear();o.data.materials.append(westcoat);o['overhaul_modified']=True
for idx,cy in [(0,4.8),(1,8.8)]:
 name='Cell transverse concrete separator'+('' if idx==0 else '.001');profile=[(cy-.08,0),(cy-.08,.20),(cy-.047,.28),(cy-.047,.88),(cy-.073,1.05),(cy-.073,1.10),(cy+.073,1.10),(cy+.073,1.05),(cy+.047,.88),(cy+.047,.28),(cy+.08,.20),(cy+.08,0)];v,f=prism_points(profile,'X',-6.0,-2.15);o=remesh(name,v,f,original_mats['Replacement cast concrete']);outward_mesh(o)
for idx,cy in [(2,9.4),(3,13.4)]:
 wall=bpy.data.objects['Cell transverse concrete separator.'+str(idx).zfill(3)]
 for pad,(xa,xb) in enumerate([(-5.875,-4.96),(-3.19,-2.285)]):
  cx=(xa+xb)/2;cut_volume(wall,'Shield bay inset impact pocket '+str(pad),(cx,cy-.053,.52),(xb-xa+.010,.076,.402))
  section=[(cy-.015,.32),(cy-.079,.32),(cy-.079,.327),(cy-.022,.327),(cy-.022,.713),(cy-.079,.713),(cy-.079,.72),(cy-.015,.72)];v,f=prism_points(section,'X',xa,xb);o=mesh('Shield bay '+str(idx)+' replaceable crash channel '+str(pad),v,f,original_mats['Structural warm graphite']);outward_mesh(o);support(o,wall.name,(cx,cy-.015,.52),(0,1,0));aged_finish(o,(.037,.051,.042),410+idx+pad,False,.46)

# The abandoned shift note is clipped visibly beside the terminal, rather than flat on the desk.
clip=cube('Inventory missing relief note clip',(-4.059,1.700,1.550),(.022,.032,.055),edge,.001);support(clip,'Instrument rear casing',(-4.070,1.700,1.550),(-1,0,0))
o=cube('Inventory note spring keeper',(-4.042,1.705,1.550),(.005,.014,.036),original_mats['Structural warm graphite'],.001);intrinsic(o,clip,'Spring steel keeper presses the shift note into the monitor clip')
note=bpy.data.objects['WS | Inventory abandoned shift note'];outline=[(1.68,1.565,-4.044),(1.89,1.565,-4.044),(1.902,1.555,-4.044),(1.898,1.415,-4.033),(1.885,1.413,-4.031),(1.68,1.419,-4.042)];verts=[(xx+th,yy,zz) for th in [0,.001] for yy,zz,xx in outline];N=len(outline);faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];remesh(note.name,verts,faces,paper);outward_mesh(note);supports[:]=[r for r in supports if r['object']!=note.name];intrinsic(note,clip,'Shift note held at its upper-left edge by the modeled spring clip')
letter=bpy.data.objects['WS | Inventory shift note printing'];letter.data.size=.025;letter.matrix_world=Matrix.LocRotScale(Vector((-4.041,1.787,1.512)),__import__('mathutils').Euler((math.pi/2,0,math.pi/2)).to_quaternion(),Vector((1,1,1)))

# A handled seal pick bridges the repair gesture from the bench into the split gasket.
# SC01's seal meter is under inspection: its separate protective glazing is swung open.
# The waste vessel remains closed at the original seal/lid pose; SC02 stays in normal storage.
from mathutils.bvhtree import BVHTree
gauge=bpy.data.objects['Instrument cast bezel.003'];G=gauge.matrix_world.translation;bpy.context.view_layer.update();evaluated=gauge.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();bv=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);posts=[];postpoints=[]
for side in [-1,1]:
 hit,n,index,distance=bv.ray_cast(G+Vector((.30,side*.045,.0495)),Vector((-1,0,0)),.6);assert hit is not None
 o=cyl('SC01 meter guard mounting stud '+str(side),hit+n*.008,.006,.016,steel,12);o.rotation_euler=n.to_track_quat('Z','Y').to_euler();support(o,gauge.name,hit,-n);posts.append(o);postpoints.append(hit+n*.016)
evaluated.to_mesh_clear();px=max(p.x for p in postpoints)+.014;centre=Vector((px,G.y,G.z+.04));fixed=cube('SC01 inspection guard fixed frame',centre,(.006,.245,.280),original_mats['Structural warm graphite'],.001);cut_volume(fixed,'Fixed guard clear gauge aperture',centre,(.035,.205,.244));intrinsic(fixed,posts[0],'Welded meter guard frame held by two gauge-case studs')
for i,start in enumerate(postpoints):
 end=Vector((px,start.y,G.z+.180));o=cyl('SC01 guard cast mounting arm '+str(i),(start+end)/2,.006,(end-start).length+.002,edge,12);o.rotation_euler=(end-start).to_track_quat('Z','Y').to_euler();intrinsic(o,posts[i],'Cast arm joins meter-case stud to the fixed upper guard rail')
hinge=Vector((px,G.y-.126,G.z+.04));o=cyl('SC01 retained guard hinge',hinge,.006,.292,steel,12);intrinsic(o,fixed,'Vertical hinge pin retained beside the fixed frame')
turn=Matrix.Rotation(math.radians(-65),3,'Z');centre=hinge+turn@Vector((0,.1225,0));door=cube('SC01 swung-open meter guard',centre,(.006,.245,.280),edge,.001);cut_volume(door,'Open guard actual glazing aperture',centre,(.035,.205,.244));door.rotation_euler.z=math.radians(-65);intrinsic(door,fixed,'Meter glazing guard swung on the retained vertical hinge')
o=cube('SC01 guard retained safety glass',centre,(.002,.202,.241),clear_window,.0005);o.rotation_euler.z=math.radians(-65);intrinsic(o,door,'Clear safety glazing is retained in the opened steel guard')
for dz in [-.09,.09]:
 o=cyl('SC01 guard hinge knuckle '+str(dz),hinge+Vector((0,0,dz)),.010,.032,edge,12);intrinsic(o,door,'Hinge knuckles retain the opened cover on the fixed pin')

# Ink conforms to the curled shift paper, with a tenth-millimetre printed offset.
letter=bpy.data.objects['WS | Inventory shift note printing'];bpy.ops.object.select_all(action='DESELECT');letter.select_set(True);bpy.context.view_layer.objects.active=letter;bpy.ops.object.convert(target='MESH');letter=bpy.context.view_layer.objects.active;bpy.context.view_layer.update();evaluated=note.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();bv=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);inverse=letter.matrix_world.inverted()
for v in letter.data.vertices:
 world=letter.matrix_world@v.co;hit,n,index,distance=bv.ray_cast(Vector((-3.90,world.y,world.z)),Vector((-1,0,0)),.30);assert hit is not None
 depth=max(0,world.x-letter.matrix_world.translation.x);v.co=inverse@(hit+Vector((.00010+depth,0,0)))
evaluated.to_mesh_clear();letter.data.update();letter['printed_surface']=note.name;letter['printed_offset_m']=.00010

# SC02 has a shaped bolted repair on its outer protective jacket, not its sealed inner core.
body=next(o for o in bpy.data.objects['SC02'].children_recursive if o.type=='MESH' and o.name.startswith('Continuous inner vessel'));bpy.context.view_layer.update();evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();bv=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);cx,cy=-4.65,12.35;N=13;verts=[];surface=[]
for zz in [1.42,1.85]:
 row=[]
 for j in range(N):
  angle=-.76+j*.48/(N-1);direction=Vector((math.cos(angle),math.sin(angle),0));hit,n,index,distance=bv.ray_cast(Vector((cx,cy,zz)),direction,1);assert hit is not None;row.append((hit,n));surface.append((hit,n))
 verts.extend([tuple(hit+n*.0005) for hit,n in row])
verts.extend([tuple(hit+n*.0045) for hit,n in surface]);faces=[]
for j in range(N-1):faces.extend([(j,j+1,N+j+1,N+j),(2*N+j,3*N+j,3*N+j+1,2*N+j+1),(j,2*N+j,2*N+j+1,j+1),(N+j,N+j+1,3*N+j+1,3*N+j)])
faces.extend([(0,N,3*N,2*N),(N-1,3*N-1,4*N-1,2*N-1)]);patch=mesh('SC02 curved outer jacket bolted repair',verts,faces,steel);outward_mesh(patch);hit,n=surface[N//2];support(patch,body.name,hit,-n);aged_finish(patch,(.105,.128,.117),481,False,.42)
for zz in [1.447,1.823]:
 for angle in [-.715,-.325]:
  direction=Vector((math.cos(angle),math.sin(angle),0));hit,n,index,distance=bv.ray_cast(Vector((cx,cy,zz)),direction,1);o=cyl('SC02 jacket repair captive bolt '+str(zz)+' '+str(angle),hit+n*.008,.009,.007,edge,6);o.rotation_euler=n.to_track_quat('Z','Y').to_euler();intrinsic(o,patch,'Captive bolt head seats on the formed outer jacket repair')
evaluated.to_mesh_clear()

# Supplemental service detail exposes the complete capture/header connection above the casks.
data=bpy.data.cameras.new('D02_CaptureService');data.lens=30;cam=bpy.data.objects.new('D02_CaptureService',data);s.collection.objects.link(cam);cam.location=(-2.40,12.80,2.50);cam.rotation_euler=(Vector((-5.48,11.50,3.30))-cam.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('D03_ExtractionRun');data.lens=18;cam=bpy.data.objects.new('D03_ExtractionRun',data);s.collection.objects.link(cam);cam.location=(0,12.20,1.68);cam.rotation_euler=(Vector((-5.10,13.50,2.25))-cam.location).to_track_quat('-Z','Y').to_euler()

# A handled seal pick bridges the repair gesture from the bench into the split gasket.
a=Vector((4.70,16.82,top+.012));b=Vector((4.765,16.978,top+.027));axis=(b-a).normalized()
handle=cyl('Abandoned seal pick worn handle',a+axis*.025,.012,.060,original_mats['Oxide painted steel'],12);handle.rotation_euler=axis.to_track_quat('Z','Y').to_euler();foot=a-axis*.005;support(handle,worktop.name,(foot.x,foot.y,top))
o=cyl('Seal pick steel shank',(a+axis*.056+b-axis*.015)/2,.003,(b-axis*.015-(a+axis*.056)).length,steel,12);o.rotation_euler=axis.to_track_quat('Z','Y').to_euler();intrinsic(o,handle,'Steel tang retained in the worn handle')
perp=Vector((-axis.y,axis.x,0));v=[b-axis*.020-perp*.006,b-axis*.020+perp*.006,b+perp*.005,b-perp*.005];verts=[tuple(p+Vector((0,0,dz))) for dz in [-.001,.001] for p in v];o=mesh('Seal pick flat release blade',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],steel);outward_mesh(o);intrinsic(o,handle,'Flat tip remains inserted beside the cut end of the rejected seal')

# The formed inlet differs from the rectangular exhaust, with actual open joints.
intake=material('Old blue-grey extraction duct coating',(.055,.090,.095),.84,.34)
weather(intake,(.055,.090,.095),.84,.34,3.1,.13)
for name in ['Longitudinal extract header','Longitudinal extract header.001','Rear intake crossheader','Raised intake bridge riser','Raised intake bridge riser.001','WS | Shield capture hollow header branch']:
 o=bpy.data.objects[name];o.data.materials.clear();o.data.materials.append(intake);o['overhaul_modified']=True
for station in range(2):aged_finish(bpy.data.objects['WS | Shield station '+str(station)+' flared folded intake'],(.095,.110,.087),430+station,False,.40)
bpy.data.objects['Filter inlet upper offset'].hide_render=True
inlet_lower_x=-4.62;inlet_upper_x=-5.45;inlet_lower_y=15.87;inlet_upper_y=16.10
inlet_lower_z=2.229
outline=[(inlet_lower_x-.23,inlet_lower_y-.26),(inlet_lower_x+.23,inlet_lower_y-.26),(inlet_lower_x+.26,inlet_lower_y-.23),(inlet_lower_x+.26,inlet_lower_y+.23),(inlet_lower_x+.23,inlet_lower_y+.26),(inlet_lower_x-.23,inlet_lower_y+.26),(inlet_lower_x-.26,inlet_lower_y+.23),(inlet_lower_x-.26,inlet_lower_y-.23)]
# The adapter expands toward its offset roof opening; its bore continues the pipe axis.
axis_x=(inlet_lower_x-inlet_upper_x)/(3.806-inlet_lower_z);axis_y=(inlet_lower_y-inlet_upper_y)/(3.806-inlet_lower_z)
bottom_dx=axis_x*(inlet_lower_z-2.018);bottom_dy=axis_y*(inlet_lower_z-2.018)
v=[(inlet_lower_x+(x-inlet_lower_x)*1.35+bottom_dx,inlet_lower_y+(y-inlet_lower_y)*1.35+bottom_dy,2.018) for x,y in outline]+[(x,y,2.230) for x,y in outline]
f=[tuple(reversed(range(8))),tuple(range(8,16))]+[(j,(j+1)%8,(j+1)%8+8,j+8) for j in range(8)]
neck=remesh('Filter inlet welded neck',v,f,intake);outward_mesh(neck);support(neck,plenum.name,(inlet_lower_x+.24,inlet_lower_y+.24,2.020))

verts=[];N=40
for cx,cy,r,z in [(inlet_lower_x,inlet_lower_y,.200,inlet_lower_z),(inlet_upper_x,inlet_upper_y,.200,3.806),(inlet_upper_x,inlet_upper_y,.180,3.806),(inlet_lower_x,inlet_lower_y,.180,inlet_lower_z)]:
 for j in range(N):
  a=j*2*math.pi/N;verts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
faces=[(r*N+j,r*N+(j+1)%N,((r+1)%4)*N+(j+1)%N,((r+1)%4)*N+j) for r in range(4) for j in range(N)]
drop=remesh('Filter inlet drop',verts,faces,intake);outward_mesh(drop)
support(drop,'Filter inlet welded neck',(inlet_lower_x+.193,inlet_lower_y,2.230),(0,0,-1))
support(drop,'Longitudinal extract header',(-5.257,16.10,3.805),(0,0,1))
def round_air_opening(obj,label,cx,cy,z,radius,depth):
 bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=radius,depth=depth,location=(cx,cy,z));cutter=bpy.context.object
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);obj['overhaul_modified']=True
round_air_opening(bpy.data.objects['Longitudinal extract header'],'Open formed inlet connection',-5.45,16.10,3.805,.180,.09)
def continuous_inlet_bore(obj,label):
 vertices=[];count=40
 for z in [1.960,2.280]:
  cx=inlet_lower_x+axis_x*(inlet_lower_z-z);cy=inlet_lower_y+axis_y*(inlet_lower_z-z)
  for j in range(count):
   angle=j*2*math.pi/count;vertices.append((cx+.180*math.cos(angle),cy+.180*math.sin(angle),z))
 faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)]
 cutter=mesh('Temporary continuous inlet cutter',vertices,faces,steel);outward_mesh(cutter);bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);obj['overhaul_modified']=True
continuous_inlet_bore(neck,'Continuous angled neck air passage')
continuous_inlet_bore(plenum,'Open plenum roof along inlet axis')
inlet_middle_x=inlet_lower_x+(inlet_upper_x-inlet_lower_x)*(3.08-inlet_lower_z)/(3.806-inlet_lower_z)
inlet_middle_y=inlet_lower_y+(inlet_upper_y-inlet_lower_y)*(3.08-inlet_lower_z)/(3.806-inlet_lower_z)
for label,cx,cy,zz,outer in [('lower',inlet_lower_x,inlet_lower_y,2.238,.235),('middle',inlet_middle_x,inlet_middle_y,3.08,.216),('upper',inlet_upper_x,inlet_upper_y,3.797,.215)]:
 verts=[];N=40
 for radius,z in [(outer,zz-.007),(outer,zz+.007),(.181,zz+.007),(.181,zz-.007)]:
  for j in range(N):a=j*2*math.pi/N;verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z))
 faces=[(r*N+j,r*N+(j+1)%N,((r+1)%4)*N+(j+1)%N,((r+1)%4)*N+j) for r in range(4) for j in range(N)]
 flange=mesh('Formed filter inlet '+label+' annular joint',verts,faces,edge);outward_mesh(flange);intrinsic(flange,drop,'Open annular reinforcement captures the formed inlet pipe')
 for j in range(6):
  a=j*2*math.pi/6;rr=(outer+.200)/2;o=cyl('Filter inlet '+label+' captive bolt '+str(j),(cx+rr*math.cos(a),cy+rr*math.sin(a),zz+.010),.006,.006,original_mats['Structural warm graphite'],6);intrinsic(o,flange,'Captive joint bolt head seated on annular flange')
# The four inherited neck fasteners follow the revised neck, with real flange seats.
for index,(dx,dy) in enumerate([(-.20,-.20),(-.20,.20),(.20,-.20),(.20,.20)]):
 name='Inlet neck flange bolt'+('' if index==0 else '.'+str(index).zfill(3));cx=inlet_lower_x+dx;cy=inlet_lower_y+dy;verts=[]
 for zz in [2.230,2.242]:
  for j in range(6):
   angle=j*2*math.pi/6;verts.append((cx+.015*math.cos(angle),cy+.015*math.sin(angle),zz))
 faces=[tuple(reversed(range(6))),tuple(range(6,12))]+[(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)];o=remesh(name,verts,faces,steel);outward_mesh(o);support(o,neck.name,(cx,cy,2.230))
s['filter_neck_fasteners_reseated']=True
s['formed_filter_inlet_open']=True
s['filter_inlet_lower_x']=inlet_lower_x;s['filter_inlet_upper_x']=inlet_upper_x;s['filter_inlet_lower_y']=inlet_lower_y;s['filter_inlet_upper_y']=inlet_upper_y;s['filter_inlet_lower_z']=inlet_lower_z
# Handling smears follow the removed seal and tool, leaving quiet timber elsewhere.
stain_material(worktop,[((4.67,16.93,top),(4.5,8,1)),((4.74,16.85,top),(9,5,1)),((5.17,16.48,top),(8,9,1))],'Interrupted seal work oily hand wipes',(.08,.075,.040),.87)

# A broad removal trace joins the split seal to the pick instead of isolated display props.
trace=[(x,y,top+.00015) for x,y in [(4.57,16.899),(4.63,16.834),(4.70,16.804),(4.75,16.734),(4.805,16.746),(4.781,16.802),(4.84,16.792),(4.86,16.827),(4.762,16.870),(4.665,16.918)]]
o=mesh('Seal removal dragged oil trace',trace,[tuple(range(len(trace)))],oil);soften_stain(o,oil);support(o,worktop.name,(4.70,16.85,top))

# Pressed hat stiffeners make the dry covers read as formed sheet, within their old rims.
for lidindex,name in enumerate(['Folded lid','Folded lid.001']):
 lid=bpy.data.objects[name];cy=6.285 if lidindex==0 else 7.315
 for ribindex,offset in enumerate([-.145,.145]):
  bpy.context.view_layer.update();evaluated=lid.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);evaluated.to_mesh_clear()
  outline=[(-.86,-.034),(.86,-.034),(.885,-.018),(.885,.018),(.86,.034),(-.86,.034),(-.885,.018),(-.885,-.018)]
  def cover_z(x,y):
   hit,n,index,d=tree.ray_cast(Vector((x,y,1.25)),Vector((0,0,-1)),.25);assert hit is not None;return hit.z
  floorz=min(cover_z(4.25+x,cy+offset+y) for x,y in outline)-.0015;verts=[]
  for ring in range(3):
   for x,y in outline:
    xx=4.25+x*(.974 if ring==2 else 1);yy=cy+offset+y*(.55 if ring==2 else 1)
    verts.append((xx,yy,floorz if ring==0 else cover_z(xx,yy)+(.016 if ring==2 else .0003)))
  verts.extend([(4.25,cy+offset,floorz),(4.25,cy+offset,cover_z(4.25,cy+offset)+.016)])
  faces=[(i,(i+1)%8,24) for i in range(8)]+[(16+(i+1)%8,16+i,25) for i in range(8)]+[(r*8+i,r*8+(i+1)%8,(r+1)*8+(i+1)%8,(r+1)*8+i) for r in range(2) for i in range(8)]
  swage=mesh('Temporary formed cover swage',verts,faces,lid.data.materials[0]);outward_mesh(swage);mod=lid.modifiers.new('Integral pressed stiffener '+str(ribindex),'BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=swage;bpy.context.view_layer.objects.active=lid;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(swage,do_unlink=True);lid['overhaul_modified']=True

# Dry storage has open service screens over a continuous catch curb, rather than another trough.
screenmat=material('Handled expanded steel service screen',(.075,.105,.087),.78,.58)
for cellindex,cy in [(4,4.8),(5,8.8)]:
 wall=bpy.data.objects['Cell transverse concrete separator.'+str(cellindex).zfill(3)]
 for openingindex,(xa,xb) in enumerate([(2.40,3.08),(4.73,5.76)]):
  za,zb=.395,1.024;cx=(xa+xb)/2
  cut_volume(wall,'Dry service screen opening '+str(openingindex),(cx,cy,.7095),(xb-xa,.24,zb-za))
  bottom=cube('Dry cell '+str(cellindex)+' screen '+str(openingindex)+' lower frame',(cx,cy-.051,.384),(xb-xa+.044,.056,.022),steel,.001)
  bpy.context.view_layer.update();evaluated=wall.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);evaluated.to_mesh_clear();hit,n,index,d=tree.ray_cast(Vector((cx,cy-.15,.373)),Vector((0,1,0)),.3);assert hit is not None;support(bottom,wall.name,hit,(0,1,0))
  for label,pos,dims in [('upper',(cx,cy-.051,1.035),(xb-xa+.044,.056,.022)),('left',(xa-.011,cy-.051,.7095),(.022,.056,.651)),('right',(xb+.011,cy-.051,.7095),(.022,.056,.651))]:
   frame=cube('Dry cell '+str(cellindex)+' screen '+str(openingindex)+' '+label+' frame',pos,dims,steel,.001);intrinsic(frame,bottom,'Welded channel perimeter holds the replaceable expanded service screen')
  # Clip both families of flat diagonal laths at their real perimeter, with no floating ends.
  verts=[];faces=[]
  def clipped(poly,axis,value,greater):
   result=[]
   for p,q in zip(poly,poly[1:]+poly[:1]):
    inp=(p[axis]>=value) if greater else (p[axis]<=value);inq=(q[axis]>=value) if greater else (q[axis]<=value)
    if inp:result.append(p)
    if inp!=inq:
     t=(value-p[axis])/(q[axis]-p[axis]);result.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(2)))
   return result
  for slope in [-.75,.75]:
   for i in range(-20,21):
    intercept=.710+i*.090;poly=[(xa-.1,intercept+slope*(xa-.1-cx)-.004),(xb+.1,intercept+slope*(xb+.1-cx)-.004),(xb+.1,intercept+slope*(xb+.1-cx)+.004),(xa-.1,intercept+slope*(xa-.1-cx)+.004)]
    for axis,value,greater in [(0,xa-.006,True),(0,xb+.006,False),(1,za-.006,True),(1,zb+.006,False)]:
     if poly:poly=clipped(poly,axis,value,greater)
    if len(poly)<3:continue
    v,f=prism_points(poly,'Y',cy-.026,cy-.023);base=len(verts);verts.extend(v);faces.extend(tuple(base+j for j in face) for face in f)
  screen=mesh('Dry cell '+str(cellindex)+' screen '+str(openingindex)+' expanded laths',verts,faces,screenmat);outward_mesh(screen);intrinsic(screen,bottom,'Clipped steel laths overlap inside the welded perimeter channels')

# Adjustable front housings on the existing wall fixtures; original wall mounts stay seated.
for suffix,cy,tilt,watts in [('.001',10.70,-32,110),('.002',16.00,-18,120)]:
 pivot=Vector((-5.945,cy,3.585));transform=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(tilt),4,'Y')@Matrix.Translation(-pivot)
 cleat=cube('Wall task fixture '+suffix+' cast tilt cleat',(-5.950,cy,3.585),(.022,.31,.024),edge,.001);support(cleat,'Wall fixture backplate'+suffix,(-5.960,cy,3.585),(-1,0,0))
 pin=cyl('Wall task fixture '+suffix+' captured tilt pin',pivot,.012,.32,edge,12);pin.rotation_euler=(math.pi/2,0,0);intrinsic(pin,cleat,'Captured trunnion joins the tilted housing to its cast backplate cleat')
 for name in ['Angled fixture housing'+suffix,'Wall wash diffuser'+suffix,'Directed practical wash'+suffix]:
  obj=bpy.data.objects[name];obj.matrix_world=transform@obj.matrix_world;obj['overhaul_modified']=True
 light=bpy.data.objects['Directed practical wash'+suffix];light.data.energy=watts;light.data.spot_size=math.radians(48);light.data.spot_blend=.48
 for pair in fixture_pairs:
  if pair['source']==light.name:pair['energy']=watts

# R26: bay-scale impact architecture, retaining every original plan boundary.
# Cast residue piers, bolted shield guard frames and folded quarantine shoulders
# carry different loads and create distinct silhouettes from the freight aisle.
shield_frame_mat=material('Shield bay worn protective frame',(.105,.113,.084),.76,.34)
quarantine_frame_mat=material('Quarantine formed blue steel',(.073,.118,.119),.79,.24)
def angular_pier(label,cx,cy,height,width,depth,mat):
 poly=[(cx-width/2,0),(cx+width/2,0),(cx+width/2,.23),(cx+width*.31,.36),(cx+width*.31,height-.25),(cx+width*.19,height),(cx-width*.19,height),(cx-width*.31,height-.25),(cx-width*.31,.36),(cx-width/2,.23)]
 v,f=prism_points(poly,'Y',cy-depth/2,cy+depth/2);pier=mesh(label,v,f,mat);outward_mesh(pier);support(pier,'Floor',(cx,cy,0));return pier
for idx,cy in [(0,4.8),(1,8.8)]:
 for side,cx in enumerate([-5.79,-2.36]):
  pier=angular_pier('Residue '+str(idx)+' cast impact shoulder '+str(side),cx,cy,1.27,.36,.21,original_mats['Replacement cast concrete'])
  shoe=cube('Residue shoulder replaceable rub plate '+str(idx)+' '+str(side),(cx,cy-.108,.45),(.145,.006,.44),original_mats['Oxide painted steel'],.002);intrinsic(shoe,pier,'Replaceable plate bolted onto cast impact shoulder')
  for zz in [.27,.63]:
   o=cyl('Residue rub plate recessed fastener '+str(idx)+' '+str(side)+' '+str(zz),(cx,cy-.113,zz),.011,.007,steel,6);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,pier,'Captive face bolt through replaceable impact shoe')
for idx,cy in [(2,9.4),(3,13.4)]:
 posts=[]
 for side,cx in enumerate([-5.79,-2.36]):
  pier=angular_pier('Shield '+str(idx)+' bolted guard upright '+str(side),cx,cy,1.35,.34,.22,shield_frame_mat);posts.append(pier)
  for zz in [.22,1.23]:
   plate=cube('Shield guard joint shoe '+str(idx)+' '+str(side)+' '+str(zz),(cx,cy-.114,zz),(.17,.012,.145),edge,.003);intrinsic(plate,pier,'Bolted shoe ties the impact frame into its cast mounting foot')
   for dx in [-.052,.052]:
    o=cyl('Shield guard shoe captive bolt '+str(idx)+' '+str(side)+' '+str(zz)+' '+str(dx),(cx+dx,cy-.123,zz),.013,.007,steel,6);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,plate,'Captive hex fixing through the guard joint shoe')
 for side,(xa,xb) in enumerate([(-5.79,-5.10),(-2.90,-2.36)]):
  rail=cube('Shield '+str(idx)+' open service corner guard '+str(side),((xa+xb)/2,cy,1.285),(xb-xa,.13,.09),shield_frame_mat,.004);intrinsic(rail,posts[side],'Short impact wing joins its upright while leaving the protected cask service frontage open')
  cx=-5.63 if side==0 else -2.52;section=[(cx-.07,1.10),(cx+.07,1.10),(cx+.07,1.265),(cx+.03,1.320),(cx-.07,1.320)];v,f=prism_points(section,'Y',cy-.055,cy+.055);o=mesh('Shield guard wing welded return '+str(idx)+' '+str(side),v,f,shield_frame_mat);outward_mesh(o);intrinsic(o,rail,'Welded corner return seats the impact wing over the original containment coping')

for idx,cy in [(6,9.4),(7,13.4)]:
 for side,cx in enumerate([2.33,5.80]):
  pier=angular_pier('Quarantine '+str(idx)+' folded impact shoulder '+str(side),cx,cy,1.34,.30,.18,quarantine_frame_mat)
  # Formed triangular gusset links the raised shoulder into the existing top coping.
  inner=cx+.27 if side==0 else cx-.27
  poly=[(cx,1.12),(inner,1.12),(cx,1.33)];v,f=prism_points(poly,'Y',cy-.071,cy-.059);o=mesh('Quarantine folded corner gusset '+str(idx)+' '+str(side),v,f,quarantine_frame_mat);outward_mesh(o);intrinsic(o,pier,'Triangular welded shoulder return stiffens the containment coping')
  for zz in [.26,1.20]:
   o=cyl('Quarantine shoulder fixing '+str(idx)+' '+str(side)+' '+str(zz),(cx,cy-.095,zz),.012,.010,steel,6);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,pier,'Retained hex fastener through the folded containment shoulder')

# Built-in receiving inspection shelf: fixed to the booth base below its window,
# before the protected door swing, and entirely outside the central route.
back=cube('Receiving inspection shelf wall cleat',(-2.347,1.025,.835),(.006,.94,.21),original_mats['Structural warm graphite'],.002);support(back,'Booth side base',(-2.350,1.025,.835),(-1,0,0))
for yy in [.64,1.41]:
 poly=[(-2.344,.740),(-2.344,.951),(-2.011,.951)];v,f=prism_points(poly,'Y',yy-.012,yy+.012);o=mesh('Receiving shelf welded bracket '+str(yy),v,f,edge);outward_mesh(o);intrinsic(o,back,'Pressed triangular bracket welded to booth-fixed shelf cleat')
shelf=cube('Receiving fixed inspection tray',(-2.183,1.025,.958),(.340,.95,.014),steel,.003);intrinsic(shelf,back,'Folded tray seats on the two triangular wall brackets')
for label,pos,dims in [('front',(-2.012,1.025,.978),(.006,.95,.040)),('south',(-2.183,.552,.978),(.340,.006,.040)),('north',(-2.183,1.498,.978),(.340,.006,.040))]:
 o=cube('Receiving tray folded '+label+' return',pos,dims,steel,.002);intrinsic(o,shelf,'Folded return retains inspection paperwork within the fixed tray')
# A used mechanical hold stamp and clipped receipt stack belong to this surface.
receipts=cube('Receiving dog-eared receipt stack',(-2.198,.98,.968),(.18,.25,.006),paper,.001);support(receipts,shelf.name,(-2.198,.98,.965))
for yy in [.914,.947,.980,1.013]:
 o=cube('Receiving faded form rule '+str(yy),(-2.198,yy,.9711),(.14,.0006,.0002),ink);intrinsic(o,receipts,'Printed rule on the top receiving receipt')
clip=cube('Receiving receipt steel keeper',(-2.20,1.097,.976),(.09,.014,.010),edge,.001);intrinsic(clip,receipts,'Spring keeper grips the upper edge of the used receipt stack')
stamp=cube('Receiving hold stamp base',(-2.18,1.29,.974),(.08,.11,.018),rubber,.002);support(stamp,shelf.name,(-2.18,1.29,.965))
o=cyl('Receiving hold stamp worn grip',(-2.18,1.29,1.015),.021,.065,wood,12);intrinsic(o,stamp,'Wood handle tenoned into the mechanical rubber stamp base')
stain_material(shelf,[((-2.09,.78,.965),(14,6,1)),((-2.21,1.29,.965),(12,14,1))],'Receiving handling oil',(.19,.22,.15),.65)

# A fixed service clamp holds one section of the rejected seal against the worktop.
# Both seals remain uninstalled; the removal blade still holds the cut end raised.
clamp_base=cube('Seal service bench clamp mounting foot',(4.379,16.955,top+.008),(.12,.11,.016),original_mats['Oxide painted steel'],.003);support(clamp_base,worktop.name,(4.379,16.955,top))
for yy in [16.920,16.990]:
 o=cyl('Seal clamp bench captive mounting screw '+str(yy),(4.356,yy,top+.019),.010,.006,steel,6);intrinsic(o,clamp_base,'Countersunk captive fixing through the fixed clamp foot')
poly=[(4.35,top+.016),(4.382,top+.016),(4.382,top+.086),(4.510,top+.086),(4.510,top+.110),(4.35,top+.110)];v,f=prism_points(poly,'Y',16.942,16.968);bridge=mesh('Seal service fixed C clamp bridge',v,f,original_mats['Oxide painted steel']);outward_mesh(bridge);intrinsic(bridge,clamp_base,'Cast cantilever rises from the bench-fixed clamp foot')
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update();seal_tree=BVHTree.FromPolygons([removed.matrix_world@v.co for v in removed.data.vertices],[list(p.vertices) for p in removed.data.polygons]);hit,n,ix,dist=seal_tree.ray_cast(Vector((4.485,16.955,top+.2)),Vector((0,0,-1)),.25)
assert hit is not None,'Seal clamp pressure shoe must seat on the actual failed part'
shoe=cyl('Seal service swiveling pressure shoe',hit+Vector((0,0,.003)),.013,.006,steel,16);intrinsic(shoe,bridge,'Swiveling pressure shoe seats on the rejected seal profile')
shaftbottom=hit.z+.006;shafttop=top+.139
o=cyl('Seal clamp threaded pressure spindle',(4.485,16.955,(shaftbottom+shafttop)/2),.0055,shafttop-shaftbottom,steel,16);intrinsic(o,bridge,'Threaded pressure spindle passes through the cast clamp bridge')
o=cyl('Seal clamp captured sliding crossbar',(4.485,16.955,top+.135),.004,.087,edge,12);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,bridge,'Sliding crossbar turns the captive pressure spindle')
for yy in [16.913,16.997]:
 o=cyl('Seal clamp crossbar retaining head '+str(yy),(4.485,yy,top+.135),.006,.006,edge,12);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,bridge,'Peened head retains the clamp crossbar')

# Reduce the repeated ceiling bars' dominance using their existing seated sources.
for pair in fixture_pairs:
 source_obj=bpy.data.objects[pair['source']]
 if source_obj.name in ['Practical pool','Practical pool.009'] and not pair['failed']:
  source_obj.data.energy=28;pair['energy']=28
  for m in bpy.data.objects[pair['lens']].data.materials:
   bsdf(m).inputs['Emission Strength'].default_value=.30
  pair['emission']=.30
s['architecture_revision']='Distinct cast residue shoulders / shield impact frames / quarantine folded returns; fixed receiving inspection tray and seal clamp'

# R27: true bored clamp bridge; the pressure spindle has clearance through the casting.
bridge=bpy.data.objects['WS | Seal service fixed C clamp bridge']
bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0062,depth=.08,location=(4.485,16.955,top+.10));cutter=bpy.context.object
bpy.context.view_layer.objects.active=bridge;mod=bridge.modifiers.new('Actual pressure spindle casting bore','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);bridge['overhaul_modified']=True
s['seal_service_clamp_bored']=True

# Project crisp paint loss onto actual curved vessel faces. These small scars follow
# collar/handling zones and leave most of the coating quiet; no global grunge field.
chip_primer=material('Old exposed vessel undercoat',(.230,.220,.180),.94,.02)
chip_steel=material('Oxidized steel beneath vessel coating',(.270,.285,.260),.88,.12)
outline=[(-.50,-.18),(-.42,-.29),(-.31,-.25),(-.19,-.39),(-.05,-.32),(.08,-.42),(.23,-.30),(.38,-.27),(.48,-.10),(.45,.08),(.34,.19),(.21,.15),(.08,.27),(-.08,.20),(-.23,.30),(-.36,.15),(-.46,.17)]
def projected_coating_loss(rootname,label,yoffset,z,width,height):
 body=next(o for o in bpy.data.objects[rootname].children_recursive if o.type=='MESH' and o.name.startswith('Continuous inner vessel'))
 dg=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(dg);me=evaluated.to_mesh();body_tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);evaluated.to_mesh_clear();centre=bpy.data.objects[rootname].matrix_world.translation
 rng=random.Random(rootname+label);angle=rng.uniform(-.08,.08);local_outline=[]
 for u,v in outline:
  factor=rng.uniform(.90,1.05);local_outline.append(((u*math.cos(angle)-v*math.sin(angle))*factor,(u*math.sin(angle)+v*math.cos(angle))*factor))
 for layer,scale,offset,mat in [('primer',1.0,.00022,chip_primer),('metal',.94,.00032,chip_steel)]:
  # Tessellate in the Y/Z plane before projecting every vertex onto the shell.
  # Large chord triangles sink beneath curved shells even when their corners seat.
  coords=[];lookup={};faces=[]
  def vertex_id(point):
   key=tuple(round(value,10) for value in point)
   if key not in lookup:lookup[key]=len(coords);coords.append(point)
   return lookup[key]
  for edge_index,A in enumerate(local_outline):
   B=local_outline[(edge_index+1)%len(local_outline)];C=(0,0)
   points=[(u*scale*width,v*scale*height) for u,v in [A,B,C]]
   longest=max(math.dist(points[i],points[(i+1)%3]) for i in range(3));divisions=max(2,math.ceil(longest/.0045));indices={}
   for i in range(divisions+1):
    for j in range(divisions-i+1):
     u=A[0]*(1-(i+j)/divisions)+B[0]*i/divisions;v=A[1]*(1-(i+j)/divisions)+B[1]*i/divisions
     indices[(i,j)]=vertex_id((u*scale,v*scale))
   for i in range(divisions):
    for j in range(divisions-i):
     faces.append((indices[(i,j)],indices[(i+1,j)],indices[(i,j+1)]))
     if i+j+1<divisions:faces.append((indices[(i+1,j)],indices[(i+1,j+1)],indices[(i,j+1)]))
  verts=[];normals=[]
  for u,v in coords:
   hit,n,ix,dist=body_tree.ray_cast(Vector((centre.x+1.2,centre.y+yoffset+u*width,z+v*height)),Vector((-1,0,0)),2.4)
   assert hit is not None,(rootname,label,layer,u,v)
   verts.append(tuple(hit+n*offset));normals.append(n)
  o=mesh(rootname+' '+label+' coating loss '+layer,verts,faces,mat)
  # Triangle normals face away from the vessel, while every vertex follows its real shell.
  if o.data.polygons[0].normal.x<0:
   for poly in o.data.polygons:poly.flip()
  o.data.update();support(o,body.name,verts[0],-normals[0]);o['surface_projected']=True
for parameters in [('SC01','upper collar handling',.24,1.985,.15,.060),('SC01','lower carrier rub',-.21,.555,.17,.065),('SC02','old jacket seam',-.24,1.70,.038,.25),('RA01','clamp handling',.17,1.025,.12,.050),('RA02','lower sealed collar rub',-.19,.555,.14,.060),('RA03','upper collar scar',.18,1.025,.13,.045)]:projected_coating_loss(*parameters)

# Formed freight coamings provide impact protection beyond the original seal tracks.
# Clear openings and host anchors stay exact; the shoulders sit on the existing floor.
portalcoat=material('Freight coaming worn blue steel',(.105,.127,.117),.79,.27)
def freight_coaming(label,halfwidth,cy,openingheight):
 posts=[];bilateral=label=='Receiving';faces=(-1,1) if bilateral else (-1,)
 for side,sign in enumerate([-1,1]):
  inner=halfwidth+.006;outer=halfwidth+.41
  poly=[(sign*inner,0),(sign*outer,0),(sign*outer,.34),(sign*(outer-.055),.48),(sign*(outer-.055),openingheight+.13),(sign*(outer-.15),openingheight+.33),(sign*inner,openingheight+.33)]
  v,f=prism_points(poly,'Y',cy-.11,cy+.11);post=mesh(label+' formed impact coaming '+str(side),v,f,portalcoat);outward_mesh(post);support(post,'Floor',(sign*(inner+.12),cy,0));posts.append(post)
  pocket_low=.84;pocket_high=openingheight-.17
  for face in faces:
   tag=' internal' if face==1 else ''
   pocket_y=cy+face*.063 if bilateral else cy-.021;depth=.118 if bilateral else .246
   cut_volume(post,label+' hollow impact jamb channel '+str(side)+tag,(sign*(halfwidth+.178),pocket_y,(pocket_low+pocket_high)/2),(.265,depth,pocket_high-pocket_low))
   shoe=cube(label+' replaceable coaming foot shoe '+str(side)+tag,(sign*(inner+.18),cy+face*.117,.44),(.26,.014,.62),original_mats['Structural warm graphite'],.004);intrinsic(shoe,post,'Replaceable face shoe bolts through the folded freight coaming')
   for dx in [-.075,.075]:
    for zz in [.20,.68]:
     o=cyl(label+' foot shoe captive bolt '+str(side)+' '+str(dx)+' '+str(zz)+tag,(sign*(inner+.18)+dx,cy+face*.128,zz),.014,.007,steel,6);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,shoe,'Hex fastener retains the impact shoe against the formed jamb')
   for index,(zz,dz,dx) in enumerate([(.30,.05,.13),(.61,.025,.08),(.54,.075,.18)]):
    xc=sign*(inner+dx);verts=[(xc-.041,cy+face*.1242,zz),(xc+.045,cy+face*.1242,zz+.006),(xc+.025,cy+face*.1242,zz+dz),(xc-.027,cy+face*.1242,zz+dz*.77)];winding=(0,1,2,3) if face==-1 else (3,2,1,0);o=mesh(label+' old coaming scrape '+str(side)+' '+str(index)+tag,verts,[winding],edge);intrinsic(o,shoe,'Exposed contact scar on the replaceable wheel-impact shoe')
 header=cube(label+' angular freight crown',(0,cy,openingheight+.22),(2*(halfwidth+.31),.22,.23),portalcoat,.005);intrinsic(header,posts[0],'Formed header overlaps and seats in both jamb shoulders above the clear opening')
 for face in faces:
  tag=' internal' if face==1 else ''
  pocket_y=cy+face*.063 if bilateral else cy-.021;depth=.118 if bilateral else .246
  cut_volume(header,label+' recessed crown channel'+tag,(0,pocket_y,openingheight+.225),(2*halfwidth-.12,depth,.112))
  for side,sign in enumerate([-1,1]):
   poly=[(sign*(halfwidth+.013),openingheight+.025),(sign*(halfwidth+.080),openingheight+.025),(sign*(halfwidth+.080),openingheight+.245),(sign*(halfwidth+.295),openingheight+.245),(sign*(halfwidth+.295),openingheight+.320),(sign*(halfwidth+.013),openingheight+.320)]
   near,far=sorted([cy+face*.124,cy+face*.110]);v,f=prism_points(poly,'Y',near,far);joint=mesh(label+' formed L corner connection '+str(side)+tag,v,f,edge);outward_mesh(joint);intrinsic(joint,posts[side],'Bolted L plate ties the folded jamb return to the freight crown')
   for dx,zz in [(.047,.055),(.047,.285),(.250,.285)]:
    o=cyl(label+' corner joint retained hex '+str(side)+' '+str(dx)+' '+str(zz)+tag,(sign*(halfwidth+dx),cy+face*.128,openingheight+zz),.013,.008,steel,6);o.rotation_euler=(math.pi/2,0,0);intrinsic(o,joint,'Captured hex head seats against the jamb-to-crown connection plate')
  o=cube(label+' folded crown contact lip'+tag,(0,cy+face*.116,openingheight+.116),(2*(halfwidth+.24),.012,.020),edge,.002);intrinsic(o,header,'Folded lower crown lip is above the reserved clear opening')
 return posts,header
freight_coaming('Dispatch',1.20,17.64,2.80)
freight_coaming('Receiving',1.50,.37,3.20)
s['freight_coamings_openings_preserved']=True
s['tessellated_vessel_losses']=True

# R34: hollow, seated coupling explains the filter-to-centrifugal-fan connection.
fan_y=16.08;fan_z=1.40
coupling_rings=[(-3.9565,.315),(-3.91,.315),(-3.78,.278),(-3.692,.265),(-3.692,.235),(-3.78,.248),(-3.91,.285),(-3.9565,.285)]
verts=[];N=32
for xx,radius in coupling_rings:
 for j in range(N):
  angle=j*2*math.pi/N;verts.append((xx,fan_y+radius*math.cos(angle),fan_z+radius*math.sin(angle)))
faces=[(ring*N+j,ring*N+(j+1)%N,((ring+1)%len(coupling_rings))*N+(j+1)%N,((ring+1)%len(coupling_rings))*N+j) for ring in range(len(coupling_rings)) for j in range(N)]
collar=remesh('Fan inlet collar',verts,faces,steel);outward_mesh(collar);support(collar,plenum.name,(-3.955,fan_y+.300,fan_z),(-1,0,0))
for poly in collar.data.polygons:
 if abs(poly.normal.x)<.95:poly.use_smooth=True
def axial_air_opening(obj,label,cx,cy,cz,radius,depth):
 bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=radius,depth=depth,location=(cx,cy,cz),rotation=(0,math.pi/2,0));cutter=bpy.context.object
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);obj['overhaul_modified']=True
axial_air_opening(plenum,'Actual open filter-to-fan port',-3.955,fan_y,fan_z,.285,.10)
axial_air_opening(bpy.data.objects['Filter outlet bolted adapter'],'Open inherited filter outlet adapter',-3.98,fan_y,fan_z,.285,.20)
volute=bpy.data.objects['Centrifugal volute'];bpy.context.view_layer.update();worldverts=[volute.matrix_world@v.co for v in volute.data.vertices];xmin=min(v.x for v in worldverts);xmax=max(v.x for v in worldverts)
innerverts=[(xmin+.025 if abs(v.x-xmin)<abs(v.x-xmax) else xmax-.025,fan_y+(v.y-fan_y)*.86,fan_z+(v.z-fan_z)*.86) for v in worldverts]
cutter=mesh('Temporary fan actual chamber cutter',innerverts,[tuple(poly.vertices) for poly in volute.data.polygons],steel);outward_mesh(cutter);bpy.context.view_layer.objects.active=volute;mod=volute.modifiers.new('Actual hollow centrifugal fan chamber','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);volute['overhaul_modified']=True
axial_air_opening(volute,'Actual inlet through fan chamber',-3.720,fan_y,fan_z,.235,.14)
axial_air_opening(bpy.data.objects['Fan casing bolted seam'],'Open bolted inlet plate',-3.715,fan_y,fan_z,.235,.14)
# A supported annular flange and captive fasteners keep the new port a built assembly.
verts=[]
for xx,radius in [(-3.954,.340),(-3.942,.340),(-3.942,.285),(-3.954,.285)]:
 for j in range(N):
  angle=j*2*math.pi/N;verts.append((xx,fan_y+radius*math.cos(angle),fan_z+radius*math.sin(angle)))
faces=[(ring*N+j,ring*N+(j+1)%N,((ring+1)%4)*N+(j+1)%N,((ring+1)%4)*N+j) for ring in range(4) for j in range(N)];flange=mesh('Fan inlet open bolted plenum flange',verts,faces,edge);outward_mesh(flange);intrinsic(flange,collar,'Open annular flange captures the reducer over the actual plenum port')
for j in range(8):
 angle=j*2*math.pi/8;o=cyl('Fan coupling captive flange hex '+str(j),(-3.937,fan_y+.325*math.cos(angle),fan_z+.325*math.sin(angle)),.010,.010,steel,6);o.rotation_euler=(0,math.pi/2,0);intrinsic(o,flange,'Captive hex head seats on the plenum-to-fan flange')
# Static rotor lies inside the opened volute, attached to its existing motor shaft.
shaft_end=xmax-.024
shaft=cyl('Fan retained impeller shaft',((-3.550+shaft_end)/2,fan_y,fan_z),.025,shaft_end+3.550,steel,24);shaft.rotation_euler=(0,math.pi/2,0);support(shaft,volute.name,(xmax-.025,fan_y,fan_z),(1,0,0))
hub=cyl('Fan actual impeller hub',(-3.550,fan_y,fan_z),.060,.048,original_mats['Structural warm graphite'],24);hub.rotation_euler=(0,math.pi/2,0);intrinsic(hub,shaft,'Static impeller hub is retained on its seated fan shaft')
for index in range(9):
 angle=index*2*math.pi/9;poly=[]
 for radius,offset in [(.055,-.06),(.205,.15),(.214,.20),(.063,.06)]:
  poly.append((fan_y+radius*math.cos(angle+offset),fan_z+radius*math.sin(angle+offset)))
 v,f=prism_points(poly,'X',-3.566,-3.534);o=mesh('Fan formed impeller vane '+str(index),v,f,steel);outward_mesh(o);intrinsic(o,hub,'Formed static vane is welded to the retained impeller hub')
s['fan_inlet_open_seated']=True
s['fan_chamber_x_bounds']=[xmin+.025,xmax-.025]

# R36: hierarchy comes from the modeled task fixtures and muted capture surfaces.
for pair in fixture_pairs:
 light=bpy.data.objects[pair['source']]
 if pair['failed']:continue
 if light.name.startswith('Practical pool'):
  powers={'Practical pool':20,'Practical pool.001':145,'Practical pool.002':75,'Practical pool.003':95,'Practical pool.004':205,'Practical pool.005':85,'Practical pool.006':115,'Practical pool.009':20}
  light.data.energy=powers[light.name];pair['energy']=light.data.energy
  emission=.18 if light.data.energy<=80 else .28
  for mat in bpy.data.objects[pair['lens']].data.materials:bsdf(mat).inputs['Emission Strength'].default_value=emission
  pair['emission']=emission
 if light.name=='WS | Inventory task tube emitter':light.data.energy=7;pair['energy']=7
# Welded hat channels reinforce the inside of the open quarantine cover.
# Their seats are measured on its real underside, keeping the original lid pose.
lid=bpy.data.objects['Folded lid.002'];bpy.context.view_layer.update();evaluated=lid.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();bv=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in me.vertices],[list(poly.vertices) for poly in me.polygons]);evaluated.to_mesh_clear();direction=(lid.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
for index,yy in enumerate([-.19,.19]):
 origin=lid.matrix_world@Vector((0,yy,-.15));hit,n,face,d=bv.ray_cast(origin,direction,.25);assert hit is not None
 zz=(lid.matrix_world.inverted()@hit).z
 section=[(yy-.047,zz+.0005),(yy-.026,zz-.019),(yy+.026,zz-.019),(yy+.047,zz+.0005),(yy+.047,zz-.0015),(yy+.026,zz-.021),(yy-.026,zz-.021),(yy-.047,zz-.0015)]
 v,f=prism_points(section,'X',-.84,.84);v=[tuple(lid.matrix_world@Vector(point)) for point in v];rib=mesh('Quarantine lid welded inner hat channel '+str(index),v,f,original_mats['Galvanized bus casing']);outward_mesh(rib);support(rib,lid.name,hit,direction);aged_finish(rib,(.14,.155,.135),520+index,False,.24)
s['hierarchy_revision']='Muted integral capture mouths, subtle aged lower wash, stronger work pools and subdued ceiling lens brightness; real quarantine-cover hat reinforcement'
