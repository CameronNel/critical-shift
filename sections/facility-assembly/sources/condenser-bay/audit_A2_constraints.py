"""Measured source-boundary report; inherited roof exception stays explicit.
Run inside Blender against the saved A2 source. Never edits or saves the scene.
"""
import hashlib,json,os,sys
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from condenser_finish_A2 import fixture_mesh_bounds
receipt=json.loads((HERE/'finish-A2-build.json').read_text());sc=bpy.context.scene
names=['D01 stub end wall','Ceiling slab','CEP-B motor feed','CEP-B motor feed end cap','WestWall','West dado','North dado']
assert all(n in sc.objects for n in names);assert sc.objects['CEP-B motor feed'].type=='CURVE'
assert any(o.name.startswith('D01 local blanking') for o in sc.objects)
assert any(o.name.startswith('D01 blanking') for o in sc.objects)
assert any(o.name.startswith('gallery inspection light') for o in sc.objects)
assert 'MODULE_condenser-bay' in bpy.data.collections
assert receipt['changed_nonlight_matrices']==[]
assert hashlib.sha256((HERE/'module.blend').read_bytes()).hexdigest()==receipt['source_sha256']
dg=bpy.context.evaluated_depsgraph_get();foot=[];upper=[];fixtures=[];total=0
for o in sc.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();total+=sum(len(p.vertices)-2 for p in m.polygons)
 pts=[ev.matrix_world@v.co for v in m.vertices];ev.to_mesh_clear()
 if not pts or o.hide_render:continue
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if o.name.startswith(('gallery inspection fixture','gallery inspection lens')):fixtures.append({'object':o.name,'evaluated_bounds':[lo,hi]})
 stub=o.name.startswith(('D01 stub','D01 local blanking','D01 blanking'))
 if lo[0]<-2.0801 or hi[0]>9.8801 or hi[1]>9.5401 or (lo[1]<-.1401 and not stub):foot.append({'object':o.name,'bounds':[lo,hi]})
 if hi[2]>5.6001:upper.append({'object':o.name,'bounds':[lo,hi],'classification':'inherited R34 structure / roof mating; NOT a universal height-cap pass'})
lights=[{'name':o.name,'z':o.location.z} for o in sc.objects if o.type=='LIGHT' and o.location.z>5.55]
assert not foot,foot;assert not lights,lights;assert total<=400000,total
metadata_checks=[]
for fixture in fixtures:
 assert fixture['evaluated_bounds'][1][2]<=5.6001,fixture
 if fixture['object'].startswith('gallery inspection fixture'):
  queried=fixture_mesh_bounds(sc.objects[fixture['object']])
  delta=max(abs(queried[i][j]-fixture['evaluated_bounds'][i][j]) for i in range(2) for j in range(3))
  assert delta<.00001,(fixture,queried,delta)
  metadata_checks.append({'object':fixture['object'],'direct_mesh_bounds':queried,'maximum_delta_from_evaluated_metres':delta})
report={'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'status':'PASS_SCOPED_SOURCE_CHECKS; INHERITED_STRUCTURE_HEIGHT_EXCEPTION','triangles':total,'footprint_violations':foot,'light_cap_violations':lights,'patched_objects_present':names,'changed_nonlight_matrices':receipt['changed_nonlight_matrices'],'packed_images':[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images],'height_cap_exceptions':upper,'height_exception_count':len(upper),'saved_fixture_measurements':fixtures,'process_id':os.getpid(),'interpretation':'Preserve R34 roof/U04 mating and gallery layout. Cap lights/new finish fixtures, retain inherited structural upper extents. Source gallery audit passes; assembled 2m gallery headroom is NOT certified. Optional owner clarification remains unanswered.','optional_reach_work':'A1 reach-check overhead valves/isolate hook not altered; no engine interaction certification.'}
report['fixture_metadata_query_checks']=metadata_checks
report['current_metadata_query_builder_sha256']=hashlib.sha256((HERE/'condenser_finish_A2.py').read_bytes()).hexdigest()
report['audit_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(HERE/'evidence-A2/source-constraints.json').write_text(json.dumps(report,indent=2)+'\n')
print('A2_CONSTRAINTS',total,'triangles',len(upper),'inherited height exceptions',flush=True)
