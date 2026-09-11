"""Read-only evaluated artifact audit. Never builds or saves the scene."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
checks=[];geometry={};warnings=[]
def check(id,ok,data):checks.append({'id':id,'pass':bool(ok),'evidence':data})
for o in s.objects:
 if o.type not in {'MESH','FONT','CURVE'}:continue
 e=o.evaluated_get(dg);m=e.to_mesh();vv=[e.matrix_world@v.co for v in m.vertices]
 if not vv:e.to_mesh_clear();continue
 lo=Vector([min(v[a] for v in vv) for a in range(3)]);hi=Vector([max(v[a] for v in vv) for a in range(3)])
 b=BVHTree.FromPolygons(vv,[tuple(p.vertices) for p in m.polygons])
 geometry[o.name]={'lo':lo,'hi':hi,'bvh':b,'object':o,'vertices':len(vv),'polygons':len(m.polygons)}
 e.to_mesh_clear()
check('material_assignments',all(len(g['object'].data.materials)>0 and all(m is not None for m in g['object'].data.materials) for g in geometry.values()),[n for n,g in geometry.items() if not g['object'].data.materials or any(m is None for m in g['object'].data.materials)])
check('finite_geometry',all(all(math.isfinite(x) for x in list(g['lo'])+list(g['hi'])) for g in geometry.values()),len(geometry))
counts=Counter(o.get('equipment_type') for o in s.objects if o.get('equipment_type'))
expected={'shielded_cask':2,'residue_overpack':3,'dry_container':2,'quarantine_container':1,'cart':1,'handling_jib':1,'ventilation':1,'inventory':1,'repair_bench':1}
check('equipment_inventory',dict(counts)==expected,dict(counts))
floor=geometry['Floor'];check('floor_footprint',all(abs(float(v)-t)<.001 for v,t in zip(list(floor['lo'])+list(floor['hi']),[-6.32,-.32,-.30,6.32,18.32,0])),[list(floor['lo']),list(floor['hi'])])
cams=[o for o in s.objects if o.type=='CAMERA'];check('fixed_cameras',len(cams)==20 and all(abs(o.location.z-1.68)<.001 for o in cams),[{'name':o.name,'location':list(o.location),'lens':o.data.lens} for o in cams])
roots=[]
for o in s.objects:
 if not o.get('support_target'):continue
 target=geometry.get(o['support_target']);row={'root':o.name,'target':o['support_target'],'anchors':[]}
 for a in json.loads(o.get('support_anchors','[[0,0,0]]')):
  p=o.matrix_world@Vector(a);d=(o.matrix_world.to_3x3()@Vector(json.loads(o.get('support_direction','[0,0,-1]')))).normalized()
  hit=target['bvh'].ray_cast(p-d*.05,d,.1) if target else (None,None,None,None)
  gap=(hit[0]-p).dot(d) if hit[0] is not None else None
  row['anchors'].append({'position':list(p),'gap':gap,'pass':gap is not None and -.00201<=gap<=.00501})
 roots.append(row)
check('registered_root_support',all(a['pass'] for r in roots for a in r['anchors']),roots)
def overlap(lo,hi,g):return all(hi[a]>g['lo'][a]+.0001 and lo[a]<g['hi'][a]-.0001 for a in range(3))
# Sweeps use conservative evaluated AABB rejection, never claim engine navigation.
paths={'main':[(0,-.2),(0,18.2)],'personnel':[(0,2.4),(6.25,2.4)],'inventory':[(0,2.3),(-2.6,2.3),(-3.2,2.3)],'residue':[(0,6.6),(-3.55,6.6)],'shielded':[(0,11),(-3,11)],'dry':[(0,6.8),(2.8,6.8)],'quarantine':[(0,11),(3.15,11)],'ventilation':[(0,16),(-2.45,16),(-2.45,14.8),(-4.4,14.8)],'bench':[(0,16),(3.3,16)]}
sweeps=[]
for name,points in paths.items():
 bad=[];n=0
 for a,b in zip(points,points[1:]):
  a=Vector(a);b=Vector(b);steps=max(1,math.ceil((b-a).length/.10))
  for j in range(steps+1):
   p=a.lerp(b,j/steps);n+=1;lo=Vector((p.x-.30,p.y-.30,.025));hi=Vector((p.x+.30,p.y+.30,1.85))
   hits=[k for k,g in geometry.items() if overlap(lo,hi,g)]
   if hits:bad.append({'point':list(p),'hits':hits})
 sweeps.append({'route':name,'samples':n,'obstructions':bad})
check('player_routes',all(not r['obstructions'] for r in sweeps),sweeps)
# Transit cart straight sweep and reserved complete turn circle bounding squares.
cart=[]
for y in [j*.1 for j in range(181)]:
 lo=Vector((-.50,y-.90,.025));hi=Vector((.50,y+.90,1.80));hits=[k for k,g in geometry.items() if overlap(lo,hi,g)]
 if hits:cart.append({'y':y,'hits':hits})
check('cart_straight_route',not cart,cart)
turns=[]
for x,y,r in [(0,2.5,1.03),(0,16,1.03)]:
 lo=Vector((x-r,y-r,.025));hi=Vector((x+r,y+r,1.8));hits=[k for k,g in geometry.items() if overlap(lo,hi,g)];turns.append({'center':[x,y],'conservative_rotating_cart_square_halfwidth':r,'hits':hits})
check('cart_rotation_envelope',all(not r['hits'] for r in turns),turns)
# Geometry aperture ray samples traverse owned wall thickness only.
portals=[]
for id,axis,center,w,h in [('WS_RECEIVING',1,(0,-.16,0),3,3.2),('WS_DISPATCH',1,(0,18.16,0),2.4,2.8),('WS_PERSONNEL',0,(6.16,2.4,0),1.2,2.3)]:
 bad=[]
 for u in [-w/2+.025,0,w/2-.025]:
  for z in [.025,1.0,h-.025]:
   p=Vector(center);p[1-axis]+=u;p.z=z;p[axis]-=.25;d=Vector((1,0,0) if axis==0 else (0,1,0))
   hits=[n for n,g in geometry.items() if g['bvh'].ray_cast(p,d,.5)[0] is not None]
   if hits:bad.append({'u':u,'z':z,'hits':hits})
 portals.append({'id':id,'obstructions':bad})
check('portal_openings',all(not p['obstructions'] for p in portals),portals)
contract=json.loads((R/'interface.json').read_text());markers=[]
for item in contract['portals']+contract['utility_interfaces']:
 ob=s.objects.get('IF_'+item['id']);markers.append({'id':item['id'],'pass':ob is not None and (ob.location-Vector(item['center'])).length<.0001})
check('connection_markers',all(m['pass'] for m in markers),markers)
source=json.loads(s.get('authoring_sources','{}'));match={n:hashlib.sha256((R/'blender'/n).read_bytes()).hexdigest()==h for n,h in source.items() if (R/'blender'/n).exists()}
check('saved_source_bytes',bool(match) and all(match.values()),match)
check('external_dependencies',not bpy.data.libraries and all(im.packed_file or im.source=='GENERATED' or im.name in ['Render Result','Viewer Node'] for im in bpy.data.images),{'libraries':len(bpy.data.libraries),'images':[im.name for im in bpy.data.images],'fonts':[{'name':f.name,'path':f.filepath} for f in bpy.data.fonts]})
report={'revision':s.get('revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'pass':all(c['pass'] for c in checks),'checks':checks,'limitations':['Conservative evaluated bounds sweeps, not dynamic navigation or carried-body simulation.','Root anchors prove assembly floor/ceiling contact; internal connection graph and individual dressing contacts require separate audit.','No engineering certification or whole-map integration asserted.']}
dest=R/'production/validation'/s.get('revision','unknown');dest.mkdir(parents=True,exist_ok=True);(dest/'technical.json').write_text(json.dumps(report,indent=2))
print('AUDIT',report['pass'],[(c['id'],c['pass']) for c in checks])


