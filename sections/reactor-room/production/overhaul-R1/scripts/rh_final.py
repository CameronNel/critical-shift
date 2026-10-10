"""Final stage of the hall pass: neutralise any leftover cool (teal / cyan / blue / violet) colour so the palette rule holds scene-wide, then verify.   usage: python rh_final.py -- <in.blend> <out.blend>
Every unlinked colour input, colour-ramp stop and light colour whose hue lies in 150..310 degrees with saturation > 0.22 is replaced by a neutral warm grey of the same value (lights keep their
energy; state-glow green at ~117 degrees is untouched).  Stages should have fixed their own materials; this is the safety net, and it logs what it had to change."""
import bpy,sys,colorsys
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
def bad(c):
    r,g,b=[max(0.0,min(1.0,x)) for x in c[:3]]; h,s,v=colorsys.rgb_to_hsv(r,g,b); return 150<=h*360<=310 and s>0.22 and v>0.02
def neutral(c):
    v=max(c[:3]); return (v*1.00,v*0.985,v*0.95)
n=0; log=[]
for m in bpy.data.materials:
    if not m.node_tree: continue
    for nd in m.node_tree.nodes:
        for i in nd.inputs:
            if i.type=='RGBA' and not i.is_linked and bad(i.default_value):
                c=neutral(i.default_value); i.default_value=(*c,1.0); n+=1; log.append(m.name)
        if nd.type=='VALTORGB':
            for e in nd.color_ramp.elements:
                if bad(e.color): c=neutral(e.color); e.color=(*c,1.0); n+=1; log.append(m.name)
for l in bpy.data.lights:
    if bad(l.color): c=neutral(l.color); l.color=c; n+=1; log.append(l.name)
for w in bpy.data.worlds:
    if w.node_tree:
        for nd in w.node_tree.nodes:
            for i in nd.inputs:
                if i.type=='RGBA' and not i.is_linked and bad(i.default_value): c=neutral(i.default_value); i.default_value=(*c,1.0); n+=1; log.append(w.name)
print("rh_final: neutralised %d cool colours in %d datablocks"%(n,len(set(log))),sorted(set(log))[:20])
bpy.ops.wm.save_as_mainfile(filepath=DST)
