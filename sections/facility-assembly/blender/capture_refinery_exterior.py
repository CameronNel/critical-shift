"""Read-only four-corner exterior reference capture. Never saves the blend."""
import bpy, json, hashlib, ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runtime/out/environment/refinery-exterior';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SRC=Path(bpy.data.filepath);original=sha(SRC)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
subject=bpy.data.objects['VC | Roof-finished MATERIAL_PREVIEW_refinery']
bb=[subject.matrix_world@Vector(p) for p in subject.bound_box]
bounds=dict(lo=[min(p[i] for p in bb) for i in range(3)],hi=[max(p[i] for p in bb) for i in range(3)])
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.seed=73
s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
camera=bpy.data.objects.new('TEMP | Refinery exterior capture',bpy.data.cameras.new('TEMP | Refinery exterior capture'))
s.collection.objects.link(camera);camera.data.lens=32;camera.data.clip_end=500;s.camera=camera
views=[('01_SW_MINE_APPROACH',(-21,-37,13)),('02_SE_RECEIVING',(13,-37,13)),('03_NE_REAR',(13,3,13)),('04_NW_COURTYARD',(-21,3,13))]
target=Vector((-4,-17,2))
manifest=dict(source=str(SRC),source_sha256=original,refinery_bounds=bounds,read_only=True,cameras_saved=False,settings=dict(engine='CYCLES',device='CPU',threads=1,resolution=[1280,720],samples=4,denoising='CPU OIDN',seed=73),views=[],complete=False)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
for name,pos in views:
    camera.location=pos;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update();path=OUT/(name+'.png');s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    manifest['views'].append(dict(name=name,position=pos,target=list(target),lens_mm=camera.data.lens,path=str(path),sha256=sha(path)))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('REFINERY_CAPTURE',name,flush=True)
manifest.update(complete=True,source_unchanged=sha(SRC)==original)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
assert manifest['source_unchanged'],'Source changed concurrently; captures belong to recorded starting revision'
