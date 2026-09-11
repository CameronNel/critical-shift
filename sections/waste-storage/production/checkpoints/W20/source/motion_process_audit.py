"""Fresh-artifact door poses and explicit process routing; never saves Blender."""
from pathlib import Path
exec(compile((Path(__file__).parent/'validate_scene.py').read_text(),'validate_scene.py','exec'))
results=[]
def descendants(root):
 out=[]
 for o in s.objects:
  p=o.parent
  while p is not None and p!=root:p=p.parent
  if p==root:out.append(o)
 return out
for name in ['WS_PERSONNEL_LEAF','WS_MONITOR_BOOTH_LEAF']:
 root=s.objects[name];members=descendants(root);own={o.name for o in members};old=root.rotation_euler.z;frames=[]
 for k in range(19):
  angle=root['closed_angle_z']+(root['open_angle_z']-root['closed_angle_z'])*k/18;root.rotation_euler.z=angle;bpy.context.view_layer.update();dg2=bpy.context.evaluated_depsgraph_get();bad=[]
  for o in members:
   if o.type not in ['MESH','CURVE']:continue
   e=o.evaluated_get(dg2);me=e.to_mesh();vv=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
   if not vv:continue
   lo=Vector([min(v[a] for v in vv) for a in range(3)]);hi=Vector([max(v[a] for v in vv) for a in range(3)])
   for n,g in geometry.items():
    if n in own or g['object'].type=='FONT':continue
    # Hinges, strike jambs and seating frame have designed contact at closure.
    if n.startswith(('Personnel outer strike jamb','Personnel jamb hinge leaf','Booth fixed hinge backing','Booth jamb','Booth door transom','Booth header')):continue
    par=g['object'].parent
    if par and par.get('portal_id')==root['door_id']:continue
    if overlap(lo,hi,g):bad.append([o.name,n])
  frames.append({'angle_degrees':math.degrees(angle),'collisions':bad})
 root.rotation_euler.z=old;bpy.context.view_layer.update()
 results.append({'id':name,'pass':all(not f['collisions'] for f in frames),'frames':frames,'method':'19 evaluated conservative AABB poses; own frame/hinge contact excluded; no neighboring scene available.'})
# Axis-aligned duct joints: measured separation/overlap, independent of empties.
def gap(a,b):return math.sqrt(sum(max(0,a['lo'][k]-b['hi'][k],b['lo'][k]-a['hi'][k])**2 for k in range(3)))
pairs=[('Connected filter plenum','Filter inlet welded neck'),('Filter inlet welded neck','Filter inlet drop'),('Filter inlet drop','Filter inlet upper offset'),('Filter inlet upper offset','Longitudinal extract header'),('Longitudinal extract header','Raised intake bridge riser'),('Raised intake bridge riser','Rear intake crossheader'),('Rear intake crossheader','Raised intake bridge riser.001'),('Raised intake bridge riser.001','Longitudinal extract header.001'),('Connected filter plenum','Filter outlet bolted adapter'),('Filter outlet bolted adapter','Fan inlet collar'),('Fan inlet collar','Centrifugal volute'),('Centrifugal volute','Fan tangential outlet'),('Fan tangential outlet','Rising exhaust duct'),('Rising exhaust duct','Skid exhaust riser'),('Skid exhaust riser','Exhaust offset'),('Exhaust offset','Exhaust outlet'),('Exhaust outlet','Exterior extract collar')]
joints=[]
for a,b in pairs:
 d=gap(geometry[a],geometry[b]);joints.append({'a':a,'b':b,'gap_m':d,'pass':d<=.001})
intake=['Longitudinal extract header','Longitudinal extract header.001','Rear intake crossheader','Raised intake bridge riser','Raised intake bridge riser.001','Filter inlet drop','Filter inlet upper offset']
exhaust=['Skid exhaust riser','Exhaust offset','Exhaust outlet'];separations=[]
for a in intake:
 for b in exhaust:
  d=gap(geometry[a],geometry[b]);separations.append({'intake':a,'exhaust':b,'gap_m':d,'pass':d>=.009})
results.append({'id':'vent_process_joints','pass':all(j['pass'] for j in joints),'joints':joints,'method':'Evaluated geometric joint continuity; not airflow simulation.'})
results.append({'id':'intake_exhaust_separation','pass':all(j['pass'] for j in separations),'pairs':separations})
record={'revision':s.get('revision'),'pass':all(r['pass'] for r in results),'checks':results,'limitations':['Door poses are static geometric tests, not an implemented animation or engine physics.','Duct solids are exterior manufactured envelopes, not CFD volumes.']}
(dest/'motion_process.json').write_text(json.dumps(record,indent=2));print('MOTION_PROCESS',[(r['id'],r['pass']) for r in results])

