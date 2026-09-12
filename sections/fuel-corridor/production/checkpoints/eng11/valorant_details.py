"""Original reference-led construction and prop assemblies, executed by build.py.

No neighboring meshes are imported. Coordinates are metric. Supported groups
carry explicit anchors, evaluated independently by validate.py.
"""

def local_wall_root(name,origin,heading=0,anchor_z=1.8,face=0):
    global PAR
    c,s=math.cos(heading),math.sin(heading)
    point=(origin[0]-s*face,origin[1]+c*face,anchor_z)
    return root(name,'wall',[point],(-s,c,0))

def place_wall_group(parent,origin,heading):
    parent.location=(origin[0],origin[1],0);parent.rotation_euler.z=heading

def gauge(name,x,y,z,r=.065):
    rod(name+'_body',(x,y+.035,z),(x,y-.025,z),r,'darksteel',48)
    rod(name+'_dial',(x,y-.026,z),(x,y-.029,z),r*.86,'ivory',48)
    for i in range(11):
        a=math.radians(225-i*27)
        rod(name+'_tick',(x+math.cos(a)*r*.66,y-.031,z+math.sin(a)*r*.66),(x+math.cos(a)*r*.78,y-.031,z+math.sin(a)*r*.78),.0015,'ink',6)
        if i%2==0:text_obj(name+'_scale',str(i),(x+math.cos(a)*r*.50,y-.030,z+math.sin(a)*r*.50-.0035),r*.135,'ink')
    text_obj(name+'_units','bar',(x,y-.030,z-r*.23),r*.15,'ink')
    rod(name+'_needle',(x,y-.033,z),(x+r*.62*math.cos(math.radians(36)),y-.033,z+r*.62*math.sin(math.radians(36))),.0017,'ink',8)
    rod(name+'_pivot',(x,y-.034,z),(x,y-.036,z),r*.06,'steel',16)

def annular_x(name,x0,x1,y,z,outer,inner,material,n=64):
    vv=[(xx,y+math.cos(i*math.tau/n)*r,z+math.sin(i*math.tau/n)*r) for xx,r in [(x0,outer),(x1,outer),(x1,inner),(x0,inner)] for i in range(n)]
    ff=[]
    for j in range(4):
        for i in range(n):ff.append((j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i))
    o=mesh(name,vv,ff,material)
    for i,p in enumerate(o.data.polygons):p.use_smooth=i//n in [0,2]
    return o

def small_case(name,loc,dimensions=(.38,.24,.18),material='teal'):
    x,y,z=loc;w,d,h=dimensions
    box(name+'_body',(x,y,z+h*.46),(w,d,h*.92),material,.018)
    box(name+'_lid',(x,y,z+h*.93),(w+.012,d+.012,h*.14),'darksteel',.009)
    for xx in [-w*.31,w*.31]:
        box(name+'_latch',(x+xx,y-d/2-.006,z+h*.78),(.041,.019,.060),'ochre',.005)
    tube(name+'_handle',[(x-.08,y,z+h),(x-.08,y,z+h+.035),(x+.08,y,z+h+.035),(x+.08,y,z+h)],.012,'rubber')
    for a in [-1,1]:
        for b in [-1,1]:box(name+'_corner',(x+a*(w*.5-.025),y+b*(d*.5-.022),z+h*.22),(.055,.052,h*.32),'darksteel',.009)
    box(name+'_rolled_base_rim',(x,y,z+.013),(w+.008,d+.008,.026),'teal_light',.004)
    for xx in [-w*.31,w*.31]:
        rod(name+'_latch_pin',(x+xx-.020,y-d/2-.018,z+h*.87),(x+xx+.020,y-d/2-.018,z+h*.87),.005,'steel',16)
        box(name+'_latch_keeper',(x+xx,y-d/2-.016,z+h*.59),(.030,.018,.024),'steel',.003)
        for part in [-1,0,1]:rod(name+'_hinge_knuckle',(x+xx+part*.019-.007,y+d/2+.004,z+h*.88),(x+xx+part*.019+.007,y+d/2+.004,z+h*.88),.009,'steel',16)
    for xx in [-w*.42,w*.42]:box(name+'_pressed_stiffener',(x+xx,y-d/2-.004,z+h*.47),(.015,.015,h*.57),'teal_light',.004)
    box(name+'_identity_plate',(x,y-d/2-.0025,z+h*.42),(.17,.005,.040),'paper',.002)
    text_obj(name+'_kit_type','TOOLS / 04',(x,y-d/2-.0055,z+h*.395),.014,'ink')
    for side in [-1,1]:
        for xx in [-w*.40,-w*.29,w*.36]:box(name+'_local_lid_wear',(x+xx,y+side*(d/2+.006),z+h*.96),(.019,.002,.005),'steel',0)

def folded_cloth(name,x,y,z,w=.24,d=.19):
    vv=[];ff=[]
    for j in range(15):
        for i in range(21):
            u,v=i/20,j/14
            fold=.017*(.5+.5*math.cos(u*math.pi*5+v*1.7))**2*math.sin(math.pi*v)+.0025*math.sin(u*17+v*9)*math.sin(math.pi*v)
            vv.append((x-w/2+u*w+.004*math.sin(v*8.3),y-d/2+v*d+.003*math.sin(u*9),z+.004+fold))
    for j in range(14):
        for i in range(20):q=j*21+i;ff.append((q,q+1,q+22,q+21))
    o=mesh(name,vv,ff,'cotton');sol=o.modifiers.new('Woven folded thickness','SOLIDIFY');sol.thickness=.004;sol.offset=-1
    for p in o.data.polygons:p.use_smooth=True

def laid_glove(name,x,y,mirror=1,angle=0):
    # One continuous sewn silhouette, with unequal finger lengths and an inset thumb web.
    points=[(-.043,-.084),(.044,-.084),(.047,-.044),(.050,-.003),(.076,.031),(.083,.050),(.077,.062),(.066,.064),(.051,.045),(.042,.032),
            (.043,.092),(.040,.112),(.029,.119),(.020,.113),(.018,.064),(.014,.065),(.013,.130),(.005,.141),(-.004,.141),(-.012,.131),(-.013,.066),(-.017,.064),
            (-.020,.121),(-.028,.133),(-.037,.131),(-.043,.119),(-.042,.059),(-.047,.054),(-.052,.095),(-.060,.104),(-.068,.099),(-.071,.086),(-.060,.029),(-.054,-.030)]
    c,s=math.cos(angle),math.sin(angle)
    def xy(u,v):return (x+c*u*mirror-s*v,y+s*u*mirror+c*v)
    def inside(u,v,contour):
        answer=False
        for a,b in zip(contour,contour[1:]+contour[:1]):
            if (a[1]>v)!=(b[1]>v) and u<(b[0]-a[0])*(v-a[1])/(b[1]-a[1])+a[0]:answer=not answer
        return answer
    def height(u,v):
        q=Vector((u,v));distance=10
        for aa,bb in zip(points,points[1:]+points[:1]):
            a,b=Vector(aa),Vector(bb);d=b-a;t=max(0,min(1,(q-a).dot(d)/d.length_squared));distance=min(distance,(q-a-d*t).length)
        dome=1-math.exp(-distance/.0045)
        return .908+dome*(.014+.0025*math.sin(v*142+u*27))
    from mathutils.geometry import delaunay_2d_cdt
    grid=[Vector(p) for p in points]
    for j in range(47):
        for i in range(33):
            u,v=-.076+i*.005,-.085+j*.005
            if inside(u,v,points):grid.append(Vector((u,v)))
    vv,ee,ff,*_=delaunay_2d_cdt(grid,[],[list(range(len(points)))],1,.0000005,False)
    verts=[(*xy(v.x,v.y),height(v.x,v.y)) for v in vv]+[(*xy(v.x,v.y),.906) for v in vv];nn=len(vv)
    faces=[tuple(f if mirror>0 else reversed(f)) for f in ff]
    faces += [tuple(i+nn for i in (reversed(f) if mirror>0 else f)) for f in ff]
    edge_count={}
    for f in ff:
        for a,b in zip(f,f[1:]+f[:1]):key=tuple(sorted((a,b)));edge_count.setdefault(key,[]).append((a,b))
    for value in edge_count.values():
        if len(value)==1:
            a,b=value[0];face=(b,a,a+nn,b+nn);faces.append(face if mirror>0 else tuple(reversed(face)))
    ob=mesh(name+'_sewn_shell',verts,faces,'glove');ob.data.materials.append(M['glove_leather'])
    patch=[(-.034,-.039),(.035,-.041),(.040,-.014),(.022,.044),(-.029,.042),(-.043,.017)]
    for k,f in enumerate(ff):
        center=sum((vv[i] for i in f),Vector((0,0)))/len(f)
        ob.data.polygons[k].use_smooth=True
        if inside(center.x,center.y,patch):ob.data.polygons[k].material_index=1
    for side in [-1,1]:
        for j in range(7):
            u=side*.034;v=-.034+j*.010
            aa=xy(u,v);bb=xy(u,v+.0035);rod(name+'_sewn_stitch',(*aa,height(u,v)+.0003),(*bb,height(u,v+.0035)+.0003),.0005,'cloth',6)
    for j in range(4):
        v=-.063+j*.005
        tube(name+'_cuff_weave',[(*xy(u,v),height(u,v)+.0003) for u in [-.038+k*.004 for k in range(20)]],.0006,'rubber')
    for u,v,w in [(-.030,.070,.013),(-.002,.083,.014),(.029,.074,.012),(-.058,.059,.011)]:
        tube(name+'_finger_fold',[(*xy(u-w/2+k*w/6,v+k*.0005),height(u-w/2+k*w/6,v+k*.0005)+.0002) for k in range(7)],.00045,'rubber')

def ellipsoid(name,loc,dimensions,material):
    rx,ry,rz=[d/2 for d in dimensions];n,m=24,12
    vertices=[(loc[0],loc[1],loc[2]+rz)]
    vertices += [(loc[0]+rx*math.sin(j*math.pi/m)*math.cos(i*math.tau/n),loc[1]+ry*math.sin(j*math.pi/m)*math.sin(i*math.tau/n),loc[2]+rz*math.cos(j*math.pi/m)) for j in range(1,m) for i in range(n)]
    vertices.append((loc[0],loc[1],loc[2]-rz));last=len(vertices)-1
    faces=[(0,1+i,1+(i+1)%n) for i in range(n)]
    for j in range(m-2):
        for i in range(n):a=1+j*n+i;b=1+j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
    faces += [(last,1+(m-2)*n+(i+1)%n,1+(m-2)*n+i) for i in range(n)]
    ob=mesh(name,vertices,faces,material)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def trolley(x=2.65,y=12.32):
    carrier=root('Long_cask_carrier','floor',[(x+sx*.59,y+sy*.32,0) for sx in [-1,1] for sy in [-1,1]])
    carrier['handling_role']='Single current reactor cartridge, preloaded, closed and parked'
    carrier['design_envelope_m']=[1.60,.90,1.30]
    for sx in [-1,1]:
        for sy in [-1,1]:
            xx=x+sx*.59;yy=y+sy*.32
            rod('Rubber_tyre',(xx,yy-.048,.12),(xx,yy+.048,.12),.12,'rubber',48)
            for a in [-1,1]:rod('Caster_hub',(xx,yy+a*.049,.12),(xx,yy+a*.055,.12),.065,'steel',32)
            rod('Caster_axle',(xx,yy-.081,.12),(xx,yy+.081,.12),.018,'darksteel',16)
            for sy2 in [-1,1]:
                beam('Pressed_caster_fork',(xx,yy+sy2*.070,.12),(xx+.035,yy+sy2*.070,.27),.043,.026,'steel')
            box('Caster_bridge',(xx+.035,yy,.267),(.093,.17,.03),'steel',.006)
            rod('Caster_swivel_race',(xx+.035,yy,.277),(xx+.035,yy,.326),.050,'darksteel',32)
            box('Caster_mount_plate',(xx+.035,yy,.333),(.16,.16,.016),'steel')
            if sx<0:
                rod('Parking_brake_pivot',(xx-.025,yy-.067,.215),(xx-.025,yy+.067,.215),.012,'steel',24)
                pedal=box('Orange_brake_pedal',(xx-.085,yy,.222),(.14,.094,.018),'ochre',.008);pedal.rotation_euler.y=.18
                box('Brake_shoe',(xx-.037,yy,.235),(.050,.072,.028),'darksteel',.006)
    for sy in [-1,1]:
        # Open drainage/handling slots formed into the folded chassis web.
        for lo,hi in [(-.77,-.545),(-.415,.415),(.545,.77)]:box('Chassis_web_segment',(x+(lo+hi)/2,y+sy*.40,.404),(hi-lo,.045,.125),'teal')
        for xx in [-.48,.48]:
            for zz in [.363,.446]:box('Chassis_slot_ligament',(x+xx,y+sy*.40,zz),(.13,.045,.041),'teal',.002)
        for z in [.346,.462]:box('Chassis_folded_flange',(x,y+sy*.368,z),(1.54,.105,.020),'teal')
        for lo,hi in [(-.8,-.55),(-.40,.40),(.55,.8)]:box('Carrier_rubber_edge',(x+(lo+hi)/2,y+sy*.438,.402),(hi-lo,.024,.061),'rubber',.008)
    for xx in [-.70,-.43,.43,.70]:box('Chassis_crossmember',(x+xx,y,.403),(.06,.84,.10),'darksteel')
    box('Carrier_inspection_ledge',(x,y-.31,.475),(1.37,.25,.012),'teal')
    z=.76
    for xx in [-.43,.43]:
        box('Cradle_bolted_foot',(x+xx,y,.476),(.21,.62,.030),'teal')
        for sy in [-1,1]:
            beam('Cradle_trestle_leg',(x+xx,y+sy*.26,.49),(x+xx,y+sy*.12,.626),.065,.065,'teal')
            bolt('Cradle_foot_bolt',(x+xx-.075,y+sy*.24,.499),(0,0,1),.013)
        outline=[(y+math.cos(a)*r,z+math.sin(a)*r) for r,angles in [(.163,[math.pi*1.08+i*math.pi*.84/20 for i in range(21)]),(.21,[math.pi*1.92-i*math.pi*.84/20 for i in range(21)])] for a in angles]
        vv=[(x+xx+t,yy,zz) for t in [-.039,.039] for yy,zz in outline];n=len(outline)
        mesh('Curved_contact_saddle',vv,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'teal_light')
    body=lathe_x('Current_reactor_cartridge',[(x-.590,.146),(x-.575,.155),(x+.575,.155),(x+.590,.146)],y,z,'cartridge_paint')
    uv=body.data.uv_layers.new(name='Cylindrical_enamel_metres')
    for poly in body.data.polygons:
        values=[]
        for li in poly.loop_indices:
            vv=body.data.vertices[body.data.loops[li].vertex_index].co
            values.append((li,(vv.x-x)/.85,(math.atan2(vv.z-z,vv.y-y)%math.tau)/math.tau))
        wrap=max(q[2] for q in values)-min(q[2] for q in values)>.5
        for li,u,v in values:uv.data[li].uv=(u,(v+1 if wrap and v<.5 else v)*1.15)
    for side in [-1,1]:
        xx=x+side*.605
        annular_x('Current_cask_end_closure',xx-.0175,xx+.0175,y,z,.170,.143,'steel')
        rod('Closure_dark_face',(xx+side*.011,y,z),(xx+side*.016,y,z),.146,'teal',48)
        torus('Closure_seal',(xx+side*.014,y,z),.145,.003,'rubber',(0,math.pi/2,0))
        rod('Closure_lock',(xx+side*.009,y,z),(xx+side*.017,y,z),.075,'darksteel',32)
        for i in range(8):
            a=i*math.tau/8
            rod('Closure_bolt',(xx+side*.011,y+math.cos(a)*.133,z+math.sin(a)*.133),(xx+side*.017,y+math.cos(a)*.133,z+math.sin(a)*.133),.010,'steel',6)
        torus('Machined_closure_lip',(xx+side*.012,y,z),.153,.004,'teal_light',(0,math.pi/2,0))
    for xx in [-.43,.43]:
        rod('Orange_cartridge_band',(x+xx-.032,y,z),(x+xx+.032,y,z),.163,'ochre',64)
        box('Latch_foot',(x+xx,y-.160,z),(.088,.024,.105),'teal')
        for e in [-1,1]:box('Latch_cheek',(x+xx+e*.034,y-.184,z),(.014,.028,.107),'steel')
        for zz in [z-.031,z+.035]:rod('Latch_pivot',(x+xx-.044,y-.185,zz),(x+xx+.044,y-.185,zz),.009,'steel',24)
        box('Closed_latch_lever',(x+xx,y-.206,z),(.050,.018,.088),'steel',.004)
        box('Orange_latch_grip',(x+xx,y-.214,z-.024),(.052,.016,.031),'ochre',.004)
        box('Lifting_eye_foot',(x+xx,y,z+.169),(.11,.08,.016),'steel')
        torus('Lifting_eye',(x+xx,y,z+.205),.032,.010,'steel',(math.pi/2,0,0))
    for sy in [-1,1]:tube('Orange_push_handle',[(x-.758,y+sy*.31,.42),(x-.758,y+sy*.31,1.18),(x-.738,y+sy*.285,1.22)],.024,'ochre')
    rod('Handle_grip',(x-.738,y-.285,1.22),(x-.738,y+.285,1.22),.027,'rubber',32)
    rod('Handle_mid_crossbar',(x-.758,y-.31,.86),(x-.758,y+.31,.86),.018,'ochre')
    # Signed inspection card is physically tethered to the handle crossbar.
    torus('Inspection_ring',(x-.758,y-.235,.85),.025,.004,'steel',(math.pi/2,0,0))
    tube('Card_tether',[(x-.758,y-.235,.831),(x-.744,y-.235,.806),(x-.743,y-.235,.789)],.003,'rubber')
    box('Inspection_card',(x-.744,y-.236,.731),(.11,.008,.12),'paper',.003)
    text_obj('Card_print','CHECKED\n07 / SHIFT B',(x-.744,y-.241,.749),.016,'ink')
    text_obj('Cask_identity','FC-07',(x-.13,y-.1555,z-.027),.048,'ink')
    box('Cask_inventory_plate',(x+.17,y-.1555,z-.012),(.135,.002,.063),'teal',0)
    text_obj('Cask_inventory_number','07 / B',(x+.17,y-.157,z-.026),.022,'ivory')
    for yy in [-1,1]:
        for xx in [-.66,.66]:
            box('Frame_corner_plate',(x+xx,y+yy*.424,.408),(.15,.005,.102),'teal_light',.002)
            for dxx in [-.046,.046]:bolt('Frame_rivet',(x+xx+dxx,y+yy*.431,.411),(0,yy,0),.007)
    for xx in [-.48,-.13,.28,.57]:
        for side in [-1,1]:box('Frame_handling_chip',(x+xx,y+side*.412,.473),(.043,.012,.0018),'steel',0)
    for xx,aa,span in [(-.36,2.89,.075),(.05,3.70,.048)]:
        coordinates=[(xx,aa),(xx+span*.18,aa+.03),(xx+span,aa+.08),(xx+span*.84,aa+.115),(xx+.018,aa+.07)]
        mesh('Barrel_painted_rub',[(x+t,y+math.cos(a)*.1557,z+math.sin(a)*.1557) for t,a in coordinates],[(0,1,2,3,4)],'wall_light')
    for i in range(5):box('Carrier_local_contact_wear',(x-.5+i*.18,y-.424,.457),(.048,.004,.004),'chip',0)
    for sy in [-1,1]:
        for xx in [-.59,.59]:
            for side in [-1,1]:
                # Twin hub circles, locking pawl and toe pad distinguish casters from disks.
                torus('Caster_hub_ring',(x+xx,y+sy*.32+side*.056,.12),.050,.006,'darksteel',(math.pi/2,0,0))
                rod('Wheel_axle_nut',(x+xx,y+sy*.32+side*.054,.12),(x+xx,y+sy*.32+side*.066,.12),.019,'steel',6)
        beam('Brake_linkage',(x-.645,y+sy*.32,.24),(x-.696,y+sy*.32,.286),.025,.032,'steel')
        box('Toe_lock_face',(x-.687,y+sy*.32,.285),(.13,.102,.023),'ochre',.003)
        for t in [-.039,-.013,.013,.039]:box('Brake_tread_rib',(x-.687+t,y+sy*.32,.30),(.009,.074,.008),'rubber',.001)
    for xx in [-.43,.43]:
        for side in [-1,1]:
            rod('Latch_retention_pin',(x+xx-.040,y-.216,z+side*.026),(x+xx+.040,y-.216,z+side*.026),.005,'steel',12)
        torus('Latch_safety_ring',(x+xx+.043,y-.224,z+.028),.013,.003,'steel',(math.pi/2,0,0))
        for sy in [-1,1]:rod('Cradle_fillet_weld',(x+xx-.032,y+sy*.247,.499),(x+xx+.032,y+sy*.247,.499),.0035,'steel',12)
    # Uneven local rubs follow the painted shell's handling direction.
    for xx,aa,width in [(-.39,2.64,.042),(.39,3.63,.034)]:
        pts=[(xx,aa),(xx+width*.19,aa-.035),(xx+width,aa+.02),(xx+width*.88,aa+.045),(xx+width*.15,aa+.016)]
        mesh('Cartridge_handling_paint',[(x+t,y+math.cos(a)*.1559,z+math.sin(a)*.1559) for t,a in pts],[(0,1,2,3,4)],'wall_patch')
    for xx in [-.45,-.14,.14,.45]:
        box('Deck_pressed_seam',(x+xx,y-.32,.482),(.013,.19,.004),'darksteel',.001)
    text_obj('Frame_brake_hint','PARK',(x-.60,y-.451,.365),.025,'ivory')

def pipework():
    # Upper supported service run stays above the 3m bypass opening.
    root('Slice_utility_header','wall',[(1.75,13.2,3.24),(3.75,13.2,3.24)],(0,1,0))
    tube('Bay_air_header',[(1.30,12.94,3.24),(4.19,12.94,3.24),(4.26,12.94,3.17),(4.26,12.94,2.48),(4.20,12.94,2.42),(3.46,12.94,2.42),(3.40,13.04,2.35),(3.40,13.04,2.25)],.05,'steel')
    rod('Header_terminal_cap',(1.295,12.94,3.24),(1.31,12.94,3.24),.055,'teal')
    for xx in [1.75,3.75]:
        box('Header_backplate',(xx,13.18,3.24),(.15,.04,.28),'teal')
        box('Header_offset_support',(xx,13.06,3.185),(.08,.24,.035),'steel')
        torus('Header_pipe_clip',(xx,12.94,3.24),.057,.009,'ochre',(0,math.pi/2,0))
    for xx in [2.0,3.45]:
        rod('Header_union',(xx-.03,12.94,3.24),(xx+.03,12.94,3.24),.075,'teal_light')
        for i in range(6):
            a=math.tau*i/6;rod('Header_union_bolt',(xx-.038,12.94+math.cos(a)*.061,3.24+math.sin(a)*.061),(xx+.038,12.94+math.cos(a)*.061,3.24+math.sin(a)*.061),.006,'steel',6)

def utility_station(name,origin,heading=0,inlet_z=2.25):
    service_recess=name=='Service_air_station'
    # The recess has raised structural trim. Three steel spacers bridge it from
    # clear panel anchor locations; the complete service board sits in front.
    par=local_wall_root(name,origin,heading,1.80,face=.20 if service_recess else 0)
    if service_recess:
        for xx,zz in [(-.30,1.64),(.30,1.64),(0,1.80)]:
            box(name+'_mounting_spacer',(xx,.10,zz),(.075,.20,.075),'steel',.003)
            box(name+'_spacer_wall_foot',(xx,.194,zz),(.115,.012,.115),'teal_light',.002)
    box(name+'_mounting_frame',(0,-.025,1.77),(.84 if service_recess else 1.04,.05,1.11),'teal')
    for xx in ([-.36,.36] if service_recess else [-.44,.44]):
        for zz in [1.32,2.22]:bolt(name+'_wall_anchor',(xx,-.058,zz))
    # Pipe rises at left, traverses the isolator and regulator, then drops to coupler.
    inlet=[(-.20,-.16,inlet_z),(-.20,-.16,1.98)] if service_recess else [(-.40,-.16,inlet_z)]
    tube(name+'_service_pipe',inlet+[(-.40,-.16,1.88),(-.32,-.16,1.80),(.04,-.16,1.80),(.34,-.16,1.80),(.39,-.16,1.75),(.39,-.16,1.53)],.042,'steel')
    for xx in [-.36,.34]:
        box(name+'_pipe_standoff',(xx,-.10,1.80),(.04,.16,.14),'teal_light')
        torus(name+'_clip',(xx,-.16,1.80),.047,.007,'steel',(0,math.pi/2,0))
    rod(name+'_isolator_body',(-.30,-.16,1.80),(-.15,-.16,1.80),.065,'teal',32)
    rod(name+'_valve_stem',(-.225,-.16,1.80),(-.225,-.33,1.80),.014,'brass')
    torus(name+'_handwheel',(-.225,-.33,1.80),.095,.010,'ochre',(math.pi/2,0,0))
    for i in range(3):
        a=i*math.tau/3;rod(name+'_wheel_spoke',(-.225,-.33,1.80),(-.225+math.cos(a)*.088,-.33,1.80+math.sin(a)*.088),.007,'ochre',12)
    for xx in [-.31,-.14,.20]:
        rod(name+'_flange',(xx-.015,-.16,1.80),(xx+.015,-.16,1.80),.061,'steel')
        for i in range(4):
            a=i*math.tau/4;rod(name+'_flange_bolt',(xx-.022,-.16+math.cos(a)*.049,1.80+math.sin(a)*.049),(xx+.022,-.16+math.cos(a)*.049,1.80+math.sin(a)*.049),.005,'darksteel',6)
    rod(name+'_regulator',(.07,-.16,1.66),(.07,-.16,1.94),.077,'teal',32)
    rod(name+'_adjuster',(.07,-.16,1.94),(.07,-.16,2.015),.042,'rubber',16)
    bowl=annular_x(name+'_hollow_glass_bowl',1.51,1.68,.07,-.16,.047,.0445,'glass',64)
    for v in bowl.data.vertices:v.co=(v.co.y,v.co.z,v.co.x)
    rod(name+'_filter_core',(.07,-.16,1.515),(.07,-.16,1.66),.022,'ivory',32)
    for i in range(12):
        a=i*math.tau/12;rod(name+'_filter_pleat',(.07+math.cos(a)*.022,-.16+math.sin(a)*.022,1.528),(.07+math.cos(a)*.022,-.16+math.sin(a)*.022,1.65),.0014,'steel',8)
    for i in range(4):box(name+'_bowl_level_mark',(.074,-.2072,1.54+i*.024),(.014 if i%2 else .022,.0006,.0015),'ivory',0)
    box(name+'_regulator_identity',(.07,-.238,1.837),(.073,.002,.045),'teal_light',0)
    text_obj(name+'_regulator_model','AR-07',(.07,-.2395,1.832),.012,'ivory')
    for xx in [-.027,.167]:
        box(name+'_housing_lug',(xx,-.16,1.874),(.040,.095,.083),'teal',.006)
        bolt(name+'_housing_assembly_bolt',(xx,-.208,1.881),(0,-1,0),.008)
    for aa in [.32,1.46,2.6,4.1,5.36]:
        tube(name+'_wheel_handling_wear',[(-.225+.096*math.cos(aa+t),-.339,1.8+.096*math.sin(aa+t)) for t in [0,.024,.052]],.0015,'steel')
    for i in range(12):
        a=i*math.tau/12
        rod(name+'_knob_grip_rib',(.07+math.cos(a)*.041,-.16+math.sin(a)*.041,1.946),(.07+math.cos(a)*.041,-.16+math.sin(a)*.041,2.005),.004,'rubber',8)
    for zz in [1.679,1.918]:rod(name+'_regulator_body_seam',(.07,-.16,zz-.006),(.07,-.16,zz+.006),.079,'steel',32)
    rod(name+'_bowl_retainer',(.07,-.16,1.50),(.07,-.16,1.52),.052,'steel')
    rod(name+'_drain_cock',(.07,-.16,1.455),(.07,-.16,1.505),.015,'brass')
    box(name+'_drain_handle',(.091,-.16,1.47),(.065,.018,.015),'ochre')
    tube(name+'_instrument_stem',[(.15,-.16,1.80),(.25,-.16,1.91),(.25,-.16,2.02)],.012,'brass')
    gauge(name+'_pressure_gauge',.25,-.20,2.065,.073)
    rod(name+'_gauge_socket',(.25,-.16,2.00),(.25,-.16,2.045),.02,'brass')
    rod(name+'_quick_coupler',(.39,-.16,1.48),(.39,-.16,1.56),.031,'brass')
    rod(name+'_coupler_grip',(.39,-.16,1.49),(.39,-.16,1.54),.037,'steel',24)
    tube(name+'_dust_cap_tether',[(.39,-.16,1.54),(.48,-.17,1.50),(.48,-.17,1.42)],.003,'rubber')
    rod(name+'_dust_cap',(.48,-.19,1.42),(.48,-.15,1.42),.028,'rubber')
    text_obj(name+'_label','SERVICE AIR',(0,-.052,2.17),.072,'ivory')
    # Hose is disconnected and capped during transit; all loops rest on a bolted hook.
    box(name+'_hose_hook_foot',(.27,-.04,1.35),(.16,.04,.20),'steel')
    tube(name+'_hose_hook',[(.27,-.04,1.35),(.27,-.30,1.35),(.27,-.30,1.40)],.013,'steel')
    for i in range(3):
        yy=-.17-i*.035
        tube(name+'_coiled_hose',[(.27+.17*math.cos(a),yy,1.077+.26*math.sin(a)) for a in [math.pi/2+j*math.tau/64 for j in range(65)]],.016,'rubber')
    tube(name+'_hose_tail',[(.27,-.17,1.337),(.10,-.17,1.16),(.10,-.17,.89),(.17,-.17,.78)],.016,'rubber')
    rod(name+'_hose_plug',(.17,-.17,.78),(.195,-.17,.75),.024,'brass')
    place_wall_group(par,origin,heading)

def wall_station():
    # The paperwork station is on the clear side of the bay's rear wall.
    par=local_wall_root('Dispatch_paperwork_station',(1.55,13.2),0,1.65)
    box('Docket_station_back',(0,-.027,1.65),(.45,.054,.65),'teal')
    box('Docket_clipboard',(0,-.068,1.69),(.31,.018,.40),'paper',.004)
    box('Clipboard_clip',(0,-.083,1.91),(.095,.018,.035),'steel')
    text_obj('Dispatch_card_heading','INSPECTION',(0,-.079,1.80),.035,'ink')
    for i in range(5):box('Inspection_rule',(.01,-.079,1.74-i*.040),(.20,.002,.002),'ink',0)
    box('Records_pocket',(0,-.105,1.41),(.37,.16,.12),'teal_light')
    for xx in [-.18,.18]:bolt('Records_anchor',(xx,-.061,1.94))
    place_wall_group(par,(1.55,13.2),0)

def task_light():
    wall_light('Cask_task_light',(3.08,13.2),0,2.58,180)

def wall_light(name,origin,heading=0,z=2.55,power=95,shallow=False):
    par=local_wall_root(name,origin,heading,z)
    projection=.5 if shallow else 1
    box(name+'_back',(0,-.022,z),(.18,.044,.30),'darksteel')
    rod(name+'_arm',(0,-.04,z+.04),(0,-.22*projection,z+.04),.019,'steel')
    box(name+'_hood',(0,-.25*projection,z+.025),(.43,.30*projection,.12),'teal',.009)
    box(name+'_diffuser',(0,-.25*projection,z-.041),(.36,.25*projection,.012),'lamp',.004)
    place_wall_group(par,origin,heading)
    c,s=math.cos(heading),math.sin(heading)
    area(name+'_pool',(origin[0]+s*.26*projection,origin[1]-c*.26*projection,z-.052),(origin[0]+s*.20,origin[1]-c*.20,.90),power*.52,(1,.75,.48),.20,.10*projection)

def floor_detail():
    root('Bay_floor_finish')
    # Staged trolley footprint is entirely east of the bypass and north of freight.
    for yy in [11.65,12.90]:box('Staged_white_line',(2.65,yy,.001),(2.18,.035,.002),'ivory',0)
    for xx in [1.56,3.74]:box('Staged_white_line',(xx,12.275,.001),(.035,1.25,.002),'ivory',0)
    text_obj('Staged_floor_type','STAGED',(2.65,11.32,.0017),.18,'ivory',(0,0,0))
    # One authored freight turn arrow, followed by a narrow edge route stripe.
    prism('Freight_floor_arrow',[(3.10,9.80),(3.65,9.80),(3.65,9.65),(4.05,10),(3.65,10.35),(3.65,10.20),(3.10,10.20)],.0007,.002,'ochre')
    box('Bypass_edge_mark',(-1.07,12.1,.001),(.04,2.10,.002),'ochre',0)

def gate_drive_detail():
    # A support-registered drive attached to the authored gate lintel.
    par=local_wall_root('Freight_gate_drive',(6.35,10),-math.pi/2,3.72,face=-.185)
    # Local source plane is the front face of the existing overhead cover.
    # Two backing segments leave the existing head access lid unobstructed.
    for lo,hi in [(-1.80,.627),(1.277,1.80)]:
        box('Gate_drive_plate',((lo+hi)/2,.177,3.7225),(hi-lo,.036,.095),'steel',.003)
    for xx in [-1.5,1.5]:
        box('Gate_track_bearing',(xx,.105,3.72),(.12,.11,.16),'teal')
        rod('Gate_roller',(xx,.04,3.72),(xx,.10,3.72),.061,'steel')
    box('Gate_chain_rail',(0,.06,3.74),(3.12,.042,.055),'darksteel')
    for zz in [3.735,3.775]:rod('Gate_chain_tension',(-1.49,.029,zz),(1.49,.029,zz),.006,'steel',12)
    # C10: 300 mm motor, 180 mm end bells and a 200 mm fin envelope.
    # The longitudinal cooling ribs meet the stator casting; detachable end
    # bells have flange screws. A guarded reducer transfers to the lower rail.
    rod('Gate_motor',(1.28,.030,3.96),(1.54,.030,3.96),.078,'motor_coat',48)
    for profile in [[(1.26,.073),(1.264,.087),(1.277,.090),(1.291,.086)],
                    [(1.526,.086),(1.542,.090),(1.556,.084),(1.56,.073)]]:
        lathe_x('Motor_end_bell',profile,.03,3.96,'motor_coat',48)
    for i in range(18):
        angle=math.tau*i/18
        if abs(angle-math.pi/2)<.24:continue
        cy,sz=math.cos(angle),math.sin(angle)
        # Tangential thickness 5 mm; radial limits 77.5–100 mm.
        ob=box('Motor_cooling_fin',(1.409,.03+cy*.08875,3.96+sz*.08875),(.232,.0225,.005),'motor_coat',.001)
        ob.rotation_euler.x=angle
        if i in [6,8,10]:
            u=1.32+(i%3)*.042
            ob=mesh('Motor_fin_edge_wear',[(u,.03+cy*.1001,3.96+sz*.1001),(u+.026,.03+cy*.1001,3.96+sz*.1001),(u+.021,.03+cy*.1001-sz*.0015,3.96+sz*.1001+cy*.0015),(u+.005,.03+cy*.1001-sz*.0015,3.96+sz*.1001+cy*.0015)],[(0,1,2,3)],'steel');ob['surface_decal']=True
    for end,direction in [(1.261,-1),(1.557,1)]:
        for i in range(4):
            a=math.pi/4+i*math.pi/2;yy=.03+math.cos(a)*.065;zz=3.96+math.sin(a)*.065
            rod('Motor_end_bell_screw',(end,yy,zz),(end+direction*.006,yy,zz),.005,'steel',6)
    for xx in [1.315,1.50]:
        box('Motor_cast_foot',(xx,.03,3.866),(.041,.09,.032),'teal',.004)
        for yy in [-.026,.086]:
            box('Motor_foot_lug',(xx,yy,3.858),(.054,.030,.016),'teal',.002)
            rod('Motor_foot_bolt',(xx,yy,3.855),(xx,yy,3.870),.005,'steel',6)
    box('Gate_motor_bracket',(1.41,.04,3.839),(.35,.22,.022),'steel',.003)
    box('Motor_vertical_mount',(1.40,.135,3.815),(.22,.048,.19),'steel',.003)
    for xx in [1.33,1.47]:rod('Motor_mount_anchor',(xx,.146,3.79),(xx,.164,3.79),.007,'steel',6)
    box('Motor_reducer_guard',(1.192,.03,3.884),(.136,.154,.254),'motor_coat',.016)
    box('Motor_guard_orange_band',(1.229,-.048,3.891),(.019,.005,.218),'ochre',.002)
    rod('Motor_guard_input',(1.25,.03,3.96),(1.269,.03,3.96),.065,'darksteel',40)
    box('Motor_guard_output_foot',(1.19,.077,3.775),(.11,.09,.048),'teal',.004)
    box('Motor_guard_service_plate',(1.185,-.049,3.897),(.053,.006,.067),'steel',.003)
    ob=mesh('Motor_guard_caution',[(1.164,-.0522,3.881),(1.206,-.0522,3.881),(1.185,-.0522,3.916)],[(0,1,2)],'ochre');ob['surface_decal']=True
    text_obj('Motor_guard_caution_type','!',(1.185,-.0525,3.885),.025,'ink')
    for xx in [1.145,1.244]:
        for zz in [3.793,3.973]:rod('Motor_guard_fastener',(xx,-.044,zz),(xx,-.054,zz),.005,'steel',6)
    # Supported terminal enclosure, lid seam, glands and a secured supply cable.
    box('Motor_terminal_neck',(1.412,.03,4.043),(.044,.044,.016),'darksteel',.002)
    box('Motor_terminal_box',(1.412,.03,4.076),(.086,.070,.052),'motor_coat',.004)
    box('Motor_terminal_lid',(1.412,.03,4.105),(.090,.074,.009),'teal',.002)
    for xx in [1.381,1.443]:
        for yy in [.008,.052]:rod('Motor_terminal_lid_screw',(xx,yy,4.107),(xx,yy,4.112),.003,'steel',6)
    rod('Motor_cable_gland',(1.452,.03,4.079),(1.476,.03,4.079),.012,'steel',6)
    rod('Motor_cable_boot',(1.470,.03,4.079),(1.484,.03,4.079),.009,'rubber',24)
    tube('Motor_supply_cable',[(1.479,.03,4.079),(1.502,.03,4.079),(1.523,.045,4.087),(1.534,.071,4.111),(1.534,.108,4.153),(1.534,.15,4.178),(1.534,.213,4.184),(1.534,.247,4.184)],.007,'rubber')
    rod('Motor_cable_id_sleeve',(1.534,.153,4.178),(1.534,.179,4.181),.008,'ochre',24)
    box('Motor_cable_clamp_back',(1.534,.243,4.184),(.062,.014,.049),'steel',.002)
    box('Motor_cable_retainer',(1.534,.220,4.184),(.025,.010,.026),'teal',.002)
    for xx in [1.516,1.552]:
        box('Motor_cable_retainer_ear',(xx,.220,4.184),(.015,.010,.024),'teal',.002)
        rod('Motor_cable_clamp_spacer',(xx,.225,4.184),(xx,.236,4.184),.0055,'steel',24)
        rod('Motor_cable_clamp_stud',(xx,.211,4.184),(xx,.249,4.184),.003,'steel',6)
    # Small invented service details stay attached to the casting and enclosure.
    box('Motor_serial_standoff',(1.411,-.064,3.957),(.108,.018,.039),'teal',.003)
    box('Motor_serial_plate',(1.411,-.075,3.957),(.114,.004,.043),'ivory',.002)
    text_obj('Motor_serial_type','FCM-01',(1.411,-.0774,3.959),.014,'ink')
    text_obj('Motor_serial_small','DRV / 030',(1.411,-.0774,3.943),.007,'ink')
    for xx in [1.361,1.461]:rod('Motor_serial_screw',(xx,-.077,3.957),(xx,-.080,3.957),.0025,'steel',6)
    text_obj('Motor_terminal_warning','!',(1.412,-.0055,4.066),.028,'ochre')
    box('Orange_drive_access',(-1.39,.020,3.93),(.41,.05,.24),'ochre')
    box('Access_cover_standoff',(-1.39,.08,3.85),(.22,.18,.20),'teal')
    for member in par.children:member.location.y-=.38
    place_wall_group(par,(6.35,10),-math.pi/2)
    if A.stage=='full':
        # Task lamp back meets the crown infill at X6.22; light source remains
        # inside the physical diffuser, above the motor and freight aperture.
        lamp=local_wall_root('Gate_motor_task_lamp',(6.22,9.03),-math.pi/2,4.16)
        box('Motor_task_back',(0,-.011,4.16),(.13,.022,.18),'darksteel',.003)
        box('Motor_task_arm',(0,-.23,4.16),(.035,.416,.025),'steel',.002)
        box('Motor_task_hood',(0,-.45,4.155),(.20,.13,.045),'teal',.005)
        box('Motor_task_diffuser',(0,-.45,4.129),(.17,.10,.007),'motor_diffuser',.002)
        for xx in [-.045,.045]:rod('Motor_task_anchor',(xx,-.024,4.16),(xx,-.006,4.16),.005,'steel',6)
        place_wall_group(lamp,(6.22,9.03),-math.pi/2)
        area('Motor_task_pool',(5.77,9.03,4.124),(5.96,8.62,3.94),7,(1,.83,.65),.16,.09)

def workbench():
    # A shallow floor-supported maintenance bench on the west wall.
    x,y=-1.81,10.58
    par=root('Maintenance_bench','floor',[(x+sx*.19,y+sy*.65,0) for sx in [-1,1] for sy in [-1,1]])
    for sx in [-1,1]:
        for sy in [-1,1]:
            box('Bench_foot',(x+sx*.19,y+sy*.65,.018),(.12,.14,.036),'darksteel')
            box('Bench_leg',(x+sx*.19,y+sy*.65,.44),(.056,.056,.844),'teal')
    box('Bench_top',(x,y,.878),(.58,1.53,.052),'steel',.008)
    box('Bench_shelf',(x,y,.22),(.46,1.39,.026),'teal')
    for sy in [-1,1]:box('Bench_apron',(x,y+sy*.68,.80),(.48,.035,.12),'teal')
    small_case('Bench_tool_case',(x,y+.38,.905),(.34,.28,.19))
    rod('Grease_tin',(x,y-.36,.905),(x,y-.36,1.025),.061,'steel',32)
    rod('Tin_lid',(x,y-.36,1.025),(x,y-.36,1.034),.063,'darksteel')
    for zz in [.909,1.019]:torus('Grease_tin_rolled_rim',(x,y-.36,zz),.060,.003,'steel')
    rod('Grease_paper_label',(x,y-.36,.939),(x,y-.36,1.004),.0614,'paper',48)
    for zz in [.939,1.004]:torus('Grease_label_border',(x,y-.36,zz),.0617,.0013,'ochre')
    folded_cloth('Bench_folded_rag',x,y-.02,.905,.23,.26)
    small_case('Spare_parts_case',(x,y+.23,.234),(.33,.39,.23),'old_teal')
    # Small glove silhouette: palm plus four articulated fingers and thumb.
    laid_glove('Left_work_glove',x-.082,y-.63,-1,-.10)
    laid_glove('Right_work_glove',x+.082,y-.60,1,.16)
    # A readable mix of shift objects, each on the bench or lower shelf.
    rod('Workshop_flask',(x-.17,y+.07,.905),(x-.17,y+.07,1.11),.046,'teal_light',32)
    rod('Flask_cap',(x-.17,y+.07,1.11),(x-.17,y+.07,1.132),.048,'steel',32)
    torus('Flask_handle',(x-.225,y+.07,1.04),.046,.008,'steel',(math.pi/2,0,0))
    text_obj('Grease_tin_label','GREASE',(x+.0625,y-.36,.965),.019,'ink',(math.pi/2,0,math.pi/2))
    rod('Worklight_body',(x+.17,y-.16,.934),(x+.17,y+.06,.934),.025,'ochre',24)
    rod('Worklight_end',(x+.17,y-.18,.934),(x+.17,y-.145,.934),.029,'darksteel',24)
    rod('Flashlight_reflector',(x+.17,y-.181,.934),(x+.17,y-.182,.934),.023,'ivory',32)
    rod('Flashlight_lens',(x+.17,y-.182,.934),(x+.17,y-.184,.934),.023,'glass',32)
    box('Torch_thumb_switch',(x+.17,y-.04,.960),(.024,.045,.012),'rubber',.004)
    for yy in [y-.11,y-.086,y+.034]:torus('Torch_grip_ring',(x+.17,yy,.934),.024,.002,'darksteel',(math.pi/2,0,0))
    torus('Flask_base_impact_ring',(x-.17,y+.07,.917),.045,.004,'rubber')
    torus('Flask_lid_seal',(x-.17,y+.07,1.112),.047,.002,'rubber')
    for i in range(16):
        aa=i*math.tau/16;rod('Flask_cap_knurl',(x-.17+math.cos(aa)*.047,y+.07+math.sin(aa)*.047,1.118),(x-.17+math.cos(aa)*.047,y+.07+math.sin(aa)*.047,1.129),.0018,'darksteel',6)
    small_case('Consumables_drawer',(x,y-.36,.234),(.35,.36,.19),'teal_light')
    for yy in [y-.65,y+.65]:
        for zz in [.30,.67]:bolt('Bench_apron_bolt',(x+.22,yy,zz),(1,0,0),.009)

def tool_board():
    origin=(-2.2,10.58);heading=math.pi/2
    par=local_wall_root('Maintenance_tool_board',origin,heading,1.75)
    box('Toolboard_back',(0,-.023,1.66),(1.30,.046,.94),'teal')
    for u in [-.56,.56]:
        for z in [1.27,2.05]:bolt('Toolboard_fixing',(u,-.053,z))
    for i in range(4):
        xx=-.45+i*.235;zz=1.84;length=.21+i*.042;factor=(24+i*4)/36
        rod('Tool_hanging_peg',(xx,-.046,zz),(xx,-.115,zz),.009,'steel')
        # Forged elliptical ring head with a true hexagonal working aperture.
        center_z=zz+.009-.0207846097*factor;nn=48;vv=[]
        for yy,inside in [(-.128,False),(-.110,False),(-.110,True),(-.128,True)]:
            for j in range(nn):
                angle=j*math.tau/nn
                radius=.018*factor/math.cos((angle+math.pi/6)%(math.pi/3)-math.pi/6)
                vv.append((xx+math.cos(angle)*(radius if inside else .035*factor),yy,center_z+math.sin(angle)*(radius if inside else .043*factor)))
        ff=[(k*nn+j,k*nn+(j+1)%nn,((k+1)%4)*nn+(j+1)%nn,((k+1)%4)*nn+j) for k in range(4) for j in range(nn)]
        head=mesh('Forged_hex_ring_head',vv,ff,'steel');be=head.modifiers.new('Forged edge fillet','BEVEL');be.width=.0015;be.segments=2
        shoulder=zz-.020;heel=zz-.045-length
        outline=[(-.021*factor,shoulder),(-.013*factor,shoulder-.05),(-.011*factor,heel+.04),(-.022*factor,heel),(.022*factor,heel),(.011*factor,heel+.04),(.013*factor,shoulder-.05),(.021*factor,shoulder)]
        vv=[(xx+u,yy,z) for yy in [-.127,-.111] for u,z in outline];nn=len(outline)
        sh=mesh('Forged_contour_shank',vv,[tuple(reversed(range(nn))),tuple(range(nn,nn*2))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)],'steel');be=sh.modifiers.new('Forged shank fillet','BEVEL');be.width=.002;be.segments=3
        box('Spanner_recessed_flute',(xx,-.1275,zz-.046-length*.46),(.008*factor,.001,length*.57),'darksteel',0)
        text_obj('Spanner_forged_size',str(24+i*4),(xx,-.127,zz-.12),.012,'darksteel')
        jaw_z=zz-.048-length
        outline=[(-.036,.024),(.036,.024),(.050,-.019),(.041,-.042),(.020,-.044),(.019,-.006),(-.016,.002),(-.025,-.035),(-.042,-.029)]
        outline=[(u*factor,v*factor) for u,v in outline]
        vv=[(xx+u,yy,jaw_z+v) for yy in [-.129,-.109] for u,v in outline];nn=len(outline)
        jaw=mesh('Open_jaw_spanner',vv,[tuple(reversed(range(nn))),tuple(range(nn,nn*2))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)],'steel');be=jaw.modifiers.new('Forged jaw edge','BEVEL');be.width=.0025;be.segments=3
    rod('Driver_hanging_peg',(.49,-.046,1.84),(.49,-.115,1.84),.009,'steel')
    torus('Driver_hang_ring',(.49,-.119,1.815),.030,.007,'steel',(math.pi/2,0,0))
    rod('Insulated_driver_grip',(.49,-.119,1.69),(.49,-.119,1.80),.023,'ochre',12)
    rod('Driver_shaft',(.49,-.119,1.53),(.49,-.119,1.69),.005,'steel',12)
    box('Driver_flat_tip',(.49,-.119,1.52),(.014,.006,.023),'steel',.001)
    box('Board_tray',(0,-.15,1.25),(1.10,.22,.026),'teal_light')
    text_obj('Toolboard_heading','TOOLS / RETURN AFTER USE',(0,-.048,1.995),.038,'ivory')
    place_wall_group(par,origin,heading)

def wall_vent(name,origin,heading=0,z=3.2,width=.85):
    par=local_wall_root(name,origin,heading,z)
    box(name+'_frame',(0,-.045,z),(width,.09,.42),'teal')
    box(name+'_shadow',(0,-.094,z),(width-.10,.016,.32),'rubber')
    for i in range(6):
        o=box(name+'_blade',(0,-.117,z-.131+i*.052),(width-.13,.047,.027),'steel',.002);o.rotation_euler.x=.25
    for xx in [-width/2+.035,width/2-.035]:
        for zz in [z-.17,z+.17]:bolt(name+'_bolt',(xx,-.096,zz),r=.009)
    place_wall_group(par,origin,heading)

def route_sign(name,label,origin,heading=0,z=2.82,width=1.70):
    par=local_wall_root(name,origin,heading,z)
    box(name+'_panel',(0,-.019,z),(width,.038,.28),'teal')
    text_obj(name+'_letters',label,(-.10,-.040,z-.047),.105,'ivory')
    for edge in [-1,1]:box(name+'_folded_edge',(0,-.041,z+edge*.139),(width,.032,.018),'darksteel',.002)
    for xx in [width*.5-.22,width*.5-.13]:
        if name=='Service_bypass_sign':
            vv=[(xx+u,-.0395,z+v) for u,v in [(-.036,-.020),(0,.040),(.036,-.020),(.036,.011),(0,.071),(-.036,.011)]]
        else:vv=[(xx-.035,-.0395,z-.052),(xx+.005,-.0395,z),(xx-.035,-.0395,z+.052),(xx,-.0395,z+.052),(xx+.04,-.0395,z),(xx,-.0395,z-.052)]
        ob=mesh(name+'_direction_chevron',vv,[(0,1,2,3,4,5)],'ochre')
    for xx in [-width*.5+.04,width*.5-.04]:bolt(name+'_fixing',(xx,-.046,z),r=.008)
    place_wall_group(par,origin,heading)

def corner_marker(name,origin,heading=0,label='04'):
    par=local_wall_root(name,origin,heading,1.6)
    box(name+'_plate',(0,-.010,1.71),(.44,.020,.74),'mineral')
    text_obj(name+'_number',label,(0,-.022,1.77),.28,'teal')
    box(name+'_accent',(0,-.023,1.48),(.36,.003,.045),'ochre',0)
    place_wall_group(par,origin,heading)

def detail_dressing(stage):
    workbench();tool_board()
    utility_station('Staging_air_station',(3.8,13.2),0)
    wall_light('Bench_worklight',(-2.2,10.58),math.pi/2,2.36,155)
    wall_vent('Staging_vent',(2.16,13.2),0,3.63,.83)
    # A sign on the actual bypass ceiling step leaves its clear opening untouched.
    route_sign('Service_bypass_sign','SERVICE',(0,13.10),0,3.37,1.85)
    wall_light('Service_header_worklight',(0,13.10),0,3.83,130)
    corner_marker('Bay_identity',(4.4,12.63),-math.pi/2,'04')
    # Original restrained graphics and edge-specific wear tie the work bay to A05.
    root('Bay_authored_wall_finish')
    ob=mesh('Staging_zone_diagonal',[(1.95,13.1985,1.38),(2.60,13.1985,1.93),(2.60,13.1985,2.19),(1.95,13.1985,1.64)],[(0,1,2,3)],'ochre');ob['surface_decal']=True
    for origin,heading,u0,u1 in [((-2.2,10.58),math.pi/2,.74,1.28),((4.4,12.63),-math.pi/2,-.28,.29)]:
        c,s=math.cos(heading),math.sin(heading)
        coordinates=[(u0,1.46),(u1,1.82),(u1,2.18),(u0,1.82)]
        vv=[(origin[0]+c*u+s*.0015,origin[1]+s*u-c*.0015,z) for u,z in coordinates]
        ob=mesh('Work_bay_diagonal',vv,[(0,1,2,3)],'ochre');ob['surface_decal']=True
    # Markings belong to the architecture and have no freestanding prop supports.
    for child in list(PAR.children):
        COL.objects.unlink(child);bpy.data.collections['01_Architecture'].objects.link(child)
    COL.objects.unlink(PAR);bpy.data.collections['01_Architecture'].objects.link(PAR)
    wall_light('Transfer_gate_key',(6.165,10),-math.pi/2,3.93,220)
    root('Staging_cable_ladder','ceiling',[(-1.55,8.1,4.4),(-1.55,11.6,4.4)],(0,0,1))
    for xx in [-1.73,-1.37]:
        box('Ladder_edge_channel',(xx,10.10,3.94),(.033,5.3,.12),'teal')
        box('Ladder_edge_fold',(xx,10.10,3.891),(.070,5.3,.023),'steel')
    for i in range(22):box('Ladder_rung',(-1.55,7.50+i*.245,3.89),(.37,.023,.025),'steel')
    for yy in [8.1,11.6]:
        for xx in [-1.72,-1.38]:rod('Ladder_drop',(xx,yy,4.4),(xx,yy,3.865),.009,'steel')
        box('Ladder_support_saddle',(-1.55,yy,3.867),(.42,.06,.025),'teal')
        box('Ladder_ceiling_shoe',(-1.55,yy,4.382),(.42,.08,.036),'steel')
    for i in range(4):tube('Laid_power_cable',[(-1.66+i*.07,7.51+j*.245,3.918) for j in range(22)],.016,'rubber' if i%3 else 'ochre')
    if stage=='full':
        utility_station('Service_air_station',(-1.45,15.00),math.pi/2,2.14)
        root('Recess_task_light','ceiling',[(-1.37,15,2.45)],(0,0,1))
        box('Recess_light_pan',(-1.37,15,2.434),(.24,.50,.032),'teal',.005)
        box('Recess_light_diffuser',(-1.37,15,2.414),(.20,.42,.008),'lamp',.002)
        area('Recess_light_pool',(-1.34,15,2.403),(-1.15,15,1.5),30,(1,.78,.55),.18,.36)
        for name,origin,angle,z in [('Entry_wall_key',(-2.2,4.8),math.pi/2,2.72),('Cross_wall_key',(9.1,12.2),0,2.72),('East_wall_key',(16.4,9.92),-math.pi/2,2.94),('Delivery_wall_key',(12,17.35),math.pi/2,2.72),('Service_corner_key',(-1.5,20.35),math.pi/2,2.36),('Medical_side_key',(8.5,21),0,2.34)]:wall_light(name,origin,angle,z,105)
        wall_vent('Entry_extract',(2.2,4.6),-math.pi/2,3.35,1.02)
        wall_vent('East_extract',(13.35,7),math.pi,3.35,1.12)
        wall_vent('Service_extract',(10.4,21),0,2.26,.72)
        corner_marker('Entry_marker',(-2.2,2.50),math.pi/2,'04')
        corner_marker('Waste_marker',(16.4,18.10),-math.pi/2,'W')
        # One compact wall-supported emergency/tool locker in the east turning bay.
        par=local_wall_root('East_service_locker',(11.0,7),math.pi,1.8)
        box('Locker_back',(0,-.035,1.45),(.72,.07,1.22),'darksteel')
        box('Locker_shell',(0,-.15,1.45),(.72,.26,1.22),'teal')
        box('Locker_orange_door',(0,-.289,1.45),(.64,.019,1.14),'ochre',.009)
        for zz in [1.1,1.85]:box('Locker_hinge',(-.33,-.30,zz),(.035,.025,.12),'steel')
        box('Locker_latch',(.24,-.321,1.42),(.06,.045,.15),'darksteel',.006)
        text_obj('Locker_identity','SERVICE\nKIT',(0,-.303,1.62),.086,'teal')
        place_wall_group(par,(11.0,7),math.pi)
        route_storytelling()


def painted_route(name,origin,heading,title,subtitle,direction=1,width=1.5,z=1.90):
    """Architectural paint, explicitly separate from physical mounted equipment."""
    par=root(name)
    text_obj(name+'_title',title,(-.10,-.0018,z+.14),min(.26,width/max(len(title),1)*1.48),'teal')
    text_obj(name+'_subtitle',subtitle,(-.10,-.0018,z-.05),min(.105,width/max(len(subtitle),1)*1.45),'teal')
    box(name+'_rule',(-.10,-.0015,z+.065),(width*.76,.001,.016),'ochre',0)
    for i in range(3):
        cx=direction*(width*.47+i*.10)
        vv=[(cx+direction*x,-.002,zz+z+.17) for x,zz in [(-.042,-.105),(.032,0),(-.042,.105),(.014,.105),(.088,0),(.014,-.105)]]
        mesh(name+'_chevron',vv,[(0,1,2,3,4,5)],'ochre')
    place_wall_group(par,origin,heading)
    for obj in list(par.children)+[par]:
        obj['surface_decal']=True
        for owner in list(obj.users_collection):owner.objects.unlink(obj)
        bpy.data.collections['01_Architecture'].objects.link(obj)


def destination_badge(name,origin,heading,number,title,subtitle,width=1.55,z=1.62,direction=-1):
    """A large painted destination fits wholly between the structural uprights."""
    par=root(name)
    for suffix,label,u,zz,size in [('number',number,.10,z+.47,.66),('title',title,.10,z+.15,min(.245,width/len(title)*1.42)),('subtitle',subtitle,.10,z,min(.085,width/len(subtitle)*1.35))]:
        ob=text_obj(name+'_'+suffix,label,(u,-.002,zz),size,'teal')
        ob.data.offset=size*.013
    box(name+'_accent',(.10,-.0016,z+.11),(width*.62,.001,.023),'ochre',0)
    for i in range(2):
        cx=direction*(width*.38+i*.105)
        vv=[(cx+direction*x,-.0022,zz+z+.70) for x,zz in [(-.045,-.14),(.045,0),(-.045,.14),(.019,.14),(.109,0),(.019,-.14)]]
        mesh(name+'_chevron',vv,[(0,1,2,3,4,5)],'ochre')
    place_wall_group(par,origin,heading)
    for obj in list(par.children)+[par]:
        obj['surface_decal']=True
        for owner in list(obj.users_collection):owner.objects.unlink(obj)
        bpy.data.collections['01_Architecture'].objects.link(obj)


def low_guide(name,origin,heading,z=.32):
    origin=(origin[0]+math.sin(heading)*.028,origin[1]-math.cos(heading)*.028)
    par=local_wall_root(name,origin,heading,z)
    box(name+'_back',(0,-.012,z),(.30,.024,.13),'darksteel',.002)
    box(name+'_housing',(0,-.035,z),(.29,.048,.12),'teal',.007)
    box(name+'_glass',(0,-.061,z),(.215,.008,.065),'lamp',.003)
    for xx in [-.124,.124]:bolt(name+'_fastener',(xx,-.060,z),r=.005)
    place_wall_group(par,origin,heading)
    c,s=math.cos(heading),math.sin(heading)
    area(name+'_wash',(origin[0]+s*.07,origin[1]-c*.07,z-.04),(origin[0]+s*.42,origin[1]-c*.42,.025),7,(1,.72,.40),.18,.035)


def permit_holder(name,origin,heading=0,z=1.65):
    origin=(origin[0]+math.sin(heading)*.012,origin[1]-math.cos(heading)*.012)
    par=local_wall_root(name,origin,heading,z,face=.012)
    box(name+'_mounting_spacer',(0,.006,z),(.10,.012,.04),'steel',.001)
    box(name+'_back',(0,-.012,z),(.235,.024,.38),'teal',.003)
    box(name+'_card',(0,-.026,z),(.192,.004,.31),'paper',0)
    box(name+'_clip',(0,-.035,z+.137),(.062,.014,.033),'steel',.002)
    text_obj(name+'_heading','WORK PERMIT',(0,-.029,z+.087),.023,'ink')
    for i in range(6):
        box(name+'_rule',(.008,-.029,z+.040-i*.026),(.15,.0015,.0015),'ink',0)
        box(name+'_checkbox',(-.073,-.029,z+.047-i*.026),(.008,.0015,.008),'ink',0)
    rod(name+'_pen',(.112,-.037,z-.10),(.112,-.037,z+.105),.006,'teal_light',12)
    box(name+'_pen_clip',(.106,-.023,z+.057),(.022,.024,.044),'steel',.002)
    for xx in [-.096,.096]:bolt(name+'_anchor',(xx,-.028,z+.168),r=.005)
    place_wall_group(par,origin,heading)


def distribution_box(name,origin,heading=0,z=1.62,compact=False):
    offset=.065 if not compact else .012
    origin=(origin[0]+math.sin(heading)*offset,origin[1]-math.cos(heading)*offset)
    par=local_wall_root(name,origin,heading,z,face=offset)
    w,h,depth=(.38,.49,.07) if compact else (.70,1.07,.13)
    box(name+'_mounting_spacer',(0,offset/2,z),(.12,offset,h*.30),'steel',.002)
    box(name+'_back',(0,-.012,z),(w,.024,h),'darksteel',.004)
    box(name+'_folded_shell',(0,-depth/2-.012,z),(w,depth,h),'teal',.012)
    front=-depth-.015
    box(name+'_gasket',(0,front,z),(w-.025,.014,h-.024),'rubber',.005)
    box(name+'_door',(0,front-.011,z),(w-.042,.020,h-.042),'teal_light',.006)
    for x in [-w*.43,w*.43]:
        for zz in [z-h*.41,z+h*.41]:bolt(name+'_quarter_turn',(x,front-.026,zz),r=.009)
    for zz in [z-h*.30,z+h*.30]:box(name+'_hinge',(-w*.48,front-.009,zz),(.027,.034,.060),'steel',.004)
    rod(name+'_switch_body',(w*.22,front-.021,z),(w*.22,front-.037,z),.045,'darksteel',24)
    box(name+'_isolation_handle',(w*.22,front-.046,z),(.021,.023,.078),'ochre',.003)
    text_obj(name+'_identity','E-03' if compact else 'FC / 04',(-w*.13,front-.022,z+h*.33),.046,'ivory')
    tri=mesh(name+'_hazard',[(x,front-.022,zz) for x,zz in [(-w*.25,z+.04),(-w*.25-.058,z-.062),(-w*.25+.058,z-.062)]],[(0,1,2)],'ochre');tri['surface_decal']=True
    text_obj(name+'_hazard_mark','!',(-w*.25,front-.023,z-.05),.063,'ink')
    box(name+'_service_sticker',(-w*.08,front-.022,z-h*.26),(.13,.0015,.09),'paper',0)
    text_obj(name+'_service_type','CHECKED\n07 / B',(-w*.08,front-.024,z-h*.27),.019,'ink')
    for xx,radius in [(-w*.21,.012),(w*.10,.019)]:
        tail=.08 if compact else 0
        tube(name+'_conduit',[(xx,-.055,z+h/2),(xx,-.055,z+h/2+.36),(xx+.045,-.055,z+h/2+.405),(xx+.045,-.055,z+h/2+.61-tail)],radius,'steel')
        for zz in [z+h/2+.11,z+h/2+.47]:
            box(name+'_clamp_standoff',(xx+(0 if zz<z+h/2+.4 else .045),-.027,zz),(.052,.054,.04),'darksteel',.003)
            box(name+'_clamp_wall_spacer',(xx+(0 if zz<z+h/2+.4 else .045),offset/2,zz),(.052,offset,.04),'steel',.002)
        box(name+'_termination',(xx+.045,-.032,z+h/2+.64-tail),(.08,.064,.08),'teal',.004)
        box(name+'_termination_spacer',(xx+.045,offset/2,z+h/2+.64-tail),(.075,offset,.07),'steel',.002)
    if not compact:
        for i in range(11):box(name+'_side_fin',(-w*.52,-.072,z-.30+i*.06),(.049,.13,.016),'darksteel',.002)
        box(name+'_packet_holder',(w*.55,-.048,z-.24),(.082,.096,.17),'steel',.003)
        box(name+'_spare_fuse_packet',(w*.55,-.098,z-.205),(.066,.006,.18),'paper',.003)
        for i in range(3):box(name+'_packet_mark',(w*.55,-.102,z-.15-i*.033),(.045,.001,.002),'ink',0)
    place_wall_group(par,origin,heading)


def first_aid_pack(name,origin,heading=0):
    z=1.79;origin=(origin[0]+math.sin(heading)*.012,origin[1]-math.cos(heading)*.012)
    par=local_wall_root(name,origin,heading,z,face=.012)
    box(name+'_wall_spacer',(0,.006,z),(.13,.012,.05),'steel',.001)
    box(name+'_mount',(0,-.012,z),(.30,.024,.42),'teal',.005)
    box(name+'_case',(0,-.049,z),(.29,.074,.40),'ivory',.023)
    box(name+'_seal',(0,-.088,z),(.273,.009,.382),'rubber',.015)
    box(name+'_clear_lid',(0,-.096,z),(.268,.009,.377),'glass',.012)
    for xx in [-.14,.14]:box(name+'_latch',(xx,-.067,z),(.024,.040,.063),'darksteel',.004)
    box(name+'_cross_v',(0,-.091,z+.044),(.035,.004,.136),'ochre',0)
    box(name+'_cross_h',(0,-.091,z+.044),(.113,.004,.035),'ochre',0)
    text_obj(name+'_type','FIRST AID',(0,-.092,z-.105),.031,'ink')
    tube(name+'_carry_loop',[(-.055,-.046,z+.194),(-.055,-.046,z+.231),(.055,-.046,z+.231),(.055,-.046,z+.194)],.007,'steel')
    place_wall_group(par,origin,heading)


def route_storytelling():
    # C07/C08 accepted generated paintovers: clear route identity and purposeful, mounted filler.
    destination_badge('East_reactor_route',(16.4,9.92),-math.pi/2,'04','REACTOR','FUEL TRANSFER')
    painted_route('Cross_service_identity',(7.35,12.2),0,'FUEL ROUTE','KEEP TURN CLEAR',1,1.00,1.85)
    destination_badge('Bypass_clean_route',(-.60,21),0,'02','SERVICE','MEDICAL / CLEAN',1.30,1.38,1)
    painted_route('Plant_branch_identity',(-1.5,18.92),math.pi/2,'PLANT','SERVICES',-1,.67,1.73)
    painted_route('Delivery_reactor_identity',(12,16.2),math.pi/2,'REACTOR','FREIGHT APPROACH',1,1.10,1.84)
    painted_route('Clean_leg_identity',(9.08,21),0,'CLEAN SERVICES','MEDICAL / COMPLIANCE',-1,1.00,1.72)
    distribution_box('East_distribution',(16.4,8.04),-math.pi/2)
    distribution_box('Bypass_isolation',(1.2,15.30),-math.pi/2,1.60,True)
    first_aid_pack('Bypass_first_aid',(1.2,15.95),-math.pi/2)
    permit_holder('Bypass_work_permit',(1.2,16.73),-math.pi/2,1.80)
    permit_holder('Plant_work_permit',(-2.85,16.2),math.pi,1.67)
    distribution_box('Clean_distribution',(9.0,18),math.pi,1.60,True)
    # A real suspended blade sign can be read before the side-facing clean door.
    par=root('Clean_branch_blade_sign','ceiling',[(4.95,19.87,3),(4.95,20.63,3)],(0,0,1))
    for yy in [19.87,20.63]:
        rod('Clean_blade_drop',(4.95,yy,3),(4.95,yy,2.69),.009,'steel')
        box('Clean_blade_ceiling_foot',(4.95,yy,2.992),(.10,.10,.016),'teal',.002)
    box('Clean_blade_panel',(4.95,20.25,2.57),(.026,1.12,.24),'sign_coat',.004)
    text_obj('Clean_blade_destination','CLEAN / MEDICAL',(4.935,20.20,2.56),.080,'sign_letters',(math.pi/2,0,-math.pi/2))
    mesh('Clean_blade_left_arrow',[(4.935,yy,zz) for yy,zz in [(20.68,2.525),(20.75,2.57),(20.68,2.615),(20.68,2.59),(20.62,2.59),(20.62,2.55),(20.68,2.55)]],[(0,1,2,3,4,5,6)],'ochre')
    par=root('Plant_branch_blade_sign','ceiling',[(-.46,16.0,3),(.46,16.0,3)],(0,0,1))
    for xx in [-.46,.46]:
        rod('Plant_blade_drop',(xx,16.0,3),(xx,16.0,2.58),.009,'steel')
        box('Plant_blade_ceiling_foot',(xx,16.0,2.992),(.10,.10,.016),'teal',.002)
    box('Plant_blade_panel',(0,16.0,2.46),(1.30,.026,.24),'sign_coat',.004)
    text_obj('Plant_blade_destination','PLANT SERVICES',(.04,15.985,2.445),.090,'sign_letters')
    mesh('Plant_blade_left_arrow',[(xx,15.985,zz) for xx,zz in [(-.48,2.415),(-.55,2.46),(-.48,2.505),(-.48,2.48),(-.42,2.48),(-.42,2.44),(-.48,2.44)]],[(0,1,2,3,4,5,6)],'ochre')
    for i,(p,hd) in enumerate([((16.4,9.6),-math.pi/2),((16.4,11.8),-math.pi/2),((8.0,12.2),0),((12,14.3),math.pi/2),((12,17.6),math.pi/2),((1.2,14.6),-math.pi/2),((-1.5,20.2),math.pi/2),((-.55,21),0),((3.0,18),math.pi),((8.8,18),math.pi),((-2.6,18.6),0)]):low_guide('Route_guide_%02d'%i,p,hd)
    # A warm turn light shows the existing northward continuation from the main crossing.
    wall_light('Reactor_turn_key',(12,15.32),math.pi/2,2.94,180)
    wall_light('Refinery_approach_key',(0,.685),math.pi,3.41,160)
    wall_light('Reactor_left_key',(11.4,22.95),math.pi/2,2.55,180,True)
    wall_light('Reactor_right_key',(17.0,22.95),-math.pi/2,2.55,180,True)
    root('Route_floor_graphics')
    prism('Entry_freight_turn_arrow',[(-.40,9.0),(1.70,9.0),(1.70,8.80),(2.22,9.15),(1.70,9.50),(1.70,9.30),(-.40,9.30)],.0005,.002,'ochre')
    text_obj('Entry_freight_floor_label','FREIGHT',(.45,8.48,.0021),.26,'ivory',(0,0,0))
    outlines=[[(12.9,9.6),(14.4,9.6),(14.4,11.4),(14.7,11.4),(14.15,12.0),(13.6,11.4),(13.9,11.4),(13.9,10.1),(12.9,10.1)],
              [(-.28,18.10),(.02,18.10),(.02,19.08),(1.0,19.08),(1.0,18.88),(1.40,19.23),(1.0,19.58),(1.0,19.38),(-.28,19.38)]]
    for i,outline in enumerate(outlines):prism('Route_turn_arrow_%d'%i,outline,.0005,.002,'ochre')
    for a,b in [((4.45,8.02),(15.25,8.02)),((15.25,8.02),(15.25,20.7)),((-.89,13.3),(-.89,20.1)),((-.89,20.1),(5.0,20.1)),((7.95,20.1),(11.7,20.1))]:
        d=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
        mark=box('Route_edge_paint',(mid.x,mid.y,.001),(d.length,.045,.002),'ochre',0);mark.rotation_euler.z=math.atan2(d.y,d.x)
    for obj in list(PAR.children)+[PAR]:
        obj['surface_decal']=True
        for owner in list(obj.users_collection):owner.objects.unlink(obj)
        bpy.data.collections['01_Architecture'].objects.link(obj)
