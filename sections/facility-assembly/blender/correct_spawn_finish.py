"""Bounded pixel-review correction: evaluated mask coordinates and local wear."""
import bpy,bmesh,math,json,hashlib,ctypes,ast,random
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/spawn-finish';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'construction.json').read_text());before=sha(SRC);assert before==r['candidate_sha256'];assert sha(SRC.with_name('facility_environment.blend'))==r['before_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();coll=bpy.data.collections['ART | Spawn and medical courtyard']
tree=ast.parse(Path(__file__).with_name('build_spawn_finish.py').read_text())
for name in ('bounds','P','wb','ring','bolt'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<helpers>','exec'))
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text().replace("'RFX | '","'SY | '"))
for name in ('mesh','box','beam','cyl'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<mesh>','exec'))
steel=bpy.data.materials['RFX | Charcoal coated steel'];zinc=bpy.data.materials['RFX | Dusty galvanized duct'];bare=bpy.data.materials['RFS | Exposed brushed edge metal'];rust=bpy.data.materials['RFX | Local oxidation'];dark=bpy.data.materials['RFX | Recess and rubber'];soot=bpy.data.materials['RFS | Mineral runoff'];cream=bpy.data.materials['RFS | Worn warm ivory stencil'];RW_X=r['tall_service_support']['point'][0]
slabs=sorted([o for o in coll.objects if o.name.startswith('SY | Dimensional courtyard slab')],key=lambda o:o.name)
N=128;cols=8;rows=math.ceil(len(slabs)/cols);pixels=np.zeros((rows*N,cols*N,4),np.float32);pixels[:,:,3]=1
image=bpy.data.images['SY | Courtyard localized wear and moisture'];uvlimits=[]
for idx,o in enumerate(slabs):
 lo,hi=bounds(o);w,h=hi.x-lo.x,hi.y-lo.y;tx,ty=idx%cols,idx//cols
 yy,xx=np.mgrid[0:N,0:N];u=np.clip((xx-2)/(N-5),0,1);v=np.clip((yy-2)/(N-5),0,1);X=lo.x+u*w;Y=lo.y+v*h
 edge=np.minimum.reduce([u*w,(1-u)*w,v*h,(1-v)*h]);variation=.5+.24*np.sin(X*2.1+Y*3.2)+.17*np.sin(X*4.1-Y*1.8)
 wear=np.clip(1-edge/.09,0,1)*np.clip((variation-.46)*2.7,0,.60)
 wear=np.maximum(wear,np.exp(-((u-.44)/.22)**2)*np.clip((variation-.65)*1.8,0,.25))
 damp=np.clip(1-edge/.23,0,1)*np.clip((.56-variation)*2,0,.45)
 for px,py,sx,sy in [(-30,14,1.6,.6),(-25,19,1.3,.45),(-15,27,.9,1.1),(-12,12,1.3,.6),(-26,28,.9,.65),(-33.8,19,.7,1.1)]:
  radius=((X-px)/sx)**2+((Y-py)/sy)**2;damp=np.maximum(damp,np.clip(1-radius+.11*np.sin(X*7+Y*4),0,1)*.98)
 pixels[ty*N:(ty+1)*N,tx*N:(tx+1)*N,:3]=np.stack((wear,damp,variation),axis=-1)
 uv=o.data.uv_layers['GF_FloorMask']
 for loop in o.data.loops:
  p=o.matrix_world@o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((tx*N+2.5+(p.x-lo.x)/w*(N-5))/(cols*N),(ty*N+2.5+(p.y-lo.y)/h*(N-5))/(rows*N))
 vals=np.asarray([d.uv[:] for d in uv.data]);uvlimits.append([o.name,vals.min(),vals.max()]);assert vals.min()>=0 and vals.max()<=1
image.pixels.foreach_set(pixels.ravel());image.pack()
# Thin, solid local paint-loss and runoff patches. They never stand in for geometry gaps.
def surface_patch(side,u,z,d,w,h,ma):
 outline=[(-.5,-.40),(-.31,-.50),(.38,-.44),(.5,-.08),(.29,.45),(-.28,.5),(-.46,.12)]
 vs=[P(side,u+a*w,d+depth,z+b*h) for depth in (0,.0007) for a,b in outline];n=len(outline)
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh('Localized coating wear',vs,fs,ma);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
for side,u in [('N',-21.1),('EN',9.8),('MW',35.3)]:
 for du,z in [(-.30,.81),(.25,.91),(-.18,1.66)]:surface_patch(side,u+du,z,.434,.04,.12,rust)
 wb('Cabinet identification plate',side,u-.07,.439,1.51,.35,.007,.13,dark,.003)
 data=bpy.data.curves.new('SY | Service cabinet label','FONT');data.body='PWR / 01' if side!='MW' else 'AIR / 02';data.size=.052;data.align_x='CENTER';data.align_y='CENTER';data.extrude=.00015;data.materials.append(cream)
 o=bpy.data.objects.new(data.name,data);coll.objects.link(o);o.location=P(side,u-.07,.444,1.51)
 right=Vector((-1,0,0) if side=='N' else (0,1,0) if side=='EN' else (0,-1,0));up=Vector((0,0,1));o.rotation_euler=Matrix((right,up,right.cross(up))).transposed().to_euler()
for side,u,z in [('N',-24.8,2.96),('N',-22.6,2.96),('EN',11.2,2.6),('MS',-21.4,2.72),('MW',32.5,1.92),('MW',33.8,1.92)]:
 surface_patch(side,u,z-.18,.0897,.045,.38,soot)
for side,u,z,w in [('N',-23.7,3.38,2.4),('E',5.9,3.38,1.15),('MW',33.2,2.35,1.4)]:
 for dz in (-.22,.22):surface_patch(side,u-w/2-.07,z+dz,.367,.04,.05,rust)
# One tool case on top of the retained stored-case cluster breaks the repeated silhouette.
box('Small maintenance toolbox',(-20.1,16,.91),(.56,.54,.285),steel,.025)
box('Toolbox gasket',(-20.1,16,1.056),(.56,.54,.008),dark,.001)
box('Toolbox lid',(-20.1,16,1.084),(.58,.56,.05),zinc,.013)
for x in (-20.29,-19.91):box('Toolbox latch',(x,16.287,1.047),(.035,.022,.08),bare,.003)
for x in (-20.21,-19.99):box('Toolbox handle foot',(x,16,1.125),(.022,.036,.04),steel,.004)
beam('Toolbox carry grip',(-20.21,16,1.15),(-19.99,16,1.15),.025,.03,steel)
# Cluster, rather than scatter, existing boulder assets behind the playable yard edge.
rocks=sorted([o for o in coll.objects if o.name.startswith('SY | Cliff-foot')],key=lambda o:o.name)
for i,o in enumerate(rocks):
 lo,hi=bounds(o);center=(lo+hi)/2;o.scale*=1.35;bpy.context.view_layer.update();lo,hi=bounds(o);o.location+=Vector((center.x-(lo.x+hi.x)/2,center.y-(lo.y+hi.y)/2,-.015-lo.z))
if rocks:
 for i,(x,y,factor) in enumerate([(-36.3,15.6,.40),(-37.1,16.3,.55),(-36.4,18.1,.48),(-36.5,20.4,.35)]):
  o=rocks[i%len(rocks)].copy();o.name='SY | Cliff-foot companion '+str(i);coll.objects.link(o);o.scale*=factor;bpy.context.view_layer.update();lo,hi=bounds(o);o.location+=Vector((x-(lo.x+hi.x)/2,y-(lo.y+hi.y)/2,-.015-lo.z))
bpy.context.view_layer.update();assert sha(SRC)==before
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
r['candidate_sha256']=sha(SRC);r['new_objects']=len(coll.objects);r['pixel_correction']='Evaluated world-space mask mapping; restrained weathering and case details; grouped edge boulders.';r['floor_mask_range']=[float(pixels[:,:,0].max()),float(pixels[:,:,1].max())];r['uv_bounds_validated']=len(uvlimits)
(OUT/'construction.json').write_text(json.dumps(r,indent=2));print('SPAWN_CORRECTED',len(uvlimits),flush=True)
