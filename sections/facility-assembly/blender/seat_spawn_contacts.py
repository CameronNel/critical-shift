"""Final owned-only contact/puddle correction on the promoted scene."""
import bpy,math,json,hashlib,ctypes,runpy
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/spawn-finish';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(SRC)
v=json.loads((OUT/'verification.json').read_text());assert before==v['sha256'];s=bpy.context.scene;bpy.context.view_layer.update();coll=bpy.data.collections['ART | Spawn and medical courtyard']
ground=[o for o in s.objects if o.type=='MESH' and (o.name.startswith(('VC | Quiet concrete','SITE | Compound ground','SITE | Reconnected MATERIAL_PREVIEW_09','MATERIAL_PREVIEW_CONNECTION_C01')) or o.name=='Watershed | Continuous Terrain')]
contacts=[]
for o in coll.objects:
 if not o.name.startswith('SY | Cliff-foot'):continue
 pts=[o.matrix_world@Vector(q) for q in o.bound_box];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);c=(lo+hi)/2;hits=[]
 for g in ground:
  inv=g.matrix_world.inverted();hit,p,n,f=g.ray_cast(inv@Vector((c.x,c.y,5)),inv.to_3x3()@Vector((0,0,-1)))
  if hit:
   wp=g.matrix_world@p
   if wp.z<.2:hits.append((wp.z,g.name_full))
 assert hits,('No ground below edge boulder',o.name)
 elevation,support=max(hits);embed=max(.045,(hi.z-lo.z)*.11);o.location.z+=elevation-embed-lo.z
 contacts.append(dict(object=o.name,ground=support,elevation=elevation,bedding_depth=embed))
water=bpy.data.materials['FLR | Shallow pooled water'].copy();water.name='SY | Quiet shallow retained water'
for n in water.node_tree.nodes:
 if n.type=='BSDF_PRINCIPLED':n.inputs['Roughness'].default_value=.24;n.inputs['Coat Weight'].default_value=.35;n.inputs['Coat Roughness'].default_value=.22
 elif n.type=='VALTORGB':
  for e,k in zip(n.color_ramp.elements,(.93,1.05)):e.color=(.14*k,.155*k,.15*k,1)
slabs=[o for o in coll.objects if o.name.startswith('SY | Dimensional courtyard slab')]
for idx,(x,y,rx,ry) in enumerate([(-21.75,21.3,.57,.32),(-24.85,23.2,.61,.32)]):
 slab=next(o for o in slabs if abs(o.location.x-x)<1.4 and abs(o.location.y-y)<1.4);pool=bpy.data.objects['SY | Recessed shallow puddle '+str(idx)];pool.data.materials[0]=water
 for o in (slab,pool):
  inv=o.matrix_world.inverted()
  for vtx in o.data.vertices:
   p=o.matrix_world@vtx.co;dx,dy=p.x-x,p.y-y;t=math.atan2(dy/ry,dx/rx);rad=(dx/rx)**2+(dy/ry)**2
   if rad<1.6:
    # Identical deformation on the recess and water contour keeps the film seated.
    f=.86+.21*math.sin(t*2+.4)+.13*math.sin(t*5-1.2);nx=dx*f;ny=dy*f*.78
    angle=.16 if idx==0 else -.21;p.x=x+nx*math.cos(angle)-ny*math.sin(angle);p.y=y+nx*math.sin(angle)+ny*math.cos(angle);vtx.co=inv@p
  o.data.update()
bpy.context.view_layer.update();assert sha(SRC)==before;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
r=json.loads((OUT/'construction.json').read_text());r['ground_contacts']=contacts;r['final_source_sha256']=sha(SRC);r['final_contact_correction']='Ray-seated edge boulders and matching asymmetric wet-pocket/water contours with quieter reflection.';(OUT/'construction.json').write_text(json.dumps(r,indent=2));print('CONTACTS_SEATED',len(contacts),flush=True)
runpy.run_path(str(Path(__file__).with_name('verify_spawn_finish.py')),run_name='__main__')
