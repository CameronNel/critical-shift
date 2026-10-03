import bpy,json,hashlib,math,sys,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');P=ROOT/'revamp-review/production';OUT=Path('/tmp/medical16-repair-technical');expected='39007192eef36f87c5299933e3a2a4f3462791871144c349a580ba2d9d322487'
assert hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()==expected
verifier=ROOT/'verify_overhaul.py';code=verifier.read_text().replace("(P/'dependency-manifest.json')","(REPORT_DIR/'dependency-manifest.json')").replace("(P/('cold-verification.json' if '--cold' in sys.argv else 'objective-verification.json'))","(REPORT_DIR/('cold-verification.json' if '--cold' in sys.argv else 'objective-verification.json'))")
namespace={'__file__':str(verifier),'__name__':'__main__','REPORT_DIR':OUT};sys.argv+=['--cold','--dependencies'];exec(compile(code,str(verifier),'exec'),namespace)
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();registry=json.loads((P/'support-registry.json').read_text());g={};inventory={};parts={};normal={}
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@x.co for x in me.vertices];f=[tuple(x.vertices) for x in me.loop_triangles]
 if v and f:g[o.name]=(v,f,BVHTree.FromPolygons(v,f,all_triangles=True))
 inventory[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'dimensions':list(o.dimensions),'bounds':[[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]] if v else None,'vertices':len(v),'triangles':len(f),'matrix_world':[list(r) for r in o.matrix_world],'properties':{k:str(o[k]) for k in o.keys()}}
 if o.name.startswith('MED_R2 |') and any(t in o.name for t in ['Sterile stock shelf bearing','Organic continuity plaque standoff','Recovery foot chart holder','Top fascia captive bearing','Upper access panel bearing','Service latch fixed bearing','Pressure gauge captive spindle']):
  bm=bmesh.new();bm.from_mesh(me);pending=set(bm.faces);components=[]
  while pending:
   todo=[pending.pop()];island=set(todo)
   for face in todo:
    for e in face.edges:
     for neighbor in e.link_faces:
      if neighbor in pending:pending.remove(neighbor);island.add(neighbor);todo.append(neighbor)
   volume=0;ids=set()
   for face in island:
    vs=[x.vert.co for x in face.loops];volume+=sum(vs[0].dot(vs[i].cross(vs[i+1]))/6 for i in range(1,len(vs)-1));ids.update(x.vert.index for x in face.loops)
   component={'closed':all(len(e.link_faces)==2 for face in island for e in face.edges),'signed_volume_m3':volume,'vertex_ids':sorted(ids),'bounds':[[min(v[i][k] for i in ids) for k in range(3)],[max(v[i][k] for i in ids) for k in range(3)]]}
   components.append(component)
  normal[o.name]={'inconsistent_edges':sum(len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert for e in bm.edges),'components':components};bm.free()
 ev.to_mesh_clear()
def contact(a,b,ids=None):
 av,af,at=g[a];bv,bf,bt=g[b]
 if ids is not None:af=[t for t in af if all(i in ids for i in t)];at=BVHTree.FromPolygons(av,af,all_triangles=True)
 best=(math.inf,None,None)
 for vs,fs,tree,rev,allowed in [(av,af,bt,False,ids),(bv,bf,at,True,None)]:
  pts=[x for i,x in enumerate(vs) if allowed is None or i in allowed]
  pts.extend((vs[t[0]]+vs[t[1]]+vs[t[2]])/3 for t in fs)
  es={tuple(sorted((t[k],t[(k+1)%3]))) for t in fs for k in range(3)};pts.extend((vs[i]+vs[j])/2 for i,j in es)
  for p in pts:
   q,n,i,d=tree.find_nearest(p)
   if d is not None and d<best[0]:best=(d,list(q) if rev else list(p),list(p) if rev else list(q))
 return {'a':a,'b':b,'sampled_surface_distance_m':best[0],'point_a':best[1],'point_b':best[2],'triangle_intersections':len(at.overlap(bt))}
stock=[]
for i in range(12):
 case='Sealed supply case'+('' if i==0 else '.'+str(i).zfill(3));foot='MED_R2 | Sterile stock shelf bearing '+str(i);shelf='Supply cabinet shelf'+('' if i%3==0 else '.'+str(i%3).zfill(3));components=[]
 for comp in normal[foot]['components']:
  ids=set(comp['vertex_ids']);top=contact(foot,case,ids);bottom=contact(foot,shelf,ids)
  components.append({'normal':comp,'case_interface':top,'shelf_interface':bottom})
 stock.append({'case':case,'foot':foot,'proper_shelf':shelf,'two_closed_positive_feet':len(components)==2 and all(c['normal']['closed'] and c['normal']['signed_volume_m3']>0 for c in components),'components':components,'direct_case_shelf_gap_m':contact(case,shelf)['sampled_surface_distance_m']})
 print('STOCK',i,len(components),[(c['case_interface']['sampled_surface_distance_m'],c['shelf_interface']['sampled_surface_distance_m']) for c in components],flush=True)
(OUT/'stock-bearing-witnesses.json').write_text(json.dumps(stock,indent=2))
pairs=[]
def pair(a,b):
 if a in g and b in g:pairs.append(contact(a,b))
for a,b in [('MED_R2 | Organic continuity plaque standoff 4.2','Engraved backing ORGANIC CONTINUITY'),('MED_R2 | Organic continuity plaque standoff 5.05','Engraved backing ORGANIC CONTINUITY'),('MED_R2 | Organic continuity plaque standoff 4.2','Inner removable liner.001'),('MED_R2 | Organic continuity plaque standoff 5.05','Inner removable liner.001'),('Recovery release slip','MED_R2 | Recovery foot chart holder'),('Release slip','Recovery release slip'),('MED_R2 | Recovery foot chart holder','Recovery bed pan'),('Meter unit','Ivory instrument dial'),('Needle pivot','MED_R2 | Pressure gauge captive spindle'),('MED_R2 | Pressure gauge captive spindle','Ivory instrument dial'),('Meter needle','Needle pivot'),('Orange latch rail.001','MED_R2 | Service latch fixed bearing 1.52'),('Orange latch rail.001','MED_R2 | Service latch fixed bearing 1.99'),('MED_R2 | Service latch fixed bearing 1.52','Jamb folded cover.001'),('MED_R2 | Service latch fixed bearing 1.99','Jamb folded cover.001'),('Service jamb narrow edge scuff','Jamb folded cover'),('Service jamb narrow edge scuff.002','Jamb folded cover.001'),('Service jamb narrow edge scuff.003','Orange latch rail.001')]:pair(a,b)
for k,slot in [(1,7),(3,9),(5,11),(7,13)]:
 fast='Top removable fascia fixing.'+str(k).zfill(3);mount='MED_R2 | Top fascia captive bearing '+str(k);pair(fast,mount);pair(mount,'MED_R2 | OCRU stepped cast pressure beam');pair('Screwdriver slot.'+str(slot).zfill(3),fast)
for k,slot,host in [(1,15,'Serviceable inner access panel'),(7,21,'Serviceable inner access panel.001')]:
 fast='Access panel fastener.'+str(k).zfill(3);mount='MED_R2 | Upper access panel bearing '+str(k);pair(fast,mount);pair(mount,host);pair('Screwdriver slot.'+str(slot).zfill(3),fast)
# Fixed architecture roots for repaired supporting hosts; actual mechanisms only.
for a,b in [('Inner removable liner.001','Rear machine skin'),('Rear machine skin','Sealed chamber pan'),('Sealed chamber pan','Chassis longitudinal channel'),('Chassis longitudinal channel','Chamber formed foot'),('Recovery bed pan','Recovery longitudinal support'),('Recovery longitudinal support','Tubular recovery leg'),('Tubular recovery leg','Bed non-marking foot'),('Bed non-marking foot','Floor'),('MED_R2 | OCRU stepped cast pressure beam','Chamber top folded fascia'),('Chamber top folded fascia','Chamber structural upright'),('Chamber structural upright','Sealed chamber pan'),('Jamb folded cover.001','Chamber structural upright.001'),('Serviceable inner access panel','MED_R2 | Access panel captive bearing 0'),('Serviceable inner access panel.001','MED_R2 | Access panel captive bearing 4'),('MED_R2 | Access panel captive bearing 0','Inner service panel inset'),('MED_R2 | Access panel captive bearing 4','Inner service panel inset.001'),('Ivory instrument dial','Instrument cast bezel'),('Instrument cast bezel','Reserve removable door'),('Reserve removable door','Reserve service hinge'),('Reserve service hinge','Reserve folded side'),('Reserve folded cap','Battery plinth'),('Battery plinth','Floor'),('Supply cabinet shelf','Supply cabinet back'),('Supply cabinet shelf.001','Supply cabinet back'),('Supply cabinet shelf.002','Supply cabinet back'),('Supply cabinet back','Cabinet wall spacer'),('Cabinet wall spacer','East wall')]:pair(a,b)
# Recheck the prior significant stored-object bearing interfaces, not arbitrary neighbors.
for i in range(12):
 case='Cartridge steel body'+('' if i==0 else '.'+str(i).zfill(3));seal='Cartridge bottom seal'+('' if i==0 else '.'+str(i).zfill(3));shelf='Folded storage shelf'+('' if i//3==0 else '.'+str(i//3).zfill(3));pair(case,seal);pair(seal,shelf)
for i in range(3):pair('Sealed consumable carton'+('' if i==0 else '.'+str(i).zfill(3)),'Bench lower shelf')
for a,b in [('Reserve battery module','MED_R2 | Battery resilient bearing pad '),('Reserve battery module.001','MED_R2 | Battery resilient bearing pad .001'),('Inventory clipboard','Supply bench top'),('Folded cleaning cloth','Supply bench top'),('Folded work glove palm','Supply bench top'),('Folded work glove palm.001','Supply bench top'),('Sterile pack','Supply bench top'),('Sterile pack.001','Sterile pack'),('Service tool tray','Supply bench top'),('Seal tool grip','Service tool tray'),('Seal tool shaft','Seal tool grip'),('Seal tool grip.001','Service tool tray'),('Seal tool shaft.001','Seal tool grip.001'),('Folded recovery blanket','Recovery foam cushion'),('Recovery foam cushion','Recovery bed pan'),('Recovery pillow','Recovery foam cushion'),('Supply bench top','Bench rear apron'),('Bench rear apron','Supply bench leg.001'),('Supply bench leg.001','Floor'),('Bench lower shelf','Supply bench leg.001')]:pair(a,b)
(OUT/'interface-witnesses.json').write_text(json.dumps(pairs,indent=2));(OUT/'new-mount-normal-components.json').write_text(json.dumps(normal,indent=2));(OUT/'geometry-inventory.json').write_text(json.dumps(inventory,indent=2))
(OUT/'registry-snapshot.json').write_text(json.dumps(registry,indent=2))
print('REPAIR_PREFLIGHT_NATIVE_COMPLETE',len(pairs),flush=True);assert hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()==expected
