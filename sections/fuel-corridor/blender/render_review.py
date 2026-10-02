"""Task evidence wrapper around the existing fixed-camera render tool.

RES=1280x853 SAMPLES=48 blender -b --python render_review.py -- scene out cams
Writes PNGs plus hash/camera/settings manifest; does not save the native scene.
"""
import os,sys,json,hashlib,datetime
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sections/spawn-room/production/optimise'))
import render_cams
args=sys.argv[sys.argv.index('--')+1:];src=Path(args[0]).resolve();out=Path(args[1]).resolve();cams=args[2].split(',')
assert src.is_file() and src.stat().st_size>1000
frames=[int(f) for f in os.environ.get('FRAMES','').split(',') if f]
if frames:
    # Temporal extension of the same fixed-view renderer/settings. Native frame
    # state is evaluated explicitly and the source is never saved.
    out.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(src))
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU'
    sc.cycles.samples=int(os.environ.get('SAMPLES','48'));sc.cycles.use_denoising=True;sc.cycles.seed=7
    sc.render.resolution_x,sc.render.resolution_y=map(int,os.environ.get('RES','960x540').split('x'))
    sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
    for frame in frames:
        sc.frame_set(frame)
        for name in cams:
            sc.camera=bpy.data.objects[name];sc.render.filepath=str(out/(name+f'_F{frame:04d}.png'))
            bpy.ops.render.render(write_still=True)
else:
    render_cams.main()
scene=bpy.context.scene
images=[(n,f,n+f'_F{f:04d}.png') for f in frames for n in cams] if frames else [(n,scene.frame_current,n+'.png') for n in cams]
assert all((out/filename).is_file() for n,f,filename in images),'Missing requested render'
report={'schema':'fuel-fixed-view-evidence/1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scene':str(src.relative_to(ROOT)),'scene_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'engine':scene.render.engine,'device':scene.cycles.device,'samples':scene.cycles.samples,'seed':scene.cycles.seed,'denoise':scene.cycles.use_denoising,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'cameras':[]}
report['frames']=frames or [scene.frame_current]
report['fps']=scene.render.fps;report['fps_base']=scene.render.fps_base
for name,frame,filename in images:
    cam=bpy.data.objects[name];png=out/filename
    report['cameras'].append({'name':name,'frame':frame,'matrix_world':[list(r) for r in cam.matrix_world],'lens':cam.data.lens,'image':png.name,'sha256':hashlib.sha256(png.read_bytes()).hexdigest()})
(out/'RENDER_MANIFEST.json').write_text(json.dumps(report,indent=2));print('REVIEW_MANIFEST',out,flush=True)
