"""Wall TV: content cycle (20 SECONDS of scene time, frame-rate independent) and the light it casts.
An empty 'CR_TV' carries the time-driven custom props  w_tel w_bro w_sta w_bar w_clip  (state weights, sum 1)  and  clip_r clip_g clip_b clip_e
(colour/intensity track of the custom clip).  The screen shader and the area light both read those props, so the light always matches the picture.
 telemetry = stability coloured (live driver on REACTOR_STATE.stability)   broadcast / static / NO SIGNAL bars = built in
 clip slot = image node 'TV CLIP' (empty placeholder).  cr_tv_clip.py loads a clip into it and re-bakes clip_* from the clip's frames."""
import bpy,math
import numpy as np
import crk,crt
from crk import _new,_n,drv,new_image
SCHED=[  # (frame, tel, bro, sta, bar)  linear crossfades, cyclic
 (1,1,0,0,0),(150,1,0,0,0),(158,0,0,1,0),(170,0,0,1,0),(180,0,1,0,0),(330,0,1,0,0),(337,0,0,1,0),(347,0,0,1,0),(355,0,0,0,1),(410,0,0,0,1),(416,0,0,1,0),(426,0,0,1,0),(434,1,0,0,0),(481,1,0,0,0)]
CYCLE_S=20.0                                        # the TV show loops every 20 SECONDS of scene time (any frame rate)
SCHED_S=[((f-1)/24.0,*w) for (f,*w) in SCHED]       # SCHED was authored in 24-fps frames; the driver schedule below is in seconds
def ramp_terms(points):
    """exact piecewise-linear function of the cycle phase p (seconds) through (t, v) points: v0 + sum of clamped ramps"""
    return points[0][1],["(%+g)*max(0,min(1,(p-%.3f)/%.3f))"%(vb-va,ta,tb-ta) for (ta,va),(tb,vb) in zip(points[:-1],points[1:]) if abs(vb-va)>1e-9]
def drive_ramp(e,name,points,per=5):
    """Blender caps a driver expression at ~255 chars, so long schedules are split over helper props <name>_k that the final prop sums"""
    v0,terms=ramp_terms(points); chunks=[terms[i:i+per] for i in range(0,len(terms),per)] or [[]]
    ph=("p",e,'["t_s"]'); names=[]
    for k,ch in enumerate(chunks):
        nm=f"{name}_{k}"; e[nm]=0.0; names.append(nm)
        drv(e,f'["{nm}"]',None,"+".join(ch) or "0",var_s=False,extra=[ph])
    vs=[(f"q{k}",e,f'["{nm}"]') for k,nm in enumerate(names)]
    drv(e,f'["{name}"]',None,"%.3f+"%v0+"+".join(v[0] for v in vs),var_s=False,extra=vs)
def make_empty(coll):
    """the empty CR_TV carries the state weights as TIME-driven custom properties (w_tel w_bro w_sta w_bar) and the clip track (w_clip, clip_r/g/b/e)"""
    e=bpy.data.objects.new("CR_TV",None); e.empty_display_type='PLAIN_AXES'; e.empty_display_size=0.1; coll.objects.link(e)
    for n in ("w_tel","w_bro","w_sta","w_bar","w_clip","clip_r","clip_g","clip_b","clip_e"): e[n]=0.0
    e["w_tel"]=1.0; e["clip_r"]=0.6; e["clip_g"]=0.6; e["clip_b"]=0.6; e["clip_e"]=1.0
    e["t_s"]=0.0; drv(e,'["t_s"]',None,"fmod(T,%.1f)"%CYCLE_S,var_s=False)      # cycle phase in seconds
    for idx,n in enumerate(("w_tel","w_bro","w_sta","w_bar")):
        drive_ramp(e,n,[(ts,w[idx]) for (ts,*w) in SCHED_S])
    return e
def _sum_vec(nt,items,x,y):
    """items: list of (color_socket, scalar_socket) -> weighted sum socket"""
    acc=None
    for k,(col,w) in enumerate(items):
        v=_n(nt,"ShaderNodeVectorMath",x,y-k*120); v.operation='SCALE'; nt.links.new(col,v.inputs[0]); nt.links.new(w,v.inputs[3])
        if acc is None: acc=v.outputs[0]
        else:
            a=_n(nt,"ShaderNodeVectorMath",x+200,y-k*120); a.operation='ADD'; nt.links.new(acc,a.inputs[0]); nt.links.new(v.outputs[0],a.inputs[1]); acc=a.outputs[0]
    return acc
def screen_material(E):
    m=_new("CR tv screen"); nt=m.node_tree
    out=_n(nt,"ShaderNodeOutputMaterial",2000,0); b=_n(nt,"ShaderNodeBsdfPrincipled",1700,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Base Color'].default_value=(0.006,0.006,0.006,1); b.inputs['Roughness'].default_value=0.08; b.inputs['Coat Weight'].default_value=0.5; b.inputs['Coat Roughness'].default_value=0.04
    uv=_n(nt,"ShaderNodeTexCoord",-900,0)
    def img(name,arr,cs,y):
        t=_n(nt,"ShaderNodeTexImage",-500,y); t.image=new_image(name,arr,cs); t.extension='EXTEND'; t.interpolation='Linear'; nt.links.new(uv.outputs['UV'],t.inputs[0]); return t
    tel=crt.tv_telemetry(); telrgb=np.repeat(tel[...,None],3,2)
    ti=img("CR tv telemetry",telrgb,'Non-Color',500); bi=img("CR tv broadcast",crt.tv_broadcast(),'sRGB',200); ni=img("CR tv bars",crt.tv_bars(),'sRGB',-100)
    ci=_n(nt,"ShaderNodeTexImage",-500,-400); ci.name="TV CLIP"; ci.label="TV CLIP (custom 20 s clip slot)"; ci.image=new_image("CR tv clip slot",np.zeros((9,16,3),dtype=np.float32)+0.02,'sRGB'); ci.extension='EXTEND'; nt.links.new(uv.outputs['UV'],ci.inputs[0])
    # stability colour (driven)
    sv=[]
    for i in range(3):
        v=_n(nt,"ShaderNodeValue",-500,900-i*90); drv(nt,f'nodes["{v.name}"].outputs[0].default_value',None,crk.stab_expr(i)); sv.append(v)
    comb=_n(nt,"ShaderNodeCombineColor",-250,850)
    for i in range(3): nt.links.new(sv[i].outputs[0],comb.inputs[i])
    tm=_n(nt,"ShaderNodeVectorMath",0,700); tm.operation='MULTIPLY'; nt.links.new(ti.outputs['Color'],tm.inputs[0]); nt.links.new(comb.outputs[0],tm.inputs[1])
    # static
    nz=_n(nt,"ShaderNodeTexNoise",-500,-750); nz.noise_dimensions='4D'; nz.inputs['Scale'].default_value=260.0; nz.inputs['Detail'].default_value=0.0
    drv(nt,f'nodes["{nz.name}"].inputs["W"].default_value',None,"frame*37.13",var_s=False)
    mul=_n(nt,"ShaderNodeVectorMath",-300,-750); mul.operation='MULTIPLY'; 
    ux=_n(nt,"ShaderNodeMapping",-700,-750); nt.links.new(uv.outputs['UV'],ux.inputs[0]); ux.inputs['Scale'].default_value=(1.0,1.0,1.0); nt.links.new(ux.outputs[0],nz.inputs['Vector'])
    mr=_n(nt,"ShaderNodeMapRange",-200,-750); mr.inputs['From Min'].default_value=0.30; mr.inputs['From Max'].default_value=0.70; nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    sc=_n(nt,"ShaderNodeCombineColor",0,-750)
    for i,k in enumerate((0.92,0.96,1.0)):
        mk=_n(nt,"ShaderNodeMath",-40,-650-i*60); mk.operation='MULTIPLY'; mk.inputs[1].default_value=k; nt.links.new(mr.outputs['Result'],mk.inputs[0]); nt.links.new(mk.outputs[0],sc.inputs[i])
    # weights from the empty
    W={}
    for n in ("w_tel","w_bro","w_sta","w_bar","w_clip"):
        v=_n(nt,"ShaderNodeValue",300,-1000-len(W)*70); drv(nt,f'nodes["{v.name}"].outputs[0].default_value',None,"w",var_s=False,extra=[("w",E,f'["{n}"]')]); W[n]=v.outputs[0]
    tot=_sum_vec(nt,[(tm.outputs[0],W["w_tel"]),(bi.outputs['Color'],W["w_bro"]),(sc.outputs['Color'],W["w_sta"]),(ni.outputs['Color'],W["w_bar"]),(ci.outputs['Color'],W["w_clip"])],700,300)
    nt.links.new(tot,b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=1.7
    drv(nt,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,"1.7*(0.96+0.04*sin(frame*3.1))",var_s=False)
    return m
def make_light(coll,E,loc,size=(1.0,0.56)):
    """spot cone aimed slightly downwards: lights the TV wall, credenza and floor in the TV's colour without washing the ceiling"""
    ld=bpy.data.lights.new("CR tv light",'SPOT'); ld.spot_size=math.radians(100); ld.spot_blend=0.9; ld.shadow_soft_size=0.3; ld.energy=80
    lo=bpy.data.objects.new("CR tv light",ld); lo.location=loc; lo.rotation_euler=(math.pi/2-0.38,0,0)      # local -Z -> +Y and tilted down
    coll.objects.link(lo)
    ex=[("wt",E,'["w_tel"]'),("wb",E,'["w_bro"]'),("ws",E,'["w_sta"]'),("wn",E,'["w_bar"]'),("wc",E,'["w_clip"]'),("cr",E,'["clip_r"]'),("cg",E,'["clip_g"]'),("cb",E,'["clip_b"]'),("ce",E,'["clip_e"]')]
    BRO=(1.0,0.42,0.16); STA=(0.78,0.88,1.0); BAR=(0.78,0.74,0.62)
    for i,cl in enumerate(("cr","cg","cb")):
        expr=f"wt*({crk.stab_expr(i)})*0.95+wb*{BRO[i]}+ws*{STA[i]}*0.95+wn*{BAR[i]}+wc*{cl}"
        drv(ld,'color',i,expr,var_s=True,extra=ex)
    drv(ld,'energy',None,"80*(wt*1.0+wb*1.25+ws*(0.55+0.55*abs(sin(frame*13.7)*sin(frame*5.9)))+wn*0.8+wc*ce)",var_s=False,extra=ex)
    return lo
def build(c,cx=-1.5,zc=7.36,w=1.22,h=0.70):
    """TV panel on the back wall (faces +Y). returns the empty."""
    A=c.A; M=c.M; g="tv"; yb=-11.91; E=make_empty(c.coll); c.TVE=E
    M["TVSCR"]=screen_material(E)
    z0,z1=zc-h/2,zc+h/2; xa,xb=cx-w/2,cx+w/2
    A.bx((g,"BLACK"),xa-0.012,xb+0.012,yb+0.05,yb+0.088,z0-0.012,z1+0.012,0.006)                        # slim bezel body
    A.bx((g,"GREY"),xa+0.1,xb-0.1,yb+0.03,yb+0.05,z0+0.08,z1-0.08,0.004)                              # rear hump
    A.plane((g,"TVSCR"),(xb,yb+0.0885,z0),(xa,yb+0.0885,z0),(xa,yb+0.0885,z1),(xb,yb+0.0885,z1))       # u along -x, faces +y
    A.bx((g,"STEEL"),cx-0.20,cx+0.20,yb,yb+0.03,zc-0.18,zc+0.18,0.004)                                  # wall plate
    for dx in (-0.16,0.16):
        for dz in (-0.14,0.14): A.screw((g,"STEEL_L"),'+y',yb+0.03,cx+dx,zc+dz,0.006)
    A.fb((g,"BLACK"),'+y',yb+0.088,cx-0.10,cx+0.10,z0-0.011,z0-0.002,0.002,0.0005) if False else None
    A.fb((g,"LED_ON"),'+y',yb+0.088,xb-0.03,xb-0.024,z0-0.008,z0-0.003,0.002,0.0)
    text(c.coll,"ORIONIX",cx,yb+0.0905,z0-0.006,'+y',0.010,M["STEEL_L"],'CENTER',"CR tv brand") if False else None
    A.tube((g,"CABLE"),[(cx+0.35,yb+0.035,z0+0.05),(cx+0.36,yb+0.04,z0-0.30),(cx+0.30,yb+0.045,z0-0.90),(cx+0.30,yb+0.02,5.85)],0.005,8)
    A.tube((g,"CABLE_G"),[(cx-0.30,yb+0.035,z0+0.05),(cx-0.29,yb+0.04,z0-0.30),(cx-0.34,yb+0.045,z0-0.80),(cx-0.40,yb+0.02,5.90)],0.004,8) if False else None
    make_light(c.coll,E,(cx,yb+0.30,zc))
    return E
