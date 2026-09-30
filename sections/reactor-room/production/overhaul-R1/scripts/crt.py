"""Control-room textures: hand-painted style, generated here with numpy (no scans, no photo textures).
text_mask() renders any string to an anti-aliased mask with a throw-away Cycles scene, so posters / forms / screens carry real lettering."""
import bpy,math,os,random,tempfile
import numpy as np
FONT_CANDS=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]
MONO_CANDS=["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
_fonts={}
def _font(cands):
    k=cands[0]
    if k in _fonts: return _fonts[k]
    f=None
    for p in cands:
        if os.path.exists(p): f=bpy.data.fonts.load(p); break
    _fonts[k]=f; return f
BOLD=lambda:_font(FONT_CANDS); MONO=lambda:_font(MONO_CANDS)
_cache={}
def text_mask(body,W,H,size,align='CENTER',mono=False,spacing=1.0,line=1.1,ax=None,ay=None):
    """returns HxW float mask (row 0 = top); text block centred on (ax,ay) px (default centre), font size in px"""
    key=(body,W,H,size,align,mono,spacing,line,ax,ay)
    if key in _cache: return _cache[key]
    import hashlib; dc=os.environ.get("CR_TEXT_CACHE"); fn=None
    if dc:
        os.makedirs(dc,exist_ok=True); fn=os.path.join(dc,hashlib.md5(repr(key).encode()).hexdigest()+".npy")
        if os.path.exists(fn): _cache[key]=np.load(fn); return _cache[key]
    W0,H0=W,H; W,H=2*W0,2*H0
    sc=bpy.data.scenes.new("_tm"); sc.render.engine='CYCLES'; sc.cycles.samples=6; sc.cycles.device='CPU'; sc.cycles.use_denoising=False; sc.cycles.use_adaptive_sampling=False
    sc.render.resolution_x=W; sc.render.resolution_y=H; sc.render.resolution_percentage=100; sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
    sc.render.film_transparent=False
    w=bpy.data.worlds.new("_tmw"); w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(0,0,0,1); sc.world=w
    cd=bpy.data.cameras.new("_tmc"); cd.type='ORTHO'; cd.ortho_scale=W; co=bpy.data.objects.new("_tmc",cd); sc.collection.objects.link(co); co.location=(W/2,H/2,10); sc.camera=co
    cu=bpy.data.curves.new("_tmt",'FONT'); cu.body=body; cu.size=size; cu.align_x=align; cu.align_y='CENTER'; cu.space_character=spacing; cu.space_line=line; cu.resolution_u=4
    f=_font(MONO_CANDS if mono else FONT_CANDS)
    if f: cu.font=f; cu.font_bold=f; cu.font_italic=f; cu.font_bold_italic=f
    ob=bpy.data.objects.new("_tmt",cu); sc.collection.objects.link(ob)
    ob.location=({'CENTER':W/2,'LEFT':W*0.25,'RIGHT':W*0.75}[align],H/2,0)
    m=bpy.data.materials.new("_tmm"); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); e=nt.nodes.new("ShaderNodeEmission"); e.inputs[1].default_value=1.0; nt.links.new(e.outputs[0],o.inputs[0]); cu.materials.append(m)
    p=os.path.join(tempfile.gettempdir(),"_tm_%d.png"%random.randint(0,10**9)); sc.render.filepath=p; sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGB'
    bpy.ops.render.render(write_still=True,scene=sc.name)
    im=bpy.data.images.load(p); im.colorspace_settings.name='Non-Color'
    a=np.array(im.pixels[:],dtype=np.float32).reshape(H,W,4)[...,0]; a=np.flipud(a).copy()
    bpy.data.images.remove(im); os.remove(p)
    for d,c in ((bpy.data.objects,ob),(bpy.data.objects,co)): d.remove(c)
    bpy.data.curves.remove(cu); bpy.data.cameras.remove(cd); bpy.data.materials.remove(m); bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    ys,xs=np.nonzero(a>0.15); out=np.zeros((H0,W0),dtype=np.float32)
    if len(xs):
        x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
        tx=(W0/2 if ax is None else ax); ty=(H0/2 if ay is None else ay)
        dx=int(round((tx-(x0+x1)/2) if align=='CENTER' else ((tx-x0) if align=='LEFT' else (tx-x1)))); dy=int(round(ty-(y0+y1)/2))
        sx0=max(0,-dx); sx1=min(W,W0-dx); sy0=max(0,-dy); sy1=min(H,H0-dy)
        if sx1>sx0 and sy1>sy0: out[sy0+dy:sy1+dy,sx0+dx:sx1+dx]=a[sy0:sy1,sx0:sx1]
    _cache[key]=out
    if fn: np.save(fn,out)
    return out
# ---------------- 2D painting
def canvas(W,H,col): a=np.zeros((H,W,3),dtype=np.float32); a[...]=col; return a
def XY(W,H): Y,X=np.mgrid[0:H,0:W].astype(np.float32); return X+0.5,Y+0.5
def over(a,m,col,al=1.0):
    m=np.clip(m,0,1)[...,None]*al; a[...]=a*(1-m)+np.array(col,dtype=np.float32)*m
def m_circle(X,Y,cx,cy,r): return np.clip(r-np.hypot(X-cx,Y-cy)+0.5,0,1)
def m_ring(X,Y,cx,cy,r0,r1): return np.clip(np.minimum(r1-np.hypot(X-cx,Y-cy),np.hypot(X-cx,Y-cy)-r0)+0.5,0,1)
def m_rect(X,Y,x0,y0,x1,y1): return np.clip(np.minimum(np.minimum(X-x0,x1-X),np.minimum(Y-y0,y1-Y))+0.5,0,1)
def m_rrect(X,Y,x0,y0,x1,y1,r):
    cx,cy=(x0+x1)/2,(y0+y1)/2; hx,hy=(x1-x0)/2-r,(y1-y0)/2-r
    qx=np.abs(X-cx)-hx; qy=np.abs(Y-cy)-hy
    d=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-r
    return np.clip(0.5-d,0,1)
def m_tri(X,Y,p0,p1,p2):
    d=None
    ps=[p0,p1,p2]
    if (p1[0]-p0[0])*(p2[1]-p0[1])-(p1[1]-p0[1])*(p2[0]-p0[0])<0: ps=[p0,p2,p1]
    for i in range(3):
        a,b=ps[i],ps[(i+1)%3]; ex,ey=b[0]-a[0],b[1]-a[1]; L=math.hypot(ex,ey)
        di=((X-a[0])*ey-(Y-a[1])*ex)*-1/L
        d=di if d is None else np.minimum(d,di)
    return np.clip(d+0.5,0,1)
def m_line(X,Y,x0,y0,x1,y1,w):
    dx,dy=x1-x0,y1-y0; L2=dx*dx+dy*dy+1e-9; t=np.clip(((X-x0)*dx+(Y-y0)*dy)/L2,0,1)
    return np.clip(w/2-np.hypot(X-(x0+t*dx),Y-(y0+t*dy))+0.5,0,1)
def m_poly(X,Y,pts):
    """convex or star polygon via even-odd + edge distance"""
    n=len(pts); inside=np.zeros(X.shape,dtype=bool); dmin=np.full(X.shape,1e9,dtype=np.float32)
    for i in range(n):
        x0,y0=pts[i]; x1,y1=pts[(i+1)%n]
        c=((y0>Y)!=(y1>Y))&(X<(x1-x0)*(Y-y0)/(y1-y0+1e-12)+x0); inside^=c
        dx,dy=x1-x0,y1-y0; L2=dx*dx+dy*dy+1e-9; t=np.clip(((X-x0)*dx+(Y-y0)*dy)/L2,0,1); dmin=np.minimum(dmin,np.hypot(X-(x0+t*dx),Y-(y0+t*dy)))
    return np.clip(np.where(inside,dmin,-dmin)+0.5,0,1)
def put_text(a,body,cx,cy,size,col,align='CENTER',mono=False,spacing=1.0,line=1.1,al=1.0):
    H,W=a.shape[:2]; over(a,text_mask(body,W,H,size,align,mono,spacing,line,cx,cy),col,al)
def smooth_noise(H,W,cell,rng):
    gh,gw=H//cell+3,W//cell+3; g=rng.random((gh,gw)).astype(np.float32)
    ys=np.linspace(0,gh-3,H); xs=np.linspace(0,gw-3,W); y0=ys.astype(int); x0=xs.astype(int); fy=(ys-y0)[:,None]; fx=(xs-x0)[None,:]
    fy=fy*fy*(3-2*fy); fx=fx*fx*(3-2*fx)
    a=g[y0][:,x0]*(1-fy)*(1-fx)+g[y0][:,x0+1]*(1-fy)*fx+g[y0+1][:,x0]*fy*(1-fx)+g[y0+1][:,x0+1]*fy*fx
    return a
def paper_grain(a,rng,amt=0.03,fold=None,age=0.0):
    H,W=a.shape[:2]; n=rng.normal(0,amt,(H,W,1)).astype(np.float32)
    # low-frequency stain
    lf=smooth_noise(H,W,48,rng)
    a+=n+(lf[...,None]-0.5)*0.035
    X,Y=XY(W,H); e=np.minimum(np.minimum(X,W-X),np.minimum(Y,H-Y)); a*= (1-0.25*np.clip(1-e/22,0,1)*(0.4+age))[...,None]
    if fold is not None:
        fy=int(H*fold); a[fy-1:fy+1]*=0.82; a[fy+1:fy+3]*=1.05
    np.clip(a,0,1,out=a); return a
# ---------------- posters (display sRGB values)
PAL={"char":(0.13,0.14,0.13),"olive":(0.36,0.40,0.20),"olive_d":(0.22,0.25,0.12),"orange":(0.86,0.38,0.09),"mustard":(0.86,0.63,0.10),"red":(0.66,0.13,0.09),"paper":(0.82,0.81,0.74),"steel":(0.42,0.46,0.47),"ink":(0.08,0.08,0.08)}
def poster(kind,W=512,H=720,seed=1):
    rng=np.random.default_rng(seed); X,Y=XY(W,H); P=PAL
    if kind=="machine":     # olive field, big orange gear
        a=canvas(W,H,P["olive"]); over(a,np.clip(Y/H,0,1),P["olive_d"],0.55)
        over(a,m_rect(X,Y,0,H-150,W,H),P["orange"]); cx,cy=W/2,H*0.52
        for k in range(12):
            ang=k*math.pi/6; ux,uy=math.cos(ang),math.sin(ang)
            over(a,m_line(X,Y,cx+ux*150,cy+uy*150,cx+ux*196,cy+uy*196,44),P["char"])
        over(a,m_circle(X,Y,cx,cy,170),P["char"]); over(a,m_circle(X,Y,cx,cy,132),P["orange"]); over(a,m_circle(X,Y,cx,cy,64),P["char"]); over(a,m_circle(X,Y,cx,cy,38),P["olive"])
        put_text(a,"THE MACHINE\nPROVIDES.",W/2,70,50,P["paper"],line=1.0); put_text(a,"YOU SUSTAIN.",W/2,H-78,44,P["char"])
    elif kind=="shift":     # orange field, bulb with rays
        a=canvas(W,H,P["orange"]); over(a,np.clip(1-Y/H,0,1),P["red"],0.35); cx,cy=W/2,H*0.44
        for k in range(16):
            ang=k*math.pi/8+0.1; ux,uy=math.cos(ang),math.sin(ang); over(a,m_line(X,Y,cx+ux*150,cy+uy*150,cx+ux*(215 if k%2 else 185),cy+uy*(215 if k%2 else 185),16),P["mustard"])
        over(a,m_circle(X,Y,cx,cy-8,118),P["mustard"]); over(a,m_rrect(X,Y,cx-52,cy+90,cx+52,cy+150,10),P["char"]); over(a,m_rect(X,Y,cx-52,cy+112,cx+52,cy+118),P["steel"])
        over(a,m_ring(X,Y,cx,cy-8,70,82),P["orange"])
        over(a,m_rect(X,Y,0,H-150,W,H),P["char"])
        put_text(a,"YOUR SHIFT KEEPS\nTHE LIGHTS ON",W/2,64,40,P["char"],line=1.0); put_text(a,"THANK YOU,\nVALUED EMPLOYEE",W/2,H-76,34,P["mustard"],line=1.05)
    elif kind=="comply":    # charcoal field, tick in disc
        a=canvas(W,H,P["char"]); over(a,np.clip(Y/H,0,1),(0.05,0.055,0.05),0.6); cx,cy=W/2,H*0.46
        over(a,m_circle(X,Y,cx,cy,175),P["mustard"]); over(a,m_circle(X,Y,cx,cy,140),P["char"])
        over(a,m_line(X,Y,cx-72,cy+6,cx-18,cy+62,34),P["mustard"]); over(a,m_line(X,Y,cx-18,cy+62,cx+82,cy-58,34),P["mustard"])
        over(a,m_rect(X,Y,0,H-120,W,H),P["mustard"]); over(a,m_rect(X,Y,0,0,W,26),P["mustard"])
        put_text(a,"COMPLIANCE\nIS COMFORT.",W/2,86,46,P["paper"],line=1.0); put_text(a,"SMILE. YOU ARE VALUED.",W/2,H-60,30,P["char"])
    elif kind=="questions": # mustard field, watching eye
        a=canvas(W,H,P["mustard"]); over(a,np.clip(1-Y/H,0,1),P["orange"],0.45); cx,cy=W/2,H*0.46
        for k in range(15):
            ang=math.pi+ (k-7)*0.21; ux,uy=math.cos(ang),math.sin(ang); over(a,m_line(X,Y,cx+ux*140,cy+uy*140,cx+ux*205,cy+uy*205,12),P["char"])
        eye=np.clip(1-((X-cx)/190)**2-((Y-cy)/92)**2,0,1); over(a,(eye>0.02).astype(np.float32)*np.clip(eye*30,0,1),P["paper"])
        over(a,m_circle(X,Y,cx,cy,78),P["red"]); over(a,m_circle(X,Y,cx,cy,42),P["char"]); over(a,m_circle(X,Y,cx+16,cy-16,10),P["paper"])
        over(a,m_rect(X,Y,0,H-130,W,H),P["char"])
        put_text(a,"QUESTIONS ARE\nINEFFICIENCY.",W/2,76,42,P["char"],line=1.0); put_text(a,"TRUST THE OUTPUT.",W/2,H-64,34,P["mustard"])
    elif kind=="report":    # red field, warning triangle
        a=canvas(W,H,P["red"]); over(a,np.clip(Y/H,0,1),P["char"],0.4); cx,cy=W/2,H*0.47
        over(a,m_tri(X,Y,(cx,cy-165),(cx-190,cy+130),(cx+190,cy+130)),P["mustard"]); over(a,m_tri(X,Y,(cx,cy-118),(cx-142,cy+106),(cx+142,cy+106)),P["char"])
        over(a,m_rrect(X,Y,cx-13,cy-58,cx+13,cy+38,8),P["mustard"]); over(a,m_circle(X,Y,cx,cy+72,15),P["mustard"])
        over(a,m_rect(X,Y,0,H-140,W,H),P["char"])
        put_text(a,"REPORT NOTHING\nUNUSUAL.",W/2,70,42,P["paper"],line=1.0); put_text(a,"NOTHING UNUSUAL\nIS REPORTED.",W/2,H-72,30,P["mustard"],line=1.05)
    elif kind=="hydrate":   # small strip poster, steel + orange
        a=canvas(W,H,P["steel"]); over(a,m_rect(X,Y,0,0,W,H*0.5),P["olive_d"]); over(a,m_rect(X,Y,0,H*0.5-8,W,H*0.5+8),P["orange"])
        put_text(a,"HYDRATE.\nREPORT.\nREPEAT.",W/2,H*0.30,62,P["paper"],line=1.0); over(a,m_circle(X,Y,W/2,H*0.74,86),P["orange"]); over(a,m_circle(X,Y,W/2,H*0.74,58),P["steel"])
        put_text(a,"HAVE A\nPRODUCTIVE\nSHIFT",W/2,H*0.74,24,P["char"],line=1.0)
    else: a=canvas(W,H,P["paper"])
    return paper_grain(a,rng,0.012,fold=0.5,age=0.3)
def notice(kind,W=384,H=512,seed=2):
    rng=np.random.default_rng(seed); X,Y=XY(W,H); P=PAL; a=canvas(W,H,(0.80,0.79,0.72)); ink=P["ink"]
    def rule(y,x0=28,x1=W-28,w=1.2): over(a,m_line(X,Y,x0,y,x1,y,w),ink,0.55)
    if kind=="form":
        put_text(a,"FORM 7-B",W/2,34,30,ink); put_text(a,"ACKNOWLEDGEMENT OF\nSATISFACTION",W/2,74,20,ink,line=1.0); rule(102)
        for i,t in enumerate(("I AM SATISFIED","I AM VERY SATISFIED","I AM TRAINED TO BE SATISFIED","I HAVE NO FURTHER REMARKS","I HAVE NOTHING TO REPORT")):
            y=138+i*44; over(a,m_rect(X,Y,30,y-11,52,y+11),ink,0.0); over(a,m_ring(X,Y,41,y,0,0),ink,0); over(a,m_rect(X,Y,30,y-11,52,y+11)-m_rect(X,Y,33,y-8,49,y+8),ink,0.8)
            if i in(0,4): over(a,m_line(X,Y,34,y,40,y+6,3.5),ink); over(a,m_line(X,Y,40,y+6,49,y-8,3.5),ink)
            put_text(a,t,66,y,17,ink,'LEFT')
        rule(380); put_text(a,"SIGNED:",30,414,17,ink,'LEFT'); rule(430,110,W-30); put_text(a,"RETURN TO MANAGEMENT.\nMANAGEMENT IS GRATEFUL.",W/2,472,13,ink,line=1.0)
        over(a,m_rect(X,Y,W-104,14,W-24,54),P["red"],0.75); put_text(a,"COPY 2",W-64,34,16,P["paper"])
    elif kind=="roster":
        put_text(a,"SHIFT 04  ROSTER",W/2,36,28,ink); rule(64)
        rows=(("VANCE, A.","REACTOR","PRESENT"),("OKAFOR, B.","COOLANT","PRESENT"),("LINDQVIST, C.","GRID","PRESENT"),("NAKAMURA, T.","SPARE","PRESENT"),("[ REMOVED ]","","----"))
        for i,(n,d,s) in enumerate(rows):
            y=104+i*46; put_text(a,n,26,y,17,ink,'LEFT'); put_text(a,d,210,y,15,ink,'LEFT'); put_text(a,s,W-24,y,15,P["olive_d"],'RIGHT'); rule(y+22,24,W-24,0.8)
        put_text(a,"ALL STAFF ARE PRESENT.\nALL STAFF ARE WELL.",W/2,H-96,17,ink,line=1.05)
        over(a,m_line(X,Y,26,104+4*46,W-26,104+4*46,3),ink,0.6)
    elif kind=="rules":
        put_text(a,"HOUSE RULES",W/2,40,32,ink); rule(70)
        rs=("1. THE MACHINE IS RIGHT.","2. IF THE MACHINE IS WRONG,\n    SEE RULE 1.","3. DO NOT LEAVE THE\n    CONSOLE UNATTENDED.","4. DO NOT DISCUSS THE\n    OTHER SHIFT.","5. LIGHTS STAY ON.")
        y=110
        for r_ in rs:
            put_text(a,r_,30,y,18,ink,'LEFT',line=1.05); y+=34+18*r_.count("\n")*1.1
        over(a,m_rect(X,Y,30,H-88,W-30,H-40),P["mustard"],0.9); put_text(a,"THANK YOU FOR COMPLYING",W/2,H-64,17,ink)
    elif kind=="log":
        put_text(a,"COOLANT LOG",W/2,32,26,ink); rule(58)
        for i in range(9):
            y=90+i*38; rule(y+16,24,W-24,0.8); put_text(a,f"{20+i:02d}:{(i*17)%60:02d}",28,y,15,ink,'LEFT',True); put_text(a,("NOMINAL","NOMINAL","NOMINAL","NOMINAL","NOMINAL","NOMINAL","NOMINAL","NOMINAL","NOMINAL")[i],160,y,15,ink,'LEFT',True)
            over(a,m_line(X,Y,W-70,y+2,W-30,y-4,1.6),(0.05,0.10,0.35),0.7)
    elif kind=="safety":
        a=canvas(W,H,P["mustard"]); put_text(a,"NOTICE",W/2,54,52,ink); over(a,m_rect(X,Y,20,88,W-20,96),ink)
        put_text(a,"THE FLOOR IS NOT\nSLIPPERY.\nTHE FLOOR IS SAFE.\nTHE FLOOR HAS\nALWAYS BEEN SAFE.",W/2,250,30,ink,line=1.15); put_text(a,"— FACILITY MANAGEMENT",W/2,H-56,16,ink)
    elif kind=="passcard":
        a=canvas(W,H,(0.22,0.24,0.22)); over(a,m_rect(X,Y,0,0,W,90),P["orange"]); put_text(a,"ACCESS",W/2,45,40,P["char"]); put_text(a,"SHIFT 04\nCONTROL",W/2,190,44,P["paper"],line=1.0)
        put_text(a,"VANCE, A.",W/2,330,26,P["mustard"]); over(a,m_rect(X,Y,60,380,W-60,440),P["char"]);
        for k in range(30): over(a,m_rect(X,Y,70+k*8.6,388,72+k*8.6+(k%3),432),P["paper"],0.9)
    return paper_grain(a,rng,0.01,fold=None,age=0.5)
# ---------------- floor tile (period = 1.2 m = 4x4 tiles of 0.3 m), display sRGB
def floor_tile(N=1024,seed=3):
    rng=np.random.default_rng(seed); t=N//4; a=np.zeros((N,N,3),dtype=np.float32)
    base=np.array([0.30,0.31,0.26],dtype=np.float32)
    for i in range(4):
        for j in range(4):
            k=1.0+rng.uniform(-0.09,0.09); tint=np.array([1+rng.uniform(-.03,.03),1,1+rng.uniform(-.04,.02)],dtype=np.float32)
            a[i*t:(i+1)*t,j*t:(j+1)*t]=base*k*tint
    # speckle flecks (vinyl composite tile)
    sp=rng.random((N,N)); a[sp>0.985]*=1.18; a[sp<0.012]*=0.80
    # soft mottling
    from_blur=smooth_noise(N,N,96,rng)
    a*=(0.93+0.14*from_blur[...,None])
    # scuffs
    X,Y=XY(N,N)
    for _ in range(60):
        x0,y0=rng.uniform(0,N,2); ang=rng.uniform(0,math.pi); L=rng.uniform(20,90); over(a,m_line(X,Y,x0,y0,x0+L*math.cos(ang),y0+L*math.sin(ang),rng.uniform(1.2,3)),(0.42,0.42,0.37),0.30)
    # grout
    g=3
    for i in range(4):
        a[i*t-g:i*t+g,:]*=0.55; a[:,i*t-g:i*t+g]*=0.55
    a[:g]*=0.55; a[:,:g]*=0.55; a[-g:]*=0.55; a[:,-g:]*=0.55
    return np.clip(a,0,1)
# ---------------- CRT screens (display values; emission colour applied in the shader)
def crt_screen(lines,W=512,H=384,seed=4,cursor=True):
    rng=np.random.default_rng(seed); a=np.zeros((H,W,3),dtype=np.float32); X,Y=XY(W,H)
    body="\n".join(lines); m=text_mask(body,W,H,25,'LEFT',True,1.0,1.18,28,H*0.46)
    g=m.copy()
    for k in range(3): g=(g+np.roll(g,2,0)+np.roll(g,-2,0)+np.roll(g,2,1)+np.roll(g,-2,1))/5     # phosphor bloom
    v=np.clip(m*0.95+g*0.55,0,1.4)
    sl=0.80+0.20*np.sin(Y*math.pi)                   # scanlines
    v*=sl
    v+=0.035*sl  # raster glow
    a[...]=v[...,None]
    vx=np.clip(1-((X-W/2)/(W*0.62))**2-((Y-H/2)/(H*0.62))**2,0,1)**0.6      # vignette
    a*=vx[...,None]
    return np.clip(a,0,1.5)
# ---------------- TV content (grey masks + colour images)
def tv_telemetry(W=384,H=216):
    a=np.zeros((H,W),dtype=np.float32); X,Y=XY(W,H)
    def R(x0,y0,x1,y1,v):
        m=m_rect(X,Y,x0,y0,x1,y1); a[...]=np.maximum(a,m*v)
    R(0,0,W,22,0.95); R(0,H-18,W,H,0.5)
    tm=text_mask("REACTOR 04  //  STABILITY MONITOR",W,H,13,'LEFT',False,1.0,1.0,10,11); a[...]=np.where(tm>0.3,0.0,a)
    tm=text_mask("SHIFT 04  ALL SYSTEMS NOMINAL  ///  ALL SYSTEMS NOMINAL  ///",W,H,11,'LEFT',False,1.0,1.0,8,H-9); a[...]=np.maximum(a,tm*0.0+ (tm>0.3)*0.0)
    for x in range(10,W-10,32): R(x,30,x+0.8,H-26,0.14)
    for y in range(34,H-24,22): R(10,y,W-10,y+0.8,0.14)
    for k,(bx,hgt) in enumerate(((22,0.74),(62,0.62),(102,0.85))):
        R(bx,H-30-int(120*hgt),bx+28,H-30,0.85); R(bx-2,H-30,bx+30,H-27,1.0)
        for t in range(0,121,20): R(bx+30,H-30-t,bx+35,H-29-t,0.55)
    xs=np.arange(150,W-16); ys=(H*0.70+14*np.sin(xs*0.11)+6*np.sin(xs*0.37)+3*np.sin(xs*0.9)).astype(int)
    for x,y in zip(xs,ys): R(x,y-1.2,x+1.2,y+1.2,1.0)
    for x in range(150,W-16,6): R(x,H-22-int(4+10*abs(math.sin(x*0.19))),x+3,H-22,0.62)
    for i in range(7):
        tm=text_mask(("BANK A   8.4 M   OK","BANK B   7.4 M   OK","COOLANT P-10  RUN","GRID DEMAND   74%","POOL TEMP   NOMINAL","TURBINE  04   SYNC","STABILITY  --")[i],W,H,10,'LEFT',True,1.0,1.0,152,44+i*14); a[...]=np.maximum(a,tm*0.85)
    return a
def tv_broadcast(W=384,H=216,seed=5):
    P=PAL; X,Y=XY(W,H); a=canvas(W,H,P["red"]); over(a,np.clip(Y/H,0,1),P["orange"],0.6)
    cx,cy=W*0.72,H*0.46
    for k in range(20): ang=k*math.pi/10; over(a,m_line(X,Y,cx,cy,cx+math.cos(ang)*260,cy+math.sin(ang)*260,26),P["mustard"],0.22)
    over(a,m_circle(X,Y,cx,cy,64),P["mustard"]); over(a,m_circle(X,Y,cx,cy,44),P["char"]); over(a,m_circle(X,Y,cx,cy,22),P["mustard"])
    over(a,m_rect(X,Y,0,H-44,W,H),P["char"]); over(a,m_rect(X,Y,0,H-48,W,H-44),P["mustard"])
    put_text(a,"THE MACHINE\nPROVIDES.",22,70,38,P["paper"],'LEFT',line=1.0)
    put_text(a,"A MESSAGE FROM MANAGEMENT",22,116,13,P["char"],'LEFT'); put_text(a,"STAY CALM.  STAY AT YOUR POST.  STAY SATISFIED.",W/2,H-22,12,P["paper"])
    for k in range(4):
        x0=26+k*46; over(a,m_circle(X,Y,x0+14,H-84,9),P["char"]); over(a,m_rrect(X,Y,x0,H-76,x0+28,H-50,8),P["char"])
    return a
def tv_bars(W=384,H=216):
    P=PAL; X,Y=XY(W,H); a=canvas(W,H,(0.05,0.06,0.06)); cols=[(0.80,0.80,0.78),(0.80,0.72,0.10),(0.15,0.65,0.30),(0.62,0.62,0.60),(0.80,0.40,0.10),(0.70,0.12,0.08),(0.30,0.30,0.30)]
    bw=W/7
    for i,c in enumerate(cols): over(a,m_rect(X,Y,i*bw,0,(i+1)*bw,H*0.72),c)
    over(a,m_rect(X,Y,0,H*0.72,W,H),(0.04,0.04,0.05)); 
    for i in range(16): over(a,m_rect(X,Y,i*W/16,H*0.72,(i+1)*W/16,H*0.80),(i/15,i/15,i/15))
    over(a,m_rrect(X,Y,W/2-92,H*0.83,W/2+92,H*0.97,4),(0.02,0.02,0.02)); put_text(a,"NO SIGNAL",W/2,H*0.90,24,(0.9,0.9,0.88))
    return a
