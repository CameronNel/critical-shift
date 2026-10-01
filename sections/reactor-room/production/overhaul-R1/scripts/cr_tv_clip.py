"""Put the user's recurring clip on the control-room TV and re-bake the light it casts.
usage: python cr_tv_clip.py -- <in.blend> <clip.(mp4|mov|webm|png-sequence-first-frame)> <out.blend> [--frames N]
 * loads the clip into image node 'TV CLIP' (material 'CR tv screen'), looping, and switches the TV to clip mode (w_clip = 1, built-in cycle off)
 * samples every frame of the clip at 32x18 through a temporary sequencer scene, and keyframes the CR_TV empty props clip_r/g/b/e
   (hue = mean colour of the frame, e = relative brightness) -> the TV area light follows the clip exactly.
 * writes tv_light_track.json next to <out.blend> so the track can be inspected / edited.
To go back to the built-in telemetry / broadcast / static cycle: set w_clip to 0 and restore the cycle by running cr_build.py again."""
import bpy,sys,os,json,tempfile,math
import numpy as np
A=sys.argv[sys.argv.index("--")+1:]; SRC,CLIP,DST=A[0],A[1],A[2]
N=int(A[A.index("--frames")+1]) if "--frames" in A else None
bpy.ops.wm.open_mainfile(filepath=SRC)
FPS=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
print("scene fps %.3f: Blender plays an image sequence / movie one frame per scene frame, so a 20 s clip should be %d frames at %.0f fps (convert the clip to the scene fps first, or the speed will be wrong)"%(FPS,round(20*FPS),FPS))
E=bpy.data.objects["CR_TV"]; m=bpy.data.materials["CR tv screen"]; node=m.node_tree.nodes["TV CLIP"]
import re
EXT=os.path.splitext(CLIP)[1].lower(); SEQ=EXT in(".png",".jpg",".jpeg",".tif",".tiff",".exr")
if SEQ:
    d=os.path.dirname(os.path.abspath(CLIP)); files=sorted(f for f in os.listdir(d) if f.lower().endswith(EXT)); FIRST=int(re.search(r'(\d+)\.[^.]+$',files[0]).group(1)); img=bpy.data.images.load(os.path.join(d,files[0])); img.source='SEQUENCE'
else:
    img=bpy.data.images.load(CLIP); img.source='MOVIE'
node.image=img; iu=node.image_user; n=N or (len(files) if SEQ else max(1,int(getattr(img,"frame_duration",480)) or 480)); iu.frame_duration=n; iu.frame_start=1; iu.use_cyclic=True; iu.use_auto_refresh=True
if SEQ: iu.frame_offset=FIRST-1
# --- sample the clip: temporary scene, one emissive plane showing the clip frame f (image_user.frame_offset), rendered at 32x18
sc=bpy.data.scenes.new("_clip"); sc.render.resolution_x,sc.render.resolution_y=32,18; sc.render.resolution_percentage=100; sc.render.engine='CYCLES'; sc.cycles.samples=1; sc.cycles.use_denoising=False; sc.cycles.device='CPU'
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGB'; sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
w=bpy.data.worlds.new("_cw"); w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(0,0,0,1); sc.world=w
cd=bpy.data.cameras.new("_cc"); cd.type='ORTHO'; cd.ortho_scale=2.0; co=bpy.data.objects.new("_cc",cd); sc.collection.objects.link(co); co.location=(0,0,5); sc.camera=co
me=bpy.data.meshes.new("_cp"); me.from_pydata([(-1,-0.5625,0),(1,-0.5625,0),(1,0.5625,0),(-1,0.5625,0)],[],[(0,1,2,3)]); uv=me.uv_layers.new(name="UVMap")
for lo,u in zip(me.loops,((0,0),(1,0),(1,1),(0,1))): uv.data[lo.index].uv=u
po=bpy.data.objects.new("_cp",me); sc.collection.objects.link(po)
pm=bpy.data.materials.new("_cm"); pm.use_nodes=True; nt=pm.node_tree; nt.nodes.clear()
o_=nt.nodes.new("ShaderNodeOutputMaterial"); e_=nt.nodes.new("ShaderNodeEmission"); tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=img; tx.interpolation='Closest'
nt.links.new(tx.outputs[0],e_.inputs[0]); nt.links.new(e_.outputs[0],o_.inputs[0]); me.materials.append(pm)
tx.image_user.frame_duration=n+1; tx.image_user.frame_start=1; tx.image_user.use_cyclic=False; tx.image_user.use_auto_refresh=True
tmp=tempfile.mkdtemp(); track=[]
for f in range(1,n+1):
    tx.image_user.frame_offset=(FIRST-1 if SEQ else 0)+f-1; p=os.path.join(tmp,"f%04d.png"%f); sc.render.filepath=p; bpy.ops.render.render(write_still=True,scene=sc.name)
    im=bpy.data.images.load(p); im.colorspace_settings.name='Non-Color'
    px=np.array(im.pixels[:],dtype=np.float32).reshape(-1,4)[:,:3]; bpy.data.images.remove(im)
    lin=np.where(px<=0.04045,px/12.92,((px+0.055)/1.055)**2.4); mean=lin.mean(0); lum=float(0.2126*mean[0]+0.7152*mean[1]+0.0722*mean[2])
    hue=mean/max(mean.max(),1e-4); hue=hue*0.85+0.15                                  # keep a little white so dark frames still read as light
    track.append([f,float(hue[0]),float(hue[1]),float(hue[2]),float(min(1.8,max(0.12,lum*2.4+0.12)))])
bpy.data.scenes.remove(sc)
# --- keyframes: clip mode (built-in cycle keys are cleared, w_clip = 1)
def fcs(act):
    if hasattr(act,'fcurves'): return list(act.fcurves)
    return [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
if E.animation_data and E.animation_data.action:
    for fc in fcs(E.animation_data.action):
        if any(k in fc.data_path for k in("w_tel","w_bro","w_sta","w_bar")):
            while len(fc.keyframe_points): fc.keyframe_points.remove(fc.keyframe_points[0])
for k,v in (("w_tel",0.0),("w_bro",0.0),("w_sta",0.0),("w_bar",0.0),("w_clip",1.0)):
    E[k]=v; E.keyframe_insert(f'["{k}"]',frame=1)
for (f,r,g,b,e) in track:
    E["clip_r"],E["clip_g"],E["clip_b"],E["clip_e"]=r,g,b,e
    for k in("clip_r","clip_g","clip_b","clip_e"): E.keyframe_insert(f'["{k}"]',frame=f)
for fc in fcs(E.animation_data.action):
    if "clip_" in fc.data_path and not any(mo.type=='CYCLES' for mo in fc.modifiers): fc.modifiers.new('CYCLES')
bpy.context.scene.frame_start,bpy.context.scene.frame_end=1,n
json.dump({"clip":os.path.basename(CLIP),"frames":n,"track":track},open(os.path.join(os.path.dirname(os.path.abspath(DST)),"tv_light_track.json"),"w"))
bpy.ops.wm.save_as_mainfile(filepath=DST); print("TV clip installed:",n,"frames")
