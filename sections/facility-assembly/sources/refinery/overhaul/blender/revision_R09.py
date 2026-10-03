"""R09: audited attachment closure, working-metal finishes and essential lettering."""
# The original worktop underside is 0.826m; make its two bearing ribs meet it exactly.
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('RF1 | PV service shelf cast cantilever'):
  for v in o.data.vertices:
   if abs(v.co.z-.825)<1e-5:v.co.z=.826
for record in supports:
 if record['group']=='PV supported service shelf':
  record['anchor'][2]=.826;record['group']='Processor_service_ledge_top'

# Seat the filter access sheet and bridge the pull grip to that sheet.
cover=bpy.data.objects['RF1 | Filter cabinet access sheet'];cover.location.y+=.001
for record in supports:
 if record['group']==cover.name:record['anchor'][1]=3.819
for x in [3.37,3.61]:rod('Filter pull mounting stud',(x,3.789,.685),(x,3.805,.685),.008,'dark')
text_object=bpy.data.objects['RF1 | Filter cabinet purpose'];text_object.location.y=3.80498;text_object.data.extrude=.00002

# Both diffuser panes touch their reflectors and are captured by physical edge clips.
for i,x in enumerate([.46,1.66]):
 suffix='' if i==0 else '.001'
 lens=bpy.data.objects['RF1 | PV suspended task diffuser'+suffix];lens.location.z+=.001
 lamp=bpy.data.objects['RF1 LIGHT | PV hood '+str(i)];lamp.location.z+=.001
 housing=bpy.data.objects['RF1 | PV suspended task reflector'+suffix]
 support(lens.name,(x,3.86,3.646),housing.name,(0,0,1))
 stay_name='RF1 | PV suspended task fixture stay'+('.001' if i==0 else '.003')
 support(housing.name,(x,3.95,3.726),stay_name,(0,0,1))
 for xx in [x-.276,x+.276]:
  clip=box('PV diffuser folded edge retainer',(xx,3.86,3.6405),(.012,.28,.012),'steel',.001)
  support(clip.name,(xx,3.86,3.6465),housing.name,(0,0,1))

# The ticket wire now enters the spring clip and the paper at both ends.
old=bpy.data.objects['RF1 | PV signed tag wire'];remove_object(old)
wire=rod('PV signed tag continuous wire',(1.23,4.035,1.559),(1.21,4.027,1.4405),.0025,'steel',8)
support(wire.name,(1.23,4.035,1.558),'RF1 | PV service ticket spring clip',(0,0,1))
paper=bpy.data.objects['RF1 | PV signed service tag']
support(paper.name,(1.21,4.027,1.442),wire.name,(0,0,1))
for name in ['PV worker tag checked','PV worker tag shift']:
 o=bpy.data.objects['RF1 | '+name];o.location.y=4.02599;o.data.extrude=.00001
ink=bpy.data.objects['RF1 | PV tag approval ink'];ink.location.y=4.02597
for v in ink.data.vertices:v.co.y=math.copysign(.00002,v.co.y)
bpy.context.view_layer.update();matrix=wire.matrix_world.copy();wire.parent=bpy.data.objects['Processor_sealed_hatch'];wire.matrix_world=matrix;wire['support_group']='RF1 | PV service ticket spring clip'

# Elliptical ear cups follow world height rather than scaling the cylinder thickness axis.
for o in s.objects:
 if o.name.startswith(('RF1 | Ear defender soft sealing pad','RF1 | Ear defender ochre cup')):o.scale.x=1.18;o.scale.z=1.0

# Brushed stainless belongs to working surfaces, while cast machine steel stays cast.
worksteel=mat('RF1_directional_worktop_stainless',(.235,.26,.247),.47,.86,.025)
nodes=worksteel.node_tree.nodes;links=worksteel.node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Anisotropic'].default_value=.42
tc=nodes.new('ShaderNodeTexCoord');vec=nodes.new('ShaderNodeVectorMath');vec.operation='MULTIPLY';vec.inputs[1].default_value=(2,95,3)
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=1
links.new(tc.outputs['Object'],vec.inputs[0]);links.new(vec.outputs[0],noise.inputs['Vector'])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.06;bump.inputs['Distance'].default_value=.00025
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
for name in ['Inspection_work_surface','Assembly_worktop','Processor_service_ledge_top','Dryer_filter_service_ledge_top']:
 o=bpy.data.objects[name]
 for i in range(len(o.data.materials)):o.data.materials[i]=worksteel
# Handling wear is confined to the press's real access cover and hydraulic sill.
for y,length in [(1.02,.11),(1.31,.08)]:
 box('Press access grip polish',(5.590,y,.618),(.001,length,.010),'steel',0)
for y,length in [(.91,.17),(1.45,.09)]:
 box('Press cast loading edge polish',(5.624,y,.864),(.002,length,.008),'steel',0)
# Essential stage stencils are readable; controls retain their finer authentic captions.
for o in s.objects:
 if o.type=='FONT' and o.name.startswith('RF1 | Process stage short stencil'):o.data.size=.070

# A formed instrument carrier keeps gauge/status shadows on purposeful hardware.
# Its inner faces follow the exact forty-sided body, with a 0.2mm seated fit.
angles=[math.radians(a) for a in range(-135,-44,9)];K=len(angles);vs=[]
for r,z in [(.6598,2.14),(.6598,2.38),(.668,2.14),(.668,2.38)]:
 vs += [(1.043+r*math.cos(a),4.984+r*math.sin(a),z) for a in angles]
fs=[]
for j in range(K-1):
 fs += [(j,j+1,K+j+1,K+j),(2*K+j,3*K+j,3*K+j+1,2*K+j+1),(j,2*K+j,2*K+j+1,j+1),(K+j,K+j+1,3*K+j+1,3*K+j)]
fs += [(0,K,3*K,2*K),(K-1,3*K-1,4*K-1,2*K-1)]
carrier=positive(mesh('PV formed instrument carrier',vs,fs,'dark'))
support(carrier.name,(1.043,4.3242,2.25),'RF1 | PV05 cast pressure vessel',(0,1,0))
for x,y in [(.572,4.512),(1.514,4.512)]:
 # Angled retaining ends are part of the formed carrier, not detached badges.
 cyl('Instrument carrier retaining rivet',(x,y,2.25),.014,.012,'steel',((x-1.043),y-4.984,0),6)
# The ready lamp remains visible in front of the instrument carrier.
bezel=bpy.data.objects['RF1 | PV ready indicator mounting bezel']
for v in bezel.data.vertices:v.co.y=math.copysign(.007,v.co.y)
bezel.location.y=4.309

# Local condensate below the steam service is a material stain, applied at the wall face.
stain=bpy.data.materials.new('RF1_local_steam_condensate');stain.use_nodes=True;n=stain.node_tree.nodes;l=stain.node_tree.links;n.clear()
p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.205,.189,.159,1);p.inputs['Roughness'].default_value=.94
transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');out=n.new('ShaderNodeOutputMaterial')
tc=n.new('ShaderNodeTexCoord');vec=n.new('ShaderNodeVectorMath');vec.operation='MULTIPLY';vec.inputs[1].default_value=(7,1,1.8)
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=1
l.new(tc.outputs['Object'],vec.inputs[0]);l.new(vec.outputs[0],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.38;r.color_ramp.elements[0].color=(0,0,0,1);r.color_ramp.elements[1].position=.72;r.color_ramp.elements[1].color=(.3,.3,.3,1)
l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
mesh('Steam wall localized condensate',[(4.01,6.37998,2.27),(4.21,6.37998,2.31),(4.24,6.37998,3.19),(4.11,6.37998,3.32),(3.99,6.37998,2.97)],[(0,1,2,3,4)],stain)
