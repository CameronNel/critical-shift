"""Preservation audit, guarded promotion and fresh-process render verification."""
import bpy,ast,json,hashlib,ctypes,sys
import numpy as np
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/ground-finish';MAIN=Path(__file__).with_name('facility_environment.blend');SRC=Path(bpy.data.filepath)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'verification.json').read_text());cold='--cold' in sys.argv;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
for path,names in (('build_transition_courtyard.py',('fingerprint','material_sig')),('refine_ground_finish.py',('geom_sig','strongmat'))):
 tree=ast.parse(Path(__file__).with_name(path).read_text())
 for fn in names:
  fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
assert sha(SRC)==report['saved_sha256' if cold else 'candidate_sha256']
if not cold:assert sha(MAIN)==report['before_sha256'],'Main changed concurrently'
objs={o.name_full:o for o in s.objects};materials={m.name_full:m for m in bpy.data.materials};changed=set(report['changed'])
errors=[]
for name,digest in report['geometry'].items():
 if name not in objs or geom_sig(objs[name])!=digest:errors.append(['Geometry',name])
print('ALL_GEOMETRY_CHECKED',len(report['geometry']),flush=True)
for name,digest in report['original_objects'].items():
 if name not in objs:errors.append(['Missing',name])
 elif name not in changed and fingerprint(objs[name])!=digest:errors.append(['Protected Object',name])
retired=[]
for name,digest in report['materials'].items():
 if name not in materials and name in {'R39 | Worn floor planks','R39 | Yard mud'}:
  # Read-only inventory confirms sole prior users were the two replaced surfaces.
  retired.append(name)
 elif name not in materials or strongmat(materials[name])!=digest:errors.append(['Original Material',name])
for name,faces in report['roof_faces'].items():
 o=objs[name]
 for index,material in faces.items():
  if o.data.materials[o.data.polygons[int(index)].material_index].name_full!=material:errors.append(['Roof Face',name,index])
for path,digest in report['libraries'].items():
 if sha(path)!=digest:errors.append(['Library',path])
missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file and not im.packed_files and im.filepath and not Path(bpy.path.abspath(im.filepath,library=im.library)).exists():missing.append(im.name)
assert not missing,missing
assert not errors,errors
audit=dict(all_mesh_geometry_unchanged=len(report['geometry']),protected_original_objects=len(report['original_objects'])-len(changed),original_material_graphs_unchanged=len(report['materials'])-len(retired),retired_unused_surface_materials=retired,roof_face_assignments_unchanged=sum(map(len,report['roof_faces'].values())),missing_textures=missing,errors=errors,scope='All mesh vertex positions/topology/transforms unchanged; floor elevations, rails and roof preserved. Material/UV/colour-attribute edits only. Not a Unity test.')
print('PRESERVATION_PASSED',flush=True)
layout={}
for m in bpy.data.materials:
 if not m.name.startswith('GF |'):continue
 nodes=m.node_tree.nodes;unframed=[n.name for n in nodes if n.type!='FRAME' and not n.parent];frames={n.label:sum(ch.parent==n for ch in nodes) for n in nodes if n.type=='FRAME'}
 layout[m.name]=dict(unframed=unframed,frames=frames)
 if m.name!='GF | Shaded Cliff Foot' and not m.name.startswith('GF | Ground Contact'):assert not unframed and all(4<=v<=19 for v in frames.values()),(m.name,unframed,frames)
audit['node_frames']=layout;audit['node_layout_limit']='Authored frame membership/counts checked. Inherited cliff upstream layout unchanged. Drawn bounds, socket alignment, crossings and compactness unverified: required headless workflow has no Node Editor.'
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
if cold:
 s.cycles.samples=json.loads((OUT/'manifest.json').read_text())['settings']['samples']
 s.camera=bpy.data.objects['GF CAMERA | refinery-floor'];s.render.filepath=str(OUT/'cold-repeat.png');bpy.ops.render.render(write_still=True)
 def pixels(path):
  im=bpy.data.images.load(str(path),check_existing=False);a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a
 a=pixels(OUT/'refinery-floor.png');b=pixels(OUT/'cold-repeat.png');delta=np.abs(a-b)
 audit['pixel_repeat']=dict(maximum=float(delta.max()),mean=float(delta.mean()),changed_channels=int(np.count_nonzero(delta)))
 assert delta.max()<=1/255+1e-6;audit['saved_sha256']=sha(MAIN);audit['complete']=True;(OUT/'cold-open.json').write_text(json.dumps(audit,indent=2));print('COLD_COMPLETE',flush=True)
 manifest=json.loads((OUT/'manifest.json').read_text())
 if not any(v['name']=='courtyard' for v in manifest['views']):
  s.camera=bpy.data.objects['JNT CAMERA | COURTYARD SOUTH'];s.render.filepath=str(OUT/'courtyard.png');bpy.ops.render.render(write_still=True)
  manifest['views'].append(dict(name='courtyard',path=s.render.filepath,sha256=sha(s.render.filepath),saved_camera=s.camera.name));assert sha(MAIN)==manifest['source_sha256'];(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('COURTYARD_VERIFIED',flush=True)
else:
 assert sha(MAIN)==report['before_sha256'];s.camera=bpy.data.objects['GF CAMERA | refinery-floor'];bpy.ops.wm.save_as_mainfile(filepath=str(MAIN),check_existing=False)
 report.update(saved_sha256=sha(MAIN),audit=audit,complete=True);(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('PROMOTED',flush=True)
 manifest=dict(source=str(MAIN),source_sha256=sha(MAIN),settings=dict(device='CPU',threads=1,resolution=[1280,720],samples=8,seed=73),views=[],complete=False)
 for name in ('refinery-floor','mine-canopy','mine-cliff-yard','courtyard'):
  s.camera=bpy.data.objects['JNT CAMERA | COURTYARD SOUTH' if name=='courtyard' else 'GF CAMERA | '+name];s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
  manifest['views'].append(dict(name=name,path=s.render.filepath,sha256=sha(s.render.filepath),saved_camera=s.camera.name));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FINAL_RENDERED',name,flush=True)
 assert sha(MAIN)==manifest['source_sha256'];manifest.update(complete=True,source_unchanged=True);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FINAL_COMPLETE',flush=True)
