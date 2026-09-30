"""Purple-free palette for the whole scene (control-room redo).
Every unlinked colour in every material / node group / light / world in the violet-blue band (hue 225-345 deg) is remapped:
  blue-violet 225-262  -> steel blue-grey (hue 208, low saturation)
  violet / plum 262-345 -> olive-khaki (hue 68) for surfaces, cool neutral for lights and volumes
luminance is preserved, so the value structure of the scene does not change.  Also sets AgX 'Medium High Contrast'.
usage: python cr_pal.py -- <src.blend> <dst.blend>       (or import and call retune())"""
import bpy,sys,colorsys
LO,HI,SMIN=225.0,345.0,0.06
def _lum(c): return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def hsv(c): h,s,v=colorsys.rgb_to_hsv(*[max(0.0,min(1.0,x)) for x in c[:3]]); return h*360.0,s,v
def is_bad(c): h,s,v=hsv(c); return LO<=h<=HI and s>SMIN
def remap(c,kind="surface"):
    h,s,v=hsv(c); l0=_lum(c)
    if kind=="light": h2,s2=208.0,min(s,0.30)
    elif v<0.03:      h2,s2=40.0,0.22                   # near-black grime / ink: neutral warm black
    elif h<262:       h2,s2=208.0,min(0.35,s*0.5)
    else:             h2,s2=68.0,min(0.42,s*0.62)
    r,g,b=colorsys.hsv_to_rgb(h2/360.0,s2,v); l1=_lum((r,g,b))
    k=(l0/l1) if l1>1e-6 else 1.0
    return (r*k,g*k,b*k)
def _tree(nt,stats):
    for nd in nt.nodes:
        for i in nd.inputs:
            if i.type=='RGBA' and not i.is_linked and is_bad(i.default_value):
                a=i.default_value; i.default_value=(*remap(a,"light" if nd.type in('PRINCIPLED_VOLUME','VOLUME_SCATTER','EMISSION') or i.name=='Emission Color' else "surface"),a[3]); stats['mat']+=1
        if nd.type=='VALTORGB':
            for e in nd.color_ramp.elements:
                if is_bad(e.color): a=e.color; e.color=(*remap(a),a[3]); stats['mat']+=1
def retune():
    st={'mat':0,'light':0,'world':0}
    for m in bpy.data.materials:
        if m.node_tree: _tree(m.node_tree,st)
    for g in bpy.data.node_groups: _tree(g,st)
    for l in bpy.data.lights:
        if is_bad(l.color): l.color=remap(l.color,"light"); st['light']+=1
        if l.node_tree: _tree(l.node_tree,st)
    for w in bpy.data.worlds:
        if w.node_tree:
            for nd in w.node_tree.nodes:
                for i in nd.inputs:
                    if i.type=='RGBA' and not i.is_linked and is_bad(i.default_value):
                        i.default_value=(*remap(i.default_value,"light"),1.0); st['world']+=1
    vs=bpy.context.scene.view_settings; vs.view_transform='AgX'; vs.look='AgX - Medium High Contrast'; vs.exposure=0.0
    return st
if __name__=="__main__":
    A=sys.argv[sys.argv.index("--")+1:]; bpy.ops.wm.open_mainfile(filepath=A[0]); print("PAL",retune()); bpy.ops.wm.save_as_mainfile(filepath=A[1])
