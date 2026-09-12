"""Original reference-led construction and prop assemblies, executed by build.py.

No meshes or textures are imported. Coordinates are metric. Supported groups
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
    for i in range(9):
        a=math.pi*.20+i*math.pi*.19
        rod(name+'_tick',(x+math.cos(a)*r*.66,y-.031,z+math.sin(a)*r*.66),(x+math.cos(a)*r*.78,y-.031,z+math.sin(a)*r*.78),.0015,'ink',6)
    rod(name+'_needle',(x,y-.033,z),(x+r*.48,y-.033,z+r*.44),.002,'ink',8)
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

def folded_cloth(name,x,y,z,w=.24,d=.19):
    vv=[];ff=[]
    for j in range(7):
        for i in range(11):vv.append((x-w/2+i*w/10,y-d/2+j*d/6,z+.005+.003*math.sin(i*1.15)))
    for j in range(6):
        for i in range(10):q=j*11+i;ff.append((q,q+1,q+12,q+11))
    o=mesh(name,vv,ff,'cloth');sol=o.modifiers.new('Woven folded thickness','SOLIDIFY');sol.thickness=.010;sol.offset=-1
    for p in o.data.polygons:p.use_smooth=True

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
    lathe_x('Current_reactor_cartridge',[(x-.590,.146),(x-.575,.155),(x+.575,.155),(x+.590,.146)],y,z,'ivory')
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
    for xx,aa,span in [(-.36,2.89,.13),(.19,3.05,.17),(.05,3.70,.09)]:
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
    for xx,aa,width in [(-.29,2.58,.19),(.14,2.66,.22),(-.1,3.55,.13),(.27,3.77,.10)]:
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
    par=local_wall_root(name,origin,heading,1.80)
    box(name+'_mounting_frame',(0,-.025,1.77),(1.04,.05,1.11),'teal')
    for xx in [-.44,.44]:
        for zz in [1.32,2.22]:bolt(name+'_wall_anchor',(xx,-.058,zz))
    # Pipe rises at left, traverses the isolator and regulator, then drops to coupler.
    tube(name+'_service_pipe',[(-.40,-.16,inlet_z),(-.40,-.16,1.88),(-.32,-.16,1.80),(.04,-.16,1.80),(.34,-.16,1.80),(.39,-.16,1.75),(.39,-.16,1.53)],.042,'steel')
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
    rod(name+'_bowl',(.07,-.16,1.51),(.07,-.16,1.68),.047,'glass',32)
    rod(name+'_filter_core',(.07,-.16,1.515),(.07,-.16,1.66),.031,'steel',24)
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
    wall_light('Cask_task_light',(3.08,13.2),0,2.58,150)

def wall_light(name,origin,heading=0,z=2.55,power=95):
    par=local_wall_root(name,origin,heading,z)
    box(name+'_back',(0,-.022,z),(.18,.044,.30),'darksteel')
    rod(name+'_arm',(0,-.04,z+.04),(0,-.22,z+.04),.019,'steel')
    box(name+'_hood',(0,-.25,z+.025),(.43,.30,.12),'teal',.009)
    box(name+'_diffuser',(0,-.25,z-.041),(.36,.25,.012),'lamp',.004)
    place_wall_group(par,origin,heading)
    c,s=math.cos(heading),math.sin(heading)
    area(name+'_pool',(origin[0]+s*.26,origin[1]-c*.26,z-.052),(origin[0]+s*.75,origin[1]-c*.75,.75),power,(1,.72,.44),.28,.14)

def floor_detail():
    root('Bay_floor_finish')
    # Staged trolley footprint is entirely east of the bypass and north of freight.
    for yy in [11.65,12.90]:box('Staged_white_line',(2.65,yy,.001),(2.18,.035,.002),'ivory',0)
    for xx in [1.56,3.74]:box('Staged_white_line',(xx,12.275,.001),(.035,1.25,.002),'ivory',0)
    text_obj('Staged_floor_type','STAGED',(2.65,11.32,.0017),.18,'ivory',(0,0,0))
    # One authored freight turn arrow, followed by a narrow edge route stripe.
    prism('Freight_floor_arrow',[(3.10,9.80),(3.65,9.80),(3.65,9.65),(4.05,10),(3.65,10.35),(3.65,10.20),(3.10,10.20)],.0007,.002,'ochre')
    box('Bypass_edge_mark',(-1.07,12.1,.001),(.04,2.10,.002),'ochre',0)
    for i in range(3):
        xx=1.85+i*.44
        prism('Parked_wheel_rub',[(xx,11.86),(xx+.10,11.89),(xx+.25,12.05),(xx+.17,12.045)],.0007,.0014,'chip')

def gate_drive_detail():
    # A support-registered drive attached to the authored gate lintel.
    par=local_wall_root('Freight_gate_drive',(6.35,10),-math.pi/2,3.72,face=-.185)
    # Local source plane is the front face of the existing overhead cover.
    box('Gate_drive_plate',(0,.177,3.72),(3.60,.036,.14),'steel')
    for xx in [-1.5,1.5]:
        box('Gate_track_bearing',(xx,.105,3.72),(.12,.11,.16),'teal')
        rod('Gate_roller',(xx,.04,3.72),(xx,.10,3.72),.061,'steel')
    box('Gate_chain_rail',(0,.06,3.74),(3.12,.042,.055),'darksteel')
    for zz in [3.735,3.775]:rod('Gate_chain_tension',(-1.49,.029,zz),(1.49,.029,zz),.006,'steel',12)
    rod('Gate_motor',(1.26,.030,3.96),(1.56,.030,3.96),.090,'teal_light')
    box('Gate_motor_bracket',(1.38,.13,3.94),(.36,.21,.055),'steel')
    for xx in [1.28,1.34,1.40,1.46,1.52]:rod('Motor_cooling_fin',(xx-.006,.03,3.96),(xx+.006,.03,3.96),.10,'darksteel')
    box('Orange_drive_access',(-1.39,.020,3.93),(.41,.05,.24),'ochre')
    box('Motor_vertical_mount',(1.38,.177,3.86),(.17,.06,.25),'steel')
    box('Access_cover_standoff',(-1.39,.08,3.85),(.22,.18,.20),'teal')
    for member in par.children:member.location.y-=.38
    place_wall_group(par,(6.35,10),-math.pi/2)

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
    folded_cloth('Bench_folded_rag',x,y-.02,.905,.23,.26)
    small_case('Spare_parts_case',(x,y+.23,.234),(.33,.39,.23),'old_teal')
    # Small glove silhouette: palm plus four articulated fingers and thumb.
    for side in [-1,1]:
        gx=x+side*.072;gy=y-.62
        box('Work_glove_palm',(gx,gy,.920),(.105,.115,.031),'rubber',.018)
        for i in range(4):
            xx=gx-.037+i*.024
            beam('Glove_finger',(xx,gy+.034,.920),(xx+.003,gy+.112-(i%3)*.009,.917),.021,.024,'rubber')
        beam('Glove_thumb',(gx+side*.038,gy-.022,.92),(gx+side*.078,gy+.01,.919),.024,.026,'rubber')
        box('Glove_cuff',(gx,gy-.07,.919),(.101,.049,.023),'ochre',.007)
    # A readable mix of shift objects, each on the bench or lower shelf.
    rod('Workshop_flask',(x-.17,y+.07,.905),(x-.17,y+.07,1.11),.046,'teal_light',32)
    rod('Flask_cap',(x-.17,y+.07,1.11),(x-.17,y+.07,1.132),.048,'steel',32)
    torus('Flask_handle',(x-.225,y+.07,1.04),.046,.008,'steel',(math.pi/2,0,0))
    text_obj('Grease_tin_label','GREASE',(x+.061,y-.36,.965),.022,'ivory',(math.pi/2,0,math.pi/2))
    rod('Worklight_body',(x+.17,y-.16,.934),(x+.17,y+.06,.934),.025,'ochre',24)
    rod('Worklight_end',(x+.17,y-.18,.934),(x+.17,y-.145,.934),.029,'darksteel',24)
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
        xx=-.42+i*.21;zz=1.84
        rod('Tool_hanging_peg',(xx,-.046,zz),(xx,-.115,zz),.009,'steel')
        torus('Hanging_ring_spanner',(xx,-.119,zz-.025),.034,.010,'steel',(math.pi/2,0,0))
        box('Spanner_shank',(xx,-.119,zz-.19),(.034,.015,.285),'steel',.006)
        box('Spanner_jaw',(xx,-.119,zz-.327),(.073,.018,.052),'steel',.006)
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
    text_obj(name+'_letters',label,(0,-.040,z-.047),.105,'ivory')
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
    wall_light('Bench_worklight',(-2.2,10.58),math.pi/2,2.36,120)
    wall_vent('Staging_vent',(2.16,13.2),0,3.63,.83)
    # A sign on the actual bypass ceiling step leaves its clear opening untouched.
    route_sign('Service_bypass_sign','SERVICE',(0,13.10),0,3.37,1.85)
    corner_marker('Bay_identity',(4.4,12.63),-math.pi/2,'04')
    # Original restrained graphics and edge-specific wear tie the work bay to A05.
    root('Bay_authored_wall_finish')
    for origin,heading,u0,u1 in [((-2.2,10.58),math.pi/2,.74,1.28),((4.4,12.63),-math.pi/2,-.28,.29)]:
        c,s=math.cos(heading),math.sin(heading)
        coordinates=[(u0,1.46),(u1,1.82),(u1,2.18),(u0,1.82)]
        vv=[(origin[0]+c*u+s*.0015,origin[1]+s*u-c*.0015,z) for u,z in coordinates]
        ob=mesh('Work_bay_diagonal',vv,[(0,1,2,3)],'ochre');ob['surface_decal']=True
    # Markings belong to the architecture and have no freestanding prop supports.
    for child in list(PAR.children):
        COL.objects.unlink(child);bpy.data.collections['01_Architecture'].objects.link(child)
    COL.objects.unlink(PAR);bpy.data.collections['01_Architecture'].objects.link(PAR)
    wall_light('Transfer_gate_key',(6.165,10),-math.pi/2,3.93,170)
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
        utility_station('Service_air_station',(-1.65,14.95),math.pi/2,2.46)
        for name,origin,angle,z in [('Entry_wall_key',(-2.2,4.8),math.pi/2,2.72),('Cross_wall_key',(9.1,12.2),0,2.72),('East_wall_key',(16.4,11.45),-math.pi/2,2.72),('Delivery_wall_key',(12,17.35),math.pi/2,2.72),('Service_corner_key',(-1.2,20.35),math.pi/2,2.50),('Medical_side_key',(8.5,21),0,2.52)]:wall_light(name,origin,angle,z,105)
        wall_vent('Entry_extract',(2.2,4.6),-math.pi/2,3.35,1.02)
        wall_vent('East_extract',(14.2,7),math.pi,3.35,1.12)
        wall_vent('Service_extract',(10.4,21),0,2.56,.72)
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
