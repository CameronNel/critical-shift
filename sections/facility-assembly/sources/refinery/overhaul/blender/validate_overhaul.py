"""Read-only refinery interface, route, contact, dependency and practical-light checks."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];src=Path(bpy.data.filepath)
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['current'];rev=a[0]
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();issues=[]
def bounds(o):
 p=[o.matrix_world@Vector(c) for c in o.bound_box];return [Vector([min(v[i] for v in p) for i in range(3)]),Vector([max(v[i] for v in p) for i in range(3)])]
cache={}
def tree(o):
 if o.name not in cache:
  e=o.evaluated_get(dg);me=e.to_mesh();cache[o.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);e.to_mesh_clear()
 return cache[o.name]
base=json.loads((root/'production/baseline_interfaces.json').read_text());changes=[]
for name,g in base['protected'].items():
 o=bpy.data.objects.get(name)
 if not o:changes.append(name);continue
 actual=dict(matrix=[list(r) for r in o.matrix_world],vertices=[list(v.co) for v in o.data.vertices] if o.type=='MESH' else [])
 if actual!=g:changes.append(name)
if changes:issues.append('Protected shell/port coordinates changed')
world=s.world.node_tree.nodes.get('Background');world_strength=world.inputs['Strength'].default_value if world else None
if world_strength!=0:issues.append('Nonzero world illumination')
lightchecks=[]
for o in s.objects:
 if o.type!='LIGHT':continue
 lens=bpy.data.objects.get(o.get('fixture_lens',''))
 if o.data.type=='SUN' or not lens:issues.append('Unmotivated light '+o.name);continue
 hit,normal,index,distance=tree(lens).find_nearest(o.matrix_world.translation)
 emission=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 angle=math.degrees(math.acos(max(-1,min(1,normal.dot(emission))))) if normal else None
 result=dict(name=o.name,lens=lens.name,distance_m=distance,emission_normal_angle_deg=angle,energy=o.data.energy,light_type=o.data.type,inside_room=abs(o.location.x)<7.506664 and abs(o.location.y)<6.434284 and 0<o.location.z<4.8)
 lightchecks.append(result)
 if distance is None or distance>.021 or not result['inside_room']:issues.append('Unseated/outside practical '+o.name)
 if angle is None or angle>12:issues.append('Practical emission does not match lens '+o.name)
 # A lens/axis match alone does not prove the beam can leave its physical housing.
 aperture=[]
 for ax,ay in [(0,0),(-.40,-.40),(-.40,.40),(.40,-.40),(.40,.40)]:
  offset=o.matrix_world.to_3x3()@Vector((ax*o.data.size,ay*o.data.size_y,0))
  origin=o.matrix_world.translation+offset+emission*.001
  blocked,point,nn,ix,object_hit,matrix=s.ray_cast(dg,origin,emission,distance=.15)
  receiver=blocked and bool(o.get('task_receiver_prefix')) and object_hit.name.startswith(o['task_receiver_prefix'])
  aperture.append(dict(sample=[ax,ay],blocked=blocked and not receiver,task_receiver=receiver,object=object_hit.name if blocked else None,distance_m=(point-origin).length if blocked else None))
 result['aperture_samples']=aperture
 if any(a['blocked'] for a in aperture):issues.append('Practical aperture obstructed '+o.name)
missing_images=[im.filepath for im in bpy.data.images if im.users and im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()]
missing_libraries=[l.filepath for l in bpy.data.libraries if not Path(bpy.path.abspath(l.filepath)).exists()]
if missing_images or missing_libraries:issues.append('Missing used dependencies')
# Check the evaluated hose against each registered annular fitting, independently
# of nominal bore dimensions and logical support declarations.
fitting_checks=[]
if s.get('overhaul_revision',0)>=12:
 hose=s.objects.get('RF1 | Refined product interstage hose')
 evaluated=hose.evaluated_get(dg);me=evaluated.to_mesh()
 hose_vertices=[evaluated.matrix_world@v.co for v in me.vertices];evaluated.to_mesh_clear()
 directions=[Vector((1,.231,.173)).normalized(),Vector((.153,1,.217)).normalized(),Vector((.193,.137,1)).normalized()]
 def inside_closed(p,bvh,d):
  count=0;origin=p.copy()
  for _ in range(128):
   hit,n,ix,distance=bvh.ray_cast(origin,d,2)
   if hit is None:break
   count+=1;origin=hit+d*.000005
  return count%2==1
 for r in json.loads(s.get('hose_fitting_registry','[]')):
  o=s.objects.get(r['name']);axis=Vector(r['axis']).normalized();centre=Vector(r['centre'])
  bvh=tree(o);blocked=bvh.ray_cast(centre-axis*.20,axis,.40)[0] is not None
  buried=sum(sum(inside_closed(p,bvh,d) for d in directions)>=2 for p in hose_vertices)
  overlaps=len(tree(hose).overlap(bvh))
  ok=not blocked and buried==0 and overlaps==0
  fitting_checks.append(dict(name=o.name,axial_ray_blocked=blocked,hose_vertices_inside=buried,surface_overlap_pairs=overlaps,status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Hose fitting obstruction '+o.name)
# Check actual mark bounds against the paper face, independent of authored target poses.
band_checks=[];reducer_checks=[]
if s.get('overhaul_revision',0)>=13:
 hose=s.objects['RF1 | Refined product interstage hose'];e=hose.evaluated_get(dg);me=e.to_mesh()
 world_vertices=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
 for o in s.objects:
  if not o.name.startswith('RF1 | Interstage hose compression band'):continue
  inv=o.matrix_world.inverted();local_vertices=[inv@v for v in world_vertices]
  outer=[math.hypot(v.x,v.y) for v in local_vertices if abs(v.z)<.007]
  bore=min(math.hypot(v.co.x,v.co.y) for v in o.data.vertices)
  squeeze=max(outer)-bore if outer else None
  ok=squeeze is not None and -.002<=squeeze<=.002
  band_checks.append(dict(name=o.name,measured_bore_m=bore,max_hose_radius_m=max(outer) if outer else None,radial_squeeze_m=squeeze,status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Compression band fit '+o.name)
 for name in ['Processor_product_line','RF1 | Processor product coupling','RF1 | Refined product interstage hose']:
  blocked=tree(s.objects[name]).ray_cast(Vector((2.425,4.898283,1.438)),Vector((1,0,0)),.052)[0] is not None
  reducer_checks.append(dict(name=name,short_interface_axis_blocked=blocked,status='FAIL' if blocked else 'PASS'))
  if blocked:issues.append('Reducer interface disk obstruction '+name)
printed_checks=[]
for r in json.loads(s.get('printed_surface_registry','[]')):
 mark=s.objects.get(r['mark']);target=s.objects.get(r['target']);d=Vector(r['direction']).normalized()
 if not mark or not target:
  issues.append('Missing printed surface '+r['mark']);continue
 lo,hi=bounds(mark);p=(lo+hi)/2
 hit,n,index,distance=tree(target).ray_cast(p-d*.001,d,.003)
 gap=distance-.001 if distance is not None else None
 ok=gap is not None and -.0001<=gap<=.0002 and n.dot(d)<-math.cos(math.radians(12))
 printed_checks.append(dict(**r,gap_m=gap,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Unseated printed mark '+mark.name)
ear_checks=[]
if s.get('overhaul_revision',0)>=10:
 for o in s.objects:
  if o.name.startswith(('RF1 | Ear defender soft sealing pad','RF1 | Ear defender ochre cup')):
   lo,hi=bounds(o);ratio=(hi.z-lo.z)/(hi.y-lo.y);ok=ratio>=1.3
   ear_checks.append(dict(name=o.name,height_to_width=ratio,status='PASS' if ok else 'FAIL'))
   if not ok:issues.append('Horizontal ear-cup ellipse '+o.name)
# Physical contact against the nominated target, with explicit support direction.
contacts=[]
for r in json.loads(s.get('support_registry','[]')):
 target=bpy.data.objects.get(r['target']);p=Vector(r['anchor']);d=Vector(r['direction']).normalized()
 if not target:contacts.append(dict(**r,status='MISSING_TARGET'));issues.append('Missing support '+r['group']);continue
 hit,n,index,dist=tree(target).ray_cast(p-d*.06,d,.12)
 gap=dist-.06 if dist is not None else None
 ok=gap is not None and -.0021<=gap<=.0051 and n.dot(d)<-math.cos(math.radians(12))
 contacts.append(dict(**r,gap_m=gap,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Support gap '+r['group'])
# Resolve inherited contracts using their actual child anchors where available.
legacy=[]
for o in s.objects:
 if not o.get('support_dependent'):continue
 target=bpy.data.objects.get(o.get('cs_support_target',''))
 label=o.get('cs_support_direction','');mapping={'-Z':(0,0,-1),'+Z':(0,0,1),'-X':(-1,0,0),'+X':(1,0,0),'-Y':(0,-1,0),'+Y':(0,1,0)}
 space,_,axis_label=label.partition('_')
 if not target or space not in {'WORLD','LOCAL'} or axis_label not in mapping:
  legacy.append(dict(name=o.name,status='UNRESOLVED'));issues.append('Unresolved inherited support '+o.name);continue
 d=Vector(mapping[axis_label])
 if space=='LOCAL':d=(o.matrix_world.to_3x3()@d).normalized()
 anchors=[a for a in o.children_recursive if a.type=='EMPTY' and a.name.startswith('SUPPORT_')]
 if anchors:points=[(a.name,a.matrix_world.translation.copy()) for a in anchors]
 else:
  axis=max(range(3),key=lambda i:abs(d[i]));lo,hi=bounds(o);p=(lo+hi)/2;p[axis]=hi[axis] if d[axis]>0 else lo[axis];points=[('bbox_face',p)]
 for name,p in points:
  hit,n,ix,dist=tree(target).ray_cast(p-d*.06,d,.12);gap=dist-.06 if dist is not None else None
  angle=math.degrees(math.acos(max(-1,min(1,-n.dot(d))))) if n else None
  ok=gap is not None and -.0021<=gap<=.0051 and angle<=12
  legacy.append(dict(name=o.name,anchor=name,target=target.name,gap_m=gap,angle_deg=angle,status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Inherited support gap '+o.name)
# Closed newly authored mesh winding is testable, unlike open decals or cloth.
normal_checks=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or not o.get('authoring_owner'):continue
 me=o.data;edge_use={tuple(sorted(e.vertices)):0 for e in me.edges}
 for p in me.polygons:
  for edge in p.edge_keys:edge_use[tuple(sorted(edge))]+=1
 if not edge_use or any(n!=2 for n in edge_use.values()):continue
 volume=sum(me.vertices[p.vertices[0]].co.dot(me.vertices[p.vertices[i]].co.cross(me.vertices[p.vertices[i+1]].co))/6 for p in me.polygons for i in range(1,len(p.vertices)-1))*o.matrix_world.to_3x3().determinant()
 normal_checks.append(dict(name=o.name,signed_volume_m3=volume,status='PASS' if volume>=-1e-8 else 'FAIL'))
 if volume<-1e-8:issues.append('Inverted closed mesh '+o.name)
# Fixed primary 2.8 m central route; actual scene ray tests at worker and cart heights.
route=[]
for x in [-3.5,-2,0,2,3.5]:
 for z in [.25,1.0,1.68]:
  hit,p,n,ix,obj,matrix=s.ray_cast(dg,Vector((x,-.86,z)),Vector((0,1,0)),distance=2.72)
  if hit:route.append(dict(x=x,z=z,object=obj.name,point=list(p)))
if route:issues.append('Primary route obstruction')
tris=0;mesh_count=0;curve_font_tris=0
for o in s.objects:
 if o.type in {'MESH','CURVE','FONT'} and not o.hide_render:
  e=o.evaluated_get(dg);me=e.to_mesh();count=sum(len(p.vertices)-2 for p in me.polygons)
  tris+=count
  if o.type=='MESH':mesh_count+=1
  else:curve_font_tris+=count
  e.to_mesh_clear()
if tris>1000000:issues.append('One million triangle authoring budget exceeded')
report=dict(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),revision=rev,protected_count=len(base['protected']),protected_changes=changes,world_strength=world_strength,light_checks=lightchecks,missing_images=missing_images,missing_libraries=missing_libraries,hose_fitting_checks=fitting_checks,compression_band_checks=band_checks,reducer_interface_checks=reducer_checks,printed_surface_checks=printed_checks,ear_cup_aspect_checks=ear_checks,new_support_contacts=contacts,legacy_support_screen=legacy,closed_mesh_normals=normal_checks,route_obstructions=route,visible_evaluated_triangles=tris,visible_curve_font_triangles=curve_font_tris,visible_mesh_count=mesh_count,issues=issues,status='PASS' if not issues else 'FAIL',limits='Four fitting axial rays and evaluated hose overlaps, two band sections, short reducer-interface rays, printed mark centers, explicit support anchors, inherited anchor/bounding-face checks and closed-mesh winding are not exhaustive self-intersection, buried-volume, fluid simulation or runtime collision certification. Triangle totals include visible evaluated mesh, curve and font geometry.')
(root/'production'/f'validation_{rev}.json').write_text(json.dumps(report,indent=2));print('VALIDATION',report['status'],'triangles',tris,'issues',issues,flush=True)
if issues:sys.exit(1)
