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
def put_label(a,body,cx,cy,size,col,al=1.0):
    """small-canvas variant of put_text (fast): renders the string on a 192x96 canvas and pastes it centred on (cx,cy)"""
    m=text_mask(body,192,96,size,'CENTER',False,1.0,1.1,96,48); H,W=a.shape[:2]
    x0=int(round(cx-96)); y0=int(round(cy-48)); sx0=max(0,-x0); sy0=max(0,-y0); sx1=min(192,W-x0); sy1=min(96,H-y0)
    if sx1<=sx0 or sy1<=sy0: return
    sub=a[y0+sy0:y0+sy1,x0+sx0:x0+sx1]; mm=np.clip(m[sy0:sy1,sx0:sx1],0,1)[...,None]*al
    a[y0+sy0:y0+sy1,x0+sx0:x0+sx1]=sub*(1-mm)+np.array(col,dtype=np.float32)*mm
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
        tm=text_mask(("BANK A   8.4 M   OK","BANK B   8.4 M   OK","COOLANT P-10  RUN","GRID DEMAND   74%","POOL TEMP   NOMINAL","TURBINE  04   SYNC","STABILITY  --")[i],W,H,10,'LEFT',True,1.0,1.0,152,44+i*14); a[...]=np.maximum(a,tm*0.85)
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
# ---------------- keyboard: ONE painted QWERTY top instead of ~110 key boxes (colour map + height map used as bump)
def keyboard_tex(W=1536,H=608):
    """0.48 m x 0.19 m keyboard top. returns (colour HxWx3 sRGB, height HxW). row 0 = BACK edge (v=1)."""
    ppm=W/0.48; X,Y=XY(W,H); col=canvas(W,H,(0.15,0.145,0.13)); hgt=np.zeros((H,W),dtype=np.float32)
    U=0.0190*ppm; gap=0.0022*ppm
    def ky(row): return H-(0.020+row*0.0195)*ppm       # top edge (canvas y) of key row; row 0 = front (space) row
    keys=[]                                               # (x0,y0,w,h,label,dark)
    x0=0.016*ppm
    def add(col_u,row,w_u,label="",dark=False,xo=0.0):
        keys.append((x0+xo*ppm+col_u*U,ky(row)-U,w_u*U,U,label,dark))
    # main block rows (front to back): space row, shift row, caps, tab, number, function
    add(0,0,1.25,"",True); add(1.25,0,1.25,"",True); add(2.5,0,1.25,"",True); add(3.75,0,6.25,""); add(10,0,1.25,"",True); add(11.25,0,1.25,"",True); add(12.5,0,1.25,"",True); add(13.75,0,1.25,"",True)
    add(0,1,2.25,"SHIFT",True)
    for i,ch in enumerate("ZXCVBNM,./"): add(2.25+i,1,1,ch)
    add(12.25,1,2.75,"SHIFT",True)
    add(0,2,1.75,"CAPS",True)
    for i,ch in enumerate("ASDFGHJKL;'"): add(1.75+i,2,1,ch)
    add(12.75,2,2.25,"ENTER",True)
    add(0,3,1.5,"TAB",True)
    for i,ch in enumerate("QWERTYUIOP[]"): add(1.5+i,3,1,ch)
    add(13.5,3,1.5,"\\",True)
    add(0,4,1,"`",True)
    for i,ch in enumerate("1234567890-="): add(1+i,4,1,ch)
    add(13,4,2,"BKSP",True)
    add(0,5.35,1,"ESC",True)
    for g_,(a,n) in enumerate(((2,4),(6.5,4),(11,4))):
        for i in range(n): add(a+i,5.35,1,"F%d"%(g_*4+i+1),True)
    xn=x0+15.5*U                                   # nav cluster
    for i in range(3):
        keys.append((xn+i*U,ky(5.35)-U,U,U,"",True)); keys.append((xn+i*U,ky(4)-U,U,U,"",True)); keys.append((xn+i*U,ky(3)-U,U,U,"",True)); keys.append((xn+i*U,ky(1)-U,U,U,"",True))
    keys.append((xn+U,ky(2)-U,U,U,"",True)) if False else None
    xp=x0+19.0*U                                   # numpad
    for i,lab in enumerate(("7","8","9","4","5","6","1","2","3")): keys.append((xp+(i%3)*U,ky(3-(i//3))-U,U,U,lab,False))
    keys.append((xp+3*U,ky(3)-U,U,2*U+0.0195*ppm-U,"+",True)); keys.append((xp+3*U,ky(1)-U,U,2*U,"",True))
    keys.append((xp,ky(0)-U,2*U,U,"0",False)); keys.append((xp+2*U,ky(0)-U,U,U,".",False)); keys.append((xp+3*U,ky(0)-U,U,U,"",True))
    for (kx,kyy,kw,kh,lab,dark) in keys:
        base=(0.50,0.47,0.40) if not dark else (0.33,0.32,0.29)
        m=m_rrect(X,Y,kx+gap/2,kyy+gap/2,kx+kw-gap/2,kyy+kh-gap/2,0.0016*ppm)
        over(col,m,tuple(c*0.80 for c in base))                                       # key side / shadow edge
        mi=m_rrect(X,Y,kx+gap/2+0.0012*ppm,kyy+gap/2+0.0008*ppm,kx+kw-gap/2-0.0012*ppm,kyy+kh-gap/2-0.0020*ppm,0.0014*ppm)
        over(col,mi,base); over(col,mi*np.clip(1-(Y-kyy)/kh,0,1),tuple(min(1,c*1.18) for c in base),0.45)     # dished top with a lit upper edge
        hgt=np.maximum(hgt,m*0.85+mi*0.15)
        if lab:
            sz=(0.0075 if len(lab)<=1 else (0.0048 if len(lab)<=3 else 0.0038))*ppm
            put_label(col,lab,kx+kw/2,kyy+kh/2-0.0010*ppm,min(sz*1.25 if len(lab)<=1 else sz*1.0,70),(0.10,0.10,0.09))
    for _ in range(3): hgt=(hgt+np.roll(hgt,1,0)+np.roll(hgt,-1,0)+np.roll(hgt,1,1)+np.roll(hgt,-1,1))/5     # soft key edges for the bump
    rng=np.random.default_rng(11); col*=(1+rng.normal(0,0.012,(H,W,1))).astype(np.float32)
    # LED strip (three lamps, back right)
    for k_ in range(3): over(col,m_rect(X,Y,W-(0.105-k_*0.022)*ppm,0.004*ppm,W-(0.105-k_*0.022)*ppm+0.011*ppm,0.008*ppm),(0.25,0.9,0.3) if k_==0 else (0.2,0.2,0.18))
    return np.clip(col,0,1),np.clip(hgt,0,1)
# ---------------- decals (RGBA, straight alpha) for grime, paint, stencils, personal items
def _rgba(rgb,alpha): 
    H,W=alpha.shape; a=np.zeros((H,W,4),dtype=np.float32); a[...,:3]=np.array(rgb,dtype=np.float32); a[...,3]=np.clip(alpha,0,1); return a
def water_stain(W=256,H=512,seed=21):
    """long streaky water stain running down a wall or over a tile (strongest at the top, feathered edges, darker tide marks)"""
    rng=np.random.default_rng(seed); X,Y=XY(W,H); u=(X-W/2)/(W/2); v=Y/H
    width=0.30+0.55*(1-v)**0.6+0.10*smooth_noise(H,W,64,rng)
    body=np.clip(1-np.abs(u)/np.maximum(width,0.05),0,1)**0.7*np.clip(1.15-v*1.05,0,1)
    streak=0.6+0.4*smooth_noise(H,W,10,rng)*np.clip(np.sin(u*37+smooth_noise(H,W,40,rng)*9)*0.5+0.5,0,1)
    edge=np.clip(1-np.abs(body-0.42)*9,0,1)*0.5                                   # tide line
    a=np.clip((body*streak*1.0+edge*body*0.8)*1.35,0,0.85)
    col=_rgba((0.14,0.09,0.04),a); col[...,:3]*=(0.85+0.3*smooth_noise(H,W,30,rng))[...,None]; return col
def floor_wear(W=512,H=512,seed=22):
    """walkway scuffing: long soft streaks of pale scuff + darker grime"""
    rng=np.random.default_rng(seed); X,Y=XY(W,H); a=np.zeros((H,W),dtype=np.float32); cols=np.zeros((H,W,3),dtype=np.float32)
    g=smooth_noise(H,W,80,rng); a+=np.clip(g-0.35,0,1)*0.55
    for _ in range(70):
        x0,y0=rng.uniform(0,W,2); ang=rng.normal(0,0.10); L=rng.uniform(80,300); a=np.maximum(a,m_line(X,Y,x0,y0,x0+L*math.cos(ang),y0+L*math.sin(ang),rng.uniform(3,9))*rng.uniform(0.08,0.22))
    for _ in range(4): a=(a+np.roll(a,2,0)+np.roll(a,-2,0)+np.roll(a,2,1)+np.roll(a,-2,1))/5      # soften: scuffs, not scratches
    edge=np.clip(1-np.abs(X/W*2-1)**3,0,1)*np.clip(1-np.abs(Y/H*2-1)**3,0,1)
    return _rgba((0.06,0.055,0.045),np.clip(a*edge*0.85,0,0.5))
def coffee_ring(W=128,H=128,seed=23,spill=False):
    rng=np.random.default_rng(seed); X,Y=XY(W,H); r=np.hypot(X-W/2,Y-H/2)/(W/2)
    if spill:
        wob=1+0.10*np.sin(np.arctan2(Y-H/2,X-W/2)*3+1.3)+0.05*np.sin(np.arctan2(Y-H/2,X-W/2)*7)
        a=np.clip((0.78*wob-r)*6,0,1)*0.30+np.clip(1-np.abs(r-0.74*wob)*16,0,1)*0.22
    else: a=np.clip(1-np.abs(r-0.72)*16,0,1)*0.55*(0.75+0.25*smooth_noise(H,W,14,rng))
    return _rgba((0.20,0.12,0.06),a*np.clip(1.5-r,0,1))
def floor_arrow(W=512,H=192,text="EXIT"):
    X,Y=XY(W,H); a=np.zeros((H,W),dtype=np.float32)
    a=np.maximum(a,m_rect(X,Y,150,H*0.36,W-10,H*0.64)); a=np.maximum(a,m_tri(X,Y,(150,H*0.12),(150,H*0.88),(6,H*0.5)))
    tm=text_mask(text,W,H,H*0.30,'CENTER',False,1.0,1.0,(W+150)/2,H/2); a=np.clip(a-tm*1.2,0,1)
    rng=np.random.default_rng(24); a*=np.clip(0.75+0.45*smooth_noise(H,W,12,rng),0,1)*0.9
    return _rgba((0.86,0.63,0.10),a)
def stencil(body,W,H,size,col=(0.06,0.065,0.06),wear=0.35,seed=25,align='CENTER'):
    rng=np.random.default_rng(seed); m=text_mask(body,W,H,size,align,False,1.0,1.05); m=np.where(m<0.10,0.0,m)
    w=np.clip(smooth_noise(H,W,10,rng)*1.6-wear,0,1); a=m*(1-0.75*np.clip(w*1.2,0,1))
    a=np.where(rng.random((H,W))<0.03,a*0.3,a); return _rgba(col,a)
def sticky(kind,W=128,H=128,seed=26):
    rng=np.random.default_rng(seed); X,Y=XY(W,H); a=canvas(W,H,(0.93,0.78,0.22)); over(a,np.clip((Y/H),0,1),(0.85,0.65,0.12),0.25)
    txt={"a":"CHECK\nBANK B\nAGAIN?","b":"DO NOT\nTOUCH\nRED DIAL","c":"HE IS\nALWAYS\nTHERE","d":"SMILE"}[kind]
    put_label(a,txt,W/2,H/2,22 if kind!="d" else 34,(0.12,0.10,0.35),0.9)
    return paper_grain(a,rng,0.01,age=0.2)
def photo(W=128,H=160,seed=27):
    P=PAL; X,Y=XY(W,H); a=canvas(W,H,(0.68,0.74,0.72)); over(a,np.clip(Y/H,0,1),(0.88,0.78,0.55),0.7)
    over(a,m_rect(X,Y,0,H*0.72,W,H),(0.32,0.40,0.22))
    for (cx,cy,r,c) in ((38,H*0.50,11,(0.12,0.12,0.12)),(64,H*0.48,12,(0.10,0.10,0.10)),(90,H*0.56,8,(0.14,0.12,0.10))):
        over(a,m_circle(X,Y,cx,cy,r),(0.85,0.68,0.55)); over(a,m_rrect(X,Y,cx-r*0.9,cy+r*0.9,cx+r*0.9,cy+r*3.3,5),c)
    return paper_grain(a,np.random.default_rng(seed),0.012,age=0.3)
def poster_defaced(W=512,H=720,seed=28):
    """the QUESTIONS poster, scrawled over in marker"""
    a=poster("questions",W,H,seed=3); X,Y=XY(W,H); rng=np.random.default_rng(seed)
    red=(0.50,0.03,0.03)
    cx,cy=W/2,H*0.46
    for (x0,y0,x1,y1) in ((cx-200,cy-110,cx+200,cy+110),(cx+200,cy-110,cx-200,cy+110)):
        for k in range(3): over(a,m_line(X,Y,x0+rng.normal(0,5),y0+rng.normal(0,5),x1+rng.normal(0,5),y1+rng.normal(0,5),rng.uniform(9,14)),red,0.92)
    over(a,m_line(X,Y,60,H-64,W-60,H-70,12),red,0.9)                                # strikes out TRUST THE OUTPUT
    m=text_mask("THEY ARE\nLISTENING",W,H,62,'CENTER',False,1.0,0.95,W/2,H*0.80); 
    ang=-0.12; ca,sa=math.cos(ang),math.sin(ang); xs=((X-W/2)*ca+(Y-H*0.80)*sa+W/2).astype(int).clip(0,W-1); ys=(-(X-W/2)*sa+(Y-H*0.80)*ca+H*0.80).astype(int).clip(0,H-1)
    over(a,m[ys,xs],red,0.95)
    for k in range(6): over(a,m_line(X,Y,cx-90+rng.uniform(0,180),cy+140+rng.uniform(0,60),cx-90+rng.uniform(0,180),cy+200+rng.uniform(0,90),4),red,0.6)   # drips
    return a
