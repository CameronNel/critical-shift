"""Bounded floor construction migration; one CPU worker, revision guarded."""
import bpy,bmesh,ast,json,hashlib,ctypes,shutil,math,random,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/floor-finish';SRC=Path(bpy.data.filepath);MAIN=SRC.with_name('facility_environment.blend')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inspection=json.loads((OUT/'inspection.json').read_text());complete='--complete' in sys.argv
assert sha(MAIN)==inspection['sha256'],'Concurrent main change'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
for fn in ('fingerprint','material_sig'):
 tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
if not complete:
 assert sha(SRC)==inspection['sha256'];backup=SRC.with_name('facility_environment.floor-before.blend')
 if backup.exists():assert sha(backup)==sha(SRC),'Different checkpoint exists'
 else:shutil.copy2(SRC,backup)
 report=dict(before_sha256=sha(SRC),backup=str(backup),original_objects={o.name_full:fingerprint(o) for o in s.objects},materials={m.name_full:material_sig(m) for m in bpy.data.materials},libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries},removed=[],changed=[],panels=[],complete=False)
 coll=bpy.data.collections.new('ART | Dimensional floor finish');s.collection.children.link(coll)
 print('FLOOR_BASELINE_RECORDED',flush=True)
else:
 report=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==report['candidate_sha256'];coll=bpy.data.collections['ART | Dimensional floor finish']
original=list(s.objects);pending_remove=set()
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return Vector(tuple(min(v[i] for v in p) for i in range(3))),Vector(tuple(max(v[i] for v in p) for i in range(3)))
def mesh(name,vs,fs,mats):
 me=bpy.data.meshes.new('FLR | '+name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);coll.objects.link(o)
 for m in mats:me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return o
def box(name,lo,hi,mat):
 vs=[(x,y,z) for z in (lo[2],hi[2]) for y in (lo[1],hi[1]) for x in (lo[0],hi[0])]
 return mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],[mat])
def remove(o):
 report['removed'].append(o.name_full);pending_remove.add(o.name);o.hide_render=True;o.hide_viewport=True
def cut(o,lo,hi):
 cutter=box('Temporary drain opening',lo,hi,bpy.data.materials['RFX | Recess and rubber']);bpy.context.view_layer.objects.active=o;o.select_set(True)
 mod=o.modifiers.new('Preserved drainage opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False);bpy.data.objects.remove(cutter,do_unlink=True)
def material(name,col,rough,coat=0):
 # Copy the existing four-node framed material; no new graph topology/layout.
 key='FLR | '+name
 if key in bpy.data.materials:return bpy.data.materials[key]
 m=bpy.data.materials['CY | Patched mineral concrete 0'].copy();m.name=key;m.diffuse_color=(*col,1)
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB':
   for e,k in zip(n.color_ramp.elements,(.90,1.09)):e.color=(*(c*k for c in col),1)
  elif n.type=='TEX_NOISE':n.inputs['Scale'].default_value=2.3;n.inputs['Detail'].default_value=2
  elif n.type=='BSDF_PRINCIPLED':
   n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=0;n.inputs['Coat Weight'].default_value=coat;n.inputs['Coat Roughness'].default_value=.10;n.inputs['IOR'].default_value=1.333 if coat else 1.45
 return m
dry=[material('Worn mineral face '+str(i),c,.84) for i,c in enumerate(((.255,.236,.199),(.30,.278,.234),(.225,.217,.195),(.275,.262,.228)))]
edge=material('Exposed pale aggregate',(.31,.29,.25),.93);side=material('Cut mineral return',(.166,.155,.130),.94);bed=material('Recessed compacted joint bed',(.068,.060,.049),.98)
damp=[material('Absorbed moisture '+str(i),c,.48) for i,c in enumerate(((.14,.13,.112),(.16,.15,.132),(.12,.119,.105),(.145,.139,.12)))]
water=material('Shallow pooled water',(.061,.071,.069),.105,1)
# Holes remain under the existing grating and frames; no drainage hardware moves.
holes=[]
for o in original:
 if o.name.startswith('RFX | Drain sump lining'):
  lo,hi=bounds(o);holes.append((lo.x+.001,hi.x-.001,lo.y+.001,hi.y-.001))
 elif o.name.startswith('RFX | Apron inspection dark well'):
  lo,hi=bounds(o);holes.append((lo.x,hi.x,lo.y,hi.y))
def relevant_holes(xa,xb,ya,yb):return [h for h in holes if h[0]<xb and h[1]>xa and h[2]<yb and h[3]>ya]
def panel(name,xa,xb,ya,yb,z,bottom,index,wet):
 rng=random.Random(5731+index);cx=(xa+xb)/2;cy=(ya+yb)/2;w=xb-xa;h=yb-ya
 # Twenty perimeter stations keep chipped bevels local, not random whole-slab warps.
 rect=[]
 corners=[(xa,ya),(xb,ya),(xb,yb),(xa,yb)]
 for k in range(4):
  a=corners[k];b=corners[(k+1)%4]
  for t in (0,.12,.39,.68,.88):rect.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
 n=len(rect);vs=[];fs=[];mi=[];bw=.022 if w>1.5 else .014;depth=min(.026,(z-bottom)*.55)
 vs.extend((x,y,bottom) for x,y in rect);vs.extend((x,y,z-depth) for x,y in rect)
 for k,(x,y) in enumerate(rect):
  inset=bw+(rng.uniform(.009,.030) if (k+index)%7==0 else 0)
  vs.append((x+(cx-x)*inset/(w/2),y+(cy-y)*inset/(h/2),z))
 fs.append(tuple(reversed(range(n))));mi.append(2)
 for a,b,m in ((0,n,2),(n,2*n,1)):
  for k in range(n):fs.append((a+k,a+(k+1)%n,b+(k+1)%n,b+k));mi.append(m if (k+index)%4==0 or m==2 else 0)
 if wet:
  # Actual shallow depression with a dark damp margin and a level water surface.
  pool=[];pcx=cx+rng.uniform(-.07,.07)*w;pcy=cy+rng.uniform(-.10,.10)*h;stretch=rng.uniform(.65,1.05)
  for k,(x,y) in enumerate(rect):
   a=math.atan2((y-cy)/(h/2),(x-cx)/(w/2));r=.23*(1+.24*math.sin(a*3+index)+.10*math.cos(a*7));pool.append((pcx+math.cos(a)*w*r,pcy+math.sin(a)*h*r*stretch))
  vs.extend((pcx+(x-pcx)*1.18,pcy+(y-pcy)*1.18,z) for x,y in pool)
  vs.extend((x,y,z-.009) for x,y in pool)
  for a,b,m in ((2*n,3*n,0),(3*n,4*n,3)):
   for k in range(n):fs.append((a+k,a+(k+1)%n,b+(k+1)%n,b+k));mi.append(m)
  fs.append(tuple(range(4*n,5*n)));mi.append(3)
  wp=[(pcx+(x-pcx)*1.085,pcy+(y-pcy)*1.085,z-.0045) for x,y in pool]
  puddle=mesh('Water in shallow slab depression',wp,[tuple(range(n))],[water]);puddle['intentional_surface_overlay']=True;puddle['water_depth_m']=.0045
 else:fs.append(tuple(range(2*n,3*n)));mi.append(0)
 o=mesh(name,vs,fs,[dry[index%4],edge,side,damp[index%4]])
 for p,m in zip(o.data.polygons,mi):p.material_index=m
 for a,b,c,d in relevant_holes(xa,xb,ya,yb):cut(o,(a,c,bottom-.03),(b,d,z+.03))
 report['panels'].append(dict(name=o.name,lo=[xa,ya,bottom],hi=[xb,yb,z],index=index,wet=wet,bevel_width=bw,joint_recess=.032 if z>.1 else .010))
 return o
def use_wet(index,xa,xb,ya,yb):return random.Random(index*171+993).random()<.24 and not relevant_holes(xa,xb,ya,yb)
if complete:
 # Pixel review correction: fewer, varied off-centre pools in the first bay.
 first=list(report['panels']);report['panels']=[]
 for o in list(coll.objects):
  if o.name.startswith(('FLR | Courtyard dimensional slab','FLR | Water in shallow slab depression')):bpy.data.objects.remove(o,do_unlink=True)
 for i,p in enumerate(first):
  xa,ya,bottom=p['lo'];xb,yb,z=p['hi'];idx=p.get('index',i);panel('Courtyard dimensional slab',xa,xb,ya,yb,z,bottom,idx,use_wet(idx,xa,xb,ya,yb))
 original=list(s.objects)
targets=[q for q in inspection['objects'] if q['name'].startswith(('CY | Patched yard slab','RFX | Solid apron paving slab'))]
chosen=[q for q in targets if (q['name'].startswith('CY | Patched yard slab 0') and int(q['name'].split('slab ')[1].split('-')[0])<3)==(not complete)]
for serial,q in enumerate(targets):
 if q not in chosen:continue
 o=bpy.data.objects[q['name']];lo,hi=bounds(o);courtyard=o.name.startswith('CY |');xa,ya=lo.x,lo.y;xb,yb=hi.x,hi.y;top=hi.z
 # Keep floor top elevations; thickness goes downward, away from doors and rails.
 bottom=lo.z if courtyard else top-.060
 under=box('Solid recessed paving bed',(xa,ya,bottom-.006),(xb,yb,top-(.032 if courtyard else .010)),bed)
 for a,b,c,d in relevant_holes(xa,xb,ya,yb):cut(under,(a,c,bottom-.04),(b,d,top+.03))
 nx=2 if courtyard else 1;ny=2 if courtyard else 1;gap=.032
 for ix in range(nx):
  for iy in range(ny):
   a=xa+(xb-xa)*ix/nx+(gap/2 if ix else 0);b=xa+(xb-xa)*(ix+1)/nx-(gap/2 if ix<nx-1 else 0)
   c=ya+(yb-ya)*iy/ny+(gap/2 if iy else 0);d=ya+(yb-ya)*(iy+1)/ny-(gap/2 if iy<ny-1 else 0)
   idx=serial*4+ix*2+iy;wet=use_wet(idx,a,b,c,d)
   panel('Courtyard dimensional slab' if courtyard else 'Refinery dimensional slab',a,b,c,d,top,bottom,idx,wet)
 remove(o)
if complete:
 # These old graphic-only patches would float over the new depressions; retire
 # only the refinery apron decorations, preserving all building materials.
 for o in original:
  if o.name in bpy.data.objects and o.name.startswith(('RFX | Uneven old paving repair','RFX | Hairline paving settlement')):remove(o)
# Existing paint remains on its old, unchanged walking elevation. Water is kept
# away from the shoulder strip by the interior footprint of each depression.
for name in pending_remove:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
for name in report['materials']:
 if name in bpy.data.materials and bpy.data.materials[name].users==0:bpy.data.materials[name].use_fake_user=True
bpy.context.view_layer.update();errors=[]
for o in coll.objects:
 if o.type!='MESH' or o.get('intentional_surface_overlay'):continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces) or abs(bm.calc_volume())<1e-12:errors.append(o.name)
 bm.free()
assert not errors,errors
report['mesh_errors']=errors;report['new_objects']=[o.name for o in coll.objects];report['new_materials']={m.name:material_sig(m) for m in bpy.data.materials if m.name.startswith('FLR |')}
report['node_layout']='Existing four-node framed topology/positions copied unchanged; socket values only. Live drawn bounds unavailable in headless mode.'
assert sha(MAIN)==inspection['sha256']
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['JNT CAMERA | COURTYARD SOUTH']
target=MAIN if complete else MAIN.with_name('facility_environment.floor-candidate.blend');bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False)
report['saved_sha256' if complete else 'candidate_sha256']=sha(target);(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('FLOOR_SAVED',str(target),flush=True)
s.render.filepath=str(OUT/'courtyard.png');bpy.ops.render.render(write_still=True);print('FLOOR_COURTYARD_RENDERED',flush=True)
if complete:
 s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];s.render.filepath=str(OUT/'refinery.png');bpy.ops.render.render(write_still=True);print('FLOOR_REFINERY_RENDERED',flush=True)
