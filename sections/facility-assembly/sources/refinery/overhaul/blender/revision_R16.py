"""Owner mood revision: neglected refinery, weak practical pools, failed lamps.

Geometry interfaces and camera/light poses are retained. Wear uses controlled
material masks and supported local films, never displacement of the room shell.
"""
def aged_colour(name,colour,roughness=None):
 material=bpy.data.materials.get(name)
 if not material:return
 old=tuple(material.diffuse_color[:3]);material.diffuse_color=(*colour,1)
 for node in material.node_tree.nodes:
  if node.type=='BSDF_PRINCIPLED':
   node.inputs['Base Color'].default_value=(*colour,1)
   if roughness is not None and not node.inputs['Roughness'].is_linked:
    node.inputs['Roughness'].default_value=roughness
  elif node.type=='VALTORGB':
   for element in node.color_ramp.elements:
    # Preserve authored low-frequency colour variation and all roughness wiring.
    element.color=(*[min(1,colour[i]*element.color[i]/max(old[i],.001)) for i in range(3)],element.color[3])

palette={
 'warmwall':((.120,.137,.123),.95),'wallpatch':((.153,.166,.145),.96),
 'cool_service_plaster':((.112,.140,.130),.94),
 'neutral_ceiling':((.105,.120,.109),.94),
 'concrete':((.093,.108,.098),.94),'dado':((.039,.063,.055),.87),
 'epoxy':((.040,.052,.045),.83),'green':((.044,.076,.063),.82),
 'oxide':((.125,.068,.037),.85),'oxide_edge':((.181,.104,.059),.89),
 'ivory':((.276,.298,.241),.89),'ochre':((.263,.225,.105),.90),
 'paper':((.365,.359,.283),.98),'wood':((.085,.060,.035),.93),
 'leather':((.124,.107,.066),.96),'ceramic':((.249,.265,.215),.63),
 'steel':((.185,.208,.197),.59),'brass':((.161,.145,.074),.74),
 'dust':((.111,.124,.098),.99),'cork':((.065,.057,.034),.99),
 'red':((.166,.037,.022),.84),'blue':((.032,.055,.064),.85),
 'muted_service_trunk':((.073,.087,.077),.90),
 'rolled_vessel_enamel':((.137,.076,.044),None),
 'cast_hydraulic_powdercoat':((.099,.065,.041),None),
 'thermal_jacket_finish':((.045,.074,.061),None),
 'work_glove_pale_leather':((.233,.228,.157),.95),
 'folded_inspection_cotton':((.042,.063,.058),.95),
}
for key,(colour,roughness) in palette.items():aged_colour('RF1_'+key,colour,roughness)
for i in range(4):aged_colour('RF1_screed_'+str(i),(.084+i*.003,.098+i*.003,.087+i*.003),.94)

# Separate every lens material before changing its source. An unpowered lens must
# also have zero shader emission; shared warm-lamp users cannot defeat the outage.
cold=(.63,.77,.69);sick=(.69,.74,.59);amber=(.80,.65,.39)
outputs={
 'PV hood 0':(42,cold),'PV hood 1':(0,cold),
 'Ceiling pendant 0':(0,cold),'Ceiling pendant 1':(85,cold),
 'Ceiling pendant 2':(135,sick),'Ceiling pendant 3':(0,cold),
 'Ceiling pendant 4':(34,cold),'Ceiling pendant 5':(0,cold),
 'Wall service lamp 0':(0,cold),'Wall service lamp 1':(9,sick),
 'Wall service lamp 2':(0,cold),'Wall service lamp 3':(7,cold),
 'Work nook lamp':(17,cold),'Press task bar':(15,cold),
 'Eyewash service practical':(9,cold),'Mine threshold practical':(22,cold),
 'Fuel transfer threshold practical':(17,amber),'Personnel threshold practical':(9,sick),
 'Inspection sample practical':(10,cold),
 'Mine transfer wall bulkhead':(14,cold),'Fuel transfer wall bulkhead':(11,amber),
}
outages=[]
for light in [o for o in s.objects if o.type=='LIGHT']:
 key=light.name.removeprefix('RF1 LIGHT | ');energy,colour=outputs[key]
 light.data.energy=energy;light.data.color=colour
 lens=bpy.data.objects[light['fixture_lens']];lens.data=lens.data.copy()
 lm=mat('RF16_lens_'+key,colour if energy else (.043,.055,.044),.63,0,0,1.8 if energy else 0)
 lens.data.materials.clear();lens.data.materials.append(lm)
 lens['electrical_state']='weak' if energy else 'failed';light['electrical_state']=lens['electrical_state']
 if not energy:outages.append(dict(light=light.name,lens=lens.name,energy=0,shader_emission=0))
s['failed_fixture_registry']=json.dumps(outages)
# Retained switch/status glows are small physical indicators rather than room fill.
for key,strength,colour in [('warm_lamp',.12,(.32,.27,.13)),('task_lamp',.08,(.15,.24,.19)),('status_amber',.20,(.63,.18,.025))]:
 mm=bpy.data.materials['RF1_'+key]
 for node in mm.node_tree.nodes:
  if node.type=='BSDF_PRINCIPLED':
   node.inputs['Emission Strength'].default_value=strength
   node.inputs['Emission Color'].default_value=(*colour,1)

# Broad enamel wear: a few irregular matte exposed patches, biased to service
# seams at the bottom/top. The existing fine manufactured finish is kept intact.
for name in ['RF1_rolled_vessel_enamel','RF1_cast_hydraulic_powdercoat','RF1_thermal_jacket_finish','RF1_oxide','RF1_green']:
 mm=bpy.data.materials[name];nodes=mm.node_tree.nodes;links=mm.node_tree.links
 p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=p.inputs['Base Color']
 original=base.links[0].from_socket if base.is_linked else None
 tc=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise')
 noise.inputs['Scale'].default_value=6.0;noise.inputs['Detail'].default_value=1.3;noise.inputs['Roughness'].default_value=.58
 links.new(tc.outputs['Generated'],noise.inputs['Vector'])
 mask=nodes.new('ShaderNodeValToRGB');mask.color_ramp.elements[0].position=.62;mask.color_ramp.elements[0].color=(0,0,0,1)
 mask.color_ramp.elements[1].position=.73;mask.color_ramp.elements[1].color=(1,1,1,1)
 links.new(noise.outputs['Fac'],mask.inputs['Fac'])
 mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX'
 if original:links.new(original,mix.inputs[1])
 else:mix.inputs[1].default_value=base.default_value
 mix.inputs[2].default_value=(.045,.052,.037,1);links.new(mask.outputs['Color'],mix.inputs[0]);links.new(mix.outputs[0],base)
 rough=nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1
 rough.inputs['To Min'].default_value=.74;rough.inputs['To Max'].default_value=.97
 links.new(mask.outputs['Color'],rough.inputs['Value']);links.new(rough.outputs['Result'],p.inputs['Roughness'])

M['damp']=mat('RF16_damp_mineral',(.043,.070,.047),.98,0,.09)
M['rust']=mat('RF16_deep_oxide',(.078,.048,.027),.96,0,.08)
M['grease']=mat('RF16_service_grease',(.018,.028,.020),.63,0,.05)
M['lime']=mat('RF16_dried_leak_salt',(.170,.182,.139),.99,0,.06)

def north_mark(name,points,material,target):
 # Actual front face 6.380m, 20 micrometres of film, no floating decal cards.
 o=mesh(name,[(x,6.37998,z) for x,z in points],[tuple(range(len(points)))],material)
 x,z=points[0];support(o.name,(x,6.37998,z),target,(0,1,0));return o

# Authored leak shapes descend from the overhead utility seam, with an irregular
# wet centre and narrow mineral tails. Calm wall areas remain between damage.
for j,(x,width,lower,target) in enumerate([(-5.18,.52,1.94,'RF1 | North acoustic concrete bay 0'),(-2.68,.33,2.57,'RF1 | North acoustic concrete bay 1'),(3.74,.56,1.89,'RF1 | North acoustic concrete bay 3'),(6.35,.30,2.31,'RF1 | North acoustic concrete bay 4')]):
 north_mark('Wall utility damp plume '+str(j),[(x,4.18),(x+width,4.18),(x+width*.87,3.60),(x+width*.72,3.23),(x+width*.78,lower+.43),(x+width*.58,lower),(x+width*.38,lower+.57),(x+width*.23,lower+.30),(x+.03,3.44)],'damp',target)
 for k in range(3):
  xx=x+.055+k*width*.24;bottom=lower+.12+k*.19
  north_mark('Wall dried mineral trickle',[(xx,3.77),(xx+.013,3.72),(xx+.016,bottom+.13),(xx+.006,bottom),(xx-.006,bottom+.07)],'lime',target)

# Grease/oil footprints at the service side of machinery, above the true floor
# overlays. These are open irregular films, without collision or raised obstacles.
for j,(x,y,rx,ry,target,z) in enumerate([(-5.13,3.75,.62,.36,'RF1 | Process epoxy field',.00122),(1.04,4.05,.70,.40,'RF1 | Process epoxy field',.00122),(3.52,3.52,.38,.25,'RF1 | Process epoxy field',.00122),(5.82,.34,.33,.31,'RF1 | Fabrication epoxy field',.00142)]):
 vs=[]
 for k in range(15):
  a=2*math.pi*k/15;f=.80+.14*math.sin(k*2.31+j)
  vs.append((x+rx*f*math.cos(a),y+ry*f*math.sin(a),z))
 o=mesh('Old service seep footprint '+str(j),vs,[tuple(range(15))],'grease')
 support(o.name,(x,y,z),target,(0,0,-1))

# Rust runs on actual cylindrical metal, not intersecting rectangular stickers.
cx,cy=1.043336,4.984283
for j,(angle,width,z0,z1) in enumerate([(-2.05,.17,1.06,1.71),(-1.35,.12,1.03,1.37),(-2.78,.11,1.34,2.38)]):
 vs=[]
 for a,z in [(angle-width/2,z0),(angle+width/2,z0+.09),(angle+width*.34,z1-.16),(angle+width*.10,z1),(angle-width*.38,z1-.05)]:
  vs.append((cx+.66002*math.cos(a),cy+.66002*math.sin(a),z))
 # A fan projected onto a curved shell would bury its centre. Use narrow quads
 # between sampled angular stations so every film vertex follows the radius.
 verts=[];faces=[];segments=12
 for k in range(segments+1):
  a=angle-width/2+width*k/segments;t=k/segments
  bottom=z0+.09*t;top=z1-.12*abs(2*t-1)
  verts.extend([(cx+.66003*math.cos(a),cy+.66003*math.sin(a),bottom),(cx+.66003*math.cos(a),cy+.66003*math.sin(a),top)])
 for k in range(segments):faces.append((2*k,2*k+2,2*k+3,2*k+1))
 patch=mesh('PV local seal corrosion run '+str(j),verts,faces,'rust')
 support(patch.name,verts[0],'RF1 | PV05 cast pressure vessel',(-math.cos(angle-width/2),-math.sin(angle-width/2),0))

# The noticeboard records work left unresolved rather than a sunny completed shift.
bpy.data.objects['RF1 | Pump scribbled note'].data.body='SEAL LEAK\nPARTS PENDING'
bpy.data.objects['RF1 | Board pump service header'].data.body='PV-05 / LEAK'
for name in ['RF1 | Crew postcard mountain print','RF1 | Crew postcard second peak','RF1 | Postcard small sun']:
 o=bpy.data.objects.get(name)
 if o:remove_object(o)
bpy.data.objects['RF1 | Crew postcard caption'].data.body='NO REPLY'
# Keep the old paper and pin as a small abandoned personal trace.
post=bpy.data.objects['RF1 | Crew postcard'];post.data=post.data.copy()
post.data.materials[0]=M['paper']
s['owner_mood_direction']='run down, dark, gloomy and hopeless; 2026-10-03'
bpy.context.view_layer.update()
