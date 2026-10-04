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
  elif obj.name.startswith(('Bolted collar','Collar radial','Carrier bearing','Sealed vessel lower shoulder','Lift eye')):
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
 for i in range(28):
  y=.16+i*.635;length=.53+random.random()*.055;width=.048+random.random()*.010
  verts=[(x-width/2,y,.00018),(x+width/2,y+.008,.00018),(x+width*.45,y+length,.00018),(x-width*.5,y+length-.014,.00018),(x-width*.40,y+length*.56,.00018)];obj=mesh('Worn freight lane '+str(side)+' '+str(i),verts,[(0,1,2,3,4)],original_mats['Ochre safety enamel']);support(obj,'Floor',(x,y+length*.4,.00018))
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
# Inventory desk: a stained logbook, dead personal clock, and folded photograph clipped to the housing.
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
# A damaged note and rolled maintenance strip belong to the extractor's actual service cassette.
cassette=bpy.data.objects['Removable filter cassette.001'];front=min((cassette.matrix_world@Vector(v)).y for v in cassette.bound_box)
obj=cube('Extractor overdue service tag',(-4.32,front-.0015,1.01),(.20,.003,.11),paper);support(obj,cassette.name,(-4.32,front,1.01),(0,1,0));tag=obj
obj=text('Extractor service tag printing','FILTER 06\nOVERDUE',(-4.32,front-.0031,1.024),.018,ink,(math.pi/2,0,0));intrinsic(obj,tag,'Printed service label')
# Rust masks and paint keep original identity/control lettering intact; no new wall slogans.
