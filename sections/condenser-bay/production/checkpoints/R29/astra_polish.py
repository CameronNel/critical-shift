"""R22+ replayable continuation of Grok R21. Cameras and room frame preserved.

The small removed sets are defective fittings, not a replacement room.
Eevee glass uses an explicit transparent surface approximation, raytracing off.
"""
import math
import bpy
from mathutils import Vector, Matrix
import kit as k
from layout import *


def remove_prefix(*prefixes):
    for o in list(k.S.objects):
        if any(o.name.startswith(p) for p in prefixes):
            bpy.data.objects.remove(o, do_unlink=True)


def assign(o, key):
    o.data.materials.clear()
    o.data.materials.append(k.M[key])


def tube(name, p, outer, inner, length, material, axis='Z'):
    # True annular tube with end-wall thickness, unlike the legacy annulus helper.
    n = 48
    verts = []
    rotation = {'Z': Matrix.Identity(3), 'Y': Matrix.Rotation(math.pi / 2, 3, 'X'),
                'X': Matrix.Rotation(math.pi / 2, 3, 'Y')}[axis]
    for z, r in [(-length / 2, outer), (length / 2, outer),
                 (-length / 2, inner), (length / 2, inner)]:
        for i in range(n):
            a = i * math.tau / n
            verts.append(Vector(p) + rotation @ Vector((r*math.cos(a), r*math.sin(a), z)))
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces += [(i,j,n+j,n+i), (2*n+i,3*n+i,3*n+j,2*n+j),
                  (i,2*n+i,2*n+j,j), (n+i,n+j,3*n+j,3*n+i)]
    return k.mesh(name,verts,faces,material,0,True)


def materials():
    k.M['cream'] = k.material('Astra ivory painted steel', 'B6B4AB', .58, .16, .025, .00015)
    k.M['steel'] = k.material('Astra brushed fastener steel', '777A7B', .40, .74, .015)
    k.M['bellows'] = k.material('Astra formed stainless bellows', '64666A', .55, .65, .025)
    k.M['water'] = k.material('Astra warm neutral liquid column', 'B5AB85', .12, .0, trans=.6)
    k.M['water'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.333
    # CPU Cycles supports physical transmission through the actual annular wall.
    k.M['glass'] = k.material('Astra borosilicate gauge glass', 'F8FAF8', .065, .0, trans=1)
    k.M['glass'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.47
    for o in k.S.objects:
        if o.type not in {'MESH','CURVE','FONT'}: continue
        for slot in o.material_slots:
            if not slot.material: continue
            old=slot.material.name
            if old=='Thermal jacket ivory': slot.material=k.M['cream']
            elif old=='Machined steel': slot.material=k.M['steel']
        if o.name.startswith('bellow'): assign(o,'bellows')
    # Smaller enamel highlight, without concealing the original cast volute shape.
    for key in ['oxide','oxide_light']:
        bs=k.M[key].node_tree.nodes.get('Principled BSDF')
        for link in list(bs.inputs['Roughness'].links): k.M[key].node_tree.links.remove(link)
        bs.inputs['Roughness'].default_value=.65
    for key in ['iron','rubber']:
        for n in k.M[key].node_tree.nodes:
            if n.type=='BUMP': n.inputs['Distance'].default_value=.00025


def sight_glasses():
    remove_prefix('level glass','level water','level guard')
    k.group('10 Condenser CD-01')
    for side in [-1,1]:
        face=CD_C[1]+side*(CD_WID_Y-.25)/2
        gy=face+side*.17
        for index,x in enumerate([2.38,3.62]):
            tag=f'LG {side} {index}'
            bottom,top=1.16,1.83
            tube(tag+' glass wall',(x,gy,(bottom+top)/2),.057,.050,top-bottom,'glass')
            # Water/air boundary visible against a pale scale card behind the glass.
            water_top=1.49 if index==0 else 1.50
            k.cyl(tag+' liquid',(x,gy,(bottom+water_top)/2),.047,water_top-bottom,'water','Z',48,.001)
            k.torus(tag+' meniscus',(x,gy,water_top),.046,.0018,'water')
            k.box(tag+' scale backing',(x,gy-side*.074,1.495),(.15,.018,.70),'paper',.002)
            for i in range(11):
                z=bottom+.035+i*.057
                k.box(tag+' graduation',(x+.045,gy+side*.066,z),(.023 if i%5 else .035,.004,.004),'ink',0)
            for z in [bottom-.025,top+.025]:
                k.cyl(tag+' gland',(x,gy,z),.071,.07,'brass','Z',16,.002)
                k.pipe(tag+' process cock',[(x,face-side*.04,z),(x,gy,z)],.023,'steel')
                k.cyl(tag+' cock body',(x,gy,z),.035,.10,'brass','Y',16,.002)
            for dx in [-.078,.078]:
                k.rod(tag+' protective rod',(x+dx,gy,bottom-.02),(x+dx,gy,top+.02),.006,'steel')
            k.text(tag+' ID','LEVEL',(x,gy+side*.075,top+.09),.042,'ink','N' if side==1 else 'S')


def return_connections():
    k.group('11 Condensate pumps')
    for name,x,y in [('CEP-A',P1[0],P1[1]),('CEP-B',P2[0],P2[1])]:
        cx=x-.38
        # Tangential cast outlet grows out of the top of the volute and meets the riser.
        k.cyl(name+' cast discharge boss',(cx,y,1.37),.118,.28,'oxide','Z',32,.006)
        k.cyl(name+' outlet flange lower',(cx,y,1.49),.153,.06,'oxide_light','Z',40,.003)
        k.cyl(name+' outlet gasket',(cx,y,1.525),.147,.014,'rubber','Z',40,.001)
        k.cyl(name+' outlet flange upper',(cx,y,1.56),.153,.06,'steel','Z',40,.003)
        for i in range(8):
            a=i*math.tau/8
            k.bolt(name+' outlet bolt',(cx+.124*math.cos(a),y+.124*math.sin(a),1.60),'Z',.012)
        # Delete buried hotwell nozzle and reroute the same suction to the actual north face.
        remove_prefix(name+' suction line',name+' HW ')
        hx=3+(.4 if name=='CEP-A' else -.4)
        face=4.05+(CD_WID_Y-.25)/2
        k.pipe(name+' suction line',[(cx,y,.35),(cx,y,-.17),(hx,y,-.17),(hx,face+.38,-.17),
                                   (hx,face+.22,1.23),(hx,face-.03,1.23)],.075,'cream',.14)
        k.cyl(name+' HW weld pad',(hx,face,1.23),.14,.07,'cream','Y',40,.003)
        k.cyl(name+' HW neck',(hx,face+.10,1.23),.095,.20,'cream','Y',32,.004)
        k.cyl(name+' HW flange inner',(hx,face+.20,1.23),.15,.05,'steel','Y',40,.003)
        k.cyl(name+' HW gasket',(hx,face+.231,1.23),.145,.012,'rubber','Y',40,.001)
        k.cyl(name+' HW flange outer',(hx,face+.262,1.23),.15,.05,'steel','Y',40,.003)
        for i in range(8):
            a=i*math.tau/8
            k.bolt(name+' HW bolt',(hx+.12*math.cos(a),face+.29,1.23+.12*math.sin(a)),'Y',.010)
        # Motor foot was separated from both motor and skid in baseline pixels.
        mx=x+.78
        for xx in [mx-.20,mx+.20]:
            k.box(name+' motor pedestal',(xx,y,.33),(.12,.38,.26),'struct',.003)
            k.box(name+' motor saddle riser',(xx,y,.61),(.14,.30,.20),'struct',.003)
        for xx in [mx-.13,mx+.13]:
            for yy in [y-.105,y+.105]: k.bolt(name+' terminal screw',(xx,yy,1.435),'Z',.009)
        remove_prefix(name+' motor feed')
        k.pipe(name+' motor feed',[(mx,y+.16,1.42),(mx,y+.40,1.42),(mx,y+.40,-.20),
                                  (-.88,y+.40,-.20),(-.88,y+.40,5.40)],.016,'rubber',.10)
    k.cyl('U02 local mating gasket',(7.9,.132,5.42),.137,.016,'rubber','Y',48,.001)
    k.cyl('U02 local front flange',(7.9,.176,5.42),.145,.064,'steel','Y',48,.002)
    for i in range(8):
        a=i*math.tau/8;x=7.9+.116*math.cos(a);z=5.42+.116*math.sin(a)
        k.cyl('U02 visible washer',(x,.213,z),.019,.009,'steel','Y',24,.001)
        k.cyl('U02 visible hex head',(x,.228,z),.014,.025,'steel','Y',6,.001)


def cooling_supports():
    k.group('12 Cooling water')
    bpy.context.view_layer.update()
    # The isolated discs in C06 are gauge BACKS with no impulse pipe, not pipe saddles.
    for tag,y in [('SUPPLY',3.2),('RETURN',4.9)]:
        centre=Vector((8.15,y,3.48))
        rotate=Matrix.Rotation(math.pi,4,'Z')
        around=Matrix.Translation(centre)@rotate@Matrix.Translation(-centre)
        for o in list(k.S.objects):
            if o.name.startswith('CW gauge '+tag): o.matrix_world=around@o.matrix_world
        k.pipe('CW '+tag+' impulse connection',[(8.55,y,3.20),(8.55,y,3.48),(8.18,y,3.48)],.019,'steel',.07)
        k.cyl('CW '+tag+' instrument root',(8.55,y,3.29),.037,.10,'brass','Z',16,.002)
        for i in range(12):
            a=i*math.tau/12; yy=y+.175*math.cos(a);z=3.15+.175*math.sin(a)
            k.cyl('CW visible wall washer',(9.505,yy,z),.020,.009,'steel','X',24,.001)
            k.cyl('CW visible wall bolt',(9.489,yy,z),.015,.025,'steel','X',6,.001)
    # Proper hollow split clamp envelopes the routed pipe, clevis joins the load rod.
    remove_prefix('CW saddle')
    ny=CD_C[1]+(CD_WID_Y-.15)/2
    ex=CD_C[0]+CD_LEN_X/2+WB_DEPTH/2
    wx=CD_C[0]-CD_LEN_X/2-WB_DEPTH/2
    for x,y in [(8.55,3.60),(8.55,4.40),(8.55,5.55),(ex,ny+.22),(wx,ny+.22)]:
        axis='Y' if abs(x-8.55)<.2 else 'X'
        tube('CW split clamp',(x,y,3.15),.111,.089,.065,'steel',axis)
        k.box('CW clamp clevis',(x,y,3.285),(.06,.055,.065),'steel',.002)
    for x,y in [(8.55,3.15),(8.55,5.95),(wx,ny+.22),(ex,ny+.22)]:
        k.box('CW beam roof spacer',(x,y,5.915),(.12,.12,.17),'struct',.003)
        k.box('CW beam ceiling plate',(x,y,5.984),(.28,.26,.032),'steel',.002)
    # Hoist rods receive structural sockets visible in the retained C06 view.
    for x in [5.3,8.9]:
        k.box('hoist upper anchor',(x,3.55,5.974),(.28,.25,.052),'steel',.002)
        k.box('hoist clevis',(x,3.55,5.68),(.09,.07,.12),'steel',.002)
        for dx in [-.095,.095]: k.bolt('hoist roof fastener',(x+dx,3.55,5.945),'Z',.012)


def instrument_faces():
    # Legacy gauge paper sat 2mm behind the solid can front. Bring the instrument
    # stack outside the can rather than changing material to disguise occlusion.
    for can in list(k.S.objects):
        if not can.name.endswith(' can'): continue
        prefix=can.name[:-4]
        axis=Vector((0,1,0)) if abs(can.rotation_euler.x)>1 else Vector((1,0,0)) if abs(can.rotation_euler.y)>1 else Vector((0,0,1))
        for o in list(k.S.objects):
            if o.name.startswith(prefix+' ') and o!=can:
                o.location+=axis*.035


def exhaust_fasteners():
    k.group('10 Condenser CD-01')
    # R28 CPU pixels exposed a black band from this legacy frame's faces exactly
    # overlapping the steam-chest walls. Its full volume is already inside them.
    remove_prefix('CD neck lower')
    remove_prefix('bellow')
    vertices=[]
    for i in range(9):
        z=5.36+i*.39/8
        delta=.12 if i%2 else .02
        vertices.extend([(3-1.25-delta,4.05-.75-delta,z),(3+1.25+delta,4.05-.75-delta,z),
                         (3+1.25+delta,4.05+.75+delta,z),(3-1.25-delta,4.05+.75+delta,z)])
    faces=[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j) for i in range(8) for j in range(4)]
    bellows=k.mesh('bellow continuous folded perimeter',vertices,faces,'bellows',0,False)
    solid=bellows.modifiers.new('Thin formed stainless wall','SOLIDIFY'); solid.thickness=.008; solid.offset=1
    # Exposed bolted joint below the opening headers. The R21 fasteners were buried
    # inside those headers, so adding more at the same elevation could not prove it.
    remove_prefix('CD neck upper','CD mating','CD gasket strip','CD flange plate','mate bolt')
    def frame(name,z,h,lip,mat):
        for side in [-1,1]:
            k.box(name+' Y',(3,4.05+side*(.75+lip/2),z),(2.5+2*lip,lip,h),mat,.003)
            k.box(name+' X',(3+side*(1.25+lip/2),4.05,z),(lip,1.5,h),mat,.003)
    frame('U04 lower bolting plate',5.755,.050,.40,'steel')
    frame('U04 visible gasket',5.79,.020,.39,'rubber')
    frame('U04 upper bolting plate',5.825,.050,.40,'steel')
    frame('U04 slab transition collar',5.925,.15,.085,'cream')
    for side in [-1,1]:
        for i in range(12):
            x=1.69+i*2.62/11; y=4.05+side*1.02
            k.cyl('U04 underside washer',(x,y,5.726),.029,.009,'steel','Z',24,.001)
            k.cyl('U04 underside nut',(x,y,5.708),.022,.030,'steel','Z',6,.001)
        for i in range(7):
            x=3+side*1.52; y=3.37+i*1.36/6
            k.cyl('U04 side underside washer',(x,y,5.726),.029,.009,'steel','Z',24,.001)
            k.cyl('U04 side underside nut',(x,y,5.708),.022,.030,'steel','Z',6,.001)


def lighting():
    s=k.S
    s.view_settings.exposure=-.10
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.20
    for o in s.objects:
        if o.type!='LIGHT': continue
        o.data.use_shadow=True
        if o.name in ['neck wash','chest well','gallery task','U04 pit lamp']:
            o.data.energy*=.35
        elif o.name.startswith('batten'):
            o.data.energy=175
            o.data.color=(1,.94,.83)
        else: o.data.energy*=.75
    # Every added task source is attached to a modeled wall-mounted fixture.
    k.group('05 Lighting')
    for x,y,z,aim in [(-1.60,3.0,3.25,(2.5,4,2)),(-1.60,7.2,3.25,(2.4,7.2,1.1)),
                         (9.4,5.5,4.30,(7.8,4.5,3.1))]:
        side=1 if x<0 else -1
        k.box('Astra task bracket',(x-side*.045,y,z),(.18,.12,.26),'struct',.005)
        body=k.box('Astra task housing',(x+side*.14,y,z),(.20,.48,.15),'struct',.006)
        k.box('Astra task diffuser',(x+side*.14,y,z-.078),(.16,.40,.014),'lamp',.002)
        k.light('Astra practical task',(x+side*.16,y,z-.095),aim,110,(1,.92,.78),.40,'RECTANGLE',.16)
    k.box('CW inspection uplight diffuser',(9.26,5.5,4.379),(.16,.40,.014),'lamp',.002)
    k.light('CW support inspection uplight',(9.25,5.5,4.395),(8.55,4.5,5.72),65,(1,.94,.83),.4,'RECTANGLE',.16)
    for x,y,z,target in [(6.30,4.10,5.65,(3.9,4.05,5.8)),(3.2,6.25,5.60,(3.2,8.0,5.5))]:
        k.box('gallery inspection fixture',(x,y,z),(.12,.30,.09),'struct',.004)
        k.box('gallery inspection lens',(x,y,z+.05),(.10,.24,.014),'lamp',.002)
        k.light('gallery inspection light',(x,y,z+.065),target,55,(1,.94,.85),.24,'RECTANGLE',.1)


def secondary_construction():
    # Annular fan housing exposes existing pitched blades. The old drum was solid.
    k.group('04 Ceiling services')
    remove_prefix('extract drum','extract bell')
    tube('extract open drum',(3,9.12,5.15),.52,.46,.42,'struct','Y')
    tube('extract inlet rim',(3,8.895,5.15),.55,.46,.065,'steel','Y')
    for o in k.S.objects:
        if o.name.startswith(('extract guard','extract spoke')): o.location.y-=.43
    # Match baluster tops to the existing rail slope; keep both stairs and landings.
    k.group('03 Stairs and gallery')
    for prefix,start,end,axis in [('stair1 baluster',(2.15,1.05),(5.05,3.12),'X'),
                                  ('stair2 baluster',(1.12,3.12),(3.95,5.28),'Y')]:
        for o in list(k.S.objects):
            if not o.name.startswith(prefix): continue
            x,y,z=o.location
            foot=z-o.dimensions.z/2
            u=x if axis=='X' else y
            top=start[1]+(end[1]-start[1])*(u-start[0])/(end[0]-start[0])
            name=o.name
            bpy.data.objects.remove(o,do_unlink=True)
            k.rod(name,(x,y,foot),(x,y,top),.012,'yellow')
    # Quiet the floor while retaining the original extraction reservation edges.
    remove_prefix('pull bay hatch','pull bay legend','no storage stencil')
    # Functional service panel details at existing reach height.
    k.group('14 Operator station')
    remove_prefix('OP subtitle')
    for yy in [3.26,4.84]:
        for zz in [.85,1.60,2.24]: k.bolt('OP captive fastener',(-1.337,yy,zz),'X',.009)
    k.box('OP process strip',(-1.327,4.05,1.66),(.018,1.45,.24),'dark',.003)
    k.text('OP process legend','EXHAUST  >  HOTWELL  >  CEP',(-1.310,4.05,1.65),.046,'white','E')
    for i,yy in enumerate([4.53,4.21,3.89,3.57]):
        k.text('OP selector caption',['VACUUM','CEP SELECT','CW ISOLATE','LOCAL'][i],(-1.31,yy,1.23),.035,'white','E')
    k.S.objects['CD nameplate text2'].data.body='HOTWELL / TUBE BUNDLE'
    # A legible actual maintenance record, kept at the original clipboard location.
    k.S.objects['log title'].data.size=.045
    k.S.objects['log title'].location.z=1.68
    for i,line in enumerate(['CD-01  /  NIGHT SHIFT','LEVEL GLASS CLEANED','CEP-A  LOCAL CHECK','CW VALVES  CHECKED']):
        k.text('log record',line,(1.15,9.315,1.59-i*.055),.018,'ink','S')
    # Folded wiping cloth at the operator's instrument work surface.
    verts=[]
    for iy in range(9):
        for ix in range(9):
            u=ix/8;v=iy/8
            verts.append((-1.20+.24*u,3.95+.15*v,.972+.010*abs(math.sin(u*math.pi*3))*math.sin(v*math.pi)))
    faces=[(j*9+i,j*9+i+1,(j+1)*9+i+1,(j+1)*9+i) for j in range(8) for i in range(8)]
    rag=k.mesh('OP folded wiping cloth',verts,faces,'cloth',0,True)
    rag.modifiers.new('Cotton thickness','SOLIDIFY').thickness=.003
    remove_prefix('OP mug')
    tube('OP mug',(-.95,3.77,1.01375),.035,.027,.0875,'burgundy')
    k.cyl('OP mug base',(-.95,3.77,.975),.028,.01,'burgundy','Z',32,.001)
    k.torus('OP mug rim',(-.95,3.77,1.0575),.031,.004,'burgundy')
    k.torus('OP mug handle',(-.91,3.77,1.02),.028,.008,'burgundy','Y')
    k.M['coffee']=k.material('Warm coffee surface','35291D',.22)
    k.cyl('OP coffee',(-.95,3.77,1.043),.026,.002,'coffee','Z',32,0)


def clearances():
    k.group('01 Architecture')
    k.S.objects['west route edge L'].location.x=-.38
    k.S.objects['west route edge R'].location.x=.48
    for name,delta in [('U04 reveal X-',(-.061,0,0)),('U04 reveal X+',(.061,0,0)),
                       ('U04 reveal Y-',(0,-.061,0)),('U04 reveal Y+',(0,.061,0))]:
        k.S.objects[name].location+=Vector(delta)
    for o in k.S.objects:
        if o.name.startswith('ext '): o.location+=Vector((-2.57,.30,0))
    remove_prefix('ext bracket')
    k.box('ext wall bracket',(-1.765,.65,.60),(.07,.16,.48),'steel',.003)
    # Flush removable plates cover the recessed suction routes, leaving the apron clear.
    # These are local construction recesses only, no turbine or neighbor edits.
    for name,x,y in [('CEP-A',P1[0],P1[1]),('CEP-B',P2[0],P2[1])]:
        cx=x-.38; hx=3+(.4 if name=='CEP-A' else -.4); sy=5.53
        for label,centre,dims in [('long', (hx,(sy+y)/2,-.16),(.25,y-sy+.25,.36)),
                                 ('cross',((cx+hx)/2,y,-.16),(abs(cx-hx)+.25,.25,.36))]:
            for target in ['Structural floor','Floor coating field']:
                cutter=k.box(name+' trench cutter',centre,dims,None,0)
                k.boolean_cut(k.S.objects[target],cutter,'local recessed suction')
            cover=k.box(name+' flush service cover '+label,(centre[0],centre[1],.009),(dims[0],dims[1],.016),'struct',.002)
            # Vertical process pipes pass through actual holes in the end covers.
            for px,py in [(cx,y),(hx,sy)]:
                cutter=k.cyl(name+' cover hole cutter',(px,py,.01),.085,.10,None,'Z',32,0)
                k.boolean_cut(cover,cutter,'pipe passage')
    # Replace the shader-debug boundary label with an authored local blanking panel.
    # Its unbound state stays explicit in interface.json and the integration documents.
    remove_prefix('D01 stub ID','D01 stub dado')
    k.box('D01 local blanking frame',(0,-2.32,1.25),(2.36,.08,2.42),'struct',.006)
    k.box('D01 local blanking panel',(0,-2.265,1.25),(2.20,.035,2.24),'dado',.005)
    for xx in [-1.04,1.04]:
        for zz in [.20,.90,1.60,2.30]: k.bolt('D01 blanking fastener',(xx,-2.235,zz),'Y',.014)
    k.text('D01 blanking ID','SERVICE CONNECTION', (0,-2.23,1.78),.085,'white','N')
    k.text('D01 blanking note','ISOLATED / LOCAL LIMIT', (0,-2.23,1.61),.047,'yellow','N')
    for x,y in [(P1[0]+.78,P1[1]+.40),(-.88,P1[1]+.40),(P2[0]+.78,P2[1]+.40),(-.88,P2[1]+.40)]:
        for target in ['Structural floor','Floor coating field']:
            cutter=k.cyl('cable sleeve cutter',(x,y,-.1),.026,.6,None,'Z',24,0)
            k.boolean_cut(k.S.objects[target],cutter,'actual cable passage')
        tube('Cable floor sleeve',(x,y,.012),.037,.025,.026,'steel')


def gallery_repairs():
    """Retain U gallery footprint; fix blocked walking line and stair overlap.

    Saved R23 gave only 1.795 m slab clearance and centerline hangers. The south
    extension also overlapped flight 2. This named subsystem warrants repair.
    """
    k.group('03 Stairs and gallery')
    gz=3.90
    # The original local slab column passed directly through flight 2 (5.55,2.15).
    # Move this one support to the outside of the stair, preserving its floor/slab load path.
    for o in k.S.objects:
        if o.name.startswith(('steel column','column base shoe','column cap plate','SUPPORT_column')):
            if abs(o.location.x-5.55)<.02 and abs(o.location.y-2.15)<.02:
                o.location.x=6.65;o.location.y=1.25
                if o.name.startswith('steel column'):o.location.z=2.755;o.dimensions.z=5.43
                if o.name.startswith('column cap plate'):o.location.z=5.48
    for o in list(k.S.objects):
        if o.name.startswith('steel column') and abs(o.location.x-6.65)>.02:
            k.box('column slab bearing shim',(o.location.x,o.location.y,5.985),(.22,.26,.03),'steel',.002)
    factor=(gz-2.07)/(GAL_Z-2.07)
    change=Matrix.Translation((0,0,2.07))@Matrix.Diagonal((1,1,factor,1))@Matrix.Translation((0,0,-2.07))
    bpy.context.view_layer.update()
    for o in list(k.S.objects):
        if o.name.startswith('stair2'): o.matrix_world=Matrix.Translation((.275,0,0))@change@o.matrix_world
    remove_prefix('mid landing','stair2 rail','stair2 midrail','stair2 baluster')
    k.box('mid landing',((5.05+6.36)/2,.65,2.07),(6.36-5.05,.95,.06),'steel',.004)
    k.box('mid landing plate',((5.05+6.36)/2,.65,2.11),(6.36-5.05,.88,.02),'dark',.003)
    for x in [5.46,6.34]:
        k.rod('stair2 rail',(x,1.12,3.12),(x,3.95,gz+1.1),.018,'yellow')
        k.rod('stair2 midrail',(x,1.12,2.62),(x,3.95,gz+.55),.014,'yellow')
        for i in range(12):
            y=1.12+(i+.5)*2.83/12;foot=2.07+(i+1)*(gz-2.07)/12
            top=3.12+(gz+1.1-3.12)*(y-1.12)/2.83
            k.rod('stair2 baluster',(x,y,foot),(x,y,top),.012,'yellow')
    for a,b in [((5.05,1.10),(5.46,1.12)),((5.05,.20),(6.34,.20)),((6.34,.20),(6.34,1.12))]:
        for z,r in [(3.12,.018),(2.62,.014)]:k.rod('mid landing connected rail',(*a,z),(*b,z),r,'yellow')
    for x,y in [(6.34,.20),(6.34,1.12),(5.46,1.12)]:k.rod('mid landing edge post',(x,y,2.10),(x,y,3.12),.014,'yellow')
    remove_prefix('gallery east','gallery west','gallery north','gallery hanger','gal rail','gal mid','gal post','kick plate E')
    for item in list(k.SUPPORT):
        if item['anchor'].startswith('ANCHOR gallery hang'):
            k.SUPPORT.remove(item)
    # Remove the original anchor empties by semantic label regardless of suffix.
    for o in list(k.S.objects):
        if o.type=='EMPTY' and 'gallery hang' in o.name:
            k.SUPPORT[:]=[a for a in k.SUPPORT if a['anchor']!=o.name]
            bpy.data.objects.remove(o,do_unlink=True)
    def grate(label,x0,x1,y0,y1):
        for x in [x0,x1]: k.box(label+' edge',(x,(y0+y1)/2,gz),(.04,y1-y0+.04,.08),'steel',.002)
        for y in [y0,y1]: k.box(label+' end',((x0+x1)/2,y,gz),(x1-x0,.04,.08),'steel',.002)
        n=math.ceil((y1-y0)/.07)
        for i in range(n+1):
            y=y0+(y1-y0)*i/n
            k.box(label+' bearing bar',((x0+x1)/2,y,gz+.015),(x1-x0,.021,.05),'struct',.001)
        for x in [x0+.2,x1-.2]: k.box(label+' cross tie',(x,(y0+y1)/2,gz+.035),(.016,y1-y0,.016),'steel',.001)
    grate('gallery east',5.45,6.35,3.95,6.295)
    grate('gallery west',-.30,.60,1.805,6.295)
    grate('gallery north',.60,5.45,5.395,6.295)
    segments=[((6.35,3.95),(6.35,6.295)),((6.35,6.295),(-.30,6.295)),
              ((-.30,6.295),(-.30,1.805)),((-.30,1.805),(.60,1.805)),
              ((.60,1.805),(.60,5.395)),((.60,5.395),(5.45,5.395)),((5.45,5.395),(5.45,4.10))]
    for a,b in segments:
        for h,r in [(1.10,.018),(.55,.014)]: k.rod('gallery continuous rail',(*a,gz+h),(*b,gz+h),r,'yellow')
        length=(Vector(b)-Vector(a)).length
        count=max(1,math.ceil(length/1.1))
        for i in range(count+1):
            x=a[0]+(b[0]-a[0])*i/count; y=a[1]+(b[1]-a[1])*i/count
            k.rod('gallery edge post',(x,y,gz+.015),(x,y,gz+1.10),.016,'yellow')
            k.box('gallery post foot',(x,y,gz+.045),(.075,.075,.035),'steel',.002)
    for x0,x1 in [(5.46,5.45),(6.34,6.35)]:
        for h,r in [(1.1,.018),(.55,.014)]:
            k.rod('stair gallery rail transition',(x0,3.95,gz+h),(x1,4.10,gz+h),r,'yellow')
    for x,y in [(6.35,4.1),(6.35,6.25),(-.3,2.1),(-.3,5.9),(3.2,6.295)]:
        k.box('gallery edge suspension',(x,y,(gz+6)/2),(.05,.05,6-gz),'struct',.002)
        k.box('gallery roof shoe',(x,y,5.98),(.22,.22,.04),'steel',.003)
        k.box('gallery lower shoe',(x,y,gz),(.16,.16,.08),'steel',.003)
        k.anchor('Astra gallery '+str((x,y)),(x,y,5.998),'Ceiling slab',(0,0,1),.006,.006)
    # Keep the lifting beam over the extraction apron, clear of stair/gallery headroom.
    remove_prefix('hoist beam','hoist hang L','hoist upper anchor','hoist clevis','hoist roof fastener')
    for z,h,w in [(5.52,.20,.028),(5.622,.036,.16),(5.418,.036,.16)]:
        k.box('hoist beam repaired',((6.48+9.20)/2,3.55,z),(9.20-6.48,w,h),'yellow',.003)
    for x in [6.65,8.9]:
        k.rod('hoist connected hanger',(x,3.55,5.64),(x,3.55,5.998),.014,'steel')
        k.box('hoist ceiling socket',(x,3.55,5.974),(.24,.24,.05),'steel',.003)
    # Move the retained original left support marker with the repaired assembly.
    for o in k.S.objects:
        if o.type=='EMPTY' and 'hoist' in o.name and abs(o.location.x-5.3)<.1: o.location.x=6.65
    for o in k.S.objects:
        if o.name.startswith(('hoist trolley','hoist gearbox','hoist hook')): o.location.x+=.65
    # Stow cover davits inward over their own waterboxes, not across the walk path.
    for side in ['east','west']:
        p=k.S.objects['WB '+side+' davit post'].location.copy()
        around=Matrix.Translation(p)@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-p)
        for o in k.S.objects:
            if o.name.startswith(('WB '+side+' davit arm','WB '+side+' davit eye')):o.matrix_world=around@o.matrix_world
    # The original ejector pipe crossed the west gallery at torso height.
    remove_prefix('EJ air suction')
    k.pipe('EJ air suction',[(1.8,4.45,4.76),(1.3,4.45,4.76),(1.3,2.5,4.76),
                             (1.3,2.5,3.65),(-.77,2.5,3.65),(-.77,7.2,3.65),(-.77,7.2,1.90)],.045,'cream',.08)
    for y in [2.5,5.0,6.8]:
        k.rod('EJ pipe support',(-.77,y,3.65),(-.77,y,5.998),.009,'steel')
        k.box('EJ ceiling pipe clip',(-.77,y,5.98),(.16,.16,.04),'steel',.002)
    # Eye heights now correspond to standing on the repaired deck. W04/W06
    # retain their positions/lenses, correcting only demonstrably invalid aims.
    fixes={'C04_EXHAUST':((5.82,4.35,5.45),(3.,4.05,5.82)),
           'C08_MAINT':((5.90,4.20,5.45),(5.20,6.0,4.15)),
           'C09_ROOF':((5.80,6.00,5.45),(3.,4.05,5.85)),
           'W08_GALLERY_TURN':((5.85,5.40,5.45),(5.85,4.00,4.90)),
           'W04_NE':((8.55,7.15,1.62),(6.85,4.10,1.90)),
           'W06_WEST_AISLE':((.12,6.85,1.55),(.10,2.0,1.4))}
    for name,(p,t) in fixes.items():
        o=k.S.objects[name];o.location=p;o.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler()
    k.S['astra_gallery_deck_z']=gz


def apply_polish():
    from astra_primitives import install
    install()
    materials()
    sight_glasses()
    return_connections()
    instrument_faces()
    cooling_supports()
    exhaust_fasteners()
    secondary_construction()
    clearances()
    gallery_repairs()
    lighting()
