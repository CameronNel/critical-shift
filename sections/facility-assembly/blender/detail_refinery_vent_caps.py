"""Seat service panels on the visible vent end caps; final close-up correction."""
import bpy,bmesh,ast,math,json,hashlib,ctypes,random
from pathlib import Path
from mathutils import Vector,Matrix
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-finish';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();src=Path(bpy.data.filepath)
report=json.loads((OUT/'verification.json').read_text());assert sha(src)==report['saved_sha256'];before=sha(src)
s=bpy.context.scene;coll=bpy.data.collections['ART | Refinery authored surface finish'];rng=random.Random(714)
for fn,names in [('build_refinery_exterior.py',('mesh','box','cyl','P','wb')),('finish_refinery_surfaces.py',('decal',))]:
 tree=ast.parse(Path(__file__).with_name(fn).read_text())
 for name in names:
  fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<cap>','exec'))
dark=bpy.data.materials['RFX | Recess and rubber'];blue=bpy.data.materials['RFX | Faded slate cobalt'];rust=bpy.data.materials['RFX | Local oxidation'];bare=bpy.data.materials['RFS | Exposed brushed edge metal'];cream=bpy.data.materials['RFS | Worn warm ivory stencil'];ochre=bpy.data.materials['RFX | Worn ochre safety enamel']
tree=ast.parse(Path(__file__).with_name('finish_refinery_surfaces.py').read_text())
for name in ('label','bolt'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<cap>','exec'))
made=[]
for x,y,z,num in ((3.02,-15.14,2.85,'02'),(-11.17,-19.565,2.8,'01')):
 d=-24.5-y
 for name,yy,dim,ma in [('Vent end service gasket',y-.001,(.435,.009,.88),dark),('Vent end replaceable panel',y-.010,(.395,.014,.84),blue)]:made.append(box(name,(x,yy,z),dim,ma,.006).name)
 for dx in (-.155,.155):
  for dz in (-.34,.34):made.append(bolt('S',x+dx,d+.024,z+dz,.014).name)
 made.append(label('Vent end stencil','EX-'+num,'S',x,d+.019,z+.15,.085).name)
 made.append(label('Vent service instruction','ISOLATE','S',x,d+.019,z-.05,.048).name)
 made.append(wb('Vent service accent','S',x,d+.019,z-.19,.29,.005,.043,ochre,.002).name)
 for j in range(11):
  a=x+rng.uniform(-.17,.17);zz=z-.40+rng.uniform(-.008,.028);w=rng.uniform(.012,.026);h=rng.uniform(.015,.036)
  made.append(decal('Vent lower fold corrosion','S',[(a-w,zz),(a+w,zz),(a+w*.6,zz+h),(a,zz+h*.6),(a-w*.5,zz+h*.8)],d+.018,rust).name)
report['new_objects']=[o.name for o in coll.objects];report['vent_end_cap_details']=made
assert sha(src)==before;bpy.ops.wm.save_as_mainfile(filepath=str(src),check_existing=False);report['saved_sha256']=sha(src);(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('VENT_CAPS_SAVED',report['saved_sha256'],flush=True)
s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];s.cycles.samples=12;s.render.filepath=str(OUT/'entry.png');bpy.ops.render.render(write_still=True);print('ENTRY_CAPS_RENDERED',flush=True)
s.camera=bpy.data.objects['RFX CAMERA | 05_WALK_MINE'];s.cycles.samples=8;s.render.filepath=str(OUT/'mine-approach.png');bpy.ops.render.render(write_still=True);print('MINE_CAPS_RENDERED',flush=True)
