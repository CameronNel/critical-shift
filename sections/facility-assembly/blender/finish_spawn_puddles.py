"""Two shallow, physically recessed wet pockets in owned paving; no global edits."""
import bpy,bmesh,math,json,hashlib,ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/spawn-finish';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(SRC)
r=json.loads((OUT/'construction.json').read_text());assert before==r['candidate_sha256'];s=bpy.context.scene;bpy.context.view_layer.update();coll=bpy.data.collections['ART | Spawn and medical courtyard']
slabs=sorted([o for o in coll.objects if o.name.startswith('SY | Dimensional courtyard slab')],key=lambda o:o.name)
water=bpy.data.materials['FLR | Shallow pooled water'];img=bpy.data.images['SY | Courtyard localized wear and moisture'];a=np.empty(len(img.pixels),np.float32);img.pixels.foreach_get(a);a=a.reshape(img.size[1],img.size[0],4)
def solid(name,pts,z0,z1,ma):
 n=len(pts);vs=[(x,y,z) for z in (z0,z1) for x,y in pts];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(ma);o=bpy.data.objects.new(name,me);coll.objects.link(o);return o
patches=[(-21.75,21.3,.57,.32),(-24.85,23.2,.61,.32)]
for number,(x,y,rx,ry) in enumerate(patches):
 target=next(o for o in slabs if abs(o.location.x-x)<1.4 and abs(o.location.y-y)<1.4)
 points=[]
 for k in range(28):
  t=2*math.pi*k/28;scale=1+.09*math.sin(t*3+.7)+.05*math.sin(t*7)
  points.append((x+rx*scale*math.cos(t),y+ry*scale*math.sin(t)))
 cutter=solid('SY TEMP | Wet pocket cutter',points,.0018,.04,water);bpy.context.view_layer.update()
 bpy.context.view_layer.objects.active=target;mod=target.modifiers.new('Shallow retained-water pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 film=solid('SY | Recessed shallow puddle '+str(number),[(x+(px-x)*.994,y+(py-y)*.994) for px,py in points],.0019,.0065,water);film['water_depth_m']=.0046
 # Capillary dampness continues from the physical pocket into its own slab face.
 idx=slabs.index(target);tx,ty=idx%8,idx//8;N=128;yy,xx=np.mgrid[0:N,0:N]
 lo=np.min(np.asarray([target.matrix_world@Vector(v) for v in target.bound_box]),axis=0);hi=np.max(np.asarray([target.matrix_world@Vector(v) for v in target.bound_box]),axis=0)
 X=lo[0]+np.clip((xx-2)/(N-5),0,1)*(hi[0]-lo[0]);Y=lo[1]+np.clip((yy-2)/(N-5),0,1)*(hi[1]-lo[1]);q=((X-x)/(rx+.16))**2+((Y-y)/(ry+.12))**2;wet=np.clip((1.18-q)*2,0,1)*.97
 tile=a[ty*N:(ty+1)*N,tx*N:(tx+1)*N];tile[:,:,1]=np.maximum(tile[:,:,1],wet)
img.pixels.foreach_set(a.ravel());img.pack()
for o in coll.objects:
 if o.name.startswith('SY | Tall riser wall bracket'):o.location.x+=.03
bpy.context.view_layer.update();assert sha(SRC)==before;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SRC));r['candidate_sha256']=sha(SRC);r['new_objects']=len(coll.objects);r['recessed_puddles']=patches;r['puddle_depth_m']=.0046;r['tall_brackets']='Rear faces seated against measured facade plane'
(OUT/'construction.json').write_text(json.dumps(r,indent=2));print('PUDDLES_SEATED',flush=True)
