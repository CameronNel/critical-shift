"""Encode the native ten-second loop through the existing fixed-view renderer.

The source is never saved. Identical evaluated light/optic holds reuse their
original PNG bytes only when all other scene animation is absent. The manifest
records every native frame and its rendered source frame; no retiming is used.
"""
from pathlib import Path
import argparse, hashlib, json, os, runpy, shutil, subprocess, sys
import bpy

ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser()
ap.add_argument('native');ap.add_argument('output');ap.add_argument('--camera',default='C01_ENTRY')
ap.add_argument('--manifest',default=str(ROOT/'sections/fuel-corridor/production/BUILD_MANIFEST.json'))
ap.add_argument('--plan-only',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(args.native).resolve();out=Path(args.output).resolve()
assert not out.exists(),'Use a new evidence directory to avoid mixing revisions'
build=json.loads(Path(args.manifest).read_text());sha=hashlib.sha256(src.read_bytes()).hexdigest()
assert sha==build['sha256'];atmo=build['atmosphere']
assert atmo['frame_start']==1 and atmo['frame_end']==240 and atmo['fps']==24 and atmo['fps_base']==1
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
bpy.ops.wm.open_mainfile(filepath=str(src));scene=bpy.context.scene
records=atmo['flicker']+atmo['alarms'];allowed={};state=[]
for record in records:
    light=bpy.data.objects[record['light']].data;allowed[light.as_pointer()]={'energy'}
    for optic in record['optics']:
        tree=bpy.data.materials[optic['material']].node_tree
        socket=tree.nodes.get('Principled BSDF').inputs['Emission Strength']
        allowed[tree.as_pointer()]={socket.path_from_id('default_value')}

# Reuse is conservative: unexpected animated data or time-dependent geometry
# falls back to rendering all 240 native frames with the same tool.
safe=True;reasons=[]
ids=list(bpy.data.objects)+list(bpy.data.lights)+list(bpy.data.materials)+list(bpy.data.worlds)+list(bpy.data.scenes)+list(bpy.data.meshes)
ids += [m.node_tree for m in bpy.data.materials if m.node_tree]
for owner in ids:
    ad=getattr(owner,'animation_data',None)
    if not ad:continue
    if ad.drivers or ad.nla_tracks:safe=False;reasons.append('Additional drivers/NLA: '+owner.name)
    if ad.action:
        paths=set()
        for layer in ad.action.layers:
            for strip in layer.strips:
                bag=strip.channelbag(ad.action_slot)
                if bag:paths.update(c.data_path for c in bag.fcurves)
        if paths!=allowed.get(owner.as_pointer()):safe=False;reasons.append('Additional channels: '+owner.name)
for obj in scene.objects:
    if any(m.type in {'NODES','CLOTH','FLUID','SOFT_BODY','PARTICLE_SYSTEM','DYNAMIC_PAINT','WAVE','BUILD','MESH_SEQUENCE_CACHE','OCEAN'} for m in obj.modifiers):safe=False;reasons.append('Time-dependent modifier: '+obj.name)
    if obj.type=='MESH' and obj.data.shape_keys:safe=False;reasons.append('Shape keys: '+obj.name)
if scene.render.use_motion_blur or scene.cycles.use_animated_seed:safe=False;reasons.append('Motion blur or animated sampling seed')
if any(i.source in {'MOVIE','SEQUENCE'} for i in bpy.data.images):safe=False;reasons.append('Time-dependent image')

matrices=None;first={};unique=[];mapping=[]
for frame in range(1,241):
    scene.frame_set(frame);graph=bpy.context.evaluated_depsgraph_get()
    transforms={o.name:[list(row) for row in o.evaluated_get(graph).matrix_world] for o in scene.objects}
    if matrices is None:matrices=transforms
    if transforms!=matrices:safe=False;reasons.append('Evaluated transform changes')
    values=[]
    for record in records:
        energy=float(bpy.data.objects[record['light']].evaluated_get(graph).data.energy)
        optics=[float(bpy.data.materials[o['material']].evaluated_get(graph).node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value) for o in record['optics']]
        values.append([record['light'],energy,optics])
    key=json.dumps(values,separators=(',',':'))
    if key not in first:first[key]=frame;unique.append(frame)
    mapping.append({'native_frame':frame,'rendered_native_frame':first[key],'evaluated_light_optic_values':values})
if not safe:
    unique=list(range(1,241))
    for record in mapping:record['rendered_native_frame']=record['native_frame']
if args.plan_only:
    print('PREVIEW_PLAN',json.dumps({'native_sha256':sha,'frames':240,'actual_rendered_states':len(unique),'identical_state_reuse':safe,'fallback_reasons':sorted(set(reasons))}),flush=True)
    sys.exit(0)

os.environ['FRAMES']=','.join(map(str,unique));os.environ.setdefault('RES','320x212');os.environ.setdefault('SAMPLES','8')
sys.argv=['render_review.py','--',str(src),str(out),args.camera]
runpy.run_path(str(Path(__file__).with_name('render_review.py')),run_name='__main__')
render=json.loads((out/'RENDER_MANIFEST.json').read_text())
assert render['scene_sha256']==sha and render['frames']==unique
hashes={c['frame']:c['sha256'] for c in render['cameras']}
for record in mapping:
    frame=record['native_frame'];origin=record['rendered_native_frame']
    source=out/(args.camera+f'_F{origin:04d}.png');dest=out/(args.camera+f'_F{frame:04d}.png')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==hashes[origin]
    if frame!=origin:shutil.copyfile(source,dest)
    record['image']=dest.name;record['sha256']=hashes[origin]
video=out.with_suffix('.mp4')
subprocess.run([ffmpeg,'-y','-v','error','-framerate','24','-start_number','1','-i',str(out/(args.camera+'_F%04d.png')),'-frames:v','240','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(video)],check=True)
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,width,height','-show_entries','format=duration','-of','json',str(video)]))
assert probe['streams'][0]['nb_frames']=='240' and probe['streams'][0]['r_frame_rate']=='24/1' and float(probe['format']['duration'])==10
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
report={'schema':'fuel-native-loop-preview/1','native_sha256':sha,'recipe_sha256':build['recipe_sha256'],'camera':args.camera,'frames':240,'fps':24,'duration_seconds':10,'actual_rendered_frames':unique,'identical_state_reuse':safe,'reuse_fallback_reasons':sorted(set(reasons)),'encoding':probe,'video':str(video.relative_to(ROOT)),'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'frame_map':mapping,'scope':'Native timing preserved. Duplicate held evaluated states reuse unedited source PNG bytes. Preview resolution does not replace full craft views. Target-speed playback review and runtime are separate.'}
(out/'PREVIEW_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
print('NATIVE_LOOP_PREVIEW',len(unique),'rendered states; 240 frames, 24 fps, 10 seconds',flush=True)
