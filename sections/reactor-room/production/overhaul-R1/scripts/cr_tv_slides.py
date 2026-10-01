"""Put a slideshow (a folder of still images) on the control-room TV; the TV light follows the current slide.
usage: python cr_tv_slides.py -- <in.blend> <image folder> <out.blend> [--hold FRAMES]
 * every image (png / jpg / tif / exr, sorted by file name) is scaled to 640x360 and packed into ONE atlas image (a static texture, so it also survives an engine export)
 * the TV screen shows slide k = floor(((frame-1) mod (N*hold)) / hold); default hold = 480 / N frames (the whole show loops in 20 s at 24 fps)
 * the TV switches to clip mode (w_clip = 1, built-in cycle keys removed) and the CR_TV props clip_r / clip_g / clip_b / clip_e get one constant key per slide
   (hue = mean colour of the slide, e = relative brightness), so the area light in front of the TV changes colour and strength with each slide.
 * writes tv_light_track.json next to <out.blend>.
Go back to the built-in cycle by running cr_build.py again."""
import bpy,sys,os,json,math
import numpy as np
A=sys.argv[sys.argv.index("--")+1:]; SRC,DIR,DST=A[0],A[1],A[2]
bpy.ops.wm.open_mainfile(filepath=SRC)
E=bpy.data.objects["CR_TV"]; m=bpy.data.materials["CR tv screen"]; nt=m.node_tree; node=nt.nodes["TV CLIP"]
files=sorted(f for f in os.listdir(DIR) if f.lower().endswith((".png",".jpg",".jpeg",".tif",".tiff",".exr",".bmp",".webp")))
if not files: raise SystemExit("no images in "+DIR)
FPS=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base; N=len(files); HOLD=int(A[A.index("--hold")+1]) if "--hold" in A else max(12,int(round(20*FPS))//N); W,H=640,360      # default: the whole show loops in 20 s at the scene frame rate
def load(f):
    im=bpy.data.images.load(os.path.join(DIR,f)); w,h=im.size; px=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[...,:3]
    srgb=im.colorspace_settings.name=='sRGB'; bpy.data.images.remove(im)
    px=np.flipud(px)                                  # row 0 = top
    ys=(np.arange(H)*h/H).astype(int); xs=(np.arange(W)*w/W).astype(int); px=px[ys][:,xs]            # nearest resample to 16:9
    return px,srgb
atlas=np.zeros((N*H,W,3),dtype=np.float32); track=[]
for k,f in enumerate(files):
    px,srgb=load(f)
    if not srgb:                                       # linear file -> encode for the sRGB atlas
        px=np.where(px<=0.0031308,px*12.92,1.055*np.power(np.maximum(px,0),1/2.4)-0.055)
    atlas[(N-1-k)*H:(N-k)*H]=px                        # slide 0 at the top of the atlas
    lin=np.where(px<=0.04045,px/12.92,((px+0.055)/1.055)**2.4); mean=lin.reshape(-1,3).mean(0); lum=float(0.2126*mean[0]+0.7152*mean[1]+0.0722*mean[2])
    hue=mean/max(mean.max(),1e-4); hue=hue*0.85+0.15
    track.append([1+k*HOLD,float(hue[0]),float(hue[1]),float(hue[2]),float(min(1.8,max(0.12,lum*2.4+0.12)))])
# atlas image + mapping node driven by the frame
old=bpy.data.images.get("CR tv slides atlas")
if old: bpy.data.images.remove(old)
im=bpy.data.images.new("CR tv slides atlas",W,N*H,alpha=False); im.colorspace_settings.name='sRGB'
a4=np.concatenate([atlas,np.ones((N*H,W,1),dtype=np.float32)],2); im.pixels.foreach_set(np.flipud(a4).reshape(-1)); im.pack(); node.image=im; node.extension='EXTEND'
src=node.inputs[0].links[0].from_socket
for l in list(node.inputs[0].links): nt.links.remove(l)
mp=nt.nodes.new("ShaderNodeMapping"); mp.name="TV SLIDES MAP"; mp.location=(node.location.x-250,node.location.y)
mp.inputs['Scale'].default_value=(1.0,1.0/N,1.0); nt.links.new(src,mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],node.inputs[0])
fc=nt.driver_add('nodes["TV SLIDES MAP"].inputs["Location"].default_value',1); d=fc.driver; d.type='SCRIPTED'
d.expression=f"floor(fmod(frame-1,{N*HOLD})/{HOLD})/{N}"
# clip mode + light track (constant key per slide, cyclic)
def fcs(act):
    if hasattr(act,'fcurves'): return list(act.fcurves)
    return [fc_ for l in act.layers for s in l.strips for cb in s.channelbags for fc_ in cb.fcurves]
if E.animation_data and E.animation_data.action:
    for fc_ in fcs(E.animation_data.action):
        if any(k in fc_.data_path for k in("w_tel","w_bro","w_sta","w_bar","w_clip","clip_")):
            while len(fc_.keyframe_points): fc_.keyframe_points.remove(fc_.keyframe_points[0])
for k,v in (("w_tel",0.0),("w_bro",0.0),("w_sta",0.0),("w_bar",0.0),("w_clip",1.0)): E[k]=v; E.keyframe_insert(f'["{k}"]',frame=1)
for (f,r,g,b,e) in track+[[1+N*HOLD]+track[0][1:]]:
    E["clip_r"],E["clip_g"],E["clip_b"],E["clip_e"]=r,g,b,e
    for k in("clip_r","clip_g","clip_b","clip_e"): E.keyframe_insert(f'["{k}"]',frame=f)
for fc_ in fcs(E.animation_data.action):
    if "clip_" in fc_.data_path:
        for kp in fc_.keyframe_points: kp.interpolation='CONSTANT'
        if not any(mo.type=='CYCLES' for mo in fc_.modifiers): fc_.modifiers.new('CYCLES')
json.dump({"slides":files,"hold_frames":HOLD,"track":track},open(os.path.join(os.path.dirname(os.path.abspath(DST)),"tv_light_track.json"),"w"),indent=1)
bpy.ops.wm.save_as_mainfile(filepath=DST); print("TV slideshow installed:",N,"slides, hold",HOLD,"frames")
