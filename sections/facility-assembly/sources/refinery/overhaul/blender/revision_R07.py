"""R07: sharp machine construction, quiet enamel and unobstructed practical apertures."""
from mathutils.bvhtree import BVHTree

def positive(o):
 me=o.data
 v=sum(me.vertices[p.vertices[0]].co.dot(me.vertices[p.vertices[i]].co.cross(me.vertices[p.vertices[i+1]].co))/6 for p in me.polygons for i in range(1,len(p.vertices)-1))
 if v<0:
  for f in me.polygons:f.flip()
 return o

def evaluated_tree(o):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh()
 t=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);e.to_mesh_clear();return t

# The broad shell needs calm enamel; low-frequency generated color was reading as dents.
for key,variation in [('oxide',.025),('green',.045)]:
 material=M[key];color=material.diffuse_color[:3]
 for node in material.node_tree.nodes:
  if node.type=='VALTORGB':
   node.color_ramp.elements[0].color=(*[c*(1-variation) for c in color],1)
   node.color_ramp.elements[1].color=(*[c*(1+variation) for c in color],1)
  if node.type=='BUMP':node.inputs['Strength'].default_value=.025;node.inputs['Distance'].default_value=.001
  if node.type=='MAP_RANGE':
   node.inputs['To Min'].default_value=.62 if key=='oxide' else .65
   node.inputs['To Max'].default_value=.68 if key=='oxide' else .73
# Analytic cylindrical normals prevent profile joins from pulling the long body out of round.
vessel=bpy.data.objects['RF1 | PV05 cast pressure vessel'];N=40
for face in vessel.data.polygons:
 if len(face.vertices)==4:face.use_smooth=True
normals=[]
for loop in vessel.data.loops:
 vertex=vessel.data.vertices[loop.vertex_index];co=vertex.co
 if 1.009<co.z<2.451:normals.append(Vector((co.x,co.y,0)).normalized())
 else:normals.append(loop.normal)
# Blender calculates remaining loops before applying the radial body normals.
vessel.data.normals_split_custom_set(normals)

# Reduce the optical enclosure without moving its supported belt-frame feet.
hood_terms=['Sorter folded optical hood','Sorter optical front gasket','Sorter amber scan window','Optical hood captive screw','Sorter small bay number','Optical hood side vent']
hood_transform=Matrix.Translation(Vector((-2.75,5.45,1.92)))@Matrix.Diagonal((.8,.85,.8,1))@Matrix.Translation(Vector((2.75,-5.45,-1.92)))
rigid_group([o for o in s.objects if o.name.startswith('RF1 | ') and any(t in o.name for t in hood_terms)],hood_transform)
# Foot/Upright X adjustment preserves the 1.315m contact plane.
post_transform=Matrix.Translation(Vector((-2.75,0,0)))@Matrix.Diagonal((.8,1,1,1))@Matrix.Translation(Vector((2.75,0,0)))
rigid_group([o for o in s.objects if o.name.startswith(('RF1 | Sorter optical foot bracket','RF1 | Sorter optical cast upright'))],post_transform)
for record in supports:
 if record['group'].startswith('RF1 | Sorter optical foot bracket'):record['anchor']=list(post_transform@Vector(record['anchor']))
# A short socket connects the existing lens carrier to the recessed optics hood.
box('Sorter optical housing underside socket',(-2.73,4.94,1.917),(.43,.68,.050),'dark',.002)

# The press becomes a floor-mounted hydraulic casting instead of another table frame.
for o in list(s.objects):
 if any(o.name.startswith(p) for p in ['ASSEMBLY_foot','ASSEMBLY_leg','ASSEMBLY_rail','ASSEMBLY_cross','ART_ASSEMBLY_foot']):remove_object(o)
sole=box('Press machined floor sole',(6.06,1.15,.045),(.98,1.92,.09),'dark',.003)
support(sole.name,(6.06,1.15,0),'Floor',(0,0,-1))
base=plate('Press hydraulic cast base',(6.06,1.15,.485),1.78,.79,.87,'oxide',.10);base.rotation_euler.z=-math.pi/2
support(base.name,(6.06,1.15,.090),sole.name,(0,0,-1))
support('Press worktop',(6.06,1.15,.880),base.name,(0,0,-1))
for material_index in range(len(bpy.data.objects['Assembly_worktop'].data.materials)):
 bpy.data.objects['Assembly_worktop'].data.materials[material_index]=M['steel']
gasket=plate('Press hydraulic access gasket',(5.617,1.15,.49),.77,.46,.014,'dark',.055);gasket.rotation_euler.z=-math.pi/2
panel=plate('Press hydraulic access cover',(5.605,1.15,.49),.72,.41,.014,'green',.045);panel.rotation_euler.z=-math.pi/2
support(gasket.name,(5.624,1.15,.49),base.name,(1,0,0))
support(panel.name,(5.612,1.15,.49),gasket.name,(1,0,0))
rod('Press service recessed pull',(5.589,1.05,.61),(5.589,1.25,.61),.012,'steel')
for y in [.79,1.51]:
 for z in [.31,.67]:cyl('Press access captive bolt',(5.589,y,z),.019,.024,'steel',(-1,0,0),6)
for x in [5.65,6.46]:
 for y in [.31,1.99]:
  cyl('Press sole floor anchor',(x,y,.115),.030,.05,'steel',(0,0,1),6)
  ring('Press sole washer',(x,y,.095),.039,.007,'steel')
# A specific cast cheek carries the angled interface from the new base.
rod('Press console cast outrigger',(5.625,1.15,.78),(5.24,1.15,1.05),.055,'dark')
text('Press base service stencil','HYDRAULIC / 07',(5.590,1.45,.38),.040,'ivory',(math.pi/2,0,-math.pi/2))

# The dryer is seated in two concave saddles following the actual polygonal drum.
for o in list(s.objects):
 if any(o.name.startswith(p) for p in ['DRYER_foot','DRYER_leg','DRYER_rail','DRYER_cross','ART_DRYER_foot','RF1 | Thermal cast cradle','RF1 | Thermal cradle securing bolt']):
  remove_object(o);continue
 if o.name.startswith('RF1 | Machine stand diagonal brace'):
  lo,hi=bounds_world(o)
  if lo.x>2.4:remove_object(o)
for x in [3.38,4.80]:
 pad=box('Thermal saddle floor sole',(x,4.97,.06),(.36,1.25,.12),'dark',.003)
 support(pad.name,(x,4.97,0),'Floor',(0,0,-1))
 yz=[(-.58,.12),(.58,.12),(.58,1.185)]
 yz += [(.67*math.sin(math.radians(a)),1.52-.67*math.cos(math.radians(a))+.0001) for a in range(60,-61,-10)]
 yz += [(-.58,1.185)]
 count=len(yz);vs=[(xx,4.97+y,z) for xx in [x-.10,x+.10] for y,z in yz]
 fs=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
 saddle=positive(mesh('Thermal concave cast saddle',vs,fs,'dark'));bevel(saddle,.002)
 support(saddle.name,(x,4.97,.12),pad.name,(0,0,-1))
 support('DR06 drum saddle contact',(x,4.97,.850),'RF1 | DR06 horizontal thermal drum',(0,0,1))
 for y in [4.44,5.50]:
  cyl('Thermal sole anchor bolt',(x,y,.155),.029,.05,'steel',(0,0,1),6)
  ring('Thermal sole anchor washer',(x,y,.127),.038,.007,'steel')
rod('Thermal rear saddle tie',(3.38,5.50,.26),(4.80,5.50,.62),.040,'dark')

# An intentional thermal air gap is carried by real radial spacers.
for o in list(s.objects):
 if o.name.startswith('RF1 | Thermal cover hold-down'):remove_object(o)
shield=bpy.data.objects['RF1 | Thermal removable insulation saddle'];drum=bpy.data.objects['RF1 | DR06 horizontal thermal drum']
st=evaluated_tree(shield);dt=evaluated_tree(drum)
for x in [3.60,4.68]:
 for degrees in [52.5,127.5]:
  a=math.radians(degrees);axis=Vector((0,math.cos(a),math.sin(a)));center=Vector((x,4.97,1.52))
  drum_hit,dn,di,dd=dt.ray_cast(center+axis*.77,-axis,.25)
  shield_hit,sn,si,sd=st.ray_cast(center+axis*.66,axis,.20)
  assert drum_hit is not None and shield_hit is not None
  spacer=rod('Thermal cover radial stand-off',drum_hit-axis*.0005,shield_hit+axis*.0005,.027,'steel')
  support(spacer.name,drum_hit-axis*.0005,drum.name,-axis)
  support(shield.name,shield_hit,spacer.name,-axis)
  outer,on,oi,od=st.ray_cast(center+axis*.77,-axis,.20)
  cap=rod('Thermal insulation retaining stud',outer+axis*.0005,outer+axis*.025,.020,'steel',6)
  support(cap.name,outer+axis*.0005,shield.name,-axis)

# Four open-bottom folded wall hoods replace solid housings in the emitted beam.
for i,x in enumerate([-5.75,-1.75,2.75,6.75]):
 suffix='' if i==0 else '.'+str(i).zfill(3)
 for n in ['ART_Wall_fixture'+suffix,'ART_Wall_fixture_diffuser'+suffix]:
  o=bpy.data.objects.get(n)
  if o:remove_object(o)
 back=box('Wall service physical backplate',(x,6.409,3.00),(.27,.045,.26),'dark',.002)
 support(back.name,(x,6.4315,3.00),'North_wall',(0,1,0))
 box('Wall service folded reflector',(x,6.319,3.009),(.27,.18,.118),'dark',.003)
 lens=box('Wall service exposed lens',(x,6.30,2.947),(.20,.080,.006),'lens',.001)
 lamp=bpy.data.objects['RF1 LIGHT | Wall service lamp '+str(i)];lamp.location=(x,6.30,2.939);lamp.rotation_euler=(0,0,0);lamp.data.size=.19;lamp.data.size_y=.070;lamp['fixture_lens']=lens.name
 for record in lights:
  if record['name']==lamp.name:record['lens']=lens.name

# Place the press strip below both the retained crosshead and the added crown.
for name in ['RF1 | Press fixture casing','RF1 | Press actual lens']:
 o=bpy.data.objects[name];o.location.z-=.165;o.location.x-=.12
lamp=bpy.data.objects['RF1 LIGHT | Press task bar'];lamp.location.z-=.165;lamp.location.x-=.12;lamp.rotation_euler=(0,0,0);lamp.data.size=.15;lamp.data.size_y=.65
for record in supports:
 if record['group']=='Press task fixture':record['anchor']=[5.78,1.15,2.170];record['target']='Assembly_crown'
box('Press strip underside mounting shoe',(5.747,1.15,2.162),(.075,.52,.016),'dark',.001)

# Flat practicals share their physical lens basis, including rectangle roll.
bpy.context.view_layer.update()
for name in ['Work nook lamp','Mine threshold practical','Fuel transfer threshold practical','Personnel threshold practical','Inspection sample practical']:
 lamp=bpy.data.objects['RF1 LIGHT | '+name];lens=bpy.data.objects[lamp['fixture_lens']]
 loc,rotation,scale=lens.matrix_world.decompose();lamp.rotation_euler=rotation.to_euler()
 axis=rotation@Vector((0,0,-1));lamp.location=loc+axis*.007
 if name=='Inspection sample practical':lamp['task_receiver_prefix']='Inspection_sample_fuel'

# Pull bulkhead heads in front of the shutter guide; extended arms remain wall mounted.
for side,title in [(-1,'Mine transfer'),(1,'Fuel transfer')]:
 terms=[title+' bulkhead cast rim',title+' bulkhead frosted lens',title+' bulkhead lens retaining ring']
 rigid_group([o for o in s.objects if o.name.startswith('RF1 | ') and any(t in o.name for t in terms)],Matrix.Translation(Vector((-side*.20,0,0))))
 lamp=bpy.data.objects['RF1 LIGHT | '+title+' wall bulkhead'];lamp.location.x-=side*.20
 old=bpy.data.objects.get('RF1 | '+title+' bulkhead cast bracket')
 if old:remove_object(old)
 emission=(lamp.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 lens=bpy.data.objects[lamp['fixture_lens']];center=lens.matrix_world.translation.copy()
 rod(title+' extended bulkhead bracket',(side*7.433,-5.67,1.92),center-emission*.035,.020,'dark')

# Each operator interface gets clipped sheet corners in its own existing local frame.
for o in s.objects:
 if o.type!='MESH' or not o.name.endswith('_Control_enclosure'):continue
 coords=[v.co for v in o.data.vertices];lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
 # Source panels are local XY sheets, thickness along Z; rotate object matrices already carry the tilt.
 axes=sorted(range(3),key=lambda a:hi[a]-lo[a]);thin,u,v=axes[0],axes[1],axes[2]
 center=(hi+lo)/2;hu=(hi[u]-lo[u])/2;hv=(hi[v]-lo[v])/2;cut=min(hu,hv)*.22
 profile=[(-hu+cut,-hv),(hu-cut,-hv),(hu,-hv+cut),(hu,hv-cut),(hu-cut,hv),(-hu+cut,hv),(-hu,hv-cut),(-hu,-hv+cut)]
 vertices=[]
 for z in [lo[thin],hi[thin]]:
  for a,b in profile:
   co=center.copy();co[thin]=z;co[u]=center[u]+a;co[v]=center[v]+b;vertices.append(co)
 faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 mats=list(o.data.materials);me=bpy.data.meshes.new(o.name+' folded sheet');me.from_pydata(vertices,[],faces)
 for m in mats:me.materials.append(m)
 o.data=me;positive(o)

# A steel scoop and sample ticket belong at the sorter reject bin, not in circulation.
# Bin base is measured by actual ray; the assembly remains seated without moving process parts.
bt=evaluated_tree(bpy.data.objects['Sorter_reject_bin_base']);hit,n,i,dist=bt.ray_cast(Vector((-1.92,3.99,.5)),Vector((0,0,-1)),.5)
z=hit.z+.0008
scoop=positive(mesh('Mineral sampling scoop bowl',[(-1.985,3.895,z),(-1.855,3.895,z),(-1.855,4.065,z),(-1.985,4.065,z),(-2.035,3.850,z+.045),(-1.805,3.850,z+.045),(-1.805,4.110,z+.045),(-2.035,4.110,z+.045)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'steel'))
support(scoop.name,(-1.92,3.99,hit.z+.0008),'Sorter_reject_bin_base',(0,0,-1))
rod('Mineral scoop steel handle',(-1.92,4.095,z+.033),(-1.84,4.34,z+.12),.014,'steel')
# Calm, readable process handoffs are marked on real nearby machine rails.
for p,body in [((-3.74,4.469,1.365),'04  SORT'),((-.28,4.31,1.06),'05  REFINE'),((3.88,4.105,1.64),'06  DRY')]:
 text('Process stage short stencil',body,p,.055,'ivory')
# Large, meaningful feed-direction arrows on the existing conveyor side rails.
for x,y,z in [(-3.95,4.474,1.255),(-.68,4.474,1.255)]:
 mesh('Transfer right arrow',[(x-.10,y,z-.024),(x+.02,y,z-.024),(x+.02,y,z-.049),(x+.10,y,z),(x+.02,y,z+.049),(x+.02,y,z+.024),(x-.10,y,z+.024)],[(0,1,2,3,4,5,6)],'ochre')
