"""Put a slideshow (a folder of still images) on the control-room TV; the TV light follows the current slide.
usage: python cr_tv_slides.py -- <in.blend> <image folder> <out.blend> [--hold-seconds S]
 * every image (png / jpg / tif / exr, sorted by file name) is scaled to 640x360 and packed into ONE atlas image (a static texture, so it also survives an engine export)
 * the TV screen shows slide k = floor((T mod (N*hold_s)) / hold_s) where T = scene time in SECONDS (frame-rate independent); default hold = 20 / N s (whole show loops in 20 s)
 * the TV switches to clip mode (w_clip = 1, built-in cycle drivers removed) and the CR_TV props clip_r / clip_g / clip_b / clip_e are drivers of the slide index (one value per slide, seconds based)
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
FPS=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base; N=len(files); HOLD_S=float(A[A.index("--hold-seconds")+1]) if "--hold-seconds" in A else 20.0/N; HOLD=max(1,int(round(HOLD_S*FPS))); W,H=640,360      # hold in SECONDS; HOLD (frames at the scene fps) only places the light keys
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
import crk
crk._fps_vars(d); d.expression=f"floor(fmod(frame*fb/fps,{N*HOLD_S:.4f})/{HOLD_S:.4f})/{N}"
# clip mode + light track
def fcs(act):
    if hasattr(act,'fcurves'): return list(act.fcurves)
    return [fc_ for l in act.layers for s in l.strips for cb in s.channelbags for fc_ in cb.fcurves]
if E.animation_data and E.animation_data.action:
    for fc_ in fcs(E.animation_data.action):
        if any(k in fc_.data_path for k in("w_tel","w_bro","w_sta","w_bar","w_clip","clip_")):
            while len(fc_.keyframe_points): fc_.keyframe_points.remove(fc_.keyframe_points[0])
for k in("w_tel","w_bro","w_sta","w_bar"):
    try: E.driver_remove(f'["{k}"]')
    except Exception: pass
for k,v in (("w_tel",0.0),("w_bro",0.0),("w_sta",0.0),("w_bar",0.0)): E[k]=v
# light follows the slide: clip_* are drivers of the slide index (seconds based), not frame keys; long lists are chunked (255-char driver limit)
from crk import drv
for k_ in("clip_r","clip_g","clip_b","clip_e"):
    if k_ in E.keys():
        try: E.driver_remove(f'["{k_}"]')
        except Exception: pass
E["slide"]=0.0; drv(E,'["slide"]',None,f"floor(fmod(T,{N*HOLD_S:.4f})/{HOLD_S:.4f})",var_s=False)
for ci,k_ in enumerate(("clip_r","clip_g","clip_b","clip_e")):
    parts=["%.4f*(sl==%d)"%(t[1+ci],i) for i,t in enumerate(track)]; per=8; hn=[]
    for j in range(0,N,per):
        hp=f"{k_}_{j//per}"; E[hp]=0.0; hn.append(hp); drv(E,f'["{hp}"]',None,"+".join(parts[j:j+per]),var_s=False,extra=[("sl",E,'["slide"]')])
    drv(E,f'["{k_}"]',None,"+".join(f"h{i}" for i in range(len(hn))),var_s=False,extra=[(f"h{i}",E,f'["{hp}"]') for i,hp in enumerate(hn)])
E["w_clip"]=1.0
json.dump({"slides":files,"hold_seconds":HOLD_S,"loop_seconds":N*HOLD_S,"track_time_s":[[(t[0]-1)/FPS]+t[1:] for t in track],"track_frames_at_scene_fps":track},open(os.path.join(os.path.dirname(os.path.abspath(DST)),"tv_light_track.json"),"w"),indent=1)
bpy.ops.wm.save_as_mainfile(filepath=DST); print("TV slideshow installed:",N,"slides, hold",HOLD_S,"s")
