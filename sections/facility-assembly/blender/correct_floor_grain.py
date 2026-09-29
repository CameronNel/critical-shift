"""Reduce high-resolution sparkle without flattening the constructed paving."""
import bpy,json,hashlib,ctypes
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/ground-finish';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=json.loads((OUT/'verification.json').read_text());before=sha(SRC);assert before==r['saved_sha256']
changed=[]
for m in bpy.data.materials:
 if not m.name.startswith(('GF | Refinery dimensional slab mineral','GF | Courtyard dimensional slab mineral')):continue
 n=m.node_tree.nodes;bum=next(q for q in n if q.type=='BUMP');bum.inputs['Strength'].default_value=.06;bum.inputs['Distance'].default_value=.0015
 fine=next(l.from_node for l in m.node_tree.links if l.to_socket==bum.inputs['Height']);fine.inputs['Scale'].default_value=18;changed.append(m.name)
assert len(changed)==8
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
assert sha(SRC)==before;bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False);r['saved_sha256']=sha(SRC);r['high_resolution_correction']=dict(materials=changed,bump_strength=.06,bump_distance_m=.0015,grain_scale=18,geometry_changed=False);(OUT/'verification.json').write_text(json.dumps(r,indent=2))
manifest=dict(source=str(SRC),source_sha256=sha(SRC),settings=dict(device='CPU',threads=1,resolution=[1280,720],samples=4,seed=73),views=[],complete=False)
for name in ('refinery-floor','mine-canopy','mine-cliff-yard','courtyard'):
 s.camera=bpy.data.objects['JNT CAMERA | COURTYARD SOUTH' if name=='courtyard' else 'GF CAMERA | '+name];s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 manifest['views'].append(dict(name=name,path=s.render.filepath,sha256=sha(s.render.filepath),saved_camera=s.camera.name));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FINAL_RENDERED',name,flush=True)
assert sha(SRC)==manifest['source_sha256'];manifest.update(complete=True,source_unchanged=True);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('FINAL_COMPLETE',flush=True)
