"""R12: open, aligned hose fittings and crisp formed sheet construction."""

def annular_part(o,outer,inner,depth,hexagon=False,left_inner=None):
 """Closed material volume with an axial bore; no centre disk faces."""
 N=48;vs=[]
 for z,r,is_outer in [(-depth/2,outer,True),(depth/2,outer,True),
                       (-depth/2,left_inner or inner,False),(depth/2,inner,False)]:
  for i in range(N):
   a=2*math.pi*i/N
   radius=r
   if hexagon and is_outer:
    radius=r*math.cos(math.pi/6)/math.cos((a%(math.pi/3))-math.pi/6)
   vs.append((radius*math.cos(a),radius*math.sin(a),z))
 fs=[]
 for i in range(N):
  j=(i+1)%N
  fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),
             (i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 materials=list(o.data.materials);me=bpy.data.meshes.new(o.name+' through-bore')
 me.from_pydata(vs,[],fs)
 for material in materials:me.materials.append(material)
 o.data=me;positive(o)
 for modifier in list(o.modifiers):o.modifiers.remove(modifier)
 for face in me.polygons:
  if face.index%4 in [0,1] and not(hexagon and face.index%4==0):face.use_smooth=True
 bevel(o,.00045)
 o['axial_bore_radius_m']=inner;o['fitting_has_through_bore']=True
 return o

# End the inherited product pipe on its actual nozzle axis. Its old terminal was
# 14 mm sideways / 18 mm down, and its 130 mm radius exceeded the 117 mm throat.
outlet=bpy.data.objects['Processor_product_line'];cu=outlet.data.copy();outlet.data=cu
cu.splines.clear();sp=cu.splines.new('BEZIER');sp.bezier_points.add(3)
world_points=[(1.653336,4.984283,1.55),(2.12,4.984283,1.55),
              (2.30,4.898283,1.438),(2.433,4.898283,1.438)]
inv=outlet.matrix_world.inverted()
for p,co in zip(sp.bezier_points,world_points):
 p.co=inv@Vector(co);p.handle_left_type='AUTO';p.handle_right_type='AUTO'
tip=sp.bezier_points[-1];tip.handle_left_type='FREE';tip.handle_right_type='FREE'
tip.handle_left=inv@Vector((2.395,4.898283,1.438));tip.handle_right=inv@Vector((2.471,4.898283,1.438))
cu.bevel_depth=.110;cu.bevel_resolution=3;cu.resolution_u=16;cu.use_fill_caps=True
outlet['terminal_nozzle_axis_aligned']=True

hose=bpy.data.objects['RF1 | Refined product interstage hose'];sp=hose.data.splines[0]
start=sp.bezier_points[0];start.co=(2.462,4.898283,1.438)
start.handle_left_type='FREE';start.handle_right_type='FREE'
start.handle_left=(2.427,4.898283,1.438);start.handle_right=(2.497,4.898283,1.438)
end=sp.bezier_points[-1];end.co=(2.911,4.970,1.520)
end.handle_left_type='FREE';end.handle_right_type='FREE'
end.handle_left=(2.878,4.970,1.520);end.handle_right=(2.944,4.970,1.520)
bpy.context.view_layer.update()

def hose_pose_at_x(x):
 points=sp.bezier_points
 for a,b in zip(points,points[1:]):
  if a.co.x<=x<=b.co.x:break
 q=[a.co.copy(),a.handle_right.copy(),b.handle_left.copy(),b.co.copy()]
 def at(t):return (1-t)**3*q[0]+3*(1-t)**2*t*q[1]+3*(1-t)*t*t*q[2]+t**3*q[3]
 low,high=0.,1.
 for _ in range(40):
  t=(low+high)/2
  if at(t).x<x:low=t
  else:high=t
 t=(low+high)/2;point=at(t)
 tangent=3*(1-t)**2*(q[1]-q[0])+6*(1-t)*t*(q[2]-q[1])+3*t*t*(q[3]-q[2])
 return point,tangent.normalized()

processor=bpy.data.objects['RF1 | Processor product coupling']
annular_part(processor,.146,.0685,.030,left_inner=.1105)
dryer=bpy.data.objects['RF1 | Dryer product inlet flange']
annular_part(dryer,.155,.075,.035)
nut=bpy.data.objects['RF1 | Product hose hex compression nut']
annular_part(nut,.103,.0715,.077,True)
neck=bpy.data.objects['RF1 | Product coupling neck sleeve']
annular_part(neck,.071,.0685,.031)
for o,x in [(nut,2.508),(neck,2.478)]:
 point,axis=hose_pose_at_x(x)
 o.matrix_world=Matrix.Translation(point)@axis.to_track_quat('Z','Y').to_matrix().to_4x4()

# Compression bands follow the actual hose centre and tangent.
for o,x in [(bpy.data.objects['RF1 | Interstage hose compression band'],2.562),
            (bpy.data.objects['RF1 | Interstage hose compression band.001'],2.863)]:
 point,axis=hose_pose_at_x(x)
 o.matrix_world=Matrix.Translation(point)@axis.to_track_quat('Z','Y').to_matrix().to_4x4()

# Replace obsolete centre-face support declarations with actual annular material.
supports[:]=[r for r in supports if r['group'] not in [dryer.name,hose.name]]
support(dryer.name,(2.9115,4.970,1.655),'RF1 | DR06 horizontal thermal drum',(1,0,0))
bpy.context.view_layer.update()
point,axis=hose_pose_at_x(2.478);radial=axis.to_track_quat('Z','Y')@Vector((1,0,0))
support(hose.name,point+radial*.067,neck.name,radial)
support(neck.name,point+radial*.071,nut.name,radial)
support(processor.name,(2.433,4.898283,1.575),'Processor_product_nozzle_flange',(-1,0,0))
s['hose_fitting_registry']=json.dumps([dict(name=o.name,axis=list(o.matrix_world.to_3x3()@Vector((0,0,1))),centre=list(o.matrix_world.translation)) for o in [processor,dryer,nut,neck]])

# Sheet housings have a small break at the sheared edge; their broad profiles stay planar.
sheet_terms=['compact folded reader','compact reader front seal','hydraulic access cover',
             'Inspection folded','Crusher recessed jaw','crusher jaw folded','Press stepped crown']
for o in s.objects:
 if o.type!='MESH':continue
 if any(term.lower() in o.name.lower() for term in sheet_terms) or o.name=='Crusher_feed_hood_roof':
  for modifier in o.modifiers:
   if modifier.type=='BEVEL':modifier.width=min(modifier.width,.001);modifier.segments=1

# The service trunk recedes behind the coloured equipment and primary black structure.
service=manufactured_paint('RF1_muted_service_trunk',(.112,.137,.129),.74,.10,110)
o=bpy.data.objects['Utility_0'];o.data=o.data.copy()
for i in range(len(o.data.materials)):o.data.materials[i]=service

# Keep wood burnish inside the true edge, including the left short patch.
table=bpy.data.objects['RF1 | Workbench timber top'];lo,hi=bounds_world(table)
for o in s.objects:
 if not o.name.startswith('RF1 | Nook timber working-edge polish'):continue
 width=o.dimensions.x;matrix=o.matrix_world.copy()
 matrix.translation.x=max(lo.x+width/2+.010,min(hi.x-width/2-.010,matrix.translation.x))
 o.matrix_world=matrix
bpy.context.view_layer.update()
