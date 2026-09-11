"""Read-only evaluated saved-scene measurements; conservative physical envelopes, not engine simulation."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();checks=[];geometry={}
def check(name,ok,data):checks.append({'id':name,'pass':bool(ok),'evidence':data})
def descendants(o):
 return [o]+[c for child in o.children for c in descendants(child)]
for o in s.objects:
 if o.type not in {'MESH','FONT','CURVE'}:continue
 e=o.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices]
 if not vv:e.to_mesh_clear();continue
 lo=Vector([min(v[a] for v in vv) for a in range(3)]);hi=Vector([max(v[a] for v in vv) for a in range(3)])
 geometry[o.name]={'lo':lo,'hi':hi,'bvh':BVHTree.FromPolygons(vv,[tuple(p.vertices) for p in m.polygons]),'object':o,'vertices':len(vv),'polygons':len(m.polygons),'digest':hashlib.sha256(json.dumps([[round(v,6) for v in co] for co in vv]).encode()).hexdigest(),'parts':[(tuple(min(vv[k][a] for k in p.vertices) for a in range(3)),tuple(max(vv[k][a] for k in p.vertices) for a in range(3))) for p in m.polygons] if o.type=='CURVE' else None};e.to_mesh_clear()
check('finite_geometry',all(all(math.isfinite(x) for x in list(g['lo'])+list(g['hi'])) for g in geometry.values()),len(geometry))
check('assigned_materials',all(g['object'].data.materials and all(g['object'].data.materials) for g in geometry.values()),len(bpy.data.materials))
expected={'ocru':1,'adult_berth':1,'body_cart':1,'restart_console':1,'cartridge_bank':1,'reserve_power':1,'recovery_berth':1,'supply_bench':1,'supplies':1,'decontamination':1,'handwash':1}
counts=dict(Counter(o.get('equipment_type') for o in s.objects if o.get('equipment_type')));check('required_equipment',counts==expected,counts)
check('main_floor',all(abs(v-t)<.001 for v,t in zip(list(geometry['Floor']['lo'])+list(geometry['Floor']['hi']),[-4.18,-.18,-.24,4.18,9.18,0])),[list(geometry['Floor']['lo']),list(geometry['Floor']['hi'])])
cams=[o for o in s.objects if o.type=='CAMERA'];check('player_height_cameras',len(cams)==14 and all(abs(o.location.z-1.68)<.001 for o in cams),[{'name':o.name,'location':list(o.location),'lens':o.data.lens} for o in cams])
roots=[]
for o in s.objects:
 if not o.get('support_target'):continue
 target=geometry.get(o['support_target']);row={'root':o.name,'target':o['support_target'],'anchors':[]}
 for a in json.loads(o.get('support_anchors','[[0,0,0]]')):
  p=o.matrix_world@Vector(a);d=(o.matrix_world.to_3x3()@Vector(json.loads(o.get('support_direction','[0,0,-1]')))).normalized();hit=target['bvh'].ray_cast(p-d*.05,d,.1) if target else (None,)*4;gap=(hit[0]-p).dot(d) if hit[0] is not None else None
  row['anchors'].append({'position':list(p),'gap':gap,'pass':gap is not None and -.00201<=gap<=.00501})
 roots.append(row)
check('registered_root_support',bool(roots) and all(a['pass'] for r in roots for a in r['anchors']),roots)
def hits_box(x,y,hx=.30,hy=.30,z0=.025,z1=1.85,ignore=()):
 lo=(x-hx,y-hy,z0);hi=(x+hx,y+hy,z1)
 return [n for n,g in geometry.items() if n not in ignore and all(hi[a]>g['lo'][a]+.0001 and lo[a]<g['hi'][a]-.0001 for a in range(3)) and (g['parts'] is None or any(all(hi[a]>pa[a]-.0001 and lo[a]<pb[a]+.0001 for a in range(3)) for pa,pb in g['parts']))]
paths={'entry_to_console':[(0,-.6),(0,6.9),(-.45,7.65)],'ocru_load':[(0,4.63),(-.82,4.63)],'cartridge_receiver':[(0,3),(-.85,3)],'suit_service':[(0,6.23),(-.85,6.23)],'reserve_maintenance':[(0,7.25),(-2.15,7.65)],'recovery':[(0,3.2),(1.95,3.2),(1.95,4.7)],'supplies':[(0,6.8),(2.5,6.8),(2.5,7.47)],'supply_bench':[(0,1.5),(2.45,1.5)],'handwash':[(0,2.95),(2.8,2.95)],'decon_walk':[(0,7.25),(2.15,7.25),(2.15,10.25)],'cart_parking_access':[(0,1.33),(-2.2,1.33)]}
routes=[]
for name,points in paths.items():
 bad=[];num=0
 for a,b in zip(points,points[1:]):
  a=Vector(a);b=Vector(b);steps=max(1,math.ceil((b-a).length/.10))
  for j in range(steps+1):
   p=a.lerp(b,j/steps);num+=1;hits=hits_box(p.x,p.y)
   if hits:bad.append({'point':list(p),'hits':hits})
 routes.append({'route':name,'points':points,'samples':num,'obstructions':bad})
check('player_routes',all(not r['obstructions'] for r in routes),routes)
cart_ignore=[o.name for o in descendants(s.objects['BODY_CART'])];cart_routes=[]
for name,points in {'arrival_to_ocru':[(0,-1.3),(0,4.63),(-.75,4.63)],'parking_extract':[(-3.12,1.33),(0,1.33)],'parking_extract_75mm_tolerance':[(-3.12,1.33),(0,1.33)],'decon_apron':[(0,4.63),(0,6.95),(2.15,6.95)],'recovery_transfer':[(0,4.63),(2.2,4.63)]}.items():
 bad=[]
 for a,b in zip(points,points[1:]):
  a=Vector(a);b=Vector(b);steps=max(1,math.ceil((b-a).length/.10))
  for j in range(steps+1):
   p=a.lerp(b,j/steps);pad=.075 if name=='parking_extract_75mm_tolerance' else 0;hits=hits_box(p.x,p.y,.37+pad,1.062+pad,.025,1.5,cart_ignore)
   if hits:bad.append({'point':list(p),'hits':hits})
 cart_routes.append({'route':name,'points':points,'cart_width':.74,'cart_length':2.124,'padding_each_side_m':pad,'obstructions':bad})
check('cart_routes',all(not r['obstructions'] for r in cart_routes),cart_routes)
portal_rows=[]
for id,center,w,h in [('main_entry',(0,0,0),2.2,2.5),('decon',(2.15,9.0,0),1.2,2.15)]:
 bad=[]
 for u in [-w/2+.025,0,w/2-.025]:
  for z in [.025,1,h-.025]:
   p=Vector((center[0]+u,center[1]-.20,z));d=Vector((0,1,0));hits=[n for n,g in geometry.items() if g['bvh'].ray_cast(p,d,.4)[0] is not None]
   if hits:bad.append({'u':u,'z':z,'hits':hits})
 portal_rows.append({'id':id,'width':w,'height':h,'obstructions':bad})
check('clear_openings',all(not r['obstructions'] for r in portal_rows),portal_rows)
contract=json.loads((R/'interface.json').read_text());markers=[]
for item in contract['portals']+contract['utilities']:
 ob=s.objects.get('IF_'+item['id']);p=item.get('center',item.get('threshold'));normal=item.get('outward',item.get('outward_normal'));markers.append({'id':item['id'],'pass':ob is not None and (ob.location-Vector(p)).length<.0001 and json.loads(ob.get('outward_normal','[]'))==normal})
check('exact_connection_markers',all(m['pass'] for m in markers),markers)
hooks=[]
for h in contract['host_hooks']:
 ob=s.objects.get('HOOK_'+h['id']);hooks.append({'id':h['id'],'position':list(ob.location) if ob else None,'target':ob.get('target_id') if ob else None,'pass':ob is not None and (ob.get('target_id') in s.objects or ob.get('target_id')=='medical-reanimation')})
check('host_hook_anchors',all(h['pass'] for h in hooks),hooks)
source=json.loads(s.get('authoring_sources','{}'));match={n:(R/'blender'/n).exists() and hashlib.sha256((R/'blender'/n).read_bytes()).hexdigest()==h for n,h in source.items()};check('saved_source_bytes',bool(match) and all(match.values()),match)
check('external_dependencies',not bpy.data.libraries and all(im.packed_file or im.source=='GENERATED' or im.name in ['Render Result','Viewer Node'] for im in bpy.data.images),{'libraries':len(bpy.data.libraries),'images':[im.name for im in bpy.data.images],'fonts':[f.filepath for f in bpy.data.fonts]})
envelopes={}
for ob in s.objects:
 if not ob.get('equipment_type'):continue
 gg=[geometry[o.name] for o in descendants(ob) if o.name in geometry]
 if gg:envelopes[ob.name]={'min':[min(g['lo'][i] for g in gg) for i in range(3)],'max':[max(g['hi'][i] for g in gg) for i in range(3)]}
report={'revision':s.get('revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'pass':all(c['pass'] for c in checks),'checks':checks,'equipment_envelopes':envelopes,'geometry_fingerprint':{n:g['digest'] for n,g in geometry.items()},'limitations':['Conservative evaluated AABB route sweeps, not runtime collision or ragdoll physics.','Assembly anchors do not alone certify every internal part.','Visual approval is separate. Neighbor placement and runtime state logic remain unbound.']}
dest=R/'production/validation'/s.get('revision','unknown');dest.mkdir(parents=True,exist_ok=True);(dest/'technical.json').write_text(json.dumps(report,indent=2));print('AUDIT',report['pass'],[(c['id'],c['pass']) for c in checks])
