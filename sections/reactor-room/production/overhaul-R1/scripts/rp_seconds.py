"""Make the hall's remaining frame-based drivers frame-rate independent.   usage: python rp_seconds.py -- <in.blend> <out.blend>   (run last)
The older hall drivers (state glow, pool glow, beacon pivots, station lamps) were written against the raw `frame` variable (tuned at 30 fps).  Each one is rewritten with the same rule the control
room uses (crk.to_seconds): `frame` -> (T*30) with T = scene time in seconds, and the scene fps / fps_base are added as driver variables, so the look is unchanged at 30 fps and identical in real time
at every other frame rate.  Drivers that already use seconds are left alone.  Verify with fps_independence_check.py -- <blend> --prefix ''."""
import bpy,sys,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
RAW=re.compile(r'\bframe\b(?!\*fb)'); n=0; blocks=[]
for coll in (bpy.data.objects,bpy.data.lights,bpy.data.cameras,bpy.data.scenes,bpy.data.meshes,bpy.data.curves,bpy.data.shape_keys): blocks+=list(coll)
for coll in (bpy.data.materials,bpy.data.worlds,bpy.data.node_groups):
    for i in coll:
        if getattr(i,'node_tree',None): blocks.append(i.node_tree)
        elif coll is bpy.data.node_groups: blocks.append(i)
for ib in blocks:
    ad=getattr(ib,'animation_data',None)
    if not ad: continue
    for fc in ad.drivers:
        d=fc.driver
        if d.type=='SCRIPTED' and RAW.search(d.expression):
            ex=crk.to_seconds(d.expression)
            if not any(v.name=='fps' for v in d.variables): crk._fps_vars(d)
            d.expression=ex; n+=1
print("rp_seconds: drivers converted to seconds:",n)
bpy.ops.wm.save_as_mainfile(filepath=DST)
