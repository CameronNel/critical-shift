"""Root-authored repairs from the first independent complete-room review.

Called inside the measured construction recipe, before native write. No map
mutation. Geometry copies retain all inherited names and world matrices.
"""
from math import exp, sqrt
from mathutils.bvhtree import BVHTree

def world_edit(o,fn,reason):
    inv=o.matrix_world.inverted()
    for v in o.data.vertices:v.co=inv@Vector(fn(o.matrix_world@v.co))
    o.data.update();uv(o);EXCEPTIONS[o.name]=reason

def shell(name,loc,dims,axis,key,front_sign=-1,taper=.8,cut=.018,opening=.82):
    # A closed manufactured shell with a real front aperture and interior wall.
    other=[k for k in range(3) if k!=axis];ww,hh=[dims[k] for k in other];dep=dims[axis]
    vs=[]
    rings=[(-dep/2,1),(-dep*.32,1),(dep/2,taper),(dep/2-.006,max(.1,taper-.04)),(-dep/2,opening)]
    for d,scale in rings:
        for q in octagon(ww*scale,hh*scale,min(cut,ww*.10,hh*.10)*scale):
            v=list(loc);v[axis]+=d*front_sign*-1;v[other[0]]+=q[0];v[other[1]]+=q[1];vs.append(v)
    fs=[]
    for a,b in [(0,1),(1,2),(3,4),(4,0)]:
        fs.extend((a*8+i,a*8+(i+1)%8,b*8+(i+1)%8,b*8+i) for i in range(8))
    # The rear is a solid closed web; the interior rear ring caps the cavity.
    fs.extend([tuple(range(16,24)),tuple(range(31,23,-1))])
    o=mesh(name,vs,fs,key,.0008)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    return o

def ring(name,loc,w,h,innerw,innerh,depth,axis,key,cut=0):
    other=[k for k in range(3) if k!=axis];vs=[]
    for dd,width,height in [(-depth/2,w,h),(depth/2,w,h),(-depth/2,innerw,innerh),(depth/2,innerw,innerh)]:
        for q in octagon(width,height,cut) if cut else [(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]:
            v=list(loc);v[axis]+=dd;v[other[0]]+=q[0];v[other[1]]+=q[1];vs.append(v)
    fs=[]
    n=8 if cut else 4
    for a,b in [(0,1),(1,3),(3,2),(2,0)]:fs.extend((a*n+i,a*n+(i+1)%n,b*n+(i+1)%n,b*n+i) for i in range(n))
    o=mesh(name,vs,fs,key,0);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o

def repair_screens():
    use_root('Staff Desk Assembly')
    replace('Terminal monitor housing',shell('TEMP hollow CRT',(-3.35,6.8,1.05),(.34,.42,.32),0,'plastic',opening=.84,taper=.66,cut=.024),'Actual CRT aperture and hollow drafted shell, no coincident screen/front cap')
    replace('Terminal CRT screen bezel',ring('TEMP real CRT bezel',(-3.5,6.8,1.05),.36,.26,.332,.232,.02,0,'charcoal'),'Real rectangular bezel aperture exposes retained native screen')
    for o in list(S.objects):
        if o.name.startswith('CD | CRT top ventilation slot'):bpy.data.objects.remove(o,do_unlink=True)
    # Vent slots follow the actual drafted plane rather than hovering over it.
    def top(x):return 1.21 if x<=-3.4588 else 1.21-(x+3.4588)*(.0544/.2788)
    for y in [6.69,6.715,6.74,6.765,6.79,6.815,6.84,6.865,6.89,6.915]:
        vs=[(x,yy,top(x)+d) for d in [0,.0006] for yy in [y-.0035,y+.0035] for x in [-3.33,-3.225]]
        mesh('CD | CRT drafted-plane vent recess',vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'ink',0)
    use_root('Cargo Inspection Conveyor')
    for i in [0,1]:
        y=7.35+i*.6
        replace('Conveyor monitor housing '+str(i),shell('TEMP hollow cargo display',(3.35,y,1.3),(.28,.38,.30),0,'plastic',front_sign=1,taper=.75,opening=.82),'Actual east-facing display aperture and correctly drafted rear; no buried screen')

def repair_structure():
    global ASM
    ASM=None
    # Frame pockets remove duplicate painted/structural faces. Their combined
    # wall boundary and 4.60 x 3.50m usable P2 opening remain identical.
    for side in [-1,1]:
        name='North wall '+('west' if side<0 else 'east')
        pts=[(-6.8,0),(-2.46,0),(-2.46,3.7),(-2.3,3.7),(-2.3,4.4),(-6.8,4.4)]
        if side>0:pts=[(-x,z) for x,z in pts][::-1]
        replace(name,profile('TEMP arrival frame pocket',pts,.28,1,(0,15.94,0),'plaster',.001),'True arrival frame pocket; combined outer wall/frame union and usable opening preserved')
        w=S.objects['North wall wainscot '+('west' if side<0 else 'east')]
        world_edit(w,lambda q:(min(q.x,-2.46) if side<0 else max(q.x,2.46),q.y,q.z),'Protective lining butts into the arrival jamb, never covers the frame')
    o=S.objects['North lintel P2'];world_edit(o,lambda q:(q.x,q.y,max(q.z,3.7)),'Lintel butts above frame header at Z3.70, removes duplicate exposed front; combined envelope preserved')
    # Rear office reveal pocket follows the already-authored front frame logic.
    for name,pts in [('Office rear wall east',[(-4.775,0),(-2.4,0),(-2.4,3.05),(-4.875,3.05),(-4.875,2.3),(-4.775,2.3)]),('Office rear wall west',[(-6.8,0),(-6.025,0),(-6.025,2.3),(-5.925,2.3),(-5.925,3.05),(-6.8,3.05)])]:
        replace(name,profile('TEMP rear frame pocket',pts,.16,1,(0,9.6,0),'plaster',.001),'Actual stepped rear door pocket butts at outer jamb; usable aperture and outer wall datum preserved')
    world_edit(S.objects['Office rear lintel'],lambda q:(max(-5.925,min(q.x,-4.875)),q.y,max(q.z,2.3)),'Rear head infill butts between stepped wall pockets above actual D2 frame; removes exposed overlapping wings')
    # Physically recess both flush floor inserts; the walk surface stays Z0.
    floor=S.objects['Floor slab'];bpy.context.view_layer.objects.active=floor
    for mod in list(floor.modifiers):
        if mod.type=='BEVEL':bpy.ops.object.modifier_apply(modifier=mod.name)
        elif mod.type=='WEIGHTED_NORMAL':floor.modifiers.remove(mod)
    for name,loc,dims in [('trench',(2.2,14.4,-.005),(8.8,.22,.03)),('P1',(0,-.10,-.045),(2.5,.20,.11))]:
        cutter=box('TEMP real floor insert pocket',loc,dims,'concrete',0)
        mod=floor.modifiers.new('Actual '+name+' floor recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.context.view_layer.objects.active=floor;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    EXCEPTIONS[floor.name]='Real 20mm trench and 100mm P1 insert seats; removes exposed flush duplicates, combined walking surface/bounds unchanged'

def repair_internal_bearing():
    use_root('Arrival Gate P2')
    for x in [-1.5,1.5]:box('CD | Arrival beacon wall bracket',(x,15.785,3.90),(.14,.030,.065),'charcoal',.001)
    use_root('G1 Cart Bypass Gate')
    cyl('CD | G1 beacon captive seat',(3.02,7,2.505),.05,.010,'charcoal',vertices=12,w=0)
    # Actuator and guide pieces are deliberately readable, inside old envelope.
    for y in [6.78,7.22]:
        box('CD | G1 telescopic guide shoe',(3.02,y,1.0),(.20,.045,.14),'steel',.001)
        for z in [.955,1.045]:cyl('CD | G1 guide keeper',(3.02,y-.026,z),.005,.008,'steel','Y',vertices=6,w=0)
    use_root('Cargo Inspection Conveyor')
    for o in list(S.objects):
        if o.name.startswith('Conveyor roller '):
            x,y,z=o.matrix_world.translation
            for xx in [4.015,5.285]:cyl('CD | Roller bearing engaged journal',(xx,y,z),.014,.012,'steel','X',vertices=8,w=0)
    for x,y in [(4.05,6.65),(4.05,8.65),(5.25,6.65),(5.25,8.65)]:
        o=S.objects[f'Lifting eyebolt stem {x}_{y}']
        world_edit(o,lambda q:(q.x,q.y,max(2.15,min(q.z,2.163))),'Stem seat terminates at the actual vertical forged-eye underside, <=2mm engagement; roof-side seat starts at actual roof skin')
        # A real flange joins the stem to the shield roof, not an air gap.
        cyl('CD | Cargo forged-eye roof flange',(x,y,2.154),.027,.008,'steel',vertices=12,w=.0005)
    for y in [9.04,9.36]:
        profile('CD | Cargo motor welded saddle',[(5.345,.625),(5.361,.625),(5.361,.505),(5.775,.505),(5.775,.493),(5.345,.493)],.052,1,(0,y,0),'steel',.0005)
    replace('Drive motor housing',profile('TEMP cast motor body',octagon(.22,.235,.022),.34,1,(5.68,9.2,.6525),'charcoal',.001),'Cast motor underside bears at actual motor-plate top Z.535 instead of penetrating 25mm; retained native pose')
    for j in range(7):
        replace('Motor cooling fin '+str(j),profile('TEMP cast cooling fin',octagon(.27,.25,.018),.010,1,(5.68,9.08+.04*j,.66),'steel',.0005),'Cast cooling fin underside meets mounting plate at Z.535; same motor envelope and native pose')
    for y in [7.35,7.95]:
        profile('CD | Cargo operator cantilever',[(3.625,.90),(3.635,.90),(3.90,1.13),(3.90,1.17),(3.885,1.17),(3.635,.94),(3.625,.94)],.052,1,(0,y,0),'steel',.0005)
    for k,y in enumerate([8.3,9.1]):
        use_root('CD | Office file cabinet '+str(k))
        for j in range(4):
            z=.22+.30*j
            for yy in [y-.1,y+.1]:cyl('CD | Drawer pull captive stud',(-6.005,yy,z),.005,.010,'steel','X',vertices=8,w=0)
            o=S.objects[f'Drawer cardholder {k}_{j}'];world_edit(o,lambda q:(min(q.x,-6.01) if q.x<-6.0 else q.x,q.y,q.z),'Cardholder rear extends into actual drawer surface, front and native pose retained')
    use_root('Evidence Cabinet H2')
    for x in [-6.1,-5.575,-5.05]:
        for z in [.48,1.18]:cyl('CD | Vault escutcheon bearing neck',(x+.14,14.7625,z),.015,.009,'steel','Y',vertices=12,w=0)
    use_root('Switchgear Console Unit')
    for x in [4.45,5.45]:cyl('CD | Switchgear lock fitted collar',(x+.32,14.6685,1.02),.016,.023,'steel','Y',vertices=12,w=.0005)

def repair_utilities():
    use_root('Wall Utilities Rack')
    for o in list(S.objects):
        if o.name.startswith('CD | Disconnect cover captive screw'):bpy.data.objects.remove(o,do_unlink=True)
    for index,n in enumerate(['Transformer box 1','Transformer box 2','Main breaker disconnect']):
        o=S.objects[n];x,y,z=o.matrix_world.translation;d,w,h=BASE[n]['dimensions'];front=x-d/2
        replace(n,shell('TEMP utility folded enclosure',(x,y,z),(d,w,h),0,'blue',opening=.81,taper=.91),'Open-front folded enclosure and separately hinged cover, same native outer envelope')
        for yy in [y-w*.34,y+w*.34]:
            for zz in [z-h*.35,z+h*.35]:cyl('CD | Utility backboard captive stand-off',(6.77,yy,zz),.010,.020,'steel','X',vertices=8,w=0)
        profile('CD | Utility fitted door',octagon(w*.86,h*.85,.018),.006,0,(front-.003,y,z),'blue',.0005)
        for yy in [y-w*.34,y+w*.34]:
            for zz in [z-h*.35,z+h*.35]:cyl('CD | Utility captive lid screw',(front-.008,yy,zz),.005,.004,'steel','X',vertices=6,w=0)
        for zz in [z-h*.25,z+h*.25]:
            box('CD | Utility hinge leaf',(front-.003,y+w*.425,zz),(.006,.04,.055),'steel',.0005)
            cyl('CD | Utility hinge pin',(front-.004,y+w*.405,zz),.006,.07,'steel',vertices=8,w=0)
        # Pipe enters a real threaded top gland; fasteners stay purpose-led.
        cyl('CD | Utility conduit top gland',(x-.01,y,z+h/2+.010),.035,.024,'charcoal',vertices=6,w=.0005)
        label='TX / 02' if index<2 else 'ISOLATE'
        profile('CD | Utility rating enamel',octagon(w*.50,.060,.006),.001,0,(front-.0065,y,z-h*.22),'ivory',0)
        txt('CD | Utility stamped rating',label,(front-.0071,y+w*.20,z-h*.24),.023,'ink',rot=(pi/2,0,-pi/2))

def tarp_height(x,y):
    u=(x+5.85)/.415;v=(y-13.25)/1.095;a=abs(u)
    knots=[(0,1.04),(.38,1.026),(.67,.95),(.86,.86),(.915,.812),(1,.555)]
    for (a0,z0),(a1,z1) in zip(knots,knots[1:]):
        if a<=a1:base=z0+(z1-z0)*(a-a0)/(a1-a0);break
    else:base=.555
    load=.045*exp(-((v-.48)/.35)**2)*max(0,1-a**2)
    end=max(0,(abs(v)-.82)/.18)*.18*max(0,1-(a/.915)**2)
    fold=.016*sin(18*u+4*v+.6*sin(5*v))*(.2+.8*a)*(1-abs(v)*.2)*max(0,min(1,(.915-a)/.055))
    return max(.542,base+load-end+fold)

def repair_tarp():
    use_root('Covered Trolley H1')
    nx,ny=24,56;vs=[];fs=[]
    for dz in [0,-.002]:
        for j in range(ny+1):
            y=12.155+2.19*j/ny
            for i in range(nx+1):
                x=-6.265+.83*i/nx;vs.append((x,y,tarp_height(x,y)+dz))
    count=(nx+1)*(ny+1)
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;b=a+1;c=b+nx+1;d=c-1
            fs.extend([(a,b,c,d),(d+count,c+count,b+count,a+count)])
    border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
    fs.extend((a,b,b+count,a+count) for a,b in zip(border,border[1:]+border[:1]))
    tarp=replace('Covered Trolley Draped Tarp',mesh('TEMP continuous cloth',vs,fs,'cotton',0),'Continuous thin gravity-led cover, broad asymmetrical tension folds and closed sewn edge; preserved footprint/hidden load')
    bm=bmesh.new();bm.from_mesh(tarp.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(tarp.data);bm.free()
    for f in tarp.data.polygons:f.use_smooth=True
    tarp['textile_grid']=[nx,ny];tarp['fabric_uv_contract']='Continuous cut coordinates integrated across drape; CD_Physical_1m remains per-face audit chart, not the textile shader'
    bpy.context.view_layer.update()
    verts=[tarp.matrix_world@v.co for v in tarp.data.vertices]
    tree=BVHTree.FromPolygons(verts,[list(f.vertices) for f in tarp.data.polygons],all_triangles=False)
    def cloth_z(x,y):
        hit=tree.ray_cast(Vector((x,y,1.5)),Vector((0,0,-1)),1.1)[0]
        if hit is None:raise RuntimeError('Missing actual cloth bearing surface')
        return hit.z
    for o in list(S.objects):
        if o.name.startswith('CD | Trolley tarp sewn side hem'):bpy.data.objects.remove(o,do_unlink=True)
    for x in [-6.265,-5.435]:
        hem=line('CD | Trolley gravity-led sewn hem',[(x,12.155+2.19*j/28,tarp_height(x,12.155+2.19*j/28)-.0005) for j in range(29)],.0012,'cotton')
        hem.data.bevel_resolution=1
    # Retain four named restraint parts, draped onto the actual cover surface.
    for j,y in enumerate([12.55,13.05,13.55,14.05]):
        vs=[];fs=[]
        for dz in [0,.002]:
            for i in range(1,24):
                x=-6.265+.83*i/24
                for yy in [y-.012,y+.012]:vs.append((x,yy,cloth_z(x,yy)+dz+.0003))
        for i in range(22):
            a=i*2;fs.extend([(a,a+2,a+3,a+1),(a+47,a+49,a+48,a+46),(a,a+46,a+48,a+2),(a+1,a+3,a+49,a+47)])
        fs.extend([(0,1,47,46),(44,90,91,45)])
        q=replace('Trolley strap '+str(j),mesh('TEMP textile restraint',vs,fs,'rubber',0),'Four closed webbing strips conform to actual continuous cover, inherited matrices retained')
        bm=bmesh.new();bm.from_mesh(q.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(q.data);bm.free()
    for o in S.objects:
        if o.name.startswith(('CD | Ratchet buckle folded shell','CD | Ratchet captive pin')):
            o.location.z=cloth_z(o.location.x,o.location.y)+(.006 if 'shell' in o.name else .005)

def material_patch(m,center,radii,color,strength=.5,broken=False):
    n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
    pos=n.new('ShaderNodeNewGeometry');v=n.new('ShaderNodeVectorMath');v.operation='SUBTRACT';v.inputs[1].default_value=center;l.new(pos.outputs['Position'],v.inputs[0])
    sc=n.new('ShaderNodeVectorMath');sc.operation='MULTIPLY';sc.inputs[1].default_value=tuple(1/r for r in radii);l.new(v.outputs[0],sc.inputs[0])
    di=n.new('ShaderNodeVectorMath');di.operation='LENGTH';l.new(sc.outputs[0],di.inputs[0])
    f=n.new('ShaderNodeMapRange');f.interpolation_type='SMOOTHSTEP';f.inputs['From Min'].default_value=.10;f.inputs['From Max'].default_value=1;f.inputs['To Min'].default_value=strength;f.inputs['To Max'].default_value=0;l.new(di.outputs['Value'],f.inputs['Value']);fac=f.outputs[0]
    if broken:
        noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=28;noise.inputs['Detail'].default_value=2;l.new(pos.outputs['Position'],noise.inputs['Vector'])
        cr=n.new('ShaderNodeMapRange');cr.inputs['From Min'].default_value=.37;cr.inputs['From Max'].default_value=.60;l.new(noise.outputs['Fac'],cr.inputs['Value'])
        mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(fac,mul.inputs[0]);l.new(cr.outputs[0],mul.inputs[1]);fac=mul.outputs[0]
    mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(*color,1);l.new(fac,mix.inputs[0]);l.new(bs.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    rr=n.new('ShaderNodeMixRGB');rr.inputs[2].default_value=(.58,.58,.58,1);l.new(fac,rr.inputs[0]);l.new(bs.inputs['Roughness'].links[0].from_socket,rr.inputs[1]);l.new(rr.outputs[0],bs.inputs['Roughness'])

def repair_surfaces_story():
    floor=S.objects['Floor slab'].data.materials[0]
    for p,r in [((0,6.8,0),(.62,1.3,.008)),((1.95,6.9,0),(.72,1.7,.008)),((-3.6,2.9,0),(.8,.55,.008)),((1.8,12.0,0),(.9,1.5,.008))]:
        material_patch(floor,p,r,(.095,.105,.118),.46,True)
        material_patch(MATERIALS['yellow'],p,(r[0]*1.5,r[1]*1.2,.008),(.19,.18,.15),.88,True)
    for p in [(6.50,13.05,1.88),(6.50,12.5,1.89),(-5.05,14.765,1.1),(.73,6.81,.18)]:
        material_patch(MATERIALS['blue'],p,(.16,.18,.22),(.21,.23,.235),.40,True)
    # Woven thread response and cloth sheen, distinct from molded plastic.
    for key in ['fabric','cotton']:
        m=MATERIALS[key];n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Sheen Weight'].default_value=.28
        coords=n.new('ShaderNodeUVMap');coords.uv_map='CD_Fabric_Cut_1m'
        waves=[]
        for direction in ['X','Y']:
            w=n.new('ShaderNodeTexWave');w.bands_direction=direction;w.inputs['Scale'].default_value=180;l.new(coords.outputs[0],w.inputs['Vector']);waves.append(w)
        mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(waves[0].outputs['Fac'],mul.inputs[0]);l.new(waves[1].outputs['Fac'],mul.inputs[1])
        bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0012;bump.inputs['Strength'].default_value=.45;l.new(mul.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    # Consolidate the original reassurance onto the transaction-level glass.
    use_root('Checkin Counter Hatch')
    box('CD | Worker reassurance glass notice',(-3.51,3.591,1.65),(.39,.001,.10),'ivory',0)
    txt('CD | Reassurance headline','A BETTER SHIFT AWAITS',(-3.51,3.5899,1.663),.027,'ink',align='CENTER')
    txt('CD | Reassurance qualification','RELEASE REQUIRES MANAGEMENT CONSENT',(-3.51,3.5898,1.63),.0095,'ink',align='CENTER')
    use_root('Covered Trolley H1')
    txt('CD | Transfer custody match','731 / HOLD',(-5.456,12.225,.56),.025,'ink',rot=(pi/2,0,pi/2))
    # Existing clipped transfer document gets a matched custody seal.
    box('CD | Transfer docket seal',(-5.4565,12.30,.49),(.001,.10,.032),'yellow',0)
    use_root('Staff Desk Assembly')
    box('CD | Shift handover form',(-3.70,7.15,.761),(.27,.19,.002),'paper',0)
    txt('CD | Handover issue','RELIEF: NOT ASSIGNED',(-3.81,7.19,.7621),.016,'ink',rot=(0,0,0))
    txt('CD | Handover incident','731  /  HOLD UNTIL NEXT SHIFT',(-3.81,7.16,.7621),.010,'ink',rot=(0,0,0))
    for j in range(4):box('CD | Handover ink line',(-3.70,7.11-j*.013,.7621),(.20-j*.024,.001,.0002),'ink',0)

def repair_lighting():
    # Two fitted inspection luminaires make the faces legible without washing
    # the whole room. Every visible bracket is genuinely roof supported.
    for name,pos,target,power in [('Inspection face', (.3,4.4,3.25),(0,7,1.45),105),('Custody transfer',(-4.8,11.3,3.15),(-5.46,12.28,.47),32)]:
        q=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y')
        pivots=[Vector(pos)+q@Vector((dx,0,0)) for dx in [-.18,.18]]
        root=asset_root(name+' luminaire','Roof deck ceiling slab',[(v.x,v.y,4.4) for v in pivots],(0,0,1))
        shade=ring('CD | Open inspection luminaire', (0,0,0),.32,.18,.24,.10,.08,2,'charcoal')
        for v in shade.data.vertices:v.co=Vector(pos)+q@v.co
        lens=box('CD | Inspection frosted aperture',(0,0,-.038),(.24,.10,.002),'warm_lamp',0)
        for v in lens.data.vertices:v.co=Vector(pos)+q@(v.co+Vector((0,0,-.038)))
        lens.location=(0,0,0)
        for v in pivots:
            cyl('CD | Luminaire twin roof stem',(v.x,v.y,(4.4+v.z+.007)/2),.007,4.4-v.z-.007,'steel',vertices=8,w=.0003)
            box('CD | Luminaire roof anchor',(v.x,v.y,4.394),(.05,.05,.012),'steel',.0005)
        for dx in [-.174,.174]:
            seat=profile('CD | Lamp pivot bearing',octagon(.025,.025,.004),.028,0,(dx,0,0),'steel',0)
            for v in seat.data.vertices:v.co=Vector(pos)+q@v.co
        # Emitter is just beyond the real aperture; it cannot be buried in a
        # solid shade. Physical fixture is outside the cart headroom corridor.
        emitter=Vector(pos)+q@Vector((0,0,-.042))
        lamp=light('CD | '+name+' practical',emitter,target,power,(.74,.84,1) if name=='Inspection face' else (1,.79,.54),.24,.10)
        reposition_parent(lamp,root)
    # Fluorescent bounce motivates a dim upward service read.
    use_root('CD | Scanner Overhead Key suspended fixture')
    lamp=light('CD | Scanner practical roof bounce',(0,7,3.60),(1,7,4.25),48,(.67,.77,1),3)
    reposition_parent(lamp,ASM)

def repair_gate_construction():
    use_root('G1 Cart Bypass Gate')
    for j in [1,2,3]:
        n=f'G1 leaf {j} frame';o=S.objects[n];x,y,z=o.matrix_world.translation
        frame=replace(n,ring('TEMP open telescopic frame',(x,y,z),.65,1.4,.63,1.36,.05,1,'steel'),'Actual welded perimeter frame exposes recessed leaf panel; original leaf pose and bounds retained')
        panel_o=S.objects[f'G1 leaf {j} panel'];assign(panel_o,'blue')
        for xx in [x-.075,x+.075]:
            carriage_y=S.objects[f'G1 leaf {j} top carriage'].matrix_world.translation.y
            shoe=box('CD | G1 carriage suspension',(xx,(y+carriage_y)/2,(z+.7+1.56)/2),(.025,.027,1.56-z-.7),'steel',.0005)
            reposition_parent(shoe,frame)
        for o in list(S.objects):
            if not o.name.startswith(f'G1 leaf {j} wheel box'):continue
            wx,wy,wz=o.matrix_world.translation
            top=z-.7-wz+.001
            pts=[(-.035,-.04),(-.020,-.04),(-.020,.012),(.020,.012),(.020,-.04),(.035,-.04),(.035,top),(-.035,top)]
            replace(o.name,profile('TEMP real caster fork',pts,.10,0,(wx,wy,wz),'steel',.0003),'U-section caster fork exposes the retained floor wheel and axle, same native caster pose')
            cyl('CD | G1 caster axle',(wx,wy,.035),.004,.074,'steel','Y',vertices=8,w=0)
        # Two functional pressed bays, flush backing and visible captive fixing.
        for zz in [z-.36,z+.26]:
            skin=profile('CD | G1 pressed panel bay',octagon(.49,.46,.035),.005,1,(x,y-.0175,zz),'blue',.0006)
            reposition_parent(skin,panel_o)
            for xx in [x-.21,x+.21]:
                screw=cyl('CD | G1 panel captive screw',(xx,y-.022,zz+.18),.004,.004,'steel','Y',vertices=6,w=0)
                reposition_parent(screw,panel_o)
    use_root('Person Scanner Arch')
    for x in [-.73,.73]:
        cover=profile('CD | Scanner front service door',octagon(.185,1.65,.035),.004,1,(x,6.818,1.34),'blue',.0005)
        for z in [.55,2.13]:
            for xx in [x-.064,x+.064]:cyl('CD | Scanner service captive screw',(xx,6.8135,z),.004,.004,'steel','Y',vertices=6,w=0)
    use_root('Arrival Gate P2')
    for x in [-1.4,1.4]:cyl('CD | P2 sign fitted stand-off',(x,15.73,3.3),.008,.04,'steel','Y',vertices=8,w=0)
    for side in [-1,1]:
        leaf=S.objects['P2 blast leaf '+('west' if side<0 else 'east')]
        for z in [1.0,2.35]:
            p=profile('CD | Arrival leaf pressed cassette',octagon(1.94,1.04,.09),.008,1,(side*1.15,15.746,z),'blue',.001)
            reposition_parent(p,leaf)
            inset=profile('CD | Arrival cassette die face',octagon(1.76,.86,.07),.004,1,(side*1.15,15.740,z),'navy',.0007)
            reposition_parent(inset,leaf)
            for xx in [side*1.15-.84,side*1.15+.84]:
                for zz in [z-.38,z+.38]:
                    pin=cyl('CD | Arrival captive panel screw',(xx,15.736,zz),.006,.004,'steel','Y',vertices=6,w=0);reposition_parent(pin,leaf)

def repair_full_candidate():
    for n in ['Scanner portal column -1','Scanner portal column 1']:
        world_edit(S.objects[n],lambda q:(q.x,q.y,min(q.z,2.65)),'Inspection columns butt into header underside at Z2.65; remove duplicated front skin, same outer arch envelope/clearance')
    repair_screens();repair_structure();repair_internal_bearing();repair_utilities();repair_tarp();repair_surfaces_story();repair_lighting();repair_gate_construction();repair_second_review();repair_third_review();repair_fourth_review();repair_scanner_pockets()
    S['first_full_cycle_repairs']='Actual internal mount contact, real screen apertures/frame pockets, continuous cloth/cut coordinates, purposeful wear/handover, fitted face keys'

def finish_full_repairs():
    reconcile_architectural_labels()
    # Shader UVs survive final bevel/triangulation, independent of the audit
    # chart. Cloth uses one continuous, angle-preserving top island. Closed
    # sewn-thickness edges are deliberate seams, never fragmented face islands.
    for o in S.objects:
        if o.type!='MESH':continue
        if not any(m and any(n.type=='UVMAP' and n.uv_map=='CD_Fabric_Cut_1m' for n in m.node_tree.nodes) for m in o.data.materials):continue
        physical=o.data.uv_layers.get('CD_Physical_1m');cut=o.data.uv_layers.get('CD_Fabric_Cut_1m') or o.data.uv_layers.new(name='CD_Fabric_Cut_1m')
        for i,value in enumerate(physical.data):cut.data[i].uv=value.uv
        if o.name=='Covered Trolley Draped Tarp':
            nx,ny=o['textile_grid'];count=(nx+1)*(ny+1)
            def boundary(v):
                i=v%(nx+1);j=v//(nx+1);return i in [0,nx] or j in [0,ny]
            for e in o.data.edges:
                a,b=e.vertices
                e.use_seam=((a<count)==(b<count) and boundary(a%count) and boundary(b%count)) or set([a,b])==set([0,count])
            for selected in list(bpy.context.selected_objects):selected.select_set(False)
            o.select_set(True);bpy.context.view_layer.objects.active=o;o.data.uv_layers.active=cut
            bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.unwrap(method='ANGLE_BASED',margin=.002);bpy.ops.object.mode_set(mode='OBJECT')
            # Unwrap replaces mesh custom-data storage: re-fetch the RNA layer.
            cut=o.data.uv_layers['CD_Fabric_Cut_1m']
            o.data.calc_loop_triangles();world_area=0;uv_area=0
            for tri in o.data.loop_triangles:
                if not all(v<count for v in tri.vertices):continue
                p=[o.matrix_world@o.data.vertices[v].co for v in tri.vertices];world_area+=(p[1]-p[0]).cross(p[2]-p[0]).length/2
                u=[cut.data[i].uv.copy() for i in tri.loops];uv_area+=abs((u[1].x-u[0].x)*(u[2].y-u[0].y)-(u[1].y-u[0].y)*(u[2].x-u[0].x))/2
            factor=sqrt(world_area/uv_area)
            values=[value.uv.copy()*factor for value in cut.data]
            for i,value in enumerate(values):cut.data[i].uv=value
            o.data.update()
            verified=0
            for tri in o.data.loop_triangles:
                if not all(v<count for v in tri.vertices):continue
                u=[cut.data[i].uv.copy() for i in tri.loops]
                verified+=abs((u[1].x-u[0].x)*(u[2].y-u[0].y)-(u[1].y-u[0].y)*(u[2].x-u[0].x))/2
            if abs(verified/world_area-1)>1e-5:raise RuntimeError('Consumed fabric area normalization failed')
            o['fabric_uv_normalization']=json.dumps({'world_top_area_m2':world_area,'uv_top_area':verified,'factor':factor})
            o.select_set(False);o['fabric_uv_contract']='Continuous ANGLE_BASED top island; globally normalized one-metre surface area; sewn hem/thickness seams; physical face chart retained for metric audit'
        for m in o.data.materials:
            for node in m.node_tree.nodes:
                if node.type=='UVMAP':node.uv_map='CD_Fabric_Cut_1m'

def return_idler(name,loc,length,outer=.033,inner=.0085):
    # Closed annular tube: a running bearing clearance, not intersecting solids.
    n=16;vs=[];fs=[]
    for x,r in [(-length/2,outer),(length/2,outer),(-length/2,inner),(length/2,inner)]:
        for j in range(n):
            t=2*pi*j/n;vs.append((loc[0]+x,loc[1]+r*sin(t),loc[2]+r*cos(t)))
    for a,b in [(0,1),(1,3),(3,2),(2,0)]:
        fs.extend((a*n+j,a*n+(j+1)%n,b*n+(j+1)%n,b*n+j) for j in range(n))
    o=mesh(name,vs,fs,'steel',0)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o['mechanical_interface']='Annular return idler; 0.5mm radial running clearance on supported shaft; top tangent bears against retained belt underside'
    return o

def repair_second_review():
    # Root authored. Construction refinements stay in the frozen layout.
    use_root('Cargo Inspection Conveyor')
    for y in [6.4,8.9]:
        return_idler('CD | Conveyor lower return idler',(4.65,y,.379),1.14)
        cyl('CD | Conveyor return through shaft',(4.65,y,.379),.008,1.26,'steel','X',vertices=12,w=0)
        # Bearing blocks bridge the shaft ends to the two retained legs.
        for x in [4.013,5.287]:
            box('CD | Return bearing welded ear',(x,y,.379),(.016,.074,.072),'charcoal',.0005)
    # Layered folded entrance/exit collars, with an actual hollow throat.
    for y in [6.5,8.8]:
        pts=[(-.75,-.70),(-.61,-.70),(-.61,.53),(.61,.53),(.61,-.70),(.75,-.70),(.75,.70),(-.75,.70)]
        profile('CD | Cargo folded throat collar',pts,.052,1,(4.65,y,1.45),'steel',.001)
        for x in [3.94,5.36]:
            for z in [.86,1.98]:cyl('CD | Throat captive fastener',(x,y+(-.031 if y<7 else .031),z),.008,.008,'steel','Y',vertices=6,w=0)
        # Corner pieces bridge folded side webs to the top return.
        for x in [4.00,5.30]:box('CD | Shield collar corner cleat',(x,y,2.108),(.18,.060,.065),'charcoal',.001)
    # Two practical toggle catches span crate body/lid joint on its visible end.
    for x in [4.43,4.87]:
        box('CD | Transit crate catch mount',(x,5.369,1.315),(.072,.012,.09),'steel',.001)
        profile('CD | Transit crate toggle handle',[(-.026,-.034),(.026,-.034),(.026,.034),(.018,.045),(-.018,.045),(-.026,.034)],.012,1,(x,5.357,1.326),'charcoal',.001)
        box('CD | Transit crate lid keeper',(x,5.355,1.40),(.075,.016,.042),'steel',.001)
        cyl('CD | Crate toggle hinge',(x,5.350,1.345),.007,.068,'steel','X',vertices=8,w=0)
    box('CD | Transit seal ribbon',(4.65,5.358,1.347),(.05,.002,.145),'yellow',0)
    txt('CD | Transit seal ID','731-A',(4.65,5.3568,1.32),.019,'ink',align='CENTER')
    # Inspection identity is dark recessed sensing hardware, unlike the gate.
    use_root('Person Scanner Arch')
    for o in S.objects:
        if o.name.startswith('CD | Scanner front service door'):assign(o,'charcoal')
        elif o.name.startswith('Scanner column inset'):assign(o,'charcoal')
    for x in [-.73,.73]:
        for y in [6.812,7.188]:
            # Folded seam along the service door edge, seated on column skin.
            for xx in [x-.105,x+.105]:box('CD | Scanner folded service edge',(xx,y,1.35),(.012,.016,2.28),'steel',.0005)
            for z in [.56,1.22,1.88]:
                box('CD | Scanner removable module seam',(x,y, z),(.185,.006,.012),'steel',.0003)
        for z in [.42,1.10,1.80,2.45]:
            # Inner sensing banks have an actual seated neutral collar.
            cyl('CD | Scanner inner bank bezel',(.613*(1 if x>0 else -1),7,z),.04,.016,'charcoal','X',vertices=16,w=.0005)
    for j in range(4):
        o=S.objects[f'Scanner status light {j}'];z=o.matrix_world.translation.z
        cyl('CD | Scanner status seated neck',(.78,6.813,z),.024,.006,'charcoal','Y',vertices=16,w=0)
    world_edit(S.objects['Scanner lintel face'],lambda q:(q.x,min(q.y,6.793) if q.y<6.81 else q.y,q.z),'Extend front plate to actual retained raised glyph backs at Y6.793; no inherited inscription pose change')
    # Muted folded gate leaves, with visible edge return and matched reverse.
    use_root('G1 Cart Bypass Gate')
    for o in S.objects:
        if o.name.startswith(('G1 leaf','CD | G1 pressed panel bay')) and o.type=='MESH' and 'frame' not in o.name and 'wheel' not in o.name and 'carriage' not in o.name:
            if any(m==MATERIALS['blue'] for m in o.data.materials):assign(o,'charcoal')
    for j in [1,2,3]:
        leaf=S.objects[f'G1 leaf {j} panel'];x,y,z=leaf.matrix_world.translation
        for xx in [x-.313,x+.313]:
            # Folded returns bear against the retained welded perimeter.
            q=box('CD | G1 leaf folded side return',(xx,y,z),(.017,.045,1.35),'steel',.0005);reposition_parent(q,leaf)
        for zz in [z-.54,z+.50]:
            q=box('CD | G1 reverse rolled rib',(x,y+.018,zz),(.60,.012,.036),'steel',.0006);reposition_parent(q,leaf)
        for xx in [x-.23,x+.23]:
            for zz in [z-.54,z+.50]:
                q=cyl('CD | G1 reverse rivet',(xx,y+.026,zz),.005,.004,'steel','Y',vertices=6,w=0);reposition_parent(q,leaf)
    # Positive end stop and locking receiver bear on the retained drive post.
    box('CD | G1 stop cast bracket',(2.94,6.974,1.30),(.16,.055,.14),'steel',.001)
    box('CD | G1 stop resilient insert',(2.854,6.974,1.30),(.012,.055,.10),'rubber',.0005)
    # Arrival leaves gain heavy edge seals/guide shoes rather than blue graphics.
    use_root('Arrival Gate P2')
    for o in S.objects:
        if o.name.startswith('CD | Arrival leaf pressed cassette'):assign(o,'charcoal')
    for side in [-1,1]:
        leaf=S.objects['P2 blast leaf '+('west' if side<0 else 'east')]
        for x in [side*.012,side*2.25]:
            q=box('CD | P2 folded vertical closure',(x,15.74,1.70),(.048,.024,3.30),'steel',.001);reposition_parent(q,leaf)
        for z in [.20,3.20]:
            q=box('CD | P2 captive guide shoe',(side*2.23,15.745,z),(.11,.034,.18),'charcoal',.001);reposition_parent(q,leaf)
        q=box('CD | P2 centre compression seal',(side*.034,15.725,1.70),(.027,.013,3.30),'rubber',.0005);reposition_parent(q,leaf)
    # A continuing conduit route, saddle mounted, within the existing wall zone.
    use_root('Wall Utilities Rack')
    for o in S.objects:
        if o.type=='MESH' and (o.name.startswith(('Transformer box','Main breaker','CD | Utility fitted door'))):assign(o,'charcoal' if 'breaker' in o.name else 'ivory')
    for y in [12.5,13.1]:
        line('CD | Utility continuing conduit',[(6.65,y,2.5),(6.65,y,2.90),(6.65,y+.08,2.98)]+([(6.65,13.8,2.98),(6.65,13.8,3.26)] if y==12.5 else []),.035,'steel')
        for z in [2.32,2.76]:
            box('CD | Utility conduit saddle',(6.707,y,z),(.145,.095,.04),'steel',.0005)
    # Mounted top terminal accepts the conduit, closed circuit rather than stubs.
    box('CD | Utility upper terminal',(6.705,13.8,3.33),(.15,.24,.14),'charcoal',.001)
    box('CD | Utility terminal lid',(6.624,13.8,3.33),(.012,.20,.11),'ivory',.0005)
    # Active lockout job, connected to the existing disconnect handle.
    box('CD | Lockout tag', (6.512,13.8,1.44),(.002,.14,.22),'paper',0)
    txt('CD | Lockout task','AWAITING PART',(6.5105,13.859,1.49),.016,'ink',rot=(pi/2,0,-pi/2))
    txt('CD | Lockout overdue','DAY 19',(6.5105,13.847,1.44),.023,'coral',rot=(pi/2,0,-pi/2))
    line('CD | Lockout tag tie',[(6.512,13.8,1.55),(6.510,13.8,1.64),(6.534,13.8,1.68)],.0015,'rubber')
    # Put the new handover on the measured exposed native paper, not under it.
    use_root('Staff Desk Assembly')
    for o in list(S.objects):
        if o.name.startswith(('CD | Shift handover form','CD | Handover issue','CD | Handover incident','CD | Handover ink line')):bpy.data.objects.remove(o,do_unlink=True)
    box('CD | Shift handover form',(-3.40,6.35,.7726),(.277,.207,.001),'paper',0)
    txt('CD | Handover issue','RELIEF: NOT ASSIGNED',(-3.524,6.40,.7732),.020,'ink',rot=(0,0,0))
    txt('CD | Handover incident','731-A / HOLD',(-3.524,6.365,.7732),.018,'coral',rot=(0,0,0))
    for j in range(4):box('CD | Handover ink line',(-3.405,6.33-j*.016,.7732),(.21-j*.03,.001,.0002),'ink',0)
    use_root('Evidence Cabinet H2')
    txt('CD | Vault matched seal','731-A',(-4.94,14.7557,1.22),.020,'coral',align='CENTER')
    use_root('Covered Trolley H1')
    txt('CD | Transfer linked ID','731-A',(-5.456,12.235,.62),.029,'coral',rot=(pi/2,0,pi/2))
    # A projecting locator makes check-in readable from the primary route.
    root=asset_root('Check-in projecting locator','Office front head lintel',[(-2.4,3.58,2.66)],(-1,0,0))
    box('CD | Locator wall bracket',(-2.37,3.58,2.66),(.06,.04,.20),'steel',.001)
    box('CD | Locator sign edge',(-2.367,3.27,2.66),(.022,.62,.18),'charcoal',.001)
    box('CD | Locator sign enamel',(-2.354,3.27,2.66),(.004,.56,.14),'ivory',.0005)
    txt('CD | Locator heading','CHECK-IN',(-2.3515,3.06,2.635),.057,'ink',rot=(pi/2,0,pi/2))
    use_root('Checkin Counter Hatch')
    for y in [2.35,2.58,2.81]:
        box('CD | Check-in branch wayfinding',(-.95,y,.0005),(.10,.12,.001),'yellow',0)
    for x in [-1.2,-1.6,-2.0,-2.4,-2.8,-3.2]:
        box('CD | Check-in branch lane',(x,2.85,.0005),(.24,.065,.001),'yellow',0)
    # Motivated local pools; original light transforms remain immutable.
    for name,power in [('CD | Inspection face practical',78),('CD | Custody transfer practical',10),('CD | Scanner practical roof bounce',28),('CD | Check-in practical',62)]:
        S.objects[name].data.energy=power
    # An entry practical is mounted on the preserved corridor overhead surface.
    root=asset_root('Entry reverse locator','P1 corridor ceiling',[(-.50,-1.0,2.60),(.50,-1.0,2.60)],(0,0,1))
    box('CD | Entry locator housing',(0,-1.0,2.577),(1.10,.10,.046),'charcoal',.001)
    box('CD | Entry locator diffuser',(0,-1.0,2.552),(1.02,.075,.004),'warm_lamp',.0005)
    l=light('CD | Entry reverse practical',(0,-1.0,2.549),(0,-1.95,1.45),16,(1,.74,.48),1.0,.07);reposition_parent(l,root)
    S['second_full_review_repairs']='Distinct scanner/gate/cargo manufacture and paired check-in hierarchy; annular return bearings, seated lenses/inscription, linked731-A chain, continuing utilities/lockout; active fabric normalized after unwrap'


def annular_bearing(name,loc,outer,inner,depth,axis,key,foot=False,split=False):
    # Closed bearing with a true journal bore. A cast hanger has a flat foot
    # seated on the door top; its eye and neck are ONE continuous solid.
    n=16;other=[k for k in range(3) if k!=axis];vs=[];fs=[]
    for dd,r in [(-depth/2,outer),(depth/2,outer),(-depth/2,inner),(depth/2,inner)]:
        for j in range(n):
            xx=r*sin(2*pi*j/n);zz=r*cos(2*pi*j/n)
            if foot and r==outer and j in [7,8,9]:
                xx={7:.027,8:0,9:-.027}[j];zz=-.080
            q=list(loc);q[axis]+=dd;q[other[0]]+=xx;q[other[1]]+=zz;vs.append(q)
    for a,b in [(0,1),(1,3),(3,2),(2,0)]:
        fs.extend((a*n+j,a*n+(j+1)%n,b*n+(j+1)%n,b*n+j) for j in range(n-1 if split else n))
    if split:fs.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
    o=mesh(name,vs,fs,key,0)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o['bearing_contract']='Split C retaining ring in actual machined axle groove' if split else 'Closed journal bore, 0.5mm radial running clearance; continuous cast hanger foot' if foot else 'Closed annular roller; 0.5mm radial running clearance'
    return o


def arrival_captive_axle(xx):
    # A single headed, grooved axle rather than intersecting shaft/head solids.
    # Front shoulder seats on the hanger; split spring ring retains the wheel.
    sections=[(15.842,.014),(15.847,.014),(15.847,.008),(15.970,.008),
              (15.970,.0075),(15.972,.0075),(15.972,.008),(15.983,.008)]
    n=12;vs=[(xx+r*sin(2*pi*j/n),yy,3.56+r*cos(2*pi*j/n)) for yy,r in sections for j in range(n)]
    fs=[tuple(range(n-1,-1,-1)),tuple(range((len(sections)-1)*n,len(sections)*n))]
    for k in range(len(sections)-1):
        fs.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
    o=mesh('CD | P2 captive headed journal',vs,fs,'steel',0)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o['bearing_contract']='Continuous headed journal; head rear Y15.847 bears hanger front; actual reduced-radius groove Y15.970..15.972 captures split retaining ring'
    return o


def repair_arrival_load_path():
    use_root('Arrival Gate P2')
    # Enclosed bottom-slotted track positively captures the running trolley.
    # Both flange strips bear on original jambs; hanger clears the real slot.
    # Original head envelope and usable aperture remain identical.
    pts=[(15.84,3.5),(15.8,3.5),(15.8,3.7),(16.08,3.7),(16.08,3.5),
         (15.88,3.5),(15.88,3.52),(16.06,3.52),(16.06,3.68),
         (15.82,3.68),(15.82,3.52),(15.84,3.52)]
    replace('P2 frame head lintel',profile('TEMP captured arrival rail',pts,4.92,0,(0,0,0),'steel',0),
            'Original header becomes enclosed bottom-slotted load track within identical bounds; lower flange strips bear on original jamb tops')
    for side in [-1,1]:
        leaf=S.objects['P2 blast leaf '+('west' if side<0 else 'east')]
        for xx in [side*.65,side*1.75]:
            hanger=annular_bearing('CD | P2 cast leaf hanger',(xx,15.860,3.56),.019,.0085,.026,1,'steel',True)
            reposition_parent(hanger,leaf)
            shaft=arrival_captive_axle(xx)
            reposition_parent(shaft,leaf)
            wheel=annular_bearing('CD | P2 captured trolley roller',(xx,15.94,3.56),.04,.0085,.060,1,'charcoal')
            reposition_parent(wheel,leaf)
            clip=annular_bearing('CD | P2 axle retaining spring',(xx,15.971,3.56),.012,.00765,.002,1,'steel',split=True)
            reposition_parent(clip,leaf)
            # Flat hanger foot meets leaf Z3.48, eye captures the axle; roller
            # bottom Z3.52 rests on the anchored rail flange, not ancestry.
        for zz in [.20,3.20]:
            # Guide pad closes the inherited 10mm lateral gap, with a declared
            # 0.5mm running clearance from the anchored jamb inner surface.
            q=box('CD | P2 lateral guide wear pad',(side*2.29475,15.837,zz),(.0095,.045,.09),'rubber',0)
            reposition_parent(q,leaf)
    world_edit(S.objects['P2 gate sign plate'],lambda q:(q.x,min(q.y,15.68005) if q.y<15.7 else q.y,q.z),
               'Printed glyph rear seats on extended real sign face; original sign/font world poses retained')
    world_edit(S.objects['P2 security console'],lambda q:(q.x,min(q.y,15.59) if q.y<15.7 else q.y,q.z),
               'Console face backs retained screen at actual Y15.59, removing inherited 10mm mounting gap')


def repair_key_cabinet():
    use_root('CD | Office key cabinet')
    replace('Office key box cabinet',shell('TEMP real glazed key cabinet',(-3,9.445,1.5),(.30,.15,.40),1,'charcoal',opening=.96,taper=1,cut=.003),
            'Hollow wall-mounted cabinet exposes retained glazing and real interior; original pose, outer front/back datums and wall support preserved')
    ring('CD | Key pane retaining ledge',(-3,9.4775,1.5),.288,.384,.250,.350,.005,1,'steel',cut=.00288)
    # Pane rear is Y9.475: it sits on the real inner retaining ledge. Key hooks
    # extend from the hollow back web and retain actual separate key rings.
    for xx in [-3.075,-3,-2.925]:
        cyl('CD | Key hook wall journal',(xx,9.495,1.55),.003,.038,'steel','Y',vertices=8,w=0)
        annular_bearing('CD | Key retained bow',(xx,9.479,1.547),.013,.006,.003,1,'brass')
        box('CD | Key blade',(xx,9.479,1.514),(.008,.003,.041),'brass',0)
        box('CD | Key tooth',(xx+.004,9.479,1.494),(.008,.003,.012),'brass',0)
    # Correct the inherited backward internal lettering through authored mesh
    # geometry, retaining its original object matrix/name rather than moving it.
    profile('CD | Key cabinet nameband',octagon(.288,.036,.003),.002,1,(-3,9.371,1.674),'charcoal',0)
    label=txt('TEMP correctly facing key label','KEYS',(-3,9.3694,1.660),.035,'ivory',align='CENTER')
    label.data.extrude=0
    for o in list(bpy.context.selected_objects):o.select_set(False)
    label.select_set(True);bpy.context.view_layer.objects.active=label;bpy.ops.object.convert(target='MESH')
    label=bpy.context.object;label.select_set(False)
    replace('Key box label',label,'Retained label matrix/name; actual readable flat inscription placed against cabinet upper front rim, correct outward facing geometry')


def repair_printed_graphics():
    # Printed letters are ink, not six-millimetre-thick sculpted glyphs. This
    # removes shadowed sidewalls which destroyed microcopy at 600p. Existing
    # names and every original object world pose survive.
    for o in S.objects:
        if o.type!='FONT':continue
        o.data.extrude=0;o.data.bevel_depth=0
        if o.name in ORIGINAL:EXCEPTIONS[o.name]='Typography construction repair: flat printed ink replaces oversized 6mm glyph depth; concise operational copy may change glyph extent, original object world pose and physical room datums retained'
        o['print_contract']='Flat editable ink glyphs; typography scaled for actual evidence cameras; no thick microtype sides'
    edits={
        'Manifest header':('DUTY CLEARANCE',.024),
        'Manifest line 1':('SECTOR 04 / ARRIVAL',.013),
        'Manifest line 2':('CUSTODY: 731-A',.014),
        'Manifest line 3':('RELEASE: DENIED',.014),
        'Cargo crate text 1':('SECTOR 04',.050),
        'Cargo crate text 2':('CUSTODY 731-A',.034),
        'Screen line 1':('COMPLIANCE OS',.022),
        'Screen line 2':('SHIFT 041 / ACTIVE',.018),
        'Screen line 3':('GATE SEALED',.018),
        'CD | Reassurance qualification':('RELEASE BY MANAGEMENT ONLY',.012),
        'CD | Handover issue':('NO RELIEF ASSIGNED',.021),
        'CD | Handover incident':('731-A / HOLD',.021),
        'CD | Lockout task':('PART PENDING',.019),
    }
    for name,(body,size) in edits.items():
        if name in S.objects and S.objects[name].type=='FONT':
            S.objects[name].data.body=body;S.objects[name].data.size=size
    # Retain one coherent identifier on the existing transfer docket rather
    # than multiple new competing captions on the same small paper.
    for name in ['CD | Transfer custody match','CD | Transfer linked ID']:
        if name in S.objects:bpy.data.objects.remove(S.objects[name],do_unlink=True)
    for o in S.objects:
        if o.type=='FONT' and o.name.startswith('Specimen tag text'):
            o.data.body={'Specimen tag text 1':'731-A / HOLD','Specimen tag text 2':'CUSTODY TRANSFER','Specimen tag text 3':'RELEASE DENIED'}.get(o.name,o.data.body)
            o.data.size={'Specimen tag text 1':.026,'Specimen tag text 2':.016,'Specimen tag text 3':.016}.get(o.name,o.data.size)


def repair_working_surfaces(crate_only=False):
    # Active shared transit-case paint, not the unused slice-only colour.
    # The bounded finish repair uses this exact canonical operation.
    material_patch(MATERIALS['coral'],(4.65,5.35,1.35),(.40,.09,.12),(.32,.25,.17),.65,True)
    if crate_only:return
    # Restrained contact wear follows actual actions; clean broad walls remain
    # deliberate negative space rather than being carpeted in arbitrary grunge.
    for o in S.objects:
        if o.type!='MESH':continue
        if o.name.startswith(('G1 leaf','CD | G1 pressed panel bay')) and 'panel' in o.name:
            if MATERIALS['charcoal'] in o.data.materials[:]:assign(o,'wear')
        elif o.name.startswith('CD | Arrival leaf pressed cassette'):assign(o,'wear')
    floor=S.objects['Floor slab'].data.materials[0]
    material_patch(floor,(0,6.45,0),(.48,.70,.009),(.09,.085,.076),.62,True)
    material_patch(floor,(1.9,6.2,0),(.35,1.55,.009),(.30,.28,.23),.55,True)
    material_patch(floor,(-3.5,2.95,0),(.65,.40,.009),(.10,.095,.08),.64,True)
    for key,p,r,color in [
        ('blue',(5.05,14.765,1.04),(.22,.035,.20),(.28,.285,.275)),
        ('navy',(.73,6.812,.23),(.15,.045,.22),(.24,.25,.255)),
        ('wear',(0,15.74,1.12),(1.30,.04,.12),(.32,.32,.29)),
        ('ivory',(6.51,13.8,1.45),(.05,.16,.16),(.40,.37,.30)),
    ]:material_patch(MATERIALS[key],p,r,color,.65,True)
    # Soft removed-notice paint shadow on the inspection wall. This changes the
    # plaster response in place; it creates no detached floating decal plane.
    material_patch(MATERIALS['plaster'],(6.80,5.95,2.00),(.009,.80,.60),(.51,.485,.425),.42,False)


def repair_personal_and_institutional_traces():
    use_root('Staff Desk Assembly')
    # An interrupted case file and an off-shift folded work jacket sit on the
    # measured desk top. Paper layers and cloth bottoms genuinely bear there.
    box('CD | Open case folder cover',(-3.86,7.18,.761),(.36,.34,.002),'coral',0)
    for j in range(3):
        box('CD | Unfinished case pages',(-3.85+.004*j,7.175-.004*j,.7625+.001*j),(.30,.28,.001),'paper',0)
    # Broad angular folds give fabric a distinct silhouette without noisy
    # micro-tessellation; folded, supported underside is Z.760 everywhere.
    nx,ny=16,14;vs=[];fs=[]
    for layer in [0,1]:
        for j in range(ny+1):
            yy=6.15+j*.34/ny
            for i in range(nx+1):
                xx=-4.09+i*.34/nx
                z=.760 if layer==0 else .781+.009*sin(i*pi/4)*sin(j*pi/ny)+.012*(1-abs(2*i/nx-1))
                vs.append((xx,yy,z))
    count=(nx+1)*(ny+1)
    for j in range(ny):
        for i in range(nx):
            q=j*(nx+1)+i;fs.extend([(q,q+nx+1,q+nx+2,q+1),(q+count,q+count+1,q+count+nx+2,q+count+nx+1)])
    border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
    fs.extend((q,border[(k+1)%len(border)],border[(k+1)%len(border)]+count,q+count) for k,q in enumerate(border))
    jacket=mesh('CD | Clerk folded work jacket',vs,fs,'fabric',0)
    bm=bmesh.new();bm.from_mesh(jacket.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(jacket.data);bm.free()
    jacket['support_geometry']='Closed folded jacket; measured entire bottom bears on Staff desk top at Z.760'
    # One faded reassurance poster has a coercive second meaning. It is mounted
    # to the retained south wall, outside circulation and all asset footprints.
    root=asset_root('Faded duty poster','South wall east',[(3.7,0,2.05)],(0,-1,0))
    box('CD | Duty poster stock',(3.7,.0008,2.05),(.92,.0016,1.18),'paper',0)
    # Angular native graphic: simplified factory roof and rays, using existing
    # warm institutional ink families instead of a round cartoon emblem.
    profile('CD | Poster factory silhouette',[(-.35,-.09),(-.35,.10),(-.15,.02),(-.15,.15),(.03,.05),(.03,.18),(.29,.07),(.29,-.09)],.0002,1,(3.7,.0017,2.12),'coral',0)
    for xx in [3.37,3.46,3.55,3.64,3.73,3.82,3.91]:
        box('CD | Poster factory windows',(xx,.0019,2.08),(.031,.0002,.043),'paper',0)
    txt('CD | Poster reassurance','YOUR WORK\nMATTERS',(3.7,.00205,2.48),.083,'ink',rot=(pi/2,0,pi),align='CENTER')
    txt('CD | Poster coercive line','CONTINUED DUTY\nIS YOUR REWARD',(3.7,.00205,1.84),.041,'ink',rot=(pi/2,0,pi),align='CENTER')
    # A bolted replacement sleeve has different finish and a physical repair
    # seam on a working conduit; this is an unfinished job, not a label alone.
    use_root('Wall Utilities Rack')
    annular_bearing('CD | Replacement conduit sleeve',(6.65,13.1,2.62),.043,.0355,.10,2,'brass')
    for zz in [2.58,2.66]:
        cyl('CD | Sleeve clamp captive stud',(6.602,13.1,zz),.004,.014,'steel','X',vertices=6,w=0)


def repair_practical_hierarchy():
    # Existing lamps keep their authored positions. Local pool changes expose
    # the cabinet/trolley without turning the support bay into a bright stage.
    for name,power in [('CD | Inspection face practical',82),('CD | Custody transfer practical',22),
                       ('CD | Scanner practical roof bounce',34),('CD | Check-in practical',62)]:
        S.objects[name].data.energy=power
    use_root('Cargo Inspection Conveyor')
    # Real shallow task-light cartridge seats on the existing curtain clamp.
    # The broad warm lip separates the dark rubber mouth from the shield body.
    box('CD | Cargo lip task housing',(4.65,6.445,1.772),(.90,.030,.025),'charcoal',.0005)
    box('CD | Cargo lip task diffuser',(4.65,6.4285,1.772),(.84,.003,.016),'warm_lamp',0)
    lamp=light('CD | Cargo mouth practical',(4.65,6.4265,1.772),(4.65,6.46,1.15),9,(1,.82,.61),.84,.016)
    reposition_parent(lamp,ASM)


def repair_third_review():
    repair_arrival_load_path();repair_key_cabinet();repair_working_surfaces()
    repair_personal_and_institutional_traces();repair_practical_hierarchy();repair_printed_graphics()
    S['third_full_review_repairs']='Actual captured P2 carriages and backing; hollow glazed key cabinet; flat readable ink and coherent custody731-A; mid-value gate leaves, selective contact wear, supported interrupted file/jacket and faded coercive duty poster; motivated cargo mouth and custody light'


def shader_math(m,operation,*values):
    node=m.node_tree.nodes.new('ShaderNodeMath');node.operation=operation
    for i,value in enumerate(values):
        if isinstance(value,(float,int)):node.inputs[i].default_value=value
        else:m.node_tree.links.new(value,node.inputs[i])
    return node.outputs[0]


def repair_surface_character():
    # These are changes to consumed families, not invisible unused materials.
    # Large floor joints are shading relief only: the actual support datum is Z0.
    floor=S.objects['Floor slab'].data.materials[0]
    n=floor.node_tree.nodes;l=floor.node_tree.links;bs=n.get('Principled BSDF')
    g=n.new('ShaderNodeNewGeometry');xyz=n.new('ShaderNodeSeparateXYZ');l.new(g.outputs['Position'],xyz.inputs[0])
    masks=[]
    for axis,period in [('X',2.8),('Y',3.2)]:
        v=shader_math(floor,'FRACT',shader_math(floor,'DIVIDE',xyz.outputs[axis],period))
        edge=shader_math(floor,'MINIMUM',v,shader_math(floor,'SUBTRACT',1,v))
        masks.append(shader_math(floor,'LESS_THAN',edge,.0045/period))
    joint=shader_math(floor,'MAXIMUM',*masks)
    mix=n.new('ShaderNodeMixRGB');l.new(shader_math(floor,'MULTIPLY',joint,.58),mix.inputs[0]);l.new(bs.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);mix.inputs[2].default_value=(.055,.051,.047,1);l.new(mix.outputs[0],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0015;bump.inputs['Strength'].default_value=.65;l.new(shader_math(floor,'MULTIPLY',joint,-1),bump.inputs['Height'])
    if bs.inputs['Normal'].is_linked:l.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    floor['surface_contract']='Authored 2.8x3.2m concrete pour joints, 9mm seam shading; no displaced support surface or new collision claim'
    # Actual dragged cart wheels, shuffled boots and counter standing position.
    for p,r,col,k in [((1.68,7.5,0),(.085,2.1,.012),(.075,.073,.067),.72),((2.18,8.1,0),(.09,2.8,.012),(.082,.077,.065),.66),((0,6.60,0),(.53,.80,.012),(.11,.099,.078),.66),((-3.47,3.01,0),(.64,.36,.012),(.095,.083,.073),.68),((.15,14.5,0),(1.35,.36,.012),(.12,.105,.084),.54)]:
        material_patch(floor,p,r,col,k,True)
    # The plaster echoes the spawn's warm/mauve neutral, dulled by the dock.
    m=MATERIALS['plaster'];m.diffuse_color=(.455,.405,.385,1)
    for node in m.node_tree.nodes:
        if node.type=='VALTORGB':
            for e,f in zip(node.color_ramp.elements,[.86,1.14]):e.color=(*(.455*f,.405*f,.385*f),1)
        if node.type=='BUMP':node.inputs['Distance'].default_value=.0032;node.inputs['Strength'].default_value=.48
        if node.type=='TEX_NOISE' and node.inputs['Scale'].default_value>100:node.inputs['Scale'].default_value=72
    # Mid-frequency woven response is legible in 600p neutral diagnostics;
    # broad dye variation remains quiet, avoiding photographic noise.
    for key in ['cotton','fabric']:
        m=MATERIALS[key];n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Sheen Weight'].default_value=.42;bs.inputs['Sheen Roughness'].default_value=.75
        for node in n:
            if node.type=='TEX_WAVE':node.inputs['Scale'].default_value=66 if node.bands_direction=='X' else 74
            if node.type=='BUMP':node.inputs['Distance'].default_value=.0014;node.inputs['Strength'].default_value=.65
        uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='CD_Fabric_Cut_1m'
        noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.5;noise.inputs['Detail'].default_value=1;l.new(uvnode.outputs[0],noise.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.66,.66,.66,1);ramp.color_ramp.elements[1].color=(1.10,1.10,1.10,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.8;l.new(bs.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    for key in ['blue','navy','wear']:
        m=MATERIALS[key];n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
        g=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.4;noise.inputs['Detail'].default_value=1;l.new(g.outputs['Position'],noise.inputs['Vector'])
        rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.58 if key=='blue' else .65;rough.inputs['To Max'].default_value=.84;l.new(noise.outputs['Fac'],rough.inputs['Value']);l.new(rough.outputs[0],bs.inputs['Roughness'])
    for key,p,r,col in [('blue',(5.78,14.678,1.18),(.11,.014,.29),(.24,.245,.235)),('blue',(4.77,14.678,1.18),(.11,.014,.29),(.22,.225,.21)),('blue',(3.90,6.68,1.15),(.024,.32,.18),(.28,.28,.255)),('wear',(1.14,6.83,.25),(.16,.05,.15),(.12,.125,.12)),('navy',(.73,6.82,.22),(.12,.04,.18),(.24,.23,.21))]:material_patch(MATERIALS[key],p,r,col,.72,True)
    # Lift the existing rubber impact insert, not all rubber curtain/wheel parts.
    material_patch(MATERIALS['rubber'],(1.4,6.80,.86),(.35,.04,.64),(.042,.045,.046),.74,False)
    material_patch(MATERIALS['Handled linoleum'],(-3.35,3.29,1.042),(.26,.12,.007),(.105,.092,.070),.66,True)
    # Replace conspicuous thin added scar geometry with consumed surface wear.
    for o in list(S.objects):
        if o.name.startswith('CD | Counter handling scar'):bpy.data.objects.remove(o,do_unlink=True)


def repair_manifest_writing_surface():
    use_root('Checkin Counter Hatch')
    # A tessellated corner curl cannot propagate across the large writing face.
    # All retained font planes remain at Z1.054. The unprinted curled corner is
    # north of every current glyph; the writing face is Z1.053 throughout.
    nx,ny=21,28;vs=[];fs=[]
    for layer in [0,1]:
        for j in range(ny+1):
            y=3.27+.28*j/ny
            for i in range(nx+1):
                x=-3.455+.21*i/nx
                lift=.004*max(0,(x+3.285)/.040)*max(0,(y-3.51)/.040)
                vs.append((x,y,(1.051 if layer==0 else 1.053)+lift))
    count=(nx+1)*(ny+1)
    for j in range(ny):
        for i in range(nx):
            q=j*(nx+1)+i;fs.extend([(q,q+nx+1,q+nx+2,q+1),(q+count,q+count+1,q+count+nx+2,q+count+nx+1)])
    border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
    fs.extend((q,border[(k+1)%len(border)],border[(k+1)%len(border)]+count,q+count) for k,q in enumerate(border))
    paper=replace('Counter manifest paper',mesh('TEMP planar writing face and isolated curl',vs,fs,'paper',0),'Tessellated 2mm paper sheet with isolated unprinted corner curl, flat Z1.053 writing surface under original Z1.054 glyphs; original name/matrix/layout preserved')
    bm=bmesh.new();bm.from_mesh(paper.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(paper.data);bm.free()
    font=bpy.data.fonts.load(str(ROOT/'revamp/art/fonts/DejaVuSansCondensed-Bold.ttf'));font.pack();font.filepath='//revamp/art/fonts/DejaVuSansCondensed-Bold.ttf'
    for name in ['Manifest header','Manifest line 1','Manifest line 2','Manifest line 3','CD | Handover issue','CD | Handover incident','CD | Lockout task','Specimen tag text 1']:
        o=S.objects.get(name)
        if o and o.type=='FONT':o.data.font=font
    for name,body,size,key in [('Manifest header','DUTY CLEARANCE',.020,'ink'),('Manifest line 1','SECTOR 04 / ARRIVAL',.013,'ink'),('Manifest line 2','CUSTODY 731-A',.014,'ink'),('Manifest line 3','HOLD / 731-A',.020,'coral')]:
        o=S.objects[name];o.data.body=body;o.data.size=size;assign(o,key)
    # Real ink rules and offset rejected-stamp frame, on the actual sheet.
    for y in [3.477,3.433,3.400,3.367,3.314]:box('CD | Manifest printed rule',(-3.35,y,1.05302),(.186,.0007,.000025),'ink',0)
    for x in [-3.445,-3.255]:box('CD | Manifest printed side rule',(x,3.3955,1.05302),(.0007,.163,.000025),'ink',0)
    # The existing lower field is centred on its retained origin; frame is
    # deliberately offset within the paper, denoting a processed hold docket.
    o=S.objects['Manifest line 3'];yy=o.matrix_world.translation.y
    for x in [-3.435,-3.265]:box('CD | Returned field border',(x,yy+.002,1.05306),(.0013,.027,.00004),'ink',0)
    for y in [yy-.0115,yy+.0155]:box('CD | Returned field border',(-3.35,y,1.05306),(.17,.0013,.00004),'ink',0)
    bpy.context.view_layer.update();verts=[paper.matrix_world@v.co for v in paper.data.vertices]
    tree=BVHTree.FromPolygons(verts,[list(f.vertices) for f in paper.data.polygons],all_triangles=False)
    dg=bpy.context.evaluated_depsgraph_get();checked=0;minimum=1
    for name in ['Manifest header','Manifest line 1','Manifest line 2','Manifest line 3']:
        o=S.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh()
        try:
            for v in me.vertices:
                q=o.matrix_world@v.co;hit=tree.ray_cast(Vector((q.x,q.y,1.10)),Vector((0,0,-1)),.1)[0]
                if hit is None:raise RuntimeError('Manifest glyph outside writing sheet: '+name)
                gap=q.z-hit.z
                if gap<-.000001 or gap>.00101:raise RuntimeError('Manifest glyph burial/support gap: '+name+' '+str(gap))
                checked+=1;minimum=min(minimum,gap)
        finally:ev.to_mesh_clear()
    S['manifest_writing_verification']=json.dumps(dict(sampled_glyph_vertices=checked,minimum_ink_gap_m=minimum,zero_buried=True,retained_font_plane_z=1.054,flat_writing_plane_z=1.053))


def repair_specific_machine_construction():
    use_root('Person Scanner Arch')
    # Individually drafted optical pods with true apertures and axial backing.
    for side in [-1,1]:
        for j in range(6):
            z=.4+.36*j
            replace(f'Sensor emitter {side}_{j}',shell('TEMP drafted optical aperture',(.63*side,7,z),(.020,.18,.24),0,'blue',front_sign=-side,taper=1,cut=.023,opening=.62),'Separate cast optical pod with actual aperture, retained original sensor position/matrix and scanner clearance')
            annular_bearing('CD | Optical pod rear mounting sleeve',(.62875*side,7,z),.047,.0355,.0105,0,'steel')
        # Inspection spines read as cast metal around dark service assemblies.
        assign(S.objects['Scanner portal column '+str(side)],'wear')
    use_root('Cargo Inspection Conveyor')
    # A folded roof service channel articulates the actual shield housing while
    # every side/rib/lifting-eye attachment retains the prior exterior surface.
    pts=[(-.75,-.70),(-.60,-.70),(-.60,.30),(.60,.30),(.60,-.70),(.75,-.70),(.75,.70),(.53,.70),(.50,.66),(-.50,.66),(-.53,.70),(-.75,.70)]
    replace('Lead tunnel main body',profile('TEMP shield with folded roof service channel',pts,2.30,1,(4.65,7.65,1.45),'blue',.002),'True open radiation shield with pressed roof service channel, retained envelope/aperture/side support surfaces and original matrix')
    # Lifting stems at X4.05/5.25 remain on the full-height corner rails;
    # the central roof depression never removes their actual bearing surface.
    for y in [6.72,8.58]:
        box('CD | Shield roof service seam',(4.65,y,2.1104),(.99,.006,.0008),'charcoal',0)
    # Separate the operator display face from the black cuboid rear in the
    # unchanged east-facing screen planes; no unsupported second console.
    for j in [0,1]:
        o=S.objects['Conveyor monitor housing '+str(j)]
        for f in o.data.polygons:f.use_smooth=False


def repair_interrupted_worker_trace():
    use_root('Staff Desk Assembly')
    o=S.objects['CD | Clerk folded work jacket'];vs=[o.matrix_world@v.co for v in o.data.vertices]
    tree=BVHTree.FromPolygons(vs,[list(f.vertices) for f in o.data.polygons],all_triangles=False)
    def z_at(x,y):
        q=tree.ray_cast(Vector((x,y,.95)),Vector((0,0,-1)),.25)[0]
        if q is None:raise RuntimeError('Missing folded jacket support')
        return q.z
    # Closed collar flaps bear over the folded jacket, giving it a garment read.
    for side in [-1,1]:
        xx=-3.92;points=[(xx+.014*side,6.418),(xx+.077*side,6.405),(xx+.055*side,6.350)]
        vv=[(x,y,z_at(x,y)+.0002) for x,y in points]+[(x,y,z_at(x,y)+h) for (x,y),h in zip(points,[.006,.016,.012])]
        q=mesh('CD | Folded jacket collar flap',vv,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'fabric',0)
        bm=bmesh.new();bm.from_mesh(q.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(q.data);bm.free()
    # Pocket hem conforms to the actual cloth rather than floating on a pad.
    outer=[(-4.035,6.22),(-3.975,6.22),(-3.975,6.292),(-4.035,6.292)];inner=[(-4.032,6.223),(-3.978,6.223),(-3.978,6.289),(-4.032,6.289)]
    vv=[(x,y,z_at(x,y)+dz) for dz in [.0001,.0016] for ringpts in [outer,inner] for x,y in ringpts];ff=[]
    for i in range(4):
        j=(i+1)%4;ff.extend([(i,j,j+4,i+4),(i+8,i+12,j+12,j+8),(i,i+8,j+8,j),(i+4,j+4,j+12,i+12)])
    q=mesh('CD | Folded jacket pocket stitched hem',vv,ff,'fabric',0)
    bm=bmesh.new();bm.from_mesh(q.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(q.data);bm.free()
    # The interrupted case page now contains an actual completed field/grid.
    for j in range(8):box('CD | Unfinished case printed rule',(-3.855,7.254-j*.023,.76502),(.237 if j<2 else .16,.0011,.00003),'ink',0)
    for x in [-3.975,-3.795]:box('CD | Unfinished case field separator',(x,7.161,.76502),(.001,.195,.00003),'ink',0)
    for name,body in [('CD | Handover issue','RELIEF CANCELLED'),('CD | Handover incident','14 HRS / 731-A HOLD'),('CD | Lockout task','NO SPARE PARTS')]:
        if name in S.objects:S.objects[name].data.body=body
    # Lift the existing transfer docket's critical ID contrast; remove the
    # confusing yellow text response on its lower field without adding labels.
    o=S.objects['Specimen tag text 3'];assign(o,'ink');o.data.body='RELEASE DENIED';o.data.size=.018


def repair_checkin_discoverability():
    root=asset_root('Arrival check-in cue','Office east corner south',[(-2.32,3.80,2.67)],(-1,0,0))
    box('CD | Arrival check-in cue plate',(-2.313,3.80,2.67),(.014,.70,.30),'charcoal',.002)
    o=txt('CD | Arrival check-in cue text','CHECK IN\n← COUNTER',(-2.3058,3.80,2.705),.065,'ivory',rot=(pi/2,0,pi/2),align='CENTER')
    o.data.font=S.objects['Manifest header'].data.font;o.data.extrude=0;o.data.bevel_depth=0
def reconcile_architectural_labels():
    # Run after final CURVE conversion, using the same local evaluated bounds
    # as static obstacle selection. No geometry or runtime collider changes.
    for o in S.objects:
        if o.get('support_class')!='architectural' or o.type!='MESH':continue
        b=[Vector(v) for v in o.bound_box];d=[max(v[k] for v in b)-min(v[k] for v in b) for k in range(3)]
        if min(d)>=.05-1e-5 and math.prod(d)>=.015:
            o['circulation_solid']=True;o['classification_scope']='Static authoring dimensional obstacle; runtime collider binding unverified'


def repair_fourth_review():
    repair_surface_character();repair_manifest_writing_surface();repair_specific_machine_construction();repair_interrupted_worker_trace();repair_checkin_discoverability()
    S['fourth_full_review_repairs']='Planar written paper and packed bold operational ink; cast optical pods/real mounting sleeves, pressed shield roof service channel; consumed pour-joint/traffic/paint/canvas response; recognizable supported folded work garment and interrupted case; compact arrival-side check-in cue; source poses/boundaries retained'


def repair_scanner_pockets():
    # The original columns are solid. Real pockets expose the actual optical
    # pods; attaching hidden detail inside the solid is not construction.
    use_root('Person Scanner Arch')
    for side in [-1,1]:
        column=S.objects['Scanner portal column '+str(side)]
        for selected in list(bpy.context.selected_objects):selected.select_set(False)
        column.select_set(True);bpy.context.view_layer.objects.active=column
        for mod in list(column.modifiers):
            if mod.type=='BEVEL':bpy.ops.object.modifier_apply(modifier=mod.name)
            elif mod.type=='WEIGHTED_NORMAL':column.modifiers.remove(mod)
        cuts=[]
        for j in range(6):
            cuts.append(box('TEMP scanner optical pocket',(.6210025*side,7,.4+.36*j),(.038005,.204,.264),'wear',0))
        cuts.append(profile('TEMP scanner outer service pocket',octagon(.28,2.40,.021),.024005,0,(.8469975*side,7,1.35),'wear',0))
        for cutter in cuts:
            mod=column.modifiers.new('Actual machined sensor/service pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.context.view_layer.objects.active=column;bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(cutter,do_unlink=True)
        bm=bmesh.new();bm.from_mesh(column.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(column.data);bm.free();uv(column)
        wn=column.modifiers.new('Manufactured face normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40
        EXCEPTIONS[column.name]='Six actual inner optical pockets and outer service rebate expose retained pods; column outer bounds, floor bearing and scanner aperture unchanged'
        replace('Scanner column inset '+str(side),profile('TEMP folded side access cover',octagon(.26,2.36,.020),.012,0,(.841*side,7,1.35),'charcoal',.0005),'Recessed folded access cover inside actual outer service pocket, back bears at X±.835; original name/matrix retained')
        for y in [6.894,7.106]:
            for z in [.22,2.48]:cyl('CD | Scanner side cover captive fixing',(.8485*side,y,z),.005,.003,'steel','X',vertices=6,w=0)
        column.select_set(False)
    # The fixed east-facing screens keep their original pose. A quieter mid-
    # value rear polymer response makes the existing drafted shell/vents read.
    for y in [7.35,7.95]:material_patch(MATERIALS['plastic'],(3.210,y,1.30),(.012,.19,.15),(.090,.100,.105),.72,False)
    S['scanner_pocket_construction']='Inner pocket floor X±.640005, pod rear X±.640; outer service seat X±.834995, cover back X±.835; outer column bounds and all inherited matrices retained'
