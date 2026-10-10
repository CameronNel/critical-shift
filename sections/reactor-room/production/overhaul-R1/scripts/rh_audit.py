"""Palette audit for the hall pass: no teal / cyan / aqua / blue / plum / purple anywhere.   usage: python rh_audit.py -- <blend> [--all]
Flags every unlinked colour input of every material node, colour ramp stop, light colour and world colour whose hue is between 150 and 310 degrees (teal, cyan, blue, violet, plum) with
saturation > 0.22 and value > 0.02.  Green (the state glow, ~117 deg), yellow, orange, red, white, greys and browns pass.  Control room / lift / rod-bank objects are included only with --all.
Prints offenders and 'AUDIT PASS' / 'AUDIT FAIL (n)'."""
import bpy,sys,colorsys,collections
A=sys.argv[sys.argv.index("--")+1:]; ALL="--all" in A
bpy.ops.wm.open_mainfile(filepath=A[0])
def bad(c):
    r,g,b=[max(0.0,min(1.0,x)) for x in c[:3]]; h,s,v=colorsys.rgb_to_hsv(r,g,b); return 150<=h*360<=310 and s>0.22 and v>0.02
used=collections.defaultdict(set)
for o in bpy.data.objects:
    if o.type=='MESH':
        for m in o.data.materials:
            if m: used[m.name].add(o.name)
off=[]
for m in bpy.data.materials:
    if not m.node_tree or m.name not in used: continue
    if not ALL and all(n.startswith(("CR ","COL ")) for n in used[m.name]): continue
    for nd in m.node_tree.nodes:
        for i in nd.inputs:
            if i.type=='RGBA' and not i.is_linked and bad(i.default_value): off.append(("mat",m.name,nd.name,i.name,tuple(round(x,2) for x in i.default_value[:3])))
        if nd.type=='VALTORGB':
            for e in nd.color_ramp.elements:
                if bad(e.color): off.append(("ramp",m.name,nd.name,"",tuple(round(x,2) for x in e.color[:3])))
for l in bpy.data.lights:
    if bad(l.color): off.append(("light",l.name,"","",tuple(round(x,2) for x in l.color[:3])))
for w in bpy.data.worlds:
    if w.node_tree:
        for nd in w.node_tree.nodes:
            for i in nd.inputs:
                if i.type=='RGBA' and not i.is_linked and bad(i.default_value): off.append(("world",w.name,nd.name,i.name,tuple(round(x,2) for x in i.default_value[:3])))
for o in off[:60]: print(o)
print("AUDIT PASS" if not off else "AUDIT FAIL (%d)"%len(off))
