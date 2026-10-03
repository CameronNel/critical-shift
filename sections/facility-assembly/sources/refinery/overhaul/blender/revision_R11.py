"""R11: manufactured finish hierarchy, legible controls and stronger human contact cues."""
def manufactured_paint(name,color,roughness,metal,grain):
 m=mat(name,color,roughness,metal,.018);n=m.node_tree.nodes;l=m.node_tree.links
 p=next(v for v in n if v.type=='BSDF_PRINCIPLED');p.inputs['Specular IOR Level'].default_value=.34
 tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=grain;noise.inputs['Detail'].default_value=1
 l.new(tc.outputs['Object'],noise.inputs['Vector']);r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=roughness-.035;r.inputs['To Max'].default_value=roughness+.035
 l.new(noise.outputs['Fac'],r.inputs['Value']);l.new(r.outputs['Result'],p.inputs['Roughness'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.065;bump.inputs['Distance'].default_value=.00025
 l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);return m
rolled=manufactured_paint('RF1_rolled_vessel_enamel',(.278,.072,.030),.51,.055,135)
cast=manufactured_paint('RF1_cast_hydraulic_powdercoat',(.225,.058,.026),.79,.045,85)
thermal=manufactured_paint('RF1_thermal_jacket_finish',(.074,.137,.111),.73,.08,110)
for o in s.objects:
 material=None
 if o.name in ['RF1 | PV05 cast pressure vessel','Processor_screw_lift_casing']:material=rolled
 if o.name.startswith('RF1 | Press hydraulic cast base'):material=cast
 if o.name in ['RF1 | DR06 horizontal thermal drum','RF1 | DR06 thermal access face']:material=thermal
 if material:
  for i in range(len(o.data.materials)):o.data.materials[i]=material

# Wear belongs to the gripping arc of each functional wheel, within its actual mesh.
for name in ['Processor_pressure_trim_wheel','Processor_temperature_trim_wheel','Processor_dump_valve_wheel']:
 o=bpy.data.objects[name];lo,hi=bounds_world(o);center=(lo+hi)/2
 o.data.materials.append(M['steel']);index=len(o.data.materials)-1
 for face in o.data.polygons:
  point=o.matrix_world@(sum((o.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices))
  if point.z>center.z+.102 and abs(point.x-center.x)<.052:face.material_index=index

# Higher-value legends and two or three primary functions per original interactive face.
legend_changes={
 'CRUSHER_START':('START',.049),'CRUSHER_STOP':('STOP',.049),'CRUSHER_REVERSE':('REVERSE',.045),
 'SORTER_BELT_SPEED':('BELT SPEED',.040),'SORTER_SCANNER_SENSITIVITY':('SENSOR',.041),
 'SORTER_DIVERTER':('DIVERTER',.038),'SORTER_RECALIBRATION':('CALIBRATE',.025),
 'SORTER_MANUAL_OVERRIDE':('OVERRIDE',.025),'RECEIVING_BRAKE':('BRAKE',.042),
 'RECEIVING_LATCH':('LATCH',.042),'RECEIVING_TIP':('TIP',.045),
 'ASSEMBLY_PRESS':('PRESS',.043),'ASSEMBLY_ALIGNMENT':('ALIGNMENT',.035),
 'DRYER_INCREASE_HEAT':('HEAT',.044),'DRYER_MOISTURE_CHECK':('MOISTURE',.040),
 'INSPECTION_BLEND':('BLEND',.042)}
printed=json.loads(s['printed_surface_registry'])
for o in s.objects:
 if o.type!='FONT' or not o.name.endswith('_engraving'):continue
 prefix=o.name.split('_')[0];head=s.objects.get(prefix+'_Control_enclosure')
 if not head:continue
 if o.data.users>1:o.data=o.data.copy()
 key=o.name.removesuffix('_engraving')
 if key in legend_changes:o.data.body,o.data.size=legend_changes[key]
 else:o.data.size=min(o.data.size,.028)
 o.data.extrude=.00001
 material=M['ivory'] if prefix in {'RECEIVING','CRUSHER'} else M['ink']
 for i in range(len(o.data.materials)):o.data.materials[i]=material
 bpy.context.view_layer.update();lo,hi=bounds_world(o);point=(lo+hi)/2
 d=-(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
 hit,n,ix,distance=evaluated_tree(head).ray_cast(point-d*.05,d,.12)
 assert hit is not None,('Caption outside case',o.name)
 matrix=o.matrix_world.copy();matrix.translation+=(hit-point)-d*.00002;o.matrix_world=matrix
 printed.append(dict(mark=o.name,target=head.name,direction=list(d)))

# Seat the folded crusher roof against its side walls on shaped continuous bearing strips.
roof=bpy.data.objects['Crusher_feed_hood_roof'];roof_tree=evaluated_tree(roof)
for name in ['Crusher_hood_side','Crusher_hood_side.001']:
 side=bpy.data.objects.get(name)
 if not side:continue
 lo,hi=bounds_world(side);x=(lo.x+hi.x)/2;y=(lo.y+hi.y)/2;side_tree=evaluated_tree(side)
 xs=[x-.010,x+.010];profile=[]
 for xx in xs:
  lower=side_tree.ray_cast(Vector((xx,y,3.3)),Vector((0,0,-1)),1)[0]
  upper=roof_tree.ray_cast(Vector((xx,y,2.8)),Vector((0,0,1)),1)[0]
  assert lower is not None and upper is not None
  profile.append((xx,lower.z-.0003,upper.z+.0003))
 vs=[(xx,yy,z) for yy in [lo.y+.025,hi.y-.025] for xx,low,high in profile for z in [low,high]]
 gasket=positive(mesh('Crusher shaped roof bearing strip',vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],'black'))
 support(gasket.name,(x,y,profile[0][1]+.0003),side.name,(0,0,-1))
 midpoint=(profile[0][2]+profile[1][2])/2-.0003
 slope=(profile[1][2]-profile[0][2])/(xs[1]-xs[0])
 support(roof.name,(x,y,midpoint),gasket.name,Vector((slope,0,-1)).normalized())
# The rear folded wall follows the roof's canted shoulder rather than leaving an open seam.
back=bpy.data.objects.get('Crusher_hood_back')
if back:
 lo,hi=bounds_world(back);ys=[lo.y,hi.y];profile=[(-6.611664,2.43),(-4.701664,2.43),(-4.701664,3.070),(-4.976664,3.190),(-6.336664,3.190),(-6.611664,3.070)]
 vs=[back.matrix_world.inverted()@Vector((x,y,z)) for y in ys for x,z in profile];N=len(profile)
 fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 me=bpy.data.meshes.new('Crusher formed hood rear');me.from_pydata(vs,[],fs);me.materials.append(M['ivory']);back.data=me;positive(back)
 for modifier in list(back.modifiers):back.modifiers.remove(modifier)
 bevel(back,.001)
 support(roof.name,(-5.65,(lo.y+hi.y)/2,3.190),back.name,(0,0,-1))

# Make the visible product stub read as a seated hose coupling.
coupling=cyl('Product hose hex compression nut',(2.506,4.908,1.449),.103,.077,'steel',(1,.13,.15),6)
rod('Product coupling neck sleeve',(2.452,4.898283,1.438),(2.480,4.904,1.444),.070,'steel')
coupling['support_group']='RF1 | Processor product coupling'
bpy.data.objects['RF1 | Refined product interstage hose'].data.use_fill_caps=True

# Specific maintenance notices replace a generic paper read; printed marks meet the papers.
bpy.data.objects['RF1 | Board pump service header'].data.body='PV-05 / SEAL'
bpy.data.objects['RF1 | Board pump service header'].data.size=.034
bpy.data.objects['RF1 | Pump scribbled note'].data.body='CHECK COLD\nSEAL OK / M.A.'
bpy.data.objects['RF1 | Pump scribbled note'].data.size=.021
paper_terms=['Roster title','Roster shift entry','Board pump service header','Pump scribbled note']
papers=[bpy.data.objects['RF1 | Pinned shift paper '+str(i)] for i in [0,1]]
for o in s.objects:
 if o.type!='FONT' or not any(o.name.startswith('RF1 | '+p) for p in paper_terms):continue
 o.data.extrude=.00001;bpy.context.view_layer.update();lo,hi=bounds_world(o);point=(lo+hi)/2
 target=min(papers,key=lambda p:abs(p.matrix_world.translation.x-point.x));d=Vector((0,-1,0))
 hit,n,ix,distance=evaluated_tree(target).ray_cast(point-d*.03,d,.06);assert hit is not None,o.name
 matrix=o.matrix_world.copy();matrix.translation+=(hit-point)-d*.00002;o.matrix_world=matrix
 printed.append(dict(mark=o.name,target=target.name,direction=list(d)))
s['printed_surface_registry']=json.dumps(printed)
# Two small radio soles meet the timber; the original radio bottom is 2 mm above it.
rigid_group([o for o in s.objects if o.name.startswith('RF1 | ') and 'radio' in o.name.lower()],Matrix.Translation(Vector((.060,-.180,0))))
radio=bpy.data.objects['RF1 | Pocket radio'];lo,hi=bounds_world(radio);center=(lo+hi)/2
table=bpy.data.objects['RF1 | Workbench timber top'];tl,th=bounds_world(table)
for x in [center.x-.073,center.x+.073]:
 foot=box('Radio rubber sole',(x,center.y,(th.z+lo.z)/2),(.032,.065,max(.003,lo.z-th.z+.001)),'black',.0004)
 support(foot.name,(x,center.y,th.z),table.name,(0,0,-1))
 support(radio.name,(x,center.y,lo.z),foot.name,(0,0,-1))
# Local timber burnish follows the actual front working edge.
for x,length in [(center.x-.19,.083),(center.x-.06,.092)]:
 box('Nook timber working-edge polish',(x,tl.y+.003,th.z-.007),(length,.003,.009),'wood',0)
bpy.context.view_layer.update()
