"""Read-only checks of Waste's preserved contracts, physical contacts and fixtures."""
import bpy,json,sys,math,hashlib,re
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[4]
args=sys.argv[sys.argv.index('--')+1:];rev=args[0];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();issues=[]
if not re.fullmatch(r'[A-Za-z0-9_]+',rev):raise ValueError('Validation label must be a safe basename')
cache={}
def tree(o):
 if o.name not in cache:
  e=o.evaluated_get(dg);me=e.to_mesh();cache[o.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);e.to_mesh_clear()
 return cache[o.name]
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [Vector([min(v[i] for v in p) for i in range(3)]),Vector([max(v[i] for v in p) for i in range(3)])]
def contact(name,target,p,d,**extra):
 p=Vector(p);d=Vector(d).normalized();t=s.objects.get(target);gap=angle=None
 if t:
  hit,n,ix,dist=tree(t).ray_cast(p-d*.06,d,.12)
  if hit is not None:gap=dist-.06;angle=math.degrees(math.acos(max(-1,min(1,-n.dot(d)))))
 ok=gap is not None and -.0021<=gap<=.0051 and angle<=12
 if not ok:issues.append('Unseated support '+name)
 return dict(object=name,target=target,anchor=list(p),direction=list(d),gap_m=gap,angle_deg=angle,status='PASS' if ok else 'FAIL',**extra)
protected=json.loads((ROOT/'production/protected_original.json').read_text())['objects'];changed=[]
for name,old in protected.items():
 o=s.objects.get(name)
 if not o or [list(r) for r in o.matrix_world]!=old['matrix_world'] or (o.parent.name if o.parent else None)!=old['parent'] or (o.type=='CAMERA' and (o.data.lens!=old['lens'] or o.data.sensor_width!=old['sensor_width'])):changed.append(name)
if changed:issues.append('Protected original transforms changed')
source=ROOT.parent/'module.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
if source_hash!='8912b5c3b3d2525abb64e838d1fe83a1ea90aa12fea0c9b5a730d4449caecedf':issues.append('Original source changed')
world=s.world.node_tree.nodes['Background'].inputs['Strength'].default_value
if world!=0:issues.append('World illumination nonzero')
fixtures=[]
for o in s.objects:
 if o.type!='LIGHT':continue
 lens=s.objects.get(o.get('physical_lens',''));energies=[];distance=angle=None;aperture=[]
 if lens:
  hit,n,ix,distance=tree(lens).find_nearest(o.matrix_world.translation);axis=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized();angle=math.degrees(math.acos(max(-1,min(1,n.dot(axis)))))
  for m in lens.data.materials:
   if m and m.use_nodes:
    for node in m.node_tree.nodes:
     if node.type=='BSDF_PRINCIPLED':energies.append(node.inputs['Emission Strength'].default_value)
 inside=-6<o.matrix_world.translation.x<6 and 0<o.matrix_world.translation.y<18 and 0<o.matrix_world.translation.z<4.8
 dead=bool(o.get('failed_fixture'))
 if lens:
  width=o.data.size if o.data.type=='AREA' else o.data.shadow_soft_size*2
  height=o.data.size_y if o.data.type=='AREA' and o.data.shape=='RECTANGLE' else width
  offsets=[(0,0),(-.45,0),(.45,0),(0,-.45),(0,.45)] if o.data.type=='AREA' and o.data.shape=='DISK' else [(0,0),(-.45,-.45),(-.45,.45),(.45,-.45),(.45,.45)]
  for x,y in offsets:
   origin=o.matrix_world.translation+o.matrix_world.to_3x3()@Vector((x*width,y*height,0))+axis*.001
   blocked,point,normal,index,obj,matrix=s.ray_cast(dg,origin,axis,distance=.15)
   aperture.append(dict(sample=[x,y],blocked=blocked,object=obj.name if blocked else None,distance_m=(point-origin).length if blocked else None))
 ok=lens is not None and o.data.type!='SUN' and inside and distance is not None and distance<.0051 and angle<=12 and not any(a['blocked'] for a in aperture) and (not dead or (o.data.energy==0 and energies and all(e==0 for e in energies)))
 fixtures.append(dict(source=o.name,lens=lens.name if lens else None,nearest_lens_distance_m=distance,normal_angle_deg=angle,aperture_samples=aperture,energy=o.data.energy,lens_emission=energies,inside=inside,failed=dead,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Invalid practical fixture '+o.name)
# Exhaustive visible emissive-material audit: every luminous surface belongs to a real fixture.
emissive=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 for m in o.data.materials:
  if not m or not m.use_nodes:continue
  for node in m.node_tree.nodes:
   strength=node.inputs['Emission Strength'].default_value if node.type=='BSDF_PRINCIPLED' else (node.inputs['Strength'].default_value if node.type=='EMISSION' else 0)
   if strength<=0:continue
   paired=s.objects.get(o.get('light_source',''))
   ok=paired is not None and paired.type=='LIGHT' and paired.get('physical_lens')==o.name
   emissive.append(dict(object=o.name,material=m.name,strength=strength,paired_source=paired.name if paired else None,status='PASS' if ok else 'FAIL'))
   if not ok:issues.append('Untracked emissive surface '+o.name)
contacts=[]
for r in json.loads(s.get('support_registry','[]')):
 o=s.objects[r['object']];p=Vector(r['anchor']);nearest=tree(o).find_nearest(p)[3] if o.type=='MESH' else None
 contacts.append(contact(o.name,r['target'],p,r['direction'],anchor_distance_to_object_m=nearest))
 if nearest is None or nearest>.0051:issues.append('Support anchor detached from object '+o.name)
legacy=[]
for o in s.objects:
 if not o.get('support_target') or o.get('overhaul_added'):continue
 anchors=o.get('support_anchors',[]);anchors=json.loads(anchors) if isinstance(anchors,str) else anchors;direction=o.get('support_direction',[0,0,-1]);direction=Vector(json.loads(direction) if isinstance(direction,str) else direction);direction=(o.matrix_world.to_3x3()@direction).normalized()
 for i,a in enumerate(anchors):legacy.append(contact(o.name,o['support_target'],o.matrix_world@Vector(a),direction,anchor_index=i))
covered={r['object'] for r in json.loads(s.get('support_registry','[]'))};unregistered=[]
for o in s.objects:
 if not o.get('overhaul_added') or o.type not in {'MESH','FONT','CURVE'}:continue
 ancestor=o
 while ancestor and ancestor.name not in covered:ancestor=ancestor.parent
 if not ancestor:unregistered.append(o.name)
if unregistered:issues.append('Unregistered new geometry supports')
# The inherited lane is 3.6m wide; sample it at cart and worker heights.
route=[]
for x in [-1.79,-1.2,-.6,0,.6,1.2,1.79]:
 for z in [.08,.25,1,1.68,2.39]:
  hit,p,n,ix,o,m=s.ray_cast(dg,Vector((x,4.51,z)),Vector((0,1,0)),distance=9.98)
  if hit:route.append(dict(x=x,z=z,object=o.name,point=list(p)))
if route:issues.append('Central freight lane obstructed')
# Closed additions must have outward winding. Open decals are explicitly excluded.
normals=[];triangles=0
for o in s.objects:
 if o.type not in {'MESH','FONT','CURVE'} or o.hide_render:continue
 e=o.evaluated_get(dg);me=e.to_mesh();triangles+=sum(len(p.vertices)-2 for p in me.polygons);e.to_mesh_clear()
 if o.type!='MESH' or not (o.get('overhaul_added') or o.get('overhaul_modified')):continue
 me=o.data;counts={tuple(sorted(e.vertices)):0 for e in me.edges};directions={key:0 for key in counts}
 for p in me.polygons:
  for i,a in enumerate(p.vertices):
   b=p.vertices[(i+1)%len(p.vertices)];key=tuple(sorted((a,b)));counts[key]+=1;directions[key]+=1 if a<b else -1
 if not counts or any(n!=2 for n in counts.values()):continue
 reference=sum((v.co for v in me.vertices),Vector())/len(me.vertices);relative=[v.co-reference for v in me.vertices];volume=math.fsum(relative[p.vertices[0]].dot(relative[p.vertices[i]].cross(relative[p.vertices[i+1]]))/6 for p in me.polygons for i in range(1,len(p.vertices)-1))*o.matrix_world.to_3x3().determinant()
 inconsistent=sum(v!=0 for v in directions.values());ok=volume>=-1e-8 and inconsistent==0;normals.append(dict(name=o.name,signed_volume_m3=volume,inconsistently_wound_edges=inconsistent,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Inverted closed mesh '+o.name)
# The new extractor must contain air space, with cavity faces directed into that space.
cavity=[]
plenum=s.objects.get('Connected filter plenum')
if plenum and plenum.get('overhaul_modified'):
 centre=Vector((-4.73,16.1,1.16))
 for axis in range(3):
  for sign in [-1,1]:
   direction=Vector([sign if i==axis else 0 for i in range(3)]);origin=centre.copy()
   if axis==0 and sign==1:origin.z=.70 # Sample the solid side below the authored fan opening.
   hit,n,ix,dist=tree(plenum).ray_cast(origin,direction,2)
   ok=hit is not None and .40<dist<.87 and n.dot(direction)<-.95
   cavity.append(dict(axis=axis,sign=sign,origin=list(origin),distance_m=dist,normal_dot_ray=n.dot(direction) if n else None,status='PASS' if ok else 'FAIL'))
   if not ok:issues.append('Extractor cavity invalid '+str(axis)+' '+str(sign))
if triangles>1000000:issues.append('Triangle budget exceeded')
# The added capture hood is hollow and has an open air connection into the header.
capture_cavity=[];capture=s.objects.get('WS | Shield bay angular capture backhood');header=s.objects.get('Longitudinal extract header')
if capture:
 old=s.objects.get('Cell extract drop.001');branch=s.objects.get('WS | Shield capture hollow header branch')
 if old and branch and not old.hide_render:
  a,b=bounds(old);c,d=bounds(branch)
  if all(min(b[k],d[k])-max(a[k],c[k])>.005 for k in range(3)):issues.append('Duplicate original extraction drop intersects capture branch')
 replaced=json.loads(s.get('replaced_capture_members','[]'))
 if replaced and any(not s.objects.get(name) or not s.objects[name].hide_render for name in replaced):issues.append('Superseded capture members still visible')
 for direction,expected in [((-1,0,0),.184),((0,0,1),.314),((0,0,-1),.324),((0,-1,0),1.664),((0,1,0),1.684)]:
  direction=Vector(direction);hit,n,ix,dist=tree(capture).ray_cast(Vector((-5.80,11.40,2.92)),direction,3);ok=hit is not None and abs(dist-expected)<.008 and n.dot(direction)<-.95;capture_cavity.append(dict(direction=list(direction),distance_m=dist,expected_m=expected,status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Capture hood cavity invalid '+str(tuple(direction)))
 origin=Vector((-5.45,11.50,4.0));direction=Vector((0,0,-1));hit,p,n,ix,o,m=s.ray_cast(dg,origin,direction,distance=2);ok=hit and 1.25<(p-origin).length<1.45 and o==capture;capture_cavity.append(dict(test='Header-to-hood open air path',first_hit=o.name if hit else None,distance_m=(p-origin).length if hit else None,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Capture branch air path blocked')
missing=[im.filepath for im in bpy.data.images if im.users and im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
if bpy.data.libraries or missing:issues.append('External dependencies')
# Socket enablement depends on node operation; a connected disabled output silently loses its field.
disabled_material_links=[]
used_materials={m.name:m for o in s.objects if not o.hide_render and hasattr(o.data,'materials') for m in o.data.materials if m}
for name,mat in sorted(used_materials.items()):
 if not mat.use_nodes:continue
 pending=[mat.node_tree];seen=set()
 while pending:
  graph=pending.pop()
  if graph.as_pointer() in seen:continue
  seen.add(graph.as_pointer())
  for node in graph.nodes:
   if node.type=='GROUP' and node.node_tree:pending.append(node.node_tree)
  for link in graph.links:
   if not link.from_socket.enabled or not link.to_socket.enabled:
    disabled_material_links.append(dict(material=name,node=link.from_node.name,output=link.from_socket.name,target_node=link.to_node.name,input=link.to_socket.name))
if disabled_material_links:issues.append('Disabled material sockets are linked: '+str(len(disabled_material_links)))

neck_fasteners=[]
neck=s.objects.get('Filter inlet welded neck')
if neck and s.get('formed_filter_inlet_open'):
 for index in range(4):
  name='Inlet neck flange bolt'+('' if index==0 else '.'+str(index).zfill(3));bolt=s.objects[name];lo,hi=bounds(bolt);centre=(lo+hi)/2;origin=Vector((centre.x,centre.y,hi.z+.002))
  hit,n,poly,distance=tree(neck).ray_cast(origin,Vector((0,0,-1)),.18)
  ok=hit is not None and n.z>.95 and lo.z-.0006<=hit.z<=hi.z+.0006
  neck_fasteners.append(dict(object=name,neck=neck.name,hit=list(hit) if hit is not None else None,bolt_z_interval=[lo.z,hi.z],status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Inherited neck fastener off actual flange: '+name)
filter_inlet_path=[]
if s.get('formed_filter_inlet_open'):
 upper_x=s.get('filter_inlet_upper_x',-5.45);lower_x=s.get('filter_inlet_lower_x',-5.38)
 upper_y=s.get('filter_inlet_upper_y',16.10);lower_y=s.get('filter_inlet_lower_y',16.10)
 lower_z=s.get('filter_inlet_lower_z',2.079)
 slope=(lower_x-upper_x)/(3.806-lower_z) if 'filter_inlet_lower_x' in s else 0
 slope_y=(lower_y-upper_y)/(3.806-lower_z)
 direction=Vector((slope,slope_y,-1)).normalized()
 for dx,yy in [(0,16.10),(.03,16.07),(.03,16.13)]:
  xx=upper_x+dx;yy=yy+upper_y-16.10;origin=Vector((xx,yy,4.0));closest=None
  # A clear angled inlet may terminate at the inward plenum side, not its floor.
  # Match the actual first cavity exit plane rather than interpreting a ray as airflow.
  cavity_low=(-5.480,15.615,.325);cavity_high=(-3.980,16.585,1.995);exits=[]
  for axis in range(3):
   if abs(direction[axis])<1e-8:continue
   boundary=cavity_high[axis] if direction[axis]>0 else cavity_low[axis]
   exits.append(((boundary-origin[axis])/direction[axis],axis))
  expected,exit_axis=min((distance,axis) for distance,axis in exits if distance>0)
  expected_normal=Vector((0,0,0));expected_normal[exit_axis]=-1 if direction[exit_axis]>0 else 1
  for candidate in s.objects:
   if candidate.type not in {'MESH','CURVE'} or candidate.hide_render:continue
   lo,hi=bounds(candidate)
   near,far=0,4.15
   for axis in range(3):
    if abs(direction[axis])<1e-9:
     if not lo[axis]-.001<=origin[axis]<=hi[axis]+.001:far=-1;break
    else:
     first,last=sorted(((lo[axis]-.001-origin[axis])/direction[axis],(hi[axis]+.001-origin[axis])/direction[axis]));near=max(near,first);far=min(far,last)
   if near>far:continue
   q,n,index,distance=tree(candidate).ray_cast(origin,direction,4.15)
   if q is not None and (closest is None or distance<closest[0]):closest=(distance,candidate,n)
  distance,o,n=closest if closest is not None else (None,None,None);ok=bool(o==plenum and abs(distance-expected)<.008 and n.dot(expected_normal)>.95)
  filter_inlet_path.append(dict(origin=[xx,yy,4.0],direction=list(direction),expected_distance=expected,expected_inward_normal=list(expected_normal),hit=o.name if o else None,distance=distance,status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Formed header-to-filter inlet path blocked')
fan_path=[]
if s.get('fan_inlet_open_seated'):
 for dy,dz in [(0,0),(.025,0),(0,.025)]:
  origin=Vector((-4.35,16.08+dy,1.40+dz));direction=Vector((1,0,0));closest=None
  for candidate in s.objects:
   if candidate.type not in {'MESH','CURVE'} or candidate.hide_render:continue
   lo,hi=bounds(candidate)
   if not lo.y-.001<=origin.y<=hi.y+.001 or not lo.z-.001<=origin.z<=hi.z+.001 or hi.x<origin.x or lo.x>origin.x+1.20:continue
   hit,n,face,distance=tree(candidate).ray_cast(origin,direction,1.20)
   if hit is not None and (closest is None or distance<closest[0]):closest=(distance,candidate,n)
  distance,obj,n=closest if closest is not None else (None,None,None);ok=bool(obj and obj.name=='WS | Fan actual impeller hub' and abs(distance-.776)<.008 and n.x<-.95)
  fan_path.append(dict(origin=list(origin),hit=obj.name if obj else None,distance=distance,status='PASS' if ok else 'FAIL',scope='Open filter chamber through seated coupling to static rotor; not an airflow simulation'))
  if not ok:issues.append('Filter-to-fan coupling blocked or detached')
# New authored geometry must stay inside the isolated room; original portal/wall geometry
# remains governed by its unchanged source contract and protected poses.
strap_closure_clearance=[]
for strap_id in range(2):
 strap=s.objects.get('WS | Overpack captive restraint strap '+str(strap_id))
 if not strap:continue
 a,b=bounds(strap.evaluated_get(dg))
 for bolt_id in range(6):
  bolt=s.objects['WS | Overpack closure captive bolt '+str(bolt_id)];c,d=bounds(bolt.evaluated_get(dg));overlap=[min(b[k],d[k])-max(a[k],c[k]) for k in range(3)]
  ok=any(v<=-.0001 for v in overlap)
  strap_closure_clearance.append(dict(strap=strap.name,bolt=bolt.name,overlap_xyz_m=overlap,status='PASS' if ok else 'FAIL'))
  if not ok:issues.append('Crown web intersects closure bolt '+str(strap_id)+' '+str(bolt_id))
geometry_integrity=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or not o.get('overhaul_modified'):continue
 ok=len(o.data.vertices)>=3 and len(o.data.polygons)>=1
 geometry_integrity.append(dict(object=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Modified visible geometry is empty '+o.name)
new_bounds=[]
for o in s.objects:
 if not o.get('overhaul_added') or o.hide_render or o.type not in {'MESH','CURVE','FONT'}:continue
 e=o.evaluated_get(dg);pts=[e.matrix_world@Vector(v) for v in e.bound_box];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)]
 ok=lo[0]>=-6.0051 and hi[0]<=6.0051 and lo[1]>=-.0051 and hi[1]<=18.0051 and lo[2]>=-.0051 and hi[2]<=4.8051
 new_bounds.append(dict(object=o.name,min=lo,max=hi,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('New geometry outside room '+o.name)
# Curved wear patches must seat across their faces, not only at projected corners.
projected_wear=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or not o.get('surface_projected'):continue
 target=s.objects.get(o.get('support_target',''));values=[]
 if target:
  stride=max(1,len(o.data.polygons)//600)
  for polygon_index in range(0,len(o.data.polygons),stride):
   poly=o.data.polygons[polygon_index]
   centre=o.matrix_world@poly.center;point,n,index,distance=tree(target).find_nearest(centre)
   if point is not None:values.append((centre-point).dot(n))
 ok=bool(values) and min(values)>.000025 and max(values)<.00055
 projected_wear.append(dict(object=o.name,target=target.name if target else None,sampled_faces=len(values),min_signed_gap_m=min(values) if values else None,max_signed_gap_m=max(values) if values else None,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Curved coating patch sinks below shell '+o.name)
# Freight additions must retain the actual receiving and dispatch clear apertures.
portal_clearance=[]
if s.get('freight_coamings_openings_preserved'):
 for name,yy,half,topheight,distance in [('receiving',-.42,1.50,3.20,1.10),('dispatch',17.49,1.20,2.80,.94)]:
  for xx in [-half+.02,-half/2,0,half/2,half-.02]:
   for zz in [.10,.50,1.68,topheight-.40,topheight-.02]:
    hit,point,normal,index,obj,matrix=s.ray_cast(dg,Vector((xx,yy,zz)),Vector((0,1,0)),distance=distance)
    portal_clearance.append(dict(portal=name,x=xx,z=zz,hit=obj.name if hit else None,status='FAIL' if hit else 'PASS'))
    if hit:issues.append('Reserved freight aperture blocked '+name+' '+obj.name)
clamp_checks=[]
if s.get('seal_service_clamp_bored'):
 bridge=s.objects['WS | Seal service fixed C clamp bridge'];shoe=s.objects['WS | Seal service swiveling pressure shoe'];removed=s.objects['WS | Brittle removed seal']
 bench_top=max(v.z for v in [s.objects['Thick plywood worktop'].matrix_world@Vector(p) for p in s.objects['Thick plywood worktop'].bound_box])
 hit,n,index,distance=tree(bridge).ray_cast(Vector((4.485,16.955,bench_top+.20)),Vector((0,0,-1)),.19)
 ok=hit is None;clamp_checks.append(dict(test='Pressure spindle casting bore',status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Seal clamp spindle intersects bridge casting')
 point=shoe.matrix_world.translation-Vector((0,0,.003));nearest=tree(removed).find_nearest(point)[3];ok=nearest is not None and nearest<.0006
 clamp_checks.append(dict(test='Pressure shoe on rejected seal',gap_m=nearest,status='PASS' if ok else 'FAIL'))
 if not ok:issues.append('Seal clamp pressure shoe detached from rejected seal')
report=dict(revision=rev,blend=Path(bpy.data.filepath).resolve().relative_to(REPO).as_posix(),blend_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),original_sha256=source_hash,disabled_material_links=disabled_material_links,protected_count=len(protected),protected_changes=changed,world_strength=world,fixture_checks=fixtures,emissive_surface_checks=emissive,new_contacts=contacts,inherited_contacts=legacy,new_geometry_bounds=new_bounds,modified_geometry_integrity=geometry_integrity,strap_closure_clearance_checks=strap_closure_clearance,unregistered_new_supports=unregistered,route_obstructions=route,freight_aperture_checks=portal_clearance,projected_wear_face_checks=projected_wear,seal_clamp_checks=clamp_checks,closed_mesh_normals=normals,extractor_cavity_checks=cavity,capture_air_path_checks=capture_cavity,filter_inlet_path_checks=filter_inlet_path,neck_fastener_checks=neck_fasteners,fan_inlet_path_checks=fan_path,visible_evaluated_triangles=triangles,issues=issues,status='PASS' if not issues else 'FAIL',limits='Registered anchor rays and sampled lane rays are not exhaustive collision certification. A nearest-lens check proves location, not complete fixture beam aperture coverage; protected original assembly poses are retained; fixture seats and directions are checked against the current authored lenses.')
(ROOT/'production'/('validation_'+rev+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('VALIDATION',report['status'],triangles,issues,flush=True)
if issues:sys.exit(1)
