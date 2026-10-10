"""Physical corrections for the review candidate; no runtime bindings renamed."""
import bpy, math
from mathutils import Vector, Matrix
import crk, rh_stlib as S
import rh_support_registry as SUPPORT
import rh_crane_identity_mount

def replace_world(o,k,key,material):
    made=k.build(o.users_collection[0],'RH temporary',{key:material})
    assert len(made)==1
    tmp=made[0]; me=tmp.data; me.transform(o.matrix_world.inverted())
    old=o.data; o.data=me; bpy.data.objects.remove(tmp,do_unlink=True)
    if old.users==0: bpy.data.meshes.remove(old)

def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]

def rods(K,M,text):
    # Keep the original swept envelope and bindings, but give the small pins
    # round sections and a quieter finish than the primary drive guide.
    for tag,x in (('A',-1.4),('B',1.4)):
        pins=next(o for o in bpy.data.objects if o.name.startswith('RP bank '+tag+' absorber pins'))
        lo,hi=bounds(pins); kit=crk.Kit()
        for i in range(8):
            for r,off in ((.40,0),(.28,math.pi/8)):
                th=i*math.pi/4+off
                kit.cyl(('absorbers','ABSORBER'),x+r*math.cos(th),r*math.sin(th),lo[2],hi[2],.026,16,0)
        replace_world(pins,kit,'ABSORBER',M['ABSORBER'])
        guide=bpy.data.objects.get('BANK_'+tag+'_DRIVE_COLUMN')
        if guide and guide.type=='MESH':
            for i in range(len(guide.data.materials)): guide.data.materials[i]=M['DRIVE_METAL']
        for o in bpy.data.objects:
            if o.type=='MESH' and o.name.startswith('RP bank '+tag+' pin tips'):
                for i in range(len(o.data.materials)): o.data.materials[i]=M['BANK_SIGNAL']
    # Registered spacer grids: each pin passes through an actual open sleeve.
    # The old spoke strips passed straight through the inner absorber ring.
    for tag,x in (('A',-1.4),('B',1.4)):
        a=next(o for o in bpy.data.objects if o.name.startswith('R2 bank A ') and 'rod band TRIM' in o.name)
        old=next(o for o in bpy.data.objects if o.name.startswith('R2 bank '+tag+' ') and 'rod band TRIM' in o.name)
        zs=sorted({round((a.matrix_world@v.co).z,4) for v in a.data.vertices})
        levels=[]
        for z in zs:
            if not levels or z-levels[-1][-1]>.5: levels.append([])
            levels[-1].append(z)
        kit=crk.Kit()
        for level in levels:
            z0,z1=min(level),max(level)
            def sleeve(cx,cy,ri,ro):
                S.lathe(kit,('grid','STEEL'),cx,cy,[(ri,z0),(ro,z0),(ro,z1),(ri,z1),(ri,z0)],32)
            sleeve(x,0,.14,.16); sleeve(x,0,.445,.463)
            for i in range(8):
                for r,off in ((.40,0),(.28,math.pi/8)):
                    th=i*math.pi/4+off; c,s=math.cos(th),math.sin(th)
                    sleeve(x+r*c,r*s,.031,.039)
                    # Two-millimetre welded engagement across the curved sleeve
                    # wall gives a real contact area rather than tangency alone.
                    for lo,hi in ((.16,r-.039+.002),(r+.039-.002,.453)):
                        kit.box(('grid','STEEL'),x+(lo+hi)/2*c,(lo+hi)/2*s,z0+.015,z1-.015,hi-lo,.018,th,0)
        replace_world(old,kit,'STEEL',M['STEEL'])
    # The state collar keeps its animation/name but gets a metal shell. A small
    # separate ring provides state indication without making all metal emissive.
    a=next(o for o in bpy.data.objects if o.name.startswith('R2 bank A ') and 'rod band GLOW' in o.name)
    for tag,x in (('A',-1.4),('B',1.4)):
        o=next(o for o in bpy.data.objects if o.name.startswith('R2 bank '+tag+' ') and 'rod band GLOW' in o.name)
        zz=sorted({round((a.matrix_world@v.co).z,4) for v in a.data.vertices}); groups=[]
        for z in zz:
            if not groups or z-groups[-1][-1]>.5: groups.append([])
            groups[-1].append(z)
        shell=crk.Kit()
        for band in groups:
            z0,z1=min(band),max(band)
            S.lathe(shell,('collar','STEEL'),x,0,[(.433,z0),(.479,z0),(.479,z1),(.433,z1),(.433,z0)],48)
        replace_world(o,shell,'STEEL',M['STEEL'])
        kit=crk.Kit()
        for g in groups:
            z=sum((min(g),max(g)))/2
            S.lathe(kit,('indicator','BANK_SIGNAL'),x,0,[(.479,z-.009),(.486,z-.009),(.486,z+.009),(.479,z+.009),(.479,z-.009)],40)
        for ob in kit.build(o.users_collection[0],'RH refine bank '+tag+' moving',M):
            ob.parent=o.parent; ob.matrix_parent_inverse=o.parent.matrix_world.inverted()
        # Service hatch occupies the existing front cassette, avoiding hydraulic
        # fittings at x+.62 and the two orange clamp bands.
        g='bank service '+tag
        K.bx((g,'BLACK'),x-.54,x+.54,-1.218,-1.208,10.77,11.55,.004)
        S.door(K,g,'-y',-1.218,x-.50,x+.50,10.80,11.52,'l0','PANEL','T',proud=.009,hz=10.98)
        text('bank letter '+tag,tag,(x,-1.229,11.21),(0,-1,0),.38)
        text('bank service id '+tag,'DRIVE '+tag+' / ACCESS',(x,-1.230,10.86),(0,-1,0),.042)
        S.nameplate(K,g,'-y',-1.212,x,10.45,.78,.09,'PANEL',True)
        text('bank lower id '+tag,'CRD-'+tag+' / MATCHED BANK',(x,-1.218,10.45),(0,-1,0),.045)
        # Depth comes from an open perimeter and individually inclined blades,
        # not black lines painted onto a single front rectangle.
        S.louvres(K,g,'STEEL','-y',-1.228,x-.30,x+.30,10.91,11.035,3,.018,True,'PANEL')
        # Fixed housing load goes through steel hangers and transverse yokes.
        # The retained black gland cables are services, not suspension members.
        for sx in (-1,1):
            xx=x+sx*.62
            K.bx(('bank suspension '+tag,'STEEL'),xx-.045,xx+.045,-.62,.62,13.49,13.52,.003)
            for sy in (-1,1):
                yy=sy*.42
                K.bx(('bank suspension '+tag,'STEEL'),xx-.075,xx+.075,yy-.075,yy+.075,12.62,12.64,.003)
                K.cyl(('bank suspension '+tag,'GALV'),xx,yy,12.64,13.49,.025,20,0)
                for z in (12.64,13.45): K.cyl(('bank suspension '+tag,'STEEL'),xx,yy,z,z+.04,.042,6,.002)
                S.anchor(K,'bank suspension '+tag,xx,sy*.52,13.52,.010,.028)
        for sx in (-1,1):
            for sy in (-1,1):
                xx=x+sx; yy=sy
                ya,yb=sorted((sy*.53,sy*1.04))
                K.bx(('bank service terminations '+tag,'STEEL'),xx-.025,xx+.025,ya,yb,13.80,13.83,.002)
                K.bx(('bank service terminations '+tag,'PANEL'),xx-.07,xx+.07,yy-.065,yy+.065,13.79,13.90,.004)
                K.cyl(('bank service terminations '+tag,'BRASS'),xx,yy,13.775,13.80,.030,12,0)
        SUPPORT.register('refinement props','bank '+tag+' lower hangers','RH refine bank suspension '+tag,'BANK_'+tag+'_FIXED_HOUSING',[(x+sx*.62,sy*.42,12.62) for sx in (-1,1) for sy in (-1,1)])
        SUPPORT.register('refinement props','bank '+tag+' upper yokes','RH refine bank suspension '+tag,'RH pool girder YELLOW',[(x+sx*.62,sy*.52,13.52) for sx in (-1,1) for sy in (-1,1)],(0,0,1),'suspension')

def legacy_props(K,M,text):
    drums=((5.2,9.5),(5.9,9.9),(5.5,8.9),(-6.6,-8.3),(-7.35,-8.65))
    for o in list(bpy.data.objects):
        if o.name.startswith(('R2 floor drums ','R2 floor crates ','MERGED 23 R2 FLOOR  R2 cone ')):
            bpy.data.objects.remove(o,do_unlink=True); continue
        if o.type=='MESH' and o.name.startswith('MERGED 23 R2 FLOOR  R2 iron '):
            lo,hi=bounds(o); x,y=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2
            if hi[2]<.8 and any(math.hypot(x-dx,y-dy)<.05 for dx,dy in drums):
                bpy.data.objects.remove(o,do_unlink=True)
    for i,(x,y) in enumerate(drums): S.drum(K,'legacy drums',x,y,'RED' if i%2==0 else 'GALV',h=.88)
    for x,y in ((6.4,5.6),(7.6,5.1),(-6.7,.4)):
        S.cone(K,'legacy cones',x,y)
        SUPPORT.register('refinement props','legacy cone bearing '+str((x,y)),
            'RH refine legacy cones RUBBER','R2 floor',[(x+dx,y+dy,0) for dx,dy in ((-.12,-.12),(.12,-.12),(-.12,.12),(.12,.12))])
    # Two supported transport cases replace the skewed three-box stack.
    for x,y in ((-9.95,5.6),(-7.6,5.6)):
        g='transport cases'
        K.bx((g,'AUDI_SATIN'),x-.42,x+.42,y-.34,y+.34,.04,.68,.025)
        for sx in (-1,1):
            for sy in (-1,1):
                K.bx((g,'RUBBER'),x+sx*.38-.035,x+sx*.38+.035,y+sy*.30-.035,y+sy*.30+.035,0,.09,.01)
                K.bx((g,'STEEL'),x+sx*.41-.02,x+sx*.41+.02,y+sy*.33-.02,y+sy*.33+.02,.06,.67,.004)
        K.bx((g,'STEEL'),x-.435,x+.435,y-.355,y+.355,.68,.705,.006)
        for dx in (-.27,.27):
            S.handle_bar(K,g,'-y',y-.341,x+dx,.40,.16,0,'STEEL',False)
        # Saved-scene frontal probes select the actual unobstructed aisle face.
        side=1 if x < -9 else -1
        face='+x' if side==1 else '-x'
        S.nameplate(K,g,face,x+side*.42,y,.56,.50,.10,'PANEL',True)
        text('case id '+str((x,y)),'TOOLS / STORE',(x+side*.426,y,.56),(side,0,0),.055)
        SUPPORT.register('refinement props','case inventory plate '+str((x,y)),
            'RH refine transport cases PANEL','RH refine transport cases AUDI_SATIN',
            [(x+side*.42,y+dy,.56) for dy in (-.20,.20)],(-side,0,0),'wall')
    # Drum inventory is readable text on registered shell patches, not anonymous
    # decorative stripes. No unverified contents or engineering ratings invented.
    all_drums=list(drums)+[(-3.84,4.93),(-3.14,4.93),(-3.84,5.67),(-3.14,5.67),(6.52,-3.70),(7.18,-3.70),(6.52,-2.98),(7.18,-2.98)]
    for i,(x,y) in enumerate(all_drums):
        z=.135 if i>=5 else 0
        face='+x' if i in (0,4) else ('+y' if i in (3,7,8,11,12) else '-y')
        if z:
            pallet_x=-3.49 if i<9 else 6.85
            bars=[pallet_x-.615+k*.1025 for k in range(13)]
            anchors=[(min(bars,key=lambda bx:abs(bx-(x+side*.18))),y,z) for side in (-1,1)]
        else:anchors=[(x+.20*math.cos(a),y+.20*math.sin(a),0) for a in (0,math.pi/2,math.pi,3*math.pi/2)]
        SUPPORT.register('refinement props','drum %02d'%(i+1),'RH refine legacy drums' if i<5 else 'RH stations props','RH stations spill pallets' if z else 'R2 floor',anchors)
        n=S.nrm(face); tangent=Vector((-n.y,n.x,0))
        for side in (-1,1):
            p=Vector((x,y,z+.48))+n*.272+tangent*side*.08
            S.disc(K,'drum label mounts','STEEL',p,n,.008,.019,seg=8)
        axis=0 if abs(n.x) else 1
        centre=(x,y)[axis]+n[axis]*.287; lateral=y if axis==0 else x
        S.nameplate(K,'drum labels',face,centre,lateral,z+.48,.20,.075,'PANEL',False)
        text('drum inventory '+str(i),'DR-%02d'%(i+1),Vector((x,y,z+.48))+n*.292,n,.044)

def equipment(K,M,text):
    # Phase-load dial numbers occupy the outer scale. Keep the pointer inside
    # that scale so its motion never sweeps over the small printed numerals.
    for needle in bpy.data.objects:
        if needle.type!='CURVE' or not needle.name.startswith('08 GRID DEMAND.phase load.needle'): continue
        needle.data=needle.data.copy()
        for spline in needle.data.splines:
            if not spline.points: continue
            hub=spline.points[0].co.copy()
            for point in list(spline.points)[1:]:
                point.co=hub+(point.co-hub)*.42
    def remount_glyph(name,p,n,scale=1):
        o=bpy.data.objects.get(name)
        if not o: return
        lo,hi=bounds(o); centre=Vector([(a+b)/2 for a,b in zip(lo,hi)])
        oldnormal=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        if o.type=='MESH':
            # Converted lettering may have its former rotation baked into the
            # vertices. Its matrix Z alone then describes the wrong plane.
            import numpy as np
            coordinates=np.array([list(o.matrix_world@v.co) for v in o.data.vertices])
            values,vectors=np.linalg.eigh(np.cov(coordinates.T))
            oldnormal=Vector(vectors[:,int(np.argmin(values))]).normalized()
            if oldnormal.dot(Vector(n))<0:oldnormal=-oldnormal
        rotation=oldnormal.rotation_difference(Vector(n).normalized())
        if o.type=='MESH':
            transform=Matrix.Translation(Vector(p))@rotation.to_matrix().to_4x4()@Matrix.Scale(scale,4)@Matrix.Translation(-centre)@o.matrix_world
            new_matrix=Matrix.Translation(Vector(p))@Vector(n).to_track_quat('Z','Y').to_matrix().to_4x4()
            o.data.transform(new_matrix.inverted()@transform)
            o.matrix_world=new_matrix
        elif o.type=='FONT':
            o.matrix_world=Matrix.Translation(Vector(p))@rotation.to_matrix().to_4x4()@Matrix.Scale(scale,4)@Matrix.Translation(-centre)@o.matrix_world
    # Retained identification lettering now sits on supported faces of the
    # replacement assemblies rather than on the removed diagonal housings.
    S.nameplate(K,'cart identity','-y',6.675,-9.0,.50,.66,.13,'PANEL',True)
    for x in (-9.25,-8.75):
        K.bx(('cart identity supports','STEEL'),x-.012,x+.012,6.71,6.735,.38,.55,.002)
        K.bx(('cart identity supports','STEEL'),x-.012,x+.012,6.674,6.735,.485,.515,.002)
    remount_glyph('MF19 identity.legend',(-9.0,6.669,.50),(0,-1,0))
    old=bpy.data.objects.get('MF19 identity')
    if old: bpy.data.objects.remove(old,do_unlink=True)
    S.nameplate(K,'sample inlet identity','-y',-3.744,1.72,1.53,.12,.06,'PANEL',False)
    remount_glyph('WF F sample inlet ID.legend',(1.72,-3.749,1.53),(0,-1,0),1.8)
    from r2lib import WALLS
    w=WALLS[5]; p=w.pt(1.8,.116)
    for du in (-.30,.30):
        a=w.pt(1.8+du,.014); b=w.pt(1.8+du,.08)
        K.prism(('cart dock mounts','STEEL'),(a.x,a.y,2.80),(b.x,b.y,2.80),.012,.012,12,0,True,0)
    q=w.pt(1.8,.095)
    K.box(('cart dock identity','PANEL'),q.x,q.y,2.70,2.90,.95,.03,w.angle,.004)
    remount_glyph('WF F wall dock identity.legend',(p.x,p.y,2.8),(w.n.x,w.n.y,0))
    old=bpy.data.objects.get('WF F wall dock identity')
    if old: bpy.data.objects.remove(old,do_unlink=True)
    n=Vector((-.70710678,-.70710678,0)); c=Vector((7.52,8.12,1.09))
    # A small registered flat patch clears the cask's lower cooling fins.
    for dx in (-.11,.11):
        t=Vector((-n.y,n.x,0)); a=c+n*.60+t*dx; b=c+n*.73+t*dx
        K.prism(('waste identity mounts','STEEL'),a,b,.008,.008,12,0,True,0)
    q=c+n*.735
    K.box(('waste identity','PANEL'),q.x,q.y,1.05,1.13,.32,.012,-math.pi/4,.002)
    remount_glyph('04 WASTE.number.legend',c+n*.743,n)
    for i,y in enumerate((-1.88,-1.20,-.52)):
        S.nameplate(K,'switchgear identity','-x',9.469,y,2.065,.39,.11,'PANEL',True)
        text('switchgear id '+str(i),'SG-%02d / L%d'%(i+1,3-i),(9.462,y,2.065),(-1,0,0),.041)
        for j,z in enumerate((.29,.74,1.18)):
            text('switchgear circuit '+str((i,j)),'C%02d'%(i*3+j+1),(9.461,y-.11,z),(-1,0,0),.039)
    for x,tag in ((3.30,'EC-1'),(1.80,'EC-2')):
        # A supported protective sight gauge and contrasting calibration marks.
        for z in (1.03,2.15):
            K.bx(('sight brackets','STEEL'),x+.26,x+.39,-9.25,-9.135,z-.018,z+.018,.003)
        for z in (1.0,2.15):
            # The nominal vessel radius is not its front coordinate off-axis.
            front=-9.65+math.sqrt(.46*.46-.30*.30)
            K.prism(('sight nozzle roots','BRASS'),(x+.30,front-.01,z),(x+.30,-9.19,z),.017,.017,16,0,True,0)
        for side in (-1,1): K.cyl(('sight guards','STEEL'),x+.31+side*.047,-9.15,1.03,2.15,.009,12,0)
        for k in range(6):
            K.bx(('sight scale','WHITE'),x+.365,x+.405,-9.145,-9.137,1.08+k*.195,1.091+k*.195,0)
        for dx in (-.12,.12):
            S.disc(K,'vessel plaque mounts','STEEL',(x+dx,-9.207,1.82),(0,1,0),.008,.027,seg=8)
        S.nameplate(K,'vessel ID','+y',-9.185,x,1.82,.30,.12,'PANEL',True)
        text(tag+' vessel label',tag,(x,-9.179,1.82),(0,1,0),.074)
        # The original four-leg cross-frame ends at .52; the vessel bottom
        # begins at .60. A circular seat transfers load onto both frame beams.
        K.cyl(('vessel seat','STEEL'),x,-9.65,.52,.601,.31,40,.002)
        for sx in (-1,1):
            for sy in (-1,1):
                px,py=x+sx*.30,-9.65+sy*.30
                K.prism(('vessel braces','STEEL'),(px,py,.15),
                    (x+sx*.20,-9.65+sy*.20,.50),.018,.018,12,0,True,0)
        if tag=='EC-1':
            # Removable sight-gauge shield; the centre stays open for inspection.
            for zz in (1.03,2.15):
                K.bx(('EC1 sight shield','GALV'),x+.25,x+.37,-9.16,-9.135,zz-.025,zz+.025,.003)
            K.bx(('EC1 sight shield','GALV'),x+.25,x+.265,-9.16,-9.135,1.03,2.15,.003)
        else:
            # EC2 has a supported sensor junction/service gland and cable. Both
            # accumulators retain the same verified hydraulic ports/circuit.
            for dx in (-.31,-.19):
                front=-9.65+math.sqrt(.46*.46-dx*dx)
                for z in (1.575,1.685):
                    K.prism(('EC2 sensor standoffs','STEEL'),(x+dx,front-.002,z),(x+dx,-9.20,z),.009,.009,12,0,True,0)
            S.jbox(K,'EC2 sensor service','+y',-9.20,x-.25,1.63,.20,.17,.10,'AUDI_SATIN',1)
            S.cable_run(K,'EC2 sensor cable',[(x-.25,-9.15,1.47),(x-.25,-9.10,1.39),(x-.07,-9.18,1.49)],.007)
    # Proper flat blind covers with a shallow machined centre, behind bolt heads.
    for x,sg in ((1.62,-1),(3.48,1)):
        S.disc(K,'blind covers','STEEL',(x,-8.84,.78),(sg,0,0),.184,.012,off=.033,seg=32,ch=.002)
    S.nameplate(K,'turbine oil ID','-x',8.870,-4.16,.98,.55,.08,'PANEL',True)
    # An angled identification hood follows the actual oblique service opening.
    # Its two standoffs bear on the south cabinet door; no pier is cut away.
    vn=Vector((-.70710678,-.70710678,0));vt=Vector((.70710678,-.70710678,0))
    vc=Vector((10.40,6.739,2.44))+vn*.12
    K.box(('vent actuator ID','PANEL'),vc.x,vc.y,2.40,2.48,.30,.008,-math.pi/4,.002)
    for side in (-1,1):
        endpoint=vc+vt*(side*.11)
        K.prism(('vent actuator ID mounts','STEEL'),(endpoint.x,6.744,2.44),endpoint,.009,.009,12,0,True,0)
    for z in (1.26,1.10): S.nameplate(K,'bearing service labels','-x',9.546,-5.75,z,.18,.065,'PANEL',False)
    # Functional information belongs beside the actual instrument/controls.
    for name,body,p,n,size in (
        ('turbine pressure','PRESSURE',(9.540,-5.75,1.10),(-1,0,0),.032),
        ('turbine instrument','T-01',(9.540,-5.75,1.26),(-1,0,0),.043),
        ('turbine oil','LUBE OIL / SERVICE',(8.863,-4.16,.98),(-1,0,0),.048),
        ('vent actuator','DAMPER / V-03',vc+vn*.006,vn,.032)):
        text(name,body,p,n,size)
    # A shallow removable coupling guard leaves the shaft visible from above.
    for x in (9.69,10.21):
        K.bx(('coupling guard','ORANGE'),x-.012,x+.012,-5.66,-5.50,.455,1.44,.003)
    for y in (-5.65,-5.51):
        K.prism(('coupling guard','ORANGE'),(9.69,y,1.44),(10.21,y,1.44),.014,.014,12,0,True,0)
    # The broad front service face is the lube-oil cabinet, not the shaft guard.
    # A stand-off impact frame has real corner elbows and visible bolted mounts;
    # it leaves the door handles and oil-service identification unobstructed.
    for y in (-4.49,-3.21):
        K.prism(('turbine service guard','STEEL'),(8.81,y,.50),(8.81,y,1.15),.025,.025,16,0,True,0)
        for z in (.58,1.07):
            K.bx(('turbine guard mounts','STEEL'),8.82,8.89,y-.045,y+.045,z-.040,z+.040,.003)
            S.disc(K,'turbine guard bolts','GALV',(8.82,y,z),(-1,0,0),.011,.01,seg=8)
    for z in (.50,1.15):
        K.prism(('turbine service guard','STEEL'),(8.81,-4.49,z),(8.81,-3.21,z),.025,.025,16,0,True,0)

def sweep_frames(points):
    frames=[];u=None
    for i,p in enumerate(points):
        t=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        if u is None:u=Vector((1,0,0)) if abs(t.x)<.9 else Vector((0,1,0))
        u=u-t*u.dot(t)
        if u.length<1e-8:
            u=Vector((0,1,0));u-=t*u.dot(t)
        u.normalize();frames.append((u.copy(),t.cross(u).normalized()))
    return frames

def continuous_sweep(K,key,points,radius,segments=16,frames=None):
    """One closed smooth skin, with shared rings instead of separate prisms."""
    bm=K.get(key);rings=[]
    for p,(u,v) in zip(points,frames or sweep_frames(points)):
        rings.append([bm.verts.new(p+radius*(u*math.cos(j*2*math.pi/segments)+v*math.sin(j*2*math.pi/segments))) for j in range(segments)])
    bm.faces.new(rings[0][::-1]);bm.faces.new(rings[-1])
    for a,b in zip(rings,rings[1:]):
        for j in range(segments):
            f=bm.faces.new((a[j],a[(j+1)%segments],b[(j+1)%segments],b[j]));f.smooth=True

def hook_block(M,body,x):
    """Open cheek plates, a grooved sheave and an actual swivel bearing."""
    frame=crk.Kit();wheel=crk.Kit();bearing=crk.Kit()
    def ring_y(K,key,profile,centre_y):
        bm=K.get(key);old=set(bm.verts)
        S.lathe(K,key,0,0,profile+[profile[0]],seg=64)
        for v in bm.verts:
            if v not in old:
                q=v.co.copy();v.co=Vector((x+q.x,centre_y+q.z,10.77-q.y))
    for yy in (4.494,4.690):
        ring_y(frame,('frame','STEEL'),[(.148,0),(.174,0),(.174,.016),(.148,.016)],yy)
        ring_y(frame,('frame','STEEL'),[(.022,0),(.058,0),(.058,.016),(.022,.016)],yy)
        for i in range(4):
            a=math.pi/4+i*math.pi/2;u=Vector((math.cos(a),0,math.sin(a)));v=Vector((-u.z,0,u.x));c=Vector((x,yy+.008,10.77))
            corners=[c+u*r+v*s+Vector((0,t,0)) for r in (.052,.156) for s in (-.012,.012) for t in (-.008,.008)]
            frame.hull(('frame','STEEL'),corners,.001)
    ring_y(frame,('frame','STEEL'),[(0,0),(.022,0),(.022,.236),(0,.236)],4.482)
    for yy,d in ((4.494,-1),(4.706,1)):
        S.disc(frame,'frame','STEEL',(x,yy,10.77),(0,d,0),.036,.012,seg=32,ch=.001)
        for i in range(4):
            a=math.pi/4+i*math.pi/2
            S.disc(frame,'frame','STEEL',(x+.163*math.cos(a),yy,10.77+.163*math.sin(a)),(0,d,0),.007,.007,seg=6)
    frame.bx(('frame','STEEL'),x-.08,x+.08,4.494,4.706,10.588,10.615,.002)
    ring_y(wheel,('sheave','IRON'),[(.022,-.05),(.131,-.05),(.137,-.044),(.137,-.031),(.122,-.024),(.109,-.019),(.108,0),(.109,.019),(.122,.024),(.137,.031),(.137,.044),(.131,.05),(.022,.05)],4.6)
    S.lathe(bearing,('swivel','GALV'),x,4.6,[(.048,10.54),(.076,10.54),(.076,10.588),(.067,10.588),(.067,10.58),(.048,10.58),(.048,10.54)],seg=64)
    objects={}
    for K,tag in ((frame,'frame'),(wheel,'sheave'),(bearing,'swivel')):
        ob=K.build(body.users_collection[0],'RH refine main hook',M)[0]
        if tag=='frame':
            objects['frame_mesh']=ob
            objects['frame']=bpy.data.objects['R2 crane trolley crane TRIM']
        else:
            ob.parent=body;ob.matrix_parent_inverse=body.matrix_world.inverted();objects[tag]=ob
    SUPPORT.register('refinement props','hook sheave on axle',objects['sheave'].name,objects['frame'].name,[(x,4.6,10.792)])
    SUPPORT.register('refinement props','hook swivel to crossmember',objects['swivel'].name,objects['frame'].name,[(x+s*.071,4.6,10.588) for s in (-1,1)],(0,0,1),'ceiling')
    SUPPORT.register('refinement props','hook retainer on swivel',body.name,objects['swivel'].name,[(x+s*.055,4.6,10.58) for s in (-1,1)])
    SUPPORT.register('refinement props','hook retainer to crossmember',body.name,objects['frame'].name,[(x+s*.055,4.6,10.588) for s in (-1,1)],(0,0,1),'ceiling')
    return objects

def main_trolley(K,M,bridge):
    body=bpy.data.objects['R2 crane trolley crane IRON'];x=body.matrix_world.translation.x
    kit=crk.Kit();cover=crk.Kit()
    rope_material=bpy.data.materials.get('RH refine crane wire rope') or bpy.data.materials.new('RH refine crane wire rope')
    rope_material.use_nodes=True
    shader=rope_material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.11,.115,.11,1)
    shader.inputs['Metallic'].default_value=.80;shader.inputs['Roughness'].default_value=.55
    M['CRANE_ROPE']=rope_material
    # Two running rails bear on the original bridge's top flange.
    rails=crk.Kit()
    for y in (4.27,4.93):rails.bx(('trolley rails','STEEL'),-9.7,9.7,y-.025,y+.025,15.35,15.38,.002)
    for o in rails.build(bridge.users_collection[0],'RH refine crane',M):
        o.parent=bridge;o.matrix_parent_inverse=bridge.matrix_world.inverted()
    for y in (4.27,4.93):
        SUPPORT.register('refinement props','trolley rail to bridge '+str(y),
            'RH refine crane trolley rails STEEL',bridge.name,
            [(xx,y,15.35) for xx in (-8,-4,4,8)])
    for y in (4.27,4.93):
        kit.bx(('body','STEEL'),x-.64,x+.64,y-.17,y+.17,15.62,15.70,.004)
        for dx in (-.48,.48):
            S.disc(kit,'body','STEEL',(x+dx,y-.07,15.50),(0,1,0),.12,.14,seg=32,ch=.002)
            S.disc(kit,'body','STEEL',(x+dx,y-.12,15.50),(0,1,0),.026,.24,seg=16)
            for yy in (y-.115,y+.115):
                S.disc(kit,'body','STEEL',(x+dx,yy-.025,15.50),(0,1,0),.045,.05,seg=20)
                kit.bx(('body','STEEL'),x+dx-.045,x+dx+.045,yy-.025,yy+.025,15.50,15.66,.003)
    # Coaxial twin grooved drums give the two retained rope legs real exits.
    for dx in (-.12,.12):
        S.disc(kit,'body','STEEL',(x+dx-.075,4.8,15.88),(1,0,0),.20,.15,seg=40)
        for end in (-.085,.075):S.disc(kit,'body','STEEL',(x+dx+end,4.8,15.88),(1,0,0),.235,.010,seg=40)
        for j in range(6):S.disc(kit,'body','STEEL',(x+dx-.066+j*.024,4.8,15.88),(1,0,0),.203,.008,seg=40)
        # The rope continues to the drum tangent; it is not a rigid steel
        # extension spliced onto the retained hanging line.
        S.torus(kit,'body','STEEL',(x+dx,4.6,15.40),(0,0,1),.026,.003,16,6)
    # Matched physical wire sections retain the named straight-line rig bounds.
    # All sections use shared transported frames and helix phase at their joins.
    def upper(dx):
        p=[Vector((x+dx,4.6,15.40))]
        p.extend(Vector((x+dx-.006*j/40,4.6-.012*j/40,15.40+.48*j/40)) for j in range(1,41))
        p.extend(Vector((x+dx-.006,4.8+.212*math.cos(math.pi-math.pi*j/64),15.88+.212*math.sin(math.pi-math.pi*j/64))) for j in range(1,33))
        return p
    sections=[('extension',list(reversed(upper(-.12)))),
        ('main',[Vector((x-.12,4.6,15.40-4.50*j/360)) for j in range(361)]),
        ('extension',[Vector((x-.12,4.6,10.90-.13*j/12)) for j in range(13)] +
            [Vector((x+.12*math.cos(math.pi+math.pi*j/96),4.6,10.77+.12*math.sin(math.pi+math.pi*j/96))) for j in range(1,97)] +
            [Vector((x+.12,4.6,10.77+.13*j/12)) for j in range(1,13)]),
        ('main',[Vector((x+.12,4.6,10.90+4.50*j/360)) for j in range(361)]),
        ('extension',upper(.12))]
    path=[];ranges=[]
    for role,points in sections:
        first=max(0,len(path)-1)
        path.extend(points if not path else points[1:])
        ranges.append((role,first,len(path)-1))
    frames=sweep_frames(path);ropes=crk.Kit();extensions=crk.Kit()
    def add_sections(points,radius,segments,all_frames):
        for role,first,last in ranges:
            continuous_sweep(ropes if role=='main' else extensions,('rope','CRANE_ROPE'),points[first:last+1],radius,segments,all_frames[first:last+1])
    add_sections(path,.008,16,frames)
    for strand in range(6):
        points=[];distance=0
        for j,(centre,(u,v)) in enumerate(zip(path,frames)):
            if j:distance+=(centre-path[j-1]).length
            angle=2*math.pi*(distance/.10+strand/6)
            points.append(centre+.010*(u*math.cos(angle)+v*math.sin(angle)))
        add_sections(points,.002,8,sweep_frames(points))
    cable=bpy.data.objects['R2 crane trolley crane CABLE']
    replace_world(cable,ropes,'CRANE_ROPE',rope_material)
    extension=extensions.build(body.users_collection[0],'RH refine crane hoist rope',M)[0]
    extension.parent=cable;extension.matrix_parent_inverse=cable.matrix_world.inverted()
    block=hook_block(M,body,x)
    SUPPORT.register('refinement props','reeved rope on sheave',extension.name,block['sheave'].name,[(x,4.6,10.662)],(0,0,1),'ceiling')
    S.disc(kit,'body','STEEL',(x-.44,4.8,15.88),(1,0,0),.035,.88,seg=20)
    for dx in (-.38,.38):
        kit.bx(('body','STEEL'),x+dx-.045,x+dx+.045,4.735,4.865,15.70,15.88,.004)
        S.disc(kit,'body','STEEL',(x+dx-.04,4.8,15.88),(1,0,0),.075,.08,seg=24)
    kit.bx(('body','STEEL'),x+.42,x+.62,4.65,4.95,15.75,16.05,.010)
    S.disc(kit,'body','STEEL',(x+.62,4.8,15.88),(1,0,0),.11,.38,seg=32)
    for j in range(7):S.disc(kit,'body','STEEL',(x+.65+j*.045,4.8,15.88),(1,0,0),.12,.010,seg=32)
    # An open hood shelters the drum without concealing its front rope exits.
    cover.bx(('cover','AUDI_SATIN'),x-.46,x+.46,4.53,5.07,16.13,16.16,.006)
    cover.bx(('cover','AUDI_SATIN'),x-.46,x+.46,5.05,5.07,15.70,16.13,.003)
    cover.bx(('cover','AUDI_SATIN'),x-.46,x+.46,4.51,4.53,16.11,16.13,.003)
    for dx in (-.45,.45):cover.bx(('cover','AUDI_SATIN'),x+dx-.012,x+dx+.012,4.53,5.07,15.95,16.13,.003)
    kit.bx(('body','STEEL'),x+.32,x+.38,4.195,4.22,15.70,16.09,.002)
    S.disc(kit,'body','STEEL',(x+.54,4.650,15.96),(0,-1,0),.022,.004,seg=24)
    # A mounted inspection lamp illuminates the drum inside the roof bay.
    lamp_c=Vector((x-.58,4.12,16.08));lamp_n=(Vector((x,4.8,15.88))-lamp_c).normalized()
    kit.cyl(('body','STEEL'),x-.58,4.12,15.70,16.08,.018,16,0)
    S.disc(kit,'body','STEEL',lamp_c-lamp_n*.05,lamp_n,.075,.10,seg=24,ch=.002)
    luminaire=crk.Kit();S.disc(luminaire,'diffuser','PRACTICAL',lamp_c+lamp_n*.051,lamp_n,.055,.008,seg=24)
    for ob in luminaire.build(body.users_collection[0],'RH refine main hoist lamp',M):ob.parent=body;ob.matrix_parent_inverse=body.matrix_world.inverted()
    light_data=bpy.data.lights.new('RH refine main hoist service','AREA');light_data.energy=18;light_data.color=(.96,.97,.96);light_data.shape='DISK';light_data.size=.11
    light_obj=bpy.data.objects.new(light_data.name,light_data);body.users_collection[0].objects.link(light_obj)
    light_obj.location=lamp_c+lamp_n*.062;light_obj.rotation_euler=lamp_n.to_track_quat('-Z','Y').to_euler();light_obj.parent=body;light_obj.matrix_parent_inverse=body.matrix_world.inverted()
    # Retain the hook-block relationship, replacing the old solid wedge hook.
    kit.cyl(('body','STEEL'),x,4.6,10.34,10.58,.048,64,0)
    kit.cyl(('body','STEEL'),x,4.6,10.58,10.588,.065,64,0)
    # One welded-free sweep gives the forged hook a smooth throat. Separate
    # capped prisms previously made its bend look like corrugated conduit.
    points=[Vector((x,4.6,10.34)),Vector((x-.035,4.6,10.25)),Vector((x-.04,4.6,10.20))]
    points.extend(Vector((x+.10+.14*math.cos(math.pi+i*.9*math.pi/48),4.6,10.20+.14*math.sin(math.pi+i*.9*math.pi/48))) for i in range(1,49))
    bm=kit.get(('body','STEEL'));rings=[]
    for j,p in enumerate(points):
        tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized();u=Vector((0,1,0));v=tangent.cross(u).normalized()
        radius=.035 if j<3 else .035*(1-.55*((j-2)/(len(points)-3))**4)
        rings.append([bm.verts.new(p+radius*(u*math.cos(a*2*math.pi/24)+v*math.sin(a*2*math.pi/24))) for a in range(24)])
    bm.faces.new(rings[0][::-1]);bm.faces.new(rings[-1])
    for lower,upper in zip(rings,rings[1:]):
        for j in range(24):face=bm.faces.new((lower[j],lower[(j+1)%24],upper[(j+1)%24],upper[j]));face.smooth=True
    # A guarded inspection lamp bears on the retained hook block and lights
    # the forged hook/socket instead of leaving this machinery in silhouette.
    hook_lamp=Vector((x+.30,4.40,10.405));hook_n=(Vector((x+.05,4.6,10.19))-hook_lamp).normalized()
    kit.bx(('body','STEEL'),x+.145,x+.175,4.484,4.494,10.785,10.815,.001)
    kit.prism(('body','STEEL'),(x+.16,4.484,10.80),hook_lamp,.014,.014,12,0,True,0)
    S.disc(kit,'body','STEEL',hook_lamp-hook_n*.025,hook_n,.045,.051,seg=32,ch=.001)
    guard_u=hook_n.cross(Vector((0,0,1))).normalized();guard_v=hook_n.cross(guard_u)
    guard_c=hook_lamp+hook_n*.033
    S.torus(kit,'body','STEEL',guard_c,hook_n,.041,.002,32,6)
    for axis in (guard_u,guard_v):
        kit.prism(('body','STEEL'),guard_c-axis*.041,guard_c+axis*.041,.002,.002,8,0,True,0)
        for side in (-1,1):
            kit.prism(('body','STEEL'),hook_lamp+hook_n*.026+axis*side*.041,guard_c+axis*side*.041,.002,.002,8,0,True,0)
    ld=bpy.data.lights.new('RH refine hook inspection service','AREA');ld.energy=3;ld.color=(.96,.97,.96);ld.shape='DISK';ld.size=.068
    lo=bpy.data.objects.new(ld.name,ld);body.users_collection[0].objects.link(lo)
    lo.location=hook_lamp+hook_n*.032;lo.rotation_euler=hook_n.to_track_quat('-Z','Y').to_euler();lo.parent=body;lo.matrix_parent_inverse=body.matrix_world.inverted()
    SUPPORT.register('refinement props','hook lamp bracket',body.name,block['frame'].name,[(x+.16,4.494,10.80)],(0,1,0),'wall')
    replace_world(body,kit,'STEEL',M['STEEL'])
    replace_world(bpy.data.objects['R2 crane trolley crane OLIVE'],cover,'AUDI_SATIN',M['AUDI_SATIN'])
    trim=bpy.data.objects['R2 crane trolley crane TRIM']
    import bmesh
    bm=bmesh.new();bm.from_mesh(trim.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if all((trim.matrix_world@v.co).z>15.3 or (trim.matrix_world@v.co).z<11.0 for v in f.verts)],context='FACES')
    bm.transform(trim.matrix_world)
    # The real lower carrier replaces the old box in its retained rig object.
    frame_mesh=block['frame_mesh']
    bm.from_mesh(frame_mesh.data)
    frame_data=frame_mesh.data
    bpy.data.objects.remove(frame_mesh,do_unlink=True)
    bpy.data.meshes.remove(frame_data)
    cap=crk.Kit();cap.bm[('cap','TRIM')]=bm
    cap.bx(('cap','TRIM'),x-.49,x+.49,4.505,4.535,16.13,16.17,.003)
    replace_world(trim,cap,'TRIM',M['STEEL'])
    led=bpy.data.objects['R2 crane trolley crane LAMPA'];led_material=led.data.materials[0]
    light=crk.Kit();S.disc(light,'led','LED',hook_lamp+hook_n*.026,hook_n,.034,.004,seg=32)
    replace_world(led,light,'LED',led_material)
    # A separate motor indicator shares the retained status material/driver.
    status=crk.Kit();S.disc(status,'motor status','LED',(x+.54,4.646,15.96),(0,-1,0),.014,.005,seg=24)
    status_ob=status.build(body.users_collection[0],'RH refine main hoist',dict(M,LED=led_material))[0]
    status_ob.parent=body;status_ob.matrix_parent_inverse=body.matrix_world.inverted()
    SUPPORT.register('refinement props','motor status lens mount',status_ob.name,body.name,[(x+.54,4.646,15.96)],(0,1,0),'wall')
    # The original x actions stay on all trolley parts; the bridge supplies
    # their shared transverse travel so wheels cannot leave their running rails.
    for part in bpy.data.objects:
        if part.name.startswith('R2 crane trolley '):
            part.parent=bridge;part.matrix_parent_inverse=bridge.matrix_world.inverted()
    SUPPORT.register('refinement props','main trolley wheels',body.name,'RH refine crane trolley rails',[(x+dx,y,15.38) for dx in (-.48,.48) for y in (4.27,4.93)])

def roof_service_lights(K,M,bridge):
    def lamp(name,p,target,power,parent=None):
        p=Vector(p);n=(Vector(target)-p).normalized();kit=crk.Kit()
        S.disc(kit,'housing','STEEL',p-n*.05,n,.09,.10,seg=24,ch=.003)
        S.disc(kit,'diffuser','PRACTICAL',p+n*.051,n,.07,.008,seg=24)
        objects=kit.build(bridge.users_collection[0],'RH refine '+name,M)
        data=bpy.data.lights.new('RH refine '+name,'AREA');data.energy=power;data.color=(.96,.97,.96);data.shape='DISK';data.size=.14
        o=bpy.data.objects.new(data.name,data);bridge.users_collection[0].objects.link(o)
        o.location=p+n*.062;o.rotation_euler=n.to_track_quat('-Z','Y').to_euler()
        if parent:
            for child in [*objects,o]:child.parent=parent;child.matrix_parent_inverse=parent.matrix_world.inverted()
    for x in (-9.65,9.65):
        kit=crk.Kit();p=Vector((x,4.10,15.05));target=(math.copysign(10,x),4.4,14.61)
        kit.prism(('mount','STEEL'),(x,4.252,15.08),p,.018,.018,12,0,True,0)
        for o in kit.build(bridge.users_collection[0],'RH refine running gear lamp',M):o.parent=bridge;o.matrix_parent_inverse=bridge.matrix_world.inverted()
        lamp('running gear service '+str(x),p,target,12,bridge)
    # Small downward fittings on actual bridge-face brackets reveal the box
    # webs and ribs without an unmounted scene fill or exposure change.
    for x in (-6.,2.5,6.):
        kit=crk.Kit()
        kit.bx(('plate','STEEL'),x-.06,x+.06,4.238,4.25,15.10,15.25,.002)
        kit.prism(('arm','STEEL'),(x,4.238,15.18),(x,3.87,15.18),.018,.018,12,0,True,0)
        for child in kit.build(bridge.users_collection[0],'RH refine bridge web light mount',M):
            child.parent=bridge;child.matrix_parent_inverse=bridge.matrix_world.inverted()
        SUPPORT.register('refinement props','bridge web light '+str(x),'RH refine bridge web light mount plate',bridge.name,
            [(x+dx,4.25,z) for dx in (-.035,.035) for z in (15.13,15.22)],(0,1,0),'wall')
        lamp('bridge web service '+str(x),(x,3.87,15.18),(x,4.26,14.95),40,bridge)
    K.bx(('gantry task lamp foot','STEEL'),6.75,6.85,1.35,1.45,13.865,13.885,.002)
    K.cyl(('gantry task lamp pole','STEEL'),6.8,1.4,13.885,15.05,.018,16,0)
    SUPPORT.register('refinement props','gantry task lamp seat','RH refine gantry task lamp foot','RH pool platform TREAD',[(6.8,1.4,13.865)])
    lamp('gantry access service',(6.8,1.4,15.05),(7.07,1.07,13.85),18)
    # Fixed housing hangers and cable glands share a service light, on a
    # modeled bracket touching the underside of the existing gantry flange.
    for x in (-1.4,1.4):
        K.bx(('housing service lamp mount','STEEL'),x-.03,x+.03,-.55,-.49,13.30,13.52,.002)
        SUPPORT.register('refinement props','housing lamp bracket '+str(x),'RH refine housing service lamp mount','RH pool girder YELLOW',[(x,-.52,13.52)],(0,0,1),'suspension')
        lamp('housing suspension service '+str(x),(x,-.52,13.30),(x,0,12.62),14)

def roof_bay_practicals(K,M):
    # Girder-web mounts carry roof uplighters and four shielded down heads.
    # The down heads reveal the fixed pool gantry front, not a global room fill.
    for x in (-7.5,-3.6,3.6,7.5):
        for y in (-2.1,2.1):
            prefix='RH refine roof bay '+str(x)+' '+str(y)
            kit=crk.Kit();p=Vector((x+.30,y,17.05))
            kit.bx(('plate','STEEL'),x+.0175,x+.0295,y-.05,y+.05,16.94,17.12,.001)
            kit.prism(('arm','STEEL'),(x+.0295,y,17.05),p,.018,.018,12,0,True,0)
            heads=[('up',p,Vector((x+1.5,y,17.8)),75)]
            if y<0:
                down=p+Vector((0,0,-.09));kit.prism(('yoke','STEEL'),p,down,.014,.014,12,0,True,0)
                heads.append(('down',down,Vector((x,-.53,14.0)),90))
            for label,center,target,power in heads:
                n=(target-center).normalized()
                S.disc(kit,label+' housing','STEEL',center-n*.045,n,.09,.09,seg=24,ch=.002)
                S.disc(kit,label+' lens','PRACTICAL',center+n*.046,n,.072,.008,seg=24)
                data=bpy.data.lights.new(prefix+' '+label,'AREA');data.energy=power;data.shape='DISK';data.size=.145;data.color=(.96,.97,.96)
                ob=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(ob)
                ob.location=center+n*.055;ob.rotation_euler=n.to_track_quat('-Z','Y').to_euler()
            kit.build('RH REFINEMENT',prefix,M)
            SUPPORT.register('refinement props',prefix+' web mount',prefix+' plate STEEL','RH walls girders STEEL',
                [(x+.0175,y+dy,z) for dy in (-.035,.035) for z in (16.97,17.09)],(-1,0,0),'wall')


def roof_perimeter_practicals(K,M):
    # The outer utility bays were in the girder shadows. Place service heads
    # on each girder's inner web face so the web cannot block their beam.
    for x in (-3.6,3.6):
        side=1 if x>0 else -1
        for y in (-8.,8.):
            prefix='RH refine perimeter utility '+str(x)+' '+str(y)
            kit=crk.Kit();p=Vector((x-side*.30,y,17.05))
            near=x-side*.0175;far=x-side*.0295
            kit.bx(('plate','STEEL'),min(near,far),max(near,far),y-.05,y+.05,16.94,17.12,.001)
            kit.prism(('arm','STEEL'),(far,y,17.05),p,.018,.018,12,0,True,0)
            n=(Vector((x,y*1.25,17.5))-p).normalized()
            S.disc(kit,'housing','STEEL',p-n*.045,n,.09,.09,seg=24,ch=.002)
            S.disc(kit,'lens','PRACTICAL',p+n*.046,n,.072,.008,seg=24)
            kit.build('RH REFINEMENT',prefix,M)
            SUPPORT.register('refinement props',prefix+' web mount',prefix+' plate STEEL','RH walls girders STEEL',
                [(near,y+dy,z) for dy in (-.035,.035) for z in (16.97,17.09)],(side,0,0),'wall')
            data=bpy.data.lights.new(prefix,'AREA');data.energy=45;data.shape='DISK';data.size=.145;data.color=(.96,.97,.96)
            ob=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(ob)
            ob.location=p+n*.055;ob.rotation_euler=n.to_track_quat('-Z','Y').to_euler()


def roof(K,M,text):
    bridge=bpy.data.objects['R2 crane bridge crane OLIVE']
    # The inherited decorative loop drove the trucks past the runway ends.
    # Keep its timing and frame-one placement inside the installed north bay,
    # between centre y4.6 and 4.3. The fixed pool crane occupies the centre
    # of the hall; this bridge cannot pass through it. Bank actions and
    # runtime ports are untouched.
    for part in bpy.data.objects:
        if not part.name.startswith('R2 crane bridge ') or not part.animation_data: continue
        action=part.animation_data.action
        if not action: continue
        curves=list(action.fcurves) if hasattr(action,'fcurves') else [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
        for curve in curves:
            if curve.data_path!='location' or curve.array_index!=1: continue
            for key in curve.keyframe_points:
                key.co.y *= -.30/1.6
                key.handle_left.y *= -.30/1.6
                key.handle_right.y *= -.30/1.6
            curve.update()
    kit=crk.Kit()
    # Replace the solid end trucks and solid girder while retaining the
    # animated bridge object. Wheels run on rail tops at z14.42, in open frames.
    body=crk.Kit()
    for y0,y1 in ((4.25,4.30),(4.535,4.555),(4.645,4.665),(4.90,4.95)):
        body.bx(('body','AUDI_SATIN'),-9.70,9.70,y0,y1,14.55,15.30,.004)
    for z0,z1 in ((14.50,14.55),(15.30,15.35)):
        for y0,y1 in ((4.25,4.55),(4.65,4.95)):
            body.bx(('body','AUDI_SATIN'),-9.70,9.70,y0,y1,z0,z1,.005)
    for a,b in ((-9.70,-9.60),(9.60,9.70)):
        body.bx(('body','AUDI_SATIN'),a,b,4.25,4.95,14.55,15.30,.005)
    for x in (-10.,10.):
        # Side plates leave wheel faces exposed and meet the bridge flanges.
        for xx in (x-.29,x+.29):
            body.bx(('body','AUDI_SATIN'),xx-.035,xx+.035,4.10,5.10,14.64,14.85,.008)
        body.bx(('body','AUDI_SATIN'),x-.325,x+.325,4.10,5.10,14.85,14.91,.008)
        for y in (4.25,4.95):
            S.disc(kit,'running gear','STEEL',(x-.13,y,14.61),(1,0,0),.19,.26,seg=32,ch=.003)
            S.disc(kit,'wheel axles','STEEL',(x-.33,y,14.61),(1,0,0),.030,.66,seg=16)
            for xx in (x-.29,x+.29):
                S.disc(kit,'wheel bearings','GALV',(xx-.04,y,14.61),(1,0,0),.065,.08,seg=20,ch=.002)
                kit.bx(('wheel bearing mounts','STEEL'),xx-.04,xx+.04,y-.07,y+.07,14.61,14.70,.004)
        kit.bx(('drive','AUDI_SATIN'),x-.22,x+.22,4.39,4.83,14.91,15.17,.012)
        S.disc(kit,'drive','AUDI',(x,4.82,15.04),(0,1,0),.10,.22,seg=24,ch=.005)
    replace_world(bridge,body,'AUDI_SATIN',M['AUDI_SATIN'])
    walkway=bpy.data.objects.get('R2 crane bridge crane IRON')
    if walkway:
        deck=crk.Kit()
        for ya,yb in ((4.05,4.25),(4.95,5.15)):
            deck.bx(('deck','STEEL'),-10,10,ya,yb,15.35,15.365,.002)
        for xx in range(-9,10,2):deck.bx(('deck','STEEL'),xx-.03,xx+.03,4.0,4.05,15.35,15.90,.004)
        replace_world(walkway,deck,'STEEL',M['STEEL'])
    trim=bpy.data.objects.get('R2 crane bridge crane TRIM')
    if trim:
        # Side trim ends before the wheel pockets; the upper guardrail stays.
        mesh=trim.data.copy(); mesh.transform(trim.matrix_world)
        for v in mesh.vertices:
            if v.co.z<15.0 and abs(v.co.x)>9.70: v.co.x=math.copysign(9.70,v.co.x)
        mesh.transform(trim.matrix_world.inverted()); trim.data=mesh
    for x in (-8.6,-6.2,-3.8,-1.4,1.4,3.8,6.2,8.6):
        for ya,yb in ((4.205,4.252),(4.948,4.995)):
            kit.bx(('bridge ribs','STEEL'),x-.018,x+.018,ya,yb,14.55,15.30,.003)
    for o in kit.build(bridge.users_collection[0],'RH refine crane bridge',M):
        o.parent=bridge; o.matrix_parent_inverse=bridge.matrix_world.inverted()
    o=text('crane identity','CRANE C-01 / CAPACITY: SEE CERTIFICATE',(0,4.236,15.04),(0,-1,0),.13)
    o.parent=bridge; o.matrix_parent_inverse=bridge.matrix_world.inverted()
    rh_crane_identity_mount.build(bridge, M, o)
    main_trolley(K,M,bridge)
    roof_service_lights(K,M,bridge)
    # Direct gantry-end access stays west of the x7.5 roof girder and
    # inboard of the crane runway. It needs no crossing of either structure.
    # rh_pool_surround builds the end-return opening before this gate is fitted.
    # Keep the merged rail mesh intact: a Boolean here could erase remote
    # disconnected handrail returns and posts.
    K.bx(('ladder top step','STEEL'),7.006,7.13,.80,1.34,13.79,13.85,.002)
    K.bx(('ladder top step','GALV'),7.0,7.13,.80,1.34,13.85,13.865,.002)
    for y in (.80,1.34):
        K.bx(('access gate posts','YELLOW'),6.97,7.02,y-.025,y+.025,13.865,14.97,.003)
    for z in (14.42,14.95):
        K.prism(('access gate','YELLOW'),(7.01,.825,z),(7.01,1.315,z),.020,.020,12,0,True,0)
    K.cyl(('access gate','YELLOW'),7.01,1.315,14.38,14.97,.019,12,0)
    for z in (14.42,14.91):
        K.cyl(('access gate hinges','STEEL'),7.01,.825,z-.035,z+.035,.025,12,0)
    for y in (.88,1.26):
        K.bx(('platform access','STEEL'),7.14,7.20,y-.028,y+.028,0,14.93,.003)
        K.bx(('ladder feet','STEEL'),7.08,7.26,y-.08,y+.08,0,.025,.003)
        # Bolted ties to the fixed gantry's end web support the ladder head.
        K.bx(('ladder head ties','STEEL'),7.006,7.20,y-.032,y+.032,13.79,13.85,.002)
    for k in range(49):
        z=.16+k*.28
        K.prism(('platform access','GALV'),(7.17,.88,z),(7.17,1.26,z),.018,.018,12,0,True,0)
    # Continuous fall-arrest guide visibly connects floor and gantry mounts.
    K.bx(('ladder fall arrest guide','GALV'),7.19,7.21,1.061,1.079,.10,13.80,.001)
    for z in (.15,3.,6.,9.,12.,13.75):
        K.bx(('ladder guide brackets','STEEL'),7.16,7.21,.88,1.26,z-.018,z+.018,.002)

def water_and_practicals(K,M):
    m=bpy.data.materials.get('RH refine clear puddle film') or bpy.data.materials.new('RH refine clear puddle film')
    m.use_nodes=True; b=m.node_tree.nodes.get('Principled BSDF')
    for node in list(m.node_tree.nodes):
        if node.type not in ('BSDF_PRINCIPLED','OUTPUT_MATERIAL'): m.node_tree.nodes.remove(node)
    b.inputs['Base Color'].default_value=(1,1,1,1)
    b.inputs['Transmission Weight'].default_value=1
    b.inputs['Roughness'].default_value=.075; b.inputs['IOR'].default_value=1.333
    # Thin water must transmit illumination to the slab when the renderer has
    # refractive caustics disabled. Camera/reflection rays retain the water BSDF.
    nt=m.node_tree
    path=nt.nodes.new('ShaderNodeLightPath')
    transparent=nt.nodes.new('ShaderNodeBsdfTransparent')
    transparent.inputs['Color'].default_value=(.8,.8,.8,1)
    # For a millimetre film the refraction displacement is negligible. A single
    # Fresnel interface avoids nested refractive volumes around the raised paint.
    reflection=nt.nodes.new('ShaderNodeBsdfGlossy')
    reflection.inputs['Color'].default_value=(1,1,1,1)
    reflection.inputs['Roughness'].default_value=.035
    fresnel=nt.nodes.new('ShaderNodeFresnel'); fresnel.inputs['IOR'].default_value=1.333
    surface_mix=nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(fresnel.outputs['Fac'],surface_mix.inputs[0])
    nt.links.new(transparent.outputs['BSDF'],surface_mix.inputs[1])
    nt.links.new(reflection.outputs['BSDF'],surface_mix.inputs[2])
    shadow_mix=nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(path.outputs['Is Shadow Ray'],shadow_mix.inputs[0])
    nt.links.new(surface_mix.outputs[0],shadow_mix.inputs[1])
    nt.links.new(transparent.outputs['BSDF'],shadow_mix.inputs[2])
    nt.links.new(shadow_mix.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
    M['FILM']=m
    # Millimetre water films have transparent bottoms and reflective free surfaces.
    # Quiet asymmetric boundaries follow low spots near the existing drain runs.
    noise=m.node_tree.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=18; noise.inputs['Detail'].default_value=1
    bump=m.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.0006
    m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']); m.node_tree.links.new(bump.outputs['Normal'],b.inputs['Normal'])
    nt.links.new(bump.outputs['Normal'],reflection.inputs['Normal'])
    nt.links.new(bump.outputs['Normal'],fresnel.inputs['Normal'])
    for j,(x,y,rx,ry,a) in enumerate(((6.3,-3.7,.98,.61,.5),(-5.4,-2.6,1.10,.68,-.3),
        (-3.0,4.7,1.02,.60,.8),(3.4,-5.6,1.27,.60,.1),(5.2,4.9,1.27,.76,.7),
        (-5.9,5.2,1.10,.68,-.7),(.5,7.,1.10,.64,.3),(7.6,.2,1.36,.68,.1),
        (-8.,-.6,1.02,.51,.2),(1.9,-8.,1.02,.51,-.2),(-1.2,-6.7,.85,.47,.4),
        (4.7,-8.4,.94,.51,.9),(-7.4,8.,.77,.43,.2),(2.3,3.5,.425,.30,0),(-3.2,-5.2,.60,.38,.6),
        (-7.43,-.60,.65,.17,0),(-5.50,-3.03,.16,.48,0),(6.47,-3.97,.18,.38,.55))):
        bm=K.get(('water film','FILM')); rings=[]
        for z,edge_scale in ((.0003,1),(.0007,1),(.0045,.985)):
            ring=[]
            for i in range(128):
                t=2*math.pi*i/128; r=1+.15*math.sin(3*t+j)+.07*math.sin(5*t-.4*j)+.03*math.sin(11*t+.7*j)+.015*math.sin(19*t-j)
                u,v=rx*r*edge_scale*math.cos(t),ry*r*edge_scale*math.sin(t)
                ring.append(bm.verts.new((x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a),z)))
            rings.append(ring)
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
        for lower,upper in zip(rings,rings[1:]):
            for i in range(128):
                q=(i+1)%128; bm.faces.new((lower[i],lower[q],upper[q],upper[i]))
    for x,y in ((-5.3,-1.0),(6.0,-5.0)):
        g='circulation practical'
        a,b=(-7.5,-3.6) if x<0 else (3.6,7.5)
        K.bx(('circulation ceiling rail','STEEL'),a-.08,b+.08,y-.045,y+.045,17.30,17.36,.003)
        SUPPORT.register('refinement props','circulation crossarm '+str(x),
            'RH refine circulation ceiling rail STEEL','RH walls girders STEEL',[(a,y,17.30),(b,y,17.30)])
        K.bx((g,'STEEL'),x-.43,x+.43,y-.17,y+.17,13.12,13.22,.012)
        K.bx((g,'PRACTICAL'),x-.39,x+.39,y-.13,y+.13,13.113,13.121,.003)
        for dx in (-.32,.32):
            K.cyl((g,'STEEL'),x+dx,y,13.22,17.30,.012,12,0)
            SUPPORT.register('refinement props','circulation pendant '+str((x,dx)),
                'RH refine circulation practical STEEL','RH refine circulation ceiling rail STEEL',
                [(x+dx,y,17.30)],(0,0,1),'suspension')
        light=bpy.data.lights.new('RH refine circulation area','AREA')
        light.energy=400; light.specular_factor=.18
        light.color=(.96,.97,.96); light.shape='RECTANGLE'; light.size=.78; light.size_y=.26
        o=bpy.data.objects.new('RH refine circulation area',light)
        bpy.data.collections['RH REFINEMENT'].objects.link(o); o.location=(x,y,13.10)
    # The three retained roof shafts now have visible housings and real
    # ceiling bearings. Wall-mounted washes retain their existing mount height.
    for source in sorted((o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith('LP roof shaft ')),key=lambda o:o.name):
        x,y,_=source.matrix_world.translation
        source.location.z=16.50
        if abs(y)==6:
            support_z=16.75;target='RH walls girders STEEL'
        else:
            support_z=17.30;target='RH refine roof shaft crossarm STEEL'
            K.bx(('roof shaft crossarm','STEEL'),3.52,7.58,y-.045,y+.045,17.30,17.36,.003)
            SUPPORT.register('refinement props','roof shaft crossarm',target,'RH walls girders STEEL',[(3.6,y,17.30),(7.5,y,17.30)])
        K.cyl(('roof shaft housing','STEEL'),x,y,16.52,16.65,.14,24,.004)
        S.disc(K,'roof shaft lens','PRACTICAL',(x,y,16.521),(0,0,-1),.115,.008,seg=24)
        K.cyl(('roof shaft suspension','STEEL'),x,y,16.65,support_z,.025,16,0)
        SUPPORT.register('refinement props',source.name+' suspension','RH refine roof shaft suspension STEEL',target,
            [(x,y,support_z)],(0,0,1),'suspension')
    # A real wall practical provides a grazing reflection in the west low spot.
    # Its face and backing are both modeled; exposure and review cameras stay fixed.
    K.bx(('south maintenance lamp','STEEL'),-1.03,-.17,-10.80,-10.70,4.0,4.20,.008)
    K.bx(('south maintenance lamp','WET_PRACTICAL'),-.97,-.23,-10.700,-10.693,4.04,4.16,.003)
    light=bpy.data.lights.new('RH refine south maintenance lamp','AREA')
    light.energy=27; light.color=(.96,.97,.96); light.shape='RECTANGLE'; light.size=.74; light.size_y=.12
    o=bpy.data.objects.new('RH refine south maintenance lamp',light)
    bpy.data.collections['RH REFINEMENT'].objects.link(o); o.location=(-.6,-10.68,4.1)
    o.rotation_euler=Vector((0,1,-.35)).to_track_quat('-Z','Y').to_euler()
    # Hall-side circulation light on the existing mezzanine exterior. The
    # protected wall remains untouched; this fixture mounts to its front face.
    # The previous south fixture was hidden behind that wall from this lane.
    K.bx(('mezzanine circulation practical','STEEL'),-6.95,-6.05,-5.58,-5.52,3.50,3.72,.008)
    K.bx(('mezzanine circulation practical','WET_PRACTICAL'),-6.89,-6.11,-5.520,-5.513,3.54,3.68,.003)
    light=bpy.data.lights.new('RH refine mezzanine circulation practical','AREA')
    light.energy=18; light.color=(.96,.97,.96); light.shape='RECTANGLE'; light.size=.78; light.size_y=.14
    o=bpy.data.objects.new('RH refine mezzanine circulation practical',light)
    bpy.data.collections['RH REFINEMENT'].objects.link(o); o.location=(-6.5,-5.50,3.61)
    o.rotation_euler=Vector((0,1,-.35)).to_track_quat('-Z','Y').to_euler()


def clip_water_to_slab():
    # Raised copy of the actual slab provides an exact footprint, including
    # drain seats, trenches, pool opening, cable trenches and expansion joints.
    floor=bpy.data.objects['R2 floor']
    mesh=floor.data.copy(); mesh.transform(Matrix.Translation((0,0,.0055))@floor.matrix_world)
    cutter=bpy.data.objects.new('RH temporary water footprint',mesh)
    bpy.context.scene.collection.objects.link(cutter)
    underside=bpy.data.materials.get('RH refine transparent film underside') or bpy.data.materials.new('RH refine transparent film underside')
    underside.use_nodes=True; nt=underside.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); transparent=nt.nodes.new('ShaderNodeBsdfTransparent')
    nt.links.new(transparent.outputs['BSDF'],out.inputs['Surface'])
    for o in list(bpy.data.objects):
        if o.type=='MESH' and o.name.startswith('RH refine water film'):
            material=o.data.materials[0]
            mod=o.modifiers.new('Water follows recessed floor','BOOLEAN')
            mod.operation='INTERSECT'; mod.solver='EXACT'; mod.object=cutter; mod.use_self=True
            bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
            o.data.materials.clear(); o.data.materials.append(material); o.data.materials.append(underside)
            # Only the free surface has a Fresnel interface. A second interface
            # below straight transparent rays caused total internal reflection.
            for poly in o.data.polygons: poly.material_index=1 if poly.normal.z<-.5 else 0
    bpy.data.objects.remove(cutter,do_unlink=True); bpy.data.meshes.remove(mesh)

def build(K,M,text):
    SUPPORT.reset('refinement props')
    legacy_props(K,M,text); rods(K,M,text); equipment(K,M,text); roof(K,M,text); roof_bay_practicals(K,M); roof_perimeter_practicals(K,M); water_and_practicals(K,M)
