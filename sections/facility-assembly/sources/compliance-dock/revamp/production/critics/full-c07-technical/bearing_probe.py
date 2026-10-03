import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');O=R/'revamp/production/critics/full-c07-technical';S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;D=bpy.context.evaluated_depsgraph_get();T={};P={}
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(D);m=ev.to_mesh();m.calc_loop_triangles();ps=[o.matrix_world@v.co for v in m.vertices];T[o.name]=BVHTree.FromPolygons(ps,[list(t.vertices) for t in m.loop_triangles],all_triangles=True);P[o.name]=ps;ev.to_mesh_clear()
rows=[]
def hit(name,origin,direction,distance):
 h=T[name].ray_cast(Vector(origin),Vector(direction),distance);return {'object':name,'point':[float(x) for x in h[0]] if h[0] else None,'normal':[float(x) for x in h[1]] if h[1] else None,'triangle':h[2],'distance_m':h[3]}
for side in [-1,1]:
 for x in [.66,.76,.81]:
  xx=side*x;z=2.65+.03*max(0,min(1,(x-.72)/.13));a=hit('Scanner portal column '+str(side),(xx,7,z+.05),(0,0,-1),.1);b=hit('Scanner portal lintel',(xx,7,z-.05),(0,0,1),.1);rows.append({'interface':'scanner actual crown and bridge','x':xx,'a':a,'b':b,'gap_m':b['point'][2]-a['point'][2] if a['point'] and b['point'] else None})
for name in [n for n in T if n.startswith('Tunnel stiffener ')]:
 pts=P[name];center=sum(pts,Vector())/len(pts);side=1 if center.x>4.65 else -1
 for z in [1.2,1.8,1.96,2.015,2.045]:
  a=hit('Lead tunnel main body',(4.65+side*1.05,center.y,z),(-side,0,0),.75);b=hit(name,(4.65+side*.58,center.y,z),(side,0,0),.55);rows.append({'interface':'cargo rib inward face and shield outer face','z':z,'a':a,'b':b,'gap_m':side*(b['point'][0]-a['point'][0]) if a['point'] and b['point'] else None})
# Registered bearing anchors: independently require an actual component seat and target at same spatial point.
val=json.loads((O/'existing-validator.json').read_text());seats=[]
for row in val['support_table']:
 p=Vector(row['anchor_world']);name=row['nearest_component'];h=T[name].find_nearest(p); seats.append({'assembly':row['assembly'],'anchor':row['anchor'],'actual_component':name,'point':list(p),'component_distance_m':h[3],'component_triangle':h[2],'target':row['target'],'target_gap_m':row.get('signed_gap_m'),'note':'Validator target ray plus independently recomputed nearest evaluated assembly geometry; not a proof of all internal loads'})
(O/'actual-bearing-surfaces.json').write_text(json.dumps({'manufactured_interfaces':rows,'registered_bearing_seats':seats,'fixing_island_contact_evidence':'island-surface-contacts.json reports every fixing-sized disconnected closed component; refined-contact-candidates.json resolves all sparse sample ambiguities with actual triangle intersections. Individual fixing torques/strength are outside authoring scope.'},indent=2));print('DONE',len(rows),len(seats),flush=True)
