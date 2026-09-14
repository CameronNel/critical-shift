"""A12 terrain closure and map containment; preserves room geometry and route layout."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/completion';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A11_map_finish.blend'),load_ui=False)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
L=json.loads((R/'production/LAYOUT_A08.json').read_text())
col=bpy.data.collections.new('19_MAP_COMPLETION');scene.collection.children.link(col)
materials=[bpy.data.materials['Map ground warm concrete'],bpy.data.materials['EXT charcoal coated steel']]
verts=[];faces=[];mids=[]
def box(c,s,mi=0):
 x,y,z=c;dx,dy,dz=[a/2 for a in s];off=len(verts)
 verts.extend([(x+a*dx,y+b*dy,z+c*dz) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
 for f in [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]:faces.append(tuple(off+i for i in f));mids.append(mi)
def hit(x,y,z=55,depth=64):
 return scene.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)),distance=depth)
def route_near(x,y,pad=.5):
 p=Vector((x,y))
 for r in L['routes']:
  for aa,bb in zip(r['points'],r['points'][1:]):
   a,b=Vector(aa).xy,Vector(bb).xy;v=b-a
   if v.length_squared<.0001:continue
   t=max(0,min(1,(p-a).dot(v)/v.length_squared))
   if (p-a-v*t).length<r['width_m']/2+pad:return True
 return False
holes=[(-101,-10.49,-58,0),(-4.51,28.7,32,59.5),(40.54,66.3,36.25,51.02),(45.74,57.98,35.02,47)]
filled=[];edge_candidates=[]
for rect in holes:
 a,b,c,d=rect;nx=math.ceil((b-a)/.5);ny=math.ceil((d-c)/.5);dx=(b-a)/nx;dy=(d-c)/ny;cells=set()
 for i in range(nx):
  for j in range(ny):
   x=a+(i+.5)*dx;y=c+(j+.5)*dy
   # Preserve every existing source surface, roof and below-grade footprint.
   if hit(x,y)[0]:continue
   if any(hit(x+sx*dx*.49,y+sy*dy*.49)[0] for sx,sy in [(-1,-1),(-1,1),(1,-1),(1,1)]):continue
   box((x,y,-.19),(dx,dy,.25));cells.add((i,j));filled.append((x,y))
 for i,j in cells:
  x=a+(i+.5)*dx;y=c+(j+.5)*dy
  for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]:
   if (i+di,j+dj) not in cells:edge_candidates.append((x+di*dx/2,y+dj*dy/2,dy if di else dx,bool(di)))
 # Original rectangle boundaries also need containment wherever they still border a drop.
 for axis,lo,hi,fixed in [('x',a,b,c),('x',a,b,d),('y',c,d,a),('y',c,d,b)]:
  n=math.ceil((hi-lo)/.5)
  for i in range(n):
   t=lo+(i+.5)*(hi-lo)/n;x,y=(t,fixed) if axis=='x' else (fixed,t)
   edge_candidates.append((x,y,(hi-lo)/n,axis=='y'))
# Mesh infill first, then evaluate the remaining open edges.
def mesh_object(name):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 for m in materials:me.materials.append(m)
 for p,mi in zip(me.polygons,mids):p.material_index=mi
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob
infill=mesh_object('A12 fitted terrain infill');verts=[];faces=[];mids=[]
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();guards=0
for x,y,length,along_y in edge_candidates:
 if route_near(x,y):continue
 # A guard is only necessary when one side is ground and the other is a drop.
 ax,ay=(.22,0) if along_y else (0,.22)
 f1=hit(x+ax,y+ay,.2,.5)[0];f2=hit(x-ax,y-ay,.2,.5)[0]
 if f1==f2:continue
 # Do not put rails through existing facade walls.
 if hit(x,y,1.25,1.15)[0]:continue
 box((x,y,-2.0),(.12 if along_y else length,length if along_y else .12,4.0))
 for z in [.5,1.1]:box((x,y,z),(.055 if along_y else length,length if along_y else .055,.055),1)
 box((x,y,.55),(.055,.055,1.1),1);guards+=1
# Continuous outside boundary: concrete footing, 2.4m wall, repeated buttresses.
for y in [-67,86]:
 box((-14,y,1.1),(192,.28,2.4));box((-14,y,-2),(192,.4,4))
 for x in range(-110,83,4):box((x,y,1.1),(.24,.5,2.4))
for x in [-110,82]:
 box((x,9.5,1.1),(.28,153,2.4));box((x,9.5,-2),(.4,153,4))
 for y in range(-67,87,4):box((x,y,1.1),(.5,.24,2.4))
mesh_object('A12 retaining guards and perimeter')
scene.name='FACILITY_A12_CONSTRUCTION';bpy.context.preferences.inputs.walk_navigation.use_gravity=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A12_complete.blend'),compress=True)
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[n].hide_viewport=True
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH']:bpy.data.collections[n].hide_viewport=False
scene.name='FACILITY_A12_CONSTRUCTION_MASTER';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A12_complete.blend'),compress=True)
(O/'BUILD.json').write_text(json.dumps({'terrain_cells':len(filled),'edge_guard_segments':guards,'objects':2,'perimeter_bounds':[-110,82,-67,86],'source_surfaces_preserved':True},indent=2));print('A12_BUILT',len(filled),guards,flush=True)
