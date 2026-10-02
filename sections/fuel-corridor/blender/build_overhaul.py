"""Rebuild visible fuel assets from a guarded baseline, preserving map interfaces.

blender -b --factory-startup --disable-autoexec --python-exit-code 1 \
 --python sections/fuel-corridor/blender/build_overhaul.py -- --stage slice
Full builds save the selected portable module. Slice builds save a task checkpoint.
"""
from pathlib import Path
import sys, math, json, hashlib, argparse, re
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from fuel_kit import *
import fuel_assets as A

TASK=ROOT/'sections/fuel-corridor'
SOURCE=ROOT/'sections/facility-assembly/sources/fuel-corridor/module.blend'
BASE=TASK/'production/checkpoints/fuel_corridor_baseline.blend'
BASE_HASH='f01b8647c4a87c88be859fce0659df8c9aaf41a91743f0c83705b8b8cfc0945c'
CONTRACT=ROOT/'sections/facility-assembly/sources/fuel-corridor/contracts/interface.json'
PROTECTED=[]
WALLS={};FLOORS={};CEILINGS={}
RECESSES=[]

def bounds(o):
    c=[o.matrix_world@Vector(v) for v in o.bound_box]
    return ([min(v[i] for v in c) for i in range(3)],[max(v[i] for v in c) for i in range(3)])

def digest(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(bytes(str(tuple(v.co)),'ascii'))
    for p in o.data.polygons:h.update(bytes(str(tuple(p.vertices)),'ascii'))
    h.update(bytes(str(tuple(tuple(r) for r in o.matrix_world)),'ascii'))
    return h.hexdigest()

def remove(o):bpy.data.objects.remove(o,do_unlink=True)

def delete_assembly(name):
    o=bpy.data.objects.get(name)
    if o:
        for child in list(o.children_recursive):remove(child)
        remove(o)

def wall_record(o):
    name=o.name[:-9];m=re.match(r'Wall_([WNSE])(-?[\d.]+)_\d+_(-?[\d.]+)',name)
    if not m:return None
    side,plane,start=m.groups();plane=float(plane);start=float(start)
    lo,hi=bounds(o);along=1 if side in 'WE' else 0
    end=hi[along];h=hi[2]
    n={'W':(1,0,0),'E':(-1,0,0),'N':(0,-1,0),'S':(0,1,0)}[side]
    # Most names record the old lining plane. Port-return stubs are exceptions;
    # derive their surface from the actual protected concrete, not a name guess.
    naxis=0 if along==1 else 1
    plane=(hi[naxis]+.04) if n[naxis]>0 else (lo[naxis]-.04)
    pos=(plane,(start+end)/2,0) if along==1 else ((start+end)/2,plane,0)
    return dict(name=name,core=o.name,pos=pos,normal=n,w=end-start,h=h)

def wall(r):
    b=B();w=r['w'];h=r['h'];name=r['name'];n=r['normal'];pos=r['pos']
    count=max(1,math.ceil(w/1.65));step=w/count
    clean=name.startswith(('Wall_N21','Wall_S18.0'))
    reactor=name.startswith(('Wall_W11.4','Wall_E17.0','Wall_N24'))
    process=name in ['Wall_E16.4_0_7','Wall_S7_1_10']
    plant=name.startswith(('Wall_N18.6','Wall_S16.2'))
    pocket=name.startswith(('Wall_W6.07','Wall_E6.78','Wall_S6.15','Wall_N13.85'))
    crossing=name.startswith(('Wall_S7.8','Wall_N12.2'))
    thermal=name=='Wall_W-2.2_0_1.2'
    opening={
        'Wall_N21_0_7.72':(-1.1075,-.3925,2.2575,2.5625),
        'Wall_S7_1_10':(.2425,.9575,2.9775,3.2825),
        'Wall_E2.2_0_1.2':(-.3575,.3575,2.9975,3.3025),
    }.get(name)
    def panel_box(dim,p,material,bevel=.002,seg=2):
        dx,dy,dz=dim;x,y,z=p
        pieces=[(x-dx/2,x+dx/2,z-dz/2,z+dz/2)]
        if opening:
            a,c,d,e=opening;result=[]
            for x0,x1,z0,z1 in pieces:
                ix0=max(x0,a);ix1=min(x1,c);iz0=max(z0,d);iz1=min(z1,e)
                if ix1<=ix0 or iz1<=iz0:result.append((x0,x1,z0,z1));continue
                for q in [(x0,ix0,z0,z1),(ix1,x1,z0,z1),(ix0,ix1,z0,iz0),(ix0,ix1,iz1,z1)]:
                    if q[1]-q[0]>.001 and q[3]-q[2]>.001:result.append(q)
            pieces=result
        for a,c,d,e in pieces:b.box((c-a,dy,e-d),((a+c)/2,y,(d+e)/2),material,min(bevel,(c-a)/4,(e-d)/4),seg=seg)
    for i in range(count):
        x=-w/2+(i+.5)*step
        upper='cool plaster' if name.startswith(('Wall_E1.2','Wall_W-1.2','Wall_W-1.5','Wall_N21','Wall_S18.0')) else 'warm plaster' if name.startswith(('Wall_S16.2','Wall_N18.6','Wall_W-5.4','Wall_E17.0','Wall_W11.4','Wall_N24')) else 'plaster'
        if name in ['Wall_W-2.2_0_1.2','Wall_E2.2_0_1.2']:upper='transfer plaster'
        m=mat('patch') if (i==count-1 and ('13.2_1' in name or '18.0' in name)) else mat(upper)
        if reactor or process:
            hh=h-1.36;pw=step-.010
            front=[(-pw/2,.034),(-pw/2+.029,.034),(-pw/2+.064,-.004),(pw/2-.064,-.004),(pw/2-.029,.034),(pw/2,.034)]
            back=[(xx,yy+.005) for xx,yy in reversed(front)]
            if process:
                # Separate face and folded edge returns allow the real extraction
                # aperture to be built in, avoiding a Boolean on a multi-part bay.
                panel_box((pw-.128,.005,hh),(x,-.0015,1.32+hh/2),mat('oxide enamel'),.001)
                for path in [front[:3],front[3:]]:
                    tail=[(xx,yy+.005) for xx,yy in reversed(path)]
                    polygon(b,path+tail,hh,mat('oxide enamel'),pos=(x,0,1.32),bevel=.001)
            else:polygon(b,front+back,hh,mat('reactor sheet'),pos=(x,0,1.32),bevel=.001)
            for zz in [1.324,h-.044]:b.box((pw,.038,.008),(x,.020,zz),mat('dark steel'),.001)
            for zz in [1.8,h-.30]:
                b.box((.075,.039,.11),(x,.0205,zz),mat('dark steel'),.002)
                for xx in [x-pw/2+.024,x+pw/2-.024]:bolt(b,(xx,.031,zz),.008)
            if process:
                # Broad removable extraction shields with folded horizontal seams.
                for zz in [2.34,3.48]:
                    polygon(b,[(-pw/2,.035),(-pw/2,-.012),(pw/2,-.012),(pw/2,.035)],.014,mat('warm enamel'),pos=(x,0,zz),bevel=.001)
        elif crossing:
            # A hollow impact/service jacket changes the load-transfer throat
            # in section: angled shoulders lead into a removable raised face.
            # The rear lining and folded ends physically close its air gap.
            panel_box((step-.010,.044,h-1.36),(x,.018,(1.32+h-.04)/2),mat('warm plaster'),.003)
            pw=step-.038
            front=[(-.014,2.30),(-.112,2.43),(-.112,3.30),(-.014,3.43)]
            back=[(yy+.006,zz) for yy,zz in reversed(front)]
            section_rot=Matrix(((0,0,1),(1,0,0),(0,1,0)))
            polygon(b,front+back,pw,mat('reactor sheet'),pos=(x-pw/2,0,0),rot=section_rot,bevel=.001)
            closed=front+[(-.004,3.43),(-.004,2.30)]
            for xx in [x-pw/2,x+pw/2-.012]:
                polygon(b,closed,.012,mat('dark steel'),pos=(xx,0,0),rot=section_rot,bevel=.001)
            for zz in [2.315,3.415]:b.box((pw,.032,.028),(x,-.012,zz),mat('steel'),.002)
            for xx in [x-pw*.36,x+pw*.36]:
                channel(b,.055,.023,.79,(xx,-.121,2.865),mat('replacement enamel'))
                for zz in [2.51,3.22]:bolt(b,(xx,-.147,zz),.008)
        elif pocket:
            # The slide pockets read as engineered guard housings connected to
            # the drive, rather than the same plaster used in personnel routes.
            pw=step-.018
            for a,z1 in [(1.32,2.62),(2.63,h-.04)]:
                hh=z1-a
                pts=[(-pw/2,.030),(-pw/2+.035,.030),(-pw/2+.075,-.004),(pw/2-.075,-.004),(pw/2-.035,.030),(pw/2,.030)]
                polygon(b,pts+[(xx,yy+.005) for xx,yy in reversed(pts)],hh,mat('reactor sheet'),pos=(x,0,a),bevel=.001)
                for zz in [a+.044,z1-.044]:
                    for xx in [x-pw/2+.09,x+pw/2-.09]:bolt(b,(xx,-.008,zz),.007)
                for xx in [x-pw*.30,x+pw*.30]:b.box((.022,.022,hh-.13),(xx,-.016,a+hh/2),mat('replacement enamel'),.002)
        elif plant:
            # Plant water gallery uses bounded mineral panels and a shallow service
            # chase, rather than continuing the refinery's plaster/dado wall.
            panel_box((step-.010,.044,h-1.36),(x,.018,(1.32+h-.04)/2),mat('warm plaster'),.003)
            for zz in [1.50,2.44]:panel_box((step-.010,.014,.025),(x,-.015,zz),mat('brass'),.002)
            for xx in [x-step/2+.10,x+step/2-.10]:panel_box((.032,.026,h-1.50),(xx,-.010,(1.38+h-.12)/2),mat('warm enamel'),.003)
        else:
            panel_box((step-.010,.044,h-(2.44 if clean else 1.36)),(x,.018,((2.40 if clean else 1.32)+h-.04)/2),m,.003)
            if thermal:
                # Open, folded heat-recovery fins above the handover/PPE zone.
                # A connected shallow cassette, not decorative wear or a decal.
                pw=step-.060
                b.box((pw,.012,.83),(x,-.010,2.985),mat('oxide enamel'),.002)
                for zz in [2.578,3.392]:b.box((pw,.080,.016),(x,-.045,zz),mat('warm enamel'),.002)
                for xx in [x-pw/2+.006,x+pw/2-.006]:b.box((.012,.080,.83),(xx,-.045,2.985),mat('warm enamel'),.002)
                count_f=max(3,int(pw/.12))
                for k in range(count_f):
                    xx=x-pw/2+.065+k*(pw-.13)/(count_f-1)
                    polygon(b,[(-.036,-.017),(-.008,-.074),(.008,-.074),(.036,-.017),(.030,-.017),(.006,-.068),(-.006,-.068),(-.030,-.017)],.75,mat('warm enamel'),pos=(xx,0,2.61),bevel=.001)
                for xx in [x-pw/2+.028,x+pw/2-.028]:
                    for zz in [2.61,3.35]:bolt(b,(xx,-.086,zz),.005)
        coat='warm enamel' if plant else 'repaired blue enamel' if i==count-1 and name in ['Wall_N13.2_1_1.2','Wall_E16.4_0_17.32'] else 'navy enamel'
        if not clean:
            b.box((step-.012,.026,1.06),(x,.005,.69),mat(coat),.004)
            if step>.34:frame(b,step-.10,.91,.013,.014,-.009,.69,mat(coat),r=.032)
            b.box((step-.014,.016,.015),(x,-.015,1.215),mat('steel'),.0015)
            for z in [.24,1.13]:
                for xx in [x-step/2+.053,x+step/2-.053]:bolt(b,(xx,-.010,z),.0055,material='dark steel')
    if clean:
        panel_box((w,.032,2.24),(0,.020,1.28),mat('sanitary grout'),.002)
        nx=max(1,math.ceil(w/.38));nz=9;tw=w/nx;th=2.24/nz
        for i in range(nx):
            for j in range(nz):
                x=-w/2+(i+.5)*tw;z=.16+(j+.5)*th
                panel_box((tw-.004,.012,th-.004),(x,-.002,z),mat('sanitary ceramic light' if (i*7+j*3)%13==2 else 'sanitary ceramic'),.0012,seg=3)
        panel_box((w,.034,.027),(0,-.012,2.41),mat('steel'),.003)
    # A restrained continuous skirting crash strip with inset bedding behind it.
    b.box((w,.035,.112),(0,-.010,.078),mat('rubber'),.004)
    b.box((w,.032,.03),(0,-.013,1.25),mat('dark steel'),.002)
    posts=[-w/2+.074,w/2-.074] if w>.4 else ([0] if w>.22 else [])
    if w>5.5:posts+=[-w/2+w*.39,-w/2+w*.71]
    for x in posts:
        channel(b,.11,.105,h-.025,(x,-.012,(h-.025)/2),mat('ink enamel'))
        b.box((.17,.145,.020),(x,-.007,.010),mat('dark steel'),.003)
        for xx in [x-.052,x+.052]:bolt(b,(xx,-.047,.021),.008,axis='Z')
        # Low stiffening plate and upper bolted splice, different widths from trim.
        b.box((.142,.014,.22),(x,-.073,.42),mat('replacement enamel'),.002)
        for z in [.35,.49]:bolt(b,(x,-.082,z),.007)
        if name in ['Wall_E2.2_0_1.2','Wall_E16.4_0_17.32','Wall_W12_0_13.2']:
            # Folded impact guards have an angled nose and real return flanges.
            profile=[(-.095,.004),(-.095,-.030),(-.053,-.030),(-.025,-.132),(.025,-.132),(.053,-.030),(.095,-.030),(.095,.004)]
            polygon(b,profile,.69,mat('ochre enamel'),pos=(x,-.058,.035))
            for xx in [x-.073,x+.073]:
                for z in [.12,.63]:bolt(b,(xx,-.093,z),.008,material='dark steel')
    # Localized scraped undercoat at cart-height corners and a repaired panel.
    if name in ['Wall_N13.2_1_1.2','Wall_S7_1_10','Wall_E2.2_0_1.2','Wall_N18.6_0_-5.4']:
        for i in range(5):
            x=-w*.27+i*.038;z=.40+(i%3)*.021
            polygon(b,[(0,0),(.09,.004),(.061,.014),(.032,.01),(-.012,.007)],.0006,mat('chip'),pos=(x,-.0085,z),rot=Matrix.Rotation(math.pi/2,3,'X'))
    # Meter scale subtle material identity, not an artificial orange band on every wall.
    o=add(b,name+' · lined bay','FC | Architecture',pos=pos,normal=n,
          target=r['core'],anchors=[(-w/2+step/2,.036 if clean else .04,min(1.8,h*.65))],direction=(0,1,0),family='layered wall bay')
    WALLS[name]=o.name
    if clean:o['fc_mount_offset_m']=-.004;o['fc_mount_offset_height_range']='[0.16,2.40]'
    return o

def fitted_point(o,point):
    p=Vector(point)
    if o.get('fc_mount_offset_height_range'):
        lo,hi=json.loads(o['fc_mount_offset_height_range'])
        if lo<p.z<hi:p.y+=o['fc_mount_offset_m']
    return p

def staging_process_recess(name='Wall_N13.2_1_1.2'):
    """Real blind process bay; external concrete faces and bounds stay fixed."""
    ob=bpy.data.objects[WALLS[name]];corner=name=='Wall_N13.2_2_10'
    core=bpy.data.objects[name+'_concrete'];w=2.0 if corner else 3.2;cw=w-.22;low=.16 if corner else 1.34;high=4.28
    cutter=B();cutter.box((cw,.18,high-low),(0,.056,(low+high)/2),mat('bed'),bevel=0)
    cut=add(cutter,'Staging process bay cutter','FC | Construction helpers');cut.matrix_world=ob.matrix_world
    for target in [ob,core]:
        mod=target.modifiers.new('Actual blind process-service bay','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
        bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name)
    remove(cut)
    b=B();h=high-low
    frame(b,cw+.08,h+.04,.060,.092,-.013,(low+high)/2,mat('dark steel'),r=.038)
    for x in [-cw/2+.014,cw/2-.014]:b.box((.027,.151,h),(x,.0205,(low+high)/2),mat('replacement enamel'),.003)
    for z in [low+.013,high-.013]:b.box((cw,.151,.026),(0,.0205,z),mat('replacement enamel'),.003)
    for i in range(3):
        x=(i-1)*(cw-.04)/3
        b.box(((cw-.04)/3-.007,.018,h-.045),(x,.104,(low+high)/2),mat('reactor sheet' if corner else 'oxide enamel'),.003)
        for xx in [x-(cw-.04)/6+.034,x+(cw-.04)/6-.034]:
            for z in [low+.06,high-.06]:bolt(b,(xx,.091,z),.006)
    for x in [-cw*.285,cw*.285]:
        for z in [1.60,4.02]:b.box((.08,.033,.12),(x,.1295,z),mat('dark steel'),.003)
    previous=B();previous.bm.from_mesh(ob.data);previous.mats=list(ob.data.materials);merge(b,previous)
    replacement=b.build('FC staging rebuilt lining',floor_normalize=False)
    ob.data=replacement.data;remove(replacement);project_uv(ob)
    support(ob,[core.name,core.name],[ob.matrix_world@Vector((x,.04,1.8)) for x in [-w/2+.045,w/2-.045]],list(ob.matrix_world.to_3x3()@Vector((0,1,0))),'wall')
    ob['fc_mount_offset_m']=.099;ob['fc_mount_offset_height_range']=json.dumps([low,high])
    ob['fc_asset_family']='deep backed staging process architecture'
    RECESSES.append({'object':ob.name,'wall':name,'width':cw,'height':h,'depth_m':.106,'purpose':'real blind process bay with folded returns and back pan','protected_external_bounds':bounds(core)})

def wall_pos(name,xyz):
    """Exact local-to-world fitting against the newly authored bay."""
    o=bpy.data.objects[WALLS[name]]
    return o.matrix_world@fitted_point(o,xyz),tuple(-(o.matrix_world.to_3x3()@Vector((0,1,0))))

def mounted(b,name,wallname,point,collection='FC | Equipment',family=None):
    pos,normal=wall_pos(wallname,point)
    b.bm.normal_update()
    # Wall-mounted recipes use Y=0 as the physical bracket/flange datum.
    # A routed feed enters that plane; its curved tube can extend beyond it.
    faces=[f for f in b.bm.faces if abs(f.normal.y)>.99 and abs(f.calc_center_median().y)<.001 and f.calc_area()>.0002]
    anchors=[tuple(f.calc_center_median()) for f in faces]
    if not anchors:
        raise ValueError('Wall assembly has no physical planar mount: '+name)
    # Real rear faces of the mounting brackets, never an empty origin in a frame.
    anchors=sorted(anchors,key=lambda p:(p[0],p[2]))
    if len(anchors)>8:anchors=anchors[::max(1,len(anchors)//8)][:8]
    return add(b,name,collection,pos=pos,normal=normal,target=WALLS[wallname],
               anchors=anchors,direction=(0,1,0),family=family)

def recessed_vent(name,wallname,point,w,h):
    """Cut the visible lining and 100mm of concrete, retaining the exterior face.

    The vent blades and their recess are real geometry; outer bounds stay exact.
    """
    wallob=bpy.data.objects[WALLS[wallname]];world=wallob.matrix_world
    cut_point=fitted_point(wallob,point)
    ceramic_opening=wallname=='Wall_N21_0_7.72' and name=='Clean extract'
    if ceramic_opening:cut_point.y-=.004
    b=B();b.box((w-.055,.17,h-.055),(cut_point.x,cut_point.y+.065,cut_point.z),mat('bed'),bevel=0)
    cut=add(b,name+' cavity cutter','FC | Construction helpers');cut.matrix_world=world
    built_opening=wallname in ['Wall_N21_0_7.72','Wall_S7_1_10','Wall_E2.2_0_1.2']
    for target in ([bpy.data.objects[wallname+'_concrete']] if built_opening else [wallob,bpy.data.objects[wallname+'_concrete']]):
        mod=target.modifiers.new(name+' actual cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
        bpy.context.view_layer.objects.active=target;target.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name);target.select_set(False)
    remove(cut)
    b=A.vent(w,h)
    # Rear filter tray behind the separated blades, not immediately under them.
    b.box((w-.064,.008,h-.064),(0,.129,0),mat('rubber'),.002)
    for x in [-w/2+.031,w/2-.031]:b.box((.008,.128,h-.058),(x,.065,0),mat('dark steel'),.001)
    pos,normal=wall_pos(wallname,point)
    if ceramic_opening:pos=world@cut_point
    anchors=[(x,0,z) for x in [-w/2+.016,w/2-.016] for z in [-h/2+.016,h/2-.016]]
    o=add(b,name,'FC | Services',pos=pos,normal=normal,target=wallob.name,anchors=anchors,direction=(0,1,0),family='recessed open vent cassette')
    RECESSES.append({'object':o.name,'wall':wallname,'width':w,'height':h,'depth_m':.145,'protected_external_bounds':bounds(bpy.data.objects[wallname+'_concrete'])})
    return o

def owned_rectangles(rect,cell):
    """One visible finish owner where frozen rectangular cells overlap."""
    pieces=[rect]
    for earlier in json.loads(CONTRACT.read_text())['floor_cells']:
        if earlier['id']==cell['id']:break
        if earlier['height']!=cell['height']:continue
        a,b,c,d=earlier['bounds'];result=[]
        for x0,x1,y0,y1 in pieces:
            ix0=max(x0,a);ix1=min(x1,b);iy0=max(y0,c);iy1=min(y1,d)
            if ix1<=ix0 or iy1<=iy0:result.append((x0,x1,y0,y1));continue
            for q in [(x0,ix0,y0,y1),(ix1,x1,y0,y1),(ix0,ix1,y0,iy0),(ix0,ix1,iy1,y1)]:
                if q[1]-q[0]>.001 and q[3]-q[2]>.001:result.append(q)
        pieces=result
    return pieces

def floor(cell):
    old=bpy.data.objects['Floor_'+cell['id']];xmin,xmax,ymin,ymax=cell['bounds']
    # Slab bottom and XY footprint stay exact; its top is recessed for real joints.
    for v in old.data.vertices:
        world=old.matrix_world@v.co
        if abs(world.z)<.005:
            world.z=-.020;v.co=old.matrix_world.inverted()@world
    old.data.materials.clear();old.data.materials.append(mat('bed'))
    b=B();nx,ny,sx,sy,service=tile_layout(cell)
    for i in range(nx):
        for j in range(ny):
            x=xmin+(i+.5)*sx;y=ymin+(j+.5)*sy
            variation=(i*17+j*7)%11
            k=(['service tile','service tile light','service tile dark'][variation%3] if service else
               'fuel tile light' if variation==2 else 'fuel tile dark' if variation==5 else 'floor')
            if cell['id'] in ['entry','inlet']:k=['transfer tile','transfer tile light','transfer tile dark'][variation%3]
            elif cell['id']=='bypass_north':k=['clean floor','clean floor light','clean floor dark'][variation%3]
            along_x=cell['id'] in ['crossing','bypass_north','plant_header']
            if (j in [0,ny-1] if along_x else i in [0,nx-1]):k='service border' if service else 'floor border'
            if cell['id']=='west_turn' and i==nx-2 and j==ny-2:k='floor repair'
            for a,c,d,e in owned_rectangles((x-sx/2+.003,x+sx/2-.003,y-sy/2+.003,y+sy/2-.003),cell):
                b.box((c-a,e-d,.020),((a+c)/2,(d+e)/2,-.010),mat(k),.0014,seg=3)
    o=add(b,'Floor finish '+cell['id'],'FC | Floor and ceiling',target=old.name,
          anchors=[((xmin+xmax)/2,(ymin+ymax)/2,-.020)],direction=(0,0,-1),kind='floor',family='flush industrial floor')
    FLOORS[cell['id']]=o.name
    return o

def tile_layout(cell):
    """Different physical scales for personnel ceramic and freight mineral tile."""
    xmin,xmax,ymin,ymax=cell['bounds']
    service=cell['id'].startswith(('bypass','plant','service_air'))
    scale=.34 if service else 1.06 if cell['id'] in ['west_turn','crossing','east_turn'] else .62
    nx=max(1,math.ceil((xmax-xmin)/scale));ny=max(1,math.ceil((ymax-ymin)/scale))
    return nx,ny,(xmax-xmin)/nx,(ymax-ymin)/ny,service

def ceiling(cell):
    b=B();xmin,xmax,ymin,ymax=cell['bounds'];roof_h=cell['height'];h=roof_h
    entry=cell['id'] in ['entry','inlet'];clean=cell['id']=='bypass_north';plant=cell['id']=='plant_header'
    dropped=cell['id']=='entry'
    if dropped:h=3.80
    nx=max(1,math.ceil((xmax-xmin)/(2.4 if clean else 1.45)));ny=max(1,math.ceil((ymax-ymin)/(1.2 if clean else 1.65)))
    sx=(xmax-xmin)/nx;sy=(ymax-ymin)/ny
    for i in range(nx):
        for j in range(ny):
            x=xmin+(i+.5)*sx;y=ymin+(j+.5)*sy
            for a,c,d,e in owned_rectangles((x-sx/2+.014,x+sx/2-.014,y-sy/2+.014,y+sy/2-.014),cell):
                b.box((c-a,e-d,.034),((a+c)/2,(d+e)/2,h+.006),mat('sanitary ceramic light' if clean else 'warm plaster' if entry else 'mineral'),.002)
            if j==0 and i==nx//2:
                # Separate hatch leaf sits in a continuous sheet lip with a reveal.
                b.box((sx*.62,sy*.56,.018),(x,y,h-.018),mat('replacement enamel'),.003)
                for xx in [x-sx*.24,x+sx*.24]:bolt(b,(xx,y,h-.029),.005,axis='Z')
    for j in range(ny+1):
        y=ymin+j*sy
        for a,c,d,e in owned_rectangles((xmin,xmax,y-.026,y+.026),cell):
            b.box((c-a,e-d,.065),((a+c)/2,(d+e)/2,h-.013),mat('replacement enamel' if clean else 'ink enamel'),.003)
    if entry:
        # Stepped perimeter service trays leave the centre route open and retain
        # the measured ceiling plane for suspended fittings. Hollow folded pans,
        # angled shoulders, removable undersides and grounded end returns.
        for side in [-1,1]:
            edge=xmin if side<0 else xmax;centre=edge-side*.22
            for a,c,d,e in owned_rectangles((centre-.22,centre+.22,ymin,ymax),cell):
                b.box((c-a,e-d,.018),((a+c)/2,(d+e)/2,h-.205),mat('transfer plaster'),.002)
                b.box((.018,e-d,.19),(centre-side*.211,(d+e)/2,h-.109),mat('warm enamel'),.002)
                for yy in [d+.013,e-.013]:b.box((c-a,.026,.19),((a+c)/2,yy,h-.109),mat('dark steel'),.002)
                for yy in [d+.32+i*1.42 for i in range(max(1,int((e-d)/1.42)))]:
                    b.box((c-a-.03,.018,.017),((a+c)/2,yy,h-.216),mat('steel'),.002)
                    for xx in [a+.06,c-.06]:bolt(b,(xx,yy,h-.226),.006,axis='Z')
                b.box((.045,e-d,.014),(centre-side*.18,(d+e)/2,h-.226),mat('brass'),.002)
    if plant:
        # Narrow bolted plant baffles provide a distinct service-gallery ceiling.
        for i in range(max(1,int((xmax-xmin)/.24))):
            xx=xmin+.12+i*.24
            for a,c,d,e in owned_rectangles((xx-.025,xx+.025,ymin,ymax),cell):
                b.box((c-a,e-d,.094),((a+c)/2,(d+e)/2,h-.044),mat('warm enamel'),.003)
    if dropped:
        # The original roof and all exterior bounds stay put. A physically hung
        # transfer canopy provides a lower human-scale volume below that roof.
        for xx in [xmin+.34,xmax-.34]:
            for yy in [ymin+.32,ymax-.32]:
                b.cyl(.008,roof_h-h-.017,(xx,yy,h+.023),mat('steel'),seg=12)
                b.box((.11,.11,.012),(xx,yy,roof_h+.012),mat('steel'),.002)
                b.box((.10,.10,.012),(xx,yy,h+.023),mat('steel'),.002)
        # Folded rear fascia closes the change of ceiling height at staging.
        b.box((xmax-xmin,.030,roof_h-h+.010),((xmin+xmax)/2,ymax-.015,(roof_h+h)/2),mat('transfer plaster'),.003)
        for zz in [h+.015,roof_h-.015]:b.box((xmax-xmin,.050,.030),((xmin+xmax)/2,ymax-.025,zz),mat('dark steel'),.002)
    if clean:
        # A hollow clean-air service spine incorporates the two actual ceiling
        # luminaires and gives the long route a deliberate continuous silhouette.
        cy=19.65;bottom=h-.145
        for yy in [cy-.30,cy+.30]:b.box((xmax-xmin,.014,.14),((xmin+xmax)/2,yy,h-.065),mat('warm enamel'),.003)
        for xx in [xmin+.009,xmax-.009]:b.box((.018,.60,.14),(xx,cy,h-.065),mat('warm enamel'),.003)
        gaps=[(3.25,4.35),(9.375,10.425)]
        spans=[(xmin,3.25),(4.35,9.375),(10.425,xmax)]
        for a,c in spans:
            count=max(1,math.ceil((c-a)/.90));step=(c-a)/count
            for i in range(count):
                xx=a+(i+.5)*step
                b.box((step-.006,.585,.012),(xx,cy,bottom),mat('sanitary ceramic light'),.002)
                for yy in [cy-.25,cy+.25]:bolt(b,(xx,yy,bottom-.007),.005,axis='Z')
        for a,c in gaps:
            for xx in [a-.009,c+.009]:b.box((.018,.60,.14),(xx,cy,h-.065),mat('replacement enamel'),.002)
    core='Ceiling_'+cell['id']
    o=add(b,'Ceiling cassettes '+cell['id'],'FC | Floor and ceiling',target=core,
          anchors=[(xx,yy,roof_h+.018) for xx in [xmin+.34,xmax-.34] for yy in [ymin+.32,ymax-.32]] if dropped else [((xmin+xmax)/2,(ymin+ymax)/2,roof_h+.018)],direction=(0,0,1),kind='ceiling',family='suspended transfer canopy' if dropped else 'clean-air service ceiling' if clean else 'ceiling cassette')
    CEILINGS[cell['id']]=o.name

def overhead(name,pos,length=1.2,energy=220,cool=False,cell='west_turn'):
    b=B();coat=mat('ink enamel');x,y,z=pos
    # Suspended folded reflector, end caps, diffuser, cable gland and actual stems.
    b.box((length,.25,.068),(0,0,-.080),coat,.006)
    b.box((length-.085,.194,.014),(0,0,-.122),mat('cool diffuser' if cool else 'warm diffuser'),.002)
    for sx in [-1,1]:
        b.box((.042,.27,.102),(sx*(length/2-.013),0,-.080),mat('dark steel'),.003)
        b.cyl(.008,.045,(sx*(length*.31),0,-.045),mat('steel'),seg=12)
        b.box((.07,.12,.012),(sx*(length*.31),0,-.006),mat('steel'),.001)
        for sy in [-1,1]:bolt(b,(sx*(length/2-.035),sy*.077,-.133),.004,axis='Z')
    b.tube(rounded_path([(length/2-.075,.08,-.085),(length/2+.01,.08,-.04),(length/2+.05,.08,-.016)]),.008,mat('rubber'),seg=10)
    o=add(b,name,'FC | Practicals',pos=pos,target=CEILINGS[cell],anchors=[(-length*.31,-.04,0),(length*.31,.04,0)],direction=(0,0,1),kind='ceiling',family='suspended luminaire')
    light(name+' pool',(x,y,z-.140),(x,y,z-2),energy,(.77,.86,1) if cool else (1,.85,.66),size=length-.09,shape='RECTANGLE',size_y=.18,parent=o.name)
    return o

def sconce(name,wallname,point,energy=80,cool=False):
    b=B();b.box((.10,.016,.15),(0,-.008,0),mat('dark steel'),.005)
    for z in [-.05,.05]:bolt(b,(0,-.018,z),.004)
    b.tube([(0,-.008,-.018),(0,-.135,-.018)],.012,mat('steel'),seg=12)
    # Pitched hood, rolled lip and downward light-emitting optic.
    polygon(b,[(-.16,-.08),(.16,-.08),(.14,.09),(-.14,.09)],.044,mat('navy enamel'),pos=(0,-.18,-.044),rot=Matrix.Rotation(.12,3,'X'))
    b.box((.26,.15,.010),(0,-.18,-.047),mat('cool diffuser' if cool else 'warm diffuser'),.002)
    o=mounted(b,name,wallname,point,'FC | Practicals','wall task luminaire')
    p=o.matrix_world@Vector((0,-.18,-.055));q=o.matrix_world@Vector((0,-.60,-1.0))
    color=(.77,.87,1) if cool else (1,.72,.46) if name=='Bench practical' else (1,.82,.62)
    light(name+' pool',p,q,energy,color,size=.23,shape='RECTANGLE',size_y=.13,parent=o.name)

def sign(name,wallname,point,title,size=.09,width=1.1,coat='ink enamel',stand_off=0):
    b=B();w=width;h=.19
    b.box((w,.017,h),(0,-.0085-stand_off,h/2),mat(coat),.006)
    if stand_off:
        for x in [-w*.40,w*.40]:b.box((.036,stand_off,.040),(x,-stand_off/2,h/2),mat('dark steel'),.002)
    for x in [-w/2+.03,w/2-.03]:bolt(b,(x,-.019-stand_off,h/2),.0045)
    o=mounted(b,name,wallname,point,'FC | Signage','folded wayfinding plate')
    p=o.matrix_world@Vector((0,-.0185-stand_off,h/2));normal=tuple(-(o.matrix_world.to_3x3()@Vector((0,1,0))))
    label(title,p,size,name=name+' type',normal=normal,material='ink' if coat in ['warm enamel','replacement enamel'] else 'white ink',parent=o.name)
    return o

def dispatch():
    wallname='Wall_N13.2_1_1.2'
    b=B();b.box((.38,.26,.035),(0,-.145,0),mat('wood'),.003)
    for x in [-.13,.13]:
        polygon(b,[(0,0),(-.20,0),(0,-.18)],.018,mat('dark steel'),pos=(x,0,0),rot=Matrix.Rotation(math.pi/2,3,'Y'))
    b.box((.35,.016,.10),(0,-.008,-.045),mat('dark steel'),.003)
    o=mounted(b,'Dispatch writing ledge',wallname,(-.60,-.008,1.02),'FC | Narrative','dispatch ledge')
    T=o.matrix_world
    p=T@Vector((0,-.15,.018))
    paper=add(A.clipboard(),'Dispatch manifest', 'FC | Narrative',pos=p,angle=0,parent=o.name,family='clipboard with layered paper')
    paper.rotation_euler.z=-.10
    return o

def staging():
    # Complete human/work cluster outside the freight and bypass clearance.
    wn='Wall_W-2.2_0_1.2';wallname='Wall_N13.2_1_1.2'
    b=A.bench();o=add(b,'Maintenance bench','FC | Furniture',pos=(-2.2,10.58,0),normal=(1,0,0),
         target=FLOORS['west_turn'],anchors=[(x,y,0) for x in [-.63,.63] for y in [-.51,-.075]],direction=(0,0,-1),kind='floor',family='maintenance workbench')
    T=o.matrix_world
    # A checked maintenance slip and the radio give the work a specific handover.
    note=B();polygon(note,[(-.048,-.034),(.048,-.034),(.048,.022),(.036,.034),(-.048,.034)],.0007,mat('paper'))
    polygon(note,[(.036,.023),(.048,.023),(.036,.034)],.0007,mat('white ink'),pos=(0,0,.001),rot=Matrix.Rotation(.14,3,'X'))
    paper=add(note,'Checked shift note','FC | Narrative',pos=T@Vector((-.01,-.11,.895)),angle=1.57,parent=o.name,family='folded checked maintenance note')
    text=label('OK / B',paper.matrix_world@Vector((0,0,.0010)),.016,material='ink',parent=paper.name)
    world=Matrix.Translation(paper.matrix_world@Vector((0,0,.0010)))@Matrix.Rotation(1.57,4,'Z');text.matrix_world=world
    add(A.radio(),'Bench service radio','FC | Narrative',pos=T@Vector((.29,-.16,.895)),angle=1.4,parent=o.name,family='handheld service radio')
    for name,b,loc,angle in [('Open field-service tool case',A.tool_case(opened=True),(-.39,-.30,.895),.06),
                            ('Folded blue wiping cloth',A.rag(),(.04,-.25,.895),-.15),
                            ('Workshop flask',A.thermos(),(-.65,-.10,.895),0),
                            ('Work mug',A.mug(),(.11,-.39,.895),.2),
                            ('Right work glove',A.glove(),(-.11,-.45,.895),-.13),
                            ('Left work glove',A.glove(),(-.21,-.41,.895),.25)]:
        minz=min(v.co.z for v in b.bm.verts)
        for v in b.bm.verts:v.co.z-=minz
        a=add(b,name,'FC | Narrative',pos=T@Vector(loc),angle=math.pi/2+angle,parent=o.name,family=name)
    for i,x in enumerate([-.34,.33]):
        add(A.tool_case(.47,.29,.20),'Spare parts case '+str(i),'FC | Narrative',pos=T@Vector((x,-.29,.242)),angle=math.pi/2,parent=o.name,family='service parts case')
    board=mounted(A.perforated_board(),'Perforated tool rack',wn,(3.37,-.004,1.79),'FC | Furniture','perforated tool board')
    for i,(name,t) in enumerate([('Combination wrench',A.spanner(.24)),('Driver',A.screwdriver()),('Long-nose pliers',A.pliers()),('Small wrench',A.spanner(.18))]):
        p=board.matrix_world@Vector(([-.39,-.16,.10,.31][i],-.032,[-.18,-.17,-.17,-.145][i]))
        add(t,name,'FC | Narrative',pos=p,normal=(1,0,0),parent=board.name,family='identified hand tool')
    # Curved hooks have a return and contact the board; tools seat over them.
    hooks=B()
    for i in range(4):
        x=[-.39,-.16,.10,.31][i];z=[.052,.063,.020,.023][i]
        hooks.tube([(x,-.029,z),(x,-.063,z),(x,-.065,z+.018)],.0035,mat('steel'),seg=8)
    add(hooks,'Tool-rack hooks','FC | Narrative',pos=board.location,normal=(1,0,0),parent=board.name,family='return tool hook')
    carrier=add(A.carrier(),'Sealed cartridge carrier','FC | Freight',pos=(2.65,12.32,0),
        target=FLOORS['west_turn'],anchors=[(x,y,0) for x in [-.61,.61] for y in [-.29,.29]],direction=(0,0,-1),kind='floor',family='cartridge carrier')
    label('FC-017',(2.69,12.1587,.723),.026,name='Cartridge identity',parent=carrier.name)
    manifold=mounted(A.manifold(),'Staging service-air manifold',wallname,(1.0,-.004,1.37),'FC | Services','cast air manifold')
    label('AIR / 07',manifold.matrix_world@Vector((-.17,-.0615,.64)),.024,normal=(0,-1,0),material='ink',parent=manifold.name)
    test=mounted(A.calibration_panel(),'Purge test and pressure balance panel',wallname,(-.72,-.004,1.57),'FC | Services','tapped dual-gauge calibration board connected to the staging air main')
    label('PURGE / BALANCE',test.matrix_world@Vector((0,-.053,.825)),.040,normal=(0,-1,0),parent=test.name)
    for txt,x in [('INLET',-.28),('RETURN',.28)]:label(txt,test.matrix_world@Vector((x,-.054,.10)),.025,normal=(0,-1,0),parent=test.name)
    mounted(A.pipe_run(2.1,1.42),'Staging air feed',wallname,(-.31,-.004,3.04),'FC | Services','routed clamped utility pipe')
    b=B();b.tube([(.74,-.13,1.62),(.74,-.16,1.62)],.023,mat('steel'),seg=20)
    p,n=wall_pos(wallname,(0,-.004,1.62));p.z=0
    add(b,'Staging inlet elbow','FC | Services',pos=p,normal=n,parent=manifold.name,family='connected manifold inlet')
    dispatch()
    sign('Staging service header',wallname,(-.66,-.004,3.38),'FUEL TRANSFER',.13,1.48)
    # Physical wall vent and bent gland connection above the service station.
    recessed_vent('Staging extraction grille',wallname,(1.0,-.004,2.65),.59,.26)
    sconce('Bench practical',wn,(3.37,-.004,2.23),155)
    sconce('Cartridge practical',wallname,(.90,-.004,2.31),50,cool=True)
    overhead('Staging main',(.0,10.0,4.389),1.55,320,False,'west_turn')

def services():
    # Routed utility assemblies, distinct from wall trims and conduits.
    for name,wn,p,L,drop in [
        ('Entry dry-air main','Wall_E2.2_0_1.2',(0,-.004,3.47),4.3,.39),
        ('Plant water branch','Wall_N18.6_0_-5.4',(0,-.004,2.55),2.8,.42),
        ('Delivery cooling main','Wall_W12_0_13.2',(0,-.004,3.59),3.5,.70),
        ('Reactor cooling union','Wall_E17.0_0_21',(0,-.004,4.77),2.0,.70)]:
        mounted(A.pipe_run(L,drop),name,wn,p,'FC | Services','routed clamped utility pipe')
    for name,wn,p,L in [
        ('Staging cable ladder','Wall_W-2.2_0_1.2',(1.8,-.004,3.83),2.0),
        ('Crossing cable ladder','Wall_N12.2_1_6.78',(0,-.004,3.82),2.6),
        ('Entry cable ladder','Wall_W-2.2_0_1.2',(-3.25,-.004,3.42),2.5),
        ('East cable ladder','Wall_S7_1_10',(-1.2,-.004,3.83),2.8),
        ('Delivery cable ladder','Wall_E16.4_0_7',(-2.1,-.004,3.83),2.2),
        ('North cable ladder','Wall_S18.0_0_1.2',(-1.6,-.004,2.68),3.4),
        ('Plant cable ladder','Wall_S16.2_0_-5.4',(0,-.004,2.68),2.8),
        ('Reactor cable ladder','Wall_W11.4_0_21',(0,-.004,5.35),2.0)]:
        mounted(A.cable_ladder(L),name,wn,p,'FC | Services','open cable ladder and sagging bundle')

def recess_feed():
    b=B();path=rounded_path([(.92,14.74,2.70),(-.94,14.74,2.70),(-1.06,14.74,2.60),(-1.06,14.74,2.30),(-1.17,14.74,2.22),(-1.41,14.74,2.22),(-1.486,14.74,2.13),(-1.486,14.74,1.63)])
    b.tube(path,.023,mat('steel'),seg=20)
    for x in [.92,-.81]:ring(b,.030,.014,(x,14.74,2.70),mat('brass'),axis='X',seg=24)
    # East wall cantilever and recessed back-wall clip carry this same pipe.
    b.box((.016,.10,.21),(1.188,14.74,2.70),mat('dark steel'),.003)
    b.tube([(1.180,14.74,2.67),(.944,14.74,2.67)],.008,mat('dark steel'),seg=12)
    b.tube([(1.180,14.74,2.625),(.944,14.74,2.67)],.007,mat('dark steel'),seg=12)
    ring(b,.030,.007,(.937,14.74,2.70),mat('dark steel'),axis='X',seg=24)
    b.box((.016,.10,.14),(-1.638,14.74,2.04),mat('dark steel'),.003)
    b.tube([(-1.630,14.74,2.04),(-1.512,14.74,2.04)],.008,mat('dark steel'),seg=12)
    ring(b,.030,.007,(-1.486,14.74,2.037),mat('dark steel'),seg=24)
    o=add(b,'Recess routed cross-header air feed','FC | Services',family='clamped connected recess air feed')
    support(o,[WALLS['Wall_E1.2_0_13.2'],WALLS['Wall_W-1.65_0_14.3']],[(1.196,14.74,2.70),(-1.646,14.74,2.04)],(1,0,0),'wall')
    o['support_directions']=json.dumps([[1,0,0],[-1,0,0]])

def cabinet_feed(name,wn,from_point,to_point,parent):
    b=B();x,y,z=from_point;xx,yy,zz=to_point
    b.tube(rounded_path([(x,y,z),(x,y,z-.16),(xx,yy,z-.24),(xx,yy,zz+.07),(xx,yy,zz+.02)]),.009,mat('rubber'),seg=12)
    b.lathe([(0,0),(.020,0),(.020,.008),(.014,.013),(.014,.030),(.011,.036),(0,.036)],to_point,mat('dark steel'),seg=20)
    p,n=wall_pos(wn,(0,-.004,0))
    add(b,name,'FC | Services',pos=p,normal=n,parent=parent,family='cabinet entry gland and routed cable')

def work_traces():
    # Purposeful clusters outside clear lanes. Work in progress in three places,
    # not arbitrary duplicate props placed at every corner.
    mounted(A.extinguisher(),'Entry fire station','Wall_E2.2_0_1.2',(1.6,-.008,.37),family='shaped fire cylinder and retaining rack')
    mounted(A.lockout_station(),'Bypass lockout rail','Wall_E1.2_0_13.2',(-1.72,-.004,1.42),family='lockout station with paper tags')
    mounted(A.extinguisher(),'Reactor fire station','Wall_E17.0_0_21',(.72,-.008,.40),family='shaped fire cylinder and retaining rack')
    bucket=add(A.pail(),'Spill absorbent pail','FC | Narrative',pos=(10.67,7.6,0),target=FLOORS['east_turn'],anchors=[(0,0,0)],direction=(0,0,-1),kind='floor',family='lidded absorbent pail')
    plate=B();plate.box((.14,.012,.065),(0,-.151,.212),mat('warm enamel'),.003)
    plaque=add(plate,'Spill pail embossed plaque','FC | Narrative',pos=bucket.location,parent=bucket.name,family='formed pail label plate')
    label('SPILL',bucket.matrix_world@Vector((0,-.1576,.212)),.037,material='ink',parent=plaque.name)
    add(A.spare_filter_box(),'Replacement filter package','FC | Narrative',pos=(11.12,7.63,0),target=FLOORS['east_turn'],anchors=[(0,0,0)],direction=(0,0,-1),kind='floor',family='open folded package and real pleated filter')
    shelf_b=B();shelf_b.box((.65,.40,.024),(0,-.20,-.012),mat('replacement enamel'),.003)
    shelf_b.box((.65,.015,.22),(0,-.0075,-.11),mat('dark steel'),.003)
    for xx in [-.235,.235]:
        polygon(shelf_b,[(0,0),(-.34,0),(0,-.19)],.018,mat('dark steel'),pos=(xx,0,-.024),rot=Matrix.Rotation(math.pi/2,3,'Y')@Matrix.Rotation(math.pi/2,3,'Z'))
        bolt(shelf_b,(xx,-.018,-.15),.007)
    shelf=mounted(shelf_b,'Gate service-kit parking rack','Wall_N12.2_1_6.78',(.17,-.008,.42),'FC | Narrative','folded service-kit rack with gussets')
    case=add(A.tool_case(.43,.30,.21),'Gate maintenance kit','FC | Narrative',pos=shelf.matrix_world@Vector((0,-.21,0)),parent=shelf.name,family='parked gate service kit')
    # Delivery paperwork ledge and spare filter: actual folded tray/mesh element.
    b=B();b.box((.48,.26,.018),(0,-.13,0),mat('warm enamel'),.003)
    for x in [-.236,.236]:b.box((.008,.26,.075),(x,-.13,.029),mat('warm enamel'),.002)
    b.box((.48,.013,.18),(0,-.0065,-.055),mat('dark steel'),.003)
    for x in [-.18,.18]:bolt(b,(x,-.016,-.09),.006)
    shelf=mounted(b,'Delivery paperwork shelf','Wall_E16.4_0_17.32',(.1,-.008,1.05),'FC | Narrative','folded dispatch shelf')
    clip=A.clipboard();minz=min(v.co.z for v in clip.bm.verts)
    for v in clip.bm.verts:v.co.z-=minz
    add(clip,'Reactor receipt clipboard','FC | Narrative',pos=shelf.matrix_world@Vector((0,-.13,.009)),angle=-1.4,parent=shelf.name,family='layered manifest clipboard')

def portal(name,pos,n,width,height,coat='navy enamel',title='',state='CLOSED',floorcell='entry'):
    # Exact clear opening. All fabrication lies outside it; no cartoon overbevel.
    b=B();m=mat(coat);outerw=width+.29
    # A U frame keeps the sill truly flush. A closed rectangle would create an
    # unacceptable 145mm bar across the freight route.
    for x in [-width/2-.073,width/2+.073]:
        if name=='Reactor boundary':
            xx=(1 if x>0 else -1)*(width/2+.125)
            pts=[(-.12,.060),(-.12,-.036),(-.085,-.153),(.085,-.153),(.12,-.036),(.12,.060)]
            polygon(b,pts,height+.14,mat('replacement enamel'),pos=(xx,0,0),bevel=.005)
            b.box((.090,.018,height-.12),(xx,-.159,height/2),mat('navy enamel'),.003)
            for zz in [.30,1.58,3.24,height-.24]:
                b.box((.20,.055,.066),(xx,-.169,zz),mat('steel'),.004)
                for xxx in [xx-.068,xx+.068]:bolt(b,(xxx,-.200,zz),.009)
        else:channel(b,.145,.16,height+.14,(x,-.040,(height+.14)/2),mat('ink enamel'))
    if name=='Freight gate':
        # The load-bearing lower header itself is now an open formed channel.
        # The original solid U-frame header caused the broad black bar in D05.
        b.box((outerw,.008,.145),(0,.035,height+.0725),mat('replacement enamel'),.0015)
        for zz in [height+.004,height+.141]:b.box((outerw,.16,.008),(0,-.040,zz),mat('steel'),.0015)
        for zz in [height+.018,height+.127]:b.box((outerw,.007,.031),(0,-.1165,zz),mat('replacement enamel'),.0015)
        for xx in [-width/2-.04,-.88,0,.88,width/2+.04]:
            b.box((.009,.149,.128),(xx,-.0365,height+.0725),mat('dark steel'),.0015)
    elif name=='Reactor boundary':
        # Chamfered pressure-bulkhead crown shares the wide jacket construction.
        b.box((width+.49,.24,.145),(0,-.044,height+.0725),mat('replacement enamel'),.018,seg=3)
        for xx in [-1.62,0,1.62]:b.box((.18,.015,.119),(xx,-.171,height+.0725),mat('navy enamel'),.008)
    else:b.box((outerw,.16,.145),(0,-.040,height+.0725),mat('ink enamel'),.006)
    b.tube([(-width/2-.009,-.136,0),(-width/2-.009,-.136,height+.009),
            (width/2+.009,-.136,height+.009),(width/2+.009,-.136,0)],.009,mat('rubber'),seg=12)
    for x in [-width/2-.075,width/2+.075]:
        foot_x=(1 if x>0 else -1)*(width/2+.125) if name=='Reactor boundary' else x
        b.box((.25 if name=='Reactor boundary' else .185,.27,.028),(foot_x,.006,.014),mat('dark steel'),.003)
        for y in [-.07,.09]:bolt(b,(x,y,.03),.009,axis='Z')
    if name=='Freight gate':
        b.box((width+.36,.006,.16),(0,.132,height+.26),mat('replacement enamel'),.0015)
        for zz in [height+.183,height+.337]:b.box((width+.36,.28,.006),(0,-.005,zz),mat('replacement enamel'),.0015)
        for zz in [height+.196,height+.324]:b.box((width+.36,.006,.030),(0,-.142,zz),mat('steel'),.0015)
        for xx in [-width/2,-.62,.62,width/2]:b.box((.009,.26,.147),(xx,-.005,height+.26),mat('dark steel'),.0015)
    else:b.box((width+.36,.28,.16),(0,-.005,height+.26),mat('dark steel'),.005)
    for x in [-width/2-.04,width/2+.04]:
        for z in [.3,height-.2]:bolt(b,(x,-.129,z),.008)
    o=add(b,name+' frame','FC | Doors',pos=pos,normal=n,target=FLOORS[floorcell],
        anchors=[(-width/2-.075,-.07,0),(width/2+.075,.09,0)],direction=(0,0,-1),kind='floor',family='manufactured portal frame')
    T=o.matrix_world
    for side in ([] if state=='PASSAGE' else [-1,1]):
        leaf=B();w=width/2-.016
        # Deep leaf rim, recessed sheet, ribs, recessed glazing, dogs and handle.
        frame(leaf,w,height-.026,.048,.072,-.063,height/2,m,r=.025)
        win_z=min(1.70 if width<3 else 1.80,height*.68)
        if width<3:
            sw=w-.093;hole=.44 if name=='Clean service' else .27
            win_h=.54 if name=='Plant service' else .26
            z0=win_z-win_h/2;z1=win_z+win_h/2
            sidew=(sw-hole)/2
            for side_x in [-1,1]:leaf.box((sidew,.025,height-.112),(side_x*(hole/2+sidew/2),-.057,height/2),m,.002)
            for a,zz in [(.056,z0),(z1,height-.056)]:leaf.box((hole,.025,zz-a),(0,-.057,(a+zz)/2),m,.002)
        else:circular_aperture_sheet(leaf,w-.093,height-.112,-.057,.025,win_z,.155,m)
        leaf.box((w-.145,.032,height*.29),(0,-.092,height*.19),mat('steel' if name=='Plant service' else 'dark steel'),.003)
        # Pressed lower access plates, folded diagonal ribs and bolted lock dogs
        # distinguish a transfer leaf from a scaled-up personnel door.
        if width>=3:
            for z,hh in [(.64,.77),(min(height-.58,3.03),min(1.1,height-2.35))]:
                ww=w-.22
                frame(leaf,ww,hh,.036,.034,-.105,z,mat('ink enamel'),r=.065)
                pts=[(-ww/2+.075,-hh/2+.04),(ww/2-.075,-hh/2+.04),(ww/2-.04,-hh/2+.075),(ww/2-.04,hh/2-.09),(ww/2-.095,hh/2-.035),(-ww/2+.09,hh/2-.035),(-ww/2+.04,hh/2-.09),(-ww/2+.04,-hh/2+.075)]
                polygon(leaf,pts,.018,mat('replacement enamel'),pos=(0,-.12,z),rot=Matrix.Rotation(math.pi/2,3,'X'))
                for xx in [-ww/2+.06,ww/2-.06]:
                    for zz in [z-hh/2+.07,z+hh/2-.07]:bolt(leaf,(xx,-.143,zz),.010)
                leaf.box((ww-.15,.026,.033),(0,-.15,z),mat('dark steel'),.003,rot=Matrix.Rotation(side*.13,3,'Y'))
            # A deep centre compression-lock rail, accessible waist-height gear.
            xx=side*(w/2-.068)
            leaf.box((.052,.075,height-.16),(xx,-.081,height/2),mat('ink enamel'),.005)
            for zz in [.50,1.38,height-.52]:
                leaf.box((.106,.081,.14),(xx,-.123,zz),mat('dark steel'),.008)
                bolt(leaf,(xx,-.169,zz),.018)
            leaf.box((.22,.003,.085),(-side*.30,-.143,.65),mat('ink enamel'),.004)
        elif name=='Plant service':
            # Utility leaves have a formed lower vent guard and vertically
            # mounted vision lights, not the generic three cross-bar grammar.
            frame(leaf,w-.15,.76,.025,.025,-.108,.57,mat('steel'),r=.036)
            for i in range(8):
                zz=.282+i*.079
                polygon(leaf,[(-.018,0),(-.018,-.015),(-.041,-.045),(-.063,-.045),(-.063,-.031),(-.034,-.010)],w-.23,mat('warm enamel'),pos=(-(w-.23)/2,-.087,zz),rot=Matrix.Rotation(math.pi/2,3,'Y'))
            for xx in [-w/2+.12,w/2-.12]:
                for zz in [.24,.90]:bolt(leaf,(xx,-.140,zz),.006)
            leaf.box((w-.19,.022,.040),(0,-.093,height-.28),mat('brass'),.002)
        else:
            frame(leaf,w-.15,.66,.020,.021,-.108,.57,mat('steel'),r=.026)
            for xx in [-w/2+.12,w/2-.12]:
                for zz in [.31,.83]:bolt(leaf,(xx,-.13,zz),.006)
            leaf.box((w-.19,.022,.040),(0,-.093,height-.28),mat('ink enamel'),.002)
        for z in ([] if name=='Plant service' else [win_z-.38,win_z+.32]):
            leaf.box((w-.078,.065,.065),(0,-.090,z),mat('replacement enamel') if coat=='navy enamel' else mat('steel'),.003)
        # Every portal has a smaller engineered aperture rather than a pasted dial.
        if width<3:
            frame(leaf,min(hole+.07,w-.17),win_h+.07,.035,.030,-.094,win_z,mat('steel'),r=.05)
            leaf.box((hole,.004,win_h),(0,-.093,win_z),mat('glass'),.003)
        else:
            leaf.lathe([(.155,0),(.203,0),(.209,.021),(.184,.043),(.155,.043),(.155,0)],(0,-.098,win_z),mat('steel'),seg=48,rot=Matrix.Rotation(math.pi/2,3,'X'))
            leaf.lathe([(0,0),(.155,0),(.155,.005),(0,.005)],(0,-.117,win_z),mat('glass'),seg=48,rot=Matrix.Rotation(math.pi/2,3,'X'))
            for k in range(8):
                a=k*math.pi/4;bolt(leaf,(.182*math.cos(a),-.143,win_z+.182*math.sin(a)),.006)
        hx=-side*(w/2-.16)
        if width>=4:
            leaf.lathe([(0,0),(.060,0),(.068,.020),(.055,.045),(.025,.10),(0,.10)],(hx,-.112,1.28),mat('dark steel'),seg=32,rot=Matrix.Rotation(math.pi/2,3,'X'))
            leaf.lathe([(.109,0),(.132,0),(.137,.012),(.132,.025),(.109,.025),(.109,0)],(hx,-.215,1.28),mat('steel'),seg=48,rot=Matrix.Rotation(math.pi/2,3,'X'))
            for k in range(3):
                ang=k*2*math.pi/3;leaf.tube([(hx,-.228,1.28),(hx+.122*math.cos(ang),-.228,1.28+.122*math.sin(ang))],.010,mat('steel'),seg=12)
            bolt(leaf,(hx,-.234,1.28),.021)
            frame(leaf,w-.19,.64,.032,.060,-.090,height-.56,mat('steel'),r=.042)
            leaf.box((w-.255,.018,.575),(0,-.098,height-.56),mat('cool plaster'),.005)
            for xx in [-w/2+.15,w/2-.15]:
                for zz in [height-.79,height-.33]:bolt(leaf,(xx,-.112,zz),.008)
        else:
            leaf.tube(rounded_path([(hx,-.111,1.02),(hx,-.19,1.08),(hx,-.19,1.47),(hx,-.111,1.53)]),.015,mat('steel'),seg=12)
            leaf.tube([(hx,-.191,1.16),(hx,-.191,1.39)],.018,mat('rubber'),seg=12)
        for z in [height*.15,height*.85]:
            leaf.box((.073,.041,.094),(-hx,-.113,z),mat('dark steel'),.006)
            bolt(leaf,(-hx,-.14,z),.011)
        if state=='OPEN':
            for xx in [-w*.29,w*.29]:
                leaf.box((.052,.035,.277),(xx,-.172,height+.111),mat('dark steel'),.003)
                leaf.lathe([(0,0),(.028,0),(.041,.008),(.046,.015),(.046,.035),(.035,.044),(.028,.056),(0,.056)],(xx,-.1985,height+.222),mat('steel'),seg=32,rot=Matrix.Rotation(math.pi/2,3,'X'))
                leaf.cyl(.009,.079,(xx,-.262,height+.222),mat('steel'),seg=16,axis='Y')
                bolt(leaf,(xx,-.258,height+.222),.010)
        x=side*(width/4 if state=='CLOSED' else width/2+w/2+.75)
        p=T@Vector((x,0,.012))
        obj=add(leaf,name+(' left leaf' if side<0 else ' right leaf'),'FC | Doors',pos=p,normal=n,parent=o.name,family='fabricated pressure leaf' if width>=3 else 'fabricated service leaf')
        obj['current_pose']=state;obj['collision_handoff']='kinematic_geometry'
        obj['controller_status']='authoring pose; engine controller not verified'
        if width>=3:
            label('L / 01' if side<0 else 'R / 02',obj.matrix_world@Vector((-side*.30,-.146,.65)),.039,normal=n,parent=obj.name)
        if width>=4:label('REACTOR' if side<0 else '02',obj.matrix_world@Vector((0,-.109,height-.56)),.19 if side<0 else .32,normal=n,material='ink',parent=obj.name)
        # Sparse handling marks at the active grip/kick region, asymmetric in use.
        damage=B()
        for j in range(4 if side<0 else 2):
            polygon(damage,[(0,0),(.042,.003),(.028,.009),(-.008,.006)],.0004,mat('chip'),pos=(.10+j*.014,-.139 if width>=3 else -.1088,(.78 if width>=3 else .62)+j*.025),rot=Matrix.Rotation(math.pi/2,3,'X'))
        add(damage,name+(' left handling wear' if side<0 else ' right handling wear'),'FC | Doors',pos=p,normal=n,parent=obj.name,family='localized handled paint loss')
        stroke=side*((width/2+w/2+.75)-width/4)
        obj['closed_to_open_translation_m']=list(T.to_3x3()@Vector((stroke,0,0)))
    if title:
        # A compact plate on the structural face leaves the serviceable drive
        # above it visible from the unchanged mechanism evaluation camera.
        hw=min(width,2.10 if width>=4 else 1.65 if name in ['Clean service','Refinery boundary'] else 1.22)
        top=B();top.box((hw,.025,.19),(0,-.0125,.095),mat('ink enamel'),.004)
        if name=='Freight gate':
            for x in [-hw*.35,hw*.35]:top.box((.08,.020,.065),(x,.010,.15),mat('dark steel'),.002)
        for x in [-hw/2+.025,hw/2-.025]:bolt(top,(x,-.027,.095),.004)
        a=add(top,name+' header','FC | Signage',pos=T@Vector((0,-.145,height+.17)),normal=n,parent=o.name,family='wayfinding plate')
        if name=='Clean service':
            # Physical ivory face with dark ink stays readable in the shadow of
            # this low, fully framed header. The plate carries its own optic.
            a.data.materials[0]=mat('warm enamel')
            label(title,a.matrix_world@Vector((0,-.026,.095)),.135,normal=n,material='ink',parent=a.name)
            optic=B();optic.box((1.34,.12,.04),(0,-.22,height+.37),mat('warm enamel'),.004)
            optic.box((1.25,.090,.009),(0,-.22,height+.345),mat('cool diffuser'),.001)
            for xx in [-.60,.60]:optic.box((.035,.19,.08),(xx,-.145,height+.365),mat('dark steel'),.002)
            lamp=add(optic,name+' header reading optic','FC | Practicals',pos=pos,normal=n,parent=o.name,family='header-supported sign reading luminaire')
            light('Clean header reading pool',T@Vector((0,-.22,height+.337)),T@Vector((0,-.17,height+.26)),9,(.84,.91,1),size=1.2,shape='RECTANGLE',size_y=.08,parent=lamp.name)
        else:
            label(title,a.matrix_world@Vector((0,-.026,.095)), .135 if name=='Refinery boundary' else .13 if width>=4 else .10,normal=n,material='white ink',parent=a.name)
            if name=='Refinery boundary':
                optic=B();optic.box((1.38,.12,.038),(0,-.22,height+.37),mat('ink enamel'),.004)
                optic.box((1.29,.090,.008),(0,-.22,height+.345),mat('warm diffuser'),.001)
                for xx in [-.62,.62]:optic.box((.035,.19,.08),(xx,-.145,height+.365),mat('dark steel'),.002)
                lamp=add(optic,name+' header reading optic','FC | Practicals',pos=pos,normal=n,parent=o.name,family='header-supported sign reading luminaire')
                light('Refinery header reading pool',T@Vector((0,-.22,height+.337)),T@Vector((0,-.17,height+.26)),10,(1,.85,.68),size=1.2,shape='RECTANGLE',size_y=.08,parent=lamp.name)
    if state!='PASSAGE':
        ceiling_h=next(c['height'] for c in json.loads(CONTRACT.read_text())['floor_cells'] if c['id']==floorcell)
        hh=ceiling_h-height-.34
        if hh>.045:
            seal=B();sw=width+.08
            # Continuous folded lower/upper returns and removable roof pan bays.
            for zz in [.012,hh-.012]:seal.box((sw,.10,.024),(0,.085,zz),mat('dark steel'),.002)
            for xx in [-sw/2+.013,sw/2-.013]:seal.box((.026,.10,hh),(xx,.085,hh/2),mat('dark steel'),.002)
            for i in range(3):
                xx=(i-1)*sw/3
                seal.box((sw/3-.013,.025,hh-.036),(xx,.121,hh/2),mat('replacement enamel'),.003)
                for xfix in [xx-sw/6+.047,xx+sw/6-.047]:
                    for zz in [.046,hh-.046]:bolt(seal,(xfix,.106,zz),.006)
            add(seal,name+' folded roof closure','FC | Architecture',pos=T@Vector((0,0,height+.34)),normal=n,parent=o.name,family='folded roof-to-portal closure')
    return o

def freight_mechanism(frame_ob):
    p=frame_ob.matrix_world@Vector((0,-.01,3.64))
    drive=add(A.gate_drive(),'Freight gate track and motor','FC | Doors',pos=p,normal=(-1,0,0),parent=frame_ob.name,family='cast sliding-door drive and twin rail')
    light('Freight drive task pool',drive.matrix_world@Vector((1.13,-.427,.434)),drive.matrix_world@Vector((1.07,-.235,.20)),7,(1,.83,.63),size=.39,shape='RECTANGLE',size_y=.17,parent=drive.name)
    root=bpy.data.objects.new('FREIGHT_GATE',None);coll('FC | Runtime metadata').objects.link(root)
    root['port_id']='INTERNAL_FREIGHT_GATE';root['geometry_owner']='fuel-corridor';root['presentation_cap']=False
    for suffix,carriage_name in [(' left leaf','FREIGHT_GATE_LEFT_CARRIAGE'),(' right leaf','FREIGHT_GATE_RIGHT_CARRIAGE')]:
        leaf=bpy.data.objects['FC | Freight gate'+suffix];world=leaf.matrix_world.copy()
        carriage=bpy.data.objects.new(carriage_name,None);coll('FC | Runtime metadata').objects.link(carriage);carriage.parent=root
        carriage['component_role']='sliding_leaf_carriage';carriage['current_pose']='OPEN';carriage['closed_to_open_translation_m']=list(leaf['closed_to_open_translation_m'])
        carriage['translation_coordinate_space']='section metres; parent root has identity transform';carriage['controller_status']='Editable rigid assembly; engine controller and continuous physics sweep unverified'
        leaf.parent=carriage;leaf.matrix_world=world;leaf['fc_attachment_to']=drive.name
    # Motor load is taken by two real posts attached to the portal header.
    b=B()
    for x in [-1.30,1.30]:
        b.box((.11,.20,.20),(x,-.04,-.02),mat('dark steel'),.003)
        b.box((.145,.180,.024),(x,-.042,.080),mat('replacement enamel'),.002)
        bolt(b,(x,-.042,.095),.008,axis='Z')
    add(b,'Freight drive clevis mounts','FC | Doors',pos=p,normal=(-1,0,0),parent=frame_ob.name,family='drive load-bearing clevis')
    lamp=B()
    # A real hood on the portal front illuminates the leaf plane when CLOSED.
    lamp.box((1.28,.25,.075),(0,-.245,3.615),mat('ink enamel'),.008)
    lamp.box((1.15,.185,.012),(0,-.254,3.574),mat('warm diffuser'),.002)
    lamp.box((.99,.080,.012),(0,-.335,3.660),mat('cool diffuser'),.002,rot=Matrix.Rotation(-.34,3,'X'))
    for x in [-.59,.59]:
        lamp.box((.055,.12,.085),(x,-.178,3.614),mat('dark steel'),.004)
        bolt(lamp,(x,-.375,3.615),.006)
    hood=add(lamp,'Freight leaf inspection hood','FC | Practicals',pos=frame_ob.location,normal=(-1,0,0),parent=frame_ob.name,family='portal-mounted folded inspection luminaire')
    light('Freight closed-leaf inspection pool',hood.matrix_world@Vector((0,-.285,3.562)),hood.matrix_world@Vector((0,-.105,1.6)),70,(1,.88,.73),size=1.1,shape='RECTANGLE',size_y=.17,parent=hood.name)
    light('Freight channel inspection uplight',hood.matrix_world@Vector((0,-.335,3.674)),hood.matrix_world@Vector((0,-.090,3.88)),5,(.83,.89,1),size=.94,shape='RECTANGLE',size_y=.060,parent=hood.name)
    # The lower open C-channel needs light inside its own returns, rather than
    # hoping a roof light reaches it through the track and guard above it.
    strip=B();spans=[(-1.48,-.91),(-.85,-.03),(.03,.85),(.91,1.48)]
    for a,c in spans:
        strip.box((c-a,.037,.010),((a+c)/2,-.066,3.635),mat('replacement enamel'),.002)
        strip.box((c-a-.045,.024,.003),((a+c)/2,-.066,3.6285),mat('warm diffuser'),.0006)
    wash=add(strip,'Freight lower-channel service optic','FC | Practicals',pos=frame_ob.location,normal=(-1,0,0),parent=frame_ob.name,family='recessed header inspection strip physically carried by top flange')
    for i,(a,c) in enumerate(spans):
        xx=(a+c)/2
        light('Freight lower-channel inspection pool '+str(i),wash.matrix_world@Vector((xx,-.066,3.625)),wash.matrix_world@Vector((xx,.025,3.56)),.6,(.96,.87,.74),size=c-a-.055,shape='RECTANGLE',size_y=.022,parent=wash.name)
    wallname='Wall_W6.07_1_12.2'
    if wallname in WALLS:
        mounted(A.cabinet(.18,.27,.08),'Freight drive guarded disconnect',wallname,(-.25,-.008,.89),family='guarded disconnect')

def service_soffit(frame_ob):
    """Close the height transition above the personnel portal with a service bay."""
    b=B();h=1.48;w=2.43
    # The folded perimeter and lower lip bridge onto the actual header.
    frame(b,w,h,.055,.12,.090,h/2,mat('ink enamel'),r=.024)
    b.box((1.25,.020,.09),(0,.145,.045),mat('dark steel'),.002)
    b.box((w-.105,.025,.69),(0,.105,.365),mat('cool plaster'),.003)
    b.box((w-.105,.025,.265),(0,.105,1.30),mat('warm enamel'),.003)
    for x in [-.865,.865]:b.box((.53,.025,.475),(x,.105,.956),mat('warm enamel'),.003)
    grille=A.vent(1.16,.40)
    for v in grille.bm.verts:v.co+=Vector((0,.083,.96))
    material_map={i:b._idx(m) for i,m in enumerate(grille.mats)}
    for f in grille.bm.faces:f.material_index=material_map[f.material_index]
    # Join authored bmesh without introducing an external asset dependency.
    temp=grille.bm.copy();mesh=bpy.data.meshes.new('temporary soffit vent');temp.to_mesh(mesh);temp.free();b.bm.from_mesh(mesh);bpy.data.meshes.remove(mesh);grille.bm.free()
    b.box((1.095,.009,.335),(0,.212,.96),mat('rubber'),.002)
    for x in [-1.11,1.11]:
        for z in [.14,1.35]:bolt(b,(x,.024,z),.009)
    return add(b,'Service height-transition bulkhead','FC | Architecture',pos=frame_ob.matrix_world@Vector((0,0,2.92)),normal=(0,-1,0),parent=frame_ob.name,family='folded service bulkhead with real louvre cavity')

def section_workstations():
    board=mounted(A.maintenance_notice(),'Transfer handover board','Wall_W-2.2_0_1.2',(-1.2,-.004,1.46),'FC | Narrative','framed handover board with clipped papers')
    for text,p,size in [('TRANSFER CHECKS',(0,-.0415,.59),.042),('JOB / 017',(.29,-.0435,.427),.029),('SHIFT B',(.26,-.0465,.174),.021)]:
        label(text,board.matrix_world@Vector(p),size,normal=(1,0,0),parent=board.name)
    sconce('Handover reading practical','Wall_W-2.2_0_1.2',(-1.2,-.004,2.29),65,False)
    console=mounted(A.interlock_console(),'Reactor transfer interlock','Wall_E17.0_0_21',(.12,-.0085,.72),'FC | Services','cast and folded interlock console')
    label('TRANSFER / READY',console.matrix_world@Vector((0,-.2145,.39)),.025,normal=(-1,0,0),parent=console.name)
    sconce('Interlock inspection practical','Wall_E17.0_0_21',(.12,-.004,2.00),65,False)
    sign('Waste bay identification','Wall_E16.4_0_7',(3.5,-.004,2.30),'WASTE / SEALED',.060,.91,coat='oxide enamel')
    extractor=mounted(A.exhaust_collector(),'East extraction collector','Wall_E16.4_0_7',(.84,-.004,1.65),'FC | Services','folded extractor and hollow flanged duct')
    label('EXTRACT / 03',extractor.matrix_world@Vector((0,-.315,.948)),.029,normal=(-1,0,0),parent=extractor.name)
    clean=mounted(A.clean_station(),'Clean transfer wipe station','Wall_N21_0_-1.5',(-2.43,-.004,1.33),'FC | Narrative','clean transfer rack with actual cloth and job sheet')
    label('CLEAN / 02',clean.matrix_world@Vector((-.20,-.053,.535)),.024,normal=(0,-1,0),parent=clean.name)
    sign('Clean bay large direction','Wall_N21_0_-1.5',(-2.49,-.004,2.25),'CLEAN  >',.22,1.45,coat='warm enamel',stand_off=.030)
    water=mounted(A.flow_monitor(),'Plant flow monitor','Wall_N18.6_0_-5.4',(.89,-.004,1.43),'FC | Services','tapped process monitor connected to plant water main')
    label('FLOW / S01',water.matrix_world@Vector((0,-.101,.109)),.030,normal=(0,-1,0),parent=water.name)
    vessel=A.sealed_transfer_bin()
    vessel.box((.185,.018,.104),(0,-.228,.407),mat('warm enamel'),.006)
    for xx in [-.077,.077]:bolt(vessel,(xx,-.240,.407),.004)
    bin_ob=add(vessel,'Sealed waste transfer vessel','FC | Narrative',pos=(15.95,17.78,0),normal=(-1,0,0),target=FLOORS['delivery'],anchors=[(-.15,-.14,0),(.15,-.14,0),(-.15,.13,0),(.15,.13,0)],direction=(0,0,-1),kind='floor',family='gasketed transfer vessel with wheeled base and foot latch')
    label('B / 017',bin_ob.matrix_world@Vector((0,-.238,.407)),.042,normal=(-1,0,0),material='ink',parent=bin_ob.name)
    seal=mounted(A.waste_seal_station(),'Waste seal and receipt station','Wall_E16.4_0_7',(-3.08,-.0085,.78),'FC | Narrative','receipt roll and captive seal tool on a supported folded pan')
    label('SEAL / RECEIPT',seal.matrix_world@Vector((0,-.071,.81)),.054,normal=(-1,0,0),material='ink',parent=seal.name)
    label('B / 017',seal.matrix_world@Vector((-.16,-.224,.468)),.032,normal=(-1,0,0),material='ink',parent=seal.name)
    sconce('Waste sealing task practical','Wall_E16.4_0_7',(-3.08,-.004,2.02),48,False)
    sconce('Waste receipt inspection practical','Wall_E16.4_0_17.32',(1.39,-.004,2.25),60,True)

def process_bays():
    bank=mounted(A.fuel_conditioner(),'Fuel conditioning and purge bank','Wall_E2.2_0_1.2',(-.85,-.0085,.31),'FC | Services','connected twin filter bank with real drain tray and isolation valve')
    for txt,p in [('FILTER / 01',(-.36,-.339,.80)),('SKIM / 02',(.36,-.339,.80))]:
        label(txt,bank.matrix_world@Vector(p),.020,normal=(-1,0,0),parent=bank.name)
    sign('Fuel conditioning identity','Wall_E2.2_0_1.2',(-.85,-.004,2.20),'FUEL CONDITIONING',.095,1.63,coat='oxide enamel')
    sconce('Filter bank reading practical','Wall_E2.2_0_1.2',(-.85,-.004,2.62),85,False)
    ppe=mounted(A.protective_kit(),'Transfer protective-kit rack','Wall_W-2.2_0_1.2',(-.20,-.004,.89),'FC | Narrative','draped canvas apron and moulded respirator on actual hooks')
    sign('Protective kit identity','Wall_W-2.2_0_1.2',(-.20,-.004,1.96),'TRANSFER KIT',.071,.86,coat='warm enamel')
    # The horizontal collector overlaps the existing riser at its sealed flanged joint.
    mounted(A.extraction_header(3.3),'East extraction service header','Wall_E16.4_0_7',(.84,-.004,4.02),'FC | Services','hollow extraction header with service hatch and cantilever saddles')
    mounted(A.extraction_header(2.1),'North clean-air service header','Wall_N21_0_7.72',(.52,-.004,2.70),'FC | Services','hollow clean-air header with inspection hatch')
    rack=add(A.linen_rack(),'Clean-transfer open linen rack','FC | Narrative',pos=(3.80,20.985,0),target=FLOORS['bypass_north'],anchors=[(-.40,-.055,0),(.40,-.055,0),(-.40,-.29,0),(.40,-.29,0)],direction=(0,0,-1),kind='floor',family='open supply rack with folded cloth canvas bag and refill bottles')
    label('CLEAN STOCK',rack.matrix_world@Vector((0,-.0555,1.37)),.031,parent=rack.name)
    log=mounted(A.clean_log_board(),'Clean-transfer inspection log','Wall_S18.0_0_1.2',(.60,-.004,1.42),'FC | Narrative','fabricated inspection station with clipped sheets and staged pen')
    label('SHIFT / CHECK',log.matrix_world@Vector((.20,-.068,.62)),.023,normal=(0,1,0),parent=log.name)
    sconce('Clean stock preparation practical','Wall_N21_0_-1.5',(1.81,-.004,2.28),75,True)
    sconce('Clean log reading practical','Wall_S18.0_0_1.2',(.60,-.004,2.33),50,True)
    cooler=mounted(A.coolant_heat_exchanger(),'Reactor return cooling cassette','Wall_N13.2_2_10',(0,-.004,.30),'FC | Services','open heat-exchanger fins with sump guarded pipes and a connected riser')
    label('RETURN / 02',cooler.matrix_world@Vector((.17,-.337,1.66)),.038,normal=(0,-1,0),parent=cooler.name)
    sign('East turn reactor designation','Wall_N13.2_2_10',(0,-.004,2.56),'REACTOR  /  02  >',.13,1.73,coat='oxide enamel',stand_off=.19)
    sconce('Reactor cooling inspection practical','Wall_N13.2_2_10',(0,-.004,2.96),75,True)
    route=B();route.tube(rounded_path([(11.18,13.153,3.59),(11.98,13.153,3.59),(12.134,13.307,3.59),(12.134,14.08,3.59)]),.023,mat('steel'),seg=20)
    for x in [11.35,11.89]:ring(route,.034,.021,(x,13.153,3.59),mat('brass'),axis='X',seg=24)
    route.box((.072,.015,.12),(11.45,13.2875,3.59),mat('dark steel'),.002)
    route.tube([(11.45,13.28,3.59),(11.45,13.153,3.59)],.007,mat('dark steel'),seg=12)
    route.box((.015,.072,.12),(12.0115,14.08,3.59),mat('dark steel'),.002)
    route.tube([(12.019,14.08,3.59),(12.134,14.08,3.59)],.007,mat('dark steel'),seg=12)
    circuit=add(route,'Cooling return corner union','FC | Services',family='clamped corner return circuit joining heat exchanger and delivery cooling main')
    support(circuit,[WALLS['Wall_N13.2_2_10'],WALLS['Wall_W12_0_13.2']],[(11.45,13.295,3.59),(12.004,14.08,3.59)],(0,1,0),'wall')
    circuit['support_directions']=json.dumps([[0,1,0],[-1,0,0]])
    mounted(A.plant_hose_reel(),'Plant utility wash-down reel','Wall_S16.2_0_-5.4',(.80,-.004,1.0),'FC | Services','formed shallow hose reel with continuous wound hose crank and utility feed')
    branch=B();branch.tube(rounded_path([(-3.88,18.466,2.55),(-3.88,18.36,2.67),(-3.88,18.20,2.80),(-3.88,16.52,2.80),(-3.88,16.34,2.70),(-3.88,16.260,2.55)]),.0255,mat('brass'),seg=20)
    for y in [18.18,16.54]:ring(branch,.041,.029,(-3.88,y,2.80),mat('brass'),axis='Y',seg=32)
    # A real flanged backflow/isolator assembly explains the visible utility run.
    branch.lathe([(0,0),(.035,0),(.058,.018),(.066,.059),(.066,.13),(.058,.17),(.035,.19),(0,.19)],(-3.88,16.955,2.80),mat('repaired blue enamel'),seg=32,rot=Matrix.Rotation(-math.pi/2,3,'X'))
    for y in [16.955,17.145]:
        ring(branch,.078,.013,(-3.88,y,2.80),mat('steel'),axis='Y',seg=32)
        for k in range(6):
            a=k*math.pi/3;bolt(branch,(-3.88+.061*math.cos(a),y-.013,2.80+.061*math.sin(a)),.006)
    branch.cyl(.017,.087,(-3.835,17.05,2.80),mat('brass'),seg=20,axis='X')
    branch.lathe([(.059,0),(.079,0),(.083,.008),(.080,.023),(.059,.023),(.059,0)],(-3.752,17.05,2.80),mat('ochre enamel'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'Y'))
    for k in range(3):
        a=k*2*math.pi/3;branch.tube([(-3.741,17.05,2.80),(-3.741,17.05+.069*math.cos(a),2.80+.069*math.sin(a))],.006,mat('ochre enamel'),seg=10)
    branch.box((.025,.20,.046),(-3.797,17.05,2.685),mat('warm enamel'),.004)
    branch.box((.016,.052,.10),(-3.831,17.05,2.728),mat('steel'),.003)
    for y,yy in [(18.590,18.48),(16.210,16.26)]:
        branch.box((.066,.012,.11),(-3.88,y,2.55),mat('dark steel'),.002)
        branch.tube([(-3.88,y,2.55),(-3.88,yy,2.55)],.007,mat('dark steel'),seg=12)
    feed=add(branch,'Plant wash-down cross-header','FC | Services',family='clamped utility branch joining north water main to south reel')
    label('WATER',(-3.782,17.05,2.685),.035,normal=(1,0,0),material='ink',parent=feed.name)
    support(feed,[WALLS['Wall_N18.6_0_-5.4'],WALLS['Wall_S16.2_0_-5.4']],[(-3.88,18.596,2.55),(-3.88,16.204,2.55)],(0,1,0),'wall')
    feed['support_directions']=json.dumps([[0,1,0],[0,-1,0]])
    sign('Plant utility reel identity','Wall_S16.2_0_-5.4',(.8,-.004,1.82),'UTILITY WATER',.065,.86)

def recess_service_handover():
    b=B();b.box((.53,.18,.014),(0,-.10,.007),mat('warm enamel'),.003)
    b.box((.53,.012,.18),(0,-.006,-.083),mat('dark steel'),.003)
    b.box((.53,.014,.10),(0,-.18,-.04),mat('warm enamel'),.003)
    for xx in [-.19,.19]:
        polygon(b,[(0,0),(-.16,0),(0,-.12)],.014,mat('dark steel'),pos=(xx,-.012,0),rot=Matrix.Rotation(math.pi/2,3,'Y')@Matrix.Rotation(math.pi/2,3,'Z'))
        bolt(b,(xx,-.014,-.115),.005)
    shelf=mounted(b,'Recess purge-service handover pan','Wall_W-1.65_0_14.3',(0,-.0085,1.20),'FC | Narrative','gusseted service ledge outside the bypass lane')
    roll=A.service_roll()
    add(roll,'Purge coupler service roll','FC | Narrative',pos=shelf.matrix_world@Vector((0,-.035,.014)),normal=(1,0,0),parent=shelf.name,family='stitched open canvas roll with spare brass couplers and a checked job slip')
    label('PURGE / CHECK B',shelf.matrix_world@Vector((0,-.188,-.04)),.041,normal=(1,0,0),material='ink',parent=shelf.name)

def auxiliary_cameras():
    # Additional branch evidence. Original 16 camera transforms/lenses stay fixed.
    for name,p,q,lens in [
        ('E01_WASTE_APPROACH',(12.60,15.8,1.7),(15.9,16.0,1.65),22),
        ('E02_CLEAN_APPROACH',(6.6,18.4,1.7),(6.6,20.5,1.65),16),
        ('E03_FREIGHT_LEAF',(3.8,10,1.7),(6.35,10,1.75),20)]:
        data=bpy.data.cameras.new(name);data.lens=lens;data.clip_start=.05;data.clip_end=200
        ob=bpy.data.objects.new(name,data);coll('FC | Additional review cameras').objects.link(ob)
        ob.matrix_world=Matrix.Translation(Vector(p))@(Vector(q)-Vector(p)).to_track_quat('-Z','Y').to_matrix().to_4x4()
        ob['fc_revision']='overhaul-20261001';ob['fc_asset_family']='additional branch evidence camera'
        ob['review_scope']='Supplementary player-height view; original 16 preserved'

def crossing_service_bulkheads():
    """Wall-borne hollow crowns give the transfer route architectural depth."""
    rot=Matrix(((0,0,1),(1,0,0),(0,1,0)))
    outline=[(7.804,4.380),(12.196,4.380),(12.196,3.900),(11.74,3.60),(8.26,3.60),(7.804,3.900)]
    lower=[(7.804,3.900),(8.26,3.600),(11.74,3.600),(12.196,3.900),(12.196,3.918),(11.74,3.618),(8.26,3.618),(7.804,3.918)]
    for i,xx in enumerate([7.65,9.40]):
        b=B()
        for xface in [-.090,.084]:polygon(b,outline,.006,mat('warm enamel' if i==0 else 'reactor sheet'),pos=(xx+xface,0,0),rot=rot,bevel=.001)
        polygon(b,lower,.18,mat('steel'),pos=(xx-.09,0,0),rot=rot,bevel=.001)
        b.box((.18,4.392,.016),(xx,10,4.372),mat('dark steel'),.002)
        for yy in [7.808,12.192]:b.box((.18,.008,.48),(xx,yy,4.140),mat('dark steel'),.002)
        for yy in [8.36,11.64]:
            b.box((.016,.065,.58),(xx-.098,yy,3.975),mat('steel'),.003)
            for zz in [3.76,4.18]:bolt(b,(xx-.108,yy,zz),.009,axis='NX')
        # Removable formed panel, physical reveal and supported identity plate.
        b.box((.018,2.34,.036),(xx-.104,10,4.215),mat('replacement enamel'),.003)
        b.box((.018,2.34,.036),(xx-.104,10,3.75),mat('replacement enamel'),.003)
        b.box((.016,1.82,.19),(xx-.105,10,3.99),mat('ink enamel'),.005)
        for yy in [9.16,10.84]:bolt(b,(xx-.116,yy,3.99),.006,axis='NX')
        ob=add(b,'Crossing hollow service crown '+str(i),'FC | Architecture',family='folded wall-borne service bulkhead with open rear and bolted removable faces')
        support(ob,[WALLS['Wall_S7.8_1_6.78'],WALLS['Wall_N12.2_1_6.78']],[(xx,7.804,4.18),(xx,12.196,4.18)],(0,-1,0),'wall')
        ob['support_directions']=json.dumps([[0,-1,0],[0,1,0]])
        label('FUEL / TRANSFER' if i==0 else 'PROCESS / 02',(xx-.114,10,3.99),.135,normal=(-1,0,0),parent=ob.name)

def floor_graphics():
    # Paint stops at real slab joints: no floating strip across a 20mm recess.
    contract=json.loads(CONTRACT.read_text());shapes=[]
    chevron=[(-.32,-.20),(0,.06),(.32,-.20),(.32,-.08),(0,.22),(-.32,-.08)]
    for y in [3.0,5.0,6.7,14.8,17.8,20.5]:
        x=0 if y<7 else 14.2
        shapes.append(([(x+u,y+v) for u,v in chevron],'ochre enamel'))
    for x in [3.7,8.8,12.7]:shapes.append(([(x-v,10+u) for u,v in chevron],'ochre enamel'))
    def strip(x,y,w,h):shapes.append(([(x-w/2,y-h/2),(x+w/2,y-h/2),(x+w/2,y+h/2),(x-w/2,y+h/2)],'white ink'))
    for y in [11.84,12.81]:
        for x in [2.08,2.65,3.22]:strip(x,y,.38,.018)
    for x in [1.78,3.52]:strip(x,12.32,.018,.66)
    def clip(poly,axis,bound,lower):
        result=[]
        for a,c in zip(poly[-1:]+poly[:-1],poly):
            ina=(a[axis]>=bound if lower else a[axis]<=bound);inc=(c[axis]>=bound if lower else c[axis]<=bound)
            if ina!=inc:
                t=(bound-a[axis])/(c[axis]-a[axis]);result.append((a[0]+t*(c[0]-a[0]),a[1]+t*(c[1]-a[1])))
            if inc:result.append(c)
        return result
    for cell in contract['floor_cells']:
        if cell['id'] not in FLOORS:continue
        b=B();anchors=[];xmin,xmax,ymin,ymax=cell['bounds'];nx,ny,sx,sy,_=tile_layout(cell)
        for i in range(nx):
            for j in range(ny):
                for shape,material in shapes:
                    poly=shape
                    for axis,bound,lower in [(0,xmin+i*sx+.004,True),(0,xmin+(i+1)*sx-.004,False),(1,ymin+j*sy+.004,True),(1,ymin+(j+1)*sy-.004,False)]:
                        if poly:poly=clip(poly,axis,bound,lower)
                    if len(poly)<3:continue
                    area=abs(sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(poly,poly[1:]+poly[:1])))
                    if area<1e-7:continue
                    polygon(b,poly,.00035,mat(material),pos=(0,0,.0001))
                    anchors.append((sum(p[0] for p in poly)/len(poly),sum(p[1] for p in poly)/len(poly),.0001))
        if anchors:add(b,'Freight paint '+cell['id'],'FC | Floor markings',target=FLOORS[cell['id']],anchors=anchors,direction=(0,0,-1),kind='floor',family='joint-clipped floor stencil')

def run():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['slice','full'],default='full')
    parser.add_argument('--output');opts=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_HASH,'Baseline changed'
    recipe_paths=[Path(__file__).resolve(),Path(__file__).with_name('fuel_kit.py'),Path(A.__file__).resolve(),ROOT/'sections/spawn-room/blender/cozy_geo.py',CONTRACT]
    recipe_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in recipe_paths}
    recipe_hash=hashlib.sha256(json.dumps(recipe_inputs,sort_keys=True).encode()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False)
    contract=json.loads(CONTRACT.read_text());palette()
    # Asset/core inventory is recorded before mutation, never inferred from output names.
    original=[{'name':o.name,'type':o.type,'bounds':bounds(o) if o.type=='MESH' else None,
               'geometry':digest(o) if o.type=='MESH' else None} for o in bpy.context.scene.objects]
    baseline_cameras=[{'name':o.name,'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in bpy.context.scene.objects if o.type=='CAMERA']
    baseline_runtime=[{'name':o.name,'matrix':[list(r) for r in o.matrix_world]} for o in bpy.context.scene.objects if o.type=='EMPTY' and o.name.startswith('FC_')]
    cores=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.endswith('_concrete')]
    records=[r for o in cores if (r:=wall_record(o))]
    full=opts.stage=='full'
    slice_walls={'Wall_W-2.2_0_1.2','Wall_N13.2_1_1.2','Wall_N13.2_0_-2.2',
                 'Wall_W6.07_0_6.15','Wall_W6.07_1_12.2','Wall_E6.78_0_6.15','Wall_E6.78_1_12.2',
                 'Wall_S6.15_0_6.07','Wall_N13.85_0_6.07'}
    # Only invisible structural cores, metadata and fixed cameras are retained.
    keep={o.name for o in cores}|{'Floor_'+c['id'] for c in contract['floor_cells']}|{'Ceiling_'+c['id'] for c in contract['floor_cells']}
    runtime=[(o,o.matrix_world.copy()) for o in bpy.context.scene.objects if o.type=='EMPTY' and o.name.startswith('FC_')]
    for o,T in runtime:
        o.parent=None;o.matrix_world=T
        for c in list(o.users_collection):c.objects.unlink(o)
        coll('FC | Runtime metadata').objects.link(o)
    if full:
        for o in list(bpy.context.scene.objects):
            if o.type in ['CAMERA'] or o.name in keep or (o.type=='EMPTY' and o.name.startswith('FC_')):continue
            remove(o)
    else:
        for r in records:
            if r['name'] in slice_walls:
                parent=bpy.data.objects.get(r['name'])
                for o in list(parent.children_recursive) if parent else []:
                    if o.name!=r['core']:remove(o)
        for name in ['Maintenance_bench','Maintenance_tool_board','Long_cask_carrier','Dispatch_paperwork_station','Staging_air_station','Bench_worklight','Cask_task_light','Staging_vent','Freight_advance_sign','Bay_identity','Staging_warm_key','Gate_cool_fill','Staging_front_practical']:
            delete_assembly(name)
        for o in list(bpy.context.scene.objects):
            if o.type=='MESH' and any(k in o.name.lower() for k in ['arrow','route_paint','parking_paint']):remove(o)
    for o in cores:
        PROTECTED.append({'name':o.name,'geometry':digest(o),'bounds':bounds(o)})
        if full or o.name[:-9] in slice_walls:
            o.data.materials.clear();o.data.materials.append(mat('mineral'));o['fc_asset_family']='protected exterior structural core';o['fc_revision']='overhaul-20261001';o['fc_support_kind']='structural-core'
    for r in records:
        if full or r['name'] in slice_walls:wall(r)
    staging_process_recess()
    if full:staging_process_recess('Wall_N13.2_2_10')
    for cell in contract['floor_cells']:
        if full or cell['id'] in ['west_turn','crossing','freight_gate_south_pocket','freight_gate_north_pocket']:floor(cell);ceiling(cell)
    staging();floor_graphics()
    if not full:
        for name in ['FREIGHT_GATE','Freight_gate_drive','Freight_gate_crown','Gate_motor_task_lamp','Transfer_gate_key']:
            delete_assembly(name)
        fg=portal('Freight gate',(6.35,10,0),(-1,0,0),3.0,3.5,'navy enamel','FREIGHT / FG01',state='OPEN',floorcell='crossing')
        freight_mechanism(fg)
        service_frame=portal('Personnel bypass',(0,13.05,0),(0,-1,0),2.4,2.6,'navy enamel','SERVICE',state='PASSAGE',floorcell='west_turn')
        service_soffit(service_frame)
    if full:
        # These threshold planes are exactly 0.50 m inboard of the frozen seam.
        portal('Refinery boundary',(0,.5,0),(0,1,0),2.6,3.0,'oxide enamel','REFINERY / F01',floorcell='inlet')
        portal('Reactor boundary',(14.2,23.5,0),(0,-1,0),5.0,5.0,'navy enamel','REACTOR / F02',floorcell='reactor_adapter')
        portal('Plant service',(-4.9,17.4,0),(1,0,0),2.0,2.5,'navy enamel','PLANT / S01',floorcell='plant_header')
        portal('Clean service',(6.6,20.5,0),(0,-1,0),2.0,2.5,'warm enamel','CLEAN / S02',floorcell='bypass_north')
        portal('Waste transfer',(15.9,16,0),(-1,0,0),2.4,3.0,'oxide enamel','WASTE / S03',floorcell='delivery')
        service_frame=portal('Personnel bypass',(0,13.05,0),(0,-1,0),2.4,2.6,'navy enamel','SERVICE',state='PASSAGE',floorcell='west_turn')
        service_soffit(service_frame)
        fg=portal('Freight gate',(6.35,10,0),(-1,0,0),3.0,3.5,'navy enamel','FREIGHT / FG01',state='OPEN',floorcell='crossing')
        freight_mechanism(fg)
        services();work_traces();section_workstations();process_bays();crossing_service_bulkheads();auxiliary_cameras()
        for name,wallname,point,title in [
            ('Service bypass','Wall_N13.2_0_-2.2',(.0,-.004,3.0),'SERVICE'),
            ('Plant direction','Wall_E1.2_0_13.2',(1.39,-.004,2.3),'PLANT  <'),
            ('Clean direction','Wall_N21_0_-1.5',(-1.20,-.004,2.02),'CLEAN  >'),
            ('Reactor approach','Wall_W12_0_13.2',(.0,-.004,2.4),'REACTOR  ^')]:
            if wallname in WALLS:sign(name,wallname,point,title,.069,.82)
        mounted(A.cabinet(.39,.52,.11,True),'Bypass first-aid cabinet','Wall_E1.2_0_13.2',(.4,-.004,1.37),family='first-aid cabinet')
        mounted(A.cabinet(.41,.58,.11),'Bypass isolation cabinet','Wall_E1.2_0_13.2',(-.65,-.004,1.37),family='isolation cabinet')
        mounted(A.manifold(.62,.68),'Recess service manifold','Wall_W-1.65_0_14.3',(.0,-.004,1.38),'FC | Services','cast air manifold')
        recess_feed()
        recess_service_handover()
        mounted(A.cabinet(.70,1.02,.21),'East service cabinet','Wall_S7_1_10',(-2.0,-.0115,.18),family='service supply cabinet')
        mounted(A.cabinet(.50,.72,.15),'East electrical distribution','Wall_E16.4_0_7',(-1.55,-.004,1.36),family='distribution cabinet')
        mounted(A.cabinet(.49,.62,.13),'Clean service distribution','Wall_S18.0_0_1.2',(-2.4,-.004,1.37),family='distribution cabinet')
        cabinet_feed('Clean cabinet feed','Wall_S18.0_0_1.2',(-2.4,-.142,2.68),(-2.4,-.07,1.99),'FC | Clean service distribution')
        cabinet_feed('East distribution feed','Wall_E16.4_0_7',(-1.55,-.142,3.83),(-1.55,-.08,2.08),'FC | East electrical distribution')
        for name,wallname,point in [('Entry extract','Wall_E2.2_0_1.2',(0,-.004,3.15)),('East extract','Wall_S7_1_10',(.6,-.004,3.13)),('Clean extract','Wall_N21_0_7.72',(-.75,-.004,2.41))]:
            recessed_vent(name,wallname,point,.77,.36)
        for name,p,L,E,cool,cell in [
            ('Entry fluorescent',(0,4.6,3.789),1.35,160,False,'entry'),
            ('Crossing fluorescent',(8.0,10,4.389),1.15,240,True,'crossing'),
            ('East fluorescent',(14.2,10.4,4.389),1.3,250,False,'east_turn'),
            ('Delivery fluorescent',(14.2,17.2,4.389),1.45,255,True,'delivery'),
            ('Reactor transfer fluorescent',(14.2,22.2,5.889),1.7,350,False,'reactor_adapter'),
            ('Bypass fluorescent',(0,16.6,2.989),.82,140,True,'bypass_west'),
            ('North fluorescent',(3.8,19.65,2.989),1.0,140,False,'bypass_north'),
            ('Clean fluorescent',(9.9,19.65,2.989),.95,160,True,'bypass_north'),
            ('Plant fluorescent',(-3.4,17.4,2.989),.85,160,False,'plant_header')]:overhead(name,p,L,E,cool,cell)
        for name,wn,point,e,c in [('Entry side practical','Wall_W-2.2_0_1.2',(-2.9,-.004,2.26),55,False),
                                ('Bypass corner practical','Wall_N21_0_-1.5',(-2.9,-.004,2.30),45,False),
                                ('East-turn practical','Wall_E16.4_0_7',(0,-.004,2.50),80,False),
                                ('Reactor approach practical','Wall_W12_0_13.2',(0,-.004,2.67),85,True),
                                ('Recess practical','Wall_W-1.65_0_14.3',(0,-.004,2.20),62,False)]:sconce(name,wn,point,e,c)
    bpy.context.scene.world.use_nodes=True
    bg=bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:bg.inputs['Color'].default_value=(.24,.27,.31,1);bg.inputs['Strength'].default_value=.055
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.seed=7
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
    scene.render.resolution_x=1440;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    if full:bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
    # No dependency on host-only font paths. Packed source fonts survive cold open.
    bpy.ops.file.pack_all()
    for o in cores:
        before=next(p for p in PROTECTED if p['name']==o.name)
        assert max(abs(bounds(o)[j][i]-before['bounds'][j][i]) for i in range(3) for j in range(2))<.00001,'Outer wall footprint changed: '+o.name
        if not any(x['wall']+'_concrete'==o.name for x in RECESSES):assert digest(o)==before['geometry']
    assert recipe_inputs=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in recipe_paths},'Construction inputs changed during build; rerun from a stable snapshot'
    bpy.data.collections['MODULE_fuel-corridor']['fc_recipe_sha256']=recipe_hash
    bpy.context.preferences.filepaths.save_version=0
    out=(Path(opts.output) if opts.output else (SOURCE if full else TASK/'production/checkpoints/fuel_style_slice.blend')).resolve()
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False,compress=True)
    report={'stage':opts.stage,'base_sha256':BASE_HASH,'output':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'recipe_inputs':recipe_inputs,'recipe_sha256':recipe_hash,
            'protected_exterior_cores':PROTECTED,'baseline_asset_inventory':original,
            'new_assets':[{'name':o.name,'family':o.get('fc_asset_family'),'support_kind':o.get('fc_support_kind'),'attachment':o.get('fc_attachment_to')} for o in scene.objects if o.get('fc_revision')],
            'fixed_cameras':[o.name for o in scene.objects if o.type=='CAMERA'],
            'baseline_cameras':baseline_cameras,'baseline_runtime':baseline_runtime,
            'wall_assets':WALLS,'floor_assets':FLOORS,'ceiling_assets':CEILINGS,'original_ports':contract['ports'],
            'localized_recesses':RECESSES}
    p=TASK/'production'/('SLICE_BUILD.json' if not full else 'BUILD_MANIFEST.json');p.write_text(json.dumps(report,indent=2))
    print('FUEL_BUILD',opts.stage,len(scene.objects),'objects',report['sha256'],flush=True)

if __name__=='__main__':run()
