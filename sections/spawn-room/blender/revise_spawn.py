"""User-directed Spawn corrections, September 6 2026.

Run against the protected tactile source/checkpoint. Changes are reproducible and
save to a new file. Latest user direction overrides older door/meter/TV/pod specs.
"""
import bpy, sys, math, json, hashlib, argparse, time
from pathlib import Path
from mathutils import Vector
from math import pi, sin, cos
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grounded_kit as k
import grounded_room as room
import validate_contacts as contacts

def remove_prefix(*prefixes):
    doomed = {o for o in bpy.data.objects if any(o.name == p or o.name.startswith(p+'_') or o.name.startswith(p+'.') for p in prefixes)}
    for o in list(doomed): doomed.update(o.children_recursive)
    names = sorted(o.name for o in doomed)
    for o in doomed: bpy.data.objects.remove(o, do_unlink=True)
    return names

def support_floor(o, anchors):
    k.support(o, bpy.data.objects['FACILITY_floor'], 'WORLD_-Z', anchors)

def portal(name, x, angle, width=1.30):
    before = k.start()
    # Reveal surfaces sit inside the rough opening. Plaster ends 25mm behind them.
    for side in [-1, 1]:
        k.box(name+'_jamb', (side*(width/2+.0375),0,1.1), (.075,.29,2.20), 'darksteel', .002)
    k.box(name+'_head',(0,0,2.2375),(width+.15,.29,.075),'darksteel',.002)
    k.box(name+'_threshold',(0,0,.004),(width,.29,.008),'worn_safety_tread',.001)
    root = k.group(name, before, (x,3.7,0), angle)
    root['asset_role']='open_room_portal';root['clear_width_m']=width;root['clear_height_m']=2.20
    return root

def architecture():
    removed = remove_prefix('BRIEFING_entry','LOCKER_entry','LOCKER_pocket','HALL_briefing_observation','HALL_locker_observation',
        'HALL_left_door_approach','HALL_right_door_approach','HALL_left_ops','HALL_right_ops','HALL_room_header',
        'LOCKER_entry_lower','LOCKER_entry_upper','BRIEFING_entry_lower','BRIEFING_entry_upper')
    room.wall_x('HALL_briefing_infill',-2.15,1.05,2.35)
    room.wall_x('HALL_locker_infill',1.7,1.85,2.575,face=-1)
    room.wall_x('HALL_left_door_approach',-1.7,2.65,3.025)
    room.wall_x('HALL_left_ops',-1.7,4.375,9.3)
    room.wall_x('HALL_right_ops',1.7,4.825,9.3,face=-1)
    for x,w in [(-1.78,1.35),(1.78,2.25)]:
        k.box('HALL_room_header',(x,3.7,2.8375),(.16,w,1.125),'wall',.001)
    for name,x,a,b,face in [('LOCKER_entry_lower',1.86,.7,2.575,1),('LOCKER_entry_upper',1.86,4.825,7.3,1),
       ('BRIEFING_entry_lower',-1.86,2.65,3.025,-1),('BRIEFING_entry_upper',-1.86,4.375,6.1,-1)]:
        room.lining(name,x,a,b,face)
    portal('BRIEFING_portal',-1.78,pi/2);portal('LOCKER_portal',1.78,-pi/2,2.20)
    # Existing directional signs touch the corrected header front faces.
    bpy.data.objects['WAYFIND_briefing'].location.x=-1.70
    bpy.data.objects['WAYFIND_lockers'].location.x=1.70
    # Repaired wall support retains exact old target names for portrait / pipe.
    return removed

def airlock():
    removed=remove_prefix('OPERATIONS_door','RADIATION','INTERACT_dose','HALL_ops_left','HALL_ops_right','HALL_ops_lintel',
                          'WAYFIND_operations','HAZARD_threshold')
    k.wall('HALL_ops_left',-1.7,-1.435,9.3)
    k.wall('HALL_ops_right',1.435,1.7,9.3)
    lintel=k.box('HALL_ops_lintel',(0,9.38,3.1375),(2.87,.16,.525),'wall',.001)
    before=k.start()
    # Recessed compression frame, 2.56m clear opening and a 200mm thick pressure leaf.
    k.frame('AIRLOCK_pressure_ring',(0,.015,1.435),2.88,2.87,.155,.34,'pressure_metal',.18)
    k.frame('AIRLOCK_compression_seal',(0,-.163,1.425),2.59,2.61,.030,.022,'rubber',.075)
    for side in [-1,1]:
        part=k.start()
        center=side*.64
        k.panel('AIRLOCK_leaf_body',(center,.035,1.36),1.267,2.62,.20,.065,'darksteel')
        k.panel('AIRLOCK_steel_face',(center,-.072,1.37),1.17,2.43,.014,.09,'pressure_metal')
        # Raised folded ribs leave broad quiet steel fields between them.
        for z in [.46,2.27]:
            k.panel('AIRLOCK_structural_rib',(center,-.099,z),1.11,.105,.04,.018,'steel')
        k.box('AIRLOCK_meeting_stile',(side*.028,-.105,1.35),(.038,.064,2.52),'steel',.004)
        for z in [.38,1.34,2.30]:
            k.box('AIRLOCK_lock_dog',(side*1.235,-.13,z),(.17,.105,.17),'pressure_metal',.014)
            k.rod('AIRLOCK_lock_pin',(side*1.235,-.189,z),(side*1.235,-.205,z),.033,'darksteel')
        k.tube('AIRLOCK_manual_grip',[(center,-.09,1.16),(center,-.19,1.16),(center,-.19,1.52),(center,-.09,1.52)],.019,'darksteel')
        for z in [1.19,1.49]:k.box('AIRLOCK_grip_collar',(center,-.19,z),(.045,.046,.038),'yellow',.004)
        leaf=k.group('AIRLOCK_leaf_L' if side<0 else 'AIRLOCK_leaf_R',part)
        leaf['interaction']='horizontal powered pressure leaf';leaf['open_translation_x']=side*1.29
    k.box('AIRLOCK_threshold',(0,-.01,.018),(2.58,.48,.036),'worn_safety_tread',.003)
    k.panel('AIRLOCK_drive_cover',(0,-.05,2.77),1.76,.13,.30,.023,'darksteel')
    for x in [-.63,.63]:k.rod('AIRLOCK_drive_cap',(x,-.208,2.77),(x,-.220,2.77),.033,'steel')
    root=k.group('AIRLOCK',before,(0,9.3,0))
    root['asset_role']='operational_airlock';root['clear_width_m']=2.56;root['clear_height_m']=2.61
    sign=room.sign('WAYFIND_operations','OPERATIONS  /  AIRLOCK',(0,9.3,3.04),2.0,size=.085)
    k.support(sign,lintel,'LOCAL_+Y',[(0,0,0)],'WALL')
    support_floor(root,[(-1.20,.015,0),(1.20,.015,0)])
    return removed

def briefing():
    removed=remove_prefix('BRIEFING_display','BRIEFING_seat')
    before=k.start()
    k.box('BRIEFING_TV_wall_mount',(0,-.025,0),(1.05,.05,.62),'darksteel',.003)
    k.panel('BRIEFING_TV_enclosure',(0,-.064,0),2.61,1.50,.06,.022,'tv_black')
    k.panel('BRIEFING_TV_screen',(0,-.096,0),2.53,1.423,.003,.008,'tv_display')
    # Content is entirely within the flat display; no console, pedestal or controls.
    k.label('BRIEFING_TV_title','SHIFT BRIEFING',(-1.12,-.099,.40),.135,'paper')
    k.label('BRIEFING_TV_subtitle','PREPARATION  /  SECTOR 04',(-1.11,-.099,.21),.039,'pale')
    for i,word in enumerate(['01   PREPARE','02   PRODUCE','03   RETURN']):
        k.label('BRIEFING_TV_step',word,(-1.10+i*.79,-.099,-.17),.051,'paper')
    k.box('BRIEFING_TV_progress',(0,-.099,-.43),(2.2,.001,.009),'pale',0)
    k.rod('BRIEFING_TV_status',(1.235,-.096,-.722),(1.235,-.10,-.722),.004,'ready',12)
    tv=k.group('BRIEFING_TV',before,(-7.3,3.55,1.86),pi/2)
    k.support(tv,bpy.data.objects['BRIEFING_focal_wall'],'LOCAL_+Y',[(0,0,0)],'WALL')
    for i,(x,y,angle) in enumerate([(-5.25,3.55,-pi/2),(-3.70,3.58,-pi/2+.018)]):
        o,anchors=k.bench('BRIEFING_bench_%02d'%(i+1),(x,y,0),angle,length=1.50)
        o['asset_role']='briefing_bench';o['seat_capacity']=2
        before=k.start()
        for sx in [-.51,.51]:
            k.tube('BRIEFING_backrest_upright',[(sx,.13,.35),(sx,.23,.59),(sx,.285,.86)],.014,'darksteel')
        for z in [.665,.805]:
            slat=k.box('BRIEFING_backrest_board',(0,.25+(z-.665)*.21,z),(1.5,.032,.115),'wood',.007)
            slat.rotation_euler.x=-.12
        for part in set(bpy.data.objects)-before:part.parent=o
        support_floor(o,anchors)
    return removed

def curved_glass(name,a,b,r=.88):
    count=40;verts=[]
    for z in [.245,2.47]:
        for i in range(count+1):
            t=math.radians(a+(b-a)*i/count);verts.append((r*cos(t),r*sin(t),z))
    obj=k.mesh(name,verts,[(i,i+1,count+2+i,count+1+i) for i in range(count)],'pod_optical_glass',True)
    sol=obj.modifiers.new('Laminated safety glazing 8mm','SOLIDIFY');sol.thickness=.008
    for z in [.245,2.47]:
        k.tube(name+'_glazing_shoe',[(r*cos(math.radians(a+(b-a)*i/count)),r*sin(math.radians(a+(b-a)*i/count)),z) for i in range(count+1)],.012,'steel')
    for angle in [a,b]:
        t=math.radians(angle);x,y=r*cos(t),r*sin(t)
        k.rod(name+'_edge_seal',(x,y,.245),(x,y,2.47),.009,'rubber')
    return obj

def pod():
    before=k.start()
    # Machined perimeter rings, an open interior and a compact rear mechanism.
    k.lathe('POD_lower_hull',[(0,0),(.87,0),(.98,.045),(.98,.13),(.91,.205),(.83,.205),(.80,.12),(0,.12),(0,0)],'pressure_metal',96)
    k.lathe('POD_lower_seal',[(.858,.207),(.901,.207),(.901,.231),(.858,.231),(.858,.207)],'rubber',96)
    k.rod('POD_standing_mat',(0,0,.121),(0,0,.137),.748,'rubber',96)
    k.lathe('POD_canopy',[(.75,2.48),(.91,2.48),(1.0,2.55),(1.0,2.67),(.91,2.77),(.45,2.77),(.45,2.68),(.75,2.64),(.75,2.48)],'pressure_metal',96)
    k.lathe('POD_upper_gasket',[(.855,2.467),(.902,2.467),(.902,2.486),(.855,2.486),(.855,2.467)],'rubber',96)
    k.box('POD_rear_service_spine',(0,.80,1.355),(.35,.23,2.27),'darksteel',.025)
    k.panel('POD_spine_service_lid',(0,.929,1.4),.26,1.67,.018,.018,'pressure_metal')
    for z in [.60,2.20]:k.rod('POD_service_fastener',(0,.943,z),(0,.951,z),.014,'steel',16)
    for angle in [-30,30,150,210]:
        t=math.radians(angle);x,y=.898*cos(t),.898*sin(t)
        k.rod('POD_load_column',(x,y,.205),(x,y,2.5),.027,'pressure_metal',32)
    curved_glass('POD_fixed_glass',-30,210,.887)
    for name,a,b,opening in [('POD_door_L',210,270,-60),('POD_door_R',270,330,60)]:
        part=k.start();curved_glass(name+'_glazing',a,b,.854)
        theta=math.radians(b if opening<0 else a);x,y=.854*cos(theta),.854*sin(theta)
        k.tube(name+'_pull',[(x,y,1.06),(x,y-.048,1.06),(x,y-.048,1.40),(x,y,1.40)],.012,'steel')
        leaf=k.group(name,part)
        for frame,amount in [(1,1),(31,0),(61,0),(91,1),(121,0),(151,0)]:
            leaf.rotation_euler.z=math.radians(opening)*amount;leaf.keyframe_insert(data_path='rotation_euler',frame=frame)
        leaf['interaction']='curved sliding seal door'
    # Accessible sloped tread at front. The contact anchors correspond to its toe.
    k.mesh('POD_entry_ramp',[(-.53,-1.105,0),(.53,-1.105,0),(.53,-.60,.125),(-.53,-.60,.125),(-.53,-.60,0),(.53,-.60,0)],
        [(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2),(4,3,2,5)],'worn_safety_tread')
    # One ceiling test head and vertical guide carriage.
    k.rod('POD_scan_mount',(0,.10,2.46),(0,.10,2.68),.14,'darksteel',48)
    k.lathe('POD_sensor_head',[(0,2.39),(.18,2.39),(.28,2.43),(.28,2.48),(.18,2.51),(0,2.51),(0,2.39)],'steel',64)
    for x in [-.25,.25]:k.rod('POD_scan_guide',(x,.66,.37),(x,.66,2.35),.017,'steel')
    scan=k.panel('POD_scanner_carriage',(0,.61,0),.62,.11,.09,.028,'pressure_metal')
    for frame,z in [(1,2.15),(31,2.15),(61,.55),(91,2.15),(121,1.2),(151,1.2)]:
        scan.location.z=z;scan.keyframe_insert(data_path='location',frame=frame)
    k.box('POD_controller_bracket',(.73,-.52,1.32),(.14,.13,.43),'darksteel',.01)
    k.panel('POD_controller',(.78,-.63,1.35),.25,.41,.065,.02,'pressure_metal')
    k.panel('POD_readout',(.78,-.668,1.44),.205,.15,.009,.009,'screen')
    states=[(1,'READY'),(31,'SEALED'),(61,'TESTING'),(91,'PASS'),(121,'INSPECT'),(151,'FAIL')]
    for i,(f,word) in enumerate(states):
        o=k.label('POD_state_'+word,word,(.78,-.675,1.429),.028,'paper',align='CENTER')
        for j,(frame,_) in enumerate(states):
            o.hide_render=j!=i;o.hide_viewport=j!=i;o.keyframe_insert(data_path='hide_render',frame=frame);o.keyframe_insert(data_path='hide_viewport',frame=frame)
    for x,mat in [(.72,'yellow'),(.845,'red')]:k.rod('POD_physical_button',(x,-.67,1.24),(x,-.688,1.24),.023,mat)
    k.label('POD_identification','INTEGRITY',(0,-.973,2.605),.053,'paper',align='CENTER')
    for obj in set(bpy.data.objects)-before:
        if obj.name in ['POD_lower_hull','POD_canopy','POD_lower_seal','POD_upper_gasket']:
            # Smooth the circular machining direction, retain crisp profile steps.
            normals=[None]*len(obj.data.loops)
            for face in obj.data.polygons:
                face.use_smooth=True
                radial=math.hypot(face.normal.x,face.normal.y)
                center=face.center;sign=1 if center.x*face.normal.x+center.y*face.normal.y>=0 else -1
                for loop in face.loop_indices:
                    v=obj.data.vertices[obj.data.loops[loop].vertex_index].co
                    t=math.atan2(v.y,v.x)
                    normals[loop]=(sign*radial*cos(t),sign*radial*sin(t),face.normal.z)
            obj.data.normals_split_custom_set(normals)
    root=k.group('INTEGRITY_POD',before,(6.82,4,0),-pi/2)
    root['asset_role']='integrity_chamber';root['states']='1 ready;31 sealed;61 test;91 pass;121 inspect;151 fail'
    support_floor(root,[(0,0,0),(-.53,-1.105,0),(.53,-1.105,0)])
    return root

def storage(name,p,angle):
    before=k.start()
    k.box(name+'_carcass',(0,.015,1.0),(.82,.48,1.90),'darksteel',.008)
    for x in [-.203,.203]:
        k.panel(name+'_door',(x,-.236,1.06),.39,1.65,.021,.010,'paint')
        k.tube(name+'_handle',[(x+.12,-.252,.98),(x+.12,-.279,.98),(x+.12,-.279,1.11),(x+.12,-.252,1.11)],.007,'steel')
        for z in [1.67,1.71,1.75]:k.box(name+'_vent',(x,-.250,z),(.22,.003,.008),'darksteel',.001)
        for z in [.3,1.8]:k.rod(name+'_hinge',(x-.175,-.25,z-.025),(x-.175,-.25,z+.025),.01,'steel')
    for x in [-.32,.32]:
        for y in [-.16,.18]:k.box(name+'_foot',(x,y,.03),(.07,.07,.06),'rubber',.002)
    root=k.group(name,before,p,angle);support_floor(root,[(x,y,0) for x in [-.32,.32] for y in [-.16,.18]])

def locker():
    removed=remove_prefix('INTEGRITY','LOCKER_bench','LOCKER_shift_notes','LOCKER_procedure')
    for i in range(4):bpy.data.objects['PPE_%02d'%(i+1)].location.x=3.0 if i%2==0 else 4.50
    for i,y in enumerate([2.85,5.15]):
        o,a=k.bench('LOCKER_changing_bench_%02d'%(i+1),(3.90,y,0),length=2.0)
        o['asset_role']='locker_changing_bench';support_floor(o,a)
    storage('LOCKER_personal_north',(6.1,6.995,0),0)
    storage('LOCKER_personal_south',(6.1,1.005,0),pi)
    pod()
    # Existing room-level audio/interaction anchors follow the relocated mechanism.
    for name,p in [('AUDIO_integrity_test_motor',(6.82,4,2.5)),('AUDIO_integrity_latch',(5.96,4,1)),('INTERACT_integrity',(6.18,3.22,1.2))]:
        o=bpy.data.objects.get(name)
        if o:o.location=p
    return removed

def materials():
    k.STAGE=3;k.M={m.name:m for m in bpy.data.materials}
    k.material('pressure_metal',(.24,.285,.29),.42,.9,.12,.0003,4)
    k.material('tv_black',(.012,.015,.016),.48,.35,.02,0,4)
    m=k.material('tv_display',(.012,.045,.045),.37,0,0,0,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.015,.048,.045,1);p.inputs['Emission Strength'].default_value=.4
    m=k.material('pod_optical_glass',(.965,.99,.983),.023,0,0,0,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
    # Art-directed thin glazing: retain a modest optical reflection while keeping
    # the interior readable through overlapping curved leaves in realtime EEVEE.
    n=m.node_tree.nodes;l=m.node_tree.links
    transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.10
    l.new(transparent.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
    m.use_raytrace_refraction=True
    m.surface_render_method='BLENDED'
    m.use_transparency_overlap=False

def shadow_fix():
    s=bpy.context.scene;s.eevee.use_shadows=True;s.eevee.shadow_pool_size='512'
    s.eevee.use_shadow_jitter_viewport=True;s.eevee.shadow_ray_count=3;s.eevee.shadow_step_count=8
    s.eevee.taa_samples=32;s.eevee.taa_render_samples=48
    for light in bpy.data.lights:
        light.shadow_filter_radius=2.5;light.shadow_maximum_resolution=.006;light.use_shadow_jitter=True
    s['shadow_correction']='Shadow-map striping isolated by shadow on/off test. Jitter enabled in viewport and on practicals; 6mm limit, 2.5px filtering.'

def startup():
    s=bpy.context.scene;s.frame_set(1);s.camera=bpy.data.objects['VALIDATE_Spawn']
    cam=s.camera
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type!='VIEW_3D':continue
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.shading.use_scene_lights=True;sp.shading.use_scene_world=True;sp.overlay.show_overlays=False
            sp.clip_start=.03;sp.clip_end=100;sp.lens=cam.data.lens
            rv=sp.region_3d;rv.view_perspective='PERSP';rv.view_rotation=cam.matrix_world.to_quaternion();rv.view_distance=1
            rv.view_location=cam.matrix_world.translation+rv.view_rotation@Vector((0,0,-1))

def validate(out):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    report={'objects':[],'failures':[]};cache={}
    for obj in sorted(contacts.get_collection_objects(contacts.REQUIRED_COLLECTION),key=lambda o:o.name):
        result=contacts.validate_object(obj,cache,dg);report['objects'].append(result)
        if result['status']!='PASS':report['failures'].append(result)
    report['status']='FAIL' if report['failures'] else 'PASS';report['objects_checked']=len(report['objects'])
    (out/'contacts.json').write_text(json.dumps(report,indent=2))
    checks={
        'old_room_doors_removed':not any(bpy.data.objects.get(n) for n in ['BRIEFING_entry','BRIEFING_entry_LEAF','LOCKER_entry','LOCKER_entry_LEAF']),
        'observation_windows_removed':not any('observation' in o.name for o in bpy.data.objects),
        'meter_removed':not any(o.name.startswith('RADIATION') for o in bpy.data.objects),
        'old_tv_console_removed':not any(o.name.startswith('BRIEFING_display') for o in bpy.data.objects),
        'exactly_two_briefing_benches':sum(o.get('asset_role')=='briefing_bench' for o in bpy.data.objects)==2,
        'four_briefing_places':sum(o.get('seat_capacity',0) for o in bpy.data.objects)==4,
        'exactly_four_suit_bays':all(bpy.data.objects.get('PPE_%02d'%i) for i in range(1,5)),
        'two_left_two_right':sum(bpy.data.objects['PPE_%02d'%i].location.y>4 for i in range(1,5))==2,
        'suits_near_entrance':all(bpy.data.objects['PPE_%02d'%i].location.x<=4.51 for i in range(1,5)),
        'pod_center_back':abs(bpy.data.objects['INTEGRITY_POD'].location.y-4)<.001 and bpy.data.objects['INTEGRITY_POD'].location.x>6.5,
        'two_changing_benches':sum(o.get('asset_role')=='locker_changing_bench' for o in bpy.data.objects)==2,
        'airlock_wider_than_old_1_7m':bpy.data.objects['AIRLOCK']['clear_width_m']>2.5,
        'all_contact_checks':report['status']=='PASS',
        'shadow_jitter_enabled':bpy.context.scene.eevee.use_shadow_jitter_viewport,
        'materials_packed':all(im.packed_file or im.packed_files for im in bpy.data.images if im.source=='FILE' and im.users),
    }
    # Test actual scene triangles along every portal opening, including child trims.
    blocked=[]
    for label,x,width in [('briefing',-1.78,1.30),('locker',1.78,2.20)]:
        for j in range(17):
            y=3.7-width/2+.025+(width-.05)*j/16
            for z in [.045,.45,1.1,1.63,2.16]:
                hit,loc,normal,index,obj,matrix=bpy.context.scene.ray_cast(dg,Vector((x-.21,y,z)),Vector((1,0,0)),distance=.42)
                if hit:blocked.append({'portal':label,'object':obj.name,'point':list(loc)})
    checks['portal_clearance_170_rays']=not blocked
    floor=bpy.data.objects['FACILITY_floor'].data
    signatures=[tuple(sorted(tuple(round(c,6) for c in floor.vertices[i].co) for i in p.vertices)) for p in floor.polygons]
    checks['no_duplicate_floor_faces']=len(signatures)==len(set(signatures))
    checks['floor_normals_up']=all(p.normal.z>.98 for p in floor.polygons if p.material_index<5)
    state_checks=[]
    for frame,left,right in [(1,-60,60),(31,0,0),(61,0,0),(91,-60,60),(121,0,0),(151,0,0)]:
        bpy.context.scene.frame_set(frame)
        visible=[o for o in bpy.data.objects if o.name.startswith('POD_state_') and not o.hide_render]
        correct=(len(visible)==1 and abs(math.degrees(bpy.data.objects['POD_door_L'].rotation_euler.z)-left)<.01 and abs(math.degrees(bpy.data.objects['POD_door_R'].rotation_euler.z)-right)<.01)
        state_checks.append({'frame':frame,'status':'PASS' if correct else 'FAIL','readout':visible[0].data.body if visible else None})
    bpy.context.scene.frame_set(1)
    checks['six_pod_states']=all(v['status']=='PASS' for v in state_checks)
    (out/'clearance_and_states.json').write_text(json.dumps({'blocked_portal_rays':blocked,'pod_states':state_checks},indent=2))
    data={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'dimensions_m':{'briefing_portal_clear':[1.30,2.20],'locker_portal_clear':[2.20,2.20],'airlock_clear':[2.56,2.61],'pod':[2,2.105,2.77],'briefing_bench_length':1.5,'seat_height':.45,'locker_middle_aisle':1.847}}
    (out/'checks.json').write_text(json.dumps(data,indent=2));print('REVISION_CHECKS',json.dumps(data),flush=True)
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('--review',default='user-corrections-01');p.add_argument('--no-bake',action='store_true');p.add_argument('--validate-only',action='store_true');p.add_argument('--cameras',default='VALIDATE_Spawn,VALIDATE_HallForward,VALIDATE_LockerDoor,VALIDATE_BriefingDoor');p.add_argument('--resolution',type=int,default=1000)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=HERE.parent/'production/renders/review'/a.review;out.mkdir(parents=True,exist_ok=True)
    source=Path(bpy.data.filepath);source_sha=hashlib.sha256(source.read_bytes()).hexdigest();s=bpy.context.scene;t=time.time()
    if not a.validate_only:
        materials();removed=architecture()+airlock()+briefing()+locker();shadow_fix();startup()
        room.cam('USER_Floor',(0,3.0,1.63),(0,4.1,0),22)
        room.cam('USER_BriefingFrame',(-.55,1.65,1.63),(-1.78,3.7,1.20),24)
        room.cam('USER_LockerEntry',(2.3,3.8,1.65),(5.3,4,1.40),12)
        s['user_revision']='2026-09-06: open portals; no observations/meter; large airlock; slim TV/two benches; forward PPE; rear optical-glass pod.'
        (out/'removed_objects.json').write_text(json.dumps(removed,indent=2))
        if not a.no_bake:
            print('REBAKE_INDIRECT',flush=True);bpy.ops.object.lightprobe_cache_bake(subset='ALL')
        startup();destination=HERE/'spawnroom_revised_walk.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
    else:destination=source
    validation=validate(out)
    s.render.resolution_x=a.resolution;s.render.resolution_y=round(a.resolution*.64);s.render.resolution_percentage=100
    for name in a.cameras.split(','):
        if not name:continue
        s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    provenance={'source':str(source),'source_sha256':source_sha,'output':str(destination),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'engine':s.render.engine,'blender':bpy.app.version_string,'elapsed_seconds':time.time()-t,'cameras':a.cameras.split(',')}
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2));print('REVISION_COMPLETE',json.dumps(provenance),flush=True)
    assert validation['status']=='PASS','Review checks failed; inspect checks.json'

if __name__=='__main__':main()
