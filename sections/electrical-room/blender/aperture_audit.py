"""Fresh saved-file wall-penetration rays and level seam bounds; read only."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();checks=[]
for ident,name,centre,axis,offsets in [
 ('U01','Portal wall return',(-4.32,0,3.88),1,(.15,.10)),
 ('U02','Portal wall return.002',(-4.32,16.4,3.88),1,(.30,.20)),
 ('U03','Reserve east wall',(8.425,14,2.8),0,(.07,.07))]:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);inv=o.matrix_world.inverted();direction=Vector((0,0,0));direction[axis]=1;across=1-axis;samples=[]
 for a in [-offsets[0],0,offsets[0]]:
  for z in [-offsets[1],0,offsets[1]]:
   p=Vector(centre);p[axis]-=.6;p[across]+=a;p.z+=z
   blocked=ev.ray_cast(inv@p,inv.to_3x3()@direction,distance=1.2)[0]
   samples.append({'origin':list(p),'blocked_by_wall':blocked})
 p=Vector(centre);p[axis]-=.6;p[across]+=.7
 control=bool(ev.ray_cast(inv@p,inv.to_3x3()@direction,distance=1.2)[0])
 checks.append({'id':ident,'wall':name,'samples':samples,'adjacent_solid_control':control,'pass':control and not any(q['blocked_by_wall'] for q in samples)})
for name,expected in [('Entry seam slab',[-.25,0]),('Waste seam slab',[16.4,16.97])]:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();vv=[o.matrix_world@v.co for v in me.vertices]
 span=[min(v.y for v in vv),max(v.y for v in vv)];z=max(v.z for v in vv);ev.to_mesh_clear()
 checks.append({'id':name,'y_bounds':span,'top_z':z,'expected_y':expected,'pass':max(abs(span[i]-expected[i]) for i in [0,1])<.00001 and abs(z)<.00001})
o=bpy.data.objects['Turbine mating adapter'];vv=[o.matrix_world@v.co for v in o.data.vertices];face=[v for v in vv if abs(v.y+.25)<.00001]
dims=[max(v.x for v in face)-min(v.x for v in face),max(v.z for v in face)-min(v.z for v in face)]
checks.append({'id':'U01 physical mating face','centre':[-4.32,-.25,3.88],'measured_cross_section':dims,'pass':abs(dims[0]-.4)<.00001 and abs(dims[1]-.3)<.00001})
r={'revision':s.get('revision'),'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'pass':all(c['pass'] for c in checks),'limits':'Local actual service apertures and floor seams; reciprocal transforms are proposed, neighboring geometry remains unchanged.'}
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2),encoding='utf-8');print('APERTURES',r['pass'])
if not r['pass']:raise RuntimeError('Saved aperture or seam failed')
