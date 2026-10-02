"""Purposeful small infrastructure for the existing fuel-corridor assemblies.

All dimensions are metres. Reuse the section's fabrication, material, UV and
support tooling; these are static authoring details, not runtime interactions.
"""
import math
import bpy
from mathutils import Matrix, Vector
from fuel_kit import (B, add, mat, surface, frame, ring, bolt, polygon,
                      rounded_path, label, support, project_uv)

FRONT=Matrix.Rotation(math.pi/2,3,'X')


def receptacles(sealed=False):
    b=B()
    b.box((.284,.014,.172),(0,-.007,0),mat('dark steel'),.009,seg=3)
    b.box((.265,.007,.156),(0,-.019,0),mat('rubber'),.007)
    b.box((.257,.027,.149),(0,-.036,0),mat('warm enamel'),.009,seg=3)
    for x in [-.111,.111]:
        for z in [-.058,.058]:bolt(b,(x,-.052,z),.004)
    for x in [-.066,.066]:
        # Formed boss, recess and replaceable seal; contacts sit inside the cup.
        b.lathe([(.031,0),(.043,0),(.046,.009),(.041,.030),(.031,.030),(.029,.017),(.031,0)],
                (x,-.049,-.009),mat('replacement enamel'),seg=40,rot=FRONT)
        b.cyl(.030,.003,(x,-.067,-.009),mat('rubber'),seg=32,axis='Y')
        for a in [30,150,270]:
            angle=math.radians(a);xx=x+.017*math.cos(angle);zz=-.009+.017*math.sin(angle)
            ring(b,.0043,.0013,(xx,-.071,zz),mat('brass'),axis='Y',seg=16)
            b.cyl(.0028,.004,(xx,-.067,zz),mat('ink'),seg=16,axis='Y')
        b.box((.074,.016,.012),(x,-.053,.036),mat('steel'),.002)
        b.cyl(.005,.083,(x-.0415,-.059,.039),mat('steel'),seg=20,axis='X')
        # One closed cover and one lifted cover, both with thickness/rolled edge.
        if sealed:
            b.lathe([(0,0),(.039,0),(.045,.006),(.045,.014),(.039,.019),(0,.019)],
                    (x,-.079,-.009),mat('navy enamel'),seg=40,rot=FRONT)
            b.box((.024,.009,.012),(x,-.103,-.038),mat('dark steel'),.003)
        elif x>0:
            tilt=Matrix.Rotation(-.62,3,'X')
            b.lathe([(0,0),(.039,0),(.044,.005),(.044,.014),(.038,.019),(0,.019)],
                    (x,-.054,.071),mat('navy enamel'),seg=40,rot=tilt)
            b.tube([(x,-.059,.039),(x,-.061,.073)],.005,mat('dark steel'),seg=12)
        else:
            b.lathe([(0,0),(.024,0),(.030,.005),(.030,.018),(.026,.022),(.023,.047),
                     (.017,.053),(.012,.076),(0,.076)],
                    (x,-.071,-.009),mat('rubber'),seg=32,rot=FRONT)
            for d in [.026,.031,.037]:ring(b,.025,.003,(x,-.071-d,-.009),mat('ochre enamel'),axis='Y',seg=24)
    b.box((.094,.0015,.021),(0,-.0505,.057),mat('ink enamel'),.001)
    return b


def retained_lead():
    b=B();rubber=mat('rubber')
    b.tube(rounded_path([(-.066,-.147,-.009),(-.067,-.16,-.056),(.003,-.14,-.093),
                        (.19,-.107,-.060),(.216,-.102,-.070)]),.006,rubber,seg=14)
    # Several sagged loops are carried on a real hook, above the walking route.
    pts=[]
    for j in range(169):
        t=j/168;a=math.pi+j*2*math.pi/56
        pts.append((.305+.089*math.cos(a),-.102-.027*t,
                    -.070+(.067+.003*math.sin(t*math.pi))*math.sin(a)))
    b.tube(pts,.0055,rubber,seg=12)
    b.box((.052,.006,.072),(.305,-.003,-.012),mat('dark steel'),.003)
    for z in [-.037,.013]:bolt(b,(.305,-.009,z),.0035)
    b.tube(rounded_path([(.305,-.005,-.012),(.305,-.055,-.012),
                        (.305,-.145,-.012),(.305,-.15,.009)]),.005,mat('steel'),seg=12)
    b.tube(rounded_path([(.216,-.129,-.070),(.236,-.135,-.140),(.295,-.138,-.161),
                        (.437,-.128,-.161),(.462,-.122,-.140)]),.0055,rubber,seg=12)
    b.lathe([(0,0),(.013,0),(.018,.006),(.018,.020),(.012,.028),(0,.028)],
            (.462,-.122,-.140),mat('warm enamel'),seg=24,rot=FRONT)
    return b


def conduit_saddle():
    b=B()
    b.box((.066,.008,.040),(0,-.004,0),mat('dark steel'),.002)
    for x in [-.026,.026]:bolt(b,(x,-.010,0),.0035)
    b.box((.019,.031,.012),(0,-.0235,0),mat('steel'),.002)
    ring(b,.011,.003,(0,-.044,-.008),mat('steel'),seg=24)
    return b


def junction_box():
    b=B()
    for x in [-.083,.083]:
        b.box((.048,.011,.258),(x,-.0055,0),mat('dark steel'),.004)
        for z in [-.109,.109]:bolt(b,(x,-.014,z),.004)
    b.box((.204,.058,.214),(0,-.040,0),mat('replacement enamel'),.010,seg=3)
    frame(b,.187,.198,.009,.009,-.072,0,mat('rubber'),r=.015)
    b.box((.181,.010,.192),(0,-.080,0),mat('warm enamel'),.006,seg=3)
    for x in [-.071,.071]:
        for z in [-.077,.077]:bolt(b,(x,-.087,z),.0038)
    for x in [-.046,.046]:
        b.lathe([(0,0),(.011,0),(.016,.005),(.016,.014),(.011,.020),(.009,.035),(0,.035)],
                (x,-.041,-.136),mat('brass'),seg=6)
        ring(b,.012,.003,(x,-.041,-.108),mat('rubber'),seg=24)
    b.box((.108,.0015,.030),(0,-.0865,.031),mat('ink enamel'),.002)
    return b


def intercom():
    b=B()
    b.box((.176,.012,.330),(0,-.006,0),mat('dark steel'),.007)
    b.box((.163,.007,.316),(0,-.0155,0),mat('rubber'),.006)
    # Sloped edges and a proper hood distinguish this from a flat wall box.
    polygon(b,[(-.081,-.047),(-.066,-.076),(.066,-.076),(.081,-.047),(.081,-.021),(-.081,-.021)],
            .302,mat('repaired blue enamel'),pos=(0,0,-.151),bevel=.002)
    b.box((.166,.072,.012),(0,-.052,.157),mat('steel'),.003)
    frame(b,.113,.118,.008,.008,-.080,.054,mat('steel'),r=.012)
    b.box((.098,.003,.103),(0,-.079,.054),mat('ink'),.002)
    for i in range(6):
        for j in range(6):
            # Individual recessed grille apertures with a visible return rim.
            ring(b,.0032,.0009,(-.0375+i*.015,-.083,.0165+j*.015),mat('steel'),axis='Y',seg=12)
    b.lathe([(0,0),(.020,0),(.024,.006),(.022,.012),(.016,.018),(0,.018)],
            (0,-.078,-.078),mat('dark steel'),seg=32,rot=FRONT)
    b.cyl(.014,.007,(0,-.099,-.078),mat('ochre enamel'),seg=32,axis='Y')
    for x in [-.030,.030]:b.box((.006,.030,.048),(x,-.090,-.078),mat('steel'),.002)
    b.box((.081,.0015,.026),(0,-.0785,-.119),mat('warm enamel'),.002)
    for x in [-.064,.064]:
        for z in [-.128,.127]:bolt(b,(x,-.078,z),.0035)
    b.lathe([(0,0),(.010,0),(.015,.006),(.015,.016),(.009,.023),(0,.023)],
            (0,-.038,-.174),mat('brass'),seg=6)
    b.tube(rounded_path([(0,-.038,-.174),(0,-.041,-.207),(.041,-.038,-.244),
                        (.044,-.028,-.306)]),.0045,mat('rubber'),seg=12)
    b.box((.042,.007,.038),(.044,-.0075,-.306),mat('dark steel'),.002)
    b.box((.012,.025,.012),(.044,-.021,-.306),mat('steel'),.002)
    return b


def bleed_cap():
    b=B();brass=mat('brass')
    # This inlet touches the underside of the existing collector, not its wall.
    b.cyl(.008,.039,(.093,-.16,.194),brass,seg=20)
    b.lathe([(0,0),(.014,0),(.021,.006),(.021,.024),(.015,.031),(0,.031)],
            (.093,-.16,.154),brass,seg=6)
    b.cyl(.008,.053,(.093,-.186,.166),mat('steel'),seg=16,axis='Y')
    b.tube([(.067,-.206,.166),(.119,-.206,.166)],.004,mat('ochre enamel'),seg=12)
    b.cyl(.006,.034,(.093,-.16,.129),brass,seg=16)
    b.lathe([(0,0),(.013,0),(.016,.006),(.016,.021),(.012,.026),(0,.026)],
            (.093,-.16,.100),mat('steel'),seg=24)
    for i in range(9):
        a=i/8;center=(.109+.043*math.sin(math.pi*a),-.16,.128-.023*a)
        rot=Matrix.Rotation(math.pi/2 if i%2 else 0,3,'Z')
        pts=[Vector(center)+rot@Vector((.004*math.cos(j*2*math.pi/16),0,.006*math.sin(j*2*math.pi/16))) for j in range(17)]
        b.tube(pts,.00085,mat('steel'),seg=6)
    return b


def motor_bond():
    b=B()
    start=Vector((.935,-.258,.197));end=Vector((.78,-.215,.172))
    for p in [start,end]:
        b.box((.020,.028,.0025),tuple(p+Vector((0,0,.003))),mat('bond copper'),.003)
        bolt(b,tuple(p+Vector((0,0,.0045))),.004,axis='Z')
    # Two interwoven bundles bow between supported lugs; no floating ribbon.
    for row in range(8):
        pts=[]
        for j in range(41):
            t=j/40;p=start.lerp(end,t)
            p.y+=(row-3.5)*.0011+math.sin(t*math.pi*12+row*.8)*.0007
            p.z+=.007+math.sin(t*math.pi)*.022
            pts.append(p)
        b.tube(pts,.00065,mat('bond copper'),seg=6)
    # Motor connection continues into a seated terminal with compression gland.
    b.box((.082,.064,.087),(1.66,-.182,.214),mat('ink enamel'),.006)
    for x in [1.638,1.682]:bolt(b,(x,-.218,.230),.003)
    b.lathe([(0,0),(.011,0),(.016,.006),(.016,.019),(.011,.027),(0,.027)],
            (1.66,-.182,.258),mat('brass'),seg=6)
    b.tube(rounded_path([(1.324,-.13,.385),(1.367,-.143,.385),
                        (1.46,-.15,.414),(1.59,-.17,.380),(1.66,-.182,.285)]),
           .007,mat('rubber'),seg=14)
    for x in [1.335,1.345,1.355]:ring(b,.011,.003,(x,-.13,.385),mat('rubber'),axis='X',seg=20)
    return b


def inspection_tag():
    b=B()
    # Wire loops around the existing handwheel, then passes through the eyelet.
    b.tube(rounded_path([(-.187,-.194,.465),(-.195,-.179,.465),(-.182,-.164,.465),
                        (-.163,-.175,.457),(-.113,-.226,.390),(-.109,-.235,.357)]),
           .0011,mat('steel'),seg=8)
    pts=[(-.149,.353),(-.138,.366),(-.080,.366),(-.069,.353),(-.069,.233),(-.149,.233)]
    polygon(b,pts,.0014,mat('paper'),pos=(0,-.235,0),rot=FRONT,bevel=.00025)
    ring(b,.004,.001,( -.109,-.2367,.355),mat('brass'),axis='Y',seg=20)
    b.box((.019,.009,.015),(-.166,-.194,.451),mat('red'),.003)
    for z in [.301,.288,.274]:b.box((.056,.0005,.0013),(-.109,-.2368,z),mat('ink'),.0001)
    b.box((.060,.0005,.012),(-.109,-.2368,.331),mat('oxide enamel'),.001)
    return b


def strainer(floors):
    finish=bpy.data.objects[floors['plant_header']]
    x,y=-3.6231,16.35
    # Cut only the finish above the retained slab; the original floor footprint
    # and slab remain untouched. Real gaps between grate bars open onto the bed.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,-.006))
    cutter=bpy.context.object;cutter.dimensions=(.286,.286,.040)
    bpy.context.view_layer.objects.active=cutter;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=finish.modifiers.new('Wet-service strainer recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=finish
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);project_uv(finish)
    b=B();m=mat('steel')
    b.box((.280,.280,.002),(0,0,-.019),mat('dark steel'),.002)
    for axis in [0,1]:
        for sign in [-1,1]:
            dim=(.010,.278,.017) if axis==0 else (.278,.010,.017)
            pos=(sign*.135,0,-.0105) if axis==0 else (0,sign*.135,-.0105)
            b.box(dim,pos,m,.001)
    for i in range(9):
        b.box((.246,.012,.007),(0,-.112+i*.028,-.0035),m,.0015,seg=3)
    for xx in [-.122,.122]:
        b.box((.010,.260,.008),(xx,0,-.008),mat('dark steel'),.001)
    for xx in [-.129,.129]:
        for yy in [-.129,.129]:bolt(b,(xx,yy,-.003),.0035,axis='Z')
    b.box((.054,.009,.003),(0,.117,-.008),mat('dark steel'),.001)
    ob=add(b,'Wet-service recessed floor strainer','FC | Infrastructure details',pos=(x,y,0),
           target='Floor_plant_header',anchors=[(-.105,-.105,-.020),(.105,.105,-.020)],
           direction=(0,0,-1),kind='floor',family='open lift-out strainer, flange and retained recessed receiver')
    return ob


def install(mounted,walls,floors,wall_pos):
    records=[]
    def record(number,idea,objects):
        records.append({'id':number,'idea':idea,'objects':[o.name for o in objects],
                        'scope':'Static authored construction; runtime operation unverified.'})
    surface('bond copper','#AA7752',.58,.78,.00015,6,.10)
    outlet=mounted(receptacles(),'Bench weatherproof receptacle bank','Wall_W-2.2_0_1.2',
                   (3.63,-.008,1.13),'FC | Infrastructure details','gasketed industrial sockets, recessed contacts, plug and hinged cover')
    sealed=mounted(receptacles(True),'Clean sealed service receptacles','Wall_S18.0_0_1.2',
                   (-3.03,-.004,.72),'FC | Infrastructure details','sealed wash-down socket covers and machined mounting flange')
    label('230V',outlet.matrix_world@Vector((0,-.0522,.057)),.012,material='white ink',normal=(1,0,0),parent=outlet.name)
    record(1,'Weatherproof sockets',[outlet,sealed])

    lead=add(retained_lead(),'Bench retained work lead','FC | Infrastructure details',pos=outlet.location,
             normal=(1,0,0),parent=outlet.name,family='moulded strain boot, sagged lead and supported retaining hook')
    support(lead,[walls['Wall_W-2.2_0_1.2']],
            [lead.matrix_world@Vector((.305,0,-.012))],(-1,0,0),'wall')
    record(2,'Retained work lead',[lead])

    saddles=[];pipe=B();centres=[]
    for z in [1.37,1.90,2.54,3.31]:
        ob=mounted(conduit_saddle(),'Bench conduit saddle '+str(z),'Wall_W-2.2_0_1.2',
                   (4.04,-.004,z),'FC | Infrastructure details','saddle clip with folded foot and socket screws')
        saddles.append(ob);centres.append(ob.matrix_world@Vector((0,-.044,0)))
    socket_top=outlet.matrix_world@Vector((.100,-.037,.075))
    path=[socket_top,socket_top+Vector((.015,0,.046)),centres[0],*centres[1:]]
    ladder=bpy.data.objects['FC | Staging cable ladder']
    entry=ladder.matrix_world@Vector((1.0,0,.024))
    end=Vector((centres[-1].x,centres[-1].y,entry.z))
    path.extend([end,Vector((entry.x+.05,entry.y+.11,entry.z)),entry])
    pipe.tube(rounded_path(path),.008,mat('steel'),seg=16)
    for p in centres:
        ring(pipe,.011,.003,tuple(p+Vector((0,0,-.015))),mat('steel'),seg=24)
    # Cast inspection tee with a removable hex plug, directly on the riser.
    p=centres[2]
    pipe.cyl(.013,.033,tuple(p+Vector((0,0,-.0165))),mat('steel'),seg=24)
    pipe.cyl(.009,.018,tuple(p),mat('steel'),seg=20,axis='X')
    pipe.cyl(.013,.006,tuple(p+Vector((.016,0,0))),mat('brass'),seg=6,axis='X')
    riser=add(pipe,'Bench clipped galvanised conduit','FC | Infrastructure details',parent=outlet.name,
              family='connected service riser, separate saddles and compression collars')
    record(3,'Clipped conduit',[riser,*saddles])

    junction=mounted(junction_box(),'Process distribution junction box','Wall_E16.4_0_7',
                     (-.78,-.008,1.07),'FC | Infrastructure details','gasketed removable junction plate, screws and cable glands')
    label('JB / 04',junction.matrix_world@Vector((0,-.088,.031)),.014,
          normal=(-1,0,0),parent=junction.name)
    feed=B();feed.tube(rounded_path([(-.046,-.041,-.137),(-.046,-.061,-.21),
                       (-.29,-.057,-.25),(-.70,-.054,-.16),(-.77,-.055,.90),(-.77,-.092,1.01)]),
                      .005,mat('rubber'),seg=12)
    for z in [.15,.58]:
        feed.box((.055,.006,.046),(-.77,-.015,z),mat('dark steel'),.003)
        feed.box((.014,.037,.013),(-.77,-.0365,z),mat('steel'),.002)
    routed=add(feed,'Process retained junction leads','FC | Infrastructure details',pos=junction.location,
               normal=(-1,0,0),parent=junction.name,family='machined glands and clipped cabinet supply lead')
    support(routed,[walls['Wall_E16.4_0_7']]*2,
            [routed.matrix_world@Vector((-.77,-.012,z)) for z in [.15,.58]],(1,0,0),'wall')
    record(4,'Junction box and glands',[junction,routed])

    drive=bpy.data.objects['FC | Freight gate track and motor']
    bond=add(motor_bond(),'Freight motor bond and strain relief','FC | Infrastructure details',
             pos=drive.matrix_world.translation,normal=(-1,0,0),parent=drive.name,
             family='braided copper earth bond, bolted lugs and retained motor supply')
    record(5,'Motor earth bond and strain relief',[bond])

    call=mounted(intercom(),'Reactor local call intercom','Wall_E17.0_0_21',
                 (-.465,-.004,1.50),'FC | Infrastructure details','formed intercom, inset grille, guarded call button and connected entry')
    support(call,[walls['Wall_E17.0_0_21']]*2,
            [call.matrix_world@Vector((0,0,0)),call.matrix_world@Vector((.044,-.004,-.306))],(1,0,0),'wall')
    label('CALL / R02',call.matrix_world@Vector((0,-.0801,-.119)),.011,
          normal=(-1,0,0),material='ink',parent=call.name)
    record(6,'Reactor intercom',[call])

    manifold=bpy.data.objects['FC | Staging service-air manifold']
    cap=add(bleed_cap(),'Staging captive bleed cap','FC | Infrastructure details',pos=manifold.location,
            normal=(0,-1,0),parent=manifold.name,family='connected brass bleed petcock, machined cap and captive chain')
    record(7,'Chained bleed cap',[cap])
    record(8,'Recessed floor strainer',[strainer(floors)])
    cloth=bpy.data.objects['FC | Folded blue wiping cloth']
    cloth['fc_asset_family']='folded textile with stitched hems, uneven folds and restrained fraying'
    record(9,'Maintenance cloth detail',[cloth])

    recess=bpy.data.objects['FC | Recess service manifold']
    tag=add(inspection_tag(),'Purge valve inspection tag and seal','FC | Infrastructure details',
            pos=recess.location,normal=(1,0,0),parent=recess.name,
            family='tied physical inspection card, eyelet, wire and tamper seal')
    label('CHECK B',tag.matrix_world@Vector((-.109,-.238,.330)),.009,
          normal=(1,0,0),parent=tag.name)
    record(10,'Inspection tag and tamper seal',[tag])
    assert [r['id'] for r in records]==list(range(1,11))
    return records
