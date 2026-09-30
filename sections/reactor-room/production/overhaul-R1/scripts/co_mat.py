"""Materials, drivers and small helpers for the 1990s control room overhaul."""
import bpy,math,random,numpy as np
from r2lib import r2mat
STATE=None      # REACTOR_STATE empty, set by the caller
def new_mat(name):
    m=bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(name); m.use_nodes=True; return m
def drv(datablock_tree,path,idx,expr,var_s=True):
    fc=datablock_tree.driver_add(path,idx) if idx is not None else datablock_tree.driver_add(path)
    d=fc.driver; d.type='SCRIPTED'
    if var_s:
        v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=STATE; v.targets[0].data_path='["stability"]'
    d.expression=expr; return fc
def emit_mat(name,rgb,strength,expr=None):
    m=new_mat(name); nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value=(*[c*0.15 for c in rgb],1); b.inputs['Emission Color'].default_value=(*rgb,1); b.inputs['Emission Strength'].default_value=strength
    b.inputs['Roughness'].default_value=0.4
    if expr: drv(nt,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,expr,var_s=False)
    return m
def stab_expr(i): return ("min(1,2*(1-s)+0.24)","0.03+0.92*s","0.20*s")[i]
PHASE="min(1,max(0,0.5+1.3*sin(frame*0.0131)))"      # 0 = reactor telemetry, 1 = propaganda broadcast (about 480 frame cycle)
def make_materials():
    M={}
    M["PLASTIC"]=r2mat("R2 90s plastic",(0.20,0.185,0.15),0.5,edge=(0.30,0.28,0.22),grime=0.3,noise=(2.5,0),mottle=0.3)
    M["PLASTICD"]=r2mat("R2 90s plastic dark",(0.05,0.05,0.055),0.42,edge=(0.12,0.12,0.13),grime=0.2,noise=(2.5,0),mottle=0.2)
    M["KEY"]=r2mat("R2 90s keycap",(0.15,0.14,0.115),0.5,edge=None,grime=0.1,noise=(2.5,0),mottle=0.2)
    M["RACK"]=r2mat("R2 rack steel",(0.13,0.13,0.14),0.42,edge=(0.28,0.28,0.30),grime=0.25,noise=(2.5,0),metal=0.6,mottle=0.25)
    M["ACW"]=r2mat("R2 aircon casing",(0.30,0.29,0.26),0.5,edge=(0.36,0.34,0.30),grime=0.35,noise=(2.5,0),mottle=0.3)
    M["CORK"]=r2mat("R2 cork",(0.22,0.12,0.055),0.85,edge=None,grime=0.1,noise=(6.0,0),mottle=0.7)
    M["P_RED"]=r2mat("R2 poster red",(0.28,0.035,0.03),0.8,edge=None,grime=0.0,noise=(3,0),mottle=0.25)
    M["P_GOLD"]=r2mat("R2 poster gold",(0.42,0.27,0.04),0.8,edge=None,grime=0.0,noise=(3,0),mottle=0.25)
    M["P_NAVY"]=r2mat("R2 poster navy",(0.035,0.05,0.13),0.8,edge=None,grime=0.0,noise=(3,0),mottle=0.25)
    M["P_INK"]=r2mat("R2 poster ink",(0.02,0.02,0.025),0.8,edge=None,grime=0.0,noise=(3,0),mottle=0.15)
    M["PAPER"]=bpy.data.materials["R2 paper"]; M["DESK"]=bpy.data.materials["R2 desk"]; M["IRON"]=bpy.data.materials["R2 iron"]; M["TRIM"]=bpy.data.materials["R2 trim rust"]
    M["INK"]=bpy.data.materials["R2 ink"]; M["FAB"]=bpy.data.materials["R2 fabric"]; M["CABLE"]=bpy.data.materials["R2 cable"]; M["GLASS"]=bpy.data.materials["observation_glass"]
    M["CONE"]=bpy.data.materials["R2 cone"]; M["BIND"]=bpy.data.materials["R2 binder a"]; M["DADO"]=bpy.data.materials["R2 dado navy"]
    # emissives
    M["SCR_G"]=emit_mat("R2 crt green",(0.12,1.0,0.22),2.6,"2.6*(0.92+0.08*sin(frame*1.7))")
    M["SCR_A"]=emit_mat("R2 crt amber",(1.0,0.55,0.07),2.4,"2.4*(0.92+0.08*sin(frame*1.3+2))")
    M["SCRBG_G"]=emit_mat("R2 crt glass green",(0.05,0.5,0.10),0.35,"0.35*(0.9+0.1*sin(frame*1.7))")
    M["SCRBG_A"]=emit_mat("R2 crt glass amber",(0.5,0.25,0.03),0.35,"0.35*(0.9+0.1*sin(frame*1.3+2))")
    M["CEIL"]=emit_mat("R2 ceiling warm",(1.0,0.60,0.30),5.0)
    M["CEIL_F"]=emit_mat("R2 ceiling warm flicker",(1.0,0.60,0.30),5.0,"5.0*(1-0.75*max(0,sin(frame*1.9)*sin(frame*0.37)-0.55)*2.2)")
    M["LAMP"]=emit_mat("R2 desk lamp bulb",(1.0,0.66,0.32),8.0)
    M["LED_W"]=emit_mat("R2 led white",(1.0,0.9,0.75),3.0)
    rnd=random.Random(5)
    for c,(rgb) in (("G",(0.1,1.0,0.15)),("A",(1.0,0.55,0.05)),("R",(1.0,0.06,0.04))):
        for k in range(4):
            a,b_,p,q=rnd.uniform(0.35,1.3),rnd.uniform(0.11,0.5),rnd.uniform(0,6.3),rnd.uniform(0,6.3)
            M[f"LED_{c}{k}"]=emit_mat(f"R2 led {c}{k}",rgb,4.0,f"4.0*max(0.04,min(1.0,(sin(frame*{a:.3f}+{p:.2f})+sin(frame*{b_:.3f}+{q:.2f}))*3.2-1.6))")
    return M
# ---------------- TV: content images + material + light
def _fill(a,x0,y0,x1,y1,v):
    h,w=a.shape[:2]; x0,x1=max(0,int(x0)),min(w,int(x1)); y0,y1=max(0,int(y0)),min(h,int(y1))
    if x1>x0 and y1>y0: a[y0:y1,x0:x1]=v
def tv_images():
    W,H=192,108
    A=np.zeros((H,W),dtype=np.float32)                       # telemetry mask (row 0 = top)
    _fill(A,0,0,W,9,1.0); _fill(A,0,H-8,W,H,0.55)             # title bar and ticker
    for i in range(14): _fill(A,6+i*6,3,9+i*6,6,0.0)          # title "text" gaps
    for x in range(8,W-8,16): _fill(A,x,12,x+1,H-10,0.16)      # grid
    for y in range(16,H-10,14): _fill(A,8,y,W-8,y+1,0.16)
    for k,(bx,hgt) in enumerate(((16,0.72),(40,0.60))):        # bank A / B bars
        _fill(A,bx,H-14-int(70*hgt),bx+16,H-14,0.9); _fill(A,bx-1,H-14,bx+17,H-12,1.0)
        for t in range(0,70,10): _fill(A,bx+16,H-14-t,bx+20,H-13-t,0.6)
    for i in range(6):                                           # label rows
        _fill(A,70,16+i*9,70+18+((i*37)%30),19+i*9,0.8)
    xs=np.arange(78,W-10)
    ys=(H*0.55+14*np.sin(xs*0.16)+6*np.sin(xs*0.53)).astype(int)                                  # trace
    for x,y in zip(xs,ys): _fill(A,x,y-1,x+1,y+1,1.0)
    for x in range(78,W-10,4): _fill(A,x,H-28,x+2,H-28-int(10+8*abs(math.sin(x*0.3))),0.7)      # histogram
    rgbA=np.zeros((H,W,4),dtype=np.float32); rgbA[...,0]=rgbA[...,1]=rgbA[...,2]=A; rgbA[...,3]=1
    B=np.zeros((H,W,4),dtype=np.float32); B[...,3]=1
    yy=np.linspace(0,1,H)[:,None]
    B[...,0]=0.55+0.25*yy; B[...,1]=0.06+0.08*yy; B[...,2]=0.05+0.03*yy         # red field
    cx,cy=W*0.5,H*0.46
    Y,X=np.mgrid[0:H,0:W]
    r=np.hypot(X-cx,(Y-cy)*1.0); ang=np.arctan2(Y-cy,X-cx)
    rays=(np.sin(ang*14)>0.2)&(r>24)&(r<70)
    B[rays,0]=0.85; B[rays,1]=0.55; B[rays,2]=0.10
    sun=r<22; B[sun,0]=1.0; B[sun,1]=0.78; B[sun,2]=0.25
    _fill(B,0,H-24,W,H-8,0.0); B[H-24:H-8,:,0]=0.05; B[H-24:H-8,:,1]=0.05; B[H-24:H-8,:,2]=0.09
    for i in range(18): B[H-20:H-14,10+i*10:16+i*10,:3]=(0.95,0.8,0.5)
    for k in range(4):                                                          # silhouettes of workers in helmets
        x0=20+k*44; B[H-46:H-24,x0:x0+16,:3]=(0.03,0.03,0.07); Y2,X2=np.mgrid[0:H,0:W]; hd=np.hypot(X2-(x0+8),Y2-(H-50))<6; B[hd,:3]=(0.03,0.03,0.07)
    imgs=[]
    for name,arr,cs in (("R2 tv telemetry",rgbA,"Non-Color"),("R2 tv broadcast",B,"sRGB")):
        im=bpy.data.images.get(name)
        if im: bpy.data.images.remove(im)
        im=bpy.data.images.new(name,W,H,alpha=False); im.colorspace_settings.name=cs
        flat=np.flipud(arr).reshape(-1)          # Blender pixel rows run bottom-up
        im.pixels.foreach_set(flat); im.pack(); imgs.append(im)
    return imgs
def tv_material(imgA,imgB):
    m=new_mat("R2 tv screen"); nt=m.node_tree; nt.nodes.clear()
    N=lambda t,x,y:(lambda n:(setattr(n,'location',(x,y)),n)[1])(nt.nodes.new(t))
    out=N("ShaderNodeOutputMaterial",1500,0); em=N("ShaderNodeEmission",1250,0); nt.links.new(em.outputs[0],out.inputs[0])
    uv=N("ShaderNodeTexCoord",-800,0)
    ta=N("ShaderNodeTexImage",-500,200); ta.image=imgA; ta.interpolation='Closest'; ta.extension='EXTEND'; nt.links.new(uv.outputs['UV'],ta.inputs[0])
    tb=N("ShaderNodeTexImage",-500,-200); tb.image=imgB; tb.interpolation='Closest'; tb.extension='EXTEND'; nt.links.new(uv.outputs['UV'],tb.inputs[0])
    # stability colour (driven)
    sc=[]
    for i in range(3):
        v=N("ShaderNodeValue",-500,500-i*80); drv(nt,f'nodes["{v.name}"].outputs[0].default_value',None,stab_expr(i)); sc.append(v)
    comb=N("ShaderNodeCombineColor",-250,450)
    for i in range(3): nt.links.new(sc[i].outputs[0],comb.inputs[i])
    mulA=N("ShaderNodeMix",0,250); mulA.data_type='RGBA'; mulA.blend_type='MULTIPLY'; mulA.inputs[0].default_value=1.0
    nt.links.new(ta.outputs['Color'],mulA.inputs[6]); nt.links.new(comb.outputs[0],mulA.inputs[7])
    ph=N("ShaderNodeValue",0,-100); drv(nt,f'nodes["{ph.name}"].outputs[0].default_value',None,PHASE,var_s=False)
    mix=N("ShaderNodeMix",300,100); mix.data_type='RGBA'
    nt.links.new(ph.outputs[0],mix.inputs[0]); nt.links.new(mulA.outputs[2],mix.inputs[6]); nt.links.new(tb.outputs['Color'],mix.inputs[7])
    # scanlines + gentle brightness flicker
    sep=N("ShaderNodeSeparateXYZ",-500,-500); nt.links.new(uv.outputs['UV'],sep.inputs[0])
    mth=N("ShaderNodeMath",-300,-500); mth.operation='MULTIPLY'; mth.inputs[1].default_value=2*math.pi*108; nt.links.new(sep.outputs['Y'],mth.inputs[0])
    sn=N("ShaderNodeMath",-120,-500); sn.operation='SINE'; nt.links.new(mth.outputs[0],sn.inputs[0])
    sl=N("ShaderNodeMath",60,-500); sl.operation='MULTIPLY_ADD'; sl.inputs[1].default_value=0.10; sl.inputs[2].default_value=0.90; nt.links.new(sn.outputs[0],sl.inputs[0])
    scan=N("ShaderNodeMix",700,0); scan.data_type='RGBA'; scan.blend_type='MULTIPLY'; scan.inputs[0].default_value=1.0
    cs=N("ShaderNodeCombineColor",300,-500)
    for i in range(3): nt.links.new(sl.outputs[0],cs.inputs[i])
    nt.links.new(mix.outputs[2],scan.inputs[6]); nt.links.new(cs.outputs[0],scan.inputs[7])
    nt.links.new(scan.outputs[2],em.inputs['Color'])
    drv(nt,f'nodes["{em.name}"].inputs["Strength"].default_value',None,"2.4*(0.93+0.07*sin(frame*2.3)*sin(frame*0.41))",var_s=False)
    return m
def tv_light(loc,size=(1.2,0.7),energy=70):
    ld=bpy.data.lights.new("R2 tv light",'AREA'); ld.shape='RECTANGLE'; ld.size=size[0]; ld.size_y=size[1]; ld.energy=energy
    lo=bpy.data.objects.new("R2 tv light",ld); lo.location=loc; lo.rotation_euler=(math.pi/2,0,0); bpy.context.scene.collection.objects.link(lo)
    B=(1.0,0.55,0.30)
    for i in range(3):
        drv(ld,'color',i,f"(1-{PHASE})*({stab_expr(i)})*0.95+{PHASE}*{B[i]}")
    drv(ld,'energy',None,f"{energy}*(0.82+0.18*sin(frame*2.3)*sin(frame*0.41)+0.25*{PHASE}*(1-{PHASE}))",var_s=True)
    return lo
