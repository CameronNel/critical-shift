"""Bounded colour-only refinery edit. Headless CPU; preserves surface construction."""
import bpy,ast,ctypes,hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-palette';OUT.mkdir(parents=True,exist_ok=True)
SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
owned={o for c in bpy.data.collections if c.name in ('ART | Refinery exterior process systems','ART | Refinery authored surface finish') for o in c.objects}
targets=['RFX | Faded slate cobalt','RFX | Charcoal coated steel','RFS | Louvre folded blue grey metal','RFX | Dusty galvanized duct','RFX | Local oxidation','RFX | Worn ochre safety enamel']
def palette(m):
 return dict(diffuse=list(m.diffuse_color),ramps=[dict(node=n.name,stops=[dict(position=e.position,color=list(e.color)) for e in n.color_ramp.elements]) for n in m.node_tree.nodes if n.type=='VALTORGB'])
if '--inspect' in sys.argv:
 rows=[]
 for name in targets:
  m=bpy.data.materials[name];users=[o for o in s.objects if any(slot.material==m for slot in o.material_slots)]
  rows.append(dict(name=name,library=str(m.library),palette=palette(m),users=[o.name for o in users],outside_owned=[o.name for o in users if o not in owned]))
 (OUT/'inspection.json').write_text(json.dumps(dict(source=str(SRC),sha256=sha(SRC),materials=rows,accent_candidates=[o.name for o in owned if any(k in o.name for k in ('Service cabinet inset face','Filter access face','Vent end replaceable panel'))]),indent=2));print('PALETTE_INSPECTED',flush=True);sys.exit(0)
tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='material_sig');exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
def geom_signature():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name_full):
  h.update(o.name_full.encode());h.update(np.asarray(o.matrix_world,dtype=np.float64).tobytes());h.update(str((o.type,o.hide_render,o.hide_viewport)).encode())
  if o.type=='MESH':
   for field,prop,dtype,n in [('vertices','co',np.float32,3),('loops','vertex_index',np.int32,1),('polygons','material_index',np.int32,1)]:
    data=getattr(o.data,field);a=np.empty(len(data)*n,dtype);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  elif o.type=='FONT':h.update(str((o.data.body,o.data.size)).encode())
  elif o.type=='LIGHT':h.update(str((o.data.energy,tuple(o.data.color))).encode())
 return h.hexdigest()
def settings():
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
if '--verify' in sys.argv:
 r=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==r['saved_sha256'];assert geom_signature()==r['geometry_sha256'],'Geometry changed'
 mats={m.name_full:m for m in bpy.data.materials};changed=[n for n,h in r['protected_materials'].items() if n not in mats or material_sig(mats[n])!=h];assert not changed,changed
 for n,p in r['result_palettes'].items():assert palette(bpy.data.materials[n])==p,n
 for o in s.objects:assert [slot.material.name_full if slot.material else None for slot in o.material_slots]==r['result_slots'][o.name_full],o.name
 badlibs=[p for p,h in r['libraries'].items() if sha(p)!=h];assert not badlibs,badlibs
 missing=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists()];assert not missing,missing
 print('PALETTE_COLD_VERIFIED',len(s.objects),len(r['protected_materials']),flush=True);settings();s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
 def pixels(p):
  im=bpy.data.images.load(str(p),check_existing=False);a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(-1,4)
 d=np.abs(pixels(OUT/'entry.png')-pixels(OUT/'cold-repeat.png'));r['cold_open']=dict(geometry_unchanged=True,protected_material_changes=changed,missing_images=missing,library_changes=badlibs,changed_pixels=int(np.any(d>0,axis=1).sum()),max_channel_difference=float(d.max()),mean_channel_difference=float(d.mean()))
 s.camera=bpy.data.objects['RFX CAMERA | 01_SW'];s.cycles.samples=4;s.render.filepath=str(OUT/'overview.png');bpy.ops.render.render(write_still=True)
 r['source_unchanged']=sha(SRC)==r['saved_sha256'];assert r['source_unchanged'];r['complete']=True;r['views']=[]
 for fn,cam,ns in [('entry.png','06_WALK_ENTRY',8),('overview.png','01_SW',4)]:
  c=bpy.data.objects['RFX CAMERA | '+cam];r['views'].append(dict(path=str(OUT/fn),sha256=sha(OUT/fn),camera=c.name,position=list(c.location),rotation=list(c.rotation_euler),lens_mm=c.data.lens,samples=ns))
 (OUT/'verification.json').write_text(json.dumps(r,indent=2));print('PALETTE_EVIDENCE_COMPLETE',flush=True);sys.exit(0)
inspection=json.loads((OUT/'inspection.json').read_text());before=sha(SRC);assert before==inspection['sha256'];assert all(not q['outside_owned'] for q in inspection['materials'])
backup=SRC.with_name('facility_environment.palette-before.blend')
if backup.exists():assert sha(backup)==before,'Different palette checkpoint'
else:shutil.copy2(SRC,backup)
geometry=geom_signature();protected={m.name_full:material_sig(m) for m in bpy.data.materials if m.name not in targets};libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries};slots={o.name_full:[slot.material.name_full if slot.material else None for slot in o.material_slots] for o in s.objects}
def recolour(m,col):
 ramps=[n for n in m.node_tree.nodes if n.type=='VALTORGB'];assert len(ramps)==1 and len(ramps[0].color_ramp.elements)==4,m.name
 for e,k in zip(ramps[0].color_ramp.elements,(.58,.84,1.11,1.27)):e.color=(*(c*k for c in col),1)
 m.diffuse_color=(*col,1)
colours={targets[0]:(.18,.174,.159),targets[1]:(.054,.052,.047),targets[2]:(.245,.237,.214),targets[3]:(.29,.271,.231),targets[4]:(.26,.093,.032),targets[5]:(.60,.305,.048)}
for n,col in colours.items():recolour(bpy.data.materials[n],col)
# Reuse the existing finish graph exactly; only its pigment changes.
oxide=bpy.data.materials[targets[0]].copy();oxide.name='RFX | Muted oxide maintenance enamel';recolour(oxide,(.225,.081,.044))
accent_names=inspection['accent_candidates'];assert accent_names
for name in accent_names:
 o=bpy.data.objects[name];assert o in owned and o.library is None;assert len(o.data.materials)==1
 o.material_slots[0].link='OBJECT';o.material_slots[0].material=oxide
result_slots={o.name_full:[slot.material.name_full if slot.material else None for slot in o.material_slots] for o in s.objects}
assert all(result_slots[n]==v for n,v in slots.items() if n not in accent_names)
assert not [m.name_full for m in bpy.data.materials if m.name_full in protected and material_sig(m)!=protected[m.name_full]]
settings();s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];assert sha(SRC)==before;bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False)
r=dict(source=str(SRC),before_sha256=before,saved_sha256=sha(SRC),backup=str(backup),geometry_sha256=geometry,protected_materials=protected,libraries=libraries,accent_objects=accent_names,result_palettes={n:palette(bpy.data.materials[n]) for n in targets+[oxide.name]},result_slots=result_slots,settings=dict(engine='CYCLES',device='CPU',threads=1,resolution=[1280,720],denoiser='CPU OIDN',seed=73),complete=False,note='Pigment and bounded material-slot edits only. No geometry, graph structure, roughness, relief or lighting changes; existing node layout preserved, drawn layout unverified headlessly.')
(OUT/'verification.json').write_text(json.dumps(r,indent=2));print('PALETTE_SAVED',r['saved_sha256'],flush=True);s.render.filepath=str(OUT/'entry.png');bpy.ops.render.render(write_still=True);print('PALETTE_ENTRY_RENDERED',flush=True)
