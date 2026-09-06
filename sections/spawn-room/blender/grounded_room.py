"""Spawn composition assembled only after the documented slice gate passed."""
import bpy, math, json
from pathlib import Path
from math import pi,sin,cos
from mathutils import Vector
import grounded_kit as k
HERE=Path(__file__).resolve().parent

def cam(name,p,target,lens):
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.03;d.clip_end=100
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o

def wall_x(name,x,y0,y1,height=3.4,face=1):
    b=k.start()
    w=k.wall(name,y0 if face==1 else -y1,y1 if face==1 else -y0,0,height)
    k.group(name+'_assembly',b,(x,0,0),face*pi/2);return w

def wall_south(name,x0,x1,y,h=3.4):
    b=k.start();w=k.wall(name,-x1,-x0,0,h);k.group(name+'_assembly',b,(0,y,0),pi);return w

def observation(name,x,y0,y1,face):
    """Internal borrowed-light window exposes room function before its doorway."""
    yc=(y0+y1)/2;w=y1-y0
    base=k.box(name+'_sill_wall',(x-face*.08,yc,.575),(.16,w,1.15),'wall',.001)
    k.box(name+'_dado',(x+face*.004,yc,.575),(.008,w,1.15),'dado',.001)
    k.box(name+'_skirt',(x+face*.019,yc,.08),(.038,w,.16),'darksteel',.008)
    k.box(name+'_head_wall',(x-face*.08,yc,2.795),(.16,w,1.21),'wall',.001)
    b=k.start();k.frame(name+'_steel_reveal',(0,0,0),w,1.04,.035,.19,'darksteel',.012)
    k.panel(name+'_glass',(0,0,0),w-.065,.975,.008,.007,'glass')
    k.group(name+'_window',b,(x-face*.08,yc,1.67),face*pi/2)
    return base

def lining(name,x,y0,y1,face):
    yc=(y0+y1)/2;w=y1-y0
    k.box(name+'_dado',(x+face*.004,yc,.59),(.008,w,1.18),'dado',.001)
    k.box(name+'_skirt',(x+face*.019,yc,.08),(.038,w,.16),'darksteel',.008)
    k.box(name+'_cap',(x+face*.008,yc,1.186),(.016,w,.012),'pale',.002)

def sign(name,body,p,w,angle=0,mat='darksteel',size=.095):
    b=k.start();k.box(name+'_plate',(0,-.012,0),(w,.024,.23),mat,.003)
    k.label(name+'_type',body,(.055 if body in ['BRIEFING','LOCKERS'] else 0,-.025,-.035),size,'ink' if mat=='yellow' else 'paper',align='CENTER')
    if body in ['BRIEFING','LOCKERS']:
        x=-w/2+.13
        if body=='BRIEFING':
            pts=[(x-.045,-.027,.067),(x-.045,-.027,-.010),(x+.042,-.027,-.010),(x+.042,-.027,-.069)]
            k.tube(name+'_chair_icon',pts,.005,'paper');k.tube(name+'_chair_icon_leg',[(x-.035,-.027,-.01),(x-.035,-.027,-.069)],.005,'paper')
        else:
            k.frame(name+'_hood_icon',(x,-.027,.053),.042,.041,.005,.002,'paper',.013)
            k.tube(name+'_suit_icon',[(x-.056,-.027,-.024),(x-.04,-.027,.019),(x+.04,-.027,.019),(x+.056,-.027,-.024)],.005,'paper')
            k.tube(name+'_suit_icon_legs',[(x-.028,-.027,.018),(x-.028,-.027,-.069),(x,-.027,-.025),(x+.028,-.027,-.069),(x+.028,-.027,.018)],.004,'paper')
    return k.group(name,b,p,angle)

def mounted_print(name,path,p,w,h,angle=0):
    b=k.start();back=k.box(name+'_back',(0,-.009,0),(w,.018,h),'darksteel',.002)
    k.frame(name+'_frame',(0,-.021,0),w+.035,h+.035,.028,.04,'darksteel',.009)
    o=k.mesh(name+'_print',[(-w/2,-.021,-h/2),(w/2,-.021,-h/2),(w/2,-.021,h/2),(-w/2,-.021,h/2)],[(0,1,2,3)],'paper')
    uv=o.data.uv_layers.new(name='Print UV')
    for i,q in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=q
    m=bpy.data.materials.new(name+'_ink_on_paper');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    img=bpy.data.images.load(str(path),check_existing=True);img.pack()
    t=n.new('ShaderNodeTexImage');t.image=img;pbr=n.get('Principled BSDF');pbr.inputs['Roughness'].default_value=.92
    l.new(t.outputs['Color'],pbr.inputs['Base Color']);o.data.materials.clear();o.data.materials.append(m)
    return k.group(name,b,p,angle)

def procedure(name,p,angle=0):
    b=k.start();board=k.box(name+'_back',(0,-.007,0),(.49,.014,.61),'pale',.003)
    k.box(name+'_paper',(0,-.0145,0),(.455,.001,.57),'paper',.001)
    k.label(name+'_head','SEAL SEQUENCE',(-.205,-.016,.21),.039,'ink')
    for i,(title,sub) in enumerate([('01   CLOSE','Check wrists and ankles'),('02   CONNECT','Secure hood and filter'),('03   TEST','Wait for integrity result')]):
        z=.09-i*.132
        k.label(name+'_step',title,(-.20,-.016,z),.031,'ink')
        k.label(name+'_instruction',sub,(-.20,-.016,z-.04),.018,'ink')
    for x in [-.205,.205]:k.box(name+'_tape',(x,-.016,.266),(.046,.003,.067),'yellow',.001)
    return k.group(name,b,p,angle)

def chair(name,p,angle=0):
    b=k.start();feet=[]
    for side in [-1,1]:
        x=side*.23
        k.tube(name+'_side_frame',[(x,-.23,.02),(x,-.18,.35),(x,-.145,.409),(x,.13,.409),(x,.18,.35),(x,.23,.02)],.0135,'darksteel')
        k.tube(name+'_back_upright',[(x,.13,.35),(x,.20,.58),(x,.255,.85)],.012,'darksteel')
        for y in [-.23,.23]:
            k.box(name+'_foot',(x,y,.009),(.045,.055,.018),'rubber',.003);feet.append((x,y,0))
    # Curved laminated seat shell, with separate upholstered pad.
    v=[];N=18
    for x in [-.238,.238]:
        for i in range(N):
            y=-.225+i*.45/(N-1);z=.423+.018*(y/.225)**2
            v.append((x,y,z))
    shell=k.mesh(name+'_formed_seat',v,[(i,i+1,N+i+1,N+i) for i in range(N-1)],'pale',True)
    sol=shell.modifiers.new('Formed shell thickness','SOLIDIFY');sol.thickness=.014;k.bevel(shell,.008,3)
    pad=k.box(name+'_seat_pad',(0,0,.449),(.44,.395,.04),'vinyl',.029)
    back=k.panel(name+'_back_pad',(0,0,0),.45,.28,.038,.055,'vinyl');back.location=(0,.218,.727);back.rotation_euler.x=-.10
    k.rod(name+'_crossbrace',(-.22,.15,.34),(.22,.15,.34),.011,'steel')
    root=k.group(name,b,p,angle);root['asset_role']='primary_seat';return root,feet

def sideboard(name,p,angle=0):
    b=k.start()
    for x in [-.51,.51]:
        for y in [-.20,.20]:k.box(name+'_foot',(x,y,.045),(.05,.05,.09),'darksteel',.003)
    k.box(name+'_carcass',(0,0,.405),(1.12,.46,.65),'paint',.003)
    k.box(name+'_laminate_top',(0,-.005,.753),(1.18,.51,.046),'wood',.007)
    for x in [-.275,.275]:
        k.box(name+'_door',(x,-.239,.414),(.532,.018,.586),'pale',.002)
        k.tube(name+'_pull',[(x+.15,-.25,.44),(x+.15,-.28,.44),(x+.15,-.28,.55),(x+.15,-.25,.55)],.006,'steel')
    root=k.group(name,b,p,angle);return root,[(-.51,-.20,0),(.51,-.20,0),(-.51,.20,0),(.51,.20,0)]

def briefing_display(name,p,angle=0):
    b=k.start()
    k.box(name+'_wall_mount',(0,-.05,0),(1.7,.10,.75),'steel',.008)
    k.panel(name+'_housing',(0,-.13,0),2.36,1.30,.16,.045,'pale')
    k.frame(name+'_bezel',(0,-.225,.02),2.15,1.04,.055,.044,'darksteel',.035)
    k.panel(name+'_screen',(0,-.237,.02),2.045,.937,.010,.015,'screen')
    # Simple readable idle lesson frame, not a screen full of sci-fi UI.
    k.label(name+'_title','SHIFT BRIEFING',(-.91,-.245,.31),.098,'paper')
    k.label(name+'_subtitle','PREPARATION  /  SECTOR 04',(-.91,-.245,.18),.033,'paper')
    for i,(word,num) in enumerate([('PREPARE','01'),('PRODUCE','02'),('RETURN','03')]):
        x=-.68+i*.69
        k.label(name+'_number',num,(x,-.245,-.04),.12,'pale',align='CENTER')
        k.label(name+'_step',word,(x,-.245,-.16),.036,'paper',align='CENTER')
    k.label(name+'_start','PRESS TO BEGIN',(-.91,-.245,-.35),.035,'paper')
    for x in [-.95,-.84,-.73]:k.rod(name+'_button',(x,-.219,-.571),(x,-.236,-.571),.018,'plastic')
    for i in range(10):k.box(name+'_speaker',(.64+i*.031,-.219,-.572),(.012,.009,.038),'darksteel',.001)
    root=k.group(name,b,p,angle);root['interaction']='optional briefing playback';return root

def meter(name,p,angle=0):
    b=k.start()
    # Modest .56 x .31 x .85 m cast and folded instrument, held by brackets.
    for z in [-.31,.31]:k.box(name+'_mount',(0,-.035,z),(.38,.07,.06),'steel',.003)
    k.panel(name+'_cast_body',(0,-.175,0),.56,.85,.23,.041,'pale')
    k.frame(name+'_gauge_bezel',(0,-.302,.18),.43,.28,.021,.027,'darksteel',.023)
    k.panel(name+'_gauge_card',(0,-.317,.18),.389,.239,.002,.004,'paper')
    for i in range(13):
        a=pi-i*pi/12;r=.15
        k.rod(name+'_tick',(r*cos(a),-.320,.12+r*sin(a)),((r-.013)*cos(a),-.320,.12+(r-.013)*sin(a)),.0015,'ink',8)
    needle=k.tube(name+'_needle',[(0,-.323,.12),(-.077,-.323,.245)],.0028,'red')
    k.label(name+'_units','DOSE  /  uSv/h',(-.165,-.321,.088),.022,'ink')
    k.rod(name+'_test_button',(.156,-.298,-.105),(.156,-.329,-.105),.031,'yellow')
    for i in range(7):k.box(name+'_speaker',(-.13,-.299,-.086-i*.021),(.16,.009,.007),'darksteel',.001)
    k.rod(name+'_detector',(0,-.173,-.43),(0,-.173,-.54),.053,'darksteel')
    k.label(name+'_instruction','CHECK BEFORE EXIT',(-.214,-.299,-.325),.023,'ink')
    root=k.group(name,b,p,angle);root['asset_role']='radiation_checkpoint';return root,[(0,0,-.31),(0,0,.31)]

def chamber(name,p,angle=-pi/2):
    b=k.start()
    base=k.box(name+'_folded_base',(0,0,.065),(1.90,1.94,.13),'darksteel',.034)
    k.box(name+'_standing_plate',(-.08,-.04,.138),(1.42,1.72,.016),'rubber',.015)
    k.box(name+'_threshold',(-.08,-.962,.067),(1.43,.015,.09),'yellow',.002)
    # A continuous substantial front portal with radiused bent corners and a deep service spine.
    portal=k.frame(name+'_pressure_frame',(-.11,-.72,1.425),1.67,2.59,.12,.19,'pale',.16)
    k.frame(name+'_front_seal',(-.11,-.83,1.425),1.44,2.36,.026,.031,'rubber',.055)
    spine=k.box(name+'_service_spine',(.73,.16,1.42),(.39,1.33,2.54),'paint',.032)
    lid=k.panel(name+'_service_lid',(0,0,0),.87,1.31,.012,.032,'pale');lid.location=(.931,.15,1.56);lid.rotation_euler.z=pi/2
    # Rear supporting bulkhead and partial side glazing, not four identical posts.
    k.box(name+'_rear_bulkhead',(0,.885,1.30),(1.86,.12,2.38),'pale',.022)
    k.panel(name+'_rear_access',(0,.952,1.42),1.36,1.65,.012,.016,'paint')
    for x in [-.62,.62]:
        for z in [.65,2.18]:k.rod(name+'_rear_captive_screw',(x,.959,z),(x,.965,z),.009,'steel',16)
    for i in range(9):k.box(name+'_rear_air_slot',(0,.959,.84+i*.037),(.82,.004,.012),'darksteel',.001)
    k.box(name+'_rear_latch',(.49,.968,1.54),(.055,.024,.095),'steel',.006)
    k.panel(name+'_rear_service_inset',(-.21,.811,1.36),1.15,1.82,.013,.04,'paint')
    k.box(name+'_left_sill',(-.902,.07,.46),(.074,1.62,.56),'pale',.008)
    k.box(name+'_left_head',(-.902,.07,2.50),(.074,1.62,.13),'pale',.006)
    k.box(name+'_side_glass',(-.902,.07,1.52),(.01,1.62,1.61),'glass',.001)
    for y in [-.71,.85]:k.box(name+'_glazing_channel',(-.903,y,1.5),(.035,.04,2.09),'darksteel',.003)
    k.box(name+'_canopy',(0,.05,2.66),(1.98,1.83,.18),'pale',.024)
    k.box(name+'_air_plenum',(.15,.15,2.765),(1.48,1.12,.035),'darksteel',.006)
    for i in range(10):k.box(name+'_plenum_louvre',(-.455+i*.133,-.66,2.62),(.054,.012,.089),'darksteel',.003)
    # Overhead test mechanism, a physical pressure seal and scanning beam.
    k.rod(name+'_test_head',(-.14,.17,2.44),(-.14,.17,2.55),.25,'steel',48)
    k.rod(name+'_test_seal',(-.14,.17,2.42),(-.14,.17,2.45),.21,'rubber',48)
    scan=k.box(name+'_scan_carriage',(-.12,.66,1.92),(1.08,.12,.12),'steel',.015)
    for x in [-.68,.47]:k.rod(name+'_linear_guide',(x,.70,.41),(x,.70,2.33),.019,'steel')
    for z in [.37,2.33]:k.box(name+'_guide_crosshead',(-.105,.73,z),(1.32,.14,.055),'darksteel',.005)
    # Inward hinged seal leaves park inside the machine envelope and clear the aisle.
    for side in [-1,1]:
        db=k.start()
        k.frame(name+'_door_frame',(-side*.36,0,0),.72,2.25,.039,.035,'steel',.03)
        k.panel(name+'_door_glass',(-side*.36,.002,0),.645,2.17,.008,.007,'glass')
        k.tube(name+'_door_pull',[(-side*.63,-.04,-.21),(-side*.63,-.071,-.21),(-side*.63,-.071,.11),(-side*.63,-.04,.11)],.009,'rubber')
        for z in [-.87,.87]:k.rod(name+'_seal_hinge',(0,0,z-.035),(0,0,z+.035),.018,'steel')
        leaf=k.group(name+('_door_L' if side<0 else '_door_R'),db,(-.11+side*.72,-.864,1.40))
        leaf['interaction']='inward hinged seal door'
        for frame,opening in [(1,1),(31,0),(61,0),(91,1),(121,0),(151,0)]:
            leaf.rotation_euler.z=-side*pi/2*opening;leaf.keyframe_insert(data_path='rotation_euler',frame=frame)
    # Compact physical controller belongs to this machine, not a freestanding kiosk.
    k.panel(name+'_control_face',(.735,-.552,1.35),.32,.55,.043,.020,'pale')
    k.frame(name+'_readout_bezel',(.735,-.581,1.45),.24,.17,.018,.018,'darksteel',.016)
    states=[(1,'READY'),(31,'OCCUPIED'),(61,'TESTING'),(91,'PASS'),(121,'INSPECT'),(151,'FAIL')]
    for i,(fr,word) in enumerate(states):
        text=k.label(name+'_readout_'+word,word,(.735,-.593,1.442),.028,'ink',align='CENTER')
        for j,(frame,_) in enumerate(states):
            text.hide_render=(j!=i);text.hide_viewport=(j!=i)
            text.keyframe_insert(data_path='hide_render',frame=frame);text.keyframe_insert(data_path='hide_viewport',frame=frame)
    k.rod(name+'_start',(.665,-.58,1.24),(.665,-.61,1.24),.025,'yellow')
    k.rod(name+'_abort',(.803,-.58,1.24),(.803,-.61,1.24),.018,'red')
    for j,color in enumerate([(.16,.5,.24),(.65,.36,.05),(.56,.05,.025)]):
        mat=k.material(name+'_signal_%d'%j,color,.27,0,0,0,1);pbr=mat.node_tree.nodes.get('Principled BSDF')
        pbr.inputs['Emission Color'].default_value=(*color,1)
        for frame,active in [(1,0),(31,1),(61,1),(91,0),(121,1),(151,2)]:
            pbr.inputs['Emission Strength'].default_value=3 if j==active else 0
            pbr.inputs['Emission Strength'].keyframe_insert(data_path='default_value',frame=frame)
        k.rod(name+'_state_lens',(.648+j*.085,-.557,1.755),(.648+j*.085,-.582,1.755),.016,name+'_signal_%d'%j)
    k.label(name+'_plate','INTEGRITY',(-.1,-.876,2.635),.065,'ink',align='CENTER')
    k.label(name+'_entry_hint','STAND CLEAR UNTIL READY',(-.1,-.861,.262),.029,'paper',align='CENTER')
    for fr,z in [(1,1.92),(31,1.92),(61,.65),(91,1.92),(121,1.2),(151,1.2)]:
        scan.location.z=z;scan.keyframe_insert(data_path='location',frame=fr)
    for o in set(bpy.data.objects)-b:
        if any(o.name.startswith(name+'_'+suffix) for suffix in ['control_face','readout','start','abort','state_lens']):o.location.y-=.40
    k.box(name+'_controller_mount',(.69,-.857,1.35),(.12,.16,.38),'darksteel',.005)
    k.box(name+'_indicator_rail',(.733,-.865,1.755),(.30,.205,.072),'darksteel',.006)
    root=k.group(name,b,p,angle);root['asset_role']='integrity_chamber';root['states']='1 idle; 31 occupied; 61 scanning; 91 pass; 121 concern; 151 fail'
    return root,[(-.75,-.75,0),(.75,-.75,0),(-.75,.75,0),(.75,.75,0)]

def build():
    gate=HERE.parent/'production/checkpoints/style-slice.json'
    assert gate.exists() and json.loads(gate.read_text())['visual_average']>=8,'Slice must pass first'
    f=k.floor('FACILITY_floor',-7.46,8.26,-.6,12.3)
    # 3.4 m hall; two 1.3 m door openings; operations 1.7 m opening.
    hleft0=wall_x('HALL_left_spawn',-1.7,-.5,.45)
    wall_x('HALL_bench_recess_S',-2.15,.45,1.05)
    observation('HALL_briefing_observation',-2.15,1.05,2.35,1)
    wall_x('HALL_bench_recess_N',-2.15,2.35,2.65)
    wall_x('HALL_left_door_approach',-1.7,2.65,3.05)
    wall_south('HALL_recess_return_S',-2.15,-1.70,.45)
    k.wall('HALL_recess_return_N',-2.15,-1.70,2.65)
    k.box('HALL_recess_ceiling',(-2.045,.645,3.48),(.53,.39,.16),'wall',.001)
    hleft1=wall_x('HALL_left_ops',-1.7,4.35,9.3)
    hright0=wall_x('HALL_right_spawn',1.7,-.5,1.85,face=-1)
    observation('HALL_locker_observation',1.7,1.85,2.85,-1)
    wall_x('HALL_right_door_approach',1.7,2.85,3.05,face=-1)
    hright1=wall_x('HALL_right_ops',1.7,4.35,9.3,face=-1)
    # Two skins form an actual pocket, so the personnel leaf never intersects solid wall.
    hright1.dimensions.y=.025;hright1.location.y=.0125
    k.box('LOCKER_pocket_back_skin',(1.8375,6.825,1.7),(.045,4.95,3.4),'wall',.001)
    for x in [-1.7,1.7]:k.box('HALL_room_header',(x,3.70,2.81),(.16,1.3,1.22),'wall',.001)
    k.wall('HALL_ops_left',-1.7,-.85,9.3);opswall=k.wall('HALL_ops_right',.85,1.7,9.3)
    k.box('HALL_ops_lintel',(0,9.38,2.88),(1.7,.16,1.04),'wall',.001)
    # The rear entry seals and a visible service corridor embed the playable cluster in a building.
    k.wall('HALL_rear_left',-1.7,-.65,-.5);k.wall('HALL_rear_right',.65,1.7,-.5)
    k.box('HALL_rear_header',(0,-.42,2.8),(1.3,.16,1.2),'wall',.001)
    k.door('HALL_rear_door',(0,-.50,0),pi)
    hallceil=k.box('HALL_ceiling',(0,4.4,3.48),(3.56,9.95,.16),'wall',.001)
    bfar=wall_x('BRIEFING_focal_wall',-7.3,1,6.1)
    bside=wall_south('BRIEFING_south',-7.3,-2.31,1)
    bnorth=k.wall('BRIEFING_north',-7.3,-1.86,6.1)
    bceil=k.box('BRIEFING_ceiling',(-4.58,3.55,3.48),(5.6,5.42,.16),'wall',.001)
    lnorth=k.wall('LOCKER_north',1.86,8.1,7.3,3.8)
    lsouth=wall_south('LOCKER_south',1.86,8.1,.7,3.8)
    lfar=wall_x('LOCKER_far',8.1,.7,7.3,3.8,-1)
    lceil=k.box('LOCKER_ceiling',(4.98,4,3.88),(6.56,6.92,.16),'wall',.001)
    k.box('LOCKER_shared_wall_upper',(1.78,4,3.6),(.16,6.6,.4),'wall',.001)
    for name,x,y0,y1,face in [('LOCKER_entry_lower',1.86,.7,3.05,1),('LOCKER_entry_upper',1.86,4.35,7.3,1),('BRIEFING_entry_lower',-1.86,2.65,3.05,-1),('BRIEFING_entry_upper',-1.86,4.35,6.1,-1),('BRIEFING_recess_back',-2.31,1,2.65,-1)]:
        lining(name,x,y0,y1,face)
    k.door('BRIEFING_entry',(-1.7,3.7,0),pi/2,opened=pi*.97)
    entry=k.door('LOCKER_entry',(1.7,3.7,0),-pi/2)
    leaf=bpy.data.objects['LOCKER_entry_LEAF']
    for obj in list(leaf.children_recursive):
        if any(s in obj.name for s in ['_hinge','_closer','_lever','_handle_escutcheon']):bpy.data.objects.remove(obj,do_unlink=True)
    leaf.location.x-=1.3;leaf.location.y=.04;leaf['interaction']='sliding personnel door';leaf['closed_x']=-.634
    rail=k.box('LOCKER_pocket_track',(0,0,0),(2.7,.072,.065),'steel',.004);rail.parent=entry;rail.location=(-.66,.075,2.245)
    pull=k.tube('LOCKER_pocket_pull',[(.611,.008,.94),(.611,.002,.94),(.611,.002,1.12),(.611,.008,1.12)],.004,'steel')
    pull.parent=leaf;pull.location.x=.634
    k.door('OPERATIONS_door',(0,9.3,0),w=1.7,h=2.35,heavy=True)
    # Quiet narrow continuation behind wired glazing.
    wall_x('SERVICE_left',-1.7,9.46,12.3);wall_x('SERVICE_right',1.7,9.46,12.3,face=-1)
    k.wall('SERVICE_end',-1.7,1.7,12.3);serviceceil=k.box('SERVICE_ceiling',(0,10.9,3.48),(3.5,3.0,.16),'wall',.001)
    for name,p,w,ang,target in [('WAYFIND_briefing',(-1.61,3.70,2.49),1.14,pi/2,hleft0),('WAYFIND_lockers',(1.61,3.70,2.49),1.14,-pi/2,hright0),('WAYFIND_operations',(0,9.29,2.66),1.66,0,opswall)]:
        body={'WAYFIND_briefing':'BRIEFING','WAYFIND_lockers':'LOCKERS','WAYFIND_operations':'OPERATIONS'}[name]
        o=sign(name,body,p,w,ang)
        # Explicit supports are the actual solid lintels, never adjacent wall segments.
        target=bpy.data.objects['HALL_ops_lintel'] if 'operations' in name else bpy.data.objects['HALL_room_header'+('' if 'briefing' in name else '.001')]
        # Plates attach directly to the corresponding lintel front face.
        if 'briefing' in name:o.location.x=-1.62
        elif 'lockers' in name:o.location.x=1.62
        else:o.location.y=9.30
        k.support(o,target,'LOCAL_+Y',[(0,0,0)],'WALL')
    # Fixtures attach to ceilings, with physical footprints defining the light sources.
    for i,y in enumerate([1.45,4.65,8.0]):
        o,a=k.practical('HALL_light_%02d'%i,(0,y,3.4),pi/2,power=150,length=1.22);k.support(o,hallceil,'WORLD_+Z',a,'CEILING')
    for i,x in enumerate([-5.9,-3.1]):
        o,a=k.practical('BRIEFING_light_%02d'%i,(x,3.60,3.4),power=170,length=1.35);k.support(o,bceil,'WORLD_+Z',a,'CEILING')
    for i,(x,y) in enumerate([(5.25,2.2),(5.25,5.80),(2.7,4.0)]):
        o,a=k.practical('LOCKER_light_%02d'%i,(x,y,3.8),power=240,length=1.55);k.support(o,lceil,'WORLD_+Z',a,'CEILING')
    o,a=k.practical('SERVICE_light',(0,11,3.4),power=90,length=1.1);k.support(o,serviceceil,'WORLD_+Z',a,'CEILING')
    # One large ventilation trunk continues through the rear operational wall.
    ductparts=k.start()
    k.box('HALL_duct',(1.22,5.8,3.12),(.52,13.0,.29),'pale',.013)
    for y in [1.2,4.5,7.8,10.8]:
        k.box('HALL_duct_join',(1.22,y,3.12),(.54,.043,.31),'steel',.005)
        for x in [.99,1.45]:k.rod('HALL_duct_hanger',(x,y,3.29),(x,y,3.4),.007,'steel')
    duct=k.group('HALL_ventilation',ductparts)
    k.support(duct,hallceil,'WORLD_+Z',[(x,y,3.4) for x in [.99,1.45] for y in [1.2,4.5,7.8]],'CEILING')
    o,a=k.utility('HALL_riser',(-1.7,7.45,0),pi/2);k.support(o,hleft1,'LOCAL_+Y',a,'WALL')
    # Exact two left/two right stations as seen from locker entry, with restrained differences.
    for i,(x,y,ang) in enumerate([(5.35,6.998,0),(6.85,6.998,0),(5.35,1.002,pi),(6.85,1.002,pi)]):
        o,a=k.bay('PPE_%02d'%(i+1),(x,y,0),ang,i);k.support(o,f,'WORLD_-Z',a)
    o,a=chamber('INTEGRITY',(5.05,4,0));k.support(o,f,'WORLD_-Z',a)
    o,a=k.bench('LOCKER_bench',(7.58,4,0),pi/2,length=1.8);k.support(o,f,'WORLD_-Z',a)
    notes=k.clipboard('LOCKER_shift_notes',(7.58,3.48,.45),pi/2+.06)
    k.support(notes,bpy.data.objects['LOCKER_bench_laminate_slat.001'],'WORLD_-Z',[(0,0,0)])
    o=procedure('LOCKER_procedure',(8.1,4,1.70),-pi/2);k.support(o,lfar,'LOCAL_+Y',[(0,0,0)],'WALL')
    ventparts=k.start()
    k.box('LOCKER_return_dark_recess',(0,-.003,0),(.80,.006,.19),'darksteel',.002)
    k.frame('LOCKER_return_surround',(0,-.012,0),.87,.25,.027,.024,'pale',.009)
    for z in [-.064,-.032,0,.032,.064]:
        blade=k.box('LOCKER_return_blade',(0,0,0),(.8,.033,.013),'steel',.002);blade.location=(0,-.024,z);blade.rotation_euler.x=.4
    vent=k.group('LOCKER_return_air',ventparts,(8.1,4,3.15),-pi/2);k.support(vent,lfar,'LOCAL_+Y',[(0,0,0)],'WALL')
    # Four primary chairs with one modest human misalignment.
    for i,(x,y,da) in enumerate([(-4.65,2.55,0),(-4.65,4.40,.04),(-3.40,2.9,-.12),(-3.38,4.0,.02)]):
        o,a=chair('BRIEFING_seat_%02d'%i,(x,y,0),-pi/2+da);k.support(o,f,'WORLD_-Z',a)
    o=briefing_display('BRIEFING_display',(-7.3,3.55,1.77),pi/2);k.support(o,bfar,'LOCAL_+Y',[(0,0,0)],'WALL')
    o,a=sideboard('BRIEFING_sideboard',(-5.80,1.37,0),pi);k.support(o,f,'WORLD_-Z',a)
    o=k.mug('BRIEFING_mug',(-5.49,1.36,.776));k.support(o,bpy.data.objects['BRIEFING_sideboard_laminate_top'],'WORLD_-Z',[(0,0,0)])
    o=k.clipboard('BRIEFING_notes',(-6.0,1.38,.776),.08);k.support(o,bpy.data.objects['BRIEFING_sideboard_laminate_top'],'WORLD_-Z',[(0,0,0)])
    portrait=mounted_print('BRIEFING_crew',HERE.parent/'assets/portraits/commissioning_crew.png',(-4.60,6.1,1.79),1.15,.767)
    k.support(portrait,bnorth,'LOCAL_+Y',[(0,0,0)],'WALL')
    portrait=mounted_print('HALL_supervisor',HERE.parent/'assets/portraits/human_contribution.png',(-1.7,5.65,1.76),.58,.87,pi/2)
    k.support(portrait,hleft1,'LOCAL_+Y',[(0,0,0)],'WALL')
    # One compact notice grouping opposite the waiting bench.
    nb=k.start();k.box('HALL_notice_back',(0,-.012,0),(.90,.024,.68),'wood',.005)
    k.frame('HALL_notice_frame',(0,-.021,0),.94,.72,.023,.030,'steel',.009)
    for i in range(2):
        x=-.21+i*.41;k.box('HALL_notice_paper',(x,-.025,-.04),(.35,.002,.48),'paper',.001)
        k.label('HALL_notice_title',['SHIFT 04','MAINTENANCE'][i],(x-.15,-.027,.143),.026,'ink')
        for j in range(6):k.box('HALL_notice_rule',(x,-.027,.072-j*.043),(.26,.001,.002),'ink',0)
        k.box('HALL_notice_clip',(x,-.030,.18),(.038,.01,.022),'steel',.003)
    k.label('HALL_notice_header','CURRENT SHIFT',(-.40,-.027,.266),.047,'paper')
    o=k.group('HALL_notice',nb,(1.7,.95,1.62),-pi/2);k.support(o,hright0,'LOCAL_+Y',[(0,0,0)],'WALL')
    o,a=k.bench('HALL_waiting_bench',(-1.87,1.55,0),pi/2,length=1.8);k.support(o,f,'WORLD_-Z',a)
    o,a=meter('RADIATION', (1.25,9.3,1.44));k.support(o,opswall,'LOCAL_+Y',a,'WALL')
    o=sign('HAZARD_threshold','RADIATION CONTROLLED AREA',(0,9.30,3.0),1.67,mat='yellow',size=.065);k.support(o,bpy.data.objects['HALL_ops_lintel'],'LOCAL_+Y',[(0,0,0)],'WALL')
    for i,(x,y) in enumerate([(-.5,7.5),(6.5,3.5)]):
        tile=k.box('FLOOR_replacement_%d'%i,(x,y,.0003),(.991,.991,.0006),'floor4',0);k.support(tile,f,'WORLD_-Z',[(0,0,-.0003)])
    for i,p in enumerate([(0,8.92,0),(3.66,4,0),(5.15,1.95,0),(6.85,6.02,0)]):
        o=k.use_marks('TRAFFIC_%d'%i,p);k.support(o,f,'WORLD_-Z',[(0,0,.0007)])
    for i,x in enumerate([-.63,.63]):
        for j,y in enumerate([.45,1.35]):
            o=bpy.data.objects.new('SPAWN_%d'%(i*2+j+1),None);bpy.context.collection.objects.link(o);o.location=(x,y,0);o['gameplay_role']='player_spawn'
    for name,p in [('AUDIO_vent',(1.2,7,3.1)),('AUDIO_operations',(0,11,1.7)),('AUDIO_briefing',(-7,3.5,1.7)),('AUDIO_integrity_test_motor',(5.05,4,2.4)),('AUDIO_integrity_latch',(4.19,4,1.0)),('INTERACT_integrity',(4.05,3.26,1.1)),('INTERACT_dose',(1.25,8.85,1.44))]:
        o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=p
    bpy.context.scene.frame_set(1)
    # Practical output is deliberately zoned, with a cooler operational threshold.
    for o in bpy.data.objects:
        if o.type=='LIGHT':
            o.data.energy *= .55
            if o.name.startswith('HALL_light_02') or o.name.startswith('SERVICE_'):
                o.data.color=(.79,.87,1.0)
            if o.name.startswith('BRIEFING_light_01'):o.data.energy *= .65
            if o.name.startswith('LOCKER_light_02'):o.data.energy *= .55
    # Formal baselines: six reference views plus original production audit cameras.
    specs=[('VALIDATE_Spawn',(0,.23,1.63),(0,6.3,1.63),22),
      ('VALIDATE_HallForward',(-.25,6.30,1.63),(.2,9.3,1.66),27),
      ('VALIDATE_LockerDoor',(1.42,3.95,1.63),(6.4,4,1.50),14.5),
      ('VALIDATE_LockerReverse',(7.35,5.85,1.63),(2.3,3.1,1.4),16),
      ('VALIDATE_BriefingDoor',(-1.92,3.7,1.63),(-5.6,3.5,1.22),23),
      ('VALIDATE_Material_A',(3.25,5.3,1.63),(5.09,6.99,1.24),30),
      ('VALIDATE_ExitReverse',(.45,8.85,1.63),(0,2.1,1.6),23),
      ('VALIDATE_Walk_A',(-.75,2.85,1.63),(1.75,3.7,1.6),25),
      ('VALIDATE_Walk_B',(6.30,5.62,1.63),(2.5,5.6,1.3),25),
      ('VALIDATE_Walk_C',(-6.05,5.0,1.63),(-2.25,3.5,1.12),25),
      ('VALIDATE_Hero_A',(2.90,2.43,1.63),(5.30,4.7,1.49),24)]
    for name,p,t,lens in specs:cam(name,p,t,lens)
    cam('DETAIL_BriefingHuman',(-2.6,1.8,1.63),(-5.1,4.7,1.5),20)
    cam('DETAIL_LockerWork',(6.4,5.4,1.63),(7.6,3.8,.85),30)
    return [n for n,p,t,l in specs]
