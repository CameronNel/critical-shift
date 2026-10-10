"""Finite regression: inherited roof tube profiles and roof-structure intersections.
The old saved C59 loops fail this check. Intentional clamps/tees are excluded;
registered supports and sampled crane poses are checked by their separate audits.
"""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
import rh_roof_utilities as U
args=sys.argv[sys.argv.index('--')+1:];source,output=map(Path,args[:2])
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
hostnames=('RH walls girders STEEL','RF BATCH structure RF edge','RF BATCH structure RF gunmetal','RF BATCH services RF white','RF BATCH skylights RF white','RF BATCH skylights RF edge')
def tree(o,ids=None):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons if ids is None or all(v in ids for v in f.vertices)])
hosts=[(n,tree(bpy.data.objects[n])) for n in hostnames if n in bpy.data.objects]
rows=[];failures=[]
for name in ('RF BATCH services RF dark','RF BATCH services RF orange'):
 o=bpy.data.objects[name]
 for ids in U.components(o.data):
  lo,hi=U.world_bounds(o,ids)
  if hi[0]-lo[0]<16 or hi[1]-lo[1]<16 or lo[2]<16.3 or hi[2]>17.3:continue
  bvh=tree(o,ids);overlaps={n:len(bvh.overlap(h)) for n,h in hosts}
  row=dict(object=name,vertices=len(ids),bounds=[lo,hi],vertical_diameter=hi[2]-lo[2],overlaps=overlaps)
  rows.append(row)
  if len(ids)<2048 or abs(hi[2]-lo[2]-.042)>.00005:failures.append('Low-resolution or incorrect 42mm loop: '+name)
  if any(overlaps.values()):failures.append('Loop intersects roof structure: '+name)
if len(rows)!=3:failures.append('Expected exactly three small utility loops')
trunk=bpy.data.objects.get('RH refine roof utility main ROOF_MAIN');main=None
if trunk:
 lo,hi=U.world_bounds(trunk,range(len(trunk.data.vertices)));overlaps={n:len(tree(trunk).overlap(h)) for n,h in hosts}
 main=dict(bounds=[lo,hi],outer_diameter=hi[2]-lo[2],overlaps=overlaps)
 if abs(main['outer_diameter']-.1)>.00005:failures.append('Main trunk is not 100mm OD')
 if any(overlaps.values()):failures.append('Main trunk intersects roof structure')
 for suffix in ('reducer','branch'):
  o=bpy.data.objects.get('RH refine roof utility main '+suffix+' ROOF_MAIN')
  if not o:failures.append('Missing actual '+suffix);continue
  overlap={n:len(tree(o).overlap(h)) for n,h in hosts}
  if any(overlap.values()):failures.append(suffix+' intersects roof structure: '+str(overlap))
else:failures.append('Missing 100mm trunk')
glyph_clearance=[]
from mathutils import Vector
from r2lib import WALLS
for name,panel in [('R2 gfx CRITICAL SHIFT ENERGY SYSTEMS','RH refine legacy hall identity panel PANEL'),('R2 gfx 02','RH refine legacy numeral 02 panel PANEL'),('R2 gfx 05','RH refine legacy numeral 05 panel PANEL')]:
 o=bpy.data.objects.get(name);plate=bpy.data.objects.get(panel)
 if not o or not plate:failures.append('Missing raised glyph/panel '+name);continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];c=sum(pts,Vector())/len(pts)
 choices=[w for w in WALLS if -.1<=(Vector((c.x,c.y))-w.P).dot(w.t)<=w.L+.1]
 w=min(choices,key=lambda w:abs((Vector((c.x,c.y))-w.P).dot(w.n)));n=Vector((w.n.x,w.n.y,0))
 gap=min(p.dot(n) for p in pts)-max((plate.matrix_world@v.co).dot(n) for v in plate.data.vertices)
 glyph_clearance.append(dict(glyph=name,panel=panel,normal=list(n),min_plane_gap=gap))
 if not .0005<=gap<=.005:failures.append('Glyph/panel lacks positive bounded separation: '+name)
report=dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pass_check=not failures,failures=failures,small_loops=rows,trunk=main,glyph_clearance=glyph_clearance,roof_obstacles=[n for n,h in hosts],scope='Actual mesh connected loop profiles positive legacy-glyph/backing separation, and BVH triangle intersections against named structural/service roof obstacles; no global collision or fluid-network claim. Supports and sampled moving machinery require separate support/motion audits.')
output.write_text(json.dumps(report,indent=2)+'\n');print('ROOF_UTILITY', 'PASS 0' if not failures else 'FAIL '+str(len(failures)),flush=True)
if failures:raise SystemExit(1)
