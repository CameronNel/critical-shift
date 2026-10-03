"""R13: bounded hose-band squeeze instead of deeply buried toroidal clamps."""
import bmesh
def hollow_profile(name,outer,inner):
 """An annular bevel profile gives actual tube walls and annular end faces."""
 profile=bpy.data.curves.new(name,'CURVE');profile.dimensions='2D';profile.fill_mode='BOTH'
 for radius,winding in [(outer,-1),(inner,1)]:
  spline=profile.splines.new('POLY');spline.points.add(47)
  for i,p in enumerate(spline.points):
   a=winding*2*math.pi*i/48;p.co=(radius*math.cos(a),radius*math.sin(a),0,1)
  spline.use_cyclic_u=True
 obj=link(bpy.data.objects.new('RF1 PROFILE | '+name,profile))
 obj.hide_render=True;obj.hide_set(True)
 return obj

for name,outer,inner in [('Processor_product_line',.110,.096),
                         ('RF1 | Refined product interstage hose',.067,.052)]:
 o=bpy.data.objects[name];o.data=o.data.copy()
 o.data.bevel_mode='OBJECT';o.data.bevel_object=hollow_profile(name+' annular section',outer,inner)
 o.data.use_fill_caps=True
 o['tube_outer_radius_m']=outer;o['tube_inner_radius_m']=inner
 o['tube_ends_annular']=True
 # Weld Blender's separate annular-cap vertices to the swept tube wall and
 # orient the closed material volume. Both pipe openings remain clear.
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 o=bpy.context.view_layer.objects.active;bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
 assert not any(e.is_boundary for e in bm.edges),(name,'Unclosed tube material')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 positive(o)
 if not o.get('authoring_owner'):tag(o)
 o.select_set(False)

for o in s.objects:
 if not o.name.startswith('RF1 | Interstage hose compression band'):continue
 o.data=o.data.copy()
 for v in o.data.vertices:
  radial=Vector((v.co.x,v.co.y,0));length=radial.length
  if length:
   new_radius=length+.0035
   v.co.x*=new_radius/length;v.co.y*=new_radius/length
 o['compression_band_major_radius_m']=.0725
 o['intended_radial_squeeze_m']=.0005
 o['support_group']='RF1 | Refined product interstage hose'
 for sign in [-1,1]:
  radial=o.matrix_world.to_3x3()@Vector((sign,0,0))
  point=o.matrix_world.translation+radial*.0665
  support(o.name,point,'RF1 | Refined product interstage hose',-radial)

# The internal rising feed stays on the screw-casing axis. The old 50 mm lean
# let its steel wall project through the orange casing as a triangular wedge.
feed=bpy.data.objects['Processor_sorted_feed'];feed.data=feed.data.copy()
feed.data.splines.clear();spline=feed.data.splines.new('POLY');spline.points.add(5)
path=[(-.3566637,4.934283,1.25),(-.190,4.934283,1.25),
      (-.08,4.984283,1.25),(.093336,4.984283,1.25),
      (.093336,4.984283,2.05),(.433336,4.984283,2.05)]
inv=feed.matrix_world.inverted()
for p,co in zip(spline.points,path):p.co=(*(inv@Vector(co)),1)
feed['rising_feed_axis_matches_casing']=True

# A shaped return on the press access sheet carries the panel into its frame.
# Unlike a decorative outline, this is an actual folded thickness at the sides.
for y in [.7835,1.5165]:
 lip=box('Press access sheet folded return',(5.614,y,.49),(.026,.013,.337),'green',.0006)
 support(lip.name,(5.625,y,.49),'RF1 | Press hydraulic cast base',(1,0,0))

# The reader service face sits within a returned edge instead of a flat plate.
head=bpy.data.objects['Sorter_calibration_access'];lo,hi=bounds_world(head)
for x,direction in [(lo.x-.006,(1,0,0)),(hi.x+.006,(-1,0,0))]:
 lip=box('Reader calibration cover side return',(x,(lo.y+hi.y)/2,(lo.z+hi.z)/2),(.012,hi.y-lo.y+.002,hi.z-lo.z-.035),'dark',.0006)
 contact=lo.x if x<lo.x else hi.x
 support(lip.name,(contact,(lo.y+hi.y)/2,(lo.z+hi.z)/2),head.name,direction)

# Move the existing work glove to the visible, empty right-hand deck beside the
# alignment tools. The source mesh, fingers and interactive hierarchy stay intact.
gloves=[o for o in s.objects if o.name.startswith(('Assembly_work_glove','ART_Assembly_work_glove'))]
rigid_group(gloves,Matrix.Translation(Vector((.89,-1.29,0))))

# A single clipped service record at the crusher door gives that station a human
# cue without filling the route or adding another prop pile.
door=bpy.data.objects['Crusher_service_hinged_panel'];lo,hi=bounds_world(door)
x=-5.65;y=lo.y-.0004;z=1.84
ticket=box('Crusher signed maintenance sheet',(x,y,z),(.19,.0008,.21),'paper',0)
support(ticket.name,(x,lo.y,z),door.name,(0,1,0))
clip=box('Crusher maintenance paper clip',(x,y-.004,z+.105),(.06,.008,.018),'steel',.0005)
support(clip.name,(x,lo.y,z+.105),door.name,(0,1,0))
printed=json.loads(s['printed_surface_registry'])
for name,body,xx,zz,size in [('Crusher record header','03 / SERVICE',x-.080,z+.060,.021),
                            ('Crusher record signed','JAW CHECK\n07 / M.A.',x-.075,z+.020,.018)]:
 ink=text(name,body,(xx,lo.y-.00082,zz),size,'ink');ink.data.extrude=.00001
 printed.append(dict(mark=ink.name,target=ticket.name,direction=[0,1,0]))
s['printed_surface_registry']=json.dumps(printed)
bpy.context.view_layer.update()
