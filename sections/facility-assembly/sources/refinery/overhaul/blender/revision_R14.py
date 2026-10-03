"""R14: readable formed service metal, recessed optical glass and measuring tools."""

def closed_profile(name,profile,low,high,axis,material):
 vs=[]
 for end in [low,high]:
  for a,b in profile:
   vs.append((end,a,b) if axis==0 else (a,end,b) if axis==1 else (a,b,end))
 N=len(profile);fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]
 fs += [(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return positive(mesh(name,vs,fs,material))

def replace_world_mesh(original,temporary):
 bpy.context.view_layer.update();inv=original.matrix_world.inverted()
 me=temporary.data.copy()
 for v in me.vertices:v.co=inv@(temporary.matrix_world@v.co)
 original.data=me
 for modifier in list(original.modifiers):original.modifiers.remove(modifier)
 remove_object(temporary);positive(original)
 return original

# Keep the original sensor object/hierarchy, replacing its solid slab with an
# actual open-front frame and a recessed glass calibration viewport.
sensor=bpy.data.objects['Sorter_sensor_head'];cx=-2.7266636;cz=1.58
outer=clipped_profile(.30,.23,.018,cx,cz)
inner=clipped_profile(.238,.164,.012,cx,cz)
frame=folded_ring('Optical sensor frame authoring',outer,inner,4.394283,4.484283,'dark')
replace_world_mesh(sensor,frame);bevel(sensor,.0008)
for o in list(sensor.children):
 if 'surface_scuffs' in o.name:remove_object(o)
access=bpy.data.objects['Sorter_calibration_access']
for o in list(access.children):
 if o.name.startswith('ART_'):remove_object(o)
lower=plate('Reader lower case authoring',(-2.7066636,4.434283,1.395),.34,.14,.065,'oxide',.012)
replace_world_mesh(access,lower);bevel(access,.0007)
for o in s.objects:
 if o.name.startswith('RF1 | Reader calibration cover side return'):
  matrix=o.matrix_world.copy();matrix.translation.z=1.395;o.matrix_world=matrix;o.scale.z=.114/.315
for r in supports:
 if r['group'].startswith('RF1 | Reader calibration cover side return'):r['anchor'][2]=1.395
for x in [-2.8386636,-2.5746636]:
 screw=cyl('Sorter lower calibration captive screw',(x,4.395783,1.353),.010,.012,'steel',(0,-1,0),6)
 support(screw.name,(x,4.401783,1.353),access.name,(0,1,0))
support(access.name,(-2.73,4.44,1.465),sensor.name,(0,0,1))
back=plate('Optical camera rear cover',(cx,4.479283,cz),.238,.164,.010,'dark',.012)
bevel(back,.0006)
support(back.name,(cx+.119,4.479283,cz),sensor.name,(1,0,0))
glass_material=mat('RF1_optical_viewport_glass',(.018,.050,.064),.15,.10,0)
glass_bsdf=next(n for n in glass_material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
glass_bsdf.inputs['Transmission Weight'].default_value=.48
glass_bsdf.inputs['IOR'].default_value=1.46
glass=plate('Sorter recessed calibration glass',(cx,4.405283,cz),.239,.165,.006,glass_material,.012)
for mod in glass.modifiers:
 if mod.type=='BEVEL':mod.width=.0004
support(glass.name,(cx-.1195,4.405283,cz),sensor.name,(-1,0,0))
barrel=cyl('Sorter calibration camera barrel',(cx-.037,4.450283,cz+.004),.043,.048,'black',(0,-1,0),32)
support(barrel.name,(cx-.037,4.474283,cz+.004),back.name,(0,1,0))
objective=cyl('Sorter dark camera objective',(cx-.037,4.423283,cz+.004),.033,.006,glass_material,(0,-1,0),32)
support(objective.name,(cx-.037,4.426283,cz+.004),barrel.name,(0,1,0))
rim=ring('Sorter objective retaining ring',(cx-.037,4.423283,cz+.004),.038,.003,'steel',(0,-1,0))
support(rim.name,(cx-.037+.038,4.426283,cz+.004),barrel.name,(0,1,0))

# A bent U-channel carries the camera from the actual optical cradle. Its open
# slot, folded sides and top bridge are visible below the unobscured SO-04 label.
bracket=bpy.data.objects['RF1 | Sorter sensor front bracket'];bx=-2.73
profile=[(bx-.0375,4.479283),(bx+.0375,4.479283),
         (bx+.0375,4.555),(bx+.0335,4.555),(bx+.0335,4.485283),
         (bx-.0335,4.485283),(bx-.0335,4.555),(bx-.0375,4.555)]
channel=closed_profile('Sorter channel authoring',profile,1.695,1.916,2,'steel')
replace_world_mesh(bracket,channel)
cutter=box('Optical channel slot cutter',(bx,4.482283,1.797),(.027,.020,.105),'black',.004)
bpy.context.view_layer.update()
boolean=bracket.modifiers.new('Real adjustment slot','BOOLEAN');boolean.operation='DIFFERENCE';boolean.solver='EXACT';boolean.object=cutter
bpy.ops.object.select_all(action='DESELECT');bracket.select_set(True);bpy.context.view_layer.objects.active=bracket
bpy.ops.object.modifier_apply(modifier=boolean.name);remove_object(cutter);positive(bracket);bevel(bracket,.0005)
support(bracket.name,(bx,4.481283,1.695),sensor.name,(0,0,-1))
bridge=box('Sorter channel top bridge',(bx,(4.555+4.609)/2,1.905),(.075,4.609-4.555,.022),'steel',.0006)
support(bridge.name,(bx,4.609,1.905),'RF1 | Sorter internal optical cradle',(0,1,0))
support(bracket.name,(bx+.0355,4.555,1.905),bridge.name,(0,1,0))

# The press door is a pressed, stepped metal surface rather than an outlined
# slab. The outer bearing still meets the original gasket at the same plane.
cover=bpy.data.objects['RF1 | Press hydraulic access cover'];loops=[]
for x,w,h,cut in [(5.598,.72,.41,.045),(5.598,.64,.33,.028),
                  (5.579,.59,.28,.023),(5.582,.59,.28,.023),
                  (5.601,.64,.33,.028),(5.612,.72,.41,.045)]:
 loops.append([(x,a,b) for a,b in clipped_profile(w,h,cut,1.15,.49)])
vs=[v for loop in loops for v in loop];fs=[]
for a,b in [(0,1),(1,2),(3,4),(4,5),(5,0)]:
 for i in range(8):j=(i+1)%8;fs.append((a*8+i,a*8+j,b*8+j,b*8+i))
fs += [tuple(range(16,24)),tuple(reversed(range(24,32)))]
pressed=positive(mesh('Pressed hydraulic door authoring',vs,fs,'green'))
replace_world_mesh(cover,pressed);bevel(cover,.0007)
pull=bpy.data.objects['RF1 | Press service recessed pull'];pull.location.x-=.031
for y in [1.05,1.25]:
 foot=box('Press pull stand-off',(5.5745,y,.61),(.009,.026,.026),'steel',.0006)
 support(foot.name,(5.579,y,.61),cover.name,(1,0,0))
 support(pull.name,(5.570,y,.61),foot.name,(1,0,0))
for o in list(s.objects):
 if o.name.startswith('RF1 | Press access grip polish'):
  remove_object(o);continue
 if o.name.startswith('RF1 | Press access captive bolt'):
  old=o.matrix_world.translation.copy();y=.835 if old.y<1.15 else 1.465;z=.33 if old.z<.49 else .65
  world=o.matrix_world.copy();world.translation=Vector((5.590,y,z));o.matrix_world=world;o.scale.z*=.016/.024
  support(o.name,(5.598,y,z),cover.name,(1,0,0))
stencil=bpy.data.objects['RF1 | Press base service stencil'];world=stencil.matrix_world.copy();world.translation.x=5.57898;world.translation.y=1.40;stencil.matrix_world=world;stencil.data.extrude=.00001
printed=json.loads(s['printed_surface_registry']);printed.append(dict(mark=stencil.name,target=cover.name,direction=[1,0,0]))

# Full-sized pale leather gloves on the exposed left worktop shoulder. Keep the
# entire source glove hierarchy rigid and clear of the press/guide envelopes.
gloves=[o for o in s.objects if o.name.startswith(('Assembly_work_glove','ART_Assembly_work_glove'))]
rigid_group(gloves,Matrix.Translation(Vector((-.861664,1.21,0))))
canvas=mat('RF1_work_glove_pale_leather',(.48,.405,.265),.89,0,.035)
for o in gloves:
 if o.type=='MESH' and 'cuff' not in o.name:
  o.data=o.data.copy()
  for i in range(len(o.data.materials)):o.data.materials[i]=canvas

# Enlarge the existing signed crusher record, keeping its actual door contact.
ticket=bpy.data.objects['RF1 | Crusher signed maintenance sheet'];bpy.context.view_layer.update();pivot=ticket.matrix_world.translation.copy()
record=[o for o in s.objects if o.name.startswith(('RF1 | Crusher signed maintenance sheet','RF1 | Crusher maintenance paper clip','RF1 | Crusher record '))]
enlarge=Matrix.Translation(pivot)@Matrix.Diagonal(Vector((1.42,1,1.42,1)))@Matrix.Translation(-pivot)
rigid_group(record,enlarge)
for r in supports:
 if r['group'] in [o.name for o in record]:r['anchor']=list(enlarge@Vector(r['anchor']))

# The inspection wipe and open caliper occupy measured unused worktop space,
# behind the sample cradle and clear of the scanner feet and sample tins.
cloth_mat=mat('RF1_folded_inspection_cotton',(.055,.112,.14),.97,0,.035)
profile=[(6.18,1.0425),(6.44,1.0425),(6.44,1.046),
         (6.435,1.052),(6.424,1.0585),(6.205,1.0585),
         (6.19,1.053),(6.18,1.046)]
cloth=closed_profile('Inspection folded cotton wipe',profile,-2.36,-2.10,1,cloth_mat);bevel(cloth,.001)
support(cloth.name,(6.31,-2.23,1.0425),'Inspection_work_surface',(0,0,-1))
tool_profile=[(6.22,-2.34),(6.372,-2.34),(6.372,-2.13),
              (6.356,-2.13),(6.356,-2.322),(6.22,-2.322)]
tool=closed_profile('Inspection caliper beam and fixed jaw',tool_profile,1.0655,1.0715,2,'steel');bevel(tool,.00045)
rest=box('Inspection caliper fixed jaw lower cheek',(6.288,-2.331,1.062),(.136,.018,.007),'steel',.0004)
support(rest.name,(6.288,-2.331,1.0585),cloth.name,(0,0,-1))
support(tool.name,(6.288,-2.331,1.0655),rest.name,(0,0,-1))
outer=[(6.345,1.0585),(6.384,1.0585),(6.384,1.0785),(6.345,1.0785)]
inner=[(6.3555,1.065),(6.3725,1.065),(6.3725,1.072),(6.3555,1.072)]
vs=[(x,y,z) for y,p in [(-2.271,outer),(-2.239,outer),(-2.271,inner),(-2.239,inner)] for x,z in p];fs=[]
for i in range(4):
 j=(i+1)%4;fs += [(i,j,4+j,4+i),(8+i,12+i,12+j,8+j),(i,8+i,8+j,j),(4+i,4+j,12+j,12+i)]
slider=positive(mesh('Inspection caliper open sliding sleeve',vs,fs,'dark'));bevel(slider,.00035)
support(slider.name,(6.35,-2.255,1.0585),cloth.name,(0,0,-1))
moving=box('Inspection caliper moving jaw',(6.2825,-2.255,1.065),(.125,.018,.013),'steel',.0004)
support(moving.name,(6.345,-2.255,1.065),slider.name,(1,0,0))
support(moving.name,(6.2825,-2.255,1.0585),cloth.name,(0,0,-1))
for i in range(9):
 mark=box('Caliper engraved scale',(6.361,-2.30+i*.018,1.07151),(.005 if i%2 else .009,.0006,.00002),'ink',0)
 support(mark.name,(6.361,-2.30+i*.018,1.0715),tool.name,(0,0,-1))

s['printed_surface_registry']=json.dumps(printed)
bpy.context.view_layer.update()
