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
  for j,v in enumerate(attr.data):v.value=.17*max(0,math.sin(math.pi*(j//2)/(N-1)))**.5*(.65+.35*math.sin(j*.44)**2)
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
 m=material(obj.name+' aged finish',paint,.82,.12);obj.data.materials.clear();obj.data.materials.append(m)
 ns=m.node_tree.nodes;ls=m.node_tree.links;shader=bsdf(m)
 geo=ns.new('ShaderNodeNewGeometry');coord=ns.new('ShaderNodeVectorMath');coord.operation='ADD';coord.inputs[1].default_value=(seed*1.73,seed*3.13,seed*.71);ls.new(geo.outputs['Position'],coord.inputs[0])
 broad=ns.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=4.8;broad.inputs['Detail'].default_value=2;ls.new(coord.outputs['Vector'],broad.inputs['Vector'])
 fine=ns.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=33;fine.inputs['Detail'].default_value=1;ls.new(coord.outputs['Vector'],fine.inputs['Vector'])
 mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';ls.new(broad.outputs['Fac'],mul.inputs[0]);ls.new(fine.outputs['Fac'],mul.inputs[1])
 ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.27;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.43-amount*.025;ramp.color_ramp.elements[1].color=(1,1,1,1);ls.new(mul.outputs[0],ramp.inputs[0])
 mask=ramp.outputs['Color']
 if lower:
  split=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],split.inputs[0]);height=ns.new('ShaderNodeMapRange');height.inputs['From Min'].default_value=.42;height.inputs['From Max'].default_value=1.02;height.inputs['To Min'].default_value=1;height.inputs['To Max'].default_value=.12;height.clamp=True;ls.new(split.outputs['Z'],height.inputs['Value']);mul2=ns.new('ShaderNodeMath');mul2.operation='MULTIPLY';ls.new(mask,mul2.inputs[0]);ls.new(height.outputs['Result'],mul2.inputs[1]);mask=mul2.outputs[0]
 # The two long dimensions locate actual panel rims; thin face depth is excluded.
 if not obj.name.startswith('Continuous inner vessel'):
  localspan=[max(v[i] for v in obj.bound_box)-min(v[i] for v in obj.bound_box) for i in range(3)]
  # Generated coordinates are normalized within the actual mesh, independent of the assembly pose.
  axes=[2] if obj.name.startswith('Protective forged collar') else sorted(range(3),key=lambda i:obj.dimensions[i],reverse=True)[:2]
  tex=ns.new('ShaderNodeTexCoord');split=ns.new('ShaderNodeSeparateXYZ');ls.new(tex.outputs['Generated'],split.inputs[0]);edge_masks=[]
  for axis in axes:
   sub=ns.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5;ls.new(split.outputs[axis],sub.inputs[0]);absolute=ns.new('ShaderNodeMath');absolute.operation='ABSOLUTE';ls.new(sub.outputs[0],absolute.inputs[0]);edgefade=ns.new('ShaderNodeMapRange');edgefade.inputs['From Min'].default_value=.31;edgefade.inputs['From Max'].default_value=.47;edgefade.clamp=True;ls.new(absolute.outputs[0],edgefade.inputs['Value']);edge_masks.append(edgefade.outputs[0])
  maximum=ns.new('ShaderNodeMath');maximum.operation='MAXIMUM';ls.new(edge_masks[0],maximum.inputs[0]);ls.new(edge_masks[-1],maximum.inputs[1]);gated=ns.new('ShaderNodeMath');gated.operation='MULTIPLY';ls.new(mask,gated.inputs[0]);ls.new(maximum.outputs[0],gated.inputs[1]);mask=gated.outputs[0]
 mix=ns.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*paint,1);mix.inputs[2].default_value=(.065,.032,.013,1);ls.new(mask,mix.inputs[0]);ls.new(mix.outputs[0],shader.inputs['Base Color'])
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
 rings=[(.027,.80),(0,1.0),(0,0),(.006,0),(.006,.94),(.027,.74)];verts=[]
 for inset,z in rings:
  for u,v in outline:verts.append(obj.matrix_world@(lo+Vector(((inset+u*(1-2*inset))*span.x,(inset+v*(1-2*inset))*span.y,z*span.z))))
 faces=[tuple(range(8)),tuple(reversed(range(40,48)))]+[(r*8+i,(r+1)*8+i,(r+1)*8+(i+1)%8,r*8+(i+1)%8) for r in range(5) for i in range(8)]
 mat=obj.data.materials[0];remesh(name,verts,faces,mat)
# A spent pleated filter stands entirely within the open quarantine tub's closure envelope.
x,y,z=4.65,11.15,.300;N=48;verts=[]
for radius,height in [(.15,z),(.15,z+.76),(.07,z+.76),(.07,z)]:
 for i in range(N):
  a=i*2*math.pi/N;r=radius+(.009 if radius>.1 and i%2==0 else 0);verts.append((x+r*math.cos(a),y+r*math.sin(a),height))
faces=[(r*N+i,r*N+(i+1)%N,((r+1)%4)*N+(i+1)%N,((r+1)%4)*N+i) for r in range(4) for i in range(N)]
obj=mesh('Quarantined spent pleated filter',verts,faces,cloth);support(obj,'Tub floor.002',(x+.15,y,z));aged_finish(obj,(.22,.205,.13),81,True,.55)
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
   verts.append((value,a,b) if axis=='X' else (a,b,value))
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
 a=i*2*math.pi/6;o=cyl('Overpack closure captive bolt '+str(i),(cx+.18*math.cos(a),cy+.18*math.sin(a),cz+.448),.012,.016,steel,6);intrinsic(o,overpack,'Captive closure bolt through bolted lid')
# Attached faded hold tag belongs to the actual incoming load.
o=cube('Incoming overpack hold tag',(cx-.21,cy,cz+.27),(.003,.12,.09),paper);intrinsic(o,overpack,'Paper transport tag held against the overpack wall')
# The extractor is an actual hollow plenum with sealed filter inspection windows.
def cut_volume(obj,name,pos,dims):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);cutter=bpy.context.object;cutter.name='TEMP | '+name;cutter.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);obj['overhaul_modified']=True # Preserve Boolean's inward cavity normals.
clear_window=material('Dusty transmissive inspection glass',(.62,.66,.57),.16);bsdf(clear_window).inputs['Transmission Weight'].default_value=1;bsdf(clear_window).inputs['IOR'].default_value=1.46
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
def glove_loft(name,sections,centre,angle):
 verts=[];N=8
 for x,y,z,w,h in sections:
  for i in range(N):
   a=i*2*math.pi/N;xx=x+w*math.cos(a);zz=z+h*math.sin(a);verts.append((centre[0]+xx*math.cos(angle)-y*math.sin(angle),centre[1]+xx*math.sin(angle)+y*math.cos(angle),top+zz))
 faces=[tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))]+[(r*N+i,r*N+(i+1)%N,(r+1)*N+(i+1)%N,(r+1)*N+i) for r in range(len(sections)-1) for i in range(N)]
 if name in bpy.data.objects:o=remesh(name,verts,faces,glove_mat)
 else:o=mesh(name,verts,faces,glove_mat)
 outward_mesh(o);return o
for hand in range(2):
 centre=(5.23+hand*.095,16.48+hand*.055);angle=.23-hand*.45;rootname='WS | Slumped glove '+str(hand)
 palm=glove_loft(rootname,[(0,-.074,.009,.028,.006),(0,-.042,.012,.035,.010),(0,0,.016,.039,.016),(0,.032,.014,.037,.010)],centre,angle)
 for finger,(x,length) in enumerate([(-.026,.043),(-.009,.070),(.009,.063),(.026,.044)]):
  o=glove_loft('Glove '+str(hand)+' collapsed finger '+str(finger),[(x,.025,.013,.010,.007),(x,.045,.017,.009,.007),(x-.003,.055+length*.4,.024,.008,.005),(x-.006,.030+length,.015,.004,.003)],centre,angle);intrinsic(o,palm,'Bent cloth finger sewn into glove palm')
 o=glove_loft('Glove '+str(hand)+' creased thumb',[(.029,-.008,.012,.012,.008),(.048,.008,.017,.010,.007),(.059,.025,.012,.005,.004)],centre,angle);intrinsic(o,palm,'Sewn thumb of collapsed work glove')

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
 width=ns.new('ShaderNodeMath');width.operation='MULTIPLY';width.inputs[1].default_value=.24;ls.new(noise.outputs['Fac'],width.inputs[0]);height=ns.new('ShaderNodeMath');height.operation='ADD';ls.new(split.outputs['Z'],height.inputs[0]);ls.new(width.outputs[0],height.inputs[1]);band=ns.new('ShaderNodeMapRange');band.inputs['From Min'].default_value=1.26;band.inputs['From Max'].default_value=1.46;band.inputs['To Min'].default_value=1;band.inputs['To Max'].default_value=0;band.clamp=True;ls.new(height.outputs[0],band.inputs[0])
 mix=ns.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.065,.095,.078,1);ls.new(base,mix.inputs[1]);ls.new(band.outputs[0],mix.inputs[0]);base=mix.outputs[0]
 # Sparse paint delamination is bounded to the high-impact base band.
 tear=ns.new('ShaderNodeValToRGB');tear.color_ramp.elements[0].position=.59;tear.color_ramp.elements[1].position=.68;ls.new(noise.outputs['Fac'],tear.inputs[0]);mask=ns.new('ShaderNodeMath');mask.operation='MULTIPLY';ls.new(tear.outputs[0],mask.inputs[0]);ls.new(band.outputs[0],mask.inputs[1]);chip=ns.new('ShaderNodeMixRGB');chip.inputs[2].default_value=(.165,.157,.120,1);ls.new(mask.outputs[0],chip.inputs[0]);ls.new(base,chip.inputs[1]);ls.new(chip.outputs[0],b.inputs['Base Color']);b.inputs['Roughness'].default_value=.96
 bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.0018;ls.new(mask.outputs[0],bump.inputs['Height']);ls.new(bump.outputs[0],b.inputs['Normal'])
# Strong wet streaks grow from a few failed service seams; most upper panels stay quiet.
for name,spots in [('West Wall',[((-6,12.85,2.22),(1,1.05,.82)),((-6,13.10,1.35),(1,4,1.05)),((-6,9.20,2.64),(1,3.6,.85))]),('East Wall.001',[((6,12.95,2.60),(1,1.8,.62)),((6,13.10,1.9),(1,6,.75)),((6,16.72,3.0),(1,2.8,.7))]),('Dispatch wall',[((-3.70,18,2.5),(1.45,1,.8)),((-3.75,18,1.35),(4.5,1,.9))])]:
 stain_material(bpy.data.objects[name],spots,'Visible service seepage '+name,(.10,.16,.08),.94)
# Shallow irregular spalls remove actual wall material, leaving a jagged aggregate recess.
aggregate=material('Exposed old wall aggregate',(.14,.137,.103),.99);weather(aggregate,(.14,.137,.103),.99,0,18,.16)
for idx,(name,y,z,w,h,side) in enumerate([('West Wall',12.80,2.13,.86,.73,-1),('West Wall',6.10,1.56,.54,.46,-1),('East Wall.001',12.86,2.05,.73,.55,1),('East Wall.001',16.72,2.58,.60,.38,1)]):
 wall=bpy.data.objects[name];wall.data.materials.append(aggregate);verts=[];outline=[(-.50,-.20),(-.38,-.48),(-.10,-.50),(.16,-.38),(.44,-.40),(.50,-.13),(.32,.05),(.49,.23),(.27,.43),(-.02,.5),(-.16,.28),(-.44,.32)];N=len(outline)
 for x in [side*5.985,side*6.026]:verts.extend([(x,y+u*w,z+v*h) for u,v in outline])
 faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 cutter=mesh('Wall spall cutter '+str(idx),verts,faces,aggregate);outward_mesh(cutter);bpy.context.view_layer.update();mod=wall.modifiers.new('Actual shallow aggregate loss '+str(idx),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);wall['overhaul_modified']=True
# Cask heads have a pressed crown and thin underside, while their lifting pads stay seated.
for idx,name in enumerate(['Shallow dished cover','Shallow dished cover.001','Shallow dished cover.002','Shallow dished cover.003','Shallow dished cover.004']):
 o=bpy.data.objects[name];cx,cy,cz=o.matrix_world.translation;rad=.3698 if idx<3 else .4902;N=32;verts=[]
 rings=[(rad,cz-.035),(rad,cz-.005),(rad*.91,cz+.016),(.12 if idx<3 else .19,cz+.025),(.09 if idx<3 else .15,cz+.058),(.04 if idx<3 else .07,cz+.078),(.04 if idx<3 else .07,cz+.070),(.09 if idx<3 else .15,cz+.050),(.12 if idx<3 else .19,cz+.017),(rad*.91,cz+.008),(rad-.006,cz-.005),(rad-.006,cz-.035)]
 for radius,z in rings:
  for j in range(N):a=j*2*math.pi/N;verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z))
 faces=[(r*N+j,r*N+(j+1)%N,((r+1)%len(rings))*N+(j+1)%N,((r+1)%len(rings))*N+j) for r in range(len(rings)) for j in range(N)]
 # Close both inner central discs, rather than connecting through a hole.
 faces=[f for f in faces if min(f)//N!=5];faces.extend([tuple(range(5*N,6*N)),tuple(reversed(range(6*N,7*N)))]);remesh(name,verts,faces,original_mats['Ivory industrial enamel']);outward_mesh(o);aged_finish(o,[(.26,.225,.16),(.18,.23,.20),(.27,.26,.21),(.30,.30,.245),(.16,.20,.225)][idx],190+idx,False,.24)
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
web=material('Oily overpack restraint webbing',(.043,.050,.035),.97)
for strap,xc in enumerate([3.31,3.49]):
 path=[(3.485,.905,0),(3.614,.916,.227),(3.633,.970,.210),(3.633,1.285,.210),(3.618,1.335,.222),(3.614,1.348,.227),(4.026,1.348,.227),(4.022,1.335,.222),(4.007,1.285,.210),(4.007,.970,.210),(4.026,.916,.227),(4.155,.905,0)];verts=[]
 for y,z,radius in path:
  for x in [xc-.018,xc+.018]:
   yy=y if radius==0 else 3.82+(-1 if y<3.82 else 1)*math.sqrt(radius**2-(x-3.4)**2);verts.append((x,yy,z))
 faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(path)-1)];o=mesh('Overpack captive restraint strap '+str(strap),verts,faces,web);support(o,'Load saddle',(xc,3.485,.905));o.modifiers.new('Webbing fabric thickness','SOLIDIFY').thickness=.0016
 buckle=cube('Saddle restraint buckle '+str(strap),(xc,3.493,.918),(.055,.042,.026),edge,.001);support(buckle,'Load saddle',(xc,3.493,.905))
 o=cube('Buckle locking spindle '+str(strap),(xc,3.493,.93),(.034,.01,.006),original_mats['Structural warm graphite'],.001);intrinsic(o,buckle,'Captive locking spindle compresses webbing against buckle')
# The booth bears hand wear and ash-like dust; the actual electronics do not glow as fill.
for name,spots in [('Steel desk top',[((-3.90,1.57,.98),(3.5,3.5,1)),((-3.82,2.20,.98),(6,5,1))]),('Keyboard housing',[((-3.81,1.45,1.03),(8,4,1)),((-3.95,1.65,1.01),(9,8,1))]),('Dose meter cast housing',[((-4.12,2.25,1.47),(1,6,6))])]:
 stain_material(bpy.data.objects[name],spots,'Long shift handled '+name,(.17,.16,.075),.93)
for i in [0,1,2,8,9,10,20,21,22,30,31]:
 name='Keycap'+('' if i==0 else '.'+str(i).zfill(3));key=bpy.data.objects[name];key.data=key.data.copy();aged_finish(key,(.16,.19,.145),270+i,False,.2)
# Dust collects in the desk corners and around the log, staying off the main freight spine.
for i,(x,y,w,h) in enumerate([(-4.37,1.04,.16,.12),(-4.27,2.27,.24,.19),(-3.77,2.21,.11,.08)]):
 verts=[(x-w*.5,y-h*.35,desktop+.00014),(x+w*.45,y-h*.5,desktop+.00014),(x+w*.5,y+h*.27,desktop+.00014),(x-w*.30,y+h*.5,desktop+.00014)];o=mesh('Inventory neglected desktop residue '+str(i),verts,[(0,1,2,3)],oil);soften_stain(o,oil);support(o,'Steel desk top',(x,y,desktop))
