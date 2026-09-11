"""Read-only evaluated glyph/backing fit and front obstruction sampling."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();geo={};rows=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices]
 if v:geo[o.name]={'vertices':v,'bvh':BVHTree.FromPolygons(v,[tuple(p.vertices) for p in m.polygons]),'object':o}
 e.to_mesh_clear()
for o in s.objects:
 if o.type!='FONT' or not (o.name.startswith('Engraved ') or o.get('backing_object')):continue
 candidates=[s.objects[o['backing_object']]] if o.get('backing_object') else [b for b in s.objects if b.name.startswith('Engraved backing '+o.data.body) and b.parent==o.parent]
 if not candidates:continue
 b=min(candidates,key=lambda b:(b.matrix_world.translation-o.matrix_world.translation).length);g=geo[o.name];invrot=b.matrix_world.to_quaternion().inverted();local=[invrot@(v-b.matrix_world.translation) for v in g['vertices']];half=b.dimensions*.5
 fit=all(-half.x+.002<=v.x<=half.x-.002 and -half.z+.001<=v.z<=half.z-.001 for v in local)
 normal=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized();blocks=set()
 for v in g['vertices'][::max(1,len(g['vertices'])//80)]:
  for n,gg in geo.items():
   if gg['object'].type=='FONT' or n==b.name:continue
   if gg['bvh'].ray_cast(v+normal*.001,normal,.06)[0] is not None:blocks.add(n)
 rows.append({'text':o.data.body,'object':o.name,'backing':b.name,'size_m':o.data.size,'fits':fit,'front_obstructions':sorted(blocks),'glyph_bounds_in_backing':[[min(v[i] for v in local) for i in range(3)],[max(v[i] for v in local) for i in range(3)]],'backing_dimensions':list(b.dimensions)})
report={'pass':all(r['fits'] and not r['front_obstructions'] for r in rows),'labels':rows,'limitations':['Checks plaque glyph fit and local front obstruction; player-view legibility still requires actual oblique renders.','Other screen/floor text is checked visually and separately in scene review.']};dest=R/'production/validation'/s.get('revision','unknown');dest.mkdir(parents=True,exist_ok=True);(dest/'signs.json').write_text(json.dumps(report,indent=2));print('SIGNS',report['pass'],[r for r in rows if not r['fits'] or r['front_obstructions']])
